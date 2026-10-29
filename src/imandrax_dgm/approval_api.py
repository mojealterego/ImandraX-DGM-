"""Standalone TLS-only approval authority: the owner signs every decision offline.

Deploy on a separate host with a private database and trust.json; never mount the
signing key into the proposer, sandbox or GitHub Actions. This service verifies,
never creates, human Ed25519 signatures.
"""
from __future__ import annotations
from dataclasses import fields
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import ssl
from typing import Mapping
from .gates import Candidate, EvidenceAttestation
from .rsi import RSIReviewStore, ApprovalEnvelope, ApprovalRequired


class ApprovalHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False


def build_server(address: tuple[str, int], store: RSIReviewStore, tokens: Mapping[str, str]):
    roles={'proposer','runner','reviewer'}
    if set(tokens) != roles or any(not isinstance(x,str) or len(x)<32 for x in tokens.values()) or len(set(tokens.values()))!=3:
        raise ValueError('Three distinct strong role tokens are required')
    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.0'
        server_version = 'ImandraXApproval/0.3'
        sys_version = ''

        def log_message(self, fmt, *args):
            # No token, path or user payload logging in reference service.
            pass

        def _reply(self, code: int, body: dict):
            raw=json.dumps(body,ensure_ascii=False,separators=(',',':')).encode()
            self.send_response(code)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _role(self, role: str) -> bool:
            return hmac.compare_digest(self.headers.get('Authorization',''), 'Bearer '+tokens[role])

        def _json(self):
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                raise ValueError('Content type must be application/json')
            length=self.headers.get('Content-Length','')
            if not length.isdecimal() or not 0<int(length)<=65536:
                raise ValueError('Invalid request size')
            raw=self.rfile.read(int(length))
            obj=json.loads(raw)
            if not isinstance(obj,dict):
                raise ValueError('Expected JSON object')
            return obj

        def do_GET(self):
            if self.path=='/healthz':
                return self._reply(200,{'status':'up','mode':'SIGNED_OWNER_APPROVAL_ONLY'})
            m=re.fullmatch(r'/v1/proposals/([A-Za-z0-9][A-Za-z0-9_.-]{0,127})(/packet)?',self.path)
            if not m:
                return self._reply(404,{'error':'NOT_FOUND'})
            if not self._role('reviewer'):
                return self._reply(401,{'error':'UNAUTHORIZED'})
            try:
                data=store.review_packet(m.group(1)) if m.group(2) else store.details(m.group(1))
                return self._reply(200,data)
            except KeyError:
                return self._reply(404,{'error':'UNKNOWN_PROPOSAL'})
            except ApprovalRequired:
                return self._reply(403,{'error':'INVALID_PROPOSAL'})

        def do_POST(self):
            m=re.fullmatch(r'/v1/evidence/([A-Za-z0-9][A-Za-z0-9_.-]{0,127})',self.path)
            if self.path=='/v1/proposals':
                role='proposer'
            elif m:
                role='runner'
            elif self.path=='/v1/decisions':
                role='reviewer'
            else:
                return self._reply(404,{'error':'NOT_FOUND'})
            if not self._role(role):
                return self._reply(401,{'error':'UNAUTHORIZED'})
            try:
                data=self._json()
                if role=='proposer':
                    if set(data)!={f.name for f in fields(Candidate)} or not isinstance(data['paths'],list):
                        raise ValueError('Invalid candidate schema')
                    data['paths']=tuple(data['paths'])
                    result=store.submit(Candidate(**data))
                    return self._reply(201,result)
                if set(data)!={'payload','signer_id','signature_hex'}:
                    raise ValueError('Invalid signed envelope')
                if role=='runner':
                    store.record_evidence(m.group(1),EvidenceAttestation(**data))
                    return self._reply(201,{'status':'EVIDENCE_RECORDED'})
                state=store.decide(ApprovalEnvelope(**data))
                return self._reply(200,{'state':state,'human_signature_verified':True})
            except ApprovalRequired:
                return self._reply(403,{'error':'APPROVAL_OR_ATTESTATION_DENIED'})
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                return self._reply(400,{'error':'INVALID_REQUEST'})

    return ApprovalHTTPServer(address,Handler)


def serve_tls(address: tuple[str,int], store: RSIReviewStore, tokens: Mapping[str,str], *, certfile: str, keyfile: str):
    if not certfile or not keyfile or not Path(certfile).is_file() or not Path(keyfile).is_file():
        raise ValueError('TLS certificate and key are mandatory; HTTP mode is test-only')
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version=ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile,keyfile)
    server=build_server(address,store,tokens)
    server.socket=context.wrap_socket(server.socket,server_side=True)
    server.serve_forever()