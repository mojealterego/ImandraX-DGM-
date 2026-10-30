"""Reproducible empirical engine exercise with an explicitly scripted proposer.

Reference mode dispatches only exact built-in fixture sources to trusted functions;
it never executes supplied Python. Docker mode executes the same proposed sources
through the existing networkless sandbox. Neither mode issues attestations.
"""
from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import time

from .cycle import ResearchCycle
from .engine import IntegratedEngine, MathTask
from .msc_index import build_index
from .sandbox import DockerSandbox, SandboxError, make_math_cases


def _broken(task):
    return None


def _euclidean(task):
    operation = task['operation']
    if operation == 'gcd':
        a, b = abs(task['a']), abs(task['b'])
        while b:
            a, b = b, a % b
        return a
    if operation == 'mod_pow':
        value = 1
        for _ in range(task['b']):
            value = value * task['a'] % task['mod']
        return value % task['mod']
    if operation == 'is_prime':
        n = task['n']
        divisor = 2
        while divisor * divisor <= n:
            if n % divisor == 0:
                return False
            divisor += 1
        return n >= 2
    raise ValueError('Unsupported operation')


def _binary(task):
    from math import gcd, isqrt
    operation = task['operation']
    if operation == 'gcd':
        return gcd(task['a'], task['b'])
    if operation == 'mod_pow':
        base, exponent, modulus = task['a'], task['b'], task['mod']
        value = 1
        while exponent:
            if exponent & 1:
                value = value * base % modulus
            base = base * base % modulus
            exponent >>= 1
        return value % modulus
    if operation == 'is_prime':
        n = task['n']
        return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))
    raise ValueError('Unsupported operation')


def fixture_sources():
    return {inspect.getsource(fn).replace('def ' + fn.__name__ + '(', 'def solve(', 1): fn
            for fn in (_broken, _euclidean, _binary)}


class ReferenceEvaluator:
    """Closed fixture dispatcher, deliberately not an untrusted-code sandbox."""
    def evaluate(self, content, cases, *, timeout=90):
        fn = fixture_sources().get(content)
        if fn is None:
            raise SandboxError('Reference simulation accepts built-in fixtures only')
        started = time.monotonic()
        passed = 0
        for case in cases:
            actual = fn({k: v for k, v in case.items() if k != 'expected'})
            passed += type(actual) is type(case['expected']) and actual == case['expected']
        return {'passed': passed, 'total': len(cases),
                'duration_ms': (time.monotonic() - started) * 1000,
                'execution': 'TRUSTED_FIXTURE_DISPATCH_SIMULATION'}


class ScriptedProposer:
    def __init__(self, generation):
        sources = list(fixture_sources())
        self.sources = iter((sources[0], sources[1 + generation % 2]))

    def complete_json(self, system, user):
        return {'hypothesis': 'Scripted simulation fixture; not LLM-generated improvement',
                'changes': [{'path': 'research/solver.py', 'content': next(self.sources)}]}


class OfflineResearch:
    def search(self, query):
        return []  # Existing MSC index supplies real provenance; no invented papers.


