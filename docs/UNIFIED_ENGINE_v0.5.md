# ImandraX × DGM × RSI Ω — jeden silnik, v0.5

**Stan:** zweryfikowana lokalnie implementacja badawcza z prawdziwym indeksem MSC2020, archiwum wielopokoleniowym i kontrolą zgody. **Nie jest to ukończony uniwersalny solver, produkcyjna autonomiczna RSI ani zewnętrznie atestowany system.** Wszystkie zmiany źródłowe zlecone przez użytkownika są wprowadzane bezpośrednio na `main`; **kandydaci tworzeni autonomicznie przez RSI nigdy nie otrzymują prawa do samodzielnego zapisu do `main`**.

## 1. Architektura jednego produktu

```text
               imandrax-dgm / IntegratedEngine
                              |
           +------------------+------------------+
           |                  |                  |
       IMANDRAX             DGM                RSI
  6006 MSC labels     ResearchArchive      OpenAlex + LLM
  19,114 optional     depth/parent SHA     sandbox Docker
  exact arithmetic    empirical ranking   persistent daemon
  Lean CI subset      ApprovedArchive      review artifacts
           |                  |                  |
           +------------------+------------------+
                              |
                    SHA-bound proposal
                              |
                    RSIReviewStore (PROPOSED)
                              |
                  independent signed evidence
                              |
                    user Ed25519 decision
                              |
                 approved archive, not deploy
```

## 2. Source and proof boundaries

- `data/msc2020_6006_coverage.csv` is a faithful 6006-code index from the user-provided MSC2020 PDF audit, including source page references. `scripts/build_msc_full_index.py` constructs a real FTS5 database. `SOURCE_INDEXED_NOT_FORMALIZED` is explicit.
- The separate 19,114-record FTS5 database (6006 encyclopedia, 6603 official MSC, 6198 MSC2010, 307 MATH appendix) is an optional larger artifact, **not included** in this public repo. The classification-only CSV does not contain all encyclopedic comments.
- `proofs/ImandraX/Basic.lean` and `Arithmetic.lean` are small Lean kernel-checkable examples. Their presence does **not** formally verify arbitrary MSC entries, Riemann, P≠NP, Navier–Stokes or any other open problem.
- 701 public GitHub repository records are indexed for triage. The three private records and full source audits are outside the current evidence scope.

## 3. Real multi-generation research evolution

1. `IntegratedEngine.evolve` checks that the requested MSC reference exists and opens an append-only research campaign.
2. `ResearchCycle` selects a parent from `ResearchArchive` with the **same pinned commit and baseline SHA-256**. Parent source is passed to the LLM as explicitly untrusted data, never as an instruction or approved patch.
3. The LLM proposes **only** `research/solver.py`. The patch is computed against the original pinned baseline and bound to SHA-256. Parent lineage is included in the review artifacts.
4. Static safety checks and isolated Docker `--network none` evaluation run regression and a deterministic secondary test set. Scores are **unattested and not a hidden external benchmark**.
5. The candidate is stored immutably in the research genealogy (depth ≤12; ≤2048 records) with parent ID, content SHA, patch SHA, evaluation digest and quality metrics. The next proposal can descend from it, even across scheduled runs if the cache is restored.
6. `IntegratedEngine.register_review_artifacts` checks manifest hashes, source drift, candidate selection and lineage consistency. It registers **PROPOSED**, never `APPROVED`.
7. Separate runner evidence and a personally signed user decision are still mandatory for `ApprovedArchive`; neither this step nor `ApprovedArchive` applies a patch to `main`.

**Limit:** the evolutionary process currently changes only the isolated solver experiment, not its own policy, tests, CI, signing, release, security controls or the entire ImandraX architecture. It does not demonstrate sustained improvement on unseen independent tasks.

## 4. Continuous execution and independent authority

- GitHub Actions `rsi-research-cycle.yml`: every six hours; public OpenAlex metadata by default, bounded LLM RSI only when explicitly enabled by owner. `actions/cache` can preserve research genealogy for the same commit, subject to cache retention. No GitHub write permission.
- `imandrax-daemon`: real loop for a **dedicated, externally operated host**, with 300–86400 second interval, unique campaign directories, baseline drift detection and stop after three failures. The included systemd unit is a template; **no external host has been provisioned or started**.
- `deploy/authority`: independent TLS 1.3 approval service with role-separated tokens and Ed25519 verification; Compose deployment recipe, no private owner signing key, no GitHub write token. **Not deployed.** SQLite audit is not WORM.
- The research worker and authority must run on separate hosts/trust domains; Docker socket is root-equivalent and cannot be shared with the approval authority.

## 5. CI evidence and release gates

Local test suite must be run in full. GitHub Actions includes Python unit/adversarial, Docker no-network E2E, real MuJoCo CPU simulation and Lean kernel compilation. The four pinned upstream Lean repositories have an independent matrix triggered on proof changes and weekly; its **results must be checked** before claiming compatibility.

Still required: comprehensive formal mathematical proof corpus; independent proof-checker service for arbitrary inputs; full mathlib/Batteries/Iris/MIL builds; Firecracker/attestation; production signer/WORM/KMS/HSM; audited multi-host authority; GitHub Ruleset and trusted release applier; full code/license/SBOM/build audit for 704 repos; real 24/7 infrastructure; external unseen benchmark proving RSI transfer. No claim of general emergent capabilities without reproducible evidence.
