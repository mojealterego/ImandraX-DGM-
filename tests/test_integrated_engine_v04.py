"""Red/green tests for a single mathematical and evolutionary engine."""
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock
import pytest

from imandrax_dgm.engine import IntegratedEngine, MathTask, ArtifactError
from imandrax_dgm.gates import Candidate, canonical_payload

ROOT = Path(__file__).resolve().parents[1]


def make_engine(tmp_path, math_db):
    return IntegratedEngine(
        knowledge_db=math_db,
        inventory=ROOT/'data/repositories_public_701.tsv',
        ledger_db=tmp_path/'ledger.sqlite3',
        review_db=tmp_path/'review.sqlite3',
        archive_db=tmp_path/'archive.sqlite3',
    )


def test_single_math_interface_classifies_sources_without_claiming_proof(tmp_path, math_db):
    engine = make_engine(tmp_path, math_db)
    result = engine.math(MathTask(kind='LOOKUP', source='MSC2020-ENC', code='00A05'))
    assert result['status'] == 'SOURCE_INDEXED'
    assert result['proof_status'] == 'NOT_PROVED'
    assert result['entries'][0]['code'] == '00A05'
    assert result['provenance']['source'] == 'MSC2020-ENC'
    assert engine.math(MathTask(kind='LOOKUP', source='MSC2020-ENC', code='INVALID'))['status'] == 'NOT_FOUND'
    with pytest.raises(ValueError):
        engine.math(MathTask(kind='LOOKUP', source='UNKNOWN', code='00A05'))


def test_exact_arithmetic_is_not_formal_proof(tmp_path, math_db):
    engine = make_engine(tmp_path, math_db)
    for op, args, expected in [
        ('gcd', {'a':-36,'b':24}, 12),
        ('mod_pow', {'a':3,'b':7,'mod':11}, 9),
        ('is_prime', {'n':97}, True),
        ('is_prime', {'n':1}, False),
    ]:
        res = engine.math(MathTask(kind='EXACT_COMPUTE', operation=op, arguments=args))
        assert res['value'] == expected
        assert res['status'] == 'COMPUTED_EXACT'
        assert res['proof_status'] == 'NOT_FORMALLY_PROVED'
    with pytest.raises(ValueError):
        engine.math(MathTask(kind='EXACT_COMPUTE', operation='mod_pow', arguments={'a':1,'b':-1,'mod':2}))
    with pytest.raises(ValueError):
        engine.math(MathTask(kind='EXACT_COMPUTE', operation='is_prime', arguments={'n':10**15}))
    with pytest.raises(ValueError):
        engine.math(MathTask(kind='EXACT_COMPUTE', operation='gcd', arguments={'a':True,'b':2}))


def test_open_formal_claim_never_becomes_proved_by_retrieval(tmp_path, math_db):
    engine = make_engine(tmp_path, math_db)
    res = engine.math(MathTask(kind='FORMAL_THEOREM', statement='Riemann hypothesis', source='MSC2020-ENC', code='00A05'))
    assert res['status'] == 'PROOF_NOT_CHECKED'
    assert res['proof_status'] == 'NOT_PROVED'
    assert 'PROVED_STRICT' not in json.dumps(res)


