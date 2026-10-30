"""Staging manifest and proposed ruleset MUST fail closed on credential exposure."""
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def test_openshift_is_staging_only_and_private():
    path=ROOT/"deploy/openshift-sandbox/staging.yaml"
    text=path.read_text()
    docs=list(yaml.safe_load_all(text))
    kinds={x["kind"] for x in docs}
    assert kinds=={"ServiceAccount","Deployment","Service","PersistentVolumeClaim","NetworkPolicy"}
    assert "Route" not in kinds and "Ingress" not in kinds
    deployment=next(x for x in docs if x["kind"]=="Deployment")
    spec=deployment["spec"]["template"]["spec"]
    assert spec["automountServiceAccountToken"] is False
    assert spec["securityContext"]["runAsNonRoot"] is True
    assert spec["serviceAccountName"]=="omega-staging-authority"
    app=spec["containers"][0]
    assert app["securityContext"]["readOnlyRootFilesystem"]
    assert app["securityContext"]["allowPrivilegeEscalation"] is False
    assert app["securityContext"]["capabilities"]["drop"]==["ALL"]
    assert "@sha256:" in app["image"]
    assert all("PRIVATE_KEY" not in str(x).upper() for x in app.get("env",[]))
    service=next(x for x in docs if x["kind"]=="Service")
    assert service["spec"]["type"]=="ClusterIP"
    policy=next(x for x in docs if x["kind"]=="NetworkPolicy")
    assert policy["spec"]["egress"]==[]
    assert "Egress" in policy["spec"]["policyTypes"]

def test_ruleset_proposal_respects_owner_main_only_without_pr():
    payload=json.loads((ROOT/"deploy/github-main/ruleset-proposed.json").read_text())
    assert payload["enforcement"]=="active"
    assert payload["conditions"]["ref_name"]["include"]==["refs/heads/main"]
    assert payload["bypass_actors"]==[]
    assert {r["type"] for r in payload["rules"]}=={"deletion","non_fast_forward"}
    assert all(x["type"] not in {"pull_request","required_status_checks"} for x in payload["rules"])
    assert not list(ROOT.glob(".github/workflows/*reviewer*"))
