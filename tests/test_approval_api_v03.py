"""RED: external authority is fail-closed and cannot approve via bearer alone."""
import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import pytest
from imandrax_dgm.approval_api import build_server, serve_tls
from imandrax_dgm.rsi import RSIReviewStore
from imandrax_dgm.gates import Candidate

TOKENS={'proposer':'p'*40,'runner':'r'*40,'reviewer':'h'*40}


def send(url, method='GET', token='', data=None):
    headers={'Authorization':f'Bearer {token}'}
    if data is not None: headers['Content-Type']='application/json'
    req=Request(url,method=method,headers=headers,data=json.dumps(data).encode() if data is not None else None)
    try:
        with urlopen(req,timeout=2) as response:
            return response.status,json.loads(response.read())
    except HTTPError as e:
        return e.code,json.loads(e.read())


def test_server_requires_distinct_strong_tokens(tmp_path):
    db=RSIReviewStore(tmp_path/'review.db')
    with pytest.raises(ValueError):
        build_server(('127.0.0.1',0),db,{'proposer':'x','runner':'x','reviewer':'x'})
    with pytest.raises(ValueError):
        serve_tls(('127.0.0.1',0),db,TOKENS,certfile='',keyfile='')


def test_proposal_and_unsigned_decision_are_rejected(tmp_path):
    db=RSIReviewStore(tmp_path/'review.db')
    server=build_server(('127.0.0.1',0),db,TOKENS)
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        assert send(base+'/healthz')[0]==200
        candidate=Candidate('x1','a'*64,'b'*64,('research/solver.py',),'Optimize mathematical solver',100,30)
        payload=dict(candidate.__dict__);payload['paths']=list(candidate.paths)
        assert send(base+'/v1/proposals','POST',token='wrong',data=payload)[0]==401
        assert send(base+'/v1/proposals','POST',token=TOKENS['proposer'],data=payload)[0]==201
        assert send(base+'/v1/proposals/x1',token=TOKENS['proposer'])[0]==401
        assert send(base+'/v1/proposals/x1',token=TOKENS['reviewer'])[1]['state']=='PROPOSED'
        packet=send(base+'/v1/proposals/x1/packet',token=TOKENS['reviewer'])[1]
        decision={'payload':{**packet,'decision':'APPROVE','reviewer_id':'user-01','expires_at':9999999999},
                  'signer_id':'user-01','signature_hex':'00'}
        assert send(base+'/v1/decisions','POST',token=TOKENS['reviewer'],data=decision)[0]==403
        assert db.status('x1')['state']=='PROPOSED'
        assert send(base+'/v1/decisions','POST',token=TOKENS['proposer'],data=decision)[0]==401
    finally:
        server.shutdown();server.server_close();t.join(timeout=2)