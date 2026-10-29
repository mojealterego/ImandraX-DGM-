"""RED-first tests: signed human approval gates all RSI source modifications."""
import hashlib
import json
from pathlib import Path
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from imandrax_dgm.gates import Candidate, EvidenceAttestation, canonical_payload
from imandrax_dgm.rsi import RSIReviewStore, RSIInbox, ApprovalEnvelope, ApprovalRequired


def keys():
    runner = Ed25519PrivateKey.generate()
    human = Ed25519PrivateKey.generate()
    def public(k):
        return k.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return runner, human, public(runner), public(human)


def candidate(ident='c1', path='harness/planner.py'):
    return Candidate(ident, 'a'*64, 'b'*64, (path,), 'Optimize proof search based on failure analysis', 1000, 30)


def store(tmp_path):
    runner, human, rp, hp = keys()
    db = RSIReviewStore(tmp_path/'rsi.sqlite3', runner_keys={'runner-01':rp}, reviewer_keys={'user-01':hp})
    return db, runner, human


def sign_attestation(runner, proposal, suite, result='PASS'):
    payload={'candidate_digest':proposal['manifest_digest'], 'source_digest':proposal['base_digest'],
             'suite':suite, 'result':result, 'runner_id':'runner-01'}
    return EvidenceAttestation(payload, 'runner-01', runner.sign(canonical_payload(payload)).hex())


def sign_review(human, packet, decision='APPROVE', expires_at=9999999999):
    payload={**packet, 'decision':decision, 'reviewer_id':'user-01', 'expires_at':expires_at}
    return ApprovalEnvelope(payload, 'user-01', human.sign(canonical_payload(payload)).hex())


