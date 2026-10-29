"""Docker-only, no-network evaluation boundary for untrusted generated Python.

This is a CONTAINER isolation prototype, NOT a Firecracker/microVM security claim.
The Docker daemon is a privileged dependency. Do not run against a hostile shared host.
"""
from __future__ import annotations
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
import uuid
from typing import Callable


class SandboxError(RuntimeError):
    pass


_ALLOWED_IMPORTS = {'math', 'functools', 'itertools', 'collections', 'fractions',
                    'decimal', 'typing', 'statistics', 'heapq', 'bisect', 'operator'}
_FORBIDDEN_NAMES = {'eval','exec','compile','open','input','__import__','getattr','setattr',
                    'delattr','globals','locals','vars','breakpoint','exit','quit'}


def static_security_check(source: str) -> dict:
    """Defence-in-depth lint, never a substitute for an isolated runtime."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {'pass': False, 'reason': 'SYNTAX_ERROR', 'line': exc.lineno}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = [x.name.split('.')[0] for x in node.names] if isinstance(node, ast.Import) else [(node.module or '').split('.')[0]]
            if any(x not in _ALLOWED_IMPORTS for x in modules) or (isinstance(node, ast.ImportFrom) and node.level):
                return {'pass': False, 'reason': 'DISALLOWED_IMPORT'}
        if isinstance(node, ast.Name) and node.id in _FORBIDDEN_NAMES:
            return {'pass': False, 'reason': 'DISALLOWED_BUILTIN'}
        if isinstance(node, ast.Attribute) and node.attr.startswith('__'):
            return {'pass': False, 'reason': 'DUNDER_ACCESS'}
    if not any(isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name == 'solve' for x in tree.body):
        return {'pass': False, 'reason': 'MISSING_SOLVE'}
    return {'pass': True, 'reason': 'STATIC_POLICY_PASS'}


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def make_math_cases(*, seed: int, count: int) -> list[dict]:
    if not 3 <= count <= 500:
        raise ValueError('Invalid evaluation case count')
    rng = random.Random(seed)
    cases = []
    for i in range(count):
        kind = ('gcd', 'mod_pow', 'is_prime')[i % 3]
        if kind == 'gcd':
            a, b = rng.randint(-100000, 100000), rng.randint(-100000, 100000)
            cases.append({'operation': kind, 'a': a, 'b': b, 'expected': math.gcd(a, b)})
        elif kind == 'mod_pow':
            a, b, mod = rng.randint(-500, 500), rng.randint(0, 150), rng.randint(2, 2000)
            cases.append({'operation': kind, 'a': a, 'b': b, 'mod': mod, 'expected': pow(a, b, mod)})
        else:
            n = rng.randint(0, 20000)
            cases.append({'operation': kind, 'n': n, 'expected': _is_prime(n)})
    return cases


class DockerSandbox:
    def __init__(self, *, image: str, worker: Path, allow_unpinned_for_ci: bool = False,
                 run: Callable = subprocess.run):
        if not re.fullmatch(r'[A-Za-z0-9._/:@-]{1,220}', image):
            raise SandboxError('Invalid image identifier')
        if not allow_unpinned_for_ci and not re.search(r'@sha256:[0-9a-f]{64}$', image):
            raise SandboxError('Production evaluation requires immutable image digest')
        self.image = image
        self.worker = Path(worker).resolve()
        self.run = run

    def command(self, input_dir: Path, name: str) -> list[str]:
        if not re.fullmatch(r'[a-z0-9-]{1,63}', name):
            raise SandboxError('Invalid container name')
        return ['docker','run','--rm','--name',name,
                '--network','none','--read-only','--cap-drop','ALL',
                '--security-opt','no-new-privileges','--pids-limit','64',
                '--memory','512m','--cpus','1','--user','65534:65534',
                '--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
                '--mount',f'type=bind,src={Path(input_dir).resolve()},dst=/input,readonly',
                '--mount',f'type=bind,src={self.worker},dst=/trusted/worker.py,readonly',
                self.image,'python','-I','-B','/trusted/worker.py','/input/solver.py','/input/cases.json']

    def evaluate(self, content: str, cases: list[dict], *, timeout: int = 60) -> dict:
        if not isinstance(content, str) or len(content.encode()) > 160_000 or not 1 <= timeout <= 120:
            raise SandboxError('Candidate exceeds execution budget')
        if not isinstance(cases, list) or len(cases) > 500:
            raise SandboxError('Invalid case corpus')
        if not self.worker.is_file():
            raise SandboxError('Trusted worker is missing')
        name = 'rsi-' + uuid.uuid4().hex[:16]
        with tempfile.TemporaryDirectory(prefix='imandrax-sandbox-') as temp:
            directory = Path(temp)
            (directory/'solver.py').write_text(content, encoding='utf-8')
            (directory/'cases.json').write_text(json.dumps(cases, ensure_ascii=False), encoding='utf-8')
            directory.chmod(0o755)
            (directory/'solver.py').chmod(0o644)
            (directory/'cases.json').chmod(0o644)
            cmd = self.command(directory, name)
            try:
                proc = self.run(cmd, timeout=timeout, text=True, capture_output=True,
                                shell=False, env={'PATH':'/usr/bin:/bin'})
            except subprocess.TimeoutExpired as exc:
                try:
                    self.run(['docker','rm','-f',name],timeout=10,text=True,capture_output=True,
                             shell=False,env={'PATH':'/usr/bin:/bin'})
                except (OSError, subprocess.SubprocessError):
                    pass
                raise SandboxError('Candidate timed out and container cleanup requested') from exc
            except OSError as exc:
                raise SandboxError('Docker runtime unavailable') from exc
            if proc.returncode != 0 or len(proc.stdout) > 16384:
                raise SandboxError(f'Candidate container failed (exit={proc.returncode})')
            try:
                result = json.loads(proc.stdout)
                if not (type(result.get('passed')) is int and type(result.get('total')) is int and
                        result['total'] == len(cases) and 0 <= result['passed'] <= result['total'] and
                        type(result.get('duration_ms')) in (int, float)):
                    raise ValueError('Invalid result')
            except (ValueError, TypeError, AttributeError) as exc:
                raise SandboxError('Malformed evaluator output') from exc
            return result