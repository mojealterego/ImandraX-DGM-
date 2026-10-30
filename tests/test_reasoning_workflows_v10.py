import asyncio
import pytest
from imandrax_dgm.reasoning_workflows import (
    OntologyTool, OntologyRegistry, PlanStep, ReWOOPlanner, TaskError,
    ThoughtBranch, TreeOfThoughts, MultiHopVerifier, critique_and_refine,
)

def test_tree_of_thoughts_beam_prunes_and_never_executes():
    tree = TreeOfThoughts(beam_width=1, max_depth=3)
    result = tree.search([
        ThoughtBranch("root", None, 0, 0.2, ("a",)),
        ThoughtBranch("weak", "root", 1, 0.1, ("a",)),
        ThoughtBranch("strong", "root", 1, 0.9, ("b",)),
        ThoughtBranch("next", "strong", 2, 0.8, ("c",))
    ])
    assert result["best_path"] == ["root", "strong", "next"]
    assert result["status"] == "HEURISTIC_PATH_NOT_PROOF"
    with pytest.raises(TaskError):
        tree.search([ThoughtBranch("root", None, 0, 0.2, ()),
                     ThoughtBranch("loop", "loop", 1, 0.9, ())])

def test_multihop_prevents_false_bridge_and_cross_tenant(tmp_path):
    from imandrax_dgm.cognitive_memory import BitemporalGraphMemory
    db = BitemporalGraphMemory(tmp_path / "memory.db")
    ts = "2026-01-01T00:00:00Z"
    db.put(tenant="t1", fact_id="ab", kind="EDGE", subject="a", predicate="supports",
           value="b", valid_from=ts, request_id="r1", provenance="source")
    db.put(tenant="t1", fact_id="bc", kind="EDGE", subject="b", predicate="supports",
           value="c", valid_from=ts, request_id="r2", provenance="source")
    verifier = MultiHopVerifier(db)
    assert verifier.check(tenant="t1", nodes=["a","b","c"], relation="supports", valid_at=ts)["status"] == "GRAPH_PATH_SUPPORTED_NOT_PROOF"
    assert verifier.check(tenant="t1", nodes=["a","c"], relation="supports", valid_at=ts)["status"] == "BLOCKED_MISSING_BRIDGE"
    assert verifier.check(tenant="t2", nodes=["a","b"], relation="supports", valid_at=ts)["status"] == "BLOCKED_MISSING_BRIDGE"

def test_ontology_dispatch_refuses_unsafe_tool_and_parameter():
    reg=OntologyRegistry([OntologyTool("lookup", "knowledge.retrieve", ("id",), "READ")])
    planner=ReWOOPlanner(reg)
    planner.validate([PlanStep("s1","lookup",{"id":"x"},())])
    with pytest.raises(TaskError):
        planner.validate([PlanStep("s1","shell",{"cmd":"whoami"},())])
    with pytest.raises(TaskError):
        planner.validate([PlanStep("s1","lookup",{"cmd":"whoami"},())])

def test_async_rewoo_order_and_evidence_binding():
    calls=[]
    async def lookup(args):
        calls.append(args["id"])
        await asyncio.sleep(0)
        return {"value": args["id"]}
    reg=OntologyRegistry([OntologyTool("lookup","knowledge.retrieve",("id",),"READ")])
    reg.bind("lookup", lookup)
    p=ReWOOPlanner(reg)
    result=asyncio.run(p.execute([
        PlanStep("a","lookup",{"id":"first"},()),
        PlanStep("b","lookup",{"id":{"$ref":"a","field":"value"}},("a",))
    ], concurrency=2, timeout=1))
    assert [result["results"][x]["value"] for x in ("a","b")] == ["first","first"]
    assert calls==["first","first"]
    assert result["status"]=="READ_ONLY_PLAN_COMPLETED_UNATTESTED"

def test_rewoo_failed_dependency_cannot_be_used():
    async def fail(_): raise RuntimeError("blocked")
    reg=OntologyRegistry([OntologyTool("lookup","knowledge.retrieve",("id",),"READ")])
    reg.bind("lookup",fail)
    p=ReWOOPlanner(reg)
    result=asyncio.run(p.execute([
        PlanStep("a","lookup",{"id":"x"},()),
        PlanStep("b","lookup",{"id":{"$ref":"a","field":"value"}},("a",))
    ], timeout=0.5))
    assert result["status"] == "INCOMPLETE_NO_SIDE_EFFECT"
    assert "b" not in result["results"]

def test_critique_and_refine_returns_only_proposals():
    result=critique_and_refine("initial", [
       {"critique":"needs source","refinement":"candidate2","score":0.8},
       {"critique":"weak","refinement":"candidate3","score":0.5}], max_rounds=2)
    assert result["selected"]=="candidate2"
    assert result["status"]=="DRAFT_NOT_EXECUTED"
    with pytest.raises(TaskError):
       critique_and_refine("initial", [{"critique":"a","refinement":"b","score":float("nan")}])
