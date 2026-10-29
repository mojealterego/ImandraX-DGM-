"""Deterministic 704-repository metadata triage, not a source-code audit."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
import re

ORIGINAL_16 = frozenset('''mathlib4 batteries iris-lean mathematics_in_lean mujoco optax mujoco_menagerie science-skills dm_control regress-lm representations4d Awesome-Quantum-Computing-Platform mathematics_conjectures alphageometry mathematics_dataset 3d-shapes'''.split())
EXTRA_README_ROOT = frozenset('''dgm RSIAI0 OpenAlpha_Evolve alphageometry2 agent-evaluation-lab Knowledge-projects ocaf-runtime jax tensorflow langgraph autogen codeql agent-opt agent-framework mcp-context-forge ToolNeuron physics-IQ-benchmark 500-AI-Agents-Projects deep-research-agent mcp-coding-agent Agent-God-Level-Omega OpenLLM llm-graph-builder agenticSeek github-mcp-server mcp-toolbox agent-learning-kit omega-x-neuromesh agents AgentGPT awesome-agent-skills NeuroAdapt-AI OpenCodeEnterprise'''.split())
P0_GROUPS = {
    'FORMAL_PROOF': 'mathlib4 batteries iris-lean mathematics_in_lean alphageometry alphageometry2',
    'MATHEMATICS_DATA': 'mathematics_conjectures mathematics_dataset Awesome-Quantum-Computing-Platform',
    'NUMERICAL_ML': 'jax optax regress-lm',
    'PHYSICS_CONTROL': 'mujoco mujoco_menagerie dm_control',
    'SCIENTIFIC_RESEARCH': 'science-skills',
    'EVOLUTION_RESEARCH': 'dgm',
    'INDEPENDENT_EVALUATION': 'agent-evaluation-lab codeql',
}
P1_GROUPS = {
    'EVOLUTION_RESEARCH': 'RSIAI0 OpenAlpha_Evolve agent-opt',
    'SCIENTIFIC_RESEARCH': 'representations4d 3d-shapes physics-IQ-benchmark',
    'AGENT_ORCHESTRATION': 'langgraph agent-framework mcp-coding-agent mcp-context-forge',
    'MODEL_RUNTIME': 'OpenLLM tensorflow',
    'KNOWLEDGE_GRAPH': 'Knowledge-projects llm-graph-builder',
    'GOVERNANCE': 'ocaf-runtime omega-x-neuromesh',
    'INDEPENDENT_EVALUATION': 'agent-learning-kit',
}
P2_GROUPS = {
    'AGENT_ORCHESTRATION': 'autogen github-mcp-server mcp-toolbox Agent-God-Level-Omega agents AgentGPT',
    'RESEARCH_WORKFLOWS': 'deep-research-agent awesome-agent-skills 500-AI-Agents-Projects',
    'MOBILE_RUNTIME': 'ToolNeuron',
    'EVOLUTION_RESEARCH': 'agenticSeek',
    'OTHER': 'NeuroAdapt-AI OpenCodeEnterprise',
}
GROUPS = {p:{n:(group,p) for group,names in groupmap.items() for n in names.split()} for p,groupmap in [('P0',P0_GROUPS),('P1',P1_GROUPS),('P2',P2_GROUPS)]}
PRIORITY_MAP = {name:(group,p) for p,entries in GROUPS.items() for name,(group,_) in entries.items()}
HEURISTICS = (
    ('FORMAL_PROOF',('math','lean','geometry','proof','theorem','logic','quantum')),
    ('SCIENTIFIC_RESEARCH',('science','physics','chem','biology','neuro','dataset','robot','mujoco','control')),
    ('EVOLUTION_RESEARCH',('evol','self-improv','rsi','dgm','agent-opt')),
    ('INDEPENDENT_EVALUATION',('benchmark','eval','codeql','security','testing')),
    ('AGENT_ORCHESTRATION',('agent','mcp','langgraph','coding','llm')),
)

@dataclass(frozen=True)
class Repository:
    full_name: str
    repo_id: str
    size_kb: int
    default_branch: str
    visibility: str
    archived: bool
    url: str
    @property
    def name(self):
        return self.full_name.split('/',1)[1]

class RepoCatalog:
    def __init__(self, repos):
        self.repos=tuple(repos)
        self._by_name={r.full_name.casefold():r for r in self.repos}
        if len(self._by_name)!=len(self.repos):
            raise ValueError('Duplicate repositories in source inventory')

    @classmethod
    def from_tsv(cls, path:Path):
        with Path(path).open(encoding='utf-8-sig',newline='') as f:
            return cls(Repository(r['repository_full_name'],r['repository_id'],int(r['size_kb']),r['default_branch'],r['visibility'],r['archived'].lower()=='true',r['url']) for r in csv.DictReader(f,delimiter='\t'))

    def by_name(self,name):
        return self._by_name.get(name.casefold())

    @staticmethod
    def classify(repo):
        if repo.name in PRIORITY_MAP:
            return PRIORITY_MAP[repo.name][0],PRIORITY_MAP[repo.name][1],'EXPLICIT_REVIEWED_SELECTION'
        low=repo.name.lower()
        for group,needles in HEURISTICS:
            if any((re.search(r'(?:^|[^a-z])'+re.escape(k)+r'(?:$|[^a-z])',low) if k in ('lean','logic') else k in low) for k in needles):
                return group,'P3','NAME_HEURISTIC_ONLY'
        return 'NOT_RELEVANT_BY_NAME','P4','METADATA_ONLY'

    def triage(self):
        out=[]
        for repo in self.repos:
            group,priority,basis=self.classify(repo)
            evidence='ROOT_README_LICENSE_REVIEWED_PREVIOUS' if repo.name in ORIGINAL_16 else ('ROOT_README_REVIEWED' if repo.name in EXTRA_README_ROOT else 'METADATA_ONLY')
            risk={'RSIAI0':'UNSAFE_REAL_MODE','mujoco_menagerie':'LICENSE_PER_ASSET','agenticSeek':'GPL_COMPATIBILITY','autogen':'MAINTENANCE_MODE'}.get(repo.name,'UNASSESSED')
            out.append({'repository':repo.full_name,'priority':priority,'domain':group,'selection_basis':basis,'evidence_tier':evidence,'risk_flag':risk,'size_kb':repo.size_kb,'branch':repo.default_branch,'visibility':repo.visibility,'archived':repo.archived,'url':repo.url,'integration_status':'NOT_INTEGRATED'})
        return sorted(out,key=lambda r:(r['priority'],r['domain'],r['repository'].casefold()))