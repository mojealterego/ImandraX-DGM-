"""New cognition uses existing IntegratedEngine and shared state directory."""
from pathlib import Path
from imandrax_dgm.engine import IntegratedEngine

ROOT = Path(__file__).resolve().parents[1]
VALID = "2026-10-30T00:00:00Z"


def test_one_engine_facade_persists_cognition_without_apex_digest_change(tmp_path):
    engine = IntegratedEngine(
        knowledge_db=tmp_path / "math.sqlite3",
        inventory=ROOT / "data" / "repositories_public_701.tsv",
        ledger_db=tmp_path / "ledger.sqlite3",
        review_db=tmp_path / "review.sqlite3",
        archive_db=tmp_path / "archive.sqlite3",
    )
    event = engine.memory.put(
        tenant="operator", fact_id="episode-1", kind="EPISODIC",
        subject="imandrax", predicate="experiment", value={"passed": True},
        valid_from=VALID, recorded_at=VALID,
        request_id="episode-1", provenance="operator",
    )
    assert event["seq"] == 1
    assert engine.memory.query(tenant="operator", valid_at=VALID)[0]["value"]["passed"] is True
    assert engine.cognition.memory is engine.memory
    second = IntegratedEngine(
        knowledge_db=tmp_path / "math.sqlite3",
        inventory=ROOT / "data" / "repositories_public_701.tsv",
        ledger_db=tmp_path / "ledger.sqlite3",
        review_db=tmp_path / "review.sqlite3",
        archive_db=tmp_path / "archive.sqlite3",
    )
    assert second.memory.checkpoint() == engine.memory.checkpoint()
