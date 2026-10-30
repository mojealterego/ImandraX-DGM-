"""CoALA-inspired deterministic cognition and offline R2 planning."""
import pytest
from imandrax_dgm.cognitive_memory import BitemporalGraphMemory
from imandrax_dgm.cognition import (
    Thought, GraphOfThoughts, DecisionOption, CognitiveDecisionCycle,
    RouteModel, route_subtasks)

STAMP = "2026-01-01T00:00:00Z"


def memory(tmp_path):
    store = BitemporalGraphMemory(tmp_path / "m.sqlite")
    store.put(tenant="t1", fact_id="obs", kind="EPISODIC",
              subject="agent", predicate="observed", value="test",
              valid_from=STAMP, recorded_at=STAMP,
              request_id="observation", provenance="operator")
    return store


def test_graph_of_thoughts_orders_dependencies_and_refuses_cycles():
    graph = GraphOfThoughts([Thought("b", ("a",), "derived", 0.7),
                             Thought("a", (), "given", 0.9)])
    assert graph.report()["execution_order"] == ["a", "b"]
    with pytest.raises(ValueError, match="CYCLE"):
        GraphOfThoughts([Thought("a", ("b",), "A", 0.8),
                         Thought("b", ("a",), "B", 0.7)])
    with pytest.raises(ValueError, match="UNKNOWN"):
        GraphOfThoughts([Thought("a", ("missing",), "A", 0.8)])


def test_decision_and_reflexion_are_non_executing(tmp_path):
    cycle = CognitiveDecisionCycle(memory(tmp_path))
    result = cycle.decide(tenant="t1", valid_at=STAMP, goal="Choose",
                          options=[DecisionOption("safe", 0.9, 0.9, 0.1, 0.1,
                                                  ("obs",)),
                                   DecisionOption("risky", 0.2, 0.4, 0.8, 0.9)])
    assert result["chosen"] == "safe"
    assert result["status"] == "RECOMMENDATION_ONLY_NOT_EXECUTED"
    cycle.reflect(tenant="t1", event_id="ref-1", expected="safe",
                  observed="failed", correction="review input",
                  valid_at=STAMP, recorded_at="2026-02-01T00:00:00Z",
                  request_id="reflection", provenance="operator")
    logs = cycle.memory.query(tenant="t1", valid_at=STAMP, kind="REFLECTION")
    assert logs[0]["value"]["applied"] is False


def test_generated_summary_provenance_is_explicit(tmp_path):
    cycle = CognitiveDecisionCycle(memory(tmp_path))
    cycle.derive_summary(tenant="t1", valid_at=STAMP, source_ids=["obs"],
                         fact_id="summary", request_id="sum",
                         recorded_at="2026-02-01T00:00:00Z", provenance="local")
    result = cycle.memory.query(tenant="t1", valid_at=STAMP, kind="GENERATIVE")
    assert result[0]["value"]["source_fact_ids"] == ["obs"]
    assert result[0]["value"]["verified"] is False
    with pytest.raises(ValueError, match="UNKNOWN"):
        cycle.derive_summary(tenant="t1", valid_at=STAMP, source_ids=["other"],
                             fact_id="new", request_id="new",
                             recorded_at="2026-02-01T00:00:00Z", provenance="local")


def test_offline_router_never_calls_external_models():
    models = [RouteModel("small", frozenset({"math"}), .7, .1),
              RouteModel("large", frozenset({"math", "code"}), .95, .6)]
    result = route_subtasks(["math", "code"], models, budget=.7)
    assert result["status"] == "OFFLINE_ROUTE_PLAN_NOT_EXECUTED"
    assert [x["model"] for x in result["allocations"]] == ["small", "large"]
    assert route_subtasks(["code"], models, budget=.1)["status"] == "NO_FEASIBLE_ROUTE"


def test_router_rejects_duplicate_tasks_and_invalid_budget():
    models = [RouteModel("m", frozenset({"math"}), .7, .1)]
    with pytest.raises(ValueError, match="INVALID_ROUTE_TASKS"):
        route_subtasks(["math", "math"], models, budget=1)
    with pytest.raises(ValueError, match="INVALID_ROUTE_BUDGET"):
        route_subtasks(["math"], models, budget=float("nan"))
