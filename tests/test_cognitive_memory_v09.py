"""Bitemporal facts, graph isolation, append-only history, logical recovery."""
from datetime import datetime, timezone
import sqlite3

import pytest

from imandrax_dgm.cognitive_memory import BitemporalGraphMemory, MemoryError

D0 = "2026-01-01T00:00:00Z"
D1 = "2026-02-01T00:00:00Z"
D2 = "2026-03-01T00:00:00Z"


def add(memory, **changes):
    args = dict(tenant="team-a", fact_id="fact-1", kind="SEMANTIC",
                subject="engine", predicate="version", value="v1",
                valid_from=D0, recorded_at=D1, request_id="req-1", provenance="operator")
    args.update(changes)
    return memory.put(**args)


def test_valid_time_and_recorded_time_are_independent(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "memory.sqlite3")
    first = add(memory)
    second = add(memory, value="corrected", recorded_at=D2, request_id="req-2",
                 expected_seq=first["seq"])
    assert second["seq"] > first["seq"]
    assert memory.query(tenant="team-a", valid_at=D0, system_at=D1)[0]["value"] == "v1"
    assert memory.query(tenant="team-a", valid_at=D0, system_at=D2)[0]["value"] == "corrected"
    assert memory.query(tenant="team-a", valid_at=D0, as_of_seq=first["seq"])[0]["value"] == "v1"
    assert memory.verify()


def test_validity_interval_and_retraction(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "m.sqlite")
    first = add(memory, valid_to=D1, recorded_at=D0)
    assert memory.query(tenant="team-a", valid_at=D1) == []
    assert memory.query(tenant="team-a", valid_at=D0)
    add(memory, value=None, retracted=True, request_id="req-2", recorded_at=D2,
        expected_seq=first["seq"])
    assert memory.query(tenant="team-a", valid_at=D0) == []


def test_graph_is_tenant_scoped(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "m.sqlite")
    memory.put(tenant="team-a", fact_id="link", kind="EDGE",
               subject="a", predicate="depends_on", value="b",
               valid_from=D0, request_id="edge-a", provenance="source")
    assert memory.graph(tenant="team-a", subject="a", valid_at=D1)[0]["value"] == "b"
    assert memory.graph(tenant="team-b", subject="a", valid_at=D1) == []
    with pytest.raises(MemoryError, match="INVALID_EDGE_TARGET"):
        memory.put(tenant="team-a", fact_id="x", kind="EDGE",
                   subject="a", predicate="depends_on", value="../etc/passwd",
                   valid_from=D0, request_id="bad", provenance="source")


def test_idempotency_and_optimistic_conflict(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "m.sqlite")
    first = add(memory)
    assert add(memory, recorded_at=D2)["status"] == "ALREADY_RECORDED"
    with pytest.raises(MemoryError, match="IDEMPOTENCY_CONFLICT"):
        add(memory, value="wrong")
    with pytest.raises(MemoryError, match="REVISION_CONFLICT"):
        add(memory, request_id="req-3", value="new", recorded_at=D2)
    assert first["seq"] == memory.checkpoint()["system_seq"]


def test_clone_pit_recovery_preserves_previous_state(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "m.sqlite")
    first = add(memory)
    add(memory, value="v2", expected_seq=first["seq"], recorded_at=D2, request_id="req-2")
    clone = memory.clone_at(tmp_path / "recovered.sqlite", as_of_seq=first["seq"])
    assert clone.checkpoint()["system_seq"] == first["seq"]
    assert clone.query(tenant="team-a", valid_at=D0)[0]["value"] == "v1"
    assert memory.query(tenant="team-a", valid_at=D0)[0]["value"] == "v2"


def test_local_history_rejects_mutation_and_corruption(tmp_path):
    path = tmp_path / "m.sqlite"
    memory = BitemporalGraphMemory(path)
    add(memory)
    with sqlite3.connect(path) as db:
        with pytest.raises(sqlite3.DatabaseError):
            db.execute("DELETE FROM memory_revisions")
        db.execute("DROP TRIGGER memory_no_update")
        db.execute("UPDATE memory_revisions SET value_json='\"forged\"' WHERE seq=1")
    assert not memory.verify()
    with pytest.raises(MemoryError, match="MEMORY_INTEGRITY_FAILURE"):
        memory.query(tenant="team-a", valid_at=D0)


def test_malformed_input_and_clock_regression_are_rejected(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "m.sqlite")
    add(memory)
    for args in [
        {"kind": "SYSTEM"},
        {"tenant": "../wrong"},
        {"valid_from": "2026-01-01"},
        {"valid_to": D0},
        {"confidence": float("nan")},
        {"value": "X" * 9000},
        {"recorded_at": D0, "request_id": "different"},
    ]:
        with pytest.raises(MemoryError):
            add(memory, **args)


def test_recover_rejects_existing_destination_and_future_position(tmp_path):
    memory = BitemporalGraphMemory(tmp_path / "m.sqlite")
    with pytest.raises(MemoryError, match="RECOVERY_FUTURE_SEQUENCE"):
        memory.clone_at(tmp_path / "out.sqlite", as_of_seq=1)
    (tmp_path / "existing.sqlite").write_bytes(b"existing")
    with pytest.raises(MemoryError, match="RECOVERY_DESTINATION_EXISTS"):
        memory.clone_at(tmp_path / "existing.sqlite", as_of_seq=0)
