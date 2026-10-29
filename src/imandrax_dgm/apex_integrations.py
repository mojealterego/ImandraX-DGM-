"""First-party, explicit integration of ImandraX, DGM and RSI into APEX.

The research proposer is intentionally UNBOUND: an arbitrary future module may
never silently acquire API tokens, a shell, release rights or the source tree.
"""
from __future__ import annotations
from .apex import ApexRegistry, Capability, EngineManifest


def core_manifests() -> tuple[EngineManifest, ...]:
    return (
        EngineManifest("imandrax", "1.0.0", (
            Capability("imandrax.math", "READ", ("operation", "arguments")),
            Capability("imandrax.formal", "READ", ("declaration",)),
        )),
        EngineManifest("dgm", "1.0.0", (
            Capability("dgm.history", "READ"),
        ), ("imandrax",)),
        EngineManifest("rsi", "1.0.0", (
            Capability("rsi.proposals", "RESEARCH"),
        ), ("dgm",)),
    )


def attach_unified_engine(engine: object) -> ApexRegistry:
    """Mount reviewed adapters only; no dynamic import of engine descriptors."""
    registry = ApexRegistry()
    for manifest in core_manifests():
        registry.register(manifest)

    def math_handler(data: dict):
        from .engine import MathTask
        task = MathTask(kind="EXACT_COMPUTE", operation=data["operation"],
                        arguments=data["arguments"])
        return engine.math(task)

    def formal_handler(data: dict):
        from .engine import MathTask
        return engine.math(MathTask(kind="FORMAL_PROOF_STATUS", statement=data["declaration"]))

    def history_handler(data: dict):
        rows = engine.research_archive.list_metadata()
        return {"generations": rows[:50], "total_generations": len(rows),
                "truncated": len(rows) > 50, "status": "RESEARCH_ONLY_UNAPPROVED"}

    registry.bind("imandrax.math", math_handler)
    registry.bind("imandrax.formal", formal_handler)
    registry.bind("dgm.history", history_handler)
    # rsi.proposals is a reserved, non-executable port until a narrowly scoped,
    # independently reviewed proposal adapter is implemented.
    return registry
