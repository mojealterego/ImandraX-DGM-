"""Control the one OMEGA Unified APEX kernel via an explicit local CLI.

This is not a web API and performs no autonomous approval, merge, or deploy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import uuid

from .apex import ApexError, ApexRegistry, ApexRequest, ApexRuntime
from .apex_integrations import attach_unified_engine, core_manifests


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="imandrax-apex", description="OMEGA APEX — unified capability and lifecycle kernel")
    p.add_argument("--state-dir", type=Path, required=True,
                   help="Owner-controlled persistence directory, outside the checked-out repository")
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("status", "start", "pause", "stop", "verify", "manifests", "history"):
        sub.add_parser(name)
    math = sub.add_parser("math")
    math.add_argument("--operation", required=True, choices=("gcd", "mod_pow", "is_prime"))
    math.add_argument("--arguments", required=True, help="JSON object of bounded integers")
    formal = sub.add_parser("formal")
    formal.add_argument("--declaration", required=True)
    args = p.parse_args(argv)
    state_dir = args.state_dir.resolve()
    root = args.root.resolve()
    if state_dir == root or state_dir.is_relative_to(root):
        p.error("--state-dir must be outside repository source")
    state_dir.mkdir(parents=True, exist_ok=True)
    db = state_dir / "apex.sqlite3"
    try:
        if args.command in {"math", "formal", "history"}:
            from .engine import IntegratedEngine
            # Formal status/history do not need to open the knowledge index, but
            # the engine constructor is deliberately shared across the product.
            integrated = IntegratedEngine(
                knowledge_db=state_dir / "mathematics.sqlite3",
                inventory=root / "data" / "repositories_public_701.tsv",
                ledger_db=state_dir / "ledger.sqlite3",
                review_db=state_dir / "review.sqlite3",
                archive_db=state_dir / "archive.sqlite3",
            )
            registry = attach_unified_engine(integrated)
        else:
            registry = ApexRegistry()
            for manifest in core_manifests():
                registry.register(manifest)
        runtime = ApexRuntime(registry, db)
        if args.command == "start":
            runtime.start()
            result = runtime.status()
        elif args.command == "pause":
            runtime.pause()
            result = runtime.status()
        elif args.command == "stop":
            runtime.stop()
            result = runtime.status()
        elif args.command == "verify":
            result = {"audit_verified": runtime.audit.verify(), "status": runtime.status()}
            if not result["audit_verified"]:
                raise ApexError("AUDIT_INTEGRITY_FAILURE")
        elif args.command == "manifests":
            result = {"engine_manifest_digest": registry.manifest_digest,
                      "manifests": [x.descriptor() for x in registry.freeze()]}
        elif args.command in ("math", "formal", "history"):
            if args.command == "math":
                payload = {"operation": args.operation, "arguments": json.loads(args.arguments)}
                capability = "imandrax.math"
            elif args.command == "formal":
                payload = {"declaration": args.declaration}
                capability = "imandrax.formal"
            else:
                payload = {}
                capability = "dgm.history"
            result = runtime.dispatch(ApexRequest(
                capability, payload, "local-operator", "cli-" + uuid.uuid4().hex))
        else:
            result = runtime.status()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except (ApexError, ValueError, OSError) as exc:
        # Avoid logging remote model messages, payloads or external secrets.
        code = str(exc) if isinstance(exc, ApexError) else "INVALID_LOCAL_CONFIGURATION"
        print(json.dumps({"status": "REJECTED", "reason": code}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
