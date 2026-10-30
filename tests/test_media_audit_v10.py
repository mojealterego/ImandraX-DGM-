from pathlib import Path
import pytest
from imandrax_dgm.media_audit import audit_media_repositories

ROOT=Path(__file__).resolve().parents[1]
def test_full_inventory_scanned_without_implementation_claims():
    result=audit_media_repositories(ROOT/"data/repositories_public_701.tsv",
                                    ROOT/"data/media_repo_evidence_v10.json",limit=120)
    assert result["inventory_total"]==701
    assert result["matching_repositories"]>=50
    assert result["root_readme_inspected"]==12
    assert result["license_headers_inspected"]==8
    assert result["integrated_count"]==0
    assert all(item["source_audit"]=="NOT_DONE" and item["integration"]=="BLOCKED"
               for item in result["items"])
    assert result["domains"]["GAME_ENGINE"]>=15
    assert result["domains"]["UNCENSORED_RESEARCH"]>=4
def test_media_evidence_forbids_claim_of_source_audit(tmp_path):
    import json
    contents=json.loads((ROOT/"data/media_repo_evidence_v10.json").read_text())
    contents["repositories"][0]["integrated"]=True
    file=tmp_path/"altered.json"
    file.write_text(json.dumps(contents))
    with pytest.raises(ValueError,match="UNVERIFIED_INTEGRATION_CLAIM"):
        audit_media_repositories(ROOT/"data/repositories_public_701.tsv",file)
