"""Bounded, deterministic cross-engine flow runner; no dynamic scripts or code updates.

A flow contains literal, independently validated requests. It cannot interpolate
untrusted outputs into commands, loosen access modes, or approve a release.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from .apex import ApexError, ApexRequest, ApexRuntime, _canonical

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


@dataclass(frozen=True)
class FlowStep:
    step_id: str
    capability: str
    payload: dict
    depends_on: tuple[str, ...] = ()


class ApexFlow:
    def __init__(self, flow_id: str, steps: tuple[FlowStep, ...]):
        if not isinstance(flow_id, str) or not _ID.fullmatch(flow_id):
            raise ApexError("INVALID_FLOW_ID")
        if not isinstance(steps, tuple) or not 1 <= len(steps) <= 32:
            raise ApexError("INVALID_FLOW_SIZE")
        for step in steps:
            if (not isinstance(step, FlowStep) or not isinstance(step.step_id, str) or
                    not _ID.fullmatch(step.step_id) or not isinstance(step.depends_on, tuple) or
                    not all(isinstance(d, str) and _ID.fullmatch(d) for d in step.depends_on) or
                    len(set(step.depends_on)) != len(step.depends_on) or
                    not isinstance(step.payload, dict)):
                raise ApexError("INVALID_FLOW_STEP")
        if len({s.step_id for s in steps}) != len(steps):
            raise ApexError("DUPLICATE_FLOW_STEP")
        self.flow_id = flow_id
        self.steps = steps
        self.order = self._order()
        self.digest = hashlib.sha256(_canonical({"flow": flow_id, "steps": [
            {"id": s.step_id, "capability": s.capability,
             "payload": s.payload, "depends_on": sorted(s.depends_on)} for s in steps]})).hexdigest()

    def _order(self) -> tuple[FlowStep, ...]:
        by_id = {s.step_id: s for s in self.steps}
        visited: set[str] = set()
        active: set[str] = set()
        result: list[FlowStep] = []

        def visit(name: str):
            if name in active:
                raise ApexError("FLOW_CYCLE")
            if name in visited:
                return
            if name not in by_id:
                raise ApexError("UNKNOWN_FLOW_DEPENDENCY")
            active.add(name)
            for dependency in sorted(by_id[name].depends_on):
                visit(dependency)
            active.remove(name)
            visited.add(name)
            result.append(by_id[name])

        for item in sorted(self.steps, key=lambda x: x.step_id):
            visit(item.step_id)
        return tuple(result)

    def execute(self, runtime: ApexRuntime, *, principal: str) -> dict:
        if not isinstance(runtime, ApexRuntime):
            raise ApexError("INVALID_RUNTIME")
        # Run no part of the flow until every capability is declared,
        # unprotected and (for research) explicitly opted into.
        for step in self.order:
            cap, handler = runtime.registry.resolve(step.capability)
            if cap.access not in {"READ", "RESEARCH"}:
                raise ApexError("PROTECTED_CAPABILITY")
            if cap.access == "RESEARCH" and not runtime.enable_research:
                raise ApexError("RESEARCH_DISABLED")
            if handler is None:
                raise ApexError("UNBOUND_CAPABILITY")
            if set(step.payload) != set(cap.input_fields):
                raise ApexError("INVALID_FLOW_PAYLOAD")
        outputs: dict[str, dict] = {}
        for step in self.order:
            request = ApexRequest(step.capability, step.payload, principal,
                                  f"{self.flow_id}-{step.step_id}")
            outputs[step.step_id] = runtime.dispatch(request)
        return {"status": "OBSERVED_RESEARCH_FLOW", "flow_digest": self.digest,
                "steps": outputs, "auto_approval": False, "auto_deploy": False}
