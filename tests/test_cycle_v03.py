"""RED: autonomous bounded loop must never publish, approve, or deploy changes."""
import json
from pathlib import Path
from imandrax_dgm.cycle import ResearchCycle

class FakeResearch:
    def search(self, query):return [{'title':'Paper','url':'https://openalex.org/W1','year':2025}]
class FakeLLM:
    def __init__(self):self.n=0
    def complete_json(self,system,user):
        self.n+=1
        return {'hypothesis':'Improve math reasoning', 'changes':[{'path':'research/solver.py','content':f'def solve(task):\n    return {self.n}\n'}]}
class FakeSandbox:
    def __init__(self):self.calls=0
    def evaluate(self,content,cases,timeout=60):
        self.calls+=1
        return {'passed':len(cases) if 'return 2' in content else 0,'total':len(cases),'duration_ms':10}


def test_cycle_generates_multiple_candidates_executes_and_writes_review_artifacts(tmp_path):
    (tmp_path/'research').mkdir()
    (tmp_path/'research/solver.py').write_text('def solve(task):\n    return None\n')
    output=tmp_path/'out'
    runner=FakeSandbox()
    result=ResearchCycle(FakeResearch(),FakeLLM(),runner,max_candidates=2).run(tmp_path,'f'*40,output)
    assert result['state']=='AWAITING_HUMAN_REVIEW'
    assert result['candidates_tested']==2
    assert runner.calls==4 # regression and heldout per candidate
    assert result['selected_candidate']
    assert (output/'proposal.json').exists()
    assert (output/'research.json').exists()
    assert (output/'evaluation.json').exists()
    assert (output/'changes.json').exists()
    assert (output/'SHA256SUMS.json').exists()
    assert (tmp_path/'research/solver.py').read_text()=='def solve(task):\n    return None\n'
    assert 'approved' not in json.dumps(result).lower()


def test_math_context_reaches_proposer_but_hidden_test_scores_do_not(tmp_path):
    (tmp_path/'research').mkdir()
    (tmp_path/'research/solver.py').write_text('def solve(task):\n    return None\n')
    class RecordingLLM(FakeLLM):
        def __init__(self):
            super().__init__()
            self.prompts=[]
        def complete_json(self,system,user):
            self.prompts.append(json.loads(user))
            return super().complete_json(system,user)
    llm=RecordingLLM()
    ResearchCycle(FakeResearch(),llm,FakeSandbox(),max_candidates=2).run(
        tmp_path,'f'*40,tmp_path/'out',mathematical_context=[{'provider':'IMANDRAX_INDEX','code':'00A05','title':'Algebra'}])
    assert any(x.get('code')=='00A05' for x in llm.prompts[0]['scholarly_metadata_untrusted'])
    assert all('heldout' not in json.dumps(x['prior_evaluation_feedback']) for x in llm.prompts)