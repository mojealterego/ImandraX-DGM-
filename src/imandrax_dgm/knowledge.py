"""Read-only, provenance-preserving mathematical knowledge index. NOT a proof engine."""
from __future__ import annotations
from pathlib import Path
import re
import sqlite3

ALLOWED_SOURCES=frozenset({'MSC2020-ENC','MSC2020-OFFICIAL','MSC2010','MATH-307','MSC2020-CLASS-ROUTING'})

class KnowledgeIndex:
    def __init__(self,path):
        self.path=Path(path).resolve()
    def _connect(self):
        con=sqlite3.connect(self.path.as_uri()+'?mode=ro',uri=True)
        con.row_factory=sqlite3.Row
        con.execute('PRAGMA query_only=ON')
        return con
    @staticmethod
    def _source(source):
        if source is not None and source not in ALLOWED_SOURCES:
            raise ValueError('Unknown knowledge source')
    def stats(self):
        with self._connect() as c:
            return {x['source']:x['n'] for x in c.execute('SELECT source,COUNT(*) n FROM entries GROUP BY source')}
    def exact(self,code,source=None):
        self._source(source)
        if not isinstance(code,str) or len(code)>64:
            raise ValueError('Invalid code')
        sql='SELECT source,code,title,body,page,status FROM entries WHERE code=?'
        params=[code]
        if source:
            sql+=' AND source=?';params.append(source)
        sql+=' ORDER BY source'
        with self._connect() as c:
            return [dict(x) for x in c.execute(sql,params)]
    def search(self,query,limit=10,source=None):
        self._source(source)
        if not isinstance(limit,int) or not 1<=limit<=100:
            raise ValueError('Limit must be 1..100')
        if not isinstance(query,str) or len(query)>4096:
            raise ValueError('Invalid query')
        tokens=re.findall(r'[^\W_]+',query,flags=re.UNICODE)[:16]
        if not tokens:
            return []
        fts=' OR '.join('"'+x+'"' for x in tokens)
        sql='''SELECT e.source,e.code,e.title,e.page,e.status,substr(e.body,1,400) excerpt,
                 bm25(entries_fts) rank FROM entries_fts
                 JOIN entries e ON e.rowid=entries_fts.rowid
                 WHERE entries_fts MATCH ?'''
        params=[fts]
        if source:
            sql+=' AND e.source=?';params.append(source)
        sql+=' ORDER BY rank LIMIT ?';params.append(limit)
        with self._connect() as c:
            return [dict(x) for x in c.execute(sql,params)]