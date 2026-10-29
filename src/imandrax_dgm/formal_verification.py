"""Proof provenance and externally signed checker evidence; NEVER proves a theorem itself.

An MSC classification code is a subject tag, not a theorem. No evidence is accepted
unless an independent runner signs the exact source hash, commit and checker verdict.
The signing key must be provisioned out of band. The user still controls releases.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .gates import canonical_payload

_SHA256 = re.compile(r'^[a-f0-9]{64}$')
_SHA40 = re.compile(r'^[a-f0-9]{40}$')
_MSC = re.compile(r'^(?:[0-9]{2}-[0-9A-Z]{2}|[0-9]{2}[A-Z][0-9]{2})$')
_NAME = re.compile(r'^[A-Za-z_][A-Za-z_0-9.]*$')
_PROOF_HOLE = re.compile(r'(?<![\w])(sorry|admit|axiom|unsafe)(?![\w])')
_ALLOWED_CHECKERS = frozenset({'nanoda', 'lean4lean', 'con-leche', 'con-ron'})


class FormalVerificationError(ValueError):
    """Untrusted, incomplete or stale formal proof evidence."""


@dataclass(frozen=True)
class ProofSpec:
    declaration: str
    msc_code: str
    module: str
    source_path: str
    source_sha256: str


@dataclass(frozen=True)
class ProofEvidence:
    declaration: str
    source_sha256: str
    toolchain: str
    base_commit: str
    kernel: str
    independent: str
    checker: str
    runner: str
    workflow_run: str


def validate_proof_sources(spec: ProofSpec, source_root: Path) -> bool:
    if not isinstance(spec, ProofSpec) or not _NAME.fullmatch(spec.declaration) or not _NAME.fullmatch(spec.module):
        raise FormalVerificationError('Invalid declaration or module')
    if not _MSC.fullmatch(spec.msc_code) or not _SHA256.fullmatch(spec.source_sha256):
        raise FormalVerificationError('Invalid MSC code or digest')
    raw = spec.source_path
    if not isinstance(raw, str) or not raw or raw.startswith('/') or '\\' in raw or '\x00' in raw:
        raise FormalVerificationError('Invalid source path')
    parts = raw.split('/')
    if any(part in ('', '.', '..') for part in parts) or not raw.endswith('.lean'):
        raise FormalVerificationError('Invalid source path')
    root = Path(source_root).resolve(strict=True)
    candidate = root.joinpath(*parts)
    if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 256_000:
        raise FormalVerificationError('Missing or untrusted Lean source')
    real = candidate.resolve(strict=True)
    if not real.is_relative_to(root) or any(p.is_symlink() for p in [root.joinpath(*parts[:i]) for i in range(1, len(parts))]):
        raise FormalVerificationError('Symlink or path escape')
    data = real.read_bytes()
    if hashlib.sha256(data).hexdigest() != spec.source_sha256:
        raise FormalVerificationError('Source SHA mismatch')
    try:
        content = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise FormalVerificationError('Non-UTF8 Lean source') from exc
    # Defense-in-depth: actual acceptance is by external kernels, not this lexical check.
    without_comments = re.sub(r'/\-.*?\-/', '', content, flags=re.S)
    without_comments = re.sub(r'--[^\n]*', '', without_comments)
    if _PROOF_HOLE.search(without_comments):
        raise FormalVerificationError('Potential proof hole or unsafe declaration')
    return True


class FormalEvidenceRegistry:
    """Append-only SQLite proof evidence; local DB owner is outside the threat model."""

    def __init__(self, database: Path, *, trusted_runner_keys: Mapping[str, bytes] | None = None):
        self.path = Path(database)
        self.trusted_runner_keys = dict(trusted_runner_keys or {})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS proof_spec (
                  declaration TEXT PRIMARY KEY, msc_code TEXT NOT NULL,
                  module TEXT NOT NULL, source_path TEXT NOT NULL,
                  source_sha256 TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'UNVERIFIED');
                CREATE TABLE IF NOT EXISTS evidence (
                  declaration TEXT PRIMARY KEY REFERENCES proof_spec(declaration),
                  evidence_json TEXT NOT NULL, runner TEXT NOT NULL, signature_hex TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS no_evidence_update BEFORE UPDATE ON evidence
                  BEGIN SELECT RAISE(ABORT, 'evidence immutable'); END;
                CREATE TRIGGER IF NOT EXISTS no_evidence_delete BEFORE DELETE ON evidence
                  BEGIN SELECT RAISE(ABORT, 'evidence immutable'); END;
            ''')

    def _db(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.execute('PRAGMA foreign_keys=ON')
        return conn

    def register(self, spec: ProofSpec, *, source_root: Path) -> dict:
        validate_proof_sources(spec, source_root)
        with self._db() as conn:
            row = conn.execute('SELECT * FROM proof_spec WHERE declaration=?', (spec.declaration,)).fetchone()
            if row:
                if row[1:5] != (spec.msc_code, spec.module, spec.source_path, spec.source_sha256):
                    raise FormalVerificationError('Declaration changed; new version required')
            else:
                conn.execute('INSERT INTO proof_spec (declaration,msc_code,module,source_path,source_sha256) VALUES (?,?,?,?,?)',
                             (spec.declaration, spec.msc_code, spec.module, spec.source_path, spec.source_sha256))
        return self.get(spec.declaration)

    def get(self, declaration: str) -> dict:
        with self._db() as conn:
            row = conn.execute('SELECT declaration,msc_code,module,source_path,source_sha256,status FROM proof_spec WHERE declaration=?', (declaration,)).fetchone()
        if row is None:
            raise FormalVerificationError('Unknown declaration')
        return dict(zip(('declaration','msc_code','module','source_path','source_sha256','status'), row))

    def msc_coverage(self, msc_code: str) -> dict:
        with self._db() as conn:
            total, checked = conn.execute('SELECT COUNT(*),SUM(CASE WHEN status=? THEN 1 ELSE 0 END) FROM proof_spec WHERE msc_code=?',
                ('EXTERNALLY_CHECKED', msc_code)).fetchone()
        return {'total': total, 'verified': checked or 0}

    def verify(self, evidence: ProofEvidence, *, signer_id: str = '', signature_hex: str = '') -> dict:
        if not isinstance(evidence, ProofEvidence):
            raise FormalVerificationError('Invalid evidence object')
        registered = self.get(evidence.declaration)
        if evidence.source_sha256 != registered['source_sha256']:
            raise FormalVerificationError('Source digest mismatch')
        if (not _SHA40.fullmatch(evidence.base_commit) or not evidence.toolchain.startswith('leanprover/lean4:v4.')
                or evidence.kernel != 'PASS' or evidence.independent != 'PASS'
                or evidence.checker not in _ALLOWED_CHECKERS
                or not evidence.runner or not evidence.workflow_run.startswith('https://github.com/mojealterego/ImandraX-DGM-/actions/runs/')):
            raise FormalVerificationError('Incomplete checker attestation')
        key = self.trusted_runner_keys.get(signer_id)
        if not key or signer_id != evidence.runner or not signature_hex:
            raise FormalVerificationError('Missing signed external runner attestation')
        try:
            Ed25519PublicKey.from_public_bytes(key).verify(bytes.fromhex(signature_hex), canonical_payload(asdict(evidence)))
        except (InvalidSignature, TypeError, ValueError) as exc:
            raise FormalVerificationError('Invalid external signature') from exc
        with self._db() as conn:
            if conn.execute('SELECT 1 FROM evidence WHERE declaration=?', (evidence.declaration,)).fetchone():
                raise FormalVerificationError('Evidence already sealed')
            conn.execute('INSERT INTO evidence VALUES (?,?,?,?)',
                (evidence.declaration, json.dumps(asdict(evidence), sort_keys=True), signer_id, signature_hex))
            conn.execute('UPDATE proof_spec SET status=? WHERE declaration=?', ('EXTERNALLY_CHECKED', evidence.declaration))
        return self.get(evidence.declaration)
