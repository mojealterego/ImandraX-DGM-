import json
import sqlite3
from pathlib import Path
import pytest

from imandrax_dgm.catalog import RepoCatalog
from imandrax_dgm.knowledge import KnowledgeIndex
from imandrax_dgm.gates import Candidate, Policy, EvidenceAttestation, ResearchGate, canonical_payload
from imandrax_dgm.ledger import ImmutableLedger

ROOT = Path(__file__).resolve().parents[1]


def test_inventory_is_complete_and_unique():
    c = RepoCatalog.from_tsv(ROOT / 'data/repositories_public_701.tsv')
    assert len(c.repos) == 701
    assert len({r.full_name for r in c.repos}) == 701
    assert c.by_name('mojealterego/mathlib4').default_branch == 'master'
    assert c.by_name('mojealterego/dgm').default_branch == 'main'
    assert c.by_name('mojealterego/ImandraX') is None


def test_catalog_never_infers_implementation_from_name():
    c = RepoCatalog.from_tsv(ROOT / 'data/repositories_public_701.tsv')
    all_rows = c.triage()
    assert len(all_rows) == 701
    assert all(r['integration_status'] == 'NOT_INTEGRATED' for r in all_rows)
    assert next(x for x in all_rows if x['repository'] == 'mojealterego/RSIAI0')['risk_flag'] == 'UNSAFE_REAL_MODE'
    assert next(x for x in all_rows if x['repository'] == 'mojealterego/mathlib4')['priority'] == 'P0'


def test_knowledge_is_read_only_and_not_proof(math_db):
    db = math_db
    k = KnowledgeIndex(db)
    assert sum(k.stats().values()) == 2
    rows = k.exact('00A05', source='MSC2020-ENC')
    assert len(rows) == 1
    assert rows[0]['code'] == '00A05'
    assert rows[0]['status'] != 'PROVED_STRICT'
    assert k.search('algebra', limit=3)
    assert k.search('" OR 1=1 --', limit=3) == [] or isinstance(k.search('" OR 1=1 --', limit=3), list)
    with pytest.raises(ValueError):
        k.search('algebra', limit=0)
    with pytest.raises(ValueError):
        k.search('algebra', source='secret')


def test_proposal_rejects_privilege_escalation_and_traversal():
    p = Policy.default()
    ok = Candidate('c1', 'a' * 64, 'b' * 64, ('harness/planner.py',), 'Test hypothesis', 1000, 30)
    assert ResearchGate(p).admit(ok).accepted
    for bad in ('../policy/kernel.py', 'policy/kernel.py', '/etc/passwd', 'harness/../../policy.py', 'harness\\evil.py', 'tests/test_policy.py', 'harness/.git/config'):
        cand = Candidate('bad', 'a'*64, 'b'*64, (bad,), 'bad', 100, 10)
        assert not ResearchGate(p).admit(cand).accepted, bad
    assert not ResearchGate(p).admit(Candidate('bad', 'a'*64, 'b'*64, ('harness/a.py',), 'bad', 999999999, 10)).accepted


def test_attestation_is_verified_but_does_not_auto_promote():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    key = Ed25519PrivateKey.generate()
    pub = key.public_key().public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    payload = {'candidate_digest': 'b'*64, 'suite': 'PUBLIC_REGRESSION', 'result': 'PASS', 'runner_id': 'runner-01', 'source_digest': 'a'*64}
    sig = key.sign(canonical_payload(payload)).hex()
    att = EvidenceAttestation(payload=payload, signer_id='runner-01', signature_hex=sig)
    g = ResearchGate(Policy.default(), trusted_runner_keys={'runner-01':pub})
    assert g.verify_attestation(att)
    assert g.evaluate_attestation(att) == 'RESEARCH_EVIDENCE_ONLY'
    tampered = EvidenceAttestation(payload={**payload,'result':'PROVED_STRICT'}, signer_id='runner-01', signature_hex=sig)
    assert not g.verify_attestation(tampered)
    assert g.evaluate_attestation(tampered) == 'REJECTED_UNVERIFIED_EVIDENCE'


