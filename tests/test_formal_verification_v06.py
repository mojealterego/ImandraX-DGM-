"""Regression contract: no classification code or LLM output is itself a proof."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from imandrax_dgm.formal_verification import (
    FormalEvidenceRegistry,
    FormalVerificationError,
    ProofEvidence,
    ProofSpec,
    validate_proof_sources,
)

ROOT = Path(__file__).resolve().parents[1]


def _spec(tmp_path: Path) -> ProofSpec:
    source = tmp_path / 'proof.lean'
    source.write_text('namespace T\ntheorem example : True := True.intro\nend T\n', encoding='utf-8')
    return ProofSpec('T.example', '03-XX', 'ImandraXMathlib', 'proof.lean', hashlib.sha256(source.read_bytes()).hexdigest())


def test_all_6006_msc_entries_start_unproved():
    rows = list(csv.DictReader((ROOT / 'data/msc2020_6006_coverage.csv').open(encoding='utf-8')))
    assert len(rows) == 6006
    assert all(row['verified_proof'] == 'NO' for row in rows)
    assert all(row['formalized_in_lean'] == 'NOT_AUDITED' for row in rows)


def test_coverage_registry_default_denies(tmp_path):
    spec = _spec(tmp_path)
    registry = FormalEvidenceRegistry(tmp_path / 'registry.sqlite3')
    result = registry.register(spec, source_root=tmp_path)
    assert result['status'] == 'UNVERIFIED'
    assert registry.get(spec.declaration)['status'] == 'UNVERIFIED'
    assert registry.msc_coverage('03-XX') == {'total': 1, 'verified': 0}


def test_source_integrity_and_forbidden_proof_holes(tmp_path):
    spec = _spec(tmp_path)
    assert validate_proof_sources(spec, tmp_path) is True
    (tmp_path / 'proof.lean').write_text('theorem bogus : False := by sorry\n')
    with pytest.raises(FormalVerificationError):
        validate_proof_sources(spec, tmp_path)
    (tmp_path / 'proof.lean').write_text('axiom bogus : False\n')
    with pytest.raises(FormalVerificationError):
        validate_proof_sources(spec, tmp_path)


def test_path_traversal_and_sha_mismatch_denied(tmp_path):
    spec = _spec(tmp_path)
    with pytest.raises(FormalVerificationError):
        validate_proof_sources(ProofSpec(spec.declaration, spec.msc_code, spec.module, '../proof.lean', spec.source_sha256), tmp_path)
    with pytest.raises(FormalVerificationError):
        validate_proof_sources(ProofSpec(spec.declaration, spec.msc_code, spec.module, spec.source_path, '0'*64), tmp_path)


def test_unsigned_and_self_attested_checkers_denied(tmp_path):
    spec = _spec(tmp_path)
    registry = FormalEvidenceRegistry(tmp_path / 'registry.sqlite3')
    registry.register(spec, source_root=tmp_path)
    evidence = ProofEvidence(declaration=spec.declaration, source_sha256=spec.source_sha256,
        toolchain='leanprover/lean4:v4.36.0-rc2', base_commit='a'*40,
        kernel='PASS', independent='PASS', checker='nanoda', runner='github-actions',
        workflow_run='https://github.com/mojealterego/ImandraX-DGM-/actions/runs/1')
    with pytest.raises(FormalVerificationError, match='signed'):
        registry.verify(evidence)
    assert registry.get(spec.declaration)['status'] == 'UNVERIFIED'


def test_workflow_has_full_mathlib_target_and_paranoid_external_check():
    wf = (ROOT / '.github/workflows/lean-full-formal-verification.yml').read_text()
    assert 'lake build Mathlib' in wf
    assert 'lake check --paranoid' in wf
    assert 'lake-package-directory' not in wf or 'proofs_mathlib' in wf
    assert 'docker run --rm --network none --read-only --cap-drop ALL' in wf
    assert '--security-opt no-new-privileges' in wf
    assert '--inadvisably-no-sandbox' in wf
    assert 'continue-on-error: true' not in wf
    assert 'd0207795ac79006da92d98544e1ce915ae386160' in wf


def test_mathlib_workspace_pinned_and_has_real_proofs():
    conf = (ROOT / 'proofs_mathlib/lakefile.toml').read_text()
    assert 'd0207795ac79006da92d98544e1ce915ae386160' in conf
    assert 'ImandraXMathlib' in conf
    proof = (ROOT / 'proofs_mathlib/ImandraXMathlib/Foundations.lean').read_text()
    assert 'theorem' in proof and '\n  ring' in proof
    assert 'sorry' not in proof and 'axiom' not in proof


def test_proof_mapping_is_only_a_claim_until_checker_evidence():
    mappings = json.loads((ROOT / 'proofs_mathlib/msc_mapping.json').read_text())
    assert mappings and all(item['status'] == 'PROOF_SOURCE_UNVERIFIED' for item in mappings)
    assert len({item['declaration'] for item in mappings}) == len(mappings)
    assert all(len(item['msc_code']) == 5 for item in mappings)


def test_signed_external_runner_can_mark_only_exact_source(tmp_path):
    from dataclasses import asdict, replace
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    from imandrax_dgm.gates import canonical_payload
    signer = Ed25519PrivateKey.generate()
    pub = signer.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    spec = _spec(tmp_path)
    registry = FormalEvidenceRegistry(tmp_path/'reg.sqlite3', trusted_runner_keys={'trusted-ci': pub})
    registry.register(spec, source_root=tmp_path)
    evidence = ProofEvidence(spec.declaration, spec.source_sha256, 'leanprover/lean4:v4.36.0-rc2',
        'a'*40, 'PASS', 'PASS', 'nanoda', 'trusted-ci',
        'https://github.com/mojealterego/ImandraX-DGM-/actions/runs/123')
    sig = signer.sign(canonical_payload(asdict(evidence))).hex()
    with pytest.raises(FormalVerificationError, match='signature'):
        registry.verify(replace(evidence, base_commit='b'*40), signer_id='trusted-ci', signature_hex=sig)
    assert registry.get(spec.declaration)['status'] == 'UNVERIFIED'
    assert registry.verify(evidence, signer_id='trusted-ci', signature_hex=sig)['status'] == 'EXTERNALLY_CHECKED'
    assert registry.msc_coverage(spec.msc_code) == {'total': 1, 'verified': 1}
    with pytest.raises(FormalVerificationError, match='sealed'):
        registry.verify(evidence, signer_id='trusted-ci', signature_hex=sig)


def test_audit_report_does_not_claim_unchecked_proofs():
    from scripts.proof_coverage_report import report
    result = report(ROOT/'data/msc2020_6006_coverage.csv',
        ROOT/'proofs_mathlib/msc_mapping.json',
        ROOT/'proofs_mathlib/ImandraXMathlib/Foundations.lean')
    assert result['total_detailed_subject_codes'] == 6006
    assert result['source_mapped_declarations'] == 9
    assert result['externally_verified_declarations'] == 0
    assert result['mapped_subject_codes'] < 6006


def test_audit_report_rejects_msc_fabrication(tmp_path):
    from scripts.proof_coverage_report import report
    mapping = json.loads((ROOT/'proofs_mathlib/msc_mapping.json').read_text())
    mapping[0]['msc_code'] = '99Z99'
    f = tmp_path/'bad.json'
    f.write_text(json.dumps(mapping))
    with pytest.raises(ValueError, match='mapping'):
        report(ROOT/'data/msc2020_6006_coverage.csv', f,
            ROOT/'proofs_mathlib/ImandraXMathlib/Foundations.lean')


def test_core_lake_default_target_is_not_noop():
    import tomllib
    config = tomllib.loads((ROOT/'proofs/lakefile.toml').read_text())
    assert 'ImandraX' in config['defaultTargets']
    assert any(x['name'] == 'ImandraX' for x in config['lean_lib'])


def test_integrated_engine_exposes_registry_without_inventing_proof(tmp_path, math_db):
    from imandrax_dgm.engine import IntegratedEngine, MathTask
    engine = IntegratedEngine(knowledge_db=math_db,
        inventory=ROOT/'data/repositories_public_701.tsv',
        ledger_db=tmp_path/'ledger.sqlite3', review_db=tmp_path/'reviews.sqlite3',
        archive_db=tmp_path/'archive.sqlite3', formal_registry_db=tmp_path/'formal.sqlite3')
    spec = _spec(tmp_path)
    engine.formal.register(spec, source_root=tmp_path)
    result = engine.math(MathTask(kind='FORMAL_PROOF_STATUS', statement=spec.declaration))
    assert result['status'] == 'UNVERIFIED'
    assert result['proof_status'] == 'NOT_PROVED'
    assert result['declaration'] == spec.declaration
    with pytest.raises(ValueError):
        engine.math(MathTask(kind='FORMAL_PROOF_STATUS', statement='No.such.theorem'))


def test_lean_import_must_be_first_nonblank_line():
    source = (ROOT/'proofs_mathlib/ImandraXMathlib/Foundations.lean').read_text()
    assert source.lstrip().startswith('import Mathlib')
