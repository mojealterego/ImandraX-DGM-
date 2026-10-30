"""Durable bounded asynchronous research event queue.

Explicit first-party event kinds; no arbitrary dynamic imports, code execution,
network adapter or deploy. SQLite is an operator-local queue, not HA/WORM.
"""
from __future__ import annotations
import asyncio
from contextlib import contextmanager
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Any
from uuid import uuid4

_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,95}\Z")
_KINDS = frozenset({"research.check", "memory.synthesize", "artifact.inspect",
                    "model.evaluate"})
_MAX_ROWS = 10000


class EventError(ValueError):
    pass


def _encode(data: Any) -> str:
    try:
        payload = json.dumps(data, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError, RecursionError) as exc:
        raise EventError("INVALID_EVENT_JSON") from exc
    if len(payload.encode()) > 8192:
        raise EventError("EVENT_TOO_LARGE")
    return payload


def _time(value: object) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise EventError("INVALID_QUEUE_TIME")
    return float(value)


class DurableEventQueue:
    def __init__(self, path: Path):
        self.path = Path(path)
        if self.path.is_symlink() or self.path.parent.is_symlink():
            raise EventError("SYMLINK_STATE_DENIED")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db(write=True) as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS task_events(
                event_id TEXT PRIMARY KEY, kind TEXT NOT NULL,
                payload TEXT NOT NULL, payload_hash TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('PENDING','LEASED','DONE','DEAD')),
                attempts INTEGER NOT NULL DEFAULT 0,
                available_at REAL NOT NULL,
                lease_until REAL, lease_token TEXT,
                result TEXT
              );
              CREATE INDEX IF NOT EXISTS task_schedule
                ON task_events(status,available_at);
              CREATE TRIGGER IF NOT EXISTS task_no_delete
                BEFORE DELETE ON task_events
                BEGIN SELECT RAISE(ABORT,'task history cannot be deleted'); END;
              CREATE TRIGGER IF NOT EXISTS task_no_payload_edit
                BEFORE UPDATE OF event_id,kind,payload,payload_hash ON task_events
                BEGIN SELECT RAISE(ABORT,'event identity immutable'); END;
            """)
        if not self.verify():
            raise EventError("EVENT_INTEGRITY_FAILURE")

    @contextmanager
    def _db(self, *, write: bool = False):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def verify(self) -> bool:
        try:
            with self._db() as db:
                for row in db.execute("SELECT kind,payload,payload_hash FROM task_events"):
                    if sha256((row["kind"] + "\0" + row["payload"]).encode()).hexdigest() != row["payload_hash"]:
                        return False
            return True
        except (sqlite3.DatabaseError, ValueError):
            return False

    def enqueue(self, *, event_id: str, kind: str,
                payload: dict, now: float) -> dict:
        if not isinstance(event_id, str) or not _RE.fullmatch(event_id):
            raise EventError("INVALID_EVENT_ID")
        if kind not in _KINDS:
            raise EventError("UNSUPPORTED_EVENT_KIND")
        if not isinstance(payload, dict):
            raise EventError("INVALID_EVENT_PAYLOAD")
        body = _encode(payload)
        t = _time(now)
        digest = sha256((kind + "\0" + body).encode()).hexdigest()
        with self._db(write=True) as db:
            existing = db.execute(
                "SELECT payload_hash FROM task_events WHERE event_id=?", (event_id,)).fetchone()
            if existing is not None:
                if existing["payload_hash"] != digest:
                    raise EventError("IDEMPOTENCY_CONFLICT")
                return {"event_id": event_id, "status": "EXISTS"}
            if db.execute("SELECT COUNT(*) FROM task_events").fetchone()[0] >= _MAX_ROWS:
                raise EventError("QUEUE_CAPACITY_EXCEEDED")
            db.execute("""INSERT INTO task_events(event_id,kind,payload,payload_hash,
                         status,attempts,available_at) VALUES(?,?,?,?,'PENDING',0,?)""",
                       (event_id, kind, body, digest, t))
            return {"event_id": event_id, "status": "ENQUEUED"}

    def claim(self, *, now: float, lease_seconds: float = 30) -> dict | None:
        t = _time(now)
        lease = _time(lease_seconds)
        if not 1 <= lease <= 3600:
            raise EventError("INVALID_LEASE")
        if not self.verify():
            raise EventError("EVENT_INTEGRITY_FAILURE")
        with self._db(write=True) as db:
            row = db.execute("""
              SELECT * FROM task_events WHERE
              (status='PENDING' AND available_at<=?) OR
              (status='LEASED' AND lease_until<=?)
              ORDER BY available_at,event_id LIMIT 1""", (t, t)).fetchone()
            if row is None:
                return None
            token = uuid4().hex
            db.execute("""UPDATE task_events SET status='LEASED',
                          lease_token=?,lease_until=?,attempts=attempts+1
                          WHERE event_id=?""", (token, t+lease, row["event_id"]))
            return {"event_id": row["event_id"], "kind": row["kind"],
                    "payload": json.loads(row["payload"]), "lease_token": token,
                    "attempts": row["attempts"] + 1}

    def _require_lease(self, db, event_id, token):
        row = db.execute("SELECT * FROM task_events WHERE event_id=?", (event_id,)).fetchone()
        if row is None or row["status"] != "LEASED" or row["lease_token"] != token:
            raise EventError("INVALID_OR_STALE_LEASE")
        return row

    def ack(self, event_id: str, lease_token: str, result: dict | None = None) -> None:
        body = _encode(result or {})
        with self._db(write=True) as db:
            self._require_lease(db, event_id, lease_token)
            db.execute("""UPDATE task_events SET status='DONE',result=?,
                         lease_token=NULL,lease_until=NULL WHERE event_id=?""",
                       (body, event_id))

    def fail(self, event_id: str, lease_token: str, *,
             now: float, max_attempts: int = 4) -> None:
        t = _time(now)
        if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
            raise EventError("INVALID_RETRY_BUDGET")
        with self._db(write=True) as db:
            row = self._require_lease(db, event_id, lease_token)
            dead = row["attempts"] >= max_attempts
            db.execute("""UPDATE task_events SET status=?, available_at=?,
                         lease_token=NULL, lease_until=NULL WHERE event_id=?""",
                       ("DEAD" if dead else "PENDING",
                        t if dead else t + min(3600.0, float(2**row["attempts"])),
                        event_id))

    def status(self, event_id: str) -> dict:
        if not self.verify():
            raise EventError("EVENT_INTEGRITY_FAILURE")
        with self._db() as db:
            row = db.execute("SELECT * FROM task_events WHERE event_id=?", (event_id,)).fetchone()
        if row is None:
            raise EventError("UNKNOWN_EVENT")
        return {"event_id": event_id, "status": row["status"],
                "attempts": row["attempts"],
                "result": json.loads(row["result"]) if row["result"] else None}

    async def process_once(self, handlers: dict[str, Any], *,
                           now: float, timeout: float = 5) -> int:
        if not isinstance(handlers, dict) or not set(handlers).issubset(_KINDS):
            raise EventError("UNTRUSTED_HANDLER_REGISTRY")
        if type(timeout) not in (float, int) or not 0 < timeout <= 30:
            raise EventError("INVALID_TIMEOUT")
        job = self.claim(now=now, lease_seconds=max(1.0, timeout+1))
        if job is None:
            return 0
        handler = handlers.get(job["kind"])
        if handler is None or not asyncio.iscoroutinefunction(handler):
            self.fail(job["event_id"], job["lease_token"], now=now)
            return 1
        try:
            result = await asyncio.wait_for(handler(job["payload"]), timeout=timeout)
            if not isinstance(result, dict):
                raise EventError("INVALID_HANDLER_RESULT")
            self.ack(job["event_id"], job["lease_token"], result)
        except Exception:
            self.fail(job["event_id"], job["lease_token"], now=now)
        return 1