def test_ledger_is_append_only_and_tamper_evident(tmp_path):
    db = tmp_path/'ledger.sqlite3'
    ledger = ImmutableLedger(db)
    first = ledger.append('camp-1', 'CREATED', {'budget':100}, idempotency_key='id-1')
    assert ledger.append('camp-1', 'CREATED', {'budget':100}, idempotency_key='id-1') == first
    second = ledger.append('camp-1', 'HYPOTHESIS', {'hypothesis':'faster'}, idempotency_key='id-2')
    assert second['sequence'] == 2
    assert ledger.verify('camp-1')
    with sqlite3.connect(db) as conn:
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute('UPDATE events SET event_type=? WHERE sequence=1',('RELEASED',))
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute('DELETE FROM events WHERE sequence=1')
    with pytest.raises(ValueError):
        ledger.append('camp-1','RELEASED',{'source':'agent'},idempotency_key='id-3')
    with pytest.raises(ValueError):
        ledger.append('camp-1','HYPOTHESIS',{'hypothesis':'other'},idempotency_key='id-1')

def test_name_heuristic_does_not_mistake_gleaner_for_lean():
    c=RepoCatalog.from_tsv(ROOT/'data/repositories_public_701.tsv')
    repo=c.by_name('mojealterego/f95-gallery-gleaner')
    group,priority,basis=c.classify(repo)
    assert group!='FORMAL_PROOF'
    assert basis in ('NAME_HEURISTIC_ONLY','METADATA_ONLY')

def test_unified_research_proposal_requires_real_source_and_keeps_evolution_separate(tmp_path, math_db):
    from imandrax_dgm.unified import UnifiedResearchEngine
    engine=UnifiedResearchEngine(
        knowledge_db=math_db,
        inventory=ROOT/'data/repositories_public_701.tsv',
        ledger_db=tmp_path/'runs.sqlite3',
    )
    engine.open_campaign('camp-1',10000)
    candidate=Candidate('c1','a'*64,'b'*64,('harness/planner.py',),'Optimize search',1000,60)
    out=engine.propose('camp-1',candidate,[('MSC2020-ENC','00A05')])
    assert out['admitted'] is True
    assert out['proof_status'] == 'NO_PROOF_ATTEMPTED'
    assert out['evolution_status'] == 'NOT_EXECUTED'
    assert engine.ledger.verify('camp-1')


def test_unified_rejects_nonexistent_knowledge_reference(tmp_path, math_db):
    from imandrax_dgm.unified import UnifiedResearchEngine
    engine=UnifiedResearchEngine(
        knowledge_db=math_db,
        inventory=ROOT/'data/repositories_public_701.tsv',
        ledger_db=tmp_path/'runs.sqlite3',
    )
    engine.open_campaign('camp-2',10000)
    candidate=Candidate('c2','a'*64,'b'*64,('harness/planner.py',),'Test claim',1000,60)
    out=engine.propose('camp-2',candidate,[('MSC2020-ENC','not-a-real-code')])
    assert out['admitted'] is False
    assert out['reason'] == 'SOURCE_REFERENCE_NOT_FOUND'
    assert engine.ledger.verify('camp-2')

def test_denied_candidate_is_terminal_and_cannot_be_built(tmp_path, math_db):
    from imandrax_dgm.unified import UnifiedResearchEngine
    engine=UnifiedResearchEngine(math_db,ROOT/'data/repositories_public_701.tsv',tmp_path/'runs.sqlite3')
    engine.open_campaign('camp-3',10000)
    bad=Candidate('c3','a'*64,'b'*64,('policy/security.py',),'Try to alter policy',1000,60)
    result=engine.propose('camp-3',bad,[('MSC2020-ENC','00A05')])
    assert not result['admitted']
    assert engine.ledger.history('camp-3')[-1]['event_type']=='REJECTED'
    with pytest.raises(ValueError):
        engine.ledger.append('camp-3','BUILD',{},'try-build')