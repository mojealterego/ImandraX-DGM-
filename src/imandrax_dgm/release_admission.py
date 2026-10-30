"""Offline verification of external independent evidence for a release candidate.

The runtime never creates signatures, approves its own code or deploys.
A signature proves *authorship*, not that the signer actually performed a
multi-host disaster recovery drill, WORM retention, HSM signing, etc.
"""
from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import json
import re
from typing import Mapping

REQUIRED_ROLES = frozenset((
    "RULESET", "AUTHORITY", "HSM_KMS", "WORM",
    "MULTI_HOST_DR", "INDEPENDENT_TESTS", "OWNER",
))
_DOMAIN = b"OMEGA_RELEASE_INDEPENDENT_ATTESTATIONS_V1\0"
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_SIG = re.compile(r"[0-9a-fA-F]{128}\Z")


class ReleaseAdmissionError(ValueError):
    """Fail-closed independent release admission contract."""


def _canonical(payload: object) -> bytes:
    try:
        result = json.dumps(payload,sort_keys=True,separators=(",", ":"),
                            allow_nan=False,ensure_ascii=False).encode()
    except (TypeError,ValueError,OverflowError,RecursionError) as exc:
        raise ReleaseAdmissionError("NON_CANONICAL_GATE_PAYLOAD") from exc
    if len(result)>4096:
        raise ReleaseAdmissionError("OVERSIZED_GATE_PAYLOAD")
    return result


def signature_message(payload: dict) -> bytes:
    if not isinstance(payload,dict) or set(payload)!={
        "kind","role","source_sha","artifact_sha256","expires_at","result"
    }:
        raise ReleaseAdmissionError("INVALID_GATE_PAYLOAD")
    if payload["kind"]!="OMEGA_INDEPENDENT_GATE_V1":
        raise ReleaseAdmissionError("WRONG_DOMAIN")
    if payload["role"] not in REQUIRED_ROLES:
        raise ReleaseAdmissionError("UNKNOWN_GATE_ROLE")
    if not isinstance(payload["source_sha"],str) or not _HEX40.fullmatch(payload["source_sha"]):
        raise ReleaseAdmissionError("INVALID_SOURCE_DIGEST")
    if not isinstance(payload["artifact_sha256"],str) or not _HEX64.fullmatch(payload["artifact_sha256"]):
        raise ReleaseAdmissionError("INVALID_ARTIFACT_DIGEST")
    if type(payload["expires_at"]) is not int or payload["expires_at"]<1:
        raise ReleaseAdmissionError("INVALID_EXPIRY")
    if payload["result"]!="PASS":
        raise ReleaseAdmissionError("GATE_NOT_PASSED")
    return _DOMAIN+_canonical(payload)


def evaluate_release(*,source_sha:str,artifact_sha256:str,
                     trusted_keys:Mapping[str,bytes],
                     receipts:Mapping[str,dict],now:int) -> dict:
    """All roles separately signed, but result NEVER authorizes deployment."""
    if (not isinstance(source_sha,str) or not _HEX40.fullmatch(source_sha)
            or not isinstance(artifact_sha256,str) or not _HEX64.fullmatch(artifact_sha256)):
        raise ReleaseAdmissionError("INVALID_RELEASE_DIGESTS")
    if type(now) is not int or not 1<=now<=2**53:
        raise ReleaseAdmissionError("INVALID_NOW")
    if not isinstance(trusted_keys,dict) or not isinstance(receipts,dict):
        raise ReleaseAdmissionError("INVALID_TRUST_MAP")
    if set(trusted_keys)!=REQUIRED_ROLES:
        raise ReleaseAdmissionError("INCOMPLETE_TRUST_ROOTS")
    if any(not isinstance(v,bytes) or len(v)!=32 for v in trusted_keys.values()):
        raise ReleaseAdmissionError("INVALID_PUBLIC_KEY")
    if len(set(trusted_keys.values()))!=len(REQUIRED_ROLES):
        raise ReleaseAdmissionError("NON_INDEPENDENT_SIGNER_KEYS")
    if not set(receipts).issubset(REQUIRED_ROLES):
        raise ReleaseAdmissionError("UNKNOWN_ATTESTATION")
    verified=[]
    for role,receipt in receipts.items():
        if not isinstance(receipt,dict) or set(receipt)!={"payload","signature_hex"}:
            raise ReleaseAdmissionError("INVALID_RECEIPT")
        payload=receipt["payload"]
        msg=signature_message(payload)
        if (payload["role"]!=role or payload["source_sha"]!=source_sha
                or payload["artifact_sha256"]!=artifact_sha256):
            raise ReleaseAdmissionError("UNBOUND_ATTESTATION")
        if payload["expires_at"]<=now or payload["expires_at"]>now+86400:
            raise ReleaseAdmissionError("EXPIRED_OR_FUTURE_ATTESTATION")
        signature=receipt["signature_hex"]
        if not isinstance(signature,str) or not _SIG.fullmatch(signature):
            raise ReleaseAdmissionError("INVALID_SIGNATURE")
        try:
            Ed25519PublicKey.from_public_bytes(trusted_keys[role]).verify(
                bytes.fromhex(signature),msg)
        except (InvalidSignature,ValueError,TypeError) as exc:
            raise ReleaseAdmissionError("INVALID_SIGNATURE") from exc
        verified.append(role)
    missing=sorted(REQUIRED_ROLES-set(verified))
    return {
        "status":("BLOCKED_MISSING_INDEPENDENT_EVIDENCE" if missing else
                  "READY_FOR_EXTERNAL_OPERATOR_REVIEW_NOT_DEPLOYED"),
        "source_sha":source_sha,"artifact_sha256":artifact_sha256,
        "missing_roles":missing,"verified_roles":sorted(verified),
        "release_authorized":False,
        "limits":"SIGNATURE_AUTHENTICITY_NOT_REAL_WORLD_ATTESTATION",
    }
