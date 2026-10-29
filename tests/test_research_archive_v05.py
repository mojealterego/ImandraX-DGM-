"""RED: research-only, durable multi-generation DGM without release privileges."""
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from imandrax_dgm.research_archive import ResearchArchive
from imandrax_dgm.cycle import ResearchCycle

BASE = 'a' * 40
BASELINE = hashlib.sha256(b'def solve(task):\n    return None\n').hexdigest()


def source(n):
    return f'def solve(task):\n    return {n}\n'


def put(archive, ident, value, *, parent_id=None, regression=1.0, heldout=1.0):
    code = source(value)
    return archive.record(candidate_id=ident, base_commit=BASE, baseline_sha256=BASELINE,
                          patch_sha256=hashlib.sha256(f'patch-{value}'.encode()).hexdigest(),
                          content=code, parent_id=parent_id, regression=regression,
                          heldout=heldout, novelty=0.2,
                          evidence_sha256=hashlib.sha256(f'evidence-{value}'.encode()).hexdigest())


def test_durable_genealogy_selects_qualified_parent_and_persists(tmp_path):
    db=tmp_path/'archive.sqlite3'
    archive=ResearchArchive(db)
    first=put(archive,'rsi-root',1)
    child=put(archive,'rsi-child',2,parent_id='rsi-root')
    assert first['depth']==0
    assert child['depth']==1
    assert child['parent_id']=='rsi-root'
    assert ResearchArchive(db).choose_parent(BASE,BASELINE)['candidate_id']=='rsi-child'
    assert ResearchArchive(db).choose_parent('b'*40,BASELINE) is None
    assert ResearchArchive(db).choose_parent(BASE,'c'*64) is None
    assert len(archive.list_metadata())==2
    assert 'content' not in archive.list_metadata()[0]


def test_immutability_rejects_reuse_unknown_parent_and_bad_scores(tmp_path):
    archive=ResearchArchive(tmp_path/'research.sqlite3')
    put(archive,'rsi-root',1)
    assert put(archive,'rsi-root',1)['candidate_id']=='rsi-root'
    with pytest.raises(ValueError):
        put(archive,'rsi-root',3)
    with pytest.raises(ValueError):
        put(archive,'rsi-orphan',3,parent_id='unknown')
    with pytest.raises(ValueError):
        put(archive,'rsi-child',1,parent_id='rsi-root')  # no identical child
    with pytest.raises(ValueError):
        put(archive,'rsi-nan',2,heldout=float('nan'))
    with pytest.raises(ValueError):
        archive.record(candidate_id='rsi-bad',base_commit=BASE,baseline_sha256=BASELINE,
                       patch_sha256='a'*64,content='import os\ndef solve(task):return 2\n',
                       parent_id=None,regression=1,heldout=1,novelty=0.1,evidence_sha256='b'*64)


def test_research_archive_cannot_approve_or_apply(tmp_path):
    archive=ResearchArchive(tmp_path/'archive.sqlite3')
    assert not hasattr(archive,'approve')
    assert not hasattr(archive,'apply_patch')
    assert not hasattr(archive,'merge')
    assert not hasattr(archive,'deploy')


class Research:
    def search(self,query):
        return [{'provider':'OpenAlex','title':'Proof search','url':'https://openalex.org/W1'}]


class GeneratingLLM:
    def __init__(self):
        self.inputs=[]
    def complete_json(self,system,user):
        prompt=json.loads(user)
        self.inputs.append(prompt)
        n=len(self.inputs)
        return {'hypothesis':'Improve solver generation','changes':[
            {'path':'research/solver.py','content':source(n)}]}


class PassingSandbox:
    def evaluate(self,content,cases,timeout=90):
        return {'passed':len(cases)-(1 if 'return 1' in content else 0),'total':len(cases),'duration_ms':2}


