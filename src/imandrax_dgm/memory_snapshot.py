"""Offline-owner-signed bitemporal memory snapshot and isolated restoration.

No private key is accepted or handled here. The owner signs the detached
domain-separated manifest OUTSIDE the runtime. The pinned public key and high
water mark must be supplied from an independently trusted location.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .cognitive_memory import BitemporalGraphMemory

_KIND = "OMEGA_BITEMPORAL_SNAPSHOT_V1"
_DOMAIN = b"OMEGA_BITEMPORAL_MEMORY_SIGNED_CHECKPOINT_V1\0"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = frozenset({"schema_version", "kind", "identity_id",
                     "snapshot_sha256", "checkpoint"})


class MemorySnapshotError(ValueError):
    """Snapshot export, verification or rollback precondition failed."""


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise MemorySnapshotError("DUPLICATE_MANIFEST_KEY")
        result[key] = value
    return result


def _check_path(path: Path, *, existing: bool) -> Path:
    path = Path(path)
    if path.is_symlink() or path.parent.is_symlink():
        raise MemorySnapshotError("SYMLINK_PATH_DENIED")
    if existing:
        if not path.is_file():
            raise MemorySnapshotError("SNAPSHOT_FILE_MISSING")
    elif path.exists() or path.is_symlink():
        raise MemorySnapshotError("DESTINATION_EXISTS")
    return path


def _digest_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for piece in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(piece)
    return h.hexdigest()


def _manifest_validate(data: object) -> dict:
    if not isinstance(data, dict) or set(data) != _FIELDS:
        raise MemorySnapshotError("INVALID_MANIFEST_SCHEMA")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise MemorySnapshotError("INVALID_MANIFEST_SCHEMA")
    if data["kind"] != _KIND:
        raise MemorySnapshotError("INVALID_MANIFEST_KIND")
    if not isinstance(data["identity_id"], str) or not _ID.fullmatch(data["identity_id"]):
        raise MemorySnapshotError("INVALID_IDENTITY")
    if not isinstance(data["snapshot_sha256"], str) or not _SHA.fullmatch(data["snapshot_sha256"]):
        raise MemorySnapshotError("INVALID_SNAPSHOT_DIGEST")
    mark = data["checkpoint"]
    if (not isinstance(mark, dict) or set(mark) !=
            {"system_seq", "head_sha256", "mode"} or
            type(mark["system_seq"]) is not int or mark["system_seq"] < 0 or
            not isinstance(mark["head_sha256"], str) or
            not _SHA.fullmatch(mark["head_sha256"]) or
            mark["mode"] != "LOGICAL_POINT_IN_TIME_MARKER"):
        raise MemorySnapshotError("INVALID_CHECKPOINT")
    return data


def signature_message(data: dict) -> bytes:
    """Only the operator's OFFLINE device should sign these canonical bytes."""
    return _DOMAIN + _canonical(_manifest_validate(data))


def _read_manifest(path: Path) -> dict:
    path = _check_path(path, existing=True)
    if path.stat().st_size > 4096:
        raise MemorySnapshotError("OVERSIZED_MANIFEST")
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              MemorySnapshotError("NON_CANONICAL_MANIFEST")))
        return _manifest_validate(data)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MemorySnapshotError("MALFORMED_MANIFEST") from exc


