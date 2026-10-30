"""RED: code execution is possible only inside a no-network resource-capped container."""
from pathlib import Path
import json
import subprocess
import pytest
from imandrax_dgm.sandbox import DockerSandbox, SandboxError, make_math_cases


def test_docker_command_is_networkless_and_unprivileged(tmp_path):
    worker=tmp_path/'worker.py';worker.write_text('print(1)')
    sandbox=DockerSandbox(image='python:3.12-slim',worker=worker,allow_unpinned_for_ci=True)
    cmd=sandbox.command(tmp_path/'input', 'case-test')
    assert cmd[:2]==['docker','run']
    assert cmd[cmd.index('--network')+1]=='none'
    assert cmd[cmd.index('--read-only')+1]=='--cap-drop'
    assert cmd[cmd.index('--cap-drop')+1]=='ALL'
    assert cmd[cmd.index('--user')+1]=='65534:65534'
    assert '--privileged' not in cmd
    assert '--security-opt' in cmd
    assert 'python:3.12-slim' in cmd
    assert 'sh' not in cmd


def test_unpinned_image_denied_by_default(tmp_path):
    with pytest.raises(SandboxError):
        DockerSandbox(image='python:3.12-slim',worker=tmp_path/'worker.py')


def test_sandbox_runs_only_via_docker_with_bounded_output(tmp_path):
    worker=tmp_path/'worker.py';worker.write_text('print(1)')
    calls=[]
    def fake_run(cmd, **kw):
        calls.append((cmd,kw))
        mount = next(arg for arg in cmd if 'dst=/trusted/worker.py' in arg)
        staged = Path(mount.split('src=')[1].split(',')[0])
        assert staged.read_bytes() == worker.read_bytes()
        assert staged.stat().st_mode & 0o777 == 0o644
        assert staged != worker
        return subprocess.CompletedProcess(cmd,0,stdout=json.dumps({'passed':1,'total':1,'duration_ms':1}),stderr='')
    sandbox=DockerSandbox(image='python:3.12-slim',worker=worker,allow_unpinned_for_ci=True,run=fake_run)
    result=sandbox.evaluate('def solve(task): return 1', [{'operation':'gcd','a':2,'b':4,'expected':2}],timeout=30)
    assert result['passed']==1
    assert calls[0][1]['timeout']==30
    assert calls[0][1]['shell'] is False
    assert calls[0][1]['env']=={'PATH':'/usr/local/bin:/usr/bin:/bin'}
    assert '--network' in calls[0][0]


def test_sandbox_timeout_forces_container_cleanup(tmp_path):
    worker=tmp_path/'worker.py';worker.write_text('print(1)')
    commands=[]
    def fake_run(cmd,**kw):
        commands.append(cmd)
        if cmd[:2]==['docker','run']:
            raise subprocess.TimeoutExpired(cmd,1)
        return subprocess.CompletedProcess(cmd,0,'','')
    sandbox=DockerSandbox(image='python:3.12-slim',worker=worker,allow_unpinned_for_ci=True,run=fake_run)
    with pytest.raises(SandboxError):
        sandbox.evaluate('def solve(task): return 1',[],timeout=1)
    assert commands[-1][:3]==['docker','rm','-f']


def test_cases_have_deterministic_oracle_and_multiple_domains():
    cases=make_math_cases(seed=42,count=20)
    assert len(cases)==20
    assert set(x['operation'] for x in cases)=={'gcd','mod_pow','is_prime'}
    assert make_math_cases(seed=42,count=20)==cases
