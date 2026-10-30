"""Portable evaluation policy and deterministic corpora; no process or network adapter."""
from __future__ import annotations
import ast
import math
import random

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

