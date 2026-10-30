"""The release decision stays externally controlled even if all signatures verify."""
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import pytest

from imandrax_dgm.release_admission import (
    ReleaseAdmissionError, REQUIRED_ROLES, signature_message, evaluate_release,
)

SHA="a"*40
ARTIFACT="b"*64
NOW=1800000000

def identity():
    private=Ed25519PrivateKey.generate()
    public=private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    return private,public

def suite():
    identities={x:identity() for x in REQUIRED_ROLES}
    trusted={x:pair[1] for x,pair in identities.items()}
    receipts={}
    for role in REQUIRED_ROLES:
        payload={"kind":"OMEGA_INDEPENDENT_GATE_V1","role":role,
                 "source_sha":SHA,"artifact_sha256":ARTIFACT,
                 "expires_at":NOW+600,"result":"PASS"}
        receipts[role]={"payload":payload,
                        "signature_hex":identities[role][0].sign(
                            signature_message(payload)).hex()}
    return trusted,receipts

def test_empty_and_partial_evidence_denies_release():
    trusted,receipts=suite()
    out=evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts={},now=NOW)
    assert out["status"]=="BLOCKED_MISSING_INDEPENDENT_EVIDENCE"
    assert out["release_authorized"] is False
    assert set(out["missing_roles"])==set(REQUIRED_ROLES)

def test_full_signatures_still_require_independent_operator():
    trusted,receipts=suite()
    out=evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)
    assert out["status"]=="READY_FOR_EXTERNAL_OPERATOR_REVIEW_NOT_DEPLOYED"
    assert out["release_authorized"] is False
    assert out["verified_roles"]==sorted(REQUIRED_ROLES)

def test_forged_role_or_artifact_is_rejected():
    trusted,receipts=suite()
    receipts["RULESET"]["payload"]["artifact_sha256"]="c"*64
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)
    trusted,receipts=suite()
    receipts["WORM"]["signature_hex"]="00"*64
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)

def test_expired_or_duplicate_signer_fails():
    trusted,receipts=suite()
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW+1000)
    trusted,receipts=suite()
    trusted["WORM"]=trusted["RULESET"]
    with pytest.raises(ReleaseAdmissionError,match="NON_INDEPENDENT"):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)

def test_malformed_or_unauthorized_gate_is_rejected():
    trusted,receipts=suite()
    receipts["NEW"]={"payload":{},"signature_hex":""}
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)
    trusted,receipts=suite()
    receipts["OWNER"]["payload"]["result"]="FAIL"
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)

def test_invalid_sha_and_nonfinite_expiry_fail():
    trusted,receipts=suite()
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha="1",artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts={},now=NOW)
    trusted,receipts=suite()
    receipts["OWNER"]["payload"]["expires_at"]=float("nan")
    with pytest.raises(ReleaseAdmissionError):
        evaluate_release(source_sha=SHA,artifact_sha256=ARTIFACT,
                         trusted_keys=trusted,receipts=receipts,now=NOW)
