"""Read-only, fail-closed repository due diligence for OMEGA Unified APEX.

Root README and license-header inspection are evidence of inspection only.
They cannot authorize code loading, capability binding, RSI promotion or merge.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from .catalog import RepoCatalog

_SHA1 = re.compile(r"[0-9a-f]{40}\Z")
_LICENSE_MARKERS = frozenset({"Apache-2.0", "MIT", "BSD-3-Clause", "UNDETERMINED", "NOT_CHECKED"})
_MAX_EVIDENCE_BYTES = 262_144
_MISSING_GATES = (
    "SOURCE_COMMIT_PIN",
    "INDEPENDENT_SOURCE_AND_SECURITY_AUDIT",
    "LICENSE_COMPATIBILITY_REVIEW",
    "SBOM_AND_DEPENDENCY_REVIEW",
    "REPRODUCIBLE_BUILD_AND_TESTS",
    "ISOLATED_ADAPTER_E2E",
    "OWNER_SIGNED_MANIFEST_EPOCH",
)


class PortfolioEvidenceError(ValueError):
    """Evidence is malformed, inconsistent or references unknown repositories."""


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise PortfolioEvidenceError("DUPLICATE_EVIDENCE_JSON_KEY")
        out[key] = value
    return out


@dataclass(frozen=True)
class RootEvidence:
    repository: str
    readme_blob_sha: str
    license_blob_sha: str | None
    license_marker: str

    @classmethod
    def parse(cls, raw: object) -> "RootEvidence":
        if not isinstance(raw, dict) or set(raw) != {
            "repository", "readme_blob_sha", "license_blob_sha", "license_marker"
        }:
            raise PortfolioEvidenceError("INVALID_EVIDENCE_SCHEMA")
        repo, readme, license_sha, marker = (
            raw["repository"], raw["readme_blob_sha"],
            raw["license_blob_sha"], raw["license_marker"]
        )
        if (not isinstance(repo, str) or not repo.startswith("mojealterego/") or
                len(repo) > 200 or not repo.split("/", 1)[1]):
            raise PortfolioEvidenceError("INVALID_EVIDENCE_REPOSITORY")
        if not isinstance(readme, str) or not _SHA1.fullmatch(readme):
            raise PortfolioEvidenceError("INVALID_README_BLOB_SHA")
        if not isinstance(marker, str) or marker not in _LICENSE_MARKERS:
            raise PortfolioEvidenceError("INVALID_LICENSE_MARKER")
        if license_sha is None:
            if marker != "NOT_CHECKED":
                raise PortfolioEvidenceError("LICENSE_MARKER_WITHOUT_FILE")
        elif (not isinstance(license_sha, str) or not _SHA1.fullmatch(license_sha)
              or marker == "NOT_CHECKED"):
            raise PortfolioEvidenceError("INVALID_LICENSE_BLOB_SHA")
        return cls(repo, readme, license_sha, marker)


class PortfolioAudit:
    """Pure reporting over a static repository catalog and inspected root files."""

    def __init__(self, catalog: RepoCatalog, evidence: tuple[RootEvidence, ...]):
        self.catalog = catalog
        self.evidence: dict[str, RootEvidence] = {}
        for entry in evidence:
            key = entry.repository.casefold()
            if key in self.evidence:
                raise PortfolioEvidenceError("DUPLICATE_REPOSITORY_EVIDENCE")
            repo = catalog.by_name(entry.repository)
            if repo is None or repo.full_name != entry.repository:
                raise PortfolioEvidenceError("UNKNOWN_OR_MISMATCHED_REPOSITORY")
            self.evidence[key] = entry

    @classmethod
    def from_paths(cls, inventory_path: Path, evidence_path: Path) -> "PortfolioAudit":
        path = Path(evidence_path)
        if (path.is_symlink() or not path.is_file() or
                path.stat().st_size > _MAX_EVIDENCE_BYTES):
            raise PortfolioEvidenceError("INVALID_EVIDENCE_PATH")
        try:
            raw = json.loads(path.read_bytes(), object_pairs_hook=_unique_keys)
        except PortfolioEvidenceError:
            raise
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise PortfolioEvidenceError("INVALID_EVIDENCE_JSON") from exc
        if (not isinstance(raw, dict) or set(raw) != {"schema_version", "evidence"} or
                type(raw["schema_version"]) is not int or raw["schema_version"] != 1 or
                not isinstance(raw["evidence"], list)):
            raise PortfolioEvidenceError("INVALID_EVIDENCE_DOCUMENT")
        catalog = RepoCatalog.from_tsv(Path(inventory_path))
        if len(raw["evidence"]) > len(catalog.repos):
            raise PortfolioEvidenceError("TOO_MANY_EVIDENCE_RECORDS")
        return cls(catalog, tuple(RootEvidence.parse(row) for row in raw["evidence"]))

    def report(self, *, limit: int = 20) -> dict[str, Any]:
        if type(limit) is not int or not 1 <= limit <= len(self.catalog.repos):
            raise ValueError("INVALID_PORTFOLIO_LIMIT")
        rows = self.catalog.triage()
        priorities = Counter(row["priority"] for row in rows)
        candidates: list[dict[str, Any]] = []
        for row in rows[:limit]:
            evidence = self.evidence.get(row["repository"].casefold())
            candidates.append({
                "repository": row["repository"],
                "priority": row["priority"],
                "domain": row["domain"],
                "default_branch": row["branch"],
                "source_url": row["url"],
                "root_evidence": (
                    "NOT_REVIEWED" if evidence is None else
                    "README_AND_LICENSE_HEADER_INSPECTED" if evidence.license_blob_sha else
                    "README_ONLY_INSPECTED"
                ),
                "readme_blob_sha": evidence.readme_blob_sha if evidence else None,
                "license_blob_sha": evidence.license_blob_sha if evidence else None,
                "license_marker": evidence.license_marker if evidence else "NOT_CHECKED",
                "license_compatibility": "NOT_AUDITED",
                "integration_status": "NOT_INTEGRATED",
                "missing_gates": list(_MISSING_GATES),
            })
        return {
            "schema_version": 1,
            "mode": "READ_ONLY_PORTFOLIO_TRIAGE",
            "catalog_total": len(self.catalog.repos),
            "readme_inspected": len(self.evidence),
            "license_files_inspected": sum(1 for x in self.evidence.values() if x.license_blob_sha),
            "source_audited": 0,
            "ready_for_integration": 0,
            "integration_gate": "BLOCKED_PENDING_OWNER_APPROVAL_AND_AUDIT",
            "priority_counts": {key: priorities.get(key, 0) for key in ("P0", "P1", "P2", "P3", "P4")},
            "candidates": candidates,
        }
