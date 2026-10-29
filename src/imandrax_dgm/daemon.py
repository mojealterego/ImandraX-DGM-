"""Optional continuous RSI research worker; never an unattended release agent.

This process may call a networked proposer and a separate networkless Docker
runner, but may only write research artifacts and local research SQLite state.
A dedicated host and owner-supplied credentials are required for real operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
from typing import Callable

from .cycle import ResearchCycle
from .engine import IntegratedEngine
from .research_engine import LLMClient, LLMConfig, OpenAlexResearch
from .sandbox import DockerSandbox


def run_loop(*, engine, cycle, root: Path, base_commit: str, output_root: Path,
             source_refs: list[tuple[str,str]], max_cycles: int = 0,
             interval_seconds: int = 21600, sleep: Callable[[float],None] = time.sleep,
             should_stop: Callable[[],bool] = lambda: False,
             expected_source_sha256: str | None = None) -> dict:
    """Run repeated bounded *proposal* cycles; never approve, apply or merge.

    max_cycles=0 means unbounded lifetime, not an unbounded single cycle.
    Three consecutive failures halt the loop instead of silently retrying forever.
    """
    if not isinstance(base_commit,str) or not re.fullmatch(r'[0-9a-f]{40}',base_commit):
        raise ValueError('Pinned 40-character base commit required')
    if type(max_cycles) is not int or not 0 <= max_cycles <= 100000:
        raise ValueError('Invalid max cycles')
    if type(interval_seconds) is not int or not 300 <= interval_seconds <= 86400:
        raise ValueError('Interval must be between 300 and 86400 seconds')
    if not isinstance(source_refs,list) or not 1 <= len(source_refs) <= 12:
        raise ValueError('Mathematical source references required')
    root=Path(root).resolve()
    if expected_source_sha256 is not None and not re.fullmatch(r'[0-9a-f]{64}',expected_source_sha256):
        raise ValueError('Invalid pinned solver source digest')
    output_root=Path(output_root)
    if output_root.is_symlink():
        raise ValueError('Output directory must not be a symlink')
    output_root=output_root.resolve()
    if output_root==root or (output_root.is_relative_to(root) and
            output_root.relative_to(root).parts[0] in
            {'research','src','tests','proofs','docs','data','.github'}):
        raise ValueError('Research output must not overlap source or policy paths')
    output_root.mkdir(parents=True,exist_ok=True)
    successes=0
    failures=0
    cycles=0
    consecutive=0
    while (max_cycles==0 or cycles<max_cycles) and not should_stop():
        if expected_source_sha256 is not None:
            source=root/'research'/'solver.py'
            if (source.is_symlink() or not source.is_file() or
                    hashlib.sha256(source.read_bytes()).hexdigest()!=expected_source_sha256):
                raise RuntimeError('Pinned solver source drift; stop research until operator review')
        campaign='rsi-research-'+uuid.uuid4().hex
        output=output_root/campaign
        output.mkdir(mode=0o700)
        try:
            result=engine.evolve(campaign_id=campaign,root=root,base_commit=base_commit,
                                 output=output,source_refs=source_refs,cycle=cycle)
            if result.get('state')=='PROPOSED_AWAITING_USER':
                successes+=1
            consecutive=0
            report={'state':result.get('state','UNKNOWN'),
                    'approval':'HUMAN_SIGNATURE_REQUIRED',
                    'source_changes_applied':False,'production_deployed':False}
        except Exception as exc:
            failures+=1
            consecutive+=1
            report={'state':'CYCLE_FAILED','error_type':type(exc).__name__,
                    'approval':'NOT_REQUESTED','source_changes_applied':False,
                    'production_deployed':False}
        (output/'cycle_result.json').write_text(json.dumps(report,sort_keys=True)+'\n',encoding='utf-8')
        cycles+=1
        if consecutive>=3:
            raise RuntimeError('Three consecutive RSI research failures; operator intervention required')
        if (max_cycles==0 or cycles<max_cycles) and not should_stop():
            sleep(interval_seconds)
    return {'cycles':cycles,'proposals':successes,'failures':failures,
            'approval':'HUMAN_SIGNATURE_REQUIRED','auto_deploy':False}


def main(argv=None):
    p=argparse.ArgumentParser(description='Persistent research-only ImandraX/DGM/RSI worker')
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--base-commit',required=True)
    p.add_argument('--knowledge-db',type=Path,required=True)
    p.add_argument('--state-dir',type=Path,required=True)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--source',required=True)
    p.add_argument('--code',required=True)
    p.add_argument('--interval-seconds',type=int,default=21600)
    p.add_argument('--max-cycles',type=int,default=0)
    p.add_argument('--max-candidates',type=int,default=2)
    args=p.parse_args(argv)
    if os.environ.get('RSI_DAEMON_ENABLED')!='true':
        p.error('Explicit RSI_DAEMON_ENABLED=true is required')
    root=args.root.resolve()
    actual=subprocess.run(['git','-C',str(root),'rev-parse','--verify','HEAD'],
                          capture_output=True,text=True,timeout=10,check=True).stdout.strip()
    if actual != args.base_commit:
        p.error('Pinned base commit does not match checkout')
    dirty=subprocess.run(['git','-C',str(root),'status','--porcelain','--','research/solver.py'],
                         capture_output=True,text=True,timeout=10,check=True).stdout.strip()
    if dirty:
        p.error('Solver baseline is dirty; refusing unpinned research')
    config=LLMConfig(endpoint=os.environ.get('RSI_LLM_ENDPOINT',''),
                     model=os.environ.get('RSI_LLM_MODEL',''),
                     api_key=os.environ.get('RSI_LLM_API_KEY',''),
                     allowed_hosts=tuple(x.strip().lower() for x in
                         os.environ.get('RSI_LLM_ALLOWED_HOSTS','').split(',') if x.strip()))
    llm=LLMClient(config)
    sandbox=DockerSandbox(image=os.environ.get('RSI_SANDBOX_IMAGE',''),
                          worker=Path(__file__).with_name('sandbox_worker.py'))
    engine=IntegratedEngine(knowledge_db=args.knowledge_db,
        inventory=root/'data/repositories_public_701.tsv',
        ledger_db=args.state_dir/'ledger.sqlite3',review_db=args.state_dir/'review.sqlite3',
        archive_db=args.state_dir/'approved.sqlite3')
    result=run_loop(engine=engine,
        cycle=ResearchCycle(OpenAlexResearch(),llm,sandbox,max_candidates=args.max_candidates),
        root=root,base_commit=args.base_commit,output_root=args.output_root,
        source_refs=[(args.source,args.code)],max_cycles=args.max_cycles,
        interval_seconds=args.interval_seconds,
        expected_source_sha256=hashlib.sha256((root/'research'/'solver.py').read_bytes()).hexdigest())
    print(json.dumps(result,ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
