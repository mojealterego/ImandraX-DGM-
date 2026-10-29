"""Tamper-evident, append-only local research event journal; not a distributed authority service."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sqlite3
from .gates import canonical_payload

_ALLOWED={
    None:{'CREATED'},
    'CREATED':{'HYPOTHESIS','CANCELLED'},
    'HYPOTHESIS':{'PROPOSAL','REJECTED','CANCELLED'},
    'PROPOSAL':{'POLICY_CHECK','REJECTED','CANCELLED'},
    'POLICY_CHECK':{'BUILD','REJECTED','CANCELLED'},
    'BUILD':{'STATIC_CHECK','FAILED','CANCELLED'},
    'STATIC_CHECK':{'SANDBOX_EVAL','QUARANTINED','FAILED','CANCELLED'},
    'SANDBOX_EVAL':{'STAT_REVIEW','FAILED','QUARANTINED','CANCELLED'},
    'STAT_REVIEW':{'ARCHIVED','REJECTED','CANCELLED'},
    'ARCHIVED':{'AWAIT_APPROVAL','CANCELLED'},
    'AWAIT_APPROVAL':{'CANCELLED'},
}

class ImmutableLedger:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS events (
                campaign_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL,
                PRIMARY KEY(campaign_id,sequence),
                UNIQUE(campaign_id,idempotency_key)
            );
            CREATE TRIGGER IF NOT EXISTS no_event_update BEFORE UPDATE ON events
              BEGIN SELECT RAISE(ABORT,'immutable event'); END;
            CREATE TRIGGER IF NOT EXISTS no_event_delete BEFORE DELETE ON events
              BEGIN SELECT RAISE(ABORT,'immutable event'); END;
            ''')
    def _connect(self):
        con=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        con.row_factory=sqlite3.Row
        return con
    @staticmethod
    def _digest(data):
        return hashlib.sha256(canonical_payload(data)).hexdigest()
    def append(self,campaign_id,event_type,payload,idempotency_key):
        if not campaign_id or not idempotency_key or not isinstance(payload,dict):
            raise ValueError('Invalid event identity or payload')
        if event_type=='RELEASED':
            raise ValueError('Release is outside the research ledger authority')
        payload_json=canonical_payload(payload).decode('utf-8')
        with self._connect() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT * FROM events WHERE campaign_id=? AND idempotency_key=?',(campaign_id,idempotency_key)).fetchone()
            if old:
                if old['event_type']!=event_type or old['payload_json']!=payload_json:
                    raise ValueError('Idempotency key reused for different event')
                return dict(old)
            last=c.execute('SELECT * FROM events WHERE campaign_id=? ORDER BY sequence DESC LIMIT 1',(campaign_id,)).fetchone()
            prev_type=last['event_type'] if last else None
            if event_type not in _ALLOWED.get(prev_type,set()):
                raise ValueError(f'Invalid state transition {prev_type!r} -> {event_type!r}')
            seq=last['sequence']+1 if last else 1
            previous_hash=last['event_hash'] if last else '0'*64
            data={'campaign_id':campaign_id,'sequence':seq,'event_type':event_type,'payload':payload,'idempotency_key':idempotency_key,'previous_hash':previous_hash}
            event_hash=self._digest(data)
            c.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?)',(campaign_id,seq,event_type,payload_json,idempotency_key,previous_hash,event_hash))
            return {'campaign_id':campaign_id,'sequence':seq,'event_type':event_type,'payload_json':payload_json,'idempotency_key':idempotency_key,'previous_hash':previous_hash,'event_hash':event_hash}
    def verify(self,campaign_id):
        with self._connect() as c:
            rows=c.execute('SELECT * FROM events WHERE campaign_id=? ORDER BY sequence',(campaign_id,)).fetchall()
        prev='0'*64
        for i,r in enumerate(rows,1):
            if r['sequence']!=i or r['previous_hash']!=prev:
                return False
            data={'campaign_id':r['campaign_id'],'sequence':r['sequence'],'event_type':r['event_type'],'payload':json.loads(r['payload_json']),'idempotency_key':r['idempotency_key'],'previous_hash':r['previous_hash']}
            if self._digest(data)!=r['event_hash']:
                return False
            prev=r['event_hash']
        return bool(rows)
    def history(self,campaign_id):
        with self._connect() as c:
            return [dict(r) for r in c.execute('SELECT * FROM events WHERE campaign_id=? ORDER BY sequence',(campaign_id,))]