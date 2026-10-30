"""One CLI for mathematical retrieval, exact computation, and bounded RSI research.

No CLI operation approves, merges, applies patches or deploys candidates.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
from .catalog import RepoCatalog
from .knowledge import KnowledgeIndex

ROOT = Path(__file__).resolve().parents[2]


def _engine(root: Path, knowledge_db: Path, state_dir: Path):
    from .engine import IntegratedEngine
    return IntegratedEngine(knowledge_db=knowledge_db,
                            inventory=root/'data/repositories_public_701.tsv',
                            ledger_db=state_dir/'ledger.sqlite3',
                            review_db=state_dir/'review.sqlite3',
                            archive_db=state_dir/'archive.sqlite3')


def main(argv=None):
    p = argparse.ArgumentParser(prog='imandrax-dgm',description='Unified mathematical knowledge, DGM evolution and human-gated RSI')
    p.add_argument('--root',type=Path,default=ROOT)
    sub = p.add_subparsers(dest='command',required=True)
    sub.add_parser('inventory')
    portfolio = sub.add_parser('portfolio', help='Read-only portfolio evidence and integration gates')
    portfolio.add_argument('--limit', type=int, default=20)
    portfolio.add_argument('--evidence', type=Path)
    cognitive = sub.add_parser('cognitive', help='Local bitemporal memory and advisory cognition')
    cognitive.add_argument('--state-dir', type=Path, required=True)
    cognitive.add_argument('--op', required=True, choices=(
        'remember', 'recall', 'graph', 'checkpoint', 'recover',
        'decision', 'reflect', 'summarize', 'thoughts', 'route', 'genotype'))
    cognitive.add_argument('--payload-file', type=Path, required=True)
    search = sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--knowledge-db',type=Path)
    search.add_argument('--limit',type=int,default=10)
    search.add_argument('--source',default=None)
    math = sub.add_parser('math')
    math.add_argument('--knowledge-db',type=Path,required=True)
    math.add_argument('--state-dir',type=Path)
    math.add_argument('--kind',required=True,choices=['LOOKUP','EXACT_COMPUTE','FORMAL_THEOREM','FORMAL_PROOF_STATUS'])
    math.add_argument('--source')
    math.add_argument('--code')
    math.add_argument('--statement',default='')
    math.add_argument('--operation')
    math.add_argument('--arguments',default='{}')
    evo = sub.add_parser('evolve')
    evo.add_argument('--knowledge-db',type=Path,required=True)
    evo.add_argument('--state-dir',type=Path,required=True)
    evo.add_argument('--campaign-id',required=True)
    evo.add_argument('--source',required=True)
    evo.add_argument('--code',required=True)
    evo.add_argument('--base-commit',required=True)
    evo.add_argument('--output',type=Path,required=True)
    evo.add_argument('--max-candidates',type=int,default=2)
    args = p.parse_args(argv)
    root = args.root.resolve()
    if args.command == 'inventory':
        c = RepoCatalog.from_tsv(root/'data/repositories_public_701.tsv')
        out = {'total':len(c.repos),'priority':dict(Counter(r['priority'] for r in c.triage())),
               'evidence_tier':dict(Counter(r['evidence_tier'] for r in c.triage()))}
    elif args.command == 'portfolio':
        from .portfolio import PortfolioAudit, PortfolioEvidenceError
        try:
            out = PortfolioAudit.from_paths(
                root / 'data' / 'repositories_public_701.tsv',
                args.evidence or root / 'data' / 'portfolio_root_evidence_v1.json',
            ).report(limit=args.limit)
        except (PortfolioEvidenceError, ValueError, OSError) as exc:
            p.error(f'Portfolio audit rejected: {exc}')
    elif args.command == 'cognitive':
        from .cognitive_cli import execute, load_payload
        from .cognitive_memory import MemoryError
        try:
            out = execute(args.op, load_payload(args.payload_file),
                          root=root, state_dir=args.state_dir)
        except (MemoryError, ValueError, TypeError, KeyError, OSError) as exc:
            p.error('Cognitive operation rejected: ' + type(exc).__name__ +
                    (': ' + str(exc) if isinstance(exc, MemoryError) else ''))
    elif args.command == 'search':
        db = args.knowledge_db or root/'data/IMANDRAX_MATH_KNOWLEDGE_FTS.sqlite3'
        out = KnowledgeIndex(db).search(args.query,args.limit,args.source)
    elif args.command == 'math':
        from .engine import MathTask
        try:
            arguments = json.loads(args.arguments)
        except json.JSONDecodeError as exc:
            p.error(f'--arguments must be JSON: {exc}')
        state_dir = args.state_dir or root/'.imandrax-state'
        out = _engine(root,args.knowledge_db,state_dir).math(
            MathTask(kind=args.kind,source=args.source,code=args.code,statement=args.statement,
                     operation=args.operation,arguments=arguments))
    else:
        from .cycle import ResearchCycle
        from .research_engine import LLMClient, LLMConfig, OpenAlexResearch
        from .sandbox import DockerSandbox
        config = LLMConfig(endpoint=os.environ.get('RSI_LLM_ENDPOINT',''),
                           model=os.environ.get('RSI_LLM_MODEL',''),
                           api_key=os.environ.get('RSI_LLM_API_KEY',''),
                           allowed_hosts=tuple(x.strip().lower() for x in os.environ.get('RSI_LLM_ALLOWED_HOSTS','').split(',') if x.strip()))
        client = LLMClient(config)
        sandbox = DockerSandbox(image=os.environ.get('RSI_SANDBOX_IMAGE',''),
            worker=Path(__file__).with_name('sandbox_worker.py'),
            allow_unpinned_for_ci=os.environ.get('RSI_CI_ALLOW_UNPINNED_IMAGE')=='true')
        cycle = ResearchCycle(OpenAlexResearch(),client,sandbox,max_candidates=args.max_candidates)
        out = _engine(root,args.knowledge_db,args.state_dir).evolve(
            campaign_id=args.campaign_id,root=root,base_commit=args.base_commit,
            output=args.output,source_refs=[(args.source,args.code)],cycle=cycle)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
