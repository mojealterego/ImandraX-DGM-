"""Bitemporal graph memory for one trusted ImandraX process.

Times are UTC; valid time describes the world, recorded time describes when
we learned a revision. Facts are data, never instructions or trusted evidence.
The journal is local tamper-evident SQLite, not WORM or independent attestation.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Iterator

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}\Z")
_KINDS = frozenset({
    "WORKING", "EPISODIC", "SEMANTIC", "PROCEDURAL", "REFLECTION",
    "GENERATIVE", "GENERAL", "EDGE",
})
_COLUMNS = ("tenant", "fact_id", "kind", "subject", "predicate", "value_json",
            "valid_from", "valid_to", "recorded_at", "provenance",
            "confidence", "retracted", "request_id")
_GENESIS = "0" * 64


class MemoryError(ValueError):
    """A rejected memory operation, conflict or corrupted local journal."""


def _id(value: str, name: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise MemoryError("INVALID_" + name)
    return value


def _utc(value: str | datetime) -> str:
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MemoryError("INVALID_TIME") from exc
    elif isinstance(value, datetime):
        parsed = value
    else:
        raise MemoryError("INVALID_TIME")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MemoryError("NAIVE_TIME_FORBIDDEN")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _encode(value: Any) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise MemoryError("INVALID_MEMORY_VALUE") from exc
    if len(raw.encode("utf-8")) > 8192:
        raise MemoryError("MEMORY_VALUE_TOO_LARGE")
    return raw


def _hash(record: dict, previous: str) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return sha256(bytes.fromhex(previous) + payload).hexdigest()


class BitemporalGraphMemory:
    """Durable knowledge/event graph with logical point-in-time recovery."""

    def __init__(self, path: Path):
        self.path = Path(path)
        if self.path.is_symlink() or self.path.parent.is_symlink():
            raise MemoryError("SYMLINK_STATE_DENIED")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect(write=True) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS memory_revisions(
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  tenant TEXT NOT NULL, fact_id TEXT NOT NULL,
                  kind TEXT NOT NULL, subject TEXT NOT NULL,
                  predicate TEXT NOT NULL, value_json TEXT NOT NULL,
                  valid_from TEXT NOT NULL, valid_to TEXT,
                  recorded_at TEXT NOT NULL, provenance TEXT NOT NULL,
                  confidence REAL NOT NULL, retracted INTEGER NOT NULL
                    CHECK(retracted IN (0,1)),
                  request_id TEXT NOT NULL, previous_sha TEXT NOT NULL,
                  digest TEXT NOT NULL,
                  UNIQUE(tenant, request_id)
                );
                CREATE INDEX IF NOT EXISTS memory_lookup_idx
                  ON memory_revisions(tenant, fact_id, seq DESC);
                CREATE INDEX IF NOT EXISTS memory_subject_idx
                  ON memory_revisions(tenant, subject, kind);
                CREATE TRIGGER IF NOT EXISTS memory_no_update
                  BEFORE UPDATE ON memory_revisions
                  BEGIN SELECT RAISE(ABORT,'memory revisions immutable'); END;
                CREATE TRIGGER IF NOT EXISTS memory_no_delete
                  BEFORE DELETE ON memory_revisions
                  BEGIN SELECT RAISE(ABORT,'memory revisions immutable'); END;
            """)
        if not self.verify():
            raise MemoryError("MEMORY_INTEGRITY_FAILURE")

    @contextmanager
    def _connect(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
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
            with self._connect() as db:
                prev = _GENESIS
                expected_seq = 1
                for row in db.execute("SELECT * FROM memory_revisions ORDER BY seq"):
                    if row["seq"] != expected_seq or row["previous_sha"] != prev:
                        return False
                    record = {key: row[key] for key in _COLUMNS}
                    if _hash(record, prev) != row["digest"]:
                        return False
                    prev = row["digest"]
                    expected_seq += 1
            return True
        except (sqlite3.DatabaseError, ValueError, TypeError):
            return False

    def put(
        self, *, tenant: str, fact_id: str, kind: str, subject: str,
        predicate: str, value: Any, valid_from: str | datetime,
        valid_to: str | datetime | None = None,
        request_id: str, provenance: str,
        confidence: float = 1.0, expected_seq: int | None = None,
        retracted: bool = False, recorded_at: str | datetime | None = None,
    ) -> dict:
        _id(tenant, "TENANT")
        _id(fact_id, "FACT_ID")
        _id(subject, "SUBJECT")
        _id(predicate, "PREDICATE")
        _id(request_id, "REQUEST_ID")
        if kind not in _KINDS:
            raise MemoryError("INVALID_MEMORY_KIND")
        if (not isinstance(provenance, str) or not 1 <= len(provenance) <= 256
                or "\x00" in provenance):
            raise MemoryError("INVALID_PROVENANCE")
        if type(confidence) not in (int, float) or not 0.0 <= confidence <= 1.0:
            raise MemoryError("INVALID_CONFIDENCE")
        if type(retracted) is not bool:
            raise MemoryError("INVALID_RETRACTION")
        if expected_seq is not None and (type(expected_seq) is not int or expected_seq < 1):
            raise MemoryError("INVALID_EXPECTED_SEQ")
        if kind == "EDGE" and (not isinstance(value, str) or not _ID.fullmatch(value)):
            raise MemoryError("INVALID_EDGE_TARGET")
        begin = _utc(valid_from)
        end = _utc(valid_to) if valid_to is not None else None
        if end is not None and end <= begin:
            raise MemoryError("INVALID_VALID_INTERVAL")
        recorded = _utc(recorded_at or datetime.now(timezone.utc))
        record = {
            "tenant": tenant, "fact_id": fact_id, "kind": kind,
            "subject": subject, "predicate": predicate,
            "value_json": _encode(value), "valid_from": begin, "valid_to": end,
            "recorded_at": recorded, "provenance": provenance,
            "confidence": float(confidence), "retracted": int(retracted),
            "request_id": request_id,
        }
        with self._connect(write=True) as db:
            existing = db.execute(
                "SELECT * FROM memory_revisions WHERE tenant=? AND request_id=?",
                (tenant, request_id)).fetchone()
            if existing is not None:
                if any(existing[key] != record[key] for key in _COLUMNS if key != "recorded_at"):
                    raise MemoryError("IDEMPOTENCY_CONFLICT")
                return {"seq": existing["seq"], "digest": existing["digest"],
                        "status": "ALREADY_RECORDED"}
            latest = db.execute(
                "SELECT seq FROM memory_revisions WHERE tenant=? AND fact_id=? ORDER BY seq DESC LIMIT 1",
                (tenant, fact_id)).fetchone()
            if (latest is None and expected_seq is not None) or (
                latest is not None and (expected_seq is None or latest["seq"] != expected_seq)
            ):
                raise MemoryError("REVISION_CONFLICT")
            tail = db.execute(
                "SELECT digest, recorded_at FROM memory_revisions ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            if tail is not None and recorded < tail["recorded_at"]:
                raise MemoryError("SYSTEM_CLOCK_REGRESSION")
            previous = tail["digest"] if tail else _GENESIS
            digest = _hash(record, previous)
            keys = (*_COLUMNS, "previous_sha", "digest")
            params = {**record, "previous_sha": previous, "digest": digest}
            sql = ("INSERT INTO memory_revisions (" + ",".join(keys) + ") VALUES (" +
                   ",".join(":" + key for key in keys) + ")")
            cursor = db.execute(sql, params)
            return {"seq": cursor.lastrowid, "digest": digest,
                    "status": "RECORDED_UNVERIFIED"}

    def query(
        self, *, tenant: str, valid_at: str | datetime,
        system_at: str | datetime | None = None,
        as_of_seq: int | None = None, kind: str | None = None,
        subject: str | None = None, limit: int = 50,
    ) -> list[dict]:
        _id(tenant, "TENANT")
        if kind is not None and kind not in _KINDS:
            raise MemoryError("INVALID_MEMORY_KIND")
        if subject is not None:
            _id(subject, "SUBJECT")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise MemoryError("INVALID_QUERY_LIMIT")
        if as_of_seq is not None and (type(as_of_seq) is not int or as_of_seq < 0):
            raise MemoryError("INVALID_SYSTEM_SEQ")
        valid = _utc(valid_at)
        system = _utc(system_at) if system_at is not None else "9999-12-31T23:59:59.999999+00:00"
        if not self.verify():
            raise MemoryError("MEMORY_INTEGRITY_FAILURE")
        params: list[Any] = [tenant, system]
        seq_where = ""
        if as_of_seq is not None:
            seq_where = " AND seq<=?"
            params.append(as_of_seq)
        sql = ("""
          SELECT m.* FROM memory_revisions m
          JOIN (
            SELECT fact_id, MAX(seq) AS latest_seq FROM memory_revisions
            WHERE tenant=? AND recorded_at<=?""" + seq_where + """
            GROUP BY fact_id
          ) versions ON m.seq=versions.latest_seq
          WHERE m.valid_from<=? AND (m.valid_to IS NULL OR m.valid_to>?)
            AND m.retracted=0""")
        params += [valid, valid]
        if kind is not None:
            sql += " AND m.kind=?"
            params.append(kind)
        if subject is not None:
            sql += " AND m.subject=?"
            params.append(subject)
        sql += " ORDER BY m.seq DESC LIMIT ?"
        params.append(limit)
        with self._connect() as db:
            rows = db.execute(sql, params).fetchall()
        return [{
            "seq": row["seq"], "tenant": row["tenant"],
            "fact_id": row["fact_id"], "kind": row["kind"],
            "subject": row["subject"], "predicate": row["predicate"],
            "value": json.loads(row["value_json"]),
            "valid_from": row["valid_from"], "valid_to": row["valid_to"],
            "recorded_at": row["recorded_at"], "provenance": row["provenance"],
            "confidence": row["confidence"], "status": "MEMORY_NOT_PROOF",
        } for row in rows]

    def graph(self, *, tenant: str, subject: str,
              valid_at: str | datetime, as_of_seq: int | None = None) -> list[dict]:
        return self.query(tenant=tenant, subject=subject, valid_at=valid_at,
                          as_of_seq=as_of_seq, kind="EDGE")

    def checkpoint(self) -> dict:
        if not self.verify():
            raise MemoryError("MEMORY_INTEGRITY_FAILURE")
        with self._connect() as db:
            row = db.execute("SELECT seq,digest FROM memory_revisions ORDER BY seq DESC LIMIT 1").fetchone()
        return {"system_seq": row["seq"] if row else 0,
                "head_sha256": row["digest"] if row else _GENESIS,
                "mode": "LOGICAL_POINT_IN_TIME_MARKER"}

    def clone_at(self, destination: Path, *, as_of_seq: int) -> "BitemporalGraphMemory":
        if type(as_of_seq) is not int or as_of_seq < 0:
            raise MemoryError("INVALID_SYSTEM_SEQ")
        destination = Path(destination)
        if destination.exists() or destination.is_symlink() or destination == self.path:
            raise MemoryError("RECOVERY_DESTINATION_EXISTS")
        marker = self.checkpoint()
        if as_of_seq > marker["system_seq"]:
            raise MemoryError("RECOVERY_FUTURE_SEQUENCE")
        replica = BitemporalGraphMemory(destination)
        try:
            with self._connect() as source, replica._connect(write=True) as target:
                cols = ("seq", *_COLUMNS, "previous_sha", "digest")
                sql = "INSERT INTO memory_revisions (" + ",".join(cols) + ") VALUES (" + ",".join("?" for _ in cols) + ")"
                for row in source.execute("SELECT * FROM memory_revisions WHERE seq<=? ORDER BY seq", (as_of_seq,)):
                    target.execute(sql, tuple(row[column] for column in cols))
            if not replica.verify():
                raise MemoryError("RECOVERY_INTEGRITY_FAILURE")
        except BaseException:
            # A failed recovery is not a success and must not be used.
            raise
        return replica
