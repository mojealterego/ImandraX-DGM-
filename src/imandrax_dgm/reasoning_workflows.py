"""Bounded evidence-aware reasoning and read-only ReWOO task planning.

No code synthesis, shell, HTTP transport, automatic approvals or deployment.
Tool observations are untrusted data, not instructions. Claims are not proofs.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import inspect
import json
import math
import re
from typing import Any, Awaitable, Callable, Mapping, Sequence

_IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}\Z")
_ALLOWED_ONTOLOGIES = frozenset({
    "knowledge.retrieve", "memory.inspect", "research.lookup",
    "model.describe", "artifact.inspect", "benchmark.read",
})


class TaskError(ValueError):
    """Reject unsafe or inconsistent research plan."""


def _ident(value: object) -> str:
    if not isinstance(value, str) or not _IDENT.fullmatch(value):
        raise TaskError("INVALID_IDENTIFIER")
    return value


def _unit(value: object) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise TaskError("INVALID_SCORE")
    return float(value)


def _json_size(value: object, max_bytes: int = 8192) -> None:
    try:
        raw = json.dumps(value, sort_keys=True, allow_nan=False, ensure_ascii=False).encode()
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise TaskError("NON_CANONICAL_JSON") from exc
    if len(raw) > max_bytes:
        raise TaskError("PAYLOAD_BUDGET_EXCEEDED")


@dataclass(frozen=True)
class ThoughtBranch:
    node_id: str
    parent: str | None
    depth: int
    score: float
    sources: tuple[str, ...]

    def __post_init__(self):
        _ident(self.node_id)
        if self.parent is not None:
            _ident(self.parent)
        if type(self.depth) is not int or not 0 <= self.depth <= 8:
            raise TaskError("INVALID_THOUGHT_DEPTH")
        _unit(self.score)
        if not isinstance(self.sources, tuple) or len(self.sources) > 8:
            raise TaskError("INVALID_THOUGHT_SOURCES")
        for source in self.sources:
            _ident(source)


class TreeOfThoughts:
    """Finite beam search over proposed paths; scores are heuristic, not truth."""

    def __init__(self, *, beam_width: int = 4, max_depth: int = 5):
        if type(beam_width) is not int or not 1 <= beam_width <= 8:
            raise TaskError("INVALID_BEAM_WIDTH")
        if type(max_depth) is not int or not 1 <= max_depth <= 8:
            raise TaskError("INVALID_MAX_DEPTH")
        self.width, self.depth = beam_width, max_depth

    def search(self, thoughts: Sequence[ThoughtBranch]) -> dict:
        if not isinstance(thoughts, (list, tuple)) or not 1 <= len(thoughts) <= 64:
            raise TaskError("INVALID_THOUGHT_COUNT")
        if any(not isinstance(t, ThoughtBranch) for t in thoughts):
            raise TaskError("INVALID_THOUGHT")
        by_id = {t.node_id: t for t in thoughts}
        if len(by_id) != len(thoughts):
            raise TaskError("DUPLICATE_THOUGHT")
        roots = [t for t in thoughts if t.parent is None]
        if len(roots) != 1 or roots[0].depth != 0:
            raise TaskError("INVALID_ROOT")
        for thought in thoughts:
            if thought.parent is not None:
                parent = by_id.get(thought.parent)
                if parent is None or thought.depth != parent.depth + 1:
                    raise TaskError("INVALID_PARENT_LINK")
            if thought.depth > self.depth:
                raise TaskError("DEPTH_BUDGET_EXCEEDED")
        root = roots[0]
        frontier = [([root.node_id], root.score)]
        explored = 1
        best = frontier[0]
        for depth in range(1, self.depth + 1):
            extended = []
            for path, score in frontier:
                for t in thoughts:
                    if t.parent == path[-1] and t.depth == depth:
                        extended.append((path + [t.node_id], score + t.score))
            if not extended:
                break
            explored += len(extended)
            frontier = sorted(extended, key=lambda item: (-item[1], item[0]))[:self.width]
            candidate = frontier[0]
            if (len(candidate[0]), candidate[1]) > (len(best[0]), best[1]):
                best = candidate
        return {"status": "HEURISTIC_PATH_NOT_PROOF", "best_path": best[0],
                "heuristic_score": round(best[1], 6), "explored": explored,
                "beam_width": self.width}


class MultiHopVerifier:
    """Require each explicit temporal graph edge; shared words never imply edges."""

    def __init__(self, memory: Any):
        self.memory = memory

    def check(self, *, tenant: str, nodes: Sequence[str], relation: str,
              valid_at: str, as_of_seq: int | None = None) -> dict:
        if not isinstance(nodes, (tuple, list)) or not 2 <= len(nodes) <= 8:
            raise TaskError("INVALID_HOP_LENGTH")
        if len(set(nodes)) != len(nodes):
            raise TaskError("REPEATED_HOP_NODE")
        for x in nodes:
            _ident(x)
        _ident(relation)
        evidence = []
        for source, target in zip(nodes, nodes[1:]):
            records = self.memory.graph(tenant=tenant, subject=source,
                                        valid_at=valid_at, as_of_seq=as_of_seq)
            matches = [r for r in records if r["predicate"] == relation
                       and r["value"] == target and r["confidence"] >= 0.8
                       and r["provenance"]]
            if not matches:
                return {"status": "BLOCKED_MISSING_BRIDGE", "missing": [source, target],
                        "verified_hops": evidence}
            latest = max(matches, key=lambda r: r["seq"])
            evidence.append({"source": source, "target": target,
                             "edge_fact_id": latest["fact_id"], "seq": latest["seq"]})
        return {"status": "GRAPH_PATH_SUPPORTED_NOT_PROOF",
                "verified_hops": evidence, "semantic_entailment": "NOT_CHECKED"}


@dataclass(frozen=True)
class OntologyTool:
    name: str
    ontology: str
    input_fields: tuple[str, ...]
    access: str

    def __post_init__(self):
        _ident(self.name)
        if self.ontology not in _ALLOWED_ONTOLOGIES or self.access != "READ":
            raise TaskError("UNTRUSTED_TOOL_CAPABILITY")
        if (not isinstance(self.input_fields, tuple) or len(self.input_fields) > 12
                or len(set(self.input_fields)) != len(self.input_fields)):
            raise TaskError("INVALID_TOOL_FIELDS")
        for field in self.input_fields:
            _ident(field)


class OntologyRegistry:
    def __init__(self, tools: Sequence[OntologyTool]):
        if not isinstance(tools, (tuple, list)) or not 1 <= len(tools) <= 32:
            raise TaskError("INVALID_TOOL_REGISTRY")
        self.tools = {t.name: t for t in tools if isinstance(t, OntologyTool)}
        if len(self.tools) != len(tools):
            raise TaskError("DUPLICATE_OR_INVALID_TOOL")
        self.handlers: dict[str, Callable[[dict], Awaitable[dict]]] = {}

    def bind(self, tool_name: str, handler: Callable[[dict], Awaitable[dict]]) -> None:
        if tool_name not in self.tools or tool_name in self.handlers or not inspect.iscoroutinefunction(handler):
            raise TaskError("UNTRUSTED_TOOL_BINDING")
        self.handlers[tool_name] = handler


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    tool: str
    params: dict[str, object]
    depends_on: tuple[str, ...]

    def __post_init__(self):
        _ident(self.step_id)
        _ident(self.tool)
        if not isinstance(self.params, dict) or not isinstance(self.depends_on, tuple):
            raise TaskError("INVALID_PLAN_STEP")
        if len(set(self.depends_on)) != len(self.depends_on) or len(self.depends_on) > 16:
            raise TaskError("INVALID_DEPENDENCIES")
        for p in self.depends_on:
            _ident(p)
        _json_size(self.params)


class ReWOOPlanner:
    """Planning and observation separated. READ only, explicit dependency DAG."""

    def __init__(self, registry: OntologyRegistry):
        self.registry = registry

    def validate(self, steps: Sequence[PlanStep]) -> list[list[PlanStep]]:
        if not isinstance(steps, (list, tuple)) or not 1 <= len(steps) <= 32:
            raise TaskError("INVALID_PLAN_LENGTH")
        table = {x.step_id: x for x in steps if isinstance(x, PlanStep)}
        if len(table) != len(steps):
            raise TaskError("DUPLICATE_STEP_ID")
        for step in steps:
            tool = self.registry.tools.get(step.tool)
            if tool is None:
                raise TaskError("UNKNOWN_ONTOLOGY_TOOL")
            if set(step.params) != set(tool.input_fields):
                raise TaskError("TOOL_SCHEMA_MISMATCH")
            if step.step_id in step.depends_on or any(p not in table for p in step.depends_on):
                raise TaskError("INVALID_PLAN_DEPENDENCIES")
            for val in step.params.values():
                if isinstance(val, dict):
                    if set(val) != {"$ref", "field"} or val["$ref"] not in step.depends_on:
                        raise TaskError("UNDECLARED_OBSERVATION_REFERENCE")
                    _ident(val["field"])
                elif type(val) not in (str, int, float, bool) and val is not None:
                    raise TaskError("UNSUPPORTED_PARAMETER_TYPE")
        remain = dict(table)
        done = set()
        waves = []
        while remain:
            ready = sorted((v for v in remain.values() if set(v.depends_on) <= done),
                           key=lambda x: x.step_id)
            if not ready:
                raise TaskError("DEPENDENCY_CYCLE")
            waves.append(ready)
            for step in ready:
                done.add(step.step_id)
                del remain[step.step_id]
        return waves

    async def execute(self, steps: Sequence[PlanStep], *,
                      concurrency: int = 4, timeout: float = 5.0) -> dict:
        waves = self.validate(steps)
        if type(concurrency) is not int or not 1 <= concurrency <= 8:
            raise TaskError("INVALID_CONCURRENCY")
        if type(timeout) not in (float, int) or not 0 < timeout <= 30:
            raise TaskError("INVALID_TIMEOUT")
        observations: dict[str, dict] = {}
        failed: list[str] = []
        sem = asyncio.Semaphore(concurrency)

        async def run_one(step: PlanStep) -> None:
            if any(parent not in observations for parent in step.depends_on):
                failed.append(step.step_id)
                return
            handler = self.registry.handlers.get(step.tool)
            if handler is None:
                failed.append(step.step_id)
                return
            params: dict[str, object] = {}
            for key, value in step.params.items():
                if isinstance(value, dict):
                    obj = observations.get(value["$ref"], {})
                    if value["field"] not in obj:
                        failed.append(step.step_id)
                        return
                    params[key] = obj[value["field"]]
                else:
                    params[key] = value
            try:
                _json_size(params)
                async with sem:
                    observed = await asyncio.wait_for(handler(params), timeout)
                if not isinstance(observed, dict):
                    raise TaskError("INVALID_OBSERVATION")
                _json_size(observed)
                observations[step.step_id] = observed
            except (Exception, asyncio.TimeoutError):
                # Do not return arbitrary tool errors or secrets.
                failed.append(step.step_id)

        for wave in waves:
            await asyncio.gather(*(run_one(s) for s in wave))
        return {"status": ("READ_ONLY_PLAN_COMPLETED_UNATTESTED" if not failed
                           else "INCOMPLETE_NO_SIDE_EFFECT"),
                "results": observations, "failed_steps": sorted(set(failed)),
                "execution_rights": "READ_ONLY"}

def critique_and_refine(draft: str, feedback: Sequence[Mapping[str, object]],
                        *, max_rounds: int = 4) -> dict:
    if not isinstance(draft, str) or not 1 <= len(draft) <= 4096:
        raise TaskError("INVALID_DRAFT")
    if type(max_rounds) is not int or not 1 <= max_rounds <= 8:
        raise TaskError("INVALID_REFLECTION_BUDGET")
    if not isinstance(feedback, (list, tuple)) or len(feedback) > max_rounds:
        raise TaskError("REFLECTION_BUDGET_EXCEEDED")
    alternatives = [(0.0, draft)]
    for entry in feedback:
        if (not isinstance(entry, dict) or
                set(entry) != {"critique", "refinement", "score"} or
                not isinstance(entry["critique"], str) or
                not 1 <= len(entry["critique"]) <= 1024 or
                not isinstance(entry["refinement"], str) or
                not 1 <= len(entry["refinement"]) <= 4096):
            raise TaskError("INVALID_CRITIQUE")
        score = _unit(entry["score"])
        alternatives.append((score, entry["refinement"]))
    winner = sorted(alternatives, key=lambda x: (-x[0], x[1]))[0]
    return {"status": "DRAFT_NOT_EXECUTED", "selected": winner[1],
            "score": winner[0], "iterations": len(feedback),
            "verified": False}
