import json
from pathlib import Path
import shutil
import socket
import subprocess

import pytest

from imandrax_dgm.apex import ApexError
from imandrax_dgm.local_runtime import LocalConfig, LocalRuntime, PLATFORMS
from scripts.check_architecture import check

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def local_config(tmp_path, math_db):
    assets = tmp_path/'assets'
    assets.mkdir()
    shutil.copyfile(math_db, assets/'mathematics.sqlite3')
    shutil.copyfile(ROOT/'data/repositories_public_701.tsv', assets/'repositories_public_701.tsv')
    return LocalConfig('linux', assets, tmp_path/'state')


def request(ident='request-001'):
    return {'api_version': 1, 'request_id': ident, 'operation': 'imandrax.math',
            'payload': {'operation': 'gcd', 'arguments': {'a': 84, 'b': 36}}}


@pytest.mark.parametrize('platform', PLATFORMS)
def test_local_contract_runs_without_network_git_or_docker(local_config, platform, monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError('No network or subprocess in local runtime')
    monkeypatch.setattr(socket, 'socket', denied)
    monkeypatch.setattr(subprocess, 'Popen', denied)
    config = LocalConfig(platform, local_config.assets, local_config.state)
    before = {p.name: p.read_bytes() for p in config.assets.iterdir()}
    runtime = LocalRuntime(config)
    identity = runtime.resume()['runtime']['identity_id']
    result = runtime.request(request())
    assert result['output']['value'] == 12
    assert result['output']['proof_status'] == 'NOT_FORMALLY_PROVED'
    assert runtime.suspend()['runtime']['state'] == 'PAUSED'
    with pytest.raises(ApexError):
        runtime.request(request('paused-request'))
    reopened = LocalRuntime(config)
    assert reopened.status()['runtime']['identity_id'] == identity
    assert reopened.status()['runtime']['state'] == 'PAUSED'
    reopened.resume()
    with pytest.raises(ApexError, match='DUPLICATE_REQUEST'):
        reopened.request(request())
    assert reopened.request(request('request-002'))['output']['value'] == 12
    assert {p.name: p.read_bytes() for p in config.assets.iterdir()} == before
    assert reopened.status()['network_required'] is False


def test_future_layout_rejected_without_database_mutation(local_config):
    runtime = LocalRuntime(local_config)
    runtime.resume()
    marker = local_config.state/'local-layout.json'
    marker.write_text(json.dumps({'api_version': 1, 'state_version': 2}))
    before = {p.name: p.read_bytes() for p in local_config.state.iterdir()}
    with pytest.raises(ValueError, match='STATE_MIGRATION_REQUIRED'):
        LocalRuntime(local_config)
    assert {p.name: p.read_bytes() for p in local_config.state.iterdir()} == before


def test_local_capabilities_and_contracts_fail_closed(local_config):
    runtime = LocalRuntime(local_config)
    runtime.resume()
    for operation in ('rsi.proposals', 'release', 'deploy', 'unknown'):
        with pytest.raises(ApexError, match='LOCAL_CAPABILITY_UNAVAILABLE'):
            runtime.request({**request(), 'operation': operation})
    for version in (True, 0, 2, '1'):
        with pytest.raises(ValueError, match='UNSUPPORTED_REQUEST_CONTRACT'):
            runtime.request({**request(), 'api_version': version})
    with pytest.raises(ValueError):
        LocalRuntime(LocalConfig('unknown', local_config.assets, local_config.state))
    with pytest.raises(ValueError, match='DISJOINT'):
        LocalRuntime(LocalConfig('android', local_config.assets, local_config.assets/'state'))


def test_boundaries_and_negative_dependency_injection(tmp_path):
    assert check(ROOT)['errors'] == []
    shutil.copytree(ROOT/'architecture', tmp_path/'architecture')
    shutil.copytree(ROOT/'src/imandrax_dgm', tmp_path/'src/imandrax_dgm')
    path = tmp_path/'src/imandrax_dgm/engine.py'
    path.write_text(path.read_text()+'\nfrom .sandbox import DockerSandbox\nimport subprocess\n')
    errors = check(tmp_path)['errors']
    assert 'forbidden dependency: engine -> sandbox' in errors
    assert 'nonportable core import: engine -> subprocess' in errors
    (tmp_path/'src/imandrax_dgm/new_plugin.py').write_text('')
    assert 'unclassified or missing module: new_plugin' in check(tmp_path)['errors']


def test_distribution_build_is_deferred():
    import yaml
    workflow = yaml.safe_load((ROOT/'.github/workflows/python-ci.yml').read_text())
    assert workflow['jobs']['wheel-and-artifact-integrity']['if'] == '${{ false }}'


def test_dependency_cycle_is_rejected(tmp_path):
    shutil.copytree(ROOT/'architecture', tmp_path/'architecture')
    shutil.copytree(ROOT/'src/imandrax_dgm', tmp_path/'src/imandrax_dgm')
    path = tmp_path/'src/imandrax_dgm/gates.py'
    path.write_text(path.read_text()+'\nfrom .evaluation_policy import SandboxError\n')
    path = tmp_path/'src/imandrax_dgm/evaluation_policy.py'
    path.write_text(path.read_text()+'\nfrom .gates import Policy\n')
    assert any(e.startswith('dependency cycle:') for e in check(tmp_path)['errors'])
