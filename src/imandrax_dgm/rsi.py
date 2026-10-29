"""Bounded RSI proposal inbox and signed *human* review authority (reference control plane).

No patch application, command execution, network calls, model invocation or deployment.
SQLite is a local prototype; the production authority must run outside the agent trust domain.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass, fields
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .gates import Candidate, EvidenceAttestation, Policy, ResearchGate, canonical_payload

REQUIRED_SUITES = frozenset({'STATIC_CHECK', 'REGRESSION', 'SECURITY', 'HELDOUT'})
ID_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')


class ApprovalRequired(ValueError):
    """The requested state transition has no valid independent human authority."""


@dataclass(frozen=True)
class ApprovalEnvelope:
    payload: dict
    signer_id: str
    signature_hex: str


def _digest(obj: dict) -> str:
    return hashlib.sha256(canonical_payload(obj)).hexdigest()


def _verify(pub: bytes | None, payload: dict, signature: str) -> bool:
    if not pub or not isinstance(payload, dict) or not isinstance(signature, str):
        return False
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(bytes.fromhex(signature), canonical_payload(payload))
        return True
    except (InvalidSignature, ValueError, TypeError, OverflowError):
        return False


class RSIReviewStore:
    """Independent reviewer-signed admission. No method in this class changes source code."""

    def __init__(self, path: Path, *, runner_keys: Mapping[str, bytes] | None = None,
                 reviewer_keys: Mapping[str, bytes] | None = None, policy: Policy | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.policy = policy or Policy.default()
        self.policy_digest = _digest(asdict(self.policy))
        self.runner_keys = dict(runner_keys or {})
        self.reviewer_keys = dict(reviewer_keys or {})
        # A runner cannot double as the independent human approver.
        if set(self.runner_keys.values()) & set(self.reviewer_keys.values()):
            raise ValueError('Runner and reviewer keys must be distinct')
        self.gate = ResearchGate(self.policy, self.runner_keys)
        with self._connect() as con:
            con.executescript('''
                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id TEXT PRIMARY KEY,
                    manifest_json TEXT NOT NULL,
                    manifest_digest TEXT NOT NULL,
                    policy_digest TEXT NOT NULL,
                    state TEXT NOT NULL CHECK (state IN ('PROPOSED','APPROVED','REJECTED'))
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    proposal_id TEXT NOT NULL,
                    suite TEXT NOT NULL,
                    signer_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    signature_hex TEXT NOT NULL,
                    PRIMARY KEY (proposal_id, suite),
                    FOREIGN KEY(proposal_id) REFERENCES proposals(proposal_id)
                );
                CREATE TABLE IF NOT EXISTS decisions (
                    proposal_id TEXT PRIMARY KEY,
                    signer_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    signature_hex TEXT NOT NULL,
                    FOREIGN KEY(proposal_id) REFERENCES proposals(proposal_id)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_digest TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_events
                    BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
                CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_events
                    BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
            ''')

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.path, timeout=10)
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
    def _audit(con: sqlite3.Connection, proposal_id: str, event_type: str, payload: dict):
        last = con.execute('SELECT event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1').fetchone()
        previous_hash = last['event_hash'] if last else '0' * 64
        event_digest = _digest(payload)
        event_hash = _digest({'proposal_id': proposal_id, 'event_type': event_type,
                              'event_digest': event_digest, 'previous_hash': previous_hash})
        con.execute('INSERT INTO audit_events(proposal_id,event_type,event_digest,previous_hash,event_hash) VALUES (?,?,?,?,?)',
                    (proposal_id, event_type, event_digest, previous_hash, event_hash))

    def verify_audit(self) -> bool:
        with self._connect() as con:
            rows = con.execute('SELECT * FROM audit_events ORDER BY sequence').fetchall()
        prev = '0' * 64
        for i, row in enumerate(rows, 1):
            if row['sequence'] != i or row['previous_hash'] != prev:
                return False
            expected = _digest({'proposal_id': row['proposal_id'], 'event_type': row['event_type'],
                                'event_digest': row['event_digest'], 'previous_hash': prev})
            if row['event_hash'] != expected:
                return False
            prev = row['event_hash']
        return bool(rows)

    def _get(self, con, proposal_id):
        row = con.execute('SELECT * FROM proposals WHERE proposal_id=?', (proposal_id,)).fetchone()
        if row is None:
            raise KeyError(proposal_id)
        manifest = json.loads(row['manifest_json'])
        if (_digest(manifest) != row['manifest_digest'] or
                row['policy_digest'] != self.policy_digest or
                manifest['policy_digest'] != self.policy_digest):
            raise ApprovalRequired('Policy or proposal manifest drift')
        return row, manifest

    def submit(self, candidate: Candidate) -> dict:
        if not isinstance(candidate.candidate_id, str) or not ID_PATTERN.fullmatch(candidate.candidate_id):
            raise ApprovalRequired('Invalid proposal ID')
        verdict = self.gate.admit(candidate)
        if not verdict.accepted:
            raise ApprovalRequired(f'Research admission denied: {verdict.reason}')
        manifest = {**asdict(candidate), 'policy_digest': self.policy_digest, 'schema_version': 1}
        digest = _digest(manifest)
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            existing = con.execute('SELECT * FROM proposals WHERE proposal_id=?', (candidate.candidate_id,)).fetchone()
            if existing:
                if existing['manifest_digest'] != digest:
                    raise ValueError('Proposal ID reused for a different immutable manifest')
                return {'proposal_id': candidate.candidate_id, 'manifest_digest': digest,
                        'base_digest': candidate.parent_digest, 'state': existing['state']}
            con.execute('INSERT INTO proposals VALUES (?,?,?,?,?)',
                        (candidate.candidate_id, canonical_payload(manifest).decode(), digest,
                         self.policy_digest, 'PROPOSED'))
            self._audit(con, candidate.candidate_id, 'PROPOSED', {'manifest_digest': digest})
        return {'proposal_id': candidate.candidate_id, 'manifest_digest': digest,
                'base_digest': candidate.parent_digest, 'state': 'PROPOSED'}

    def status(self, proposal_id: str) -> dict:
        with self._connect() as con:
            row, manifest = self._get(con, proposal_id)
            suites = {r['suite']: json.loads(r['payload_json'])['result'] for r in con.execute(
                'SELECT suite,payload_json FROM evidence WHERE proposal_id=?', (proposal_id,))}
            return {'proposal_id': proposal_id, 'state': row['state'], 'manifest_digest': row['manifest_digest'],
                    'policy_digest': self.policy_digest, 'suites': suites, 'required_suites': sorted(REQUIRED_SUITES)}

    def details(self, proposal_id: str) -> dict:
        """Full human-review manifest; hash alone is not sufficient for approval."""
        with self._connect() as con:
            row, manifest = self._get(con, proposal_id)
            return {'proposal_id': proposal_id, 'state': row['state'],
                    'manifest_digest': row['manifest_digest'], 'manifest': manifest}

    def review_packet(self, proposal_id: str) -> dict:
        with self._connect() as con:
            row, manifest = self._get(con, proposal_id)
            return {'proposal_id': proposal_id, 'manifest_digest': row['manifest_digest'],
                    'policy_digest': self.policy_digest, 'base_digest': manifest['parent_digest'],
                    'patch_digest': manifest['patch_digest']}

    def record_evidence(self, proposal_id: str, attestation: EvidenceAttestation) -> None:
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            row, manifest = self._get(con, proposal_id)
            if row['state'] != 'PROPOSED':
                raise ApprovalRequired('Proposal already reviewed')
            if not self.gate.verify_attestation(attestation):
                raise ApprovalRequired('Untrusted or invalid runner signature')
            payload = attestation.payload
            if (payload['suite'] not in REQUIRED_SUITES or
                    payload['candidate_digest'] != row['manifest_digest'] or
                    payload['source_digest'] != manifest['parent_digest']):
                raise ApprovalRequired('Attestation not bound to exact proposal and source')
            old = con.execute('SELECT * FROM evidence WHERE proposal_id=? AND suite=?',
                              (proposal_id, payload['suite'])).fetchone()
            encoded = canonical_payload(payload).decode()
            if old:
                if old['payload_json'] != encoded or old['signature_hex'] != attestation.signature_hex or old['signer_id'] != attestation.signer_id:
                    raise ApprovalRequired('Evidence is immutable; conflicting resubmission denied')
                return
            con.execute('INSERT INTO evidence VALUES (?,?,?,?,?)',
                        (proposal_id, payload['suite'], attestation.signer_id, encoded, attestation.signature_hex))
            self._audit(con, proposal_id, 'EVIDENCE', {'suite': payload['suite'], 'digest': _digest(payload)})

    def _evidence_passes(self, con, proposal_id, row, manifest):
        results = con.execute('SELECT * FROM evidence WHERE proposal_id=?', (proposal_id,)).fetchall()
        if {r['suite'] for r in results} != REQUIRED_SUITES:
            return False
        for r in results:
            payload = json.loads(r['payload_json'])
            att = EvidenceAttestation(payload, r['signer_id'], r['signature_hex'])
            if (not self.gate.verify_attestation(att) or payload['suite'] != r['suite'] or
                    payload['candidate_digest'] != row['manifest_digest'] or
                    payload['source_digest'] != manifest['parent_digest'] or payload['result'] != 'PASS'):
                return False
        return True

    def decide(self, envelope: ApprovalEnvelope, *, now: int | None = None) -> str:
        if not isinstance(envelope.payload, dict):
            raise ApprovalRequired('Invalid review envelope')
        payload = envelope.payload
        proposal_id = payload.get('proposal_id')
        if not isinstance(proposal_id, str):
            raise ApprovalRequired('Missing proposal ID')
        with self._connect() as con:
            con.execute('BEGIN IMMEDIATE')
            row, manifest = self._get(con, proposal_id)
            if row['state'] != 'PROPOSED':
                raise ApprovalRequired('Decision already final')
            packet = {'proposal_id': proposal_id, 'manifest_digest': row['manifest_digest'],
                      'policy_digest': self.policy_digest, 'base_digest': manifest['parent_digest'],
                      'patch_digest': manifest['patch_digest']}
            if (set(payload) != set(packet) | {'decision', 'reviewer_id', 'expires_at'} or
                    any(payload.get(k) != v for k, v in packet.items()) or
                    payload.get('decision') not in ('APPROVE', 'REJECT') or
                    payload.get('reviewer_id') != envelope.signer_id or
                    type(payload.get('expires_at')) is not int or
                    payload['expires_at'] <= (int(time.time()) if now is None else now) or
                    not _verify(self.reviewer_keys.get(envelope.signer_id), payload, envelope.signature_hex)):
                raise ApprovalRequired('Invalid, expired or untrusted human decision')
            if payload['decision'] == 'APPROVE' and not self._evidence_passes(con, proposal_id, row, manifest):
                raise ApprovalRequired('Required independent PASS evidence missing')
            state = 'APPROVED' if payload['decision'] == 'APPROVE' else 'REJECTED'
            con.execute('INSERT INTO decisions VALUES (?,?,?,?)',
                        (proposal_id, envelope.signer_id, canonical_payload(payload).decode(), envelope.signature_hex))
            con.execute('UPDATE proposals SET state=? WHERE proposal_id=?', (state, proposal_id))
            self._audit(con, proposal_id, state, {'reviewer_id': envelope.signer_id, 'decision_digest': _digest(payload)})
            return state

    def is_authorized(self, proposal_id: str, *, now: int | None = None) -> bool:
        try:
            with self._connect() as con:
                row, manifest = self._get(con, proposal_id)
                if row['state'] != 'APPROVED':
                    return False
                if not self._evidence_passes(con, proposal_id, row, manifest):
                    return False
                decision = con.execute('SELECT * FROM decisions WHERE proposal_id=?', (proposal_id,)).fetchone()
                if not decision:
                    return False
                payload = json.loads(decision['payload_json'])
                expected = self.review_packet(proposal_id)
                if (payload.get('decision') != 'APPROVE' or
                        payload.get('reviewer_id') != decision['signer_id'] or
                        any(payload.get(k) != v for k, v in expected.items()) or
                        type(payload.get('expires_at')) is not int or
                        payload['expires_at'] <= (int(time.time()) if now is None else now)):
                    return False
                return _verify(self.reviewer_keys.get(decision['signer_id']), payload, decision['signature_hex'])
        except (KeyError, ApprovalRequired, ValueError, sqlite3.DatabaseError):
            return False


class RSIInbox:
    """Read-only queue scanner for agent-proposed candidates; never applies patches."""

    def __init__(self, store: RSIReviewStore, inbox: Path):
        self.store = store
        self.inbox = Path(inbox)

    def tick(self, max_items: int = 32) -> dict:
        if not 1 <= max_items <= 256:
            raise ValueError('Invalid tick budget')
        submitted = 0
        rejected = 0
        for path in sorted(self.inbox.glob('*.json'))[:max_items]:
            try:
                if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
                    raise ValueError('Unsafe inbox file')
                raw = json.loads(path.read_text(encoding='utf-8'))
                if not isinstance(raw, dict) or set(raw) != {f.name for f in fields(Candidate)}:
                    raise ValueError('Invalid candidate schema')
                if not isinstance(raw['paths'], list):
                    raise ValueError('Invalid paths')
                raw['paths'] = tuple(raw['paths'])
                candidate = Candidate(**raw)
                with self.store._connect() as con:
                    existing = con.execute('SELECT proposal_id FROM proposals WHERE proposal_id=?',
                                           (candidate.candidate_id,)).fetchone()
                if existing:
                    # Check idempotency / detect ID collision.
                    self.store.submit(candidate)
                    continue
                self.store.submit(candidate)
                submitted += 1
            except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                rejected += 1
        return {'submitted': submitted, 'rejected': rejected, 'mode': 'PROPOSE_ONLY_NO_EXECUTION'}