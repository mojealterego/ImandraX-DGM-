"""Research-only digital genotype / bounded mutation and fitness assessment.

This module never executes candidate code and has no promotion, merge or deploy API.
The existing ResearchCycle and ResearchArchive remain the only code-evolution path.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence

GENES = frozenset({
    "retrieval_weight", "reflection_threshold", "exploration_rate",
    "router_cost_weight",
})


def _bounded(value: object, name: str) -> float:
    if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("INVALID_" + name)
    return float(value)


@dataclass(frozen=True)
class DigitalGenotype:
    genes: tuple[tuple[str, float], ...]

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "DigitalGenotype":
        if not isinstance(values, dict) or set(values) != GENES:
            raise ValueError("INVALID_GENOTYPE_SCHEMA")
        return cls(tuple(sorted((k, _bounded(v, k.upper())) for k, v in values.items())))

    @property
    def digest(self) -> str:
        raw = json.dumps(dict(self.genes), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

    def mutate(self, gene: str, value: float) -> "DigitalGenotype":
        if gene not in GENES:
            raise ValueError("PROTECTED_OR_UNKNOWN_GENE")
        changed = dict(self.genes)
        changed[gene] = _bounded(value, "GENE")
        if changed[gene] == dict(self.genes)[gene]:
            raise ValueError("NOOP_MUTATION")
        return DigitalGenotype.from_mapping(changed)


@dataclass(frozen=True)
class FitnessEvidence:
    regression: float
    heldout: float
    robustness: float
    safety: float
    efficiency: float
    novelty: float

    def __post_init__(self):
        for field in ("regression", "heldout", "robustness", "safety",
                      "efficiency", "novelty"):
            _bounded(getattr(self, field), field.upper())


def fitness(evidence: FitnessEvidence, *, baseline_heldout: float) -> dict:
    """Fixed, inspectable weights. Metrics are supplied, never attested here."""
    base = _bounded(baseline_heldout, "BASELINE_HELDOUT")
    score = (0.15*evidence.regression + 0.45*evidence.heldout +
             0.15*evidence.robustness + 0.15*evidence.safety +
             0.07*evidence.efficiency + 0.03*evidence.novelty)
    valid = (evidence.safety >= 0.98 and evidence.regression >= 0.90 and
             evidence.heldout >= base)
    return {
        "score": round(score, 6),
        "admissible_for_review": valid,
        "status": "RESEARCH_ONLY_UNATTESTED_NOT_APPROVED" if valid else "REJECTED_BY_FITNESS_GATE",
    }


def mutation_loop(
    seed: DigitalGenotype, mutations: Sequence[tuple[str, float, FitnessEvidence]],
    *, baseline_heldout: float, max_mutations: int = 8,
) -> dict:
    """Evaluates explicit, externally supplied evidence; no generated patch or auto-apply."""
    if not isinstance(seed, DigitalGenotype):
        raise ValueError("INVALID_SEED_GENOTYPE")
    if type(max_mutations) is not int or not 1 <= max_mutations <= 8:
        raise ValueError("INVALID_MUTATION_BUDGET")
    if not isinstance(mutations, (list, tuple)) or len(mutations) > max_mutations:
        raise ValueError("MUTATION_BUDGET_EXCEEDED")
    candidates = []
    for item in mutations:
        if (not isinstance(item, (list, tuple)) or len(item) != 3 or
                not isinstance(item[2], FitnessEvidence)):
            raise ValueError("INVALID_MUTATION_EVIDENCE")
        gene, value, evidence = item
        candidate = seed.mutate(gene, value)
        if any(x["genotype_sha256"] == candidate.digest for x in candidates):
            raise ValueError("DUPLICATE_GENOTYPE")
        assessment = fitness(evidence, baseline_heldout=baseline_heldout)
        candidates.append({"genotype_sha256": candidate.digest,
                           "changed_gene": gene,
                           "assessment": assessment})
    ranked = sorted(candidates, key=lambda x: (
        not x["assessment"]["admissible_for_review"],
        -x["assessment"]["score"],
        x["genotype_sha256"]))
    return {
        "seed_genotype_sha256": seed.digest,
        "status": "RESEARCH_PROPOSALS_ONLY_NO_APPLY",
        "evaluated": len(ranked),
        "ranked": ranked,
        "approval": "OWNER_AND_INDEPENDENT_CHECKS_REQUIRED",
    }
