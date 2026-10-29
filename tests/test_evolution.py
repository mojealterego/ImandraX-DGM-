"""DGM archive retains only human-approved generations, and never executes them."""
import math
import pytest
from imandrax_dgm.evolution import ApprovedArchive


def test_archive_refuses_unapproved_generation(tmp_path):
    archive=ApprovedArchive(tmp_path/'archive.sqlite3',authorize=lambda proposal: False)
    with pytest.raises(PermissionError):
        archive.add('c1',parent_id=None,score=0.5,transfer_score=0.5)
    assert archive.list()==[]


def test_archive_selects_verified_approved_parents(tmp_path):
    approved={'genesis','child'}
    archive=ApprovedArchive(tmp_path/'archive.sqlite3',authorize=lambda proposal: proposal in approved)
    archive.add('genesis',parent_id=None,score=0.4,transfer_score=0.4)
    archive.add('child',parent_id='genesis',score=0.8,transfer_score=0.7)
    assert archive.choose_parent()['proposal_id']=='child'
    assert len(archive.list())==2
    assert archive.add('child',parent_id='genesis',score=0.8,transfer_score=0.7)['proposal_id']=='child'
    with pytest.raises(ValueError):
        archive.add('child',parent_id='genesis',score=0.9,transfer_score=0.7)


def test_archive_blocks_unknown_parent_and_bad_metrics(tmp_path):
    archive=ApprovedArchive(tmp_path/'archive.sqlite3',authorize=lambda proposal: True)
    with pytest.raises(ValueError):
        archive.add('child',parent_id='unknown',score=0.8,transfer_score=0.8)
    with pytest.raises(ValueError):
        archive.add('root',parent_id=None,score=float('nan'),transfer_score=0.8)
    with pytest.raises(ValueError):
        archive.add('root',parent_id=None,score=1.2,transfer_score=0.8)


def test_archive_refuses_late_revocation(tmp_path):
    allowed={'root'}
    archive=ApprovedArchive(tmp_path/'archive.sqlite3',authorize=lambda proposal: proposal in allowed)
    archive.add('root',parent_id=None,score=0.5,transfer_score=0.5)
    allowed.clear()
    assert archive.choose_parent() is None