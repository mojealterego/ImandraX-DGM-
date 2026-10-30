"""Package integrity checks are fail closed, independent of dynamic imports."""
from pathlib import Path
import io
import tarfile
import zipfile

import pytest
from scripts.release_artifact_report import build_report, ArtifactError


def build_archive(tmp_path, name="imandrax-dgm-unified", version="1.1.0"):
    root=tmp_path/"dist"
    root.mkdir()
    project=tmp_path/"pyproject.toml"
    project.write_text(f'[project]\nname="{name}"\nversion="{version}"\n')
    whl=root/"unit-1.1.0-py3-none-any.whl"
    with zipfile.ZipFile(whl,"w") as z:
        z.writestr("unit-1.1.0.dist-info/METADATA",
                   f"Metadata-Version: 2.3\nName: {name}\nVersion: {version}\n")
    sd=root/"unit-1.1.0.tar.gz"
    content=f"Metadata-Version: 2.3\nName: {name}\nVersion: {version}\n".encode()
    with tarfile.open(sd,"w:gz") as archive:
        info=tarfile.TarInfo("unit-1.1.0/PKG-INFO")
        info.size=len(content)
        archive.addfile(info,io.BytesIO(content))
    return root,project,whl


def test_valid_archive_report_is_unsigned_and_non_authoritative(tmp_path):
    dist,project,whl=build_archive(tmp_path)
    report=build_report(dist,project,"a"*40)
    assert len(report["artifacts"])==2
    assert report["release_authorized"] is False
    assert report["source_commit"]=="a"*40
    assert report["status"]=="UNSIGNED_BUILD_ARTIFACT_EVIDENCE_NOT_RELEASE_APPROVAL"


def test_archive_rejects_unexpected_duplicate_or_bad_metadata(tmp_path):
    dist,project,whl=build_archive(tmp_path)
    (dist/"rogue.whl").write_bytes(b"data")
    with pytest.raises(ArtifactError,match="EXPECTED_ONE"):
        build_report(dist,project,"a"*40)
    (dist/"rogue.whl").unlink()
    with zipfile.ZipFile(whl,"w") as z:
        z.writestr("unit-1.1.0.dist-info/METADATA",
                   "Name: wrong-package\nVersion: 1.1.0\n")
    with pytest.raises(ArtifactError,match="PACKAGE_NAME"):
        build_report(dist,project,"a"*40)


def test_archive_rejects_path_traversal(tmp_path):
    dist,project,whl=build_archive(tmp_path)
    with zipfile.ZipFile(whl,"w") as z:
        z.writestr("../malicious",b"X")
        z.writestr("unit-1.1.0.dist-info/METADATA",
                   "Name: imandrax-dgm-unified\nVersion: 1.1.0\n")
    with pytest.raises(ArtifactError,match="ARCHIVE_PATH_TRAVERSAL"):
        build_report(dist,project,"a"*40)


def test_source_commit_is_validated(tmp_path):
    dist,project,_=build_archive(tmp_path)
    with pytest.raises(ArtifactError,match="INVALID_SOURCE_COMMIT"):
        build_report(dist,project,"nope")
