"""Integration against the actual in-repository ImandraX/DGM facade, not mocks."""
from pathlib import Path
from imandrax_dgm.apex import ApexRequest, ApexRuntime, ApexError
from imandrax_dgm.apex_integrations import attach_unified_engine
from imandrax_dgm.engine import IntegratedEngine

ROOT = Path(__file__).resolve().parents[1]


def test_apex_routes_real_exact_math_and_dgm_without_approval(tmp_path):
    engine = IntegratedEngine(
        knowledge_db=tmp_path / "unused_knowledge.sqlite3",
        inventory=ROOT / "data" / "repositories_public_701.tsv",
        ledger_db=tmp_path / "ledger.sqlite3",
        review_db=tmp_path / "review.sqlite3",
        archive_db=tmp_path / "archive.sqlite3",
    )
    runtime = ApexRuntime(attach_unified_engine(engine), tmp_path / "apex.sqlite3")
    runtime.start()
    result = runtime.dispatch(ApexRequest("imandrax.math", {
        "operation": "gcd", "arguments": {"a": 84, "b": 18}}, "owner", "math-e2e-01"))
    assert result["output"]["value"] == 6
    assert result["output"]["proof_status"] == "NOT_FORMALLY_PROVED"
    history = runtime.dispatch(ApexRequest("dgm.history", {}, "owner", "dgm-e2e-01"))
    assert history["output"]["status"] == "RESEARCH_ONLY_UNAPPROVED"
    assert runtime.audit.verify()
