"""Deterministic tiny offline fixture. Real 19,114-row dataset is an optional artifact."""
import sqlite3
import pytest

@pytest.fixture
def math_db(tmp_path):
    path=tmp_path/'math_fixture.sqlite3'
    with sqlite3.connect(path) as c:
        c.execute('CREATE TABLE entries (source TEXT, code TEXT, title TEXT, body TEXT, page INTEGER, status TEXT)')
        c.execute("CREATE VIRTUAL TABLE entries_fts USING fts5(title,body,content='entries',content_rowid='rowid')")
        c.executemany('INSERT INTO entries VALUES (?,?,?,?,?,?)',[
            ('MSC2020-ENC','00A05','Algebraic structures','Elementary algebra',1,'SOURCE_REFERENCE_ONLY'),
            ('MSC2020-ENC','00A10','Number theory','Numbers and proofs',2,'SOURCE_REFERENCE_ONLY'),
        ])
        c.execute("INSERT INTO entries_fts(entries_fts) VALUES('rebuild')")
    return path