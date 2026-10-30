"""CoALA-inspired bounded cognition. Advisory only: no tools, deployment or LLM calls."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any, Sequence

from .cognitive_memory import BitemporalGraphMemory, MemoryError

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}\Z")


def _unit(number: object, key: str) -> float:
    if type(number) not in (int, float) or not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError("INVALID_" + key)
    return float(number)


@dataclass(frozen=True)
class Thought:
    thought_id: str
    parents: tuple[str, ...]
    claim: str
    confidence: float

    def __post_init__(self):
        if not isinstance(self.thought_id, str) or not _NAME.fullmatch(self.thought_id):
            raise ValueError("INVALID_THOUGHT_ID")
        if (not isinstance(self.parents, tuple) or
                any(not isinstance(x, str) or not _NAME.fullmatch(x) for x in self.parents)):
            raise ValueError("INVALID_THOUGHT_PARENTS")
        if (not isinstance(self.claim, str) or
                not 1 <= len(self.claim) <= 2000 or "\x00" in self.claim):
            raise ValueError("INVALID_THOUGHT_CLAIM")
        _unit(self.confidence, "THOUGHT_CONFIDENCE")


class GraphOfThoughts:
    """Data-only DAG validation; not generative model reasoning."""

    def __init__(self, thoughts: Sequence[Thought]):
        if not isinstance(thoughts, (list, tuple)) or not 1 <= len(thoughts) <= 32:
            raise ValueError("INVALID_THOUGHT_COUNT")
        self._thoughts = {t.thought_id: t for t in thoughts if isinstance(t, Thought)}
        if len(self._thoughts) != len(thoughts):
            raise ValueError("DUPLICATE_OR_INVALID_THOUGHT")
        state: dict[str, int] = {}
        order: list[str] = []

        def visit(node: str):
            if node not in self._thoughts:
                raise ValueError("UNKNOWN_THOUGHT_DEPENDENCY")
            if state.get(node) == 1:
                raise ValueError("THOUGHT_GRAPH_CYCLE")
            if state.get(node) == 2:
                return
            state[node] = 1
            for parent in self._thoughts[node].parents:
                visit(parent)
            state[node] = 2
            order.append(node)

        for ident in sorted(self._thoughts):
            visit(ident)
        self.order = tuple(order)

    def report(self) -> dict:
        return {"status": "UNVERIFIED_THOUGHT_GRAPH",
                "execution_order": list(self.order), "total": len(self.order),
                "claims": [
                    {"id": ident, "claim": self._thoughts[ident].claim,
                     "confidence": self._thoughts[ident].confidence,
                     "parents": list(self._thoughts[ident].parents)}
                    for ident in self.order]}


@dataclass(frozen=True)
class DecisionOption:
    option_id: str
    relevance: float
    evidence_coverage: float
    estimated_cost: float
    risk: float
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.option_id, str) or not _NAME.fullmatch(self.option_id):
            raise ValueError("INVALID_OPTION_ID")
        for key in ("relevance", "evidence_coverage", "estimated_cost", "risk"):
            _unit(getattr(self, key), key.upper())
        if (not isinstance(self.evidence_refs, tuple) or len(self.evidence_refs) > 16 or
                any(not isinstance(x, str) or not _NAME.fullmatch(x) for x in self.evidence_refs)):
            raise ValueError("INVALID_EVIDENCE_REFS")


class CognitiveDecisionCycle:
    """Working-memory read, decision and retrospective reflection."""

    def __init__(self, memory: BitemporalGraphMemory):
        self.memory = memory

    def decide(self, *, tenant: str, valid_at: str, goal: str,
               options: Sequence[DecisionOption], limit: int = 8) -> dict:
        if not isinstance(goal, str) or not 1 <= len(goal) <= 2048:
            raise ValueError("INVALID_GOAL")
        if not isinstance(options, (list, tuple)) or not 1 <= len(options) <= 16:
            raise ValueError("INVALID_OPTIONS")
        if len({o.option_id for o in options}) != len(options):
            raise ValueError("DUPLICATE_OPTIONS")
        if any(not isinstance(o, DecisionOption) for o in options):
            raise ValueError("INVALID_OPTIONS")
        notes = self.memory.query(tenant=tenant, valid_at=valid_at, limit=limit)
        known = {row["fact_id"] for row in notes}
        assessments = []
        for option in options:
            if not set(option.evidence_refs).issubset(known):
                raise ValueError("UNKNOWN_OR_OUT_OF_SCOPE_EVIDENCE")
            score = (0.45 * option.relevance + 0.35 * option.evidence_coverage
                     - 0.1 * option.estimated_cost - 0.1 * option.risk)
            assessments.append({"option_id": option.option_id,
                                "score": round(score, 6),
                                "evidence_refs": list(option.evidence_refs)})
        assessments.sort(key=lambda r: (-r["score"], r["option_id"]))
        return {"status": "RECOMMENDATION_ONLY_NOT_EXECUTED",
                "goal": goal, "chosen": assessments[0]["option_id"],
                "ranked": assessments, "working_memory_count": len(notes),
                "evidence_status": "UNVERIFIED_LOCAL_MEMORY_NOT_PROOF"}

    def reflect(self, *, tenant: str, event_id: str, expected: str,
                observed: str, correction: str, valid_at: str,
                recorded_at: str, request_id: str, provenance: str) -> dict:
        if any(not isinstance(x, str) or not 1 <= len(x) <= 1500
               for x in (expected, observed, correction)):
            raise ValueError("INVALID_REFLECTION")
        return self.memory.put(
            tenant=tenant, fact_id=event_id, kind="REFLECTION",
            subject="cognitive-cycle", predicate="retrospective-correction",
            value={"expected": expected, "observed": observed,
                   "proposed_correction": correction, "applied": False},
            valid_from=valid_at, recorded_at=recorded_at,
            request_id=request_id, provenance=provenance)

    def derive_summary(self, *, tenant: str, valid_at: str,
                       source_ids: Sequence[str], fact_id: str, request_id: str,
                       recorded_at: str, provenance: str) -> dict:
        """Deterministic referenced summary, not LLM-generated knowledge."""
        if not isinstance(source_ids, (list, tuple)) or not 1 <= len(source_ids) <= 8:
            raise ValueError("INVALID_SUMMARY_SOURCES")
        entries = {x["fact_id"]: x for x in self.memory.query(
            tenant=tenant, valid_at=valid_at, limit=100)}
        if len(set(source_ids)) != len(source_ids) or any(x not in entries for x in source_ids):
            raise ValueError("UNKNOWN_SUMMARY_SOURCE")
        return self.memory.put(
            tenant=tenant, fact_id=fact_id, kind="GENERATIVE",
            subject="cognitive-cycle", predicate="derived-summary",
            value={"source_fact_ids": list(source_ids),
                   "summary": "Referenced observations: " + ", ".join(source_ids),
                   "verified": False},
            valid_from=valid_at, recorded_at=recorded_at,
            request_id=request_id, provenance=provenance)


@dataclass(frozen=True)
class RouteModel:
    model_id: str
    supported_tasks: frozenset[str]
    quality_estimate: float
    cost_estimate: float

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not _NAME.fullmatch(self.model_id):
            raise ValueError("INVALID_ROUTE_MODEL")
        if (not isinstance(self.supported_tasks, frozenset) or
                not self.supported_tasks or
                any(not isinstance(x, str) or not _NAME.fullmatch(x)
                    for x in self.supported_tasks)):
            raise ValueError("INVALID_ROUTE_TASKS")
        _unit(self.quality_estimate, "MODEL_QUALITY")
        _unit(self.cost_estimate, "MODEL_COST")


def route_subtasks(tasks: Sequence[str], models: Sequence[RouteModel],
                   *, budget: float) -> dict:
    """R2-inspired *offline* budget-aware routing, not an RL-trained R2 model."""
    _unit(budget, "ROUTE_BUDGET")
    if (not isinstance(tasks, (tuple, list)) or not 1 <= len(tasks) <= 16 or
            not isinstance(models, (tuple, list)) or not 1 <= len(models) <= 16):
        raise ValueError("INVALID_ROUTE_DIMENSIONS")
    if len(set(tasks)) != len(tasks) or any(
            not isinstance(task, str) or not _NAME.fullmatch(task) for task in tasks):
        raise ValueError("INVALID_ROUTE_TASKS")
    if any(not isinstance(model, RouteModel) for model in models):
        raise ValueError("INVALID_ROUTE_MODELS")
    if len({x.model_id for x in models}) != len(models):
        raise ValueError("DUPLICATE_ROUTE_MODELS")
    # Bounded beam search preserves future-task feasibility; scores and costs
    # are user-supplied research estimates, not measured model guarantees.
    # Cap 256 candidate paths to prevent combinatorial resource exhaustion.
    states = [(0.0, 0.0, [])]  # (score, spent, assignments)
    for task in tasks:
        expanded = []
        for total, spent, assignments in states:
            for model in models:
                new_spent = spent + model.cost_estimate
                if task not in model.supported_tasks or new_spent > budget + 1e-12:
                    continue
                expanded.append((
                    total + model.quality_estimate - 0.2 * model.cost_estimate,
                    new_spent,
                    assignments + [{"task": task, "model": model.model_id,
                                    "estimated_cost": model.cost_estimate}],
                ))
        if not expanded:
            return {"status": "NO_FEASIBLE_ROUTE", "allocations": [],
                    "remaining_budget": round(budget, 6)}
        states = sorted(expanded, key=lambda x: (-x[0], x[1],
                        tuple(a["model"] for a in x[2])))[:256]
    score, spent, allocations = states[0]
    return {"status": "OFFLINE_ROUTE_PLAN_NOT_EXECUTED",
            "allocations": allocations, "remaining_budget": round(max(0, budget-spent), 6),
            "quality_estimates": "UNVERIFIED_EXTERNAL_INPUTS",
            "search": "BOUNDED_BEAM_256_NOT_GUARANTEED_OPTIMAL"}
