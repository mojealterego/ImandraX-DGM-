"""Deterministic audit of MSC2020 subject taxonomy versus mapped Lean declarations.

A mapped source is not a kernel-verified theorem. This script never awards PASS.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DECL = re.compile(r'^ImandraXMathlib\.[A-Za-z_][A-Za-z0-9_]*$')
MSC = re.compile(r'^(?:[0-9]{2}-[0-9A-Z]{2}|[0-9]{2}[A-Z][0-9]{2})$')


def report(csv_file: Path, mapping_file: Path, proof_file: Path) -> dict:
    with csv_file.open(encoding='utf-8', newline='') as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 6006 or len({r['msc_code'] for r in rows}) != 6006:
        raise ValueError('Expected 6006 unique MSC2020 detailed codes')
    if any(r.get('verified_proof') != 'NO' or r.get('formalized_in_lean') != 'NOT_AUDITED' for r in rows):
        raise ValueError('Source taxonomy must not be represented as verified theorems')
    valid_codes = {r['msc_code'] for r in rows}
    mapping = json.loads(mapping_file.read_text(encoding='utf-8'))
    source = proof_file.read_text(encoding='utf-8')
    if not isinstance(mapping, list) or not mapping:
        raise ValueError('Empty proof source mapping')
    declarations = set()
    for entry in mapping:
        if not isinstance(entry, dict) or set(entry) != {'declaration','msc_code','module','status'}:
            raise ValueError('Invalid proof mapping entry')
        name, code = entry['declaration'], entry['msc_code']
        if (not isinstance(name, str) or not DECL.fullmatch(name) or name in declarations or
            not isinstance(code, str) or not MSC.fullmatch(code) or code not in valid_codes or
            entry['module'] != 'ImandraXMathlib.Foundations' or entry['status'] != 'PROOF_SOURCE_UNVERIFIED'):
            raise ValueError('Untrusted proof mapping')
        local_name = name.rsplit('.', 1)[-1]
        if not re.search(r'(?m)^theorem\s+' + re.escape(local_name) + r'\b', source):
            raise ValueError('Mapped declaration missing from Lean source')
        declarations.add(name)
    return {
        'taxonomy': 'MSC2020-OFFICIAL',
        'total_detailed_subject_codes': 6006,
        'source_mapped_declarations': len(mapping),
        'mapped_subject_codes': len({x['msc_code'] for x in mapping}),
        'externally_verified_declarations': 0,
        'proof_status': 'SOURCE_MAPPED_UNVERIFIED',
        'note': 'The source map is not a proof acceptance record; independent signed runner evidence required.',
    }


def main() -> int:
    print(json.dumps(report(ROOT/'data/msc2020_6006_coverage.csv',
        ROOT/'proofs_mathlib/msc_mapping.json',
        ROOT/'proofs_mathlib/ImandraXMathlib/Foundations.lean'), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
