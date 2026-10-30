"""Persistent *research-only* DGM genealogy, never a release or approval authority.

All code is untrusted data. Only evaluated candidates enter this archive; entries
are immutable and bound to an exact baseline commit and source SHA-256. The
archive is not an attested/WORM log and cannot be used as proof of correctness.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import math
from pathlib import Path
import re
import sqlite3

from .gates import canonical_payload
from .evaluation_policy import static_security_check

_SHA256 = re.compile(r'^[0-9a-f]{64}$')
_SHA40 = re.compile(r'^[0-9a-f]{40}$')
_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')
_MAX_DEPTH = 12
_MAX_SOURCE_BYTES = 160_000
_MAX_RECORDS = 2048


def _digest(obj: dict) -> str:
    return hashlib.sha256(canonical_payload(obj)).hexdigest()


class ResearchArchive:
    """Mutable research history of immutable candidate records; no promotion API."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS research_generations (
                candidate_id TEXT PRIMARY KEY,
                base_commit TEXT NOT NULL,
                baseline_sha256 TEXT NOT NULL,
                parent_id TEXT,
                depth INTEGER NOT NULL CHECK(depth BETWEEN 0 AND 12),
                patch_sha256 TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                content TEXT NOT NULL,
                regression REAL NOT NULL CHECK(regression BETWEEN 0 AND 1),
                heldout REAL NOT NULL CHECK(heldout BETWEEN 0 AND 1),
                novelty REAL NOT NULL CHECK(novelty BETWEEN 0 AND 1),
                evidence_sha256 TEXT NOT NULL,
                record_sha256 TEXT NOT NULL,
                FOREIGN KEY(parent_id) REFERENCES research_generations(candidate_id)
            )''')
            con.execute('''CREATE INDEX IF NOT EXISTS research_baseline_idx
                           ON research_generations(base_commit,baseline_sha256)''')
            con.executescript('''
                CREATE TRIGGER IF NOT EXISTS research_no_update
                BEFORE UPDATE ON research_generations
                BEGIN SELECT RAISE(ABORT,'research record immutable'); END;
                CREATE TRIGGER IF NOT EXISTS research_no_delete
                BEFORE DELETE ON research_generations
                BEGIN SELECT RAISE(ABORT,'research record immutable'); END;
            ''')

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.path, timeout=15)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @staticmethod
    def _validate(row: dict) -> dict:
        actual = dict(row)
        digest = actual.pop('record_sha256')
        if digest != _digest(actual):
            raise ValueError('Research archive integrity check failed')
        return actual

    def record(self, *, candidate_id: str, base_commit: str, baseline_sha256: str,
               patch_sha256: str, content: str, parent_id: str | None,
               regression: float, heldout: float, novelty: float,
               evidence_sha256: str) -> dict:
        if not isinstance(candidate_id,str) or not _ID.fullmatch(candidate_id):
            raise ValueError('Invalid research candidate ID')
        if not isinstance(base_commit,str) or not _SHA40.fullmatch(base_commit):
            raise ValueError('Invalid pinned Git commit')
        if any(not isinstance(x,str) or not _SHA256.fullmatch(x)
               for x in (baseline_sha256,patch_sha256,evidence_sha256)):
            raise ValueError('Invalid research digests')
        if not isinstance(content,str) or not content or '\x00' in content or len(content.encode()) > _MAX_SOURCE_BYTES:
            raise ValueError('Invalid research source')
        if not static_security_check(content)['pass']:
            raise ValueError('Research source fails static safety gate')
        if any(type(x) not in (int,float) or not math.isfinite(x) or not 0 <= x <= 1
               for x in (regression,heldout,novelty)):
            raise ValueError('Invalid research score')
        if parent_id is not None and (not isinstance(parent_id,str) or not _ID.fullmatch(parent_id)):
            raise ValueError('Invalid research parent ID')
        source_sha = hashlib.sha256(content.encode()).hexdigest()
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            depth = 0
            if parent_id is not None:
                parent = con.execute('SELECT * FROM research_generations WHERE candidate_id=?',(parent_id,)).fetchone()
                if parent is None:
                    raise ValueError('Research parent not found')
                parent = self._validate(dict(parent))
                if parent['base_commit'] != base_commit or parent['baseline_sha256'] != baseline_sha256:
                    raise ValueError('Research parent baseline mismatch')
                if parent['source_sha256'] == source_sha:
                    raise ValueError('Research child must change parent source')
                depth = parent['depth'] + 1
                if depth > _MAX_DEPTH:
                    raise ValueError('Research genealogy depth exceeded')
            payload = dict(candidate_id=candidate_id,base_commit=base_commit,
                           baseline_sha256=baseline_sha256,parent_id=parent_id,
                           depth=depth,patch_sha256=patch_sha256,
                           source_sha256=source_sha,content=content,
                           regression=float(regression),heldout=float(heldout),
                           novelty=float(novelty),evidence_sha256=evidence_sha256)
            record = {**payload,'record_sha256':_digest(payload)}
            old = con.execute('SELECT * FROM research_generations WHERE candidate_id=?',(candidate_id,)).fetchone()
            if old is not None:
                if dict(old) != record:
                    raise ValueError('Immutable research ID reused with changed content or metrics')
                return {k:v for k,v in payload.items() if k != 'content'}
            if con.execute('SELECT COUNT(*) FROM research_generations').fetchone()[0] >= _MAX_RECORDS:
                raise ValueError('Research archive capacity reached')
            con.execute('''INSERT INTO research_generations
                (candidate_id,base_commit,baseline_sha256,parent_id,depth,patch_sha256,
                 source_sha256,content,regression,heldout,novelty,evidence_sha256,record_sha256)
                VALUES (:candidate_id,:base_commit,:baseline_sha256,:parent_id,:depth,:patch_sha256,
                        :source_sha256,:content,:regression,:heldout,:novelty,:evidence_sha256,:record_sha256)''',record)
        return {k:v for k,v in payload.items() if k != 'content'}

    def list_metadata(self) -> list[dict]:
        with self._connect() as con:
            rows = con.execute('SELECT * FROM research_generations ORDER BY candidate_id').fetchall()
        return [{k:v for k,v in self._validate(dict(row)).items() if k != 'content'} for row in rows]

    def choose_parent(self, base_commit: str, baseline_sha256: str) -> dict | None:
        if not isinstance(base_commit,str) or not _SHA40.fullmatch(base_commit):
            raise ValueError('Invalid baseline commit')
        if not isinstance(baseline_sha256,str) or not _SHA256.fullmatch(baseline_sha256):
            raise ValueError('Invalid baseline digest')
        with self._connect() as con:
            rows = [self._validate(dict(row)) for row in con.execute('''
                SELECT * FROM research_generations
                WHERE base_commit=? AND baseline_sha256=? AND regression>=0.9 AND heldout>=0.9
                  AND depth < ?''',(base_commit,baseline_sha256,_MAX_DEPTH))]
            rows = [r for r in rows if len(r['content'].encode()) <= 12000]
            if not rows:
                return None
            children = {r['candidate_id']:con.execute(
                'SELECT COUNT(*) FROM research_generations WHERE parent_id=?',
                (r['candidate_id'],)).fetchone()[0] for r in rows}
        # Empirical ranking only, not proof of generalization or human authorization.
        winner = max(rows,key=lambda r:(0.25*r['regression']+0.55*r['heldout']+
                         0.1*r['novelty']+0.1/(1+children[r['candidate_id']]),
                         r['depth'],r['candidate_id']))
        return winner
