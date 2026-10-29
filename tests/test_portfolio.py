"""Read-only portfolio audit gates: evidence never authorizes integration."""
import csv
import json
from pathlib import Path

import pytest

from imandrax_dgm.portfolio import PortfolioAudit, PortfolioEvidenceError


def _inventory(tmp_path: Path) -> Path:
    path = tmp_path / 'repositories.tsv'
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t')
        writer.writerow(('repository_full_name', 'repository_id', 'size_kb',
                         'default_branch', 'visibility', 'archived', 'url'))
        for index, name in enumerate(('mathlib4', 'dgm', 'irrelevant'), 1):
            writer.writerow((f'mojealterego/{name}', str(index), '123', 'main',
                             'public', 'false', f'https://github.com/mojealterego/{name}'))
    return path


def _evidence(tmp_path: Path, entries: list[dict]) -> Path:
    path = tmp_path / 'evidence.json'
    path.write_text(json.dumps({'schema_version': 1, 'evidence': entries}), encoding='utf-8')
    return path


def _record(name: str = 'mathlib4', *, license_sha: str | None = 'b' * 40,
            license_marker: str = 'Apache-2.0') -> dict:
    return {'repository': f'mojealterego/{name}', 'readme_blob_sha': 'a' * 40,
            'license_blob_sha': license_sha, 'license_marker': license_marker}


def test_root_evidence_never_authorizes_code_integration(tmp_path):
    audit = PortfolioAudit.from_paths(_inventory(tmp_path), _evidence(tmp_path, [_record()]))
    report = audit.report(limit=3)
    assert report['catalog_total'] == 3
    assert report['readme_inspected'] == 1
    assert report['license_files_inspected'] == 1
    assert report['source_audited'] == 0
    assert report['ready_for_integration'] == 0
    assert report['integration_gate'] == 'BLOCKED_PENDING_OWNER_APPROVAL_AND_AUDIT'
    mathlib = next(x for x in report['candidates'] if x['repository'] == 'mojealterego/mathlib4')
    assert mathlib['priority'] == 'P0'
    assert mathlib['root_evidence'] == 'README_AND_LICENSE_HEADER_INSPECTED'
    assert mathlib['license_marker'] == 'Apache-2.0'
    assert mathlib['integration_status'] == 'NOT_INTEGRATED'
    assert 'OWNER_SIGNED_MANIFEST_EPOCH' in mathlib['missing_gates']
    assert 'INDEPENDENT_SOURCE_AND_SECURITY_AUDIT' in mathlib['missing_gates']
    assert all(x['integration_status'] == 'NOT_INTEGRATED' for x in report['candidates'])


def test_no_evidence_is_not_conflated_with_readme_inspection(tmp_path):
    audit = PortfolioAudit.from_paths(_inventory(tmp_path), _evidence(tmp_path, []))
    report = audit.report(limit=3)
    assert report['readme_inspected'] == 0
    assert report['license_files_inspected'] == 0
    assert all(x['root_evidence'] == 'NOT_REVIEWED' for x in report['candidates'])


@pytest.mark.parametrize('records', [
    [_record(), _record()],
    [_record('unknown')],
    [{**_record(), 'readme_blob_sha': 'not-a-sha'}],
    [_record(license_sha=None, license_marker='Apache-2.0')],
    [{**_record(), 'extra': 'unexpected'}],
    [{**_record(), 'license_marker': 'UNRESTRICTED'}],
])
def test_malformed_or_untrusted_evidence_is_rejected(tmp_path, records):
    with pytest.raises(PortfolioEvidenceError):
        PortfolioAudit.from_paths(_inventory(tmp_path), _evidence(tmp_path, records))


def test_duplicate_json_keys_are_rejected(tmp_path):
    path = _evidence(tmp_path, [])
    path.write_text('{"schema_version":1,"schema_version":1,"evidence":[]}', encoding='utf-8')
    with pytest.raises(PortfolioEvidenceError, match='DUPLICATE'):
        PortfolioAudit.from_paths(_inventory(tmp_path), path)


def test_limits_and_output_order_are_deterministic(tmp_path):
    audit = PortfolioAudit.from_paths(_inventory(tmp_path), _evidence(tmp_path, [_record('dgm')]))
    assert [r['repository'] for r in audit.report(limit=2)['candidates']] == [
        'mojealterego/mathlib4', 'mojealterego/dgm']
    for limit in (0, -1, 4, True, '2'):
        with pytest.raises(ValueError):
            audit.report(limit=limit)


def test_license_header_without_compatibility_review_is_not_license_approval(tmp_path):
    audit = PortfolioAudit.from_paths(_inventory(tmp_path), _evidence(tmp_path, [_record()]))
    row = audit.report(limit=1)['candidates'][0]
    assert row['license_compatibility'] == 'NOT_AUDITED'
    assert 'LICENSE_COMPATIBILITY_REVIEW' in row['missing_gates']
    assert 'SBOM_AND_DEPENDENCY_REVIEW' in row['missing_gates']


def test_checked_in_root_evidence_is_well_formed(tmp_path):
    root = Path(__file__).resolve().parents[1]
    evidence_path = root / 'data' / 'portfolio_root_evidence_v1.json'
    rows = json.loads(evidence_path.read_text(encoding='utf-8'))['evidence']
    assert len(rows) == 18
    assert sum(row['license_blob_sha'] is not None for row in rows) == 15
    inventory = tmp_path / 'catalog.tsv'
    with inventory.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t')
        writer.writerow(('repository_full_name', 'repository_id', 'size_kb',
                         'default_branch', 'visibility', 'archived', 'url'))
        for i, row in enumerate(rows, 1):
            repo = row['repository']
            writer.writerow((repo, str(i), '1', 'main', 'public', 'false',
                             'https://github.com/' + repo))
    report = PortfolioAudit.from_paths(inventory, evidence_path).report(limit=18)
    assert report['catalog_total'] == 18
    assert report['readme_inspected'] == 18
    assert report['license_files_inspected'] == 15
    assert report['ready_for_integration'] == 0
