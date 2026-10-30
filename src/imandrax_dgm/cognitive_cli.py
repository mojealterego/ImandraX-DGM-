"""Explicit operator CLI for the single ImandraX/DGM/APEX package.

No network, model execution, owner-signature generation, source change or deploy.
Inputs are local JSON data; JSON records are never treated as instructions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adaptive_evolution import DigitalGenotype, FitnessEvidence, mutation_loop
from .cognitive_memory import BitemporalGraphMemory, MemoryError
from .cognition import (
    CognitiveDecisionCycle, DecisionOption, GraphOfThoughts, RouteModel,
    Thought, route_subtasks,
)


def _unique(pairs):
    value = {}
    for k, v in pairs:
        if k in value:
            raise ValueError("DUPLICATE_INPUT_KEY")
        value[k] = v
    return value


def load_payload(path: Path) -> dict:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("INVALID_COGNITIVE_INPUT_FILE")
    try:
        data = json.loads(path.read_text("utf-8"), object_pairs_hook=_unique)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("INVALID_COGNITIVE_INPUT_JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("INVALID_COGNITIVE_INPUT_OBJECT")
    return data


def execute(op: str, payload: dict[str, Any], *,
            root: Path, state_dir: Path) -> dict:
    root = Path(root).resolve()
    state_dir = Path(state_dir).resolve()
    if state_dir == root or state_dir.is_relative_to(root):
        raise ValueError("COGNITIVE_STATE_INSIDE_SOURCE_FORBIDDEN")
    if not isinstance(payload, dict):
        raise ValueError("INVALID_COGNITIVE_PAYLOAD")
    allowed = {
        "remember", "recall", "graph", "checkpoint", "recover",
        "decision", "reflect", "summarize", "thoughts", "route", "genotype",
        "tot", "multihop", "rewoo-validate", "critique", "episodes", "cascade",
        "event-enqueue", "event-claim", "event-status", "event-ack",
        "event-fail", "event-process",
    }
    if op not in allowed:
        raise ValueError("UNKNOWN_COGNITIVE_OPERATION")
    memory = BitemporalGraphMemory(state_dir / "cognitive_memory.sqlite3")
    cycle = CognitiveDecisionCycle(memory)
    if op == "remember":
        return memory.put(**payload)
    if op == "recall":
        return {"status": "READ_ONLY_UNVERIFIED_MEMORY", "facts": memory.query(**payload)}
    if op == "graph":
        return {"status": "READ_ONLY_UNVERIFIED_GRAPH", "edges": memory.graph(**payload)}
    if op == "checkpoint":
        if payload:
            raise ValueError("CHECKPOINT_HAS_NO_PARAMETERS")
        return memory.checkpoint()
    if op == "recover":
        if set(payload) != {"destination", "as_of_seq"}:
            raise ValueError("INVALID_RECOVERY_PARAMETERS")
        destination = Path(payload["destination"])
        if not destination.is_absolute() or destination.resolve().is_relative_to(root):
            raise ValueError("INVALID_RECOVERY_DESTINATION")
        clone = memory.clone_at(destination, as_of_seq=payload["as_of_seq"])
        return {"status": "RECOVERED_COPY_ONLY_SOURCE_UNCHANGED",
                "checkpoint": clone.checkpoint(), "path": str(clone.path)}
    if op == "decision":
        data = dict(payload)
        raw = data.pop("options")
        data["options"] = [
            DecisionOption(**{**x, "evidence_refs": tuple(x.get("evidence_refs", []))})
            for x in raw
        ]
        return cycle.decide(**data)
    if op == "reflect":
        return cycle.reflect(**payload)
    if op == "summarize":
        return cycle.derive_summary(**payload)
    if op == "thoughts":
        if set(payload) != {"thoughts"}:
            raise ValueError("INVALID_THOUGHT_PARAMETERS")
        return GraphOfThoughts([
            Thought(**{**x, "parents": tuple(x["parents"])})
            for x in payload["thoughts"]]).report()
    if op == "route":
        if set(payload) != {"tasks", "models", "budget"}:
            raise ValueError("INVALID_ROUTE_PARAMETERS")
        models = [RouteModel(**{**x, "supported_tasks": frozenset(x["supported_tasks"])})
                  for x in payload["models"]]
        return route_subtasks(payload["tasks"], models, budget=payload["budget"])
    if op == "tot":
        from .reasoning_workflows import ThoughtBranch, TreeOfThoughts
        if set(payload) != {"thoughts", "beam_width", "max_depth"}:
            raise ValueError("INVALID_TOT_PAYLOAD")
        entries = [ThoughtBranch(x["node_id"], x["parent"], x["depth"],
                                 x["score"], tuple(x["sources"]))
                   for x in payload["thoughts"]]
        return TreeOfThoughts(beam_width=payload["beam_width"],
                              max_depth=payload["max_depth"]).search(entries)
    if op == "multihop":
        from .reasoning_workflows import MultiHopVerifier
        return MultiHopVerifier(memory).check(**payload)
    if op == "rewoo-validate":
        from .reasoning_workflows import OntologyRegistry, OntologyTool, PlanStep, ReWOOPlanner
        if set(payload) != {"tools", "steps"}:
            raise ValueError("INVALID_REWOO_PAYLOAD")
        tools = [OntologyTool(x["name"], x["ontology"],
                              tuple(x["input_fields"]), x["access"])
                 for x in payload["tools"]]
        steps = [PlanStep(x["step_id"], x["tool"],
                          x["params"], tuple(x["depends_on"]))
                 for x in payload["steps"]]
        waves = ReWOOPlanner(OntologyRegistry(tools)).validate(steps)
        return {"status":"READ_ONLY_PLAN_VALIDATED_NOT_EXECUTED",
                "waves":[[x.step_id for x in wave] for wave in waves]}
    if op == "critique":
        from .reasoning_workflows import critique_and_refine
        return critique_and_refine(**payload)
    if op == "episodes":
        from .episode_synthesis import synthesize_episodes
        return synthesize_episodes(memory, **payload)
    if op == "cascade":
        from .cognitive_proactive import CascadeStage, cascade_plan
        if set(payload) != {"stages", "target_quality", "budget"}:
            raise ValueError("INVALID_CASCADE_PAYLOAD")
        return cascade_plan([CascadeStage(**x) for x in payload["stages"]],
                            target_quality=payload["target_quality"],
                            budget=payload["budget"])
    if op.startswith("event-"):
        from .event_workflows import DurableEventQueue
        from .cognitive_proactive import research_handlers
        import asyncio
        queue = DurableEventQueue(state_dir / "research_events.sqlite3")
        if op == "event-enqueue":
            return queue.enqueue(**payload)
        if op == "event-claim":
            return {"event":queue.claim(**payload)}
        if op == "event-status":
            return queue.status(**payload)
        if op == "event-ack":
            queue.ack(**payload)
            return {"status":"ACKNOWLEDGED"}
        if op == "event-fail":
            queue.fail(**payload)
            return {"status":"RETRY_SCHEDULED_OR_DEAD"}
        if op == "event-process":
            if set(payload) != {"now"}:
                raise ValueError("INVALID_PROCESS_PAYLOAD")
            processed = asyncio.run(queue.process_once(research_handlers(memory),
                                                       now=payload["now"]))
            return {"status":"BOUNDED_READ_ONLY_HANDLER", "processed":processed}
    if op == "genotype":
        if set(payload) != {"seed", "mutations", "baseline_heldout"}:
            raise ValueError("INVALID_GENOTYPE_PARAMETERS")
        mutations = [(x["gene"], x["value"], FitnessEvidence(**x["evidence"]))
                     for x in payload["mutations"]]
        return mutation_loop(DigitalGenotype.from_mapping(payload["seed"]),
                             mutations, baseline_heldout=payload["baseline_heldout"])
    raise ValueError("UNKNOWN_COGNITIVE_OPERATION")
