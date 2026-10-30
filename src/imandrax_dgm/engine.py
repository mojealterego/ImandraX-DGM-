"""Single ImandraX/DGM/RSI facade: mathematical evidence + bounded evolution.

The trusted authority is external. This facade can retrieve, compute, propose,
register and archive *independently approved* variants. It cannot approve or
apply its own patches, deploy itself, or claim an unchecked formal theorem.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import difflib
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Mapping

from .formal_verification import FormalEvidenceRegistry, FormalVerificationError
from .evolution import ApprovedArchive
from .research_archive import ResearchArchive
from .gates import Candidate, Policy, canonical_payload
from .knowledge import KnowledgeIndex
from .rsi import RSIReviewStore
from .unified import UnifiedResearchEngine

_SHA40 = re.compile(r'^[0-9a-f]{40}$')
_SHA256 = re.compile(r'^[0-9a-f]{64}$')
_ARTIFACT_NAMES = frozenset({'proposal.json', 'changes.json', 'evaluation.json',
                             'cycle_status.json', 'research.json'})


class ArtifactError(ValueError):
    """Candidate artifacts are stale, altered, or outside their trust contract."""


@dataclass(frozen=True)
class MathTask:
    kind: str
    source: str | None = None
    code: str | None = None
    statement: str = ''
    operation: str | None = None
    arguments: dict = field(default_factory=dict)


class IntegratedEngine:
    """One product API, separate trust domains for source, runner and human."""

    def __init__(self, *, knowledge_db: Path, inventory: Path, ledger_db: Path,
                 review_db: Path, archive_db: Path, policy: Policy | None = None,
                 formal_registry_db: Path | None = None,
                 runner_keys: Mapping[str, bytes] | None = None,
                 reviewer_keys: Mapping[str, bytes] | None = None):
        self.policy = policy or Policy.default()
        self.formal = FormalEvidenceRegistry(formal_registry_db or Path(archive_db).with_name("formal_proofs.sqlite3"))
        self.research = UnifiedResearchEngine(knowledge_db, inventory, ledger_db, self.policy)
        self.knowledge = self.research.knowledge
        self.catalog = self.research.catalog
        self.ledger = self.research.ledger
        self.reviews = RSIReviewStore(review_db, policy=self.policy,
                                      runner_keys=runner_keys, reviewer_keys=reviewer_keys)
        self.archive = ApprovedArchive(archive_db, authorize=self.reviews.is_authorized)
        self.research_archive = ResearchArchive(Path(archive_db).with_name("research_generations.sqlite3"))

        # Shared cognition is loaded on demand; it does not change the
        # signed APEX manifest or grant RSI an approval/merge capability.
        self._cognitive_memory_db = Path(archive_db).with_name("cognitive_memory.sqlite3")
        self._cognitive_memory = None

    @property
    def memory(self):
        """The same persistent bitemporal store as the operator CLI."""
        if self._cognitive_memory is None:
            from .cognitive_memory import BitemporalGraphMemory
            self._cognitive_memory = BitemporalGraphMemory(self._cognitive_memory_db)
        return self._cognitive_memory

    @property
    def cognition(self):
        """Advisory decision/reflection over this engine's local memory."""
        from .cognition import CognitiveDecisionCycle
        return CognitiveDecisionCycle(self.memory)

    @staticmethod
    def _bounded_integer(value: object) -> int:
        if type(value) is not int or value.bit_length() > 256:
            raise ValueError('Only bounded 256-bit integers are supported')
        return value

    def math(self, task: MathTask) -> dict:
        if not isinstance(task, MathTask):
            raise TypeError('Expected typed MathTask')
        if task.kind == 'LOOKUP':
            if not task.source or not task.code:
                raise ValueError('Source and MSC code required')
            rows = self.knowledge.exact(task.code, task.source)
            return {'status': 'SOURCE_INDEXED' if rows else 'NOT_FOUND',
                    'proof_status': 'NOT_PROVED', 'entries': rows,
                    'provenance': {'source': task.source, 'code': task.code,
                                   'authority': 'SOURCE_REFERENCE_ONLY'}}
        if task.kind == 'FORMAL_THEOREM':
            if not isinstance(task.statement, str) or not task.statement.strip():
                raise ValueError('Formal theorem requires a statement')
            if not task.source or not task.code:
                raise ValueError('Source reference required')
            rows = self.knowledge.exact(task.code, task.source)
            return {'status': 'PROOF_NOT_CHECKED', 'proof_status': 'NOT_PROVED',
                    'statement': task.statement, 'source_found': bool(rows),
                    'checker': 'NO_INDEPENDENT_KERNEL_ATTESTATION',
                    'note': 'A source entry or a generated proof is not kernel verification'}
        if task.kind == 'FORMAL_PROOF_STATUS':
            if not isinstance(task.statement, str) or not task.statement.strip():
                raise ValueError('Named Lean declaration required')
            try:
                record = self.formal.get(task.statement)
            except FormalVerificationError as exc:
                raise ValueError('Unknown formally registered declaration') from exc
            return {**record, 'proof_status': ('EXTERNALLY_CHECKED' if record['status'] == 'EXTERNALLY_CHECKED' else 'NOT_PROVED'),
                    'scope': 'DECLARATION_ONLY_NOT_ENTIRE_MSC_CATEGORY',
                    'note': 'Status is a signed checker attestation, not a claim about an arbitrary natural-language statement'}
        if task.kind == 'EXACT_COMPUTE':
            args = task.arguments
            if not isinstance(args, dict):
                raise ValueError('Arguments must be an object')
            if task.operation == 'gcd' and set(args) == {'a','b'}:
                a, b = (self._bounded_integer(args[k]) for k in ('a','b'))
                value = math.gcd(a,b)
            elif task.operation == 'mod_pow' and set(args) == {'a','b','mod'}:
                a, b, mod = (self._bounded_integer(args[k]) for k in ('a','b','mod'))
                if b < 0 or mod < 2 or b > 100_000:
                    raise ValueError('Invalid exponent/modulus budget')
                value = pow(a,b,mod)
            elif task.operation == 'is_prime' and set(args) == {'n'}:
                n = self._bounded_integer(args['n'])
                if n < 0 or n > 1_000_000:
                    raise ValueError('Primality exact-check range exceeded')
                value = n >= 2 and all(n % d for d in range(2,math.isqrt(n)+1))
            else:
                raise ValueError('Unsupported exact operation or arguments')
            return {'status': 'COMPUTED_EXACT', 'proof_status': 'NOT_FORMALLY_PROVED',
                    'operation': task.operation, 'value': value,
                    'method': 'DETERMINISTIC_PYTHON_ARITHMETIC',
                    'scope': 'BOUNDED_INPUTS_ONLY'}
        raise ValueError('Unknown task kind; no speculative result')

    def _validated_sources(self, refs: list[tuple[str,str]]) -> list[dict]:
        if not isinstance(refs, list) or not 1 <= len(refs) <= 12:
            raise ValueError('1..12 verified mathematical references required')
        context = []
        for ref in refs:
            if not isinstance(ref, (tuple,list)) or len(ref) != 2:
                raise ValueError('Malformed mathematical source reference')
            source, code = ref
            rows = self.knowledge.exact(code, source)
            if not rows:
                raise ValueError('Mathematical reference not in source index')
            row = rows[0]
            context.append({'provider':'IMANDRAX_INDEX', 'source':source, 'code':code,
                            'title':row['title'], 'excerpt':row.get('body','')[:300] if 'body' in row else '',
                            'proof_status':'SOURCE_REFERENCE_ONLY'})
        return context

    @staticmethod
    def _load_artifacts(output: Path) -> dict:
        output = Path(output)
        if output.is_symlink() or not output.is_dir():
            raise ArtifactError('Artifact directory is missing or a symlink')
        checksum_file = output/'SHA256SUMS.json'
        if checksum_file.is_symlink() or not checksum_file.is_file():
            raise ArtifactError('Missing artifact checksum manifest')
        try:
            manifest = json.loads(checksum_file.read_text(encoding='utf-8'))
            if not isinstance(manifest,dict) or set(manifest) != _ARTIFACT_NAMES:
                raise ArtifactError('Unexpected artifact manifest')
            result = {}
            for name in sorted(_ARTIFACT_NAMES):
                file = output/name
                if file.is_symlink() or not file.is_file() or file.stat().st_size > 1_000_000:
                    raise ArtifactError('Invalid candidate artifact')
                raw = file.read_bytes()
                if not isinstance(manifest[name],str) or not _SHA256.fullmatch(manifest[name]):
                    raise ArtifactError('Invalid artifact digest')
                if hashlib.sha256(raw).hexdigest() != manifest[name]:
                    raise ArtifactError('Artifact checksum mismatch')
                result[name] = json.loads(raw)
            return result
        except (UnicodeDecodeError, json.JSONDecodeError, OSError) as exc:
            raise ArtifactError('Invalid artifact encoding') from exc

    def register_review_artifacts(self, root: Path, base_commit: str, output: Path) -> Candidate:
        """Bind generated source, patch, tests and manifest; register as PROPOSED only."""
        if not isinstance(base_commit,str) or not _SHA40.fullmatch(base_commit):
            raise ArtifactError('Expected pinned base Git SHA')
        data = self._load_artifacts(output)
        proposal, changes, evaluation, status = (data[k] for k in
            ('proposal.json','changes.json','evaluation.json','cycle_status.json'))
        if not all(isinstance(x,dict) for x in (proposal,changes,evaluation,status)):
            raise ArtifactError('Malformed review artifacts')
        if (status.get('state') != 'AWAITING_HUMAN_REVIEW' or
                status.get('no_automatic_apply') is not True or
                status.get('no_automatic_merge') is not True or
                proposal.get('state') != 'PROPOSED_NOT_APPROVED' or
                proposal.get('base_commit') != base_commit):
            raise ArtifactError('Untrusted cycle status or base commit')
        if set(changes) != {'research/solver.py'} or not isinstance(changes['research/solver.py'],str):
            raise ArtifactError('Only research solver proposals are supported')
        try:
            obj = proposal['candidate']
            candidate = Candidate(**{**obj, 'paths': tuple(obj['paths'])})
        except (TypeError, KeyError, ValueError) as exc:
            raise ArtifactError('Invalid candidate schema') from exc
        if tuple(candidate.paths) != ('research/solver.py',):
            raise ArtifactError('Protected code change attempted')
        source = Path(root)/'research'/'solver.py'
        if source.is_symlink() or source.parent.is_symlink() or not source.is_file():
            raise ArtifactError('Untrusted baseline source')
        baseline = source.read_bytes()
        if len(baseline) > 160_000 or not isinstance(proposal.get('baseline_sha256'),str):
            raise ArtifactError('Invalid source size or baseline digest')
        baseline_sha = hashlib.sha256(baseline).hexdigest()
        if baseline_sha != proposal['baseline_sha256']:
            raise ArtifactError('Source drift detected')
        parent = hashlib.sha256(canonical_payload({'commit':base_commit,'source_sha256':baseline_sha})).hexdigest()
        if candidate.parent_digest != parent:
            raise ArtifactError('Candidate not bound to base source')
        try:
            old = baseline.decode('utf-8')
            patch = ''.join(difflib.unified_diff(old.splitlines(keepends=True),
                changes['research/solver.py'].splitlines(keepends=True),
                fromfile='a/research/solver.py',tofile='b/research/solver.py'))
        except UnicodeDecodeError as exc:
            raise ArtifactError('Source is not UTF-8') from exc
        if (not patch or patch != proposal.get('patch') or
                hashlib.sha256(patch.encode()).hexdigest() != candidate.patch_digest):
            raise ArtifactError('Patch/source binding mismatch')
        if not isinstance(evaluation.get('selected'),dict) or not isinstance(evaluation.get('candidates'),list):
            raise ArtifactError('Missing independent selection record')
        selected = evaluation['selected']
        matching = [r for r in evaluation['candidates'] if isinstance(r,dict) and r.get('id')==candidate.candidate_id]
        if (selected.get('id') != candidate.candidate_id or
                status.get('selected_candidate') != candidate.candidate_id or
                len(matching) != 1 or matching[0].get('status') != 'EVALUATED_UNATTESTED' or
                selected.get('status') != 'EVALUATED_UNATTESTED'):
            raise ArtifactError('Selected candidate does not match evaluation')
        lineage = proposal.get('research_lineage')
        if lineage is not None:
            if (not isinstance(lineage,dict) or
                    set(lineage) != {'parent_id','depth','parent_source_sha256'} or
                    type(lineage['depth']) is not int or not 0 <= lineage['depth'] <= 12 or
                    (lineage['parent_id'] is None) != (lineage['depth'] == 0) or
                    (lineage['parent_source_sha256'] is None) != (lineage['depth'] == 0)):
                raise ArtifactError('Malformed research lineage')
            if lineage['depth']:
                if (not isinstance(lineage['parent_id'],str) or
                        not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}',lineage['parent_id']) or
                        not isinstance(lineage['parent_source_sha256'],str) or
                        not _SHA256.fullmatch(lineage['parent_source_sha256'])):
                    raise ArtifactError('Invalid research parent digest')
            for record in (selected, matching[0]):
                if (record.get('research_parent_id') != lineage['parent_id'] or
                        record.get('research_depth') != lineage['depth']):
                    raise ArtifactError('Research lineage and evaluation mismatch')
        for record in (selected, matching[0]):
            for field in ('regression','heldout'):
                val=record.get(field)
                if type(val) not in (int,float) or not math.isfinite(val) or not .9 <= val <= 1:
                    raise ArtifactError('Insufficient or invalid evaluation result')
        # This is unsigned local research evidence, NOT a signed evaluation suite.
        self.reviews.submit(candidate)
        return candidate

    def evolve(self, *, campaign_id: str, root: Path, base_commit: str,
               output: Path, source_refs: list[tuple[str,str]], cycle) -> dict:
        """Math grounding -> DGM proposal/test -> RSI human review, never self-approval."""
        context = self._validated_sources(source_refs)  # Reject before any LLM call.
        if not isinstance(campaign_id,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}',campaign_id):
            raise ValueError('Invalid campaign identifier')
        if not _SHA40.fullmatch(base_commit):
            raise ValueError('Expected pinned Git commit')
        self.research.open_campaign(campaign_id,self.policy.max_tokens)
        result = cycle.run(root,base_commit,output,mathematical_context=context,
                           research_archive=self.research_archive)
        if result.get('state') != 'AWAITING_HUMAN_REVIEW':
            self.ledger.append(campaign_id,'CANCELLED',{'reason':'NO_ADMISSIBLE_CANDIDATE'},campaign_id+':cancel')
            return {'state':'NO_ADMISSIBLE_CANDIDATE','proof_status':'NOT_PROVED','approval':'NOT_REQUESTED'}
        candidate = self.register_review_artifacts(root,base_commit,output)
        admitted = self.research.propose(campaign_id,candidate,source_refs)
        if not admitted['admitted']:
            raise ArtifactError('Mathematical research gate denied candidate')
        self.ledger.append(campaign_id,'BUILD',{'scope':'EPHEMERAL_SANDBOX_ONLY'},campaign_id+':build')
        self.ledger.append(campaign_id,'STATIC_CHECK',{'result':'LOCAL_UNATTESTED'},campaign_id+':static')
        self.ledger.append(campaign_id,'SANDBOX_EVAL',{'result':'LOCAL_UNATTESTED'},campaign_id+':sandbox')
        self.ledger.append(campaign_id,'STAT_REVIEW',{'result':'LOCAL_UNATTESTED'},campaign_id+':stat')
        return {'state':'PROPOSED_AWAITING_USER','proposal_id':candidate.candidate_id,
                'proof_status':'NOT_PROVED','approval':'REQUIRED_SIGNED_USER_DECISION',
                'auto_apply':False,'auto_merge':False,'evidence':'UNATTESTED_RESEARCH_ONLY'}

    def archive_approved(self, proposal_id: str, *, score: float, transfer_score: float,
                         parent_id: str | None = None) -> dict:
        """Only externally signed, still-valid approvals can enter the DGM parent pool."""
        if not self.reviews.is_authorized(proposal_id):
            raise PermissionError('Independent human approval is required')
        return self.archive.add(proposal_id,parent_id=parent_id,score=score,transfer_score=transfer_score)
