"""Scheduled public scholarly metadata watch, with no LLM, code mutation or secrets."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from imandrax_dgm.research_engine import OpenAlexResearch
from imandrax_dgm.gates import canonical_payload

QUERIES = (
    'Lean 4 formal proof verification mathlib',
    'Darwinian Godel machine recursive self improvement',
    'numerical verified computing interval arithmetic',
    'MuJoCo control model predictive optimization',
)


def write_report(research, output: Path, *, queries=QUERIES) -> dict:
    if not 1 <= len(queries) <= 8:
        raise ValueError('Invalid research query budget')
    hits, errors = [], []
    for query in queries:
        try:
            for item in research.search(query,per_page=5):
                hits.append({'query':query, **item})
        except Exception as exc:
            errors.append({'query':query,'error':type(exc).__name__})
    digest=hashlib.sha256(canonical_payload({'queries':list(queries),'results':hits,'errors':errors})).hexdigest()
    report={'mode':'READ_ONLY_PUBLIC_METADATA','source_digest_sha256':digest,
            'queries':list(queries),'results':hits,'errors':errors,
            'limitations':'No full-text reading, formal proof, generated code, or ChatGPT Deep Research'}
    output=Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError('Refuse to overwrite previous research evidence')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    report=write_report(OpenAlexResearch(),args.output)
    print(json.dumps({'results':len(report['results']),'errors':len(report['errors']),
                      'digest':report['source_digest_sha256']}))


if __name__=='__main__':
    main()