"""Bounded DGM-style RSI cycle: research -> generate -> isolate -> rank -> REVIEW ONLY.

No GitHub write token, no patch application, no approval private key, no deploy.
"""
from __future__ import annotations
from dataclasses import asdict
import difflib
import hashlib
import json
from pathlib import Path
from .generator import ProposalGenerator, ProposalError, score_population
from .sandbox import SandboxError, make_math_cases, static_security_check


class ResearchCycle:
    def __init__(self, research, llm, sandbox, *, max_candidates: int = 2):
        if not 1 <= max_candidates <= 4:
            raise ValueError('Cycle budget must be 1..4 candidates')
        self.research = research
        self.llm = llm
        self.sandbox = sandbox
        self.max_candidates = max_candidates

    def run(self, root: Path, base_commit: str, output: Path, *, mathematical_context: list[dict] | None = None) -> dict:
        root, output = Path(root), Path(output)
        if output.resolve().is_relative_to(root.resolve()):
            # Only generated review files may be written under root; never alter source.
            if output.resolve() == root.resolve() / 'research':
                raise ValueError('Output may not overwrite research source')
        output.mkdir(parents=True, exist_ok=True)
        papers, errors = list((mathematical_context or [])[:8]), []
        for query in ('Lean 4 automated theorem proving proof search',
                      'Darwinian Godel machine recursive self improvement empirical evaluation'):
            try:
                papers.extend(self.research.search(query)[:5])
            except Exception as exc:
                errors.append({'source':'OpenAlex', 'reason':type(exc).__name__})
        # The proposer never sees the regression or held-out test cases.
        regression = make_math_cases(seed=13, count=30)
        heldout = make_math_cases(seed=1949, count=45)
        source_path = root / 'research' / 'solver.py'
        base_content = source_path.read_text(encoding='utf-8') if source_path.exists() else ''
        generator = ProposalGenerator(self.llm)
        feedback, evaluated, proposals = [], [], {}
        for _ in range(self.max_candidates):
            try:
                proposal = generator.propose(root, base_commit, papers, feedback)
                ident = proposal.candidate.candidate_id
                if ident in proposals:
                    feedback.append({'status':'DUPLICATE_PROPOSAL'})
                    continue
                content = proposal.changes['research/solver.py']
                static = static_security_check(content)
                if not static['pass']:
                    evaluated.append({'id':ident, 'status':'STATIC_REJECTED', 'reason':static['reason']})
                    feedback.append({'status':'STATIC_REJECTED','reason':static['reason']})
                    continue
                regression_result = self.sandbox.evaluate(content, regression, timeout=90)
                heldout_result = self.sandbox.evaluate(content, heldout, timeout=90)
                regression_score = regression_result['passed']/regression_result['total']
                heldout_score = heldout_result['passed']/heldout_result['total']
                novelty = 1 - difflib.SequenceMatcher(a=base_content, b=content, autojunk=False).ratio()
                record = {'id':ident, 'status':'EVALUATED_UNATTESTED',
                          'regression':regression_score, 'heldout':heldout_score,
                          'novelty':round(novelty,5), 'regression_counts':regression_result,
                          'heldout_counts':heldout_result}
                evaluated.append(record)
                proposals[ident] = proposal
                feedback.append({'status':'EVALUATED_UNATTESTED','regression':regression_score,
                                 'novelty':round(novelty,5)})
            except (ProposalError, SandboxError, ValueError) as exc:
                evaluated.append({'status':'REJECTED','reason':type(exc).__name__,'detail':str(exc)[:200]})
                feedback.append({'status':'REJECTED','reason':type(exc).__name__})
        selected = next((x for x in score_population([x for x in evaluated if x.get('status')=='EVALUATED_UNATTESTED' and x['regression']>=0.9 and x['heldout']>=0.9])
                         if x['id'] in proposals), None)
        if selected:
            winner = proposals[selected['id']]
            proposal_json = {'candidate':asdict(winner.candidate), 'base_commit':winner.base_commit,
                             'baseline_sha256':winner.baseline_sha256,
                             'patch':winner.patch, 'state':'PROPOSED_NOT_APPROVED'}
            changes_json = dict(winner.changes)
            state = 'AWAITING_HUMAN_REVIEW'
        else:
            proposal_json = {}
            changes_json = {}
            state = 'NO_ADMISSIBLE_CANDIDATE'
        files = {'research.json':{'sources':papers,'retrieval_errors':errors,
                                  'mode':'PUBLIC_METADATA_NOT_CHATGPT_DEEP_RESEARCH'},
                 'evaluation.json':{'candidates':evaluated,'selected':selected,
                                    'evidence':'UNSIGNED_LOCAL_EVALUATION_NOT_INDEPENDENT_ATTESTATION'},
                 'proposal.json':proposal_json, 'changes.json':changes_json,
                 'cycle_status.json':{'state':state,'candidates_tested':len(evaluated),
                                      'selected_candidate':selected['id'] if selected else None,
                                      'no_automatic_apply':True,'no_automatic_merge':True}}
        hashes={}
        for name, data in files.items():
            raw=json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2).encode('utf-8')+b'\n'
            (output/name).write_bytes(raw)
            hashes[name]=hashlib.sha256(raw).hexdigest()
        (output/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        return files['cycle_status.json']