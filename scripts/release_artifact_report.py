"""Standalone check of built wheel/sdist provenance; never a release authority.

Examines archive metadata and SHA-256 without importing or executing untrusted
packaging entrypoints. Unsigned report is local CI build evidence only.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib
import zipfile

_HASH = re.compile("[a-f0-9]{40}\\Z")
_MAX_ARCHIVE = 100 * 1024 * 1024


class ArtifactError(ValueError):
    pass


def _digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as source:
        for part in iter(lambda: source.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()


def _safe_path(name: str) -> None:
    name = name.replace("\\", "/")
    p = PurePosixPath(name)
    if (not name or p.is_absolute() or ".." in p.parts or
            any(not element or element == "." for element in p.parts)):
        raise ArtifactError("ARCHIVE_PATH_TRAVERSAL")


def _archive_metadata(path: Path, *, wheel: bool) -> bytes:
    if wheel:
        if not zipfile.is_zipfile(path):
            raise ArtifactError("INVALID_WHEEL")
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                _safe_path(info.filename)
                if info.file_size > _MAX_ARCHIVE:
                    raise ArtifactError("OVERSIZED_ARCHIVE_MEMBER")
            entries = [x for x in z.namelist() if x.endswith(".dist-info/METADATA")]
            if len(entries) != 1:
                raise ArtifactError("MISSING_OR_DUPLICATE_WHEEL_METADATA")
            data = z.read(entries[0])
    else:
        if not tarfile.is_tarfile(path):
            raise ArtifactError("INVALID_SDIST")
        with tarfile.open(path, "r:*") as tf:
            entries = []
            for member in tf.getmembers():
                _safe_path(member.name)
                if member.issym() or member.islnk():
                    raise ArtifactError("UNEXPECTED_ARCHIVE_LINK")
                if member.size > _MAX_ARCHIVE:
                    raise ArtifactError("OVERSIZED_ARCHIVE_MEMBER")
                # Only top-level sdist metadata; nested *.egg-info/PKG-INFO
                # is legitimate and must not count as a second root manifest.
                if member.name.endswith("/PKG-INFO") and len(PurePosixPath(member.name).parts) == 2:
                    entries.append(member)
            if len(entries) != 1:
                raise ArtifactError("MISSING_OR_DUPLICATE_SDIST_METADATA")
            stream = tf.extractfile(entries[0])
            if stream is None:
                raise ArtifactError("MISSING_SDIST_METADATA")
            data = stream.read(_MAX_ARCHIVE + 1)
    if len(data) > 1024*1024:
        raise ArtifactError("OVERSIZED_PACKAGE_METADATA")
    return data


def build_report(dist: Path, project: Path, commit: str) -> dict:
    if not isinstance(commit, str) or not _HASH.fullmatch(commit):
        raise ArtifactError("INVALID_SOURCE_COMMIT")
    dist, project = Path(dist), Path(project)
    if dist.is_symlink() or not dist.is_dir() or project.is_symlink() or not project.is_file():
        raise ArtifactError("INVALID_BUILD_INPUT")
    expected = tomllib.loads(project.read_text(encoding="utf-8"))["project"]
    name, version = expected["name"], expected["version"]
    packages = []
    files = sorted(x for x in dist.iterdir() if x.is_file())
    wheel_files = [x for x in files if x.name.endswith(".whl")]
    source_files = [x for x in files if x.name.endswith(".tar.gz")]
    if len(wheel_files) != 1 or len(source_files) != 1 or len(files) != 2:
        raise ArtifactError("EXPECTED_ONE_WHEEL_AND_ONE_SDIST")
    for path in (*wheel_files, *source_files):
        if path.is_symlink() or not 100 <= path.stat().st_size <= _MAX_ARCHIVE:
            raise ArtifactError("INVALID_BUILD_ARCHIVE")
        header = _archive_metadata(path, wheel=path in wheel_files).decode("utf-8")
        if not re.search(r"(?m)^Name:\s*" + re.escape(name) + r"\s*$", header):
            raise ArtifactError("PACKAGE_NAME_MISMATCH")
        if not re.search(r"(?m)^Version:\s*" + re.escape(version) + r"\s*$", header):
            raise ArtifactError("PACKAGE_VERSION_MISMATCH")
        packages.append({"name": path.name, "sha256": _digest(path),
                         "size_bytes": path.stat().st_size,
                         "type": "wheel" if path in wheel_files else "sdist"})
    return {
        "status": "UNSIGNED_BUILD_ARTIFACT_EVIDENCE_NOT_RELEASE_APPROVAL",
        "source_commit": commit, "name": name, "version": version,
        "artifacts": packages,
        "release_authorized": False,
        "missing_independent_gates": [
            "RULESET_MAIN_REVIEW", "SIGNED_OWNER_DECISION",
            "INDEPENDENT_TEST_ATTESTATIONS", "EXTERNAL_AUTHORITY_DEPLOYED",
            "DISASTER_RECOVERY_DRILL", "KMS_WORM_AND_PRIVACY_POLICY"
        ]
    }


def main(argv=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--dist",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--commit",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    result=build_report(args.dist,args.project,args.commit)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
