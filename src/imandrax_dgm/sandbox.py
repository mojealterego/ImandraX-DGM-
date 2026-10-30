"""Docker-only, no-network evaluation boundary for untrusted generated Python.

This is a CONTAINER isolation prototype, NOT a Firecracker/microVM security claim.
The Docker daemon is a privileged dependency. Do not run against a hostile shared host.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
from typing import Callable

from .evaluation_policy import SandboxError, make_math_cases, static_security_check


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

    def command(self, input_dir: Path, name: str, *, worker: Path | None = None) -> list[str]:
        if not re.fullmatch(r'[a-z0-9-]{1,63}', name):
            raise SandboxError('Invalid container name')
        return ['docker','run','--rm','--name',name,
                '--network','none','--read-only','--cap-drop','ALL',
                '--security-opt','no-new-privileges','--pids-limit','64',
                '--memory','512m','--cpus','1','--user','65534:65534',
                '--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
                '--mount',f'type=bind,src={Path(input_dir).resolve()},dst=/input,readonly',
                '--mount',f'type=bind,src={worker or self.worker},dst=/trusted/worker.py,readonly',
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
            # A checkout may use mode 0600. Stage a readable, immutable mount
            # without changing the original trusted worker's permissions.
            staged_worker = directory/'worker.py'
            staged_worker.write_bytes(self.worker.read_bytes())
            staged_worker.chmod(0o644)
            directory.chmod(0o755)
            (directory/'solver.py').chmod(0o644)
            (directory/'cases.json').chmod(0o644)
            cmd = self.command(directory, name, worker=staged_worker)
            try:
                proc = self.run(cmd, timeout=timeout, text=True, capture_output=True,
                                shell=False, env={'PATH':'/usr/local/bin:/usr/bin:/bin'})
            except subprocess.TimeoutExpired as exc:
                try:
                    self.run(['docker','rm','-f',name],timeout=10,text=True,capture_output=True,
                             shell=False,env={'PATH':'/usr/local/bin:/usr/bin:/bin'})
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
