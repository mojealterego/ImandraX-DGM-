"""Read-only user CLI for catalog and knowledge; no autonomous mutation commands."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter
from .catalog import RepoCatalog
from .knowledge import KnowledgeIndex

ROOT=Path(__file__).resolve().parents[2]

def main(argv=None):
    p=argparse.ArgumentParser(prog='imandrax-dgm',description='Unified research knowledge/control reference')
    p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('inventory')
    search=sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--limit',type=int,default=10)
    search.add_argument('--source',default=None)
    args=p.parse_args(argv)
    if args.command=='inventory':
        c=RepoCatalog.from_tsv(args.root/'data/repositories_public_701.tsv')
        out={'total':len(c.repos),'priority':dict(Counter(r['priority'] for r in c.triage())),'evidence_tier':dict(Counter(r['evidence_tier'] for r in c.triage()))}
    else:
        out=KnowledgeIndex(args.root/'data/IMANDRAX_MATH_KNOWLEDGE_FTS.sqlite3').search(args.query,args.limit,args.source)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())