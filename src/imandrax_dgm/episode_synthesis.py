"""Deterministic episodic-to-semantic index consolidation, not fact invention."""
from __future__ import annotations

from typing import Sequence

from .cognitive_memory import BitemporalGraphMemory


def synthesize_episodes(
    memory: BitemporalGraphMemory, *, tenant: str,
    source_ids: Sequence[str], semantic_id: str, now: str, request_id: str
) -> dict:
    if not isinstance(source_ids, (list, tuple)) or not 1 <= len(source_ids) <= 12:
        raise ValueError("INVALID_EPISODE_SET")
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("DUPLICATE_EPISODE")
    rows = memory.query(tenant=tenant, valid_at=now, kind="EPISODIC", limit=100)
    sources = {row["fact_id"]: row for row in rows}
    if not set(source_ids).issubset(sources):
        raise ValueError("EPISODE_MISSING_OR_DIFFERENT_TENANT")
    memory.put(tenant=tenant, fact_id=semantic_id, kind="SEMANTIC",
               subject="episodic-synthesis", predicate="references",
               value={"sources": list(source_ids), "inferred_fact": False,
                      "statement": "Indexed episodes without independent inference",
                      "source_versions": {id: sources[id]["seq"] for id in source_ids}},
               valid_from=now, request_id=request_id, provenance="LOCAL_REFERENCE_SYNTHESIS")
    return {"status": "SEMANTIC_REFERENCE_SYNTHESIS_NOT_PROOF",
            "source_count": len(source_ids), "semantic_fact_id": semantic_id}
