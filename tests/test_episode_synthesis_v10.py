from imandrax_dgm.cognitive_memory import BitemporalGraphMemory
from imandrax_dgm.episode_synthesis import synthesize_episodes
import pytest

def test_synthesis_cites_existing_episodic_ids_and_no_new_facts(tmp_path):
    memory=BitemporalGraphMemory(tmp_path/"mem.db")
    now="2026-01-01T00:00:00Z"
    for ident in ("ep1","ep2"):
        memory.put(tenant="a",fact_id=ident,kind="EPISODIC",subject="agent",
                   predicate="observed",value={"result":ident},
                   valid_from=now,recorded_at=now,request_id=ident,provenance="tester")
    result=synthesize_episodes(memory,tenant="a",source_ids=["ep1","ep2"],
                               semantic_id="sem1",now=now,request_id="summary")
    assert result["status"]=="SEMANTIC_REFERENCE_SYNTHESIS_NOT_PROOF"
    rows=memory.query(tenant="a",valid_at=now,kind="SEMANTIC")
    assert rows[0]["value"]["sources"]==["ep1","ep2"]
    assert rows[0]["value"]["inferred_fact"] is False
    with pytest.raises(ValueError):
        synthesize_episodes(memory,tenant="b",source_ids=["ep1"],
                            semantic_id="sem2",now=now,request_id="wrong")
