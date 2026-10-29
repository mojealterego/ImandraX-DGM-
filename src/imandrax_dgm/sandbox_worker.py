"""Trusted evaluator script mounted read-only into networkless container.

This script is not writable by the candidate. It uses a fixed solve(task) contract.
"""
import contextlib
import importlib.util
import io
import json
import sys
import time


def main():
    if len(sys.argv) != 3:
        raise SystemExit(2)
    with open(sys.argv[2], encoding='utf-8') as f:
        cases = json.load(f)
    start = time.monotonic()
    passed = 0
    # Suppress candidate stdout: the only result is emitted by this trusted script.
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        spec = importlib.util.spec_from_file_location('rsi_candidate', sys.argv[1])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        solver = getattr(module, 'solve')
        for case in cases:
            task = {k: v for k, v in case.items() if k != 'expected'}
            try:
                actual = solver(task)
                if type(actual) is type(case['expected']) and actual == case['expected']:
                    passed += 1
            except Exception:
                pass
    print(json.dumps({'passed': passed, 'total': len(cases),
                      'duration_ms': round((time.monotonic()-start)*1000,3)}, separators=(',',':')))


if __name__ == '__main__':
    main()