"""Research genotype is not a self-deploying evolutionary runtime."""
import pytest
from imandrax_dgm.adaptive_evolution import (
    DigitalGenotype, FitnessEvidence, fitness, mutation_loop)


def sample():
    return DigitalGenotype.from_mapping({
        "retrieval_weight": 0.5, "reflection_threshold": 0.5,
        "exploration_rate": 0.1, "router_cost_weight": 0.2})


def good():
    return FitnessEvidence(0.99, 0.98, 0.96, 1.0, 0.7, 0.5)


def test_genotype_canonical_hash_and_mutation():
    seed = sample()
    assert seed.digest == DigitalGenotype.from_mapping(dict(reversed(seed.genes))).digest
    updated = seed.mutate("retrieval_weight", 0.9)
    assert seed.digest != updated.digest
    assert dict(seed.genes)["retrieval_weight"] == 0.5
    with pytest.raises(ValueError, match="PROTECTED"):
        seed.mutate("disable_policy", 1.0)


def test_mutation_selection_remains_unapproved():
    result = mutation_loop(sample(), [("retrieval_weight", 0.8, good())],
                           baseline_heldout=0.95)
    assert result["ranked"][0]["assessment"]["admissible_for_review"]
    assert result["status"] == "RESEARCH_PROPOSALS_ONLY_NO_APPLY"
    assert result["approval"] == "OWNER_AND_INDEPENDENT_CHECKS_REQUIRED"


def test_fitness_does_not_allow_low_safety_or_regression():
    weak = FitnessEvidence(1, 1, 1, .50, 1, 1)
    assert fitness(weak, baseline_heldout=0.9)["status"] == "REJECTED_BY_FITNESS_GATE"
    assert fitness(FitnessEvidence(.7, 1, 1, 1, 1, 1),
                   baseline_heldout=0.9)["admissible_for_review"] is False
    assert fitness(good(), baseline_heldout=0.99)["admissible_for_review"] is False


@pytest.mark.parametrize("value", [-0.1, 1.01, float("nan"), "0.2", True])
def test_numeric_guards_reject_invalid_gene_values(value):
    with pytest.raises(ValueError):
        sample().mutate("retrieval_weight", value)


def test_mutation_budget_is_bounded_and_duplicate_genotypes_rejected():
    with pytest.raises(ValueError, match="MUTATION_BUDGET"):
        mutation_loop(sample(), [("exploration_rate", .2, good())]*9,
                      baseline_heldout=0.9)
    with pytest.raises(ValueError, match="DUPLICATE_GENOTYPE"):
        mutation_loop(sample(), [("exploration_rate", .2, good()),
                                 ("exploration_rate", .2, good())],
                      baseline_heldout=0.9)


def test_untrusted_outcome_never_proves_independent_fitness():
    assert fitness(good(), baseline_heldout=0.9)["status"] == (
        "RESEARCH_ONLY_UNATTESTED_NOT_APPROVED"
    )
