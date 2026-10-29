"""One research interface: source-grounded mathematical proposals + bounded DGM governance.

This integration does not execute arbitrary code, compile Lean, prove theorems,
run MuJoCo, or promote a candidate to production.
"""
from __future__ import annotations
from pathlib import Path
import json
from .catalog import RepoCatalog
from .knowledge import KnowledgeIndex
from .gates import Candidate, Policy, ResearchGate
from .ledger import ImmutableLedger

class UnifiedResearchEngine:
    def __init__(self,knowledge_db:Path,inventory:Path,ledger_db:Path,policy:Policy|None=None):
        self.knowledge=KnowledgeIndex(knowledge_db)
        self.catalog=RepoCatalog.from_tsv(inventory)
        self.ledger=ImmutableLedger(ledger_db)
        self.gate=ResearchGate(policy or Policy.default())

    def open_campaign(self,campaign_id:str,max_tokens:int):
        if not 0<max_tokens<=self.gate.policy.max_tokens:
            raise ValueError('Campaign budget outside policy')
        return self.ledger.append(campaign_id,'CREATED',{'max_tokens':max_tokens,'mode':'RESEARCH_ONLY'},f'{campaign_id}:create')

    def propose(self,campaign_id:str,candidate:Candidate,source_refs:list[tuple[str,str]]):
        history=self.ledger.history(campaign_id)
        if not history or history[0]['event_type']!='CREATED':
            raise ValueError('Campaign must be explicitly created')
        budget=json.loads(history[0]['payload_json'])['max_tokens']
        self.ledger.append(campaign_id,'HYPOTHESIS',{'candidate_id':candidate.candidate_id,'hypothesis':candidate.hypothesis},f'{candidate.candidate_id}:hypothesis')
        self.ledger.append(campaign_id,'PROPOSAL',{'candidate_id':candidate.candidate_id,'parent_digest':candidate.parent_digest,'patch_digest':candidate.patch_digest,'source_refs':source_refs,'paths':candidate.paths},f'{candidate.candidate_id}:proposal')
        if not source_refs or any(not self.knowledge.exact(code,source) for source,code in source_refs):
            self.ledger.append(campaign_id,'REJECTED',{'reason':'SOURCE_REFERENCE_NOT_FOUND'},f'{candidate.candidate_id}:reject')
            return {'admitted':False,'reason':'SOURCE_REFERENCE_NOT_FOUND','proof_status':'NO_PROOF_ATTEMPTED','evolution_status':'NOT_EXECUTED'}
        if candidate.max_tokens>budget:
            self.ledger.append(campaign_id,'REJECTED',{'reason':'CAMPAIGN_BUDGET_DENIED'},f'{candidate.candidate_id}:reject')
            return {'admitted':False,'reason':'CAMPAIGN_BUDGET_DENIED','proof_status':'NO_PROOF_ATTEMPTED','evolution_status':'NOT_EXECUTED'}
        decision=self.gate.admit(candidate)
        self.ledger.append(campaign_id,'POLICY_CHECK',{'candidate_id':candidate.candidate_id,'accepted':decision.accepted,'reason':decision.reason},f'{candidate.candidate_id}:policy')
        if not decision.accepted:
            self.ledger.append(campaign_id,'REJECTED',{'reason':decision.reason},f'{candidate.candidate_id}:reject')
        return {'admitted':decision.accepted,'reason':decision.reason,'proof_status':'NO_PROOF_ATTEMPTED','evolution_status':'NOT_EXECUTED'}