"""Execute one bounded research/proposal/evaluation cycle; never write GitHub."""
import argparse
import json
import os
from pathlib import Path
import sys
from .cycle import ResearchCycle
from .research_engine import LLMClient, LLMConfig, OpenAlexResearch, ResearchError
from .sandbox import DockerSandbox, SandboxError


def main():
    p=argparse.ArgumentParser(description='ImandraX DGM RSI: propose + isolated test, no auto-approval')
    p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--base-commit',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-candidates',type=int,default=2)
    args=p.parse_args()
    try:
        config=LLMConfig(endpoint=os.environ.get('RSI_LLM_ENDPOINT',''),
                         model=os.environ.get('RSI_LLM_MODEL',''),
                         api_key=os.environ.get('RSI_LLM_API_KEY',''),
                         allowed_hosts=tuple(h.strip().lower() for h in os.environ.get('RSI_LLM_ALLOWED_HOSTS','').split(',') if h.strip()))
        client=LLMClient(config)
        image=os.environ.get('RSI_SANDBOX_IMAGE','')
        sandbox=DockerSandbox(image=image,
                              worker=Path(__file__).with_name('sandbox_worker.py'),
                              allow_unpinned_for_ci=os.environ.get('RSI_CI_ALLOW_UNPINNED_IMAGE')=='true')
        result=ResearchCycle(OpenAlexResearch(),client,sandbox,max_candidates=args.max_candidates).run(
            args.root,args.base_commit,args.output)
    except (ResearchError,SandboxError,ValueError) as exc:
        print(json.dumps({'state':'CONFIGURATION_OR_RUNTIME_FAILURE','reason':type(exc).__name__,
                          'message':str(exc)[:240]}))
        return 2
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['state']=='AWAITING_HUMAN_REVIEW' else 3


if __name__=='__main__':
    sys.exit(main())