def export_snapshot(memory: BitemporalGraphMemory, *,
                    snapshot: Path, manifest: Path, identity_id: str) -> dict:
    """Consistent SQLite online backup, exported UNsigned for offline owner approval."""
    if not isinstance(memory, BitemporalGraphMemory) or not memory.verify():
        raise MemorySnapshotError("MEMORY_INTEGRITY_FAILURE")
    if not isinstance(identity_id, str) or not _ID.fullmatch(identity_id):
        raise MemorySnapshotError("INVALID_IDENTITY")
    snapshot = _check_path(snapshot, existing=False)
    manifest = _check_path(manifest, existing=False)
    if snapshot.resolve() == manifest.resolve() or snapshot.resolve() == memory.path.resolve():
        raise MemorySnapshotError("SNAPSHOT_SOURCE_COLLISION")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
        # sqlite3.backup takes a consistent snapshot even if the WAL is active.
        with sqlite3.connect(memory.path) as source:
            with sqlite3.connect(snapshot) as destination:
                source.backup(destination)
        backup = BitemporalGraphMemory(snapshot)
        mark = backup.checkpoint()
        data = _manifest_validate({
            "schema_version": 1, "kind": _KIND,
            "identity_id": identity_id,
            "snapshot_sha256": _digest_file(snapshot),
            "checkpoint": mark,
        })
        content = _canonical(data) + b"\n"
        fd = os.open(manifest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        return data
    except BaseException:
        # Never present partial export as a valid backup.
        snapshot.unlink(missing_ok=True)
        manifest.unlink(missing_ok=True)
        raise


def verify_snapshot(*, snapshot: Path, manifest: Path,
                    signature_hex: str, owner_public_key: bytes,
                    expected_identity_id: str, min_system_seq: int = 0) -> dict:
    """Requires externally pinned owner public key and anti-rollback sequence."""
    if type(min_system_seq) is not int or min_system_seq < 0:
        raise MemorySnapshotError("INVALID_HIGHWATER")
    if not isinstance(expected_identity_id, str) or not _ID.fullmatch(expected_identity_id):
        raise MemorySnapshotError("INVALID_IDENTITY")
    snapshot = _check_path(snapshot, existing=True)
    data = _read_manifest(manifest)
    if data["identity_id"] != expected_identity_id:
        raise MemorySnapshotError("WRONG_IDENTITY")
    if data["checkpoint"]["system_seq"] < min_system_seq:
        raise MemorySnapshotError("ROLLBACK_DENIED")
    if not isinstance(owner_public_key, bytes) or len(owner_public_key) != 32:
        raise MemorySnapshotError("INVALID_OWNER_PUBLIC_KEY")
    if not isinstance(signature_hex, str) or not re.fullmatch(r"[0-9a-fA-F]{128}", signature_hex):
        raise MemorySnapshotError("INVALID_SIGNATURE")
    try:
        Ed25519PublicKey.from_public_bytes(owner_public_key).verify(
            bytes.fromhex(signature_hex), signature_message(data))
    except (InvalidSignature, ValueError) as exc:
        raise MemorySnapshotError("SIGNATURE_INVALID") from exc
    if _digest_file(snapshot) != data["snapshot_sha256"]:
        raise MemorySnapshotError("SNAPSHOT_DIGEST_MISMATCH")
    # Open a read-only SQLite handle before the trusted parser. A signed file
    # is still parsed as untrusted database material.
    try:
        with sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True) as db:
            result = db.execute("PRAGMA quick_check").fetchone()
            if result is None or result[0] != "ok":
                raise MemorySnapshotError("SQLITE_INTEGRITY_FAILURE")
        actual = BitemporalGraphMemory(snapshot).checkpoint()
    except (sqlite3.DatabaseError, OSError, ValueError) as exc:
        raise MemorySnapshotError("SNAPSHOT_INTEGRITY_FAILURE") from exc
    if actual != data["checkpoint"]:
        raise MemorySnapshotError("SNAPSHOT_CHECKPOINT_MISMATCH")
    return {"status": "SIGNED_SNAPSHOT_VERIFIED", "identity_id": expected_identity_id,
            "checkpoint": actual, "snapshot_sha256": data["snapshot_sha256"],
            "protection": "OFFLINE_SIGNATURE_WITH_EXTERNAL_HIGHWATER"}


def restore_snapshot(*, snapshot: Path, manifest: Path,
                     signature_hex: str, owner_public_key: bytes,
                     expected_identity_id: str, destination: Path,
                     min_system_seq: int = 0) -> dict:
    """Create an isolated copy; never overwrite or replace a live memory DB."""
    proof = verify_snapshot(snapshot=snapshot, manifest=manifest,
                            signature_hex=signature_hex,
                            owner_public_key=owner_public_key,
                            expected_identity_id=expected_identity_id,
                            min_system_seq=min_system_seq)
    destination = _check_path(destination, existing=False)
    if destination.resolve() in (Path(snapshot).resolve(), Path(manifest).resolve()):
        raise MemorySnapshotError("RECOVERY_SOURCE_COLLISION")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as output, Path(snapshot).open("rb") as source:
            shutil.copyfileobj(source, output, 1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
        if _digest_file(destination) != proof["snapshot_sha256"]:
            raise MemorySnapshotError("RECOVERY_DIGEST_MISMATCH")
        if BitemporalGraphMemory(destination).checkpoint() != proof["checkpoint"]:
            raise MemorySnapshotError("RECOVERY_CHECKPOINT_MISMATCH")
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return {"status": "VERIFIED_COPY_RESTORED_NO_LIVE_REPLACEMENT",
            "path": str(destination), "checkpoint": proof["checkpoint"]}