def run_simulation(*, root: Path, output: Path, generations=2,
                   backend='reference', image=None):
    if type(generations) is not int or not 1 <= generations <= 2:
        raise ValueError('Simulation budget must be 1..2 generations')
    if backend not in ('reference', 'docker'):
        raise ValueError('Unknown simulation backend')
    root, output = Path(root).resolve(), Path(output).absolute()
    if output.resolve().is_relative_to(root):
        raise ValueError('Simulation output must be outside the source repository')
    source = root / 'research/solver.py'
    baseline = source.read_bytes()
    commit = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                            check=True, capture_output=True, text=True).stdout.strip()
    evaluator = (ReferenceEvaluator() if backend == 'reference' else
                 DockerSandbox(image=image or '', worker=Path(__file__).with_name('sandbox_worker.py')))
    # Atomic reservation: existing runs are never overwritten or silently resumed.
    output.mkdir(parents=True, exist_ok=False)
    count = build_index(root/'data/msc2020_6006_coverage.csv', output/'knowledge.sqlite3')
    def engine():
        return IntegratedEngine(knowledge_db=output/'knowledge.sqlite3',
            inventory=root/'data/repositories_public_701.tsv', ledger_db=output/'ledger.sqlite3',
            review_db=output/'review.sqlite3', archive_db=output/'archive.sqlite3')
    runs = []
    for generation in range(generations):
        current = engine()  # Reload persisted genealogy between cycles.
        campaign = f'simulation-{generation}'
        directory = output/f'generation-{generation}'
        result = current.evolve(campaign_id=campaign, root=root, base_commit=commit,
            output=directory, source_refs=[('MSC2020-OFFICIAL', '00-01')],
            cycle=ResearchCycle(OfflineResearch(), ScriptedProposer(generation), evaluator))
        evaluation = json.loads((directory/'evaluation.json').read_text())
        selected = evaluation['selected']
        runs.append({'campaign': campaign, 'result': result, 'selected': selected,
                     'ledger_verified': current.ledger.verify(campaign),
                     'bad_fixture_rejected': any(r.get('regression') == 0 and r.get('heldout') == 0
                                                 for r in evaluation['candidates'])})
    current = engine()
    # Fresh empirical corpus, excluded from proposal selection; public, not sealed.
    cases = make_math_cases(seed=20261030, count=300)
    arithmetic_passed = 0
    for case in cases:
        answer = current.math(MathTask(kind='EXACT_COMPUTE', operation=case['operation'],
                            arguments={k:v for k,v in case.items() if k not in ('expected','operation')}))
        arithmetic_passed += type(answer['value']) is type(case['expected']) and answer['value'] == case['expected']
    transfer = []
    for content in list(fixture_sources())[1:]:
        try:
            transfer.append(evaluator.evaluate(content, cases))
        except SandboxError as exc:
            transfer.append({'passed': 0, 'total': len(cases), 'error': str(exc)})
    genealogy = current.research_archive.list_metadata()
    checks = {
        'math_cases': arithmetic_passed == len(cases),
        'transfer_cases': all(x['passed'] == len(cases) for x in transfer),
        'all_cycles_selected': all(r['result']['state'] == 'PROPOSED_AWAITING_USER' for r in runs),
        'bad_fixtures_rejected': all(r['bad_fixture_rejected'] for r in runs),
        'ledger_integrity': all(r['ledger_verified'] for r in runs),
        'baseline_unchanged': source.read_bytes() == baseline,
        'no_release_authority': not current.archive.list() and all(
            not current.reviews.is_authorized(r['result']['proposal_id'])
            for r in runs if 'proposal_id' in r['result']),
        'persistent_lineage': generations == 1 or any(r['depth'] > 0 for r in genealogy),
    }
    report = {'schema_version': 1, 'status': 'SIMULATION_PASS' if all(checks.values()) else 'SIMULATION_FAIL',
        'evidence_kind': 'EMPIRICAL_SIMULATION_NOT_FORMAL_PROOF', 'release_authorized': False,
        'backend': backend, 'image': image if backend == 'docker' else None,
        'base_commit': commit, 'baseline_sha256': hashlib.sha256(baseline).hexdigest(),
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_files_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root/'src/imandrax_dgm').glob('*.py'))},
        'msc_entries': count, 'scripted_proposer': True, 'external_research': False,
        'checks': checks, 'arithmetic': {'passed': arithmetic_passed, 'total': len(cases)},
        'transfer': transfer, 'runs': runs, 'genealogy': genealogy,
        'limitations': ['Finite public arithmetic corpus, not a sealed generalization benchmark',
                        'Scripted candidate pool, not autonomous learning or LLM inference',
                        'No external authority, WORM, HSM, microVM or production deployment',
                        'SHA-256 records local integrity, not independent attestation']}
    (output/'report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    hashes = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'SHA256SUMS.json').write_text(json.dumps(hashes, indent=2, sort_keys=True)+'\n')
    return report
