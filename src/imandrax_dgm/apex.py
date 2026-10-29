"""OMEGA Unified APEX: deterministic, deny-by-default multi-engine control fabric.

Apex is *not* an autonomous release authority, a dynamic plugin loader, or a
conscious entity. It is a versioned capability router and an inspectable event
journal for trusted, explicitly bound in-process adapters. New engines remain
untrusted descriptors until a reviewed adapter is bound by application code.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Callable, Mapping
from uuid import uuid4

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_ENGINE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_CAPABILITY = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_FIELD = re.compile(r"^[a-z][a-z0-9_]*$")
_VERSION = re.compile(r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_ACCESS = frozenset({"READ", "RESEARCH", "MUTATION", "AUTHORITY"})
_PROTECTED_RESPONSE_KEYS = frozenset({"deploy", "deployed", "merge", "auto_merge", "apply_patch", "self_approved", "code_applied"})
_MAX_INPUT_BYTES = 16384
_MAX_OUTPUT_BYTES = 65536


class ApexError(ValueError):
    """A refused operation, invalid contract, or tampered persisted state."""


def _canonical(obj: object) -> bytes:
    try:
        raw = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ApexError("NON_CANONICAL_JSON") from exc
    return raw


def _sha(obj: object) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


@dataclass(frozen=True)
class Capability:
    name: str
    access: str
    input_fields: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.name, str) or len(self.name) > 120 or not _CAPABILITY.fullmatch(self.name):
            raise ApexError("INVALID_CAPABILITY")
        if self.access not in _ACCESS:
            raise ApexError("INVALID_ACCESS_MODE")
        if not isinstance(self.input_fields, tuple) or len(self.input_fields) > 32:
            raise ApexError("INVALID_INPUT_FIELDS")
        if any(not isinstance(x, str) or not _FIELD.fullmatch(x) for x in self.input_fields):
            raise ApexError("INVALID_INPUT_FIELDS")
        if len(set(self.input_fields)) != len(self.input_fields):
            raise ApexError("INVALID_INPUT_FIELDS")


@dataclass(frozen=True)
class EngineManifest:
    engine_id: str
    version: str
    capabilities: tuple[Capability, ...]
    dependencies: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.engine_id, str) or len(self.engine_id) > 64 or not _ENGINE.fullmatch(self.engine_id):
            raise ApexError("INVALID_ENGINE_ID")
        if not isinstance(self.version, str) or not _VERSION.fullmatch(self.version) or len(self.version) > 40:
            raise ApexError("INVALID_VERSION")
        if not isinstance(self.capabilities, tuple) or not self.capabilities or len(self.capabilities) > 128:
            raise ApexError("INVALID_CAPABILITIES")
        names = []
        for cap in self.capabilities:
            if not isinstance(cap, Capability) or not cap.name.startswith(self.engine_id + "."):
                raise ApexError("CAPABILITY_NAMESPACE_MISMATCH")
            names.append(cap.name)
        if len(set(names)) != len(names):
            raise ApexError("DUPLICATE_CAPABILITY")
        if not isinstance(self.dependencies, tuple) or len(self.dependencies) > 32 or len(set(self.dependencies)) != len(self.dependencies):
            raise ApexError("INVALID_DEPENDENCIES")
        if any(not isinstance(d, str) or not _ENGINE.fullmatch(d) or d == self.engine_id for d in self.dependencies):
            raise ApexError("INVALID_DEPENDENCIES")

    def descriptor(self) -> dict:
        return {"engine_id": self.engine_id, "version": self.version,
                "capabilities": [{"name": c.name, "access": c.access,
                                  "input_fields": list(c.input_fields)} for c in self.capabilities],
                "dependencies": list(self.dependencies)}


class ApexRegistry:
    """Only trusted application code binds handlers; no import-by-name or eval."""

    def __init__(self):
        self._engines: dict[str, EngineManifest] = {}
        self._bound: dict[str, Callable[[Mapping], object]] = {}
        self._frozen = False
        self._order: tuple[EngineManifest, ...] = ()

    def register(self, manifest: EngineManifest):
        if self._frozen:
            raise ApexError("REGISTRY_FROZEN")
        if not isinstance(manifest, EngineManifest):
            raise ApexError("INVALID_MANIFEST")
        if manifest.engine_id in self._engines:
            raise ApexError("DUPLICATE_ENGINE")
        self._engines[manifest.engine_id] = manifest

    def bind(self, capability: str, handler: Callable[[Mapping], object]):
        if self._frozen:
            raise ApexError("REGISTRY_FROZEN")
        if not callable(handler):
            raise ApexError("INVALID_HANDLER")
        declared = {c.name for m in self._engines.values() for c in m.capabilities}
        if capability not in declared or capability in self._bound:
            raise ApexError("UNKNOWN_OR_DUPLICATE_BINDING")
        self._bound[capability] = handler

    def freeze(self) -> tuple[EngineManifest, ...]:
        if self._frozen:
            return self._order
        result: list[EngineManifest] = []
        active: set[str] = set()
        done: set[str] = set()

        def visit(engine_id: str):
            if engine_id in active:
                raise ApexError("DEPENDENCY_CYCLE")
            if engine_id in done:
                return
            if engine_id not in self._engines:
                raise ApexError("MISSING_DEPENDENCY")
            active.add(engine_id)
            manifest = self._engines[engine_id]
            for dependency in sorted(manifest.dependencies):
                visit(dependency)
            active.remove(engine_id)
            done.add(engine_id)
            result.append(manifest)

        for engine_id in sorted(self._engines):
            visit(engine_id)
        if not result:
            raise ApexError("EMPTY_REGISTRY")
        self._order = tuple(result)
        self._frozen = True
        return self._order

    @property
    def manifest_digest(self) -> str:
        return _sha([m.descriptor() for m in self.freeze()])

    def resolve(self, capability: str) -> tuple[Capability, Callable | None]:
        for engine in self.freeze():
            for cap in engine.capabilities:
                if cap.name == capability:
                    return cap, self._bound.get(capability)
        raise ApexError("UNKNOWN_CAPABILITY")


@dataclass(frozen=True)
class ApexRequest:
    capability: str
    payload: dict
    principal: str
    request_id: str


def canonical_upgrade_message(identity_id: str, old_digest: str, new_digest: str, epoch: int) -> bytes:
    """Precisely scoped, domain-separated message to be signed OFFLINE by the owner."""
    if (not isinstance(identity_id, str) or not identity_id or
            not all(isinstance(x, str) and re.fullmatch(r"[a-f0-9]{64}", x)
                    for x in (old_digest, new_digest)) or
            old_digest == new_digest or type(epoch) is not int or epoch < 1):
        raise ApexError("INVALID_UPGRADE_MESSAGE")
    return _canonical({"kind": "OMEGA_APEX_MANIFEST_UPGRADE_V1", "identity_id": identity_id,
                       "from": old_digest, "to": new_digest, "epoch": epoch})


class ApexAudit:
    """Hash-chained local journal; not a WORM store or remote attestation."""

    def __init__(self, path: Path, manifest_digest: str, *, owner_public_key: bytes | None = None):
        self.owner_public_key = owner_public_key
        self.path = Path(path)
        if self.path.is_symlink():
            raise ApexError("SYMLINK_STATE_DENIED")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS metadata (
                  k TEXT PRIMARY KEY, v TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_json TEXT NOT NULL,
                  previous_hash TEXT NOT NULL,
                  event_digest TEXT NOT NULL,
                  request_id TEXT UNIQUE
                );
                CREATE TRIGGER IF NOT EXISTS apex_events_no_update BEFORE UPDATE ON events
                BEGIN SELECT RAISE(ABORT, 'apex events append-only'); END;
                CREATE TRIGGER IF NOT EXISTS apex_events_no_delete BEFORE DELETE ON events
                BEGIN SELECT RAISE(ABORT, 'apex events append-only'); END;
            """)
            existing = dict(con.execute("SELECT k,v FROM metadata").fetchall())
            fingerprint = (hashlib.sha256(owner_public_key).hexdigest()
                           if isinstance(owner_public_key, bytes) and len(owner_public_key) == 32
                           else "")
            if owner_public_key is not None and not fingerprint:
                raise ApexError("INVALID_OWNER_KEY")
            if not existing:
                con.executemany("INSERT INTO metadata (k,v) VALUES (?,?)", [
                    ("identity_id", str(uuid4())), ("manifest_digest", manifest_digest),
                    ("initial_manifest_digest", manifest_digest), ("state", "CREATED"),
                    ("epoch", "0"), ("owner_key_digest", fingerprint)])
            elif (existing.get("manifest_digest") != manifest_digest or
                  existing.get("state") not in {"CREATED", "ACTIVE", "PAUSED", "STOPPED"} or
                  not existing.get("identity_id")):
                raise ApexError("MANIFEST_DRIFT")
            elif fingerprint and existing.get("owner_key_digest") != fingerprint:
                raise ApexError("TRUST_ROOT_DRIFT")
        if not self.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path, timeout=10)
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def meta(self) -> dict:
        with self._connect() as con:
            return dict(con.execute("SELECT k,v FROM metadata").fetchall())

    def has_request(self, request_id: str) -> bool:
        with self._connect() as con:
            return con.execute("SELECT 1 FROM events WHERE request_id=?", (request_id,)).fetchone() is not None

    @staticmethod
    def _append_tx(con: sqlite3.Connection, *, kind: str, principal: str,
                   capability: str = "", request_id: str | None = None,
                   input_digest: str = "", output_digest: str = "",
                   context: dict | None = None) -> str:
        previous = con.execute("SELECT event_digest FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        prev_hash = previous[0] if previous else "0" * 64
        event = {"kind": kind, "principal_digest": hashlib.sha256(principal.encode()).hexdigest(),
                 "capability": capability, "input_digest": input_digest,
                 "output_digest": output_digest,
                 "occurred_at": datetime.now(timezone.utc).isoformat(),
                 "identity_id": con.execute("SELECT v FROM metadata WHERE k='identity_id'").fetchone()[0]}
        if context is not None:
            event["context"] = context
        digest = _sha({"event": event, "previous_hash": prev_hash, "request_id": request_id})
        try:
            con.execute("INSERT INTO events (event_json,previous_hash,event_digest,request_id) VALUES (?,?,?,?)",
                        (_canonical(event).decode(), prev_hash, digest, request_id))
        except sqlite3.IntegrityError as exc:
            raise ApexError("DUPLICATE_REQUEST") from exc
        return digest

    def append(self, *, kind: str, principal: str, capability: str = "",
               request_id: str | None = None, input_digest: str = "", output_digest: str = "") -> str:
        if not all(isinstance(x, str) for x in (kind, principal, capability, input_digest, output_digest)):
            raise ApexError("INVALID_AUDIT_EVENT")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            return self._append_tx(con, kind=kind, principal=principal,
                                   capability=capability, request_id=request_id,
                                   input_digest=input_digest, output_digest=output_digest)

    def transition(self, old: str, new: str):
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            current = con.execute("SELECT v FROM metadata WHERE k='state'").fetchone()[0]
            if current != old:
                raise ApexError("INVALID_TRANSITION")
            con.execute("UPDATE metadata SET v=? WHERE k='state'", (new,))
            self._append_tx(con, kind="LIFECYCLE_" + new, principal="LOCAL_OPERATOR")

    def upgrade_manifest(self, new_digest: str, *, signature_hex: str,
                         owner_public_key: bytes):
        """Signed, paused-only manifest evolution with stable platform identity.

        No agent, proposer or runtime can produce this Ed25519 approval signature.
        The public key must match the out-of-band pinned trust root.
        """
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            meta = dict(con.execute("SELECT k,v FROM metadata").fetchall())
            if not meta.get("owner_key_digest"):
                raise ApexError("OWNER_TRUST_ROOT_MISSING")
            if meta.get("state") != "PAUSED":
                raise ApexError("NOT_PAUSED")
            if (not isinstance(owner_public_key, bytes) or len(owner_public_key) != 32 or
                    hashlib.sha256(owner_public_key).hexdigest() != meta["owner_key_digest"]):
                raise ApexError("TRUST_ROOT_DRIFT")
            try:
                msg = canonical_upgrade_message(meta["identity_id"], meta["manifest_digest"],
                                                new_digest, int(meta["epoch"]) + 1)
                Ed25519PublicKey.from_public_bytes(owner_public_key).verify(bytes.fromhex(signature_hex), msg)
            except (InvalidSignature, ValueError, TypeError, ApexError) as exc:
                raise ApexError("INVALID_OWNER_SIGNATURE") from exc
            next_epoch = int(meta["epoch"]) + 1
            self._append_tx(con, kind="MANIFEST_UPGRADE", principal="OFFLINE_OWNER_SIGNER",
                            context={"from": meta["manifest_digest"], "to": new_digest,
                                     "epoch": next_epoch, "signature": signature_hex})
            con.execute("UPDATE metadata SET v=? WHERE k='manifest_digest'", (new_digest,))
            con.execute("UPDATE metadata SET v=? WHERE k='epoch'", (str(next_epoch),))
        if not self.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")

    def count(self) -> int:
        with self._connect() as con:
            return con.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def verify(self) -> bool:
        with self._connect() as con:
            rows = con.execute("SELECT seq,event_json,previous_hash,event_digest,request_id FROM events ORDER BY seq").fetchall()
            metadata = dict(con.execute("SELECT k,v FROM metadata").fetchall())
        previous = "0" * 64
        state = "CREATED"
        epoch = 0
        manifest = metadata.get("initial_manifest_digest", "")
        for expected_seq, (seq, raw, prev, digest, req_id) in enumerate(rows, start=1):
            try:
                record = json.loads(raw)
            except (ValueError, TypeError):
                return False
            if (seq != expected_seq or prev != previous or
                    record.get("identity_id") != metadata.get("identity_id") or
                    digest != _sha({"event": record, "previous_hash": previous, "request_id": req_id})):
                return False
            event = record.get("kind", "")
            if event == "LIFECYCLE_ACTIVE":
                if state not in {"CREATED", "PAUSED"}:
                    return False
                state = "ACTIVE"
            elif event == "LIFECYCLE_PAUSED":
                if state != "ACTIVE":
                    return False
                state = "PAUSED"
            elif event == "LIFECYCLE_STOPPED":
                if state not in {"ACTIVE", "PAUSED"}:
                    return False
                state = "STOPPED"
            elif event == "MANIFEST_UPGRADE":
                ctx = record.get("context", {})
                if (state != "PAUSED" or ctx.get("from") != manifest or
                        ctx.get("epoch") != epoch + 1 or
                        not isinstance(ctx.get("to"), str)):
                    return False
                if self.owner_public_key:
                    try:
                        msg = canonical_upgrade_message(metadata["identity_id"],
                                                        manifest, ctx["to"], epoch + 1)
                        Ed25519PublicKey.from_public_bytes(self.owner_public_key).verify(
                            bytes.fromhex(ctx["signature"]), msg)
                    except (KeyError, ValueError, InvalidSignature, TypeError):
                        return False
                manifest = ctx["to"]
                epoch += 1
            previous = digest
        return (state == metadata.get("state") and str(epoch) == metadata.get("epoch")
                and manifest == metadata.get("manifest_digest"))


class ApexRuntime:
    """One stateful, inspectable fabric for explicitly mounted engine adapters."""

    def __init__(self, registry: ApexRegistry, database: Path, *, enable_research: bool = False,
                 owner_public_key: bytes | None = None):
        if not isinstance(registry, ApexRegistry):
            raise ApexError("INVALID_REGISTRY")
        self.registry = registry
        self.registry.freeze()
        self.audit = ApexAudit(database, registry.manifest_digest, owner_public_key=owner_public_key)
        self.enable_research = enable_research is True

    def status(self) -> dict:
        if not self.audit.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")
        metadata = self.audit.meta()
        return {"identity_id": metadata["identity_id"], "state": metadata["state"],
                "epoch": int(metadata["epoch"]),
                "manifest_digest": self.registry.manifest_digest,
                "engines": [m.engine_id for m in self.registry.freeze()],
                "capabilities": sorted(c.name for m in self.registry.freeze() for c in m.capabilities),
                "audit_events": self.audit.count(), "auto_merge": False,
                "auto_deploy": False, "claims_consciousness": False}

    def start(self):
        if not self.audit.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")
        state = self.audit.meta()["state"]
        if state not in {"CREATED", "PAUSED"}:
            raise ApexError("INVALID_TRANSITION")
        self.audit.transition(state, "ACTIVE")

    def pause(self):
        if not self.audit.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")
        self.audit.transition("ACTIVE", "PAUSED")

    def stop(self):
        if not self.audit.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")
        state = self.audit.meta()["state"]
        if state not in {"ACTIVE", "PAUSED"}:
            raise ApexError("INVALID_TRANSITION")
        self.audit.transition(state, "STOPPED")

    @staticmethod
    def _unsafe_result(value: object) -> bool:
        if isinstance(value, dict):
            if isinstance(value.get("state"), str) and value["state"] in {"APPROVED", "MERGED", "DEPLOYED", "RELEASED"}:
                return True
            for key, val in value.items():
                if str(key).casefold() in _PROTECTED_RESPONSE_KEYS and val not in (False, None, "", 0):
                    return True
                if ApexRuntime._unsafe_result(val):
                    return True
        if isinstance(value, list):
            return any(ApexRuntime._unsafe_result(x) for x in value)
        return False

    def dispatch(self, request: ApexRequest) -> dict:
        if not self.audit.verify():
            raise ApexError("AUDIT_INTEGRITY_FAILURE")
        if not isinstance(request, ApexRequest) or not isinstance(request.capability, str) or not _CAPABILITY.fullmatch(request.capability):
            raise ApexError("INVALID_REQUEST")
        if (not isinstance(request.request_id, str) or not _IDENTIFIER.fullmatch(request.request_id) or
                not isinstance(request.principal, str) or not _IDENTIFIER.fullmatch(request.principal)):
            raise ApexError("INVALID_REQUEST")
        if self.audit.has_request(request.request_id):
            raise ApexError("DUPLICATE_REQUEST")
        if self.audit.meta()["state"] != "ACTIVE":
            self.audit.append(kind="DENIED_NOT_ACTIVE", principal=request.principal,
                              capability=request.capability, request_id=request.request_id)
            raise ApexError("NOT_ACTIVE")
        cap, handler = self.registry.resolve(request.capability)
        if (not isinstance(request.payload, dict) or set(request.payload) != set(cap.input_fields)):
            self.audit.append(kind="DENIED_BAD_INPUT", principal=request.principal,
                              capability=request.capability, request_id=request.request_id)
            raise ApexError("INVALID_PAYLOAD")
        try:
            raw = _canonical(request.payload)
        except ApexError as exc:
            raise ApexError("INVALID_PAYLOAD") from exc
        if len(raw) > _MAX_INPUT_BYTES:
            raise ApexError("INVALID_PAYLOAD")
        input_digest = hashlib.sha256(raw).hexdigest()
        if cap.access in {"AUTHORITY", "MUTATION"}:
            self.audit.append(kind="DENIED_PROTECTED", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("PROTECTED_CAPABILITY")
        if cap.access == "RESEARCH" and not self.enable_research:
            self.audit.append(kind="DENIED_RESEARCH_DISABLED", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("RESEARCH_DISABLED")
        if handler is None:
            self.audit.append(kind="DENIED_UNBOUND", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("UNBOUND_CAPABILITY")
        try:
            output = handler(dict(request.payload))
        except Exception as exc:
            self.audit.append(kind="HANDLER_FAILED", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("HANDLER_FAILED") from exc
        try:
            encoded = _canonical(output)
        except ApexError as exc:
            self.audit.append(kind="INVALID_RESULT", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("INVALID_RESULT") from exc
        if len(encoded) > _MAX_OUTPUT_BYTES:
            self.audit.append(kind="INVALID_RESULT", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("INVALID_RESULT")
        if cap.access == "RESEARCH" and self._unsafe_result(output):
            self.audit.append(kind="DENIED_UNSAFE_RESULT", principal=request.principal,
                              capability=cap.name, request_id=request.request_id,
                              input_digest=input_digest)
            raise ApexError("UNSAFE_RESULT")
        result_digest = hashlib.sha256(encoded).hexdigest()
        event_hash = self.audit.append(kind="OBSERVED", principal=request.principal,
                                       capability=cap.name, request_id=request.request_id,
                                       input_digest=input_digest, output_digest=result_digest)
        return {"status": "OBSERVED", "capability": cap.name, "output": output,
                "event_hash": event_hash, "identity_id": self.audit.meta()["identity_id"],
                "release_authority": "NONE"}
