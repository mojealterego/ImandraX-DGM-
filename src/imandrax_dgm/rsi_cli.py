"""Operator CLI. Human signing is external; this tool has no self-approval path."""
from __future__ import annotations
import argparse
from dataclasses import fields
import json
from pathlib import Path
import time

from .gates import Candidate, EvidenceAttestation
from .rsi import RSIReviewStore, RSIInbox, ApprovalEnvelope


def _read_json(path):
    value=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(value,dict):
        raise ValueError('Expected JSON object')
    return value


def main(argv=None):
    parser=argparse.ArgumentParser(prog='imandrax-rsi',description='RSI research proposals with mandatory human signature')
    parser.add_argument('--db',type=Path,default=Path('local-rsi-review.sqlite3'))
    parser.add_argument('--trust',type=Path,help='External trusted public keys JSON; NEVER agent-writable')
    sub=parser.add_subparsers(dest='action',required=True)
    submit=sub.add_parser('submit');submit.add_argument('--candidate',type=Path,required=True)
    tick=sub.add_parser('tick');tick.add_argument('--inbox',type=Path,required=True)
    watch=sub.add_parser('watch');watch.add_argument('--inbox',type=Path,required=True)
    watch.add_argument('--interval',type=float,default=30.0)
    watch.add_argument('--max-cycles',type=int,default=1,help='0 = indefinitely while operator keeps process running')
    evidence=sub.add_parser('evidence');evidence.add_argument('--file',type=Path,required=True);evidence.add_argument('--id',required=True)
    decide=sub.add_parser('decide');decide.add_argument('--file',type=Path,required=True)
    for action in ('packet','status','details','authorized'):
        cmd=sub.add_parser(action);cmd.add_argument('--id',required=True)
    sub.add_parser('audit')
    args=parser.parse_args(argv)
    trust=_read_json(args.trust) if args.trust else {}
    def keymap(section):
        return {str(k):bytes.fromhex(v) for k,v in trust.get(section,{}).items()}
    store=RSIReviewStore(args.db,runner_keys=keymap('runners'),reviewer_keys=keymap('reviewers'))
    if args.action=='submit':
        payload=_read_json(args.candidate)
        if set(payload)!={f.name for f in fields(Candidate)} or not isinstance(payload['paths'],list):
            raise ValueError('Invalid candidate schema')
        payload['paths']=tuple(payload['paths'])
        result=store.submit(Candidate(**payload))
    elif args.action=='tick':
        result=RSIInbox(store,args.inbox).tick()
    elif args.action=='watch':
        if args.interval<1 or args.max_cycles<0:
            raise ValueError('Invalid watch budget')
        cycles=0
        try:
            while args.max_cycles==0 or cycles<args.max_cycles:
                result=RSIInbox(store,args.inbox).tick()
                print(json.dumps(result,ensure_ascii=False),flush=True)
                cycles+=1
                if args.max_cycles==0 or cycles<args.max_cycles:
                    time.sleep(args.interval)
        except KeyboardInterrupt:
            return 130
        return 0
    elif args.action=='evidence':
        data=_read_json(args.file)
        store.record_evidence(args.id,EvidenceAttestation(**data))
        result=store.status(args.id)
    elif args.action=='decide':
        data=_read_json(args.file)
        result={'decision':store.decide(ApprovalEnvelope(**data))}
    elif args.action=='packet':
        result=store.review_packet(args.id)
    elif args.action=='status':
        result=store.status(args.id)
    elif args.action=='details':
        result=store.details(args.id)
    elif args.action=='authorized':
        result={'authorized':store.is_authorized(args.id),'meaning':'SIGNED_REVIEW_ONLY_NOT_DEPLOYED'}
    else:
        result={'audit_chain_valid':store.verify_audit()}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())