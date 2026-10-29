> **ARCHIWALNA SPECYFIKACJA v0.1.** Aktualna implementacja i wspólny kontrakt v0.4: [UNIFIED_ENGINE_v0.4.md](UNIFIED_ENGINE_v0.4.md). Wcześniejsze stany „NOT IMPLEMENTED” mogą być nieaktualne.

# IMANDRAX × DGM–RSI Ω — Unified Mathematical Discovery & Verified Evolution Engine

**Document ID:** IMDGM-SYS-001  
**Version:** 0.1.0, 2026-10-29  
**State:** `REFERENCE_IMPLEMENTATION_TESTED_LOCALLY / PRODUCTION_NOT_VERIFIED`  
**Scope:** new independent integrated design. The original ImandraX v1.3 and DGM–RSI v1.0 remain unchanged and are preserved in `docs/`. No changes were made to `mojealterego/dgm`, `ocaf-runtime`, or any other remote repository.

## 1. Engineering decision: combine functions, not trust domains

The unified system is one product with two mutually constrained subsystems:

- **ImandraX Knowledge/Proof Plane**: MSC2020/MSC2010, source provenance, theorem retrieval, typed mathematical intermediate representation, independently checked proofs, numerical enclosures, simulations, uncertainty, counterexamples and research evidence.
- **DGM–RSI Evolution Plane**: bounded hypotheses, alternative implementations of proof-search strategies and agent harnesses, empirical comparisons, reproducible experiments, genealogical archive, selection and meta-evaluation of future proposer quality.
- **Independent Authority Plane**: signed policies, immutable budgets, sandbox orchestration, hidden benchmark custody, release authorization and rollback. This plane is neither writable nor executable by evolutionary candidates.

**Fundamental rule:** DGM can improve *how ImandraX searches, plans, retrieves, formalizes and schedules*, but it cannot certify its own mathematics, relax its own acceptance criteria or grant itself production rights.

```text
                              IMANDRAX × DGM Ω
                    One product / one typed request interface
                                      |
             +------------------------+------------------------+
             |                        |                        |
       Knowledge Plane           Proof Plane              Research Plane
       19,114 records            Lean/SMT*                DGM Proposer*
       704 repo inventory        DDAR*                    Parent Selection*
       MSC2020 taxonomy          Interval certs*         Quality-Diversity*
       Source citations          Model checking*         Hypothesis Archive*
             |                        |                        |
             +------------------------+------------------------+
                                      |
                          Independent Policy Gate
                           [implemented subset]
                                      |
                     Signed Evaluation / Proof Checker*
                                      |
                         Evidence Ledger [local]
                                      |
                      Human Approval / Release Gate*

* Planned adapter or infrastructure, NOT implemented or tested here.
```

## 2. Distinguish six classes of results

| Type | Meaning | Required evidence | May be labeled `PROVED_STRICT`? |
|---|---|---|---|
| `SOURCE_INDEXED` | text/classification in a source | source digest, page, license, timestamp | No |
| `HYPOTHESIS` | conjecture or proposal | statement, assumptions, provenance | No |
| `EMPIRICAL_BENCHMARK` | observed experiment | pinned code, dataset, seed, trace, confidence interval | No |
| `NUMERICAL_BOUND` | certified interval under explicit assumptions | rounding mode, enclosure, independent check | Only if separately formalized |
| `FINITE_MODEL_CHECK` | finite or bounded property | model, scope, bound, certificate | Not an unbounded theorem |
| `FORMAL_THEOREM` | theorem under a declared theory | closed proof term + checker acceptance + axioms/toolchain/commit hashes | Yes, only in verified scope |

The prototype's Ed25519 verification **authenticates an external evaluation report**. It is not a Lean kernel and cannot prove a theorem. The existing 19,114-entry SQLite index is a retrieval corpus, not a proof library.

## 3. Trust boundaries and process separation

1. `knowledge-api`: read-only FTS5 database and source index. Untrusted PDF/repo contents never become instructions.
2. `proof-bridge`: pinned Lean toolchains and independent proof checkers, in isolated workers. Future adapter; no proof-checking executable is included.
3. `numeric-lab`: Optax/JAX, interval methods, optimization, regression. Future adapter; stochastic evidence cannot be upgraded to proof.
4. `physics-lab`: MuJoCo, dm_control and Menagerie. Future adapter; numerical simulation does not establish physical-system safety by itself.
5. `evolution-proposer`: suggests scoped patch and experiment only. Future adapter; cannot invoke shell on host.
6. `policy-authority`: independently signed immutable policy and budgets, separate service identity; proposed future production service.
7. `experiment-runner`: ephemeral offline microVM with read-only root, no host mounts/secrets/network, limits on CPU/RAM/disk/processes, signed results. Future infrastructure; local Python tests do not establish isolation.
8. `release-authority`: separate signer, human review, canary, rollback. Future infrastructure; intentionally no auto-release endpoint in prototype.

