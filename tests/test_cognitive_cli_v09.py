"""One-product CLI memory/cognition contract."""
import json
from pathlib import Path
from imandrax_dgm.cli import main
from imandrax_dgm.cognitive_cli import execute, load_payload


def test_cognitive_cli_roundtrip_and_checkpoint(tmp_path, capsys):
    root = Path(__file__).resolve().parents[1]
    state = tmp_path / "state"
    payload_file = tmp_path / "input.json"
    payload_file.write_text(json.dumps({
        "tenant": "tenant-1", "fact_id": "fact-1", "kind": "EPISODIC",
        "subject": "engine", "predicate": "observed",
        "value": {"event": "proof-started"}, "valid_from": "2026-10-30T00:00:00Z",
        "request_id": "event-1", "provenance": "operator"
    }), encoding="utf-8")
    args = ["--root", str(root), "cognitive", "--state-dir", str(state),
            "--op", "remember", "--payload-file", str(payload_file)]
    assert main(args) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["status"] == "RECORDED_UNVERIFIED"
    payload_file.write_text(json.dumps({
        "tenant": "tenant-1", "valid_at": "2026-10-30T00:00:00Z"
    }), encoding="utf-8")
    args[args.index("remember")] = "recall"
    assert main(args) == 0
    query = json.loads(capsys.readouterr().out)
    assert query["facts"][0]["value"] == {"event": "proof-started"}
    payload_file.write_text("{}", encoding="utf-8")
    args[args.index("recall")] = "checkpoint"
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["system_seq"] == 1


def test_no_memory_is_written_inside_source_repo(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    try:
        execute("checkpoint", {}, root=root, state_dir=root / "local")
    except ValueError as exc:
        assert "SOURCE_FORBIDDEN" in str(exc)
    else:
        raise AssertionError("State isolation was not enforced")


def test_json_duplicate_keys_rejected(tmp_path):
    import pytest
    path = tmp_path / "bad.json"
    path.write_text('{"tenant":"a","tenant":"b"}', encoding="utf-8")
    with pytest.raises(ValueError, match="DUPLICATE_INPUT_KEY"):
        load_payload(path)
