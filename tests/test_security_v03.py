"""Additional adversarial tests for the new autonomous boundaries."""
import json
from pathlib import Path
import subprocess
import pytest
from imandrax_dgm.sandbox import static_security_check, DockerSandbox, SandboxError
from imandrax_dgm.research_engine import LLMConfig, LLMClient, ResearchError, OpenAlexResearch
from imandrax_dgm.generator import ProposalGenerator, ProposalError


@pytest.mark.parametrize('code',[
    'import os\ndef solve(task): return 1',
    'from subprocess import run\ndef solve(task): return 1',
    'def solve(task): return open("/etc/passwd").read()',
    'def solve(task): return task.__class__',
    'def nope(task): return 1',
    'def solve(task):\n    return eval("2+2")',
])
def test_static_security_denies_unsafe_code(code):
    assert not static_security_check(code)['pass']


def test_sandbox_rejects_forged_result_count(tmp_path):
    worker=tmp_path/'worker.py';worker.write_text('print(1)')
    def fake(cmd,**kw):
        return subprocess.CompletedProcess(cmd,0,json.dumps({'passed':99,'total':99,'duration_ms':0}),'')
    runner=DockerSandbox(image='python:3.12-slim',worker=worker,allow_unpinned_for_ci=True,run=fake)
    with pytest.raises(SandboxError):
        runner.evaluate('def solve(task): return 1',[{'expected':1}],timeout=10)


def test_llm_output_is_strict_json_and_request_has_no_extra_authority():
    class Response:
        status=200
        headers={'Content-Type':'application/json'}
        def read(self,n):
            return json.dumps({'choices':[{'message':{'content':'{"hypothesis":"x","changes":[]}'}}]}).encode()
        def __enter__(self):return self
        def __exit__(self,*a):pass
    captured=[]
    def opener(req,timeout):
        captured.append(req)
        return Response()
    client=LLMClient(LLMConfig('https://api.example.com/v1/chat/completions','model','token',('api.example.com',)),opener=opener)
    result=client.complete_json('system','user')
    assert result['hypothesis']=='x'
    body=json.loads(captured[0].data)
    assert set(body)=={'model','temperature','messages'}
    assert 'tools' not in body


def test_model_cannot_write_anything_outside_review_proposal(tmp_path):
    (tmp_path/'research').mkdir()
    source=tmp_path/'research/solver.py';source.write_text('def solve(task):return None\n')
    class LLM:
        def complete_json(self,system,user):
            return {'hypothesis':'Change only solver','changes':[{'path':'research/solver.py','content':'def solve(task): return 2\n'}]}
    proposal=ProposalGenerator(LLM()).propose(tmp_path,'f'*40,[])
    assert source.read_text()=='def solve(task):return None\n'
    assert proposal.candidate.patch_digest


def test_workflow_has_no_automated_merge_or_write_permission():
    root=Path(__file__).resolve().parents[1]
    flow=(root/'.github/workflows/rsi-research-cycle.yml').read_text()
    assert 'cron:' in flow
    assert 'contents: read' in flow
    assert 'contents: write' not in flow
    assert 'pull-requests: write' not in flow
    assert 'RSI_CYCLE_ENABLED' in flow
    assert 'actions/upload-artifact@v4' in flow