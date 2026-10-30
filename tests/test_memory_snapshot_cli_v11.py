"""One-engine CLI exports unsigned backups; only offline operator can sign."""
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from imandrax_dgm.cognitive_cli import execute
from imandrax_dgm.memory_snapshot import signature_message

def test_operator_export_verify_restore(tmp_path):
    root=tmp_path/"repo";root.mkdir()
    state=tmp_path/"state"
    execute("remember",{"tenant":"lab","fact_id":"a","kind":"EPISODIC",
            "subject":"engine","predicate":"verified","value":{"good":True},
            "valid_from":"2026-01-01T00:00:00Z",
            "recorded_at":"2026-01-01T00:00:00Z",
            "request_id":"r1","provenance":"operator"},
            root=root,state_dir=state)
    snapshot=tmp_path/"backups"/"memory.sqlite3"
    manifest=tmp_path/"backups"/"manifest.json"
    exported=execute("snapshot-export",{
        "snapshot":str(snapshot),"manifest":str(manifest),
        "identity_id":"omega-1"},root=root,state_dir=state)
    assert exported["status"]=="UNSIGNED_BACKUP_REQUIRES_OFFLINE_OWNER_SIGNATURE"
    sk=Ed25519PrivateKey.generate()
    pk=sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)
    sig=sk.sign(signature_message(exported["manifest"])).hex()
    data={"snapshot":str(snapshot),"manifest":str(manifest),
          "signature_hex":sig,"owner_public_key_hex":pk.hex(),
          "expected_identity_id":"omega-1","min_system_seq":1}
    assert execute("snapshot-verify",data,root=root,state_dir=state)["status"]=="SIGNED_SNAPSHOT_VERIFIED"
    data["destination"]=str(tmp_path/"recovered"/"memory.sqlite3")
    assert execute("snapshot-restore",data,root=root,state_dir=state)["status"]=="VERIFIED_COPY_RESTORED_NO_LIVE_REPLACEMENT"

def test_export_source_tree_is_protected(tmp_path):
    import pytest
    root=tmp_path/"repo";root.mkdir()
    with pytest.raises(ValueError,match="SNAPSHOT_PATH"):
        execute("snapshot-export",{
            "snapshot":str(root/"x.sqlite"),
            "manifest":str(tmp_path/"manifest.json"),
            "identity_id":"omega-1"},
            root=root,state_dir=tmp_path/"state")
