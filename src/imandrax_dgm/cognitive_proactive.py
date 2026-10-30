"""Non-agentic cascaded inference planning and hypothesis checks over local memory."""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Any, Sequence
from .cognitive_memory import BitemporalGraphMemory


@dataclass(frozen=True)
class CascadeStage:
    model_id: str
    estimated_quality: float
    estimated_cost: float

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id or len(self.model_id) > 80:
            raise ValueError("INVALID_STAGE_ID")
        for number in (self.estimated_quality, self.estimated_cost):
            if type(number) not in (float, int) or not math.isfinite(number) or not 0 <= number <= 1:
                raise ValueError("INVALID_STAGE_ESTIMATE")


def cascade_plan(stages: Sequence[CascadeStage], *, target_quality: float,
                 budget: float) -> dict:
    """Plan escalating estimates: no model call, no claims of real accuracy."""
    if (not isinstance(stages, (list, tuple)) or not 1 <= len(stages) <= 8
            or len({s.model_id for s in stages}) != len(stages)):
        raise ValueError("INVALID_CASCADE")
    if any(not isinstance(s, CascadeStage) for s in stages):
        raise ValueError("INVALID_CASCADE")
    for x in (target_quality, budget):
        if type(x) not in (float, int) or not math.isfinite(x) or not 0 <= x <= 1:
            raise ValueError("INVALID_CASCADE_BUDGET")
    arranged = sorted(stages, key=lambda s:(s.estimated_cost, s.model_id))
    spent = 0.0
    planned = []
    for stage in arranged:
        if spent + stage.estimated_cost > budget + 1e-12:
            continue
        planned.append(stage.model_id)
        spent += stage.estimated_cost
        if stage.estimated_quality >= target_quality:
            return {"status":"CASCADE_PLAN_UNEXECUTED", "stages":planned,
                    "estimated_total_cost":round(spent,6),
                    "quality_verified":False}
    return {"status":"CASCADE_QUALITY_UNMET", "stages":planned,
            "estimated_total_cost":round(spent,6), "quality_verified":False}


def verify_hypothesis(memory: BitemporalGraphMemory, *, tenant: str,
                      hypothesis_id: str, required_fact_ids: Sequence[str],
                      valid_at: str, as_of_seq: int | None = None) -> dict:
    if (not isinstance(hypothesis_id, str) or not 1 <= len(hypothesis_id) <= 96
            or not isinstance(required_fact_ids, (list, tuple))
            or not 1 <= len(required_fact_ids) <= 16
            or len(set(required_fact_ids)) != len(required_fact_ids)):
        raise ValueError("INVALID_HYPOTHESIS")
    rows=memory.query(tenant=tenant,valid_at=valid_at,
                      as_of_seq=as_of_seq,limit=100)
    found={x["fact_id"]:x for x in rows}
    missing=sorted(set(required_fact_ids)-set(found))
    return {"hypothesis_id":hypothesis_id,
            "status":("REFERENCES_PRESENT_NOT_PROVED" if not missing
                      else "UNSUPPORTED_MISSING_REFERENCES"),
            "missing":missing,
            "evidence":[{"fact_id":r,"seq":found[r]["seq"],"provenance":found[r]["provenance"]}
                        for r in required_fact_ids if r in found],
            "truth_verified":False}


def research_handlers(memory: BitemporalGraphMemory) -> dict:
    """Closed registry for the bounded event executor; no arbitrary shell/API."""
    async def check(data: dict[str,Any]) -> dict:
        if not isinstance(data,dict) or set(data)!={"tenant","hypothesis_id",
                                                     "required_fact_ids","valid_at"}:
            raise ValueError("INVALID_RESEARCH_EVENT")
        return verify_hypothesis(memory, **data)
    return {"research.check":check}
