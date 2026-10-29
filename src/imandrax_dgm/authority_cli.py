"""Start external signed human-approval authority (no private signing key)."""
import argparse
import json
import os
from pathlib import Path
from .approval_api import serve_tls
from .rsi import RSIReviewStore


def _load_token(role: str) -> str:
    if role not in ('proposer','runner','reviewer'):
        raise ValueError('Invalid authority role')
    name = 'RSI_AUTH_' + role.upper() + '_TOKEN'
    env_value, file_path = os.environ.get(name,''), os.environ.get(name+'_FILE','')
    if env_value and file_path:
        raise ValueError('Specify a token or token file, never both')
    if file_path:
        path = Path(file_path)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 512:
            raise ValueError('Invalid token secret file')
        token = path.read_text(encoding='utf-8').strip('\r\n')
    else:
        token = env_value
    if not 32 <= len(token) <= 256 or any(c.isspace() for c in token):
        raise ValueError('Authority token must be a strong single-line secret')
    return token


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--trust',type=Path,required=True)
    p.add_argument('--db',type=Path,required=True)
    p.add_argument('--bind',default='127.0.0.1')
    p.add_argument('--port',type=int,default=9443)
    p.add_argument('--cert',required=True)
    p.add_argument('--key',required=True)
    a=p.parse_args()
    trust=json.loads(a.trust.read_text(encoding='utf-8'))
    runners={name:bytes.fromhex(value) for name,value in trust['runners'].items()}
    reviewers={name:bytes.fromhex(value) for name,value in trust['reviewers'].items()}
    if not runners or not reviewers:
        raise ValueError('Independent runner and reviewer public keys are mandatory')
    tokens={role:_load_token(role) for role in ('proposer','runner','reviewer')}
    store=RSIReviewStore(a.db,runner_keys=runners,reviewer_keys=reviewers)
    serve_tls((a.bind,a.port),store,tokens,certfile=a.cert,keyfile=a.key)


if __name__=='__main__':
    main()
