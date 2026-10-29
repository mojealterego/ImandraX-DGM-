"""Deterministic 63-class MSC routing bootstrap; NOT the full 19,114-row index.

Source is a locally reviewed classification routing table in docs. Its labels
and proposed modules are metadata, not mathematical proof or verified axioms.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sqlite3

ROW = re.compile(r'^\|\s*([0-9]{2})\s*\|\s*([^|]+)\s*\|\s*([0-9]+)\s*\|\s*([^|]+)\s*\|')


def build_index(source: Path, destination: Path) -> int:
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Refuse to overwrite a knowledge database')
    rows = []
    for line in source.read_text(encoding='utf-8').splitlines():
        match = ROW.match(line)
        if match:
            code, title, count, module = match.groups()
            rows.append(('MSC2020-CLASS-ROUTING',f'{code}-XX',title.strip(),
                         f'Project routing module: {module.strip()}; detail code count: {count}',
                         0,'INDEXED_ROUTING_ONLY'))
    if len(rows) != 63 or len({r[1] for r in rows}) != 63:
        raise ValueError('Routing table must contain exactly 63 distinct MSC classes')
    destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        with sqlite3.connect(destination) as con:
            con.execute('CREATE TABLE entries (source TEXT, code TEXT, title TEXT, body TEXT, page INTEGER, status TEXT)')
            con.execute("CREATE VIRTUAL TABLE entries_fts USING fts5(title,body,content='entries',content_rowid='rowid')")
            con.executemany('INSERT INTO entries VALUES (?,?,?,?,?,?)',rows)
            con.execute("INSERT INTO entries_fts(entries_fts) VALUES('rebuild')")
        return len(rows)
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1]/'docs/MSC2020_63_CLASS_ROUTING.md')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    print(f'INDEXED_ROUTING_ONLY: {build_index(args.source,args.output)} MSC classes')


if __name__=='__main__':
    main()