def test_two_generations_in_one_cycle_then_parent_reuse_next_cycle(tmp_path):
    root=tmp_path/'repo'
    (root/'research').mkdir(parents=True)
    (root/'research'/'solver.py').write_text('def solve(task):\n    return None\n')
    archive=ResearchArchive(tmp_path/'archive.sqlite3')
    llm=GeneratingLLM()
    cycle=ResearchCycle(Research(),llm,PassingSandbox(),max_candidates=2)
    out=tmp_path/'cycle1'
    result=cycle.run(root,BASE,out,research_archive=archive)
    assert result['state']=='AWAITING_HUMAN_REVIEW'
    assert result['research_generation']==1
    assert len(archive.list_metadata())==2
    assert llm.inputs[0]['research_parent_untrusted'] is None
    assert llm.inputs[1]['research_parent_untrusted']['candidate_id']
    assert llm.inputs[1]['research_parent_untrusted']['content']==source(1)
    assert (root/'research'/'solver.py').read_text()=='def solve(task):\n    return None\n'
    assert json.loads((out/'proposal.json').read_text())['research_lineage']['depth']==1
    second_llm=GeneratingLLM()
    second_llm.inputs.extend([{}, {}])  # first actual proposal differs from first cycle
    next_cycle=ResearchCycle(Research(),second_llm,PassingSandbox(),max_candidates=1)
    result2=next_cycle.run(root,BASE,tmp_path/'cycle2',research_archive=ResearchArchive(tmp_path/'archive.sqlite3'))
    assert result2['state']=='AWAITING_HUMAN_REVIEW'
    assert second_llm.inputs[2]['research_parent_untrusted']['candidate_id']
    assert result2['research_generation']>=2
    assert (root/'research'/'solver.py').read_text()=='def solve(task):\n    return None\n'


def test_research_archive_does_not_accept_stale_baseline_and_does_not_leak_heldout(tmp_path):
    root=tmp_path/'repo';(root/'research').mkdir(parents=True)
    (root/'research'/'solver.py').write_text('def solve(task):\n    return None\n')
    archive=ResearchArchive(tmp_path/'archive.sqlite3')
    put(archive,'rsi-legacy',5)
    (root/'research'/'solver.py').write_text('def solve(task):\n    return 999\n')
    llm=GeneratingLLM()
    cycle=ResearchCycle(Research(),llm,PassingSandbox(),max_candidates=1)
    cycle.run(root,BASE,tmp_path/'out',research_archive=archive)
    assert llm.inputs[0]['research_parent_untrusted'] is None
    assert 'heldout' not in json.dumps(llm.inputs[0])


def test_archive_integrity_check_detects_database_row_tampering(tmp_path):
    archive=ResearchArchive(tmp_path/'archive.sqlite3')
    put(archive,'rsi-root',1)
    with sqlite3.connect(tmp_path/'archive.sqlite3') as con:
        con.execute('DROP TRIGGER research_no_update')
        con.execute("UPDATE research_generations SET content='def solve(task):\\n    return 0\\n' WHERE candidate_id='rsi-root'")
    with pytest.raises(ValueError,match='integrity'):
        archive.choose_parent(BASE,BASELINE)


def test_archive_rejects_existing_output_and_never_overwrites(tmp_path):
    root=tmp_path/'repo';(root/'research').mkdir(parents=True)
    (root/'research'/'solver.py').write_text('def solve(task):\n    return None\n')
    output=tmp_path/'out';output.mkdir()
    (output/'proposal.json').write_text('immutable')
    with pytest.raises(ValueError,match='fresh'):
        ResearchCycle(Research(),GeneratingLLM(),PassingSandbox(),max_candidates=1).run(
            root,BASE,output,research_archive=ResearchArchive(tmp_path/'archive.sqlite3'))
    assert (output/'proposal.json').read_text()=='immutable'


def test_engine_rejects_recomputed_manifest_with_fake_genealogy(tmp_path):
    from imandrax_dgm.engine import IntegratedEngine, ArtifactError
    from tests.test_integrated_engine_v04 import make_engine, write_review_artifacts
    # All five file checksums are recomputed by an adversary: semantic cross-check must still fail.
    from tests.conftest import math_db as math_fixture
    # The shared fixture is pytest-managed; construct a minimal compatible index here.
    from scripts.build_msc_class_index import build_index
    root=Path(__file__).resolve().parents[1]
    db=tmp_path/'msc.sqlite3'
    build_index(root/'docs/MSC2020_63_CLASS_ROUTING.md',db)
    engine=IntegratedEngine(knowledge_db=db,inventory=root/'data/repositories_public_701.tsv',
        ledger_db=tmp_path/'ledger.sqlite3',review_db=tmp_path/'review.sqlite3',
        archive_db=tmp_path/'approved.sqlite3')
    project=tmp_path/'project';out=tmp_path/'out'
    commit,_=write_review_artifacts(project,out)
    proposal=json.loads((out/'proposal.json').read_text())
    proposal['research_lineage']={'parent_id':'fake','depth':1,'parent_source_sha256':'0'*64}
    (out/'proposal.json').write_text(json.dumps(proposal))
    checks=json.loads((out/'SHA256SUMS.json').read_text())
    checks['proposal.json']=hashlib.sha256((out/'proposal.json').read_bytes()).hexdigest()
    (out/'SHA256SUMS.json').write_text(json.dumps(checks))
    with pytest.raises(ArtifactError,match='lineage'):
        engine.register_review_artifacts(project,commit,out)
