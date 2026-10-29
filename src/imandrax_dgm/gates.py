"""Research admission and external evidence verification. No code execution or release authority."""
from __future__ import annotations
from dataclasses import dataclass
import json
import re
from pathlib import PurePosixPath
from typing import Mapping
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

_SHA=re.compile(r'^[0-9a-f]{64}$')
_FORBIDDEN={'policy','policies','security','secrets','secret','tests','test','evaluator','evaluation','benchmark','benchmarks','signer','signing','release','releases','.git','.github','config','ci','keys','authority'}

def canonical_payload(payload:dict)->bytes:
    return json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')

@dataclass(frozen=True)
class Candidate:
    candidate_id:str
    parent_digest:str
    patch_digest:str
    paths:tuple[str,...]
    hypothesis:str
    max_tokens:int
    max_runtime_seconds:int

@dataclass(frozen=True)
class Policy:
    mutable_roots:tuple[str,...]
    max_tokens:int
    max_runtime_seconds:int
    max_files:int
    @classmethod
    def default(cls):
        return cls(('harness','adapters','research'),40000,1200,5)

@dataclass(frozen=True)
class Admission:
    accepted:bool
    reason:str
    scope:str='RESEARCH_ONLY'

@dataclass(frozen=True)
class EvidenceAttestation:
    payload:dict
    signer_id:str
    signature_hex:str

class ResearchGate:
    def __init__(self,policy:Policy,trusted_runner_keys:Mapping[str,bytes]|None=None):
        self.policy=policy
        self.trusted_runner_keys=dict(trusted_runner_keys or {})
    def admit(self,candidate:Candidate)->Admission:
        if not candidate.candidate_id or not candidate.hypothesis.strip():
            return Admission(False,'EMPTY_ID_OR_HYPOTHESIS')
        if not _SHA.fullmatch(candidate.parent_digest) or not _SHA.fullmatch(candidate.patch_digest):
            return Admission(False,'INVALID_DIGEST')
        if not 1<=len(candidate.paths)<=self.policy.max_files:
            return Admission(False,'INVALID_FILE_COUNT')
        if not 0<candidate.max_tokens<=self.policy.max_tokens or not 0<candidate.max_runtime_seconds<=self.policy.max_runtime_seconds:
            return Admission(False,'BUDGET_DENIED')
        for raw in candidate.paths:
            if not isinstance(raw,str) or not raw or '\\' in raw or '\x00' in raw or raw.startswith('/') or raw.startswith('//') or '//' in raw:
                return Admission(False,'INVALID_PATH')
            segments=raw.split('/')
            if any(s in ('','.','..') for s in segments):
                return Admission(False,'PATH_TRAVERSAL')
            if any(s.casefold() in _FORBIDDEN for s in segments):
                return Admission(False,'PROTECTED_PATH')
            if segments[0] not in self.policy.mutable_roots:
                return Admission(False,'OUT_OF_SCOPE')
            if str(PurePosixPath(raw))!=raw:
                return Admission(False,'NON_CANONICAL_PATH')
        return Admission(True,'POLICY_PASS_RESEARCH_ONLY')
    def verify_attestation(self,att:EvidenceAttestation)->bool:
        key=self.trusted_runner_keys.get(att.signer_id)
        if not key or not isinstance(att.payload,dict):
            return False
        required={'candidate_digest','suite','result','runner_id','source_digest'}
        if not required.issubset(att.payload) or att.payload['runner_id']!=att.signer_id:
            return False
        if not all(isinstance(att.payload[x],str) for x in required):
            return False
        if not _SHA.fullmatch(att.payload['candidate_digest']) or not _SHA.fullmatch(att.payload['source_digest']):
            return False
        if att.payload['result'] not in ('PASS','FAIL','TIMEOUT','INFRA_FAILURE'):
            return False
        try:
            Ed25519PublicKey.from_public_bytes(key).verify(bytes.fromhex(att.signature_hex),canonical_payload(att.payload))
        except (InvalidSignature,ValueError,TypeError):
            return False
        return True
    def evaluate_attestation(self,att:EvidenceAttestation)->str:
        return 'RESEARCH_EVIDENCE_ONLY' if self.verify_attestation(att) else 'REJECTED_UNVERIFIED_EVIDENCE'