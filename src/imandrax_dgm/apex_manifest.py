"""Untrusted capability descriptor input: validates data, never loads Python code."""
from __future__ import annotations

import json
from pathlib import Path
from .apex import ApexError, Capability, EngineManifest

MAX_MANIFEST_BYTES = 65536


def parse_manifest(raw: bytes) -> EngineManifest:
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_MANIFEST_BYTES:
        raise ApexError("INVALID_MANIFEST_LENGTH")
    def no_duplicate_keys(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ApexError("DUPLICATE_MANIFEST_KEY")
            obj[key] = value
        return obj
    try:
        data = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (ValueError, UnicodeError) as exc:
        raise ApexError("INVALID_MANIFEST_JSON") from exc
    if not isinstance(data, dict) or set(data) != {"engine_id", "version", "dependencies", "capabilities"}:
        raise ApexError("INVALID_MANIFEST_SCHEMA")
    if not isinstance(data["dependencies"], list) or not isinstance(data["capabilities"], list):
        raise ApexError("INVALID_MANIFEST_SCHEMA")
    capabilities = []
    for obj in data["capabilities"]:
        if not isinstance(obj, dict) or set(obj) != {"name", "access", "input_fields"}:
            raise ApexError("INVALID_MANIFEST_SCHEMA")
        if not isinstance(obj["input_fields"], list):
            raise ApexError("INVALID_MANIFEST_SCHEMA")
        capabilities.append(Capability(obj["name"], obj["access"], tuple(obj["input_fields"])))
    return EngineManifest(data["engine_id"], data["version"], tuple(capabilities),
                          tuple(data["dependencies"]))


def load_manifest(path: Path) -> EngineManifest:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ApexError("INVALID_MANIFEST_PATH")
    return parse_manifest(path.read_bytes())
