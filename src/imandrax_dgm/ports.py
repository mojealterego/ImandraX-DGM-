"""Provider contracts: application code never selects a network/process backend."""
from typing import Protocol


class ResearchProvider(Protocol):
    def search(self, query: str) -> list[dict]: ...


class ProposalProvider(Protocol):
    def complete_json(self, system: str, user: str) -> dict: ...


class CandidateEvaluator(Protocol):
    def evaluate(self, content: str, cases: list[dict], *, timeout: int = 60) -> dict: ...
