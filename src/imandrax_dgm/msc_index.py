"""Deterministic MSC2020 detailed-code FTS5 bootstrap from user-supplied PDF audit.

This is a source title index (6006 entries), not a Lean theorem library and not
an ingestion of the separate 19,114-record full mathematical research corpus.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import re
import sqlite3

_REQUIRED={'msc_code','class','official_title','encyclopedia_page','classification_page',
           'knowledge_indexed','formalized_in_lean','verified_proof','implementation_status'}
_CODE=re.compile(r'^[0-9]{2}(?:-[0-9]{2}|[A-Z][0-9]{2})$')


def build_index(source: Path, destination: Path) -> int:
    source,destination=Path(source),Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Refuse to overwrite existing mathematical index')
    with source.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not _REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError('Missing required MSC2020 provenance columns')
        rows=[]
        for r in reader:
            code=r['msc_code']
            title=r['official_title']
            if (not isinstance(code,str) or not _CODE.fullmatch(code) or
                    not isinstance(title,str) or not 1<=len(title)<=1000 or
                    r['class']!=code[:2] or
                    r['knowledge_indexed']!='YES' or r['verified_proof']!='NO' or
                    r['formalized_in_lean']!='NOT_AUDITED'):
                raise ValueError('MSC2020 row lacks source integrity or proof status')
            try:
                page=int(r['classification_page'])
                enc_page=int(r['encyclopedia_page'])
            except (TypeError,ValueError) as exc:
                raise ValueError('Missing MSC2020 source page') from exc
            if not 1<=page<=300 or not 1<=enc_page<=2000:
                raise ValueError('MSC2020 source page out of range')
            body=(f'MSC2020 classification entry {code}; official classification PDF page {page}; '
                  f'editorial encyclopedia PDF page {enc_page}. Source-indexed only; '
                  'no independently kernel-checked proof for this classification entry.')
            rows.append(('MSC2020-OFFICIAL',code,title,body,page,'SOURCE_INDEXED_NOT_FORMALIZED'))
    if len(rows)!=6006 or len({x[1] for x in rows})!=6006:
        raise ValueError('Expected exactly 6006 unique MSC2020 detailed codes')
    destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        with sqlite3.connect(destination) as con:
            con.execute('CREATE TABLE entries (source TEXT, code TEXT, title TEXT, body TEXT, page INTEGER, status TEXT)')
            con.execute("CREATE VIRTUAL TABLE entries_fts USING fts5(title,body,content='entries',content_rowid='rowid')")
            con.executemany('INSERT INTO entries VALUES (?,?,?,?,?,?)',rows)
            con.execute("INSERT INTO entries_fts(entries_fts) VALUES('rebuild')")
            if con.execute('SELECT COUNT(*) FROM entries').fetchone()[0]!=6006:
                raise ValueError('Incomplete MSC2020 database transaction')
        return len(rows)
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[2]/'data/msc2020_6006_coverage.csv')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    count=build_index(args.source,args.output)
    print(f'MSC2020-OFFICIAL: {count} source-indexed detailed codes (not formal proofs)')


if __name__=='__main__':
    main()
