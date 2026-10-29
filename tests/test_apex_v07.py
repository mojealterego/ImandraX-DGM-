"""Omega Unified APEX: fail-closed cross-engine kernel contract tests."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import json
import pytest

from imandrax_dgm.apex import (
    ApexAudit, ApexError, ApexRegistry, ApexRequest, ApexRuntime,
    Capability, EngineManifest,
)
from imandrax_dgm.apex_integrations import attach_unified_engine, core_manifests


def manifest(name, dependencies=(), *, access="READ", handler="lookup"):
    return EngineManifest(name, "1.0.0", (Capability(f"{name}.{handler}", access, ("query",)),), tuple(dependencies))


def boot(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    reg.bind("imandrax.lookup", lambda payload: {"value": payload["query"], "proof_status": "NOT_PROVED"})
    runtime = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    return reg, runtime


def req(name="imandrax.lookup", q="x", request_id="req-01"):
    return ApexRequest(name, {"query": q}, "operator", request_id)


def test_manifest_graph_deterministic_and_extensible():
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    reg.register(manifest("dgm", ("imandrax",)))
    reg.register(manifest("rsi", ("dgm",)))
    assert [x.engine_id for x in reg.freeze()] == ["imandrax", "dgm", "rsi"]
    assert len(reg.manifest_digest) == 64
    assert reg.freeze() == reg.freeze()
    with pytest.raises(ApexError):
        reg.register(manifest("engine-four"))


def test_cyclic_or_unknown_dependencies_are_rejected():
    reg = ApexRegistry()
    reg.register(manifest("a", ("b",)))
    reg.register(manifest("b", ("a",)))
    with pytest.raises(ApexError, match="CYCLE"):
        reg.freeze()
    other = ApexRegistry()
    other.register(manifest("a", ("missing",)))
    with pytest.raises(ApexError, match="MISSING_DEPENDENCY"):
        other.freeze()


def test_invalid_manifests_fail_closed():
    for name in ("../escape", "a/B", "a b", "a..b", "", "A", "__"):
        with pytest.raises(ApexError):
            manifest(name)
    with pytest.raises(ApexError):
        EngineManifest("engine", "not-semver", (), ())
    with pytest.raises(ApexError):
        EngineManifest("engine", "1.0.0", (Capability("other.lookup", "READ", ("query",)),), ())
    with pytest.raises(ApexError):
        EngineManifest("engine", "1.0.0", (Capability("engine.lookup", "ELEVATE", ("query",)),), ())


def test_untrusted_unbound_and_authority_actions_denied(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("imandrax", access="AUTHORITY"))
    reg.bind("imandrax.lookup", lambda payload: {"unauthorized": True})
    runtime = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    runtime.start()
    with pytest.raises(ApexError, match="PROTECTED_CAPABILITY"):
        runtime.dispatch(req())
    assert runtime.audit.verify()
    assert runtime.audit.count() == 2  # START and DENIED


def test_unbound_read_capability_does_not_run(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    runtime = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    runtime.start()
    with pytest.raises(ApexError, match="UNBOUND_CAPABILITY"):
        runtime.dispatch(req())


def test_lifecycle_persists_and_rejects_invalid_transitions(tmp_path):
    reg, runtime = boot(tmp_path)
    with pytest.raises(ApexError, match="NOT_ACTIVE"):
        runtime.dispatch(req())
    runtime.start()
    assert runtime.status()["state"] == "ACTIVE"
    identity = runtime.status()["identity_id"]
    runtime.pause()
    with pytest.raises(ApexError, match="NOT_ACTIVE"):
        runtime.dispatch(req("imandrax.lookup", "abc", "req-02"))
    runtime.start()
    assert runtime.dispatch(req(request_id="req-03"))["output"]["value"] == "x"
    runtime.stop()
    assert runtime.audit.verify()
    restarted = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    assert restarted.status()["state"] == "STOPPED"
    assert restarted.status()["identity_id"] == identity
    with pytest.raises(ApexError):
        restarted.start()


def test_rejects_duplicate_and_tampered_requests(tmp_path):
    reg, runtime = boot(tmp_path)
    runtime.start()
    assert runtime.dispatch(req())["status"] == "OBSERVED"
    with pytest.raises(ApexError, match="DUPLICATE_REQUEST"):
        runtime.dispatch(req(request_id="req-01", q="other"))
    with pytest.raises(ApexError, match="INVALID_PAYLOAD"):
        runtime.dispatch(ApexRequest("imandrax.lookup", {"extra": 1}, "operator", "req-03"))
    with pytest.raises(ApexError, match="INVALID_PAYLOAD"):
        runtime.dispatch(ApexRequest("imandrax.lookup", {"query": "x" * 65536}, "operator", "req-04"))
    assert runtime.audit.verify()


def test_research_requires_explicit_enable_and_is_never_release(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("rsi", access="RESEARCH", handler="propose"))
    reg.bind("rsi.propose", lambda payload: {"state": "PROPOSED_AWAITING_REVIEW", "code_applied": False})
    no_research = ApexRuntime(reg, tmp_path / "test.sqlite3")
    no_research.start()
    with pytest.raises(ApexError, match="RESEARCH_DISABLED"):
        no_research.dispatch(ApexRequest("rsi.propose", {"query": "proof search"}, "operator", "research-01"))
    yes_research = ApexRuntime(reg, tmp_path / "test.sqlite3", enable_research=True)
    assert yes_research.dispatch(ApexRequest("rsi.propose", {"query": "proof search"}, "operator", "research-02"))["output"]["code_applied"] is False


def test_research_cannot_launder_authority_in_response(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("rsi", access="RESEARCH", handler="propose"))
    reg.bind("rsi.propose", lambda payload: {"state": "APPROVED", "deploy": True})
    rt = ApexRuntime(reg, tmp_path / "test.sqlite3", enable_research=True)
    rt.start()
    with pytest.raises(ApexError, match="UNSAFE_RESULT"):
        rt.dispatch(ApexRequest("rsi.propose", {"query": "x"}, "operator", "test-01"))


def test_integrity_chain_detects_database_mutation(tmp_path):
    reg, runtime = boot(tmp_path)
    runtime.start()
    runtime.dispatch(req())
    assert runtime.audit.verify()
    with sqlite3.connect(tmp_path / "apex.sqlite3") as con:
        with pytest.raises(sqlite3.DatabaseError):
            con.execute("UPDATE events SET event_digest='x' WHERE seq=1")
        # An adversary with filesystem control can destroy/replace DB; this test
        # only asserts append-only triggers, not an external WORM attestation.
    assert runtime.audit.verify()


def test_handler_exception_not_logged_with_raw_payload(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    reg.bind("imandrax.lookup", lambda payload: (_ for _ in ()).throw(RuntimeError("secret-token")))
    rt = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    rt.start()
    with pytest.raises(ApexError, match="HANDLER_FAILED") as e:
        rt.dispatch(req(q="private-owner-information"))
    assert "secret-token" not in str(e.value)
    with sqlite3.connect(tmp_path / "apex.sqlite3") as con:
        rows = repr(con.execute("SELECT * FROM events").fetchall())
    assert "private-owner-information" not in rows
    assert rt.audit.verify()


def test_bound_results_require_json_and_bounded_size(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    reg.bind("imandrax.lookup", lambda _: {"bad": object()})
    rt = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    rt.start()
    with pytest.raises(ApexError, match="INVALID_RESULT"):
        rt.dispatch(req())


def test_first_party_engine_math_and_dgm_are_wrapped(tmp_path):
    class FakeResearchArchive:
        def list_metadata(self):
            return [{"candidate_id": "abc", "depth": 2}]
    class FakeEngine:
        research_archive = FakeResearchArchive()
        def math(self, task):
            return {"status": "COMPUTED_EXACT", "value": 12, "operation": task.operation, "proof_status": "NOT_FORMALLY_PROVED"}
    reg = attach_unified_engine(FakeEngine())
    assert [x.engine_id for x in reg.freeze()] == ["imandrax", "dgm", "rsi"]
    rt = ApexRuntime(reg, tmp_path / "apex.sqlite3", enable_research=True)
    rt.start()
    a = rt.dispatch(ApexRequest("imandrax.math", {"operation": "gcd", "arguments": {"a": 12, "b": 24}}, "operator", "math-01"))
    assert a["output"]["value"] == 12
    b = rt.dispatch(ApexRequest("dgm.history", {}, "operator", "history-01"))
    assert b["output"]["generations"][0]["depth"] == 2
    with pytest.raises(ApexError, match="UNBOUND_CAPABILITY"):
        rt.dispatch(ApexRequest("rsi.proposals", {}, "operator", "proposal-01"))
    assert rt.audit.verify()


def test_manifest_change_rejected_with_same_identity_database(tmp_path):
    reg, rt = boot(tmp_path)
    reg2 = ApexRegistry()
    reg2.register(EngineManifest("imandrax", "2.0.0", (Capability("imandrax.lookup", "READ", ("query",)),), ()))
    with pytest.raises(ApexError, match="MANIFEST_DRIFT"):
        ApexRuntime(reg2, tmp_path / "apex.sqlite3")


def test_no_code_execution_or_deployment_entrypoints():
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    for method in ("apply_patch", "merge", "release", "deploy", "execute_shell", "load_plugin"):
        assert not hasattr(reg, method)
        assert not hasattr(ApexRuntime, method)


def test_tampering_with_lifecycle_metadata_is_detected(tmp_path):
    reg, rt = boot(tmp_path)
    rt.start()
    rt.pause()
    with sqlite3.connect(tmp_path / "apex.sqlite3") as con:
        con.execute("UPDATE metadata SET v='ACTIVE' WHERE k='state'")
    assert rt.audit.verify() is False
    with pytest.raises(ApexError, match="AUDIT_INTEGRITY_FAILURE"):
        ApexRuntime(reg, tmp_path / "apex.sqlite3")


def test_owner_signed_epoch_upgrade_preserves_identity(tmp_path):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from imandrax_dgm.apex import canonical_upgrade_message

    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    old = ApexRegistry()
    old.register(manifest("imandrax"))
    rt = ApexRuntime(old, tmp_path / "apex.sqlite3", owner_public_key=pub)
    rt.start()
    rt.pause()
    identity = rt.status()["identity_id"]

    newer = ApexRegistry()
    newer.register(manifest("imandrax"))
    newer.register(manifest("dgm", ("imandrax",)))
    message = canonical_upgrade_message(identity, old.manifest_digest, newer.manifest_digest, 1)
    signature = priv.sign(message).hex()
    rt.audit.upgrade_manifest(newer.manifest_digest, signature_hex=signature, owner_public_key=pub)
    advanced = ApexRuntime(newer, tmp_path / "apex.sqlite3", owner_public_key=pub)
    assert advanced.status()["identity_id"] == identity
    assert advanced.status()["epoch"] == 1
    assert advanced.audit.verify()
    with pytest.raises(ApexError):
        advanced.audit.upgrade_manifest("f" * 64, signature_hex=signature, owner_public_key=pub)
    with pytest.raises(ApexError):
        ApexRuntime(old, tmp_path / "apex.sqlite3", owner_public_key=pub)


def test_upgrade_requires_pinned_owner_key_and_paused_state(tmp_path):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from imandrax_dgm.apex import canonical_upgrade_message
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    reg, rt = boot(tmp_path)
    with pytest.raises(ApexError, match="OWNER_TRUST_ROOT_MISSING"):
        rt.audit.upgrade_manifest("f" * 64, signature_hex="0" * 128, owner_public_key=pub)
    path = tmp_path / "other.sqlite3"
    other = ApexRuntime(reg, path, owner_public_key=pub)
    newer = ApexRegistry()
    newer.register(manifest("imandrax"))
    newer.register(manifest("dgm", ("imandrax",)))
    msg = canonical_upgrade_message(other.status()["identity_id"], reg.manifest_digest,
                                    newer.manifest_digest, 1)
    with pytest.raises(ApexError, match="NOT_PAUSED"):
        other.audit.upgrade_manifest(newer.manifest_digest, signature_hex=priv.sign(msg).hex(), owner_public_key=pub)
    other.start()
    other.pause()
    wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    with pytest.raises(ApexError, match="TRUST_ROOT_DRIFT"):
        other.audit.upgrade_manifest(newer.manifest_digest, signature_hex=priv.sign(msg).hex(), owner_public_key=wrong_key)
    with pytest.raises(ApexError, match="INVALID_OWNER_SIGNATURE"):
        other.audit.upgrade_manifest(newer.manifest_digest, signature_hex="0" * 128, owner_public_key=pub)


def test_strict_manifest_parser_never_executes_code(tmp_path):
    from imandrax_dgm.apex_manifest import parse_manifest, load_manifest
    from imandrax_dgm.apex import _canonical
    example = manifest("new-engine")
    raw = _canonical(example.descriptor())
    loaded = parse_manifest(raw)
    assert loaded == example
    path = tmp_path / "descriptor.json"
    path.write_bytes(raw)
    assert load_manifest(path) == example
    alias = tmp_path / "alias.json"
    alias.symlink_to(path)
    with pytest.raises(ApexError, match="INVALID_MANIFEST_PATH"):
        load_manifest(alias)
    for wrong in (b"{}", b"not-json", b"[]", b" " * 70000):
        with pytest.raises(ApexError):
            parse_manifest(wrong)
    untrusted = json.loads(raw)
    untrusted["entrypoint"] = "os.system('malicious')"
    with pytest.raises(ApexError, match="INVALID_MANIFEST_SCHEMA"):
        parse_manifest(_canonical(untrusted))


def test_flow_topology_and_safe_execution(tmp_path):
    from imandrax_dgm.apex_flow import ApexFlow, FlowStep
    reg = ApexRegistry()
    reg.register(manifest("imandrax"))
    reg.register(manifest("dgm", ("imandrax",)))
    reg.bind("imandrax.lookup", lambda d: {"lookup": d["query"]})
    reg.bind("dgm.lookup", lambda d: {"checked": d["query"]})
    rt = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    rt.start()
    steps = (FlowStep("b", "dgm.lookup", {"query": "second"}, ("a",)),
             FlowStep("a", "imandrax.lookup", {"query": "first"}))
    flow = ApexFlow("flow01", steps)
    assert [x.step_id for x in flow.order] == ["a", "b"]
    outcome = flow.execute(rt, principal="operator")
    assert outcome["steps"]["a"]["output"]["lookup"] == "first"
    assert outcome["steps"]["b"]["output"]["checked"] == "second"
    assert outcome["auto_deploy"] is False
    with pytest.raises(ApexError, match="DUPLICATE_REQUEST"):
        flow.execute(rt, principal="operator")
    assert rt.audit.verify()


def test_flow_rejects_cycle_and_protected_operation_before_any_handler(tmp_path):
    from imandrax_dgm.apex_flow import ApexFlow, FlowStep
    with pytest.raises(ApexError, match="FLOW_CYCLE"):
        ApexFlow("loop", (FlowStep("a", "imandrax.lookup", {}, ("b",)),
                          FlowStep("b", "imandrax.lookup", {}, ("a",))))
    with pytest.raises(ApexError, match="UNKNOWN_FLOW_DEPENDENCY"):
        ApexFlow("unknown", (FlowStep("a", "imandrax.lookup", {}, ("missing",)),))
    visits = []
    reg = ApexRegistry()
    reg.register(EngineManifest("imandrax", "1.0.0", (
        Capability("imandrax.read", "READ"), Capability("imandrax.deploy", "MUTATION"))))
    reg.bind("imandrax.read", lambda _: visits.append(1) or {})
    rt = ApexRuntime(reg, tmp_path / "apex.sqlite3")
    rt.start()
    flow = ApexFlow("secure", (FlowStep("a", "imandrax.read", {}),
                               FlowStep("b", "imandrax.deploy", {}, ("a",))))
    with pytest.raises(ApexError, match="PROTECTED_CAPABILITY"):
        flow.execute(rt, principal="operator")
    assert visits == []


def test_apex_cli_lifecycle_and_status(tmp_path, capsys):
    from imandrax_dgm.apex_cli import main
    state = tmp_path / "state"
    root = tmp_path / "source"
    root.mkdir()
    opts = ["--state-dir", str(state), "--root", str(root)]
    assert main(opts + ["status"]) == 0
    assert '"state": "CREATED"' in capsys.readouterr().out
    assert main(opts + ["start"]) == 0
    assert '"state": "ACTIVE"' in capsys.readouterr().out
    assert main(opts + ["pause"]) == 0
    assert main(opts + ["verify"]) == 0
    assert '"audit_verified": true' in capsys.readouterr().out
    assert main(opts + ["stop"]) == 0
    assert main(opts + ["start"]) == 2


def test_cli_refuses_to_write_state_inside_repo(tmp_path):
    from imandrax_dgm.apex_cli import main
    source = tmp_path / "repo"
    source.mkdir()
    with pytest.raises(SystemExit):
        main(["--state-dir", str(source / ".apex"), "--root", str(source), "status"])


def test_invalid_json_nan_and_nested_untrusted_state(tmp_path):
    reg = ApexRegistry()
    reg.register(manifest("rsi", access="RESEARCH", handler="propose"))
    reg.bind("rsi.propose", lambda _: {"nested": [{"state": "APPROVED", "deploy": True}]})
    rt = ApexRuntime(reg, tmp_path / "state.sqlite3", enable_research=True)
    rt.start()
    with pytest.raises(ApexError, match="UNSAFE_RESULT"):
        rt.dispatch(ApexRequest("rsi.propose", {"query": "ok"}, "operator", "req-01"))
    with pytest.raises(ApexError, match="INVALID_PAYLOAD"):
        rt.dispatch(ApexRequest("rsi.propose", {"query": float("nan")}, "operator", "req-02"))
    assert rt.audit.verify()


def test_cli_can_pin_owner_public_key_at_first_boot(tmp_path, capsys):
    from imandrax_dgm.apex_cli import main
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    key_path = tmp_path / "owner_ed25519_public.key"
    key_path.write_bytes(pub)
    root = tmp_path / "source"
    root.mkdir()
    state = tmp_path / "state"
    opts = ["--root", str(root), "--state-dir", str(state),
            "--owner-public-key-file", str(key_path)]
    assert main(opts + ["status"]) == 0
    assert main(opts + ["start"]) == 0
    registry = ApexRegistry()
    for item in core_manifests():
        registry.register(item)
    runtime = ApexRuntime(registry, state / "apex.sqlite3", owner_public_key=pub)
    assert runtime.audit.meta()["owner_key_digest"] == __import__("hashlib").sha256(pub).hexdigest()
    wrong = tmp_path / "wrong.key"
    wrong.write_bytes(Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
    assert main(["--root", str(root), "--state-dir", str(state),
                 "--owner-public-key-file", str(wrong), "status"]) == 2


def test_manifest_rejects_duplicate_json_keys_and_unhashable_fields():
    from imandrax_dgm.apex_manifest import parse_manifest
    duplicate = b'{"engine_id":"a","engine_id":"b","version":"1.0.0","capabilities":[{"name":"a.x","access":"READ","input_fields":[]}],"dependencies":[]}'
    with pytest.raises(ApexError):
        parse_manifest(duplicate)
    malformed = b'{"engine_id":"a","version":"1.0.0","capabilities":[{"name":"a.x","access":"READ","input_fields":[["nested"]]}],"dependencies":[]}'
    with pytest.raises(ApexError):
        parse_manifest(malformed)


def test_flow_rejects_non_string_dependency_without_typeerror():
    from imandrax_dgm.apex_flow import ApexFlow, FlowStep
    with pytest.raises(ApexError, match="INVALID_FLOW_STEP"):
        ApexFlow("abc", (FlowStep("a", "imandrax.lookup", {}, (["wrong"],)),))
