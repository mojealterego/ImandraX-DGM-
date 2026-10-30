import hashlib
import json
from pathlib import Path

import pytest

from imandrax_dgm.simulation import ReferenceEvaluator, fixture_sources, run_simulation
from imandrax_dgm.sandbox import SandboxError

ROOT = Path(__file__).resolve().parents[1]


def test_full_simulation_persists_lineage_and_binds_evidence(tmp_path):
    output = tmp_path/'simulation'
    report = run_simulation(root=ROOT, output=output)
    assert report['status'] == 'SIMULATION_PASS'
    assert all(report['checks'].values())
    assert report['release_authorized'] is False
    assert report['arithmetic'] == {'passed': 300, 'total': 300}
    assert any(r['depth'] > 0 for r in report['genealogy'])
    assert all(r['selected']['regression_counts']['passed'] == 30 for r in report['runs'])
    manifest = json.loads((output/'SHA256SUMS.json').read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest() == digest
    with pytest.raises(FileExistsError):
        run_simulation(root=ROOT, output=output)


def test_reference_dispatch_rejects_arbitrary_code_and_measures_failures(tmp_path):
    evaluator = ReferenceEvaluator()
    marker = tmp_path/'executed'
    with pytest.raises(SandboxError):
        evaluator.evaluate(f'open({str(marker)!r}, "w").write("bad")', [])
    assert not marker.exists()
    sources = list(fixture_sources())
    cases = [{'operation': 'gcd', 'a': 0, 'b': -12, 'expected': 12},
             {'operation': 'mod_pow', 'a': -3, 'b': 0, 'mod': 2, 'expected': 1},
             {'operation': 'is_prime', 'n': 0, 'expected': False},
             {'operation': 'is_prime', 'n': 2, 'expected': True}]
    assert evaluator.evaluate(sources[0], cases)['passed'] == 0
    for source in sources[1:]:
        assert evaluator.evaluate(source, cases)['passed'] == 4
    wrong_oracle = [{**cases[0], 'expected': 99}]
    assert evaluator.evaluate(sources[1], wrong_oracle)['passed'] == 0


@pytest.mark.parametrize('generations', [0, 3, True])
def test_budget_rejected_before_writes(tmp_path, generations):
    with pytest.raises(ValueError):
        run_simulation(root=ROOT, output=tmp_path/'new', generations=generations)
    assert not (tmp_path/'new').exists()


def test_repository_output_denied():
    with pytest.raises(ValueError, match='outside'):
        run_simulation(root=ROOT, output=ROOT/'simulation-output')


def test_cli_simulation(tmp_path, capsys):
    from imandrax_dgm.cli import main
    assert main(['--root', str(ROOT), 'simulate', '--output', str(tmp_path/'run'),
                 '--generations', '1']) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'SIMULATION_PASS'


def test_unavailable_docker_records_failure_without_reference_fallback(tmp_path, monkeypatch):
    def unavailable(self, *args, **kwargs):
        raise SandboxError('Runtime unavailable')
    monkeypatch.setattr('imandrax_dgm.simulation.DockerSandbox.evaluate', unavailable)
    report = run_simulation(root=ROOT, output=tmp_path/'failed', backend='docker',
                            image='python@sha256:' + 'a'*64)
    assert report['status'] == 'SIMULATION_FAIL'
    assert report['backend'] == 'docker'
    assert not report['checks']['all_cycles_selected']
    assert not report['checks']['transfer_cases']
    assert all(r['error'] == 'Runtime unavailable' for r in report['transfer'])
    assert report['release_authorized'] is False
