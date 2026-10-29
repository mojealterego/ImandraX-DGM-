"""MSC2020 official 6006 detailed labels are actual runtime data, not just a plan."""
from pathlib import Path
import csv
import sqlite3
import pytest
from scripts.build_msc_full_index import build_index
from imandrax_dgm.knowledge import KnowledgeIndex

ROOT=Path(__file__).resolve().parents[1]


def test_official_6006_source_rows_really_indexed(tmp_path):
    source=ROOT/'data/msc2020_6006_coverage.csv'
    with source.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==6006
    assert len({r['msc_code'] for r in rows})==6006
    db=tmp_path/'msc.sqlite3'
    assert build_index(source,db)==6006
    index=KnowledgeIndex(db)
    assert index.stats()=={'MSC2020-OFFICIAL':6006}
    entry=index.exact('00-01',source='MSC2020-OFFICIAL')[0]
    assert entry['page']==4
    assert entry['status']=='SOURCE_INDEXED_NOT_FORMALIZED'
    assert 'Introductory exposition' in entry['title']
    assert index.search('logic',source='MSC2020-OFFICIAL')
    with pytest.raises(FileExistsError):
        build_index(source,db)


def test_full_msc_index_rejects_missing_rows(tmp_path):
    src=ROOT/'data/msc2020_6006_coverage.csv'
    bad=tmp_path/'bad.csv'
    bad.write_text('\n'.join(src.read_text().splitlines()[:10]))
    with pytest.raises(ValueError,match='6006'):
        build_index(bad,tmp_path/'not-created.sqlite3')
    assert not (tmp_path/'not-created.sqlite3').exists()