def test_default_denies_unsigned_approval(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    assert proposal['state']=='PROPOSED'
    assert not db.is_authorized('c1')
    with pytest.raises(ApprovalRequired):
        db.decide(ApprovalEnvelope({**db.review_packet('c1'), 'decision':'APPROVE', 'reviewer_id':'user-01','expires_at':9999999999}, 'user-01','00'))
    assert not db.is_authorized('c1')


def test_signed_evidence_and_explicit_user_approval(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    for suite in ('STATIC_CHECK','REGRESSION','SECURITY','HELDOUT'):
        db.record_evidence('c1',sign_attestation(runner,proposal,suite))
    packet=db.review_packet('c1')
    assert packet['manifest_digest']==proposal['manifest_digest']
    assert not db.is_authorized('c1')
    db.decide(sign_review(human,packet))
    assert db.is_authorized('c1')
    assert db.status('c1')['state']=='APPROVED'
    assert not hasattr(db,'apply_patch')


def test_failed_or_missing_evidence_blocks_approval(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    db.record_evidence('c1',sign_attestation(runner,proposal,'STATIC_CHECK','FAIL'))
    with pytest.raises(ApprovalRequired):
        db.decide(sign_review(human,db.review_packet('c1')))
    assert not db.is_authorized('c1')


def test_tampered_runner_attestation_rejected(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    a=sign_attestation(runner,proposal,'SECURITY')
    bad=EvidenceAttestation({**a.payload,'result':'PASS','suite':'HELDOUT'},a.signer_id,a.signature_hex)
    with pytest.raises(ApprovalRequired):
        db.record_evidence('c1',bad)


def test_review_signature_binds_exact_manifest_and_policy(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    for suite in ('STATIC_CHECK','REGRESSION','SECURITY','HELDOUT'):
        db.record_evidence('c1',sign_attestation(runner,proposal,suite))
    packet=db.review_packet('c1')
    a=sign_review(human,packet)
    with pytest.raises(ApprovalRequired):
        db.decide(ApprovalEnvelope({**a.payload,'manifest_digest':'0'*64},a.signer_id,a.signature_hex))
    assert not db.is_authorized('c1')


def test_review_expiry_and_rejection_are_final(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    for suite in ('STATIC_CHECK','REGRESSION','SECURITY','HELDOUT'):
        db.record_evidence('c1',sign_attestation(runner,proposal,suite))
    packet=db.review_packet('c1')
    with pytest.raises(ApprovalRequired):
        db.decide(sign_review(human,packet,expires_at=1))
    db.decide(sign_review(human,packet,decision='REJECT'))
    assert db.status('c1')['state']=='REJECTED'
    with pytest.raises(ApprovalRequired):
        db.decide(sign_review(human,packet))


def test_replay_and_policy_path_denied(tmp_path):
    db, runner, human=store(tmp_path)
    db.submit(candidate())
    assert db.submit(candidate())['state']=='PROPOSED'
    with pytest.raises(ValueError):
        db.submit(candidate('c1','harness/other.py'))
    with pytest.raises(ApprovalRequired):
        db.submit(candidate('escape','security/keys.py'))
    with pytest.raises(ApprovalRequired):
        db.submit(candidate('escape2','harness/../security/keys.py'))


def test_inbox_research_cycle_only_registers_proposals(tmp_path):
    db, runner, human=store(tmp_path)
    inbox=tmp_path/'inbox';inbox.mkdir()
    c=candidate()
    (inbox/'c1.json').write_text(json.dumps(c.__dict__),encoding='utf-8')
    queue=RSIInbox(db,inbox)
    result=queue.tick()
    assert result['submitted']==1
    assert queue.tick()['submitted']==0
    assert db.status('c1')['state']=='PROPOSED'
    assert not db.is_authorized('c1')
    assert not hasattr(queue,'apply_patch')


def test_inbox_ignores_symlinks_and_untrusted_files(tmp_path):
    db, runner, human=store(tmp_path)
    inbox=tmp_path/'inbox';inbox.mkdir()
    outside=tmp_path/'secret.json';outside.write_text(json.dumps(candidate().__dict__),encoding='utf-8')
    (inbox/'alias.json').symlink_to(outside)
    (inbox/'bad.json').write_text('{broken',encoding='utf-8')
    result=RSIInbox(db,inbox).tick()
    assert result['submitted']==0
    assert result['rejected']>=2


def test_no_trusted_human_key_means_no_approval(tmp_path):
    runner, human, rp, hp=keys()
    db=RSIReviewStore(tmp_path/'rsi.sqlite3',runner_keys={'runner-01':rp},reviewer_keys={})
    proposal=db.submit(candidate())
    for suite in ('STATIC_CHECK','REGRESSION','SECURITY','HELDOUT'):
        db.record_evidence('c1',sign_attestation(runner,proposal,suite))
    with pytest.raises(ApprovalRequired):
        db.decide(sign_review(human,db.review_packet('c1')))


def test_approval_cannot_be_forged_by_editing_sqlite_state(tmp_path):
    import sqlite3
    db, runner, human=store(tmp_path)
    db.submit(candidate())
    with sqlite3.connect(tmp_path/'rsi.sqlite3') as con:
        con.execute("UPDATE proposals SET state='APPROVED' WHERE proposal_id='c1'")
    assert not db.is_authorized('c1')


def test_expired_signature_no_longer_authorizes(tmp_path):
    db, runner, human=store(tmp_path)
    proposal=db.submit(candidate())
    for suite in ('STATIC_CHECK','REGRESSION','SECURITY','HELDOUT'):
        db.record_evidence('c1',sign_attestation(runner,proposal,suite))
    packet=db.review_packet('c1')
    db.decide(sign_review(human,packet,expires_at=1000),now=500)
    assert db.is_authorized('c1',now=999)
    assert not db.is_authorized('c1',now=1000)


def test_operator_can_inspect_exact_proposal_manifest(tmp_path):
    db, runner, human=store(tmp_path)
    db.submit(candidate())
    details=db.details('c1')
    assert details['manifest']['hypothesis']=='Optimize proof search based on failure analysis'
    assert details['manifest']['paths']==['harness/planner.py']
    assert details['state']=='PROPOSED'