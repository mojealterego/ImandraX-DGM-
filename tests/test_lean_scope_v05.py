"""Proof foundation cannot be mistaken for blanket formalization."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def test_formal_library_imports_and_no_holes():
    modules=(ROOT/'proofs/ImandraX.lean').read_text()
    assert 'import ImandraX.Arithmetic' in modules
    src=(ROOT/'proofs/ImandraX/Arithmetic.lean').read_text()
    for name in ('nat_add_left_identity','nat_add_commutative',
                 'nat_mul_commutative','conjunction_associative'):
        assert f'theorem {name}' in src
    assert not re.search(r'\b(sorry|admit|axiom|unsafe)\b', '\n'.join(
        line for line in src.splitlines() if not line.lstrip().startswith(('/-', '*', '--'))))


def test_lean_build_and_pinned_upstream_matrix_present():
    workflow=(ROOT/'.github/workflows/python-ci.yml').read_text()
    assert 'leanprover/lean-action@v1' in workflow
    assert 'Reject proof holes' in workflow
    matrix=(ROOT/'.github/workflows/lean-upstream-manual.yml').read_text()
    for repo in ('mathlib4','batteries','iris-lean','mathematics_in_lean'):
        assert 'mojealterego/'+repo in matrix
