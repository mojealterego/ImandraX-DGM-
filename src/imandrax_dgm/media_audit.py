"""Read-only multimedia repository triage over the existing 701-item inventory.

Name categories and README/LICENSE metadata are not code or model licensing audits.
No cloning, importing, execution, dynamic plugin loading or tool privilege.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
from .catalog import RepoCatalog

DOMAINS = {
    "GAME_ENGINE": re.compile(r"unreal|unity|godot|game|metahuman|3d|world", re.I),
    "PHOTO_IMAGE": re.compile(r"photo|image|diffusion|comfy|aether|portrait|camera|raw|exif", re.I),
    "VIDEO_FILM": re.compile(r"video|cinema|film|wan|hunyuan|ltx|animation|motion", re.I),
    "AUDIO_MUSIC": re.compile(r"audio|music|voice|sound|tts|speech|whisper", re.I),
    "MODEL_TRAINING": re.compile(r"train|fine.?tun|dataset|lora|model|jax|torch|tensorflow", re.I),
    "UNCENSORED_RESEARCH": re.compile(r"uncensored|abliterat|nsfw|adult", re.I),
}


def audit_media_repositories(inventory: Path, evidence: Path,
                             *, limit: int = 120) -> dict:
    if type(limit) is not int or not 1 <= limit <= 701:
        raise ValueError("INVALID_AUDIT_LIMIT")
    path = Path(evidence)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("INVALID_AUDIT_EVIDENCE")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(raw, dict) or raw.get("schema_version") != 1
            or not isinstance(raw.get("repositories"), list)):
        raise ValueError("INVALID_AUDIT_EVIDENCE")
    catalog = RepoCatalog.from_tsv(inventory)
    lookup = {}
    for item in raw["repositories"]:
        if not isinstance(item, dict) or set(item) != {
            "repository", "readme_blob_sha", "license_blob_sha", "license_label",
            "license_compatibility", "source_audit", "integrated"
        }:
            raise ValueError("INVALID_AUDIT_RECORD")
        key = item["repository"]
        if key in lookup or catalog.by_name(key) is None:
            raise ValueError("INVALID_OR_DUPLICATE_REPO")
        if item["integrated"] is not False or item["source_audit"] != "NOT_DONE" or item["license_compatibility"] != "NOT_REVIEWED":
            raise ValueError("UNVERIFIED_INTEGRATION_CLAIM")
        lookup[key] = item
    results=[]
    counts={x:0 for x in DOMAINS}
    for repo in catalog.repos:
        domains=[name for name,pattern in DOMAINS.items() if pattern.search(repo.name)]
        if not domains:
            continue
        for name in domains:
            counts[name]+=1
        evidence_item=lookup.get(repo.full_name)
        results.append({
            "repository":repo.full_name, "domains":domains, "default_branch":repo.default_branch,
            "url":repo.url, "readme_inspected":evidence_item is not None,
            "license_label":evidence_item["license_label"] if evidence_item else "NOT_INSPECTED",
            "license_compatibility":"NOT_REVIEWED",
            "source_audit":"NOT_DONE", "integration":"BLOCKED",
            "requires":["PIN_COMMIT_AND_VERIFY_LICENSES","AUDIT_CODE_AND_DEPENDENCIES",
                        "REPRODUCIBLE_TESTS","OWNER_SIGNED_APEX_MIGRATION"]
        })
    results.sort(key=lambda x:(-len(x["domains"]),x["repository"].casefold()))
    return {"status":"READ_ONLY_METADATA_TRIAGE", "inventory_total":len(catalog.repos),
            "matching_repositories":len(results), "root_readme_inspected":len(lookup),
            "license_headers_inspected":sum(x["license_blob_sha"] is not None for x in lookup.values()),
            "domains":counts, "items":results[:limit],
            "truncated":len(results)>limit, "integrated_count":0}
