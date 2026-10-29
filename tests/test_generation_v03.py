"""RED: deterministic, review-only RSI candidate generation and evidence provenance."""
import hashlib
import json
from pathlib import Path
import pytest
from imandrax_dgm.generator import ProposalGenerator, ProposalError, score_population
from imandrax_dgm.research_engine import OpenAlexResearch, ResearchError, LLMClient, LLMConfig


class FakeLLM:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.prompts = []
    def complete_json(self, system, user):
        self.prompts.append((system, user))
        return next(self.outputs)


def base(tmp_path):
    p = tmp_path / 'research' / 'solver.py'
    p.parent.mkdir()
    p.write_text('def solve(task):\n    return None\n')
    return p


def test_generator_creates_real_content_and_hash_bound_candidate(tmp_path):
    p = base(tmp_path)
    content = 'def solve(task):\n    return task["a"] + task["b"]\n'
    llm = FakeLLM([{'hypothesis':'Use integer addition','changes':[{'path':'research/solver.py','content':content}]}])
    proposal = ProposalGenerator(llm).propose(tmp_path, 'a'*40, research=[{'title':'A', 'url':'https://doi.org/10.1/example'}])
    assert proposal.candidate.paths == ('research/solver.py',)
    assert proposal.changes['research/solver.py'] == content
    assert proposal.candidate.patch_digest == hashlib.sha256(proposal.patch.encode()).hexdigest()
    assert proposal.candidate.parent_digest != 'a'*64
    assert proposal.base_commit == 'a'*40
    assert '--- a/research/solver.py' in proposal.patch
    assert 'https://doi.org/10.1/example' in llm.prompts[0][1]
    assert proposal.candidate.candidate_id.startswith('rsi-')
    assert p.read_text() != content  # no mutation before owner approval


@pytest.mark.parametrize('path', ['.github/workflows/pwn.yml','security/policy.py','research/../tests/test.py','/etc/passwd','research\\evil.py','tests/test.py'])
def test_generator_rejects_protected_paths(tmp_path, path):
    base(tmp_path)
    llm = FakeLLM([{'hypothesis':'bad','changes':[{'path':path,'content':'pass\n'}]}])
    with pytest.raises(ProposalError):
        ProposalGenerator(llm).propose(tmp_path, 'b'*40, research=[])


def test_generator_rejects_symlink_and_malformed_llm(tmp_path):
    base(tmp_path)
    (tmp_path/'research'/'link.py').symlink_to('/etc/passwd')
    with pytest.raises(ProposalError):
        ProposalGenerator(FakeLLM([{'hypothesis':'link','changes':[{'path':'research/link.py','content':'x=1'}]}])).propose(tmp_path,'a'*40,[])
    with pytest.raises(ProposalError):
        ProposalGenerator(FakeLLM([{'hypothesis':'missing','changes':[]}])).propose(tmp_path,'a'*40,[])


def test_generation_rejects_extra_fields_and_budget(tmp_path):
    base(tmp_path)
    with pytest.raises(ProposalError):
        ProposalGenerator(FakeLLM([{'hypothesis':'x','changes':[{'path':'research/solver.py','content':'x=1','secret':'a'}]}])).propose(tmp_path,'a'*40,[])
    with pytest.raises(ProposalError):
        ProposalGenerator(FakeLLM([{'hypothesis':'x','changes':[{'path':'research/solver.py','content':'x'*200001}]}])).propose(tmp_path,'a'*40,[])


def test_population_selection_uses_heldout_and_diversity():
    reports=[{'id':'a','regression':0.9,'heldout':0.1,'novelty':0.1}, {'id':'b','regression':0.7,'heldout':0.9,'novelty':0.3}]
    assert score_population(reports)[0]['id']=='b'
    assert reports[0].get('fitness') is None


def test_openalex_fetch_rejects_redirect_and_bad_provenance():
    class FakeResponse:
        status=200
        headers={'Content-Type':'application/json'}
        def read(self,n):
            return json.dumps({'results':[{'id':'https://openalex.org/W123','title':'Verified theorem','publication_year':2025,'doi':'https://doi.org/10.1000/abc'}, {'id':'http://evil.com/x','title':'bad'}]}).encode()
        def __enter__(self):return self
        def __exit__(self,*a):pass
    captured=[]
    def opener(req, timeout):
        captured.append(req.full_url)
        return FakeResponse()
    hits=OpenAlexResearch(opener=opener).search('formal theorem')
    assert len(hits)==1
    assert hits[0]['url']=='https://openalex.org/W123'
    assert captured[0].startswith('https://api.openalex.org/works?')
    assert 'formal+theorem' in captured[0]


def test_llm_network_requires_https_explicit_allowlist_and_secret():
    with pytest.raises(ResearchError):
        LLMConfig(endpoint='http://localhost/v1/chat/completions',model='x',api_key='x',allowed_hosts=('localhost',)).validate()
    with pytest.raises(ResearchError):
        LLMConfig(endpoint='https://169.254.169.254/x',model='x',api_key='x',allowed_hosts=('169.254.169.254',)).validate()
    with pytest.raises(ResearchError):
        LLMConfig(endpoint='https://api.example.com/v1/chat/completions',model='x',api_key='',allowed_hosts=('api.example.com',)).validate()
    assert LLMConfig(endpoint='https://api.example.com/v1/chat/completions',model='x',api_key='key',allowed_hosts=('api.example.com',)).validate()