The reference implementation implements (1), source-aware proposal routing, local policy checks, Ed25519 verification of supplied reports, and a SQLite hash-chain event journal. It **does not** execute patches, run a microVM, check proofs, train models or deploy releases.

## 4. Typed interfaces and data contracts

### 4.1. Mathematical request

```json
{
  "task_id": "UUID",
  "task_kind": "THEOREM_PROOF | NUMERIC_CERT | SIMULATION | RESEARCH",
  "msc2020": ["00A05"],
  "source_refs": [{"source": "MSC2020-ENC", "code": "00A05"}],
  "statement": "typed Math IR",
  "assumptions": [],
  "resource_budget": {"max_cpu_seconds": 300, "max_tokens": 10000},
  "proof_policy": {"checker": "Lean4", "allowed_axioms": [], "strict": true}
}
```

### 4.2. DGM candidate (research only)

```json
{
  "candidate_id": "c-uuid",
  "parent_digest": "64-lowercase-hex",
  "patch_digest": "64-lowercase-hex",
  "hypothesis": "Reducing duplicate theorem retrieval improves pass rate on unseen tasks",
  "paths": ["harness/planner.py"],
  "max_tokens": 10000,
  "max_runtime_seconds": 600,
  "source_refs": [{"source": "MSC2020-ENC", "code": "00A05"}],
  "promotion_rights": false
}
```

The current `Candidate` dataclass implements a narrower schema and admits a *proposal record*, not patch application.

### 4.3. Signed external evaluation evidence

The current prototype verifies an Ed25519 signature on canonical JSON with fields `candidate_digest`, `source_digest`, `suite`, `result`, `runner_id`. The public key must be explicitly configured in the trusted runner map. Verification only yields `RESEARCH_EVIDENCE_ONLY`; never a production promotion or formal theorem. Production must additionally bind the full source-tree digest, VM attestation, policy hash, benchmark epoch, time and revocation status.

## 5. Bounded self-improvement cycle

1. **Source retrieval**: cite a stable MSC entry, formal theorem, issue or benchmark. Preserve source hashes.
2. **Failure analysis**: identify reproducible failed tests, runtime costs, wrong assumptions and known limitations.
3. **Hypothesis**: propose one falsifiable improvement with negative-control experiment.
4. **Scope admission**: restrict mutable paths to agent harness, research adapters and non-authoritative research code.
5. **Static gate**: validate patch syntax, dependencies, licenses, forbidden imports and symlinks (future work).
6. **Sandbox evaluation**: compile/test in isolated microVM with no secrets/network; independent runner signs evidence (future work).
7. **Statistical review**: paired trials, confidence intervals, hidden transfer tasks, fixed compute/token budget (future work).
8. **Archive**: append all attempts including failures, keeping immutable genealogy (future work; prototype has only event journal).
9. **Meta-evaluation**: compare *future offspring yield* from original and modified proposers on unseen problems (future work).
10. **Promotion**: explicit operator signature after all release gates; independent authority, canary and rollback (future work).

No stage may reinterpret a failed security check as a minor quality penalty. A new model must not rewrite `policy`, `security`, `tests`, `benchmark`, `signer`, `release`, `config`, `.git`, `.github` or protected service code. A candidate that produces a high score without an independently verified execution trace is rejected.

## 6. Source ingestion and repository selection

The GitHub inventory contains 704 accessible repository metadata records. The machine-readable `REPOSITORY_TRIAGE_704.csv` assigns P0–P4 and an explicit evidence tier. **A name-based heuristic is not a code audit.** 49 selected repositories have had root/README-level review; 655 remain metadata-only. A repository is never marked `INTEGRATED` merely because it appears in this catalog.

For any chosen repository, the future importer must:

- pin the source commit and compute SHA-256 of each imported file;
- record upstream origin, license per file, transitive dependencies, external model/dataset terms, SBOM and provenance;
- statically inspect build scripts before execution;
- mount the code as read-only in an isolated worker;
- run a reproducible build and the repository's own test suite;
- create typed adapters and negative tests;
- record `INTEGRATED` only after independent E2E evidence.

Recommended first integration order: Lean toolchains and proof kernel, then DGM harness and independent evaluation, then geometry/numeric/simulation, then research skills and remaining adapters. Do not attempt to vendor all 704 repositories into one codebase.

## 7. Lean toolchain isolation (confirmed on GitHub)

| Repository | Toolchain at inspected default branch | Required action |
|---|---|---|
| `mathlib4` | `leanprover/lean4:v4.36.0-rc2` | separate pinned workspace |
| `batteries` | `leanprover/lean4:v4.36.0-rc2` | match mathlib version and manifests |
| `iris-lean/Iris` | `leanprover/lean4:v4.35.0` | independent workspace; Iris pins batteries v4.35.0 |
| `mathematics_in_lean` | `leanprover/lean4:v4.34.0` | independent workspace; MIL pins mathlib v4.34.0 |

The repository HEAD versions cannot be presumed mutually compatible. Correct solution: independent Lake workspaces per pinned toolchain, with typed proof artifact exchange and re-checking. A shared workspace is only permissible after an explicit compatibility migration with passing builds.

## 8. Physical/numerical validation obligations

- **MuJoCo/dm_control**: state/action schema, units SI, contact solver tolerances, deterministic seeds where supported, model hash, control traces, stochastic repetition, falsification tests and stability envelope.
- **Optax/JAX**: dtype and precision policy, objective/gradient checks, optimizer state, random seeds, reproducibility, error bounds; optimality claims require separate certificates.
- **AlphaGeometry/AlphaGeometry2**: nondegeneracy assumptions, proof trace, auxiliary constructions, independent Lean translation or trusted checker, negative geometry fixtures.
- **RegressLM/representations4d/3d-shapes**: distribution shifts, calibration, model weights/dataset license, confidence and ground truth, no conversion of prediction into proof.
- **Science skills**: allowlisted external data sources, access control, citation, licensing and privacy. Never run `SKILL.md` content as arbitrary executable instruction.

## 9. Attack surface and controls

| Threat | Required control | Prototype status |
|---|---|---|
| Candidate modifies evaluator/policy | separate authority + path allowlist | allowlist implemented locally; process separation not implemented |
| Arbitrary code execution | microVM no network/no host mounts | NOT IMPLEMENTED |
| Forged evaluation score | Ed25519 verification with trusted public keys | local verification implemented; runner attestation not implemented |
| Unapproved production release | external human-signed promotion | no release API implemented |
| Repository prompt injection | data-only retrieval, no instruction elevation | retrieval is read-only; full ingestion not implemented |
| Benchmark contamination | sealed holdout + transfer evaluation | NOT IMPLEMENTED |
| SQLite history tampering | hash chain, triggers, external immutable store | local chain/triggers implemented; external store NOT IMPLEMENTED |
| Dependency/license violations | per-file license + SBOM + offline build | NOT IMPLEMENTED |
| Hidden model drift | pinned manifests and controlled benchmark epoch | NOT IMPLEMENTED |
| Unbounded evolution cost | immutable budget and job quotas | admission checks implemented; scheduler not implemented |

## 10. Acceptance contract

A release is **not** production ready unless: (a) pinned code+dependencies+licenses; (b) independently built Lean libraries and proof kernel; (c) bounded worker isolation and external evaluator; (d) E2E on real MuJoCo where applicable; (e) failure/recovery/chaos tests; (f) negative security tests; (g) independent statistical comparison including held-out tasks; (h) manual signed approval; (i) monitored canary+rollback; (j) complete evidence manifest. The attached DGM–RSI `R0–R14` and ImandraX `G01–G20` gates remain mandatory, not silently renumbered or considered passed.

## 11. Current evidence and non-claims

**Verified locally in this delivery:** inventory of 704 repo metadata; 49 root/README reviews across current and prior sessions; 19,114-record read-only knowledge index; testable research proposal admission; Ed25519 evidence verification; append-only SQLite event journal; source-aware unified proposal path; tests listed in `VALIDATION_RESULTS.json`.

**Not verified:** full code-level audit of 704 repos, full clone of 16 original repos, any Lean `lake build`, MuJoCo tests, independent proof checking, running original DGM, Firecracker isolation, GPU/TPU acceleration, sustained autonomous improvement, causal RSI benchmark gains, deployment. These remain tracked work, not completed features.

## 12. Source traceability

- `docs/IMANDRAX_OMEGA_ENGINE_BLUEPRINT_v1.3.md`: original ImandraX architecture, MSC2020 coverage and 20 G-gates.
- `docs/DGM_RSI_OMEGA_PRODUCTION_BLUEPRINT_v1.0.md`: original DGM–RSI architecture, experimental methodology, immutable authority and 15 R-gates.
- `docs/DGM_RSI_OMEGA_SECURITY_VALIDATION_AND_RELEASE_v1.0.md`: original DGM threat model and negative tests.
- `docs/REPOSITORY_AUDIT_16.md`: pinned 16 repo snapshots, structural findings and license caveats.
- `data/repositories_704.tsv`: 704 metadata records from linked GitHub search, captured 2026-10-29.
- `data/IMANDRAX_MATH_KNOWLEDGE_FTS.sqlite3`: 19,114 indexed records from user-provided mathematical PDF corpus.

All third-party sources remain subject to their own licenses and update history. This new document supersedes the previous *prohibition on merging ImandraX and DGM* **only for this newly requested combined project**, not for the original standalone repositories or their historical requirements.