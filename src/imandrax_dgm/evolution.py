"""DGM-style genealogy of independently reviewed variants (metadata only).

The archive never edits or runs code. Production must bind `authorize` to an
external, signed, independently hosted approval authority.
"""
from __future__ import annotations
from contextlib import contextmanager
import math
from pathlib import Path
import sqlite3
from typing import Callable


class ApprovedArchive:
    def __init__(self, path: Path, *, authorize: Callable[[str], bool]):
        if not callable(authorize):
            raise ValueError('Independent approval callback is required')
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.authorize = authorize
        with self._connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS generations (
                proposal_id TEXT PRIMARY KEY,
                parent_id TEXT,
                score REAL NOT NULL CHECK(score>=0 AND score<=1),
                transfer_score REAL NOT NULL CHECK(transfer_score>=0 AND transfer_score<=1),
                FOREIGN KEY(parent_id) REFERENCES generations(proposal_id))''')

    @contextmanager
    def _connect(self):
        con=sqlite3.connect(self.path,timeout=10)
        con.row_factory=sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def add(self, proposal_id: str, *, parent_id: str | None, score: float, transfer_score: float) -> dict:
        if (not isinstance(proposal_id,str) or not proposal_id or
                not all(isinstance(v,(int,float)) and math.isfinite(v) and 0<=v<=1 for v in (score,transfer_score))):
            raise ValueError('Invalid generation metadata')
        if not self.authorize(proposal_id):
            raise PermissionError('Human-signed approval required before archiving variant')
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            old=con.execute('SELECT * FROM generations WHERE proposal_id=?',(proposal_id,)).fetchone()
            if old:
                if (old['parent_id'],old['score'],old['transfer_score'])!=(parent_id,score,transfer_score):
                    raise ValueError('Immutable generation ID reused with changed metrics')
                return dict(old)
            if parent_id is not None:
                parent=con.execute('SELECT * FROM generations WHERE proposal_id=?',(parent_id,)).fetchone()
                if not parent or not self.authorize(parent_id):
                    raise ValueError('Parent must exist and retain valid approval')
            con.execute('INSERT INTO generations VALUES (?,?,?,?)',
                        (proposal_id,parent_id,float(score),float(transfer_score)))
            return dict(con.execute('SELECT * FROM generations WHERE proposal_id=?',(proposal_id,)).fetchone())

    def list(self):
        with self._connect() as con:
            return [dict(row) for row in con.execute('SELECT * FROM generations ORDER BY proposal_id')]

    def choose_parent(self):
        """Prefer quality, transfer and genealogical novelty; never choose revoked variants."""
        rows=self.list()
        valid=[r for r in rows if self.authorize(r['proposal_id'])]
        if not valid:
            return None
        children={r['proposal_id']:sum(x['parent_id']==r['proposal_id'] for x in rows) for r in valid}
        return max(valid,key=lambda r:(0.55*r['score']+0.35*r['transfer_score']+
                                      0.1/math.sqrt(children[r['proposal_id']]+1),r['proposal_id']))