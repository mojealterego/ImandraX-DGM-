import asyncio
from imandrax_dgm.cognitive_memory import BitemporalGraphMemory
from imandrax_dgm.cognitive_proactive import (
    CascadeStage, cascade_plan, verify_hypothesis, research_handlers)
from imandrax_dgm.event_workflows import DurableEventQueue

def test_cascade_stops_at_quality_threshold_without_inference():
    stages=[CascadeStage("small",.60,.1),CascadeStage("medium",.85,.2),
            CascadeStage("large",.95,.6)]
    result=cascade_plan(stages,target_quality=.8,budget=.5)
    assert result["status"]=="CASCADE_PLAN_UNEXECUTED"
    assert result["stages"]==["small","medium"]
    assert result["quality_verified"] is False
    assert cascade_plan(stages,target_quality=.99,budget=.2)["status"]=="CASCADE_QUALITY_UNMET"

def test_hypothesis_event_can_verify_while_other_jobs_wait(tmp_path):
    store=BitemporalGraphMemory(tmp_path/"mem.db")
    when="2026-01-01T00:00:00Z"
    store.put(tenant="lab",fact_id="fact",kind="EPISODIC",
              subject="q",predicate="observed",value={"value":3},
              valid_from=when,recorded_at=when,request_id="r1",provenance="test")
    q=DurableEventQueue(tmp_path/"events.db")
    q.enqueue(event_id="h1",kind="research.check",now=1,
              payload={"tenant":"lab","hypothesis_id":"hyp",
                       "required_fact_ids":["fact"],"valid_at":when})
    q.enqueue(event_id="pending",kind="research.check",now=999,
              payload={"tenant":"lab","hypothesis_id":"future",
                       "required_fact_ids":["unknown"],"valid_at":when})
    assert asyncio.run(q.process_once(research_handlers(store),now=2))==1
    result=q.status("h1")["result"]
    assert result["status"]=="REFERENCES_PRESENT_NOT_PROVED"
    assert q.status("pending")["status"]=="PENDING"
    assert verify_hypothesis(store,tenant="other",hypothesis_id="hyp",
                             required_fact_ids=["fact"],valid_at=when)["status"] == "UNSUPPORTED_MISSING_REFERENCES"
