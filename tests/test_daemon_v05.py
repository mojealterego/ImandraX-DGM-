"""Background RSI runner must remain research-only, bounded and human gated."""
from pathlib import Path
import json
import pytest
from imandrax_dgm.daemon import run_loop


class FakeEngine:
    def __init__(self,fail=False):
        self.calls=[];self.fail=fail
    def evolve(self,**kw):
        self.calls.append(kw)
        if self.fail:raise RuntimeError('No sandbox')
        return {'state':'PROPOSED_AWAITING_USER','approval':'REQUIRED_SIGNED_USER_DECISION'}


def test_daemon_cycles_generate_distinct_artifacts_without_any_release(tmp_path):
    engine=FakeEngine()
    stats=run_loop(engine=engine,cycle=object(),root=tmp_path,base_commit='a'*40,
                   output_root=tmp_path/'out',source_refs=[('MSC2020-CLASS-ROUTING','00-XX')],
                   max_cycles=3,interval_seconds=300,sleep=lambda s:None)
    assert stats['cycles']==3
    assert stats['proposals']==3
    assert len({x['campaign_id'] for x in engine.calls})==3
    assert len({str(x['output']) for x in engine.calls})==3
    assert all(x['base_commit']=='a'*40 for x in engine.calls)
    assert all('apply_patch' not in x and 'deploy' not in x for x in engine.calls)
    assert all('APPROVED' not in x for x in engine.calls)
    assert len(list((tmp_path/'out').glob('*/cycle_result.json')))==3


def test_daemon_stops_after_repeated_failure_and_does_not_claim_approval(tmp_path):
    engine=FakeEngine(fail=True)
    with pytest.raises(RuntimeError,match='consecutive'):
        run_loop(engine=engine,cycle=object(),root=tmp_path,base_commit='b'*40,
                 output_root=tmp_path/'out',source_refs=[('MSC2020-CLASS-ROUTING','00-XX')],
                 max_cycles=0,interval_seconds=300,sleep=lambda s:None)
    assert len(engine.calls)==3
    assert len(list((tmp_path/'out').glob('*/cycle_result.json')))==3


def test_daemon_rejects_bad_interval_and_root_overlap(tmp_path):
    engine=FakeEngine()
    with pytest.raises(ValueError):
        run_loop(engine=engine,cycle=object(),root=tmp_path,base_commit='a'*40,
                 output_root=tmp_path/'out',source_refs=[],max_cycles=1,interval_seconds=1)
    with pytest.raises(ValueError):
        run_loop(engine=engine,cycle=object(),root=tmp_path,base_commit='a'*40,
                 output_root=tmp_path/'research',source_refs=[('a','b')],max_cycles=1,interval_seconds=300)


def test_daemon_stops_on_source_drift_before_any_llm(tmp_path):
    import hashlib
    (tmp_path/'research').mkdir()
    source=tmp_path/'research'/'solver.py'
    source.write_text('def solve(task): return 1\n')
    engine=FakeEngine()
    with pytest.raises(RuntimeError,match='drift'):
        run_loop(engine=engine,cycle=object(),root=tmp_path,base_commit='a'*40,
                 output_root=tmp_path/'out',source_refs=[('a','b')],max_cycles=1,
                 interval_seconds=300,expected_source_sha256='0'*64)
    assert engine.calls==[]