def write_review_artifacts(root: Path, output: Path, *, source='def solve(task):\n    return 2\n', content='def solve(task):\n    return 3\n'):
    from difflib import unified_diff
    research = root/'research'
    research.mkdir(parents=True,exist_ok=True)
    (research/'solver.py').write_text(source)
    import hashlib
    baseline = hashlib.sha256(source.encode()).hexdigest()
    commit = 'b'*40
    patch = ''.join(unified_diff(source.splitlines(keepends=True),content.splitlines(keepends=True),fromfile='a/research/solver.py',tofile='b/research/solver.py'))
    patch_sha=hashlib.sha256(patch.encode()).hexdigest()
    parent=hashlib.sha256(canonical_payload({'commit':commit,'source_sha256':baseline})).hexdigest()
    candidate=Candidate('rsi-test-001',parent,patch_sha,('research/solver.py',),'Make the solver better',8000,90)
    files={
        'proposal.json':{'candidate':candidate.__dict__,'base_commit':commit,'baseline_sha256':baseline,'patch':patch,'state':'PROPOSED_NOT_APPROVED'},
        'changes.json':{'research/solver.py':content},
        'evaluation.json':{'candidates':[{'id':candidate.candidate_id,'status':'EVALUATED_UNATTESTED','regression':1.0,'heldout':1.0}],'selected':{'id':candidate.candidate_id,'status':'EVALUATED_UNATTESTED','regression':1.0,'heldout':1.0},'evidence':'UNSIGNED_LOCAL_EVALUATION_NOT_INDEPENDENT_ATTESTATION'},
        'cycle_status.json':{'state':'AWAITING_HUMAN_REVIEW','selected_candidate':candidate.candidate_id,'no_automatic_apply':True,'no_automatic_merge':True},
        'research.json':{'sources':[]},
    }
    output.mkdir(parents=True,exist_ok=True)
    checksums={}
    for name, obj in files.items():
        raw=(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode()
        (output/name).write_bytes(raw)
        checksums[name]=hashlib.sha256(raw).hexdigest()
    (output/'SHA256SUMS.json').write_text(json.dumps(checksums))
    return commit,candidate


def test_cycle_is_registered_in_same_engine_but_not_approved(tmp_path, math_db):
    engine = make_engine(tmp_path, math_db)
    root=tmp_path/'project'
    output=tmp_path/'out'
    commit,candidate=write_review_artifacts(root,output)
    cycle=Mock()
    cycle.run.return_value={'state':'AWAITING_HUMAN_REVIEW','selected_candidate':candidate.candidate_id}
    result=engine.evolve(campaign_id='c-01',root=root,base_commit=commit,output=output,
                         source_refs=[('MSC2020-ENC','00A05')],cycle=cycle)
    assert result['state']=='PROPOSED_AWAITING_USER'
    assert result['proposal_id']==candidate.candidate_id
    assert engine.reviews.status(candidate.candidate_id)['state']=='PROPOSED'
    assert not engine.reviews.is_authorized(candidate.candidate_id)
    assert engine.archive.list()==[]
    assert engine.ledger.verify('c-01')
    assert cycle.run.call_count == 1
    with pytest.raises(PermissionError):
        engine.archive_approved(candidate.candidate_id,score=0.95,transfer_score=0.93)


def test_artifact_tampering_and_source_drift_are_rejected(tmp_path, math_db):
    engine=make_engine(tmp_path, math_db)
    root=tmp_path/'project';output=tmp_path/'out'
    commit,candidate=write_review_artifacts(root,output)
    (output/'changes.json').write_text('{"research/solver.py":"evil"}')
    with pytest.raises(ArtifactError):
        engine.register_review_artifacts(root,commit,output)
    assert engine.archive.list()==[]
    write_review_artifacts(root,output)
    (root/'research/solver.py').write_text('new baseline')
    with pytest.raises(ArtifactError):
        engine.register_review_artifacts(root,commit,output)


def test_no_selected_candidate_is_never_registered(tmp_path, math_db):
    engine=make_engine(tmp_path, math_db)
    root=tmp_path/'project';out=tmp_path/'out'
    root.mkdir()
    fake=Mock()
    fake.run.return_value={'state':'NO_ADMISSIBLE_CANDIDATE','selected_candidate':None}
    result=engine.evolve(campaign_id='c-02',root=root,base_commit='b'*40,output=out,
                         source_refs=[('MSC2020-ENC','00A05')],cycle=fake)
    assert result['state']=='NO_ADMISSIBLE_CANDIDATE'
    assert engine.archive.list()==[]
    assert engine.ledger.verify('c-02')


def test_missing_mathematical_source_denies_evolution_before_llm(tmp_path, math_db):
    engine=make_engine(tmp_path,math_db)
    fake=Mock()
    with pytest.raises(ValueError):
        engine.evolve(campaign_id='c-03',root=tmp_path,base_commit='b'*40,output=tmp_path/'out',
                      source_refs=[('MSC2020-ENC','no-such-code')],cycle=fake)
    fake.run.assert_not_called()


def test_single_cli_supports_mathematics_and_inventory(tmp_path, math_db, capsys):
    from imandrax_dgm.cli import main
    assert main(['--root',str(ROOT),'math','--knowledge-db',str(math_db),
                 '--kind','LOOKUP','--source','MSC2020-ENC','--code','00A05']) == 0
    out=json.loads(capsys.readouterr().out)
    assert out['status']=='SOURCE_INDEXED'
    assert main(['--root',str(ROOT),'math','--knowledge-db',str(math_db),
                 '--kind','EXACT_COMPUTE','--operation','gcd','--arguments','{"a":24,"b":18}'])==0
    out=json.loads(capsys.readouterr().out)
    assert out['value']==6
    assert out['proof_status']=='NOT_FORMALLY_PROVED'


def test_reproducible_63_class_bootstrap_index(tmp_path):
    from scripts.build_msc_class_index import build_index
    from imandrax_dgm.knowledge import KnowledgeIndex
    path=tmp_path/'bootstrap.sqlite3'
    count=build_index(ROOT/'docs/MSC2020_63_CLASS_ROUTING.md',path)
    assert count==63
    index=KnowledgeIndex(path)
    assert index.stats()=={'MSC2020-CLASS-ROUTING':63}
    rows=index.exact('00-XX',source='MSC2020-CLASS-ROUTING')
    assert len(rows)==1
    assert rows[0]['status']=='INDEXED_ROUTING_ONLY'
    assert index.search('logic',source='MSC2020-CLASS-ROUTING')


def test_research_watch_emits_provenance_and_does_not_require_llm(tmp_path):
    from scripts.research_watch import write_report
    class FakeResearch:
        def search(self,query,per_page=5):
            return [{'provider':'OpenAlex','title':'Proof search','url':'https://openalex.org/W1','retrieval_status':'METADATA_ONLY'}]
    target=tmp_path/'research-report.json'
    report=write_report(FakeResearch(),target,queries=['Lean proof search','DGM meta-learning'])
    assert report['mode']=='READ_ONLY_PUBLIC_METADATA'
    assert len(report['queries'])==2
    assert len(report['results'])==2
    assert len(report['source_digest_sha256'])==64
    assert target.exists()


def test_real_research_cycle_integrates_with_math_sources_and_review(tmp_path, math_db):
    from imandrax_dgm.cycle import ResearchCycle
    root=tmp_path/'project';(root/'research').mkdir(parents=True)
    (root/'research/solver.py').write_text('def solve(task):\n    return None\n')
    class Research:
        def search(self,query):
            return [{'provider':'OpenAlex','title':'Test metadata','url':'https://openalex.org/W1'}]
    class LLM:
        def __init__(self):self.prompts=[]
        def complete_json(self,system,user):
            self.prompts.append(json.loads(user))
            return {'hypothesis':'Use a deterministic reference implementation',
                    'changes':[{'path':'research/solver.py','content':'def solve(task):\n    return 42\n'}]}
    class Sandbox:
        def evaluate(self,content,cases,timeout=90):
            return {'passed':len(cases),'total':len(cases),'duration_ms':5}
    llm=LLM()
    engine=make_engine(tmp_path,math_db)
    out=engine.evolve(campaign_id='end-to-end',root=root,base_commit='c'*40,
                      output=tmp_path/'review',source_refs=[('MSC2020-ENC','00A05')],
                      cycle=ResearchCycle(Research(),llm,Sandbox(),max_candidates=1))
    assert out['state']=='PROPOSED_AWAITING_USER'
    assert llm.prompts[0]['scholarly_metadata_untrusted'][0]['code']=='00A05'
    assert engine.reviews.status(out['proposal_id'])['state']=='PROPOSED'
    assert engine.ledger.verify('end-to-end')
    assert (root/'research/solver.py').read_text()=='def solve(task):\n    return None\n'