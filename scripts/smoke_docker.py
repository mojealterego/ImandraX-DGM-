"""GitHub-hosted runner: execute trusted baseline inside Docker no-net container."""
from pathlib import Path
from imandrax_dgm.sandbox import DockerSandbox, make_math_cases, static_security_check

root=Path(__file__).resolve().parents[1]
content=(root/'research/solver.py').read_text(encoding='utf-8')
assert static_security_check(content)['pass']
runner=DockerSandbox(image='python:3.12-slim',
                     worker=root/'src/imandrax_dgm/sandbox_worker.py',
                     allow_unpinned_for_ci=True) # TEST ONLY; prod requires image digest.
cases=make_math_cases(seed=42,count=60)
result=runner.evaluate(content,cases,timeout=90)
print(result)
assert result['passed']==result['total']==60