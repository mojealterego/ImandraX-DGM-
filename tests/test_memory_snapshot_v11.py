"""Offline owner-signed durable memory backup / restore contract.

Private Ed25519 signing material exists only inside this test, never in engine.
"""
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from imandrax_dgm.cognitive_memory import BitemporalGraphMemory
from imandrax_dgm.memory_snapshot import (
    MemorySnapshotError, export_snapshot, verify_snapshot, restore_snapshot,
    signature_message,
)

TS = "2026-10-30T00:00:00Z"
IDENTITY = "operator-omega-1"


def signing_key():
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return sk, pk


def build(tmp_path):
    path=tmp_path/"state"/"cognitive_memory.sqlite3"
    memory=BitemporalGraphMemory(path)
    memory.put(tenant="lab",fact_id="episode-1",kind="EPISODIC",
               subject="imandrax",predicate="test",value={"result":"good"},
               valid_from=TS,recorded_at=TS,request_id="event-1",provenance="operator")
    snapshot=tmp_path/"exports"/"snapshot.sqlite3"
    manifest=tmp_path/"exports"/"manifest.json"
    data=export_snapshot(memory,snapshot=snapshot,manifest=manifest,
                         identity_id=IDENTITY)
    sk,pk=signing_key()
    signature=sk.sign(signature_message(data)).hex()
    return memory,snapshot,manifest,data,signature,pk


def test_export_verify_and_restore_signed_backup(tmp_path):
    memory,snapshot,manifest,data,sig,pk=build(tmp_path)
    result=verify_snapshot(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                           owner_public_key=pk,expected_identity_id=IDENTITY,
                           min_system_seq=1)
    assert result["status"]=="SIGNED_SNAPSHOT_VERIFIED"
    recovered=restore_snapshot(snapshot=snapshot,manifest=manifest,
                               signature_hex=sig,owner_public_key=pk,
                               expected_identity_id=IDENTITY,min_system_seq=1,
                               destination=tmp_path/"recovered"/"memory.sqlite3")
    assert recovered["status"]=="VERIFIED_COPY_RESTORED_NO_LIVE_REPLACEMENT"
    assert BitemporalGraphMemory(tmp_path/"recovered"/"memory.sqlite3").query(
        tenant="lab",valid_at=TS)[0]["value"]=={"result":"good"}
    assert memory.checkpoint()["system_seq"]==1


def test_export_rejects_existing_destination(tmp_path):
    memory,snapshot,manifest,data,sig,pk=build(tmp_path)
    with pytest.raises(MemorySnapshotError,match="DESTINATION_EXISTS"):
        export_snapshot(memory,snapshot=snapshot,manifest=manifest,
                        identity_id=IDENTITY)
    with pytest.raises(MemorySnapshotError,match="DESTINATION_EXISTS"):
        restore_snapshot(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                         owner_public_key=pk,expected_identity_id=IDENTITY,
                         min_system_seq=1,destination=snapshot)


def test_signature_forgery_and_identity_mismatch_fail_closed(tmp_path):
    memory,snapshot,manifest,data,sig,pk=build(tmp_path)
    other_sk,other_pk=signing_key()
    for kwargs in (
        {"owner_public_key":other_pk},
        {"signature_hex":"00"*64},
        {"expected_identity_id":"another-identity"},
        {"min_system_seq":2},
    ):
        args=dict(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                  owner_public_key=pk,expected_identity_id=IDENTITY,min_system_seq=1)
        args.update(kwargs)
        with pytest.raises(MemorySnapshotError):
            verify_snapshot(**args)


def test_snapshot_byte_tamper_detected(tmp_path):
    memory,snapshot,manifest,data,sig,pk=build(tmp_path)
    with open(snapshot,"r+b") as f:
        f.seek(120)
        original=f.read(1)
        f.seek(120)
        f.write(bytes([original[0]^1]))
    with pytest.raises(MemorySnapshotError,match="SNAPSHOT_DIGEST_MISMATCH"):
        verify_snapshot(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                        owner_public_key=pk,expected_identity_id=IDENTITY,
                        min_system_seq=1)


def test_manifest_mutation_and_duplicate_keys_detected(tmp_path):
    memory,snapshot,manifest,data,sig,pk=build(tmp_path)
    forged=dict(data,identity_id="fake")
    manifest.write_text(json.dumps(forged))
    with pytest.raises(MemorySnapshotError):
        verify_snapshot(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                        owner_public_key=pk,expected_identity_id=IDENTITY)
    manifest.write_text('{"schema_version":1,"schema_version":2}')
    with pytest.raises(MemorySnapshotError):
        verify_snapshot(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                        owner_public_key=pk,expected_identity_id=IDENTITY)


def test_externally_pinned_highwater_blocks_history_rollback(tmp_path):
    memory,snapshot,manifest,data,sig,pk=build(tmp_path)
    memory.put(tenant="lab",fact_id="episode-2",kind="EPISODIC",
               subject="imandrax",predicate="test",value="new",
               valid_from=TS,request_id="event-2",provenance="operator")
    assert memory.checkpoint()["system_seq"]==2
    with pytest.raises(MemorySnapshotError,match="ROLLBACK_DENIED"):
        verify_snapshot(snapshot=snapshot,manifest=manifest,signature_hex=sig,
                        owner_public_key=pk,expected_identity_id=IDENTITY,
                        min_system_seq=memory.checkpoint()["system_seq"])
