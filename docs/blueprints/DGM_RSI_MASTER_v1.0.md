# DGM–RSI Ω — Darwinian Gödel Evolution & Recursive Improvement Engine
## Pełna specyfikacja architektoniczna i produkcyjna silnika samodoskonalenia agentów programistycznych

**Dokument:** DGM-RSI-OMEGA-SYS-001 | **Wersja:** 1.0.0 | **Data analizy:** 2026-10-25 | **Status:** `SPECIFIED / NOT IMPLEMENTED`  
**Projekt:** niezależny `DGM–RSI Ω`; **nie jest częścią OCAF Runtime, Aetheris, ImandraX ani ich repozytoriów**.  
**Cel:** stworzenie nowej architektury ewolucji i iteracyjnej poprawy agentów programistycznych opartej na empirii, różnorodności behawioralnej, ograniczonym ryzyku, jawnej ścieżce pochodzenia i powtarzalnych eksperymentach.  
**Granica twierdzeń:** słowa *autorski*, *produkcyjny* i *Ω* opisują projekt i wymagania wykonawcze, nie istniejący skompilowany produkt ani przewagę dowiedzioną pomiarami. „Maksimum” interpretowane jako optymalizacja zbioru celów Pareto, nie obietnica nieograniczonej inteligencji.  
**Zakaz samowolnych wdrożeń:** brak operacji na cudzych repozytoriach, kontach, hostach lub produktach bez oddzielnego uprawnienia. Brak automatycznego połączenia z innym projektem.  

---

## 0. Podstawy źródłowe, weryfikacja i provenance

### 0.1. Materiały źródłowe — stan w dniu 25.10.2026

- **[S01]** Jenny Zhang, Shengran Hu, Cong Lu, Robert Lange, Jeff Clune, *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents*, arXiv:2505.22954v3 (12.03.2026), https://arxiv.org/abs/2505.22954 ; publikacja konferencyjna ICLR 2026. Naukowy punkt bazowy metody: kod agenta poprawiany przez potomka + empiryczna ocena + archiwum przodków.
- **[S02]** Autorzy publikacji: https://github.com/jennyzzt/dgm. Badawcza implementacja referencyjna; pliki `coding_agent.py`, `DGM_outer.py`, `swe_bench/`, `polyglot/`, `tests/` i ostrzeżenia o kodzie generowanym przez model.
- **[S03]** https://sakana.ai/dgm/ (30.05.2025). Omówienie metody i danych eksperymentalnych. SWE-bench 20,0→50,0%; Polyglot 14,2→30,7% w streszczeniu; te liczby odnoszą się do scenariuszy publikacji, **nie są prognozą działania DGM–RSI Ω**.
- **[S04]** https://github.com/BrandonDavidJones1/RSIAI0 — eksperymentalny *RSIAI0-Seed*, inny projekt niż [S02]. README deklaruje modyfikację katalogu `seed/`, Bootstrap LLM, wariant Darwinian GA, pamięć, tryby simulated/real. Krytyczne: README ostrzega o potencjalnie nieograniczonym shellu w trybie real; `ENABLE_DARWINIAN_MODE` opisany jako domyślnie wyłączony. Nie utożsamiać deklaracji README z dowodem odporności kodu.
- **[S05]** https://github.com/BrandonDavidJones1/RSI-AI-Scaffolding — nazwa występująca w otrzymanym opisie; **nie udało się potwierdzić dostępności tej konkretnej ścieżki**. Za jednoznacznie zweryfikowany obiekt uważamy [S04]. Nie zakładać, że to fork/alias bez potwierdzenia.
- **[S06]** https://www.biorxiv.org/content/10.1101/2025.08.21.671415v2 — *Darwin–Gödel Drug Discovery Machine*, przykład dziedzinowej koncepcji dwóch pętli; preprint biologiczny, nie zweryfikowane klinicznie odkrywanie leków.
- **[S07]** https://github.com/google-research/rrsi — RRSI (*Regularized Recursive Self-Improvement of Agent Harnesses*, komunikat 21.09.2026). Istotna motywacja: przeuczenie agentów na stałym zbiorze zadań i regularizacja trajektorii zmian. Zastosowanie w Ω jest własną propozycją inżynierską, nie implementacją RRSI.
- **[S08]** J. Schmidhuber, *Gödel Machines: Fully Self-Referential Optimal Universal Self-Improvers* (teoria maszyn Gödla): formalny program dowodzący korzyści modyfikacji; DGM zastępuje niedostępną na ogół gwarancję globalną testami empirycznymi. Nie wolno zrównywać obu typów zapewnień.

**Poziom analizy:** przeczytano repozytoria/README i publikację udostępnione publicznie; nie przeprowadzono audytu każdej instrukcji kodu RSIAI0, clone/uruchomienia tej implementacji, testu GPU ani implementacji nowego silnika. Nie powoływać się na rzekomą sprawność CI repozytorium, jeśli nie zweryfikowano historii runów.

### 0.2. Rozdzielenie faktów i projektowanych ulepszeń

| Cecha | DGM autorów [S01] | RSIAI0-Seed [S04] (deklaracja) | Projekt DGM–RSI Ω |
|---|---|---|---|
| Pętla self-modification | Tak, empiryczna | Tak, eksperymentalna | Własna, stanowa z transakcyjnym journalem |
| Archiwum gałęzi i wybór przodków | Tak | Tryb GA opcjonalny | Pareto + Quality-Diversity + genealogy + novelty |
| Modyfikacja foundation-model weights | Nie wykazano | Nie potwierdzono | Poza MVP; wymaga osobnego programu treningowego |
| Dowód formalny korzyści globalnej | Nie | Nie potwierdzono | Nie obiecuje; możliwa weryfikacja wybranych niezmienników |
| Mocna izolacja hosta | Autorzy raportują sandboxing | README ostrzega o ryzykownej konfiguracji | Wymagana izolacja mikroVM, brak domyślnego shell hosta |
| Samomodyfikowalna polityka bezpieczeństwa | Nie jest celem publikacji | Nie należy zakładać bezpieczeństwa | Nie; policy/root of trust zewnętrzny, read-only |
| Produkcyjne przejęcie nowej generacji | Badawczy archiwum agentów | Eksperymentalne | Wyłącznie podpisana, audytowana decyzja człowieka |

---

## 1. Mission profile, zakres i definicja sukcesu

### 1.1. Dozwolony zakres pierwszego produktu

Silnik eksploruje **agent harness**: planowanie kolejności działań, wyszukiwanie plików, narzędzia read/edit dla kopii kodu, obsługę błędów, kompresję kontekstu, pamięć przyczyn porażek, weryfikację patchy, trasowanie zadań, budżety i kolejność testów. Punkt startowy: *fixed frozen LLM*, aby odróżnić poprawę warstwy agentowej od wpływu zmian modelu. Pierwsze eksperymenty dotyczą **wyłącznie zadań programistycznych** w kontrolowanych benchmarkach.

Nie stanowią celu MVP: nieograniczone samodoskonalenie ogólnej inteligencji, modyfikacja własnego systemu oceny i ochrony, samodzielna zmiana uprawnień, dostęp do Internetu z sandboxu, automatyczna produkcyjna instalacja wyników, masowe skanowanie sieci, samo-replikacja infrastruktury, trening dowolnych modeli bazowych, optymalizacja w zastosowaniach klinicznych lub finansowych bez osobnego programu walidacji.

### 1.2. Formalne kryterium przyrostu

Nie wystarczy wzrost jednego rankingu. Wynik musi równocześnie zachować wymagane niezmienniki oraz wykazać statystycznie odporną zmianę jakości na **nowych, niewidzianych problemach**. Rozdzielać: (a) poprawę rozwiązania problemów; (b) poprawę jakości przyszłych propozycji modyfikacji; (c) wzrost sprawności przy tym samym koszcie; (d) uczenie się pamięci zadaniowej, które nie jest poprawą algorytmiczną.

### 1.3. Profile środowisk

- `P0_OFFLINE_ANALYSIS`: statyczny parser i projektowanie zmian, bez wykonywania kodu.
- `P1_SAFE_SIMULATION`: generator kandydatów + fałszywe zadania i symulowane wyniki, bez systemowych skutków ubocznych.
- `P2_EPHEMERAL_EVAL`: izolowane mikroVM, offline fixtures, przydział CPU/RAM/IOPS.
- `P3_RESEARCH_CAMPAIGN`: wiele kandydatów, losowanie różnych seedów, zamrożone benchmarki i dystrybucja do niezależnych workerów.
- `P4_STAGED_RELEASE`: testowane artefakty udostępnione w cieniu, po osobnej decyzji operatora.
- `P5_PRODUCTION`: tylko po wszystkich bramkach wydania, bez samoczynnej aktywacji przez algorytm RSI.

---

## 2. Architektura referencyjna — izolacja ewolucji od władzy wykonawczej

```text
Operator / Policy Owner / Signer (zewnętrzny wobec RSI)
                      |
       Trust Root / Admission Policy / Approval Ledger (IMMUTABLE)
                      |
          Evolution Control Plane [Rust 2024]
  +-------------------+-----------------------------+
  |                   |                             |
Archive &         Proposer /                   Experiment
Lineage DB         Hypothesis Lab               Controller
  |                   |                             |
  |              Patch Capsule                   Evaluation
  |                   |                             |
  +-------------------+-----------------------------+
                      |
          Verification & Sandboxing Gateway
          /                              \
  Disposable microVM A                 Disposable microVM B
  (no writable host, no net)           (no writable host, no net)
          \                              /
                Artifact CAS / Metrics
                      |
            Independent Promotion Gate
                      |
                 Staged Release
```

**Invariant A:** kandydat nie potrafi zmieniać bezpośrednio `Trust Root`, polityk, testów ukrytych, budżetów, dekodera wyników ani kluczy podpisujących.  
**Invariant B:** program generujący patch może być zmieniany przez ewolucję, ale walidator/promotion pozostaje poza jej obszarem zapisu.  
**Invariant C:** brak sieci i brak tajnych danych w środowisku wykonującym kod modelu; broker ma wyłącznie bezpieczne, zawężone interfejsy RPC.  
**Invariant D:** żaden wynik benchmarku nie daje samodzielnie uprawnienia do publikacji w repozytorium ani wdrożenia na produkcję.  
**Invariant E:** każdy kandydat ma kompletne genealogy (`parent_ids`), digest źródła, diff, konfigurację, semantykę celu i podsumowanie ryzyka.

### 2.1. Podsystemy i granice

1. **Ω-Treasury/Control:** quota kampanii, koszt obliczeń, identyfikatory tenantów, stop/cancel, monotonic generation_id.
2. **Ω-Genome Registry:** immutable definicje agenta, manifest kodu, sekwencja zmian i zgodności ABI; zapisy wyłącznie przez controller.
3. **Ω-Mutation Proposer:** proponuje hipotezę, zakres zmian i ocenę kosztu; nie ma dostępu do etykiet hidden-set.
4. **Ω-Patch Compiler:** transakcyjny patch, AST/CST validation, import map, dependency diff, reguły allowlist, replikowalne dependencies.
5. **Ω-Sandbox Runner:** microVM Firecracker/KVM lub równoważny mocno izolowany worker; kontenery zwykłe tylko do mniej ryzykownych, znanych fixture.
6. **Ω-Evaluation Orchestrator:** oddzielne train/dev/test/hidden/transfer/regression/safety benches, lekcja testów losowych.
7. **Ω-Evolutionary Archive:** QD cells, Pareto fronts, semantyczne fingerprints, genealogia, normalizowane wyniki.
8. **Ω-Formal Constraint Gate:** statyczne bezpieczeństwo, dowody/kontrprzykłady lokalnych kontraktów, weryfikacja uprawnień.
9. **Ω-Promotion Authority:** ludzka aprobata, podpis, canary, rollback, audit; wyodrębniona tożsamość.
10. **Ω-Observability:** traces, resource usage, wpływ zmian, detekcja działań poza zakresem i koszt/score.

### 2.2. Preferowany stos

- **Sterowanie:** Rust 2024 (`unsafe_code` zabronione dla własnego core), Tokio, typed domain events, Postgres albo embedded SQLite single-node, JSON Schema/Protobuf, mTLS do workera.
- **Uczenie / generowanie propozycji:** adapter LLM Python/HTTP do modeli lokalnych i zewnętrznych. Bez vendor lock-in. API key wyłącznie w osobnym vault dla propose plane, nigdy w sandboxie.
- **Wykonanie:** izolowane Linux microVM z odczytem obrazu bazowego i tymczasowym overlayem; `seccomp`, namespaces, `cgroup v2`, ograniczenie egress; nie traktować samego Docker jako granicy przeciw hostile code przy dostępie do socketu Dockera.
- **Artifact/CAS:** SHA-256 lub BLAKE3 do adresowania + osobne kryptograficzne podpisy manifestów; archiwum append-only; pliki źródłowe po patchu immutable.
- **Weryfikacja:** parsery języków, Semgrep/Ruff/Clippy/pytest/cargo test na odpowiednich podzbiorach, sanitizer/fuzzing, SLSA/SBOM; SMT Z3/cvc5 opcjonalnie dla specyficznych własności.
- **Proces zarządzania:** typowane state machine i idempotency keys, outbox/events; brak nieautoryzowanego mergera.

---

## 3. Model matematyczny: zdolność, jakość, ryzyko i koszt

Niech `a ∈ A` będzie wersją agenta, `d ∼ D` zadaniem, `s` losowym ziarnem, `r(a,d,s)` wektorem obserwacji. Osobno mierzyć `success`, `runtime`, `tokens`, `compute_cost`, `violations`, `stability`, `coverage`, `edit_quality`, `transfer_gap`.

**Efektywna użyteczność:**

\[
U(a;D)=w_1\,E_{d,s}[\mathrm{pass}(a,d,s)]-w_2\,E[\mathrm{cost}]-w_3\,E[\mathrm{latency}]-w_4\,\mathrm{regressions};
\]

ale ta funkcja jest **porządkiem w obrębie populacji dopuszczalnej**, a nie zamiennikiem bezwzględnych ograniczeń. Zbiór dopuszczalny:

\[
\mathcal F=\{a: \mathrm{SecurityPolicy}(a)=\mathrm{PASS},\ \mathrm{LicensePolicy}(a)=\mathrm{PASS},\ R(a)\le R_{max},\ \mathrm{Budget}(a)\le B\}.
\]

W praktyce preferować **ranking Pareto** w wymiarach `accuracy ↑`, `robustness ↑`, `uncertainty calibration ↑`, `cost ↓`, `latency ↓`, `security risk ↓`, gdyż arbitralny zestaw wag może ukryć regresję bezpieczeństwa.

### 3.1. Interval evidence i niepewność

Dla binarnego rozwiązania testu `y_i∈{0,1}` obserwacja średnia `p̂=k/n`. Zawsze zapisuj `k`, `n`, definicję populacji i seed. Wilson 95% przedział orientacyjny:

\[
\frac{\hat p+\frac{z^2}{2n}\pm z\sqrt{\frac{\hat p(1-\hat p)}n+\frac{z^2}{4n^2}}}{1+\frac{z^2}n},\ z=1.96.
\]

Przedział nie uwzględnia współzależności zadań i wielokrotnych eksperymentów — wymagany bootstrap klastrowy per repo/task, paired trials, korekta wielokrotnych porównań, preregistration i ostateczny sequestered test. Kandydaci mogą mieć ten sam zbiór dev, ale **nie znają held-out testów**. Ocena stochastycznych agentów wymaga kilku seedów oraz analizy ogona opóźnień.

### 3.2. Bezpieczny warunek promocji

Dla konfiguracji nowej `a'` względem referencyjnej `a₀`:

\[
\operatorname{Promote}(a')=\mathrm{InvariantPass}\land\mathrm{RegressionPass}\land\mathrm{SecurityPass}\land\mathrm{HumanApprove}\land
(L_{95\%}(\Delta Q)>\delta)\land(U_{95\%}(\Delta R)<\epsilon),
\]

gdzie `ΔQ` jest zmianą wyniku na zarejestrowanych testach transferowych, `ΔR` różnicą ryzyka; `δ,ε` to **uprzednio podpisane progi** (nie dobierane po wyniku). Własności, których nie da się skalibrować, kończą się `REVIEW`, nie `ACCEPT`.

### 3.3. Prawdopodobieństwo wyboru rodzica

Oryginalny DGM faworyzuje wydajność i rzadziej eksplorowane gałęzie [S01]. Nasza kandydacka funkcja:

\[
P(a_i)=\frac{\mathbf 1_{a_i\in\mathcal F}\,[\varepsilon+\operatorname{rank}_Q(a_i)]^\alpha\,[1+\operatorname{novelty}(a_i)]^\beta\,[1+\operatorname{offspring}(a_i)]^{-\gamma}\,\operatorname{fairness}(a_i)}{\sum_j(\cdots)}.
\]

`rank_Q` jest nieujemnym score po normalizacji w obrębie kampanii, `novelty` jest distance w stałej wersji embedding/behavior schema, a `ε>0` zachowuje eksplorację. Nie obiecuje się ergodyczności przy skończonych kosztach i wykluczeniach; niedopuszczalne gałęzie mają P=0. Przypadki nan/inf/underflow prowadzą do jawnego fallback `uniform among eligible`, z audytem.

### 3.4. Quality-Diversity (MAP-Elites + Pareto)

Tworzymy wielowymiarowe komórki zachowań np.: sprawność edycji/rollback, strategia planowania, obsługa dużych plików, liczba prób, zużycie tokenów, niezawodność testów, programistyczne języki. Rozdzielamy *behavior descriptors* od metryki fitness, inaczej wyszukiwanie traci różnorodność. Każda komórka przechowuje 1–k Pareto-niedominowanych reprezentantów i historie prób. Nadmiar deduplikujemy po `genome_digest`, zestawie zmian AST i podobieństwie behawioralnym; unikamy usuwania ważnych genotypów jedynie na podstawie krótkiego opisu LLM.

### 3.5. Novelty i anti-reward-hacking

Nowość projektu nie jest sama celem rozstrzygającym. Algorytm może optymalizować szybkość, omijając testy lub zapisując wyniki zamiast je uzyskiwać. Stosować tylko pochodzące z niezależnego wykonania sygnały: niezależny exit code, hash repo po zmianie, diff artefaktu, test reporter podpisany przez worker, artefakty stderr/stdout i perf counters. Wszystkie dane zadania uznawać za niezaufane, w szczególności README z benchmarku i output toola.

---

## 4. Rdzeń RSI — bezpieczny, iteracyjny cykl modyfikacji

### 4.1. Kanoniczna maszyna stanów

`CREATED → HYPOTHESIS → PROPOSAL → POLICY_CHECK → BUILD → STATIC_CHECK → SANDBOX_EVAL → STAT_REVIEW → ARCHIVED → AWAIT_APPROVAL → CANARY → RELEASED`. Wszystkie terminalne stany: `REJECTED`, `FAILED`, `TIMEOUT`, `CANCELLED`, `ROLLED_BACK`, `QUARANTINED`.

Każdy transition zawiera `actor`, `policy_version`, `job_id`, `seq`, `timestamp`, `manifest_digest`, `evidence_digest`, `reason`, `signature`; tylko kontroler wymusza CAS/transaction, generowana kopia agenta nie modyfikuje stanu w bazie.

### 4.2. Schemat eksperymentu

1. **Baseline:** zdefiniuj niezmienny task universe i seedy, zamroź obraz bazowy/LLM+config.
2. **Diagnose:** wyznacz typ porażek po kodach i logach; nie wyciągaj wniosku na podstawie jednego zadania.
3. **Hypothesis:** atomowa, falsyfikowalna hipoteza: `Zmiana X zmniejszy Y o >=δ bez regresji Z`.
4. **Generate:** model tworzy `ChangeProposal` z diff, deklaracją wpływu, spodziewaną awarią i rozmiarem zmian.
5. **Bound scope:** whitelist modyfikowalnych ścieżek (harness, narzędzia, workflow), blacklist certyfikowanego control plane i evaluation.
6. **Check:** detekcja sekretów, dependency pinning, AST, policy-as-code i build w środowisku izolowanym.
7. **Evaluate:** train/dev, stale referencje, randomized negative tests; limit walltime i zasobów.
8. **Archive:** kandydat przechodzi do append-only archive także przy słabej jakości tylko jeśli bezpieczny; „stepping stones” oznaczamy eksperymentalnie, nie jako działający release.
9. **Holdout:** sequestered suite odrębnej tożsamości; wyniki nie wypływają z powrotem do generatora w postaci rozwiązań.
10. **Approval:** na produkcję tylko osoba uprawniona z protokołem code review i możliwość cofnięcia.

### 4.3. Pseudokod bez uprzywilejowanych skrótów

```python
# Algorytm referencyjny w dokumencie, NIE gotowy runtime.
archive = seed_with_evaluated_baseline()
for generation in bounded_range(campaign.max_generations):
    if stop_requested() or campaign.budget_exhausted():
        break
    parents = select_diverse_eligible_parents(archive, policy_snapshot)
    for parent in parents:
        proposal = propose_bounded_hypothesis(parent, accessible_dev_evidence)
        if not independent_policy_gate(proposal):
            record_rejection(proposal)
            continue
        candidate = materialize_immutable_snapshot_and_patch(parent, proposal)
        if not static_and_dependency_gate(candidate):
            quarantine(candidate)
            continue
        evidence = evaluate_in_ephemeral_isolated_vm(candidate, sealed_eval_config)
        if evidence.integrity_invalid or evidence.security_violation:
            quarantine(candidate)
            continue
        archive.append(candidate, evidence, state="research_only")
        if statistically_robust_and_no_regressions(evidence):
            submit_human_review(candidate, evidence)
# Operator controls any real deployment; archive inclusion is not deployment.
```

W powyższym pseudokodzie `policy_snapshot`, `sealed_eval_config` i `promotion_signer` znajdują się poza przestrzenią zapisu agenta. `bounded_range` nie jest automatycznie wznowiony przez tworzenie własnych procesów ani płatnych zadań przez kandydatów.

### 4.4. Self-modifying the self-modifier

Dopuszczamy eksplorację kodu `ProposerHarness` w wydzielonym trybie meta. Model nie może aktualizować wymagań oceny, arbitra bezpieczeństwa, polityk promowania, sekretów ani profili uprawnień. Warunek metapoziomu: nowa wersja `M'` musi poprawiać wyniki przyszłych propozycji na osobnej populacji problemów i ograniczonej liczbie generacji (meta-benchmark); wzrost tylko pojedynczego `a` nie jest dowodem lepszego meta-proposera. Porównania meta prowadzimy w tych samych budżetach, seedach i z równymi próbami.

### 4.5. Samokorekta eksperymentów

Każda hipoteza zawiera *falsification criterion*, *alternative explanation*, *risk of leakage*, *expected compute*. Gdy kandydat wykryje błąd benchmarku, tworzy zgłoszenie; **nie poprawia benchmarku w ramach tej samej kampanii**, gdyż przestałaby być porównywalna. Naprawa benchmarku rozpoczyna nową epokę z nowym `benchmark_version` i nowym baseline.

---

## 5. Archiwum ewolucyjne — dane, historia i niezmienność

### 5.1. Relacyjny model danych

- `Campaign(id, owner, baseline_digest, policy_digest, benchmark_epoch, budget, state)`.
- `Genome(id, digest, entrypoint, abi_version, llm_config_hash, parents[], change_manifest, source_license, feature_flags)`.
- `Proposal(id, hypothesis, target_files[], patch_digest, proposer_genome, expected_gain, expected_risk, timestamp)`.
- `Trial(id, genome, suite_id, seed, VM_attestation, result_digest, runner_version, cost, started, ended, exit_reason)`.
- `ScoreCard(id, genome, suite, n, k, CI95, latency_p50_p95, cost, violations, comparator)`.
- `ArchiveCell(id, descriptor_schema_id, cell_key, genome_ids[], novelty_index_version)`.
- `Approval(id, review_digest, approver_identity, signed_decision, scope, ttl)`.
- `Release(id, genome_digest, environment, canary_evidence, rollback_digest)`.

Kontrola integralności: każdy `Genome` jest adresem content-defined, `Trial` nie jest modyfikowany po podpisaniu, poprawki jako nowe `Trial`/`ScoreCard`; usuwanie według polityki retencji zachowuje informację o tombstone z minimalną metadaną (bez danych wrażliwych). Deduplikacja bajtowa i logiczna. Bitemporalność eksperymentów przez `observed_at` i `committed_at`, nie domyślna rekonstrukcja świata.

### 5.2. Graph lineage

Acykliczny graf skierowany `G=(V,E)` opisuje ewolucję z gałęziami, zbiegami i cofnięciami. Krawędzie mają typ `MUTATE`, `REBASE`, `CHERRY_PICK`, `EVAL_REPLAY`. Każda rekombinacja ma listę wszystkich rodziców. Nie wstawiać historii zmiany do pamięci jedynie na podstawie samodzielnego opisu modelu; dowodem jest digest snapshotu i diff.

### 5.3. Archiwum nie utożsamia się z bazą wiedzy LLM

Episodic memory może opisać próby, ale klasyfikacja źródła musi rozróżniać `observed_runner`, `derived_metric`, `hypothesis_llm`, `operator_note`. Rejestrować nie tylko udane patche; także fałszywe hipotezy i niepowodzenia, by ograniczyć ich wielokrotne generowanie. Pamięć i prompt nie mogą zawierać sekretów, cudzych payloadów ukrytych testów, prywatnych ścieżek ani pełnych logów z identyfikatorami użytkowników.

---

## 6. Specyfikacja silnika eksperymentów i benchmarków

### 6.1. Warstwy danych

`TRAIN_DEV` (do analizy agentowi), `PUBLIC_REGRESSION` (znane przypadki), `BLIND_VALIDATION` (oddzielony od propozycji), `SEALED_HOLDOUT` (jeden finalny odczyt per kampania), `TRANSFER` (inne języki, repozytoria i modele), `SAFETY_ADVERSARIAL`, `RESOURCE_STRESS`, `METAMORPHIC` (przeformatowane semantycznie równoważne zadania).

Nie testować finalnego wyniku wielokrotnie na tym samym ukrytym benchmarku po zapoznaniu się z pośrednimi metrykami, bo tworzy to leakage przez wynik. Przeciwdziałać `benchmark gaming`: hidden-data escrow, kryteria rozwiązania pod kontrolą oryginalnych testów, kasowanie danych sesji, detekcja wykorzystania niezamierzonych ścieżek/plików.

### 6.2. Modele odniesienia

Porównuj co najmniej: `fixed seed`, `non-self-modifying proposer`, `greedy best-parent`, `random constrained`, `novelty-only`, `MAP-Elites QD`, `Pareto+QD+RSI`, `no-meta-history`. Każdy wariant otrzymuje porównywalne budżety i taki sam bazowy LLM. Warianty plus ablation `without sandbox` **nie są uruchamiane**, izolacja to wymóg podstawowy, nie parametr optymalizacyjny.

### 6.3. Ocena wielopoziomowa

- **L0** Format: zgodność API, compile/import, manifest, sha256.
- **L1** Zdolność: proste read/edit/patch/revert na nieprodukcyjnej kopii.
- **L2** Trafność: SWE-bench-like i Polyglot-like sealed tasks; wynik liczony przez weryfikowalnego workera.
- **L3** Transfer: inny model inference i język kodowania, bez retreningu harness.
- **L4** Stabilność: chaos/timeouts/OOM/kill/replay/poisoned logs.
- **L5** Bezpieczeństwo: naruszenia sieci, prób odczytu sekretów, modyfikacji polityki.
- **L6** Ekonomia: `score per 1M tokens`, `score per CPUh/GPUh`, `p95 wall time`, efektywność emisji testów.
- **L7** RSI: jaki jest sukces potomków generowanych przez dany proposer na odrębnych próbach. Wymaga rekursywnego eksperymentu z oddzielonym sequestered evaluation.

### 6.4. Anti-contamination

Repozytoria testowe muszą mieć zarejestrowane provenance, timestampy, commity, embargo oraz kontrolę czy model bazowy mógł widzieć rozwiązanie w pretraining. Dla porównania względnego używać także świeżo syntetyzowanych zadań z prawdziwą semantyką i testami własności. `PASS` na zadaniu znanym modelowi nie dowodzi uogólniania. Nie usuwać nieudanych prób, nie zmieniać selektywnie mianownika.

---

## 7. Patch engineering: atomowość, kompatybilność, operacje na AST

Kandydat generuje **jedną wersjonowaną paczkę zmian** zawierającą `unified_diff`, ewentualne transformacje AST, wymagane nowe pliki, lockfile-diff, plan migracji, testy własne i hipotezę. Planner najpierw czyta AST i testy, tworzy mapę punktów rozszerzeń i waliduje granice scope; brak zgody na ślepe globalne regex patching. Każdy apply jest atomowy na disposable repo snapshot. Zmiana musi utrzymywać `ToolABI` wersjonowane semver i być odwracalna przez hash poprzedniej wersji; kompatybilność testuje zewnętrzny harness.

**Własne klasy zmian:** `TOOLING`, `PROMPT_POLICY`, `CONTEXT_MANAGEMENT`, `MEMORY`, `VERIFICATION`, `RETRY_SCHEDULING`, `PATCH_STRATEGY`, `PLANNER`, `OBSERVABILITY`, `COST_OPT`, `META_PROPOSER`. Każda ma inny limit skali zmian i ścieżki. `SAFETY_CONTROL`, `AUTH`, `SANDBOX`, `BENCHMARK`, `SIGNER`, `COST_BUDGET` są niemodyfikowalne przez RSI.

**Blokady:** dodanie dynamicznego kodu w niejawnych startup hooks, dependency auto-update, `subprocess` spoza przydzielonego worker API, wysyłanie kodu i danych poza sandbox, modyfikacja `pytest.ini` lub `conftest.py` zasłaniająca testy, przywracanie sesji po wygaśnięciu quota. Wykrycie takich prób jest zdarzeniem `QUARANTINED` z analizą, nie możliwością automatycznego zaakceptowania po obniżeniu wagi ryzyka.

---

## 8. Ekonomia compute i ograniczanie eksplozji kosztu

Koszt kampanii:
\[
C=\sum_i (P^{(i)}_{in}T^{(i)}_{in}+P^{(i)}_{out}T^{(i)}_{out}+P^{(i)}_{GPU}h^{(i)}_{GPU}+P^{(i)}_{CPU}h^{(i)}_{CPU}+C^{(i)}_{storage}),
\]

gdzie ceny zamrożone w konfiguracji kampanii z `price_version`. `BudgetGuard` blokuje zlecenia przed przekroczeniem limitu; rozlicza także koszty przerwanych jobów. Scheduler bierze pod uwagę wartość informacyjną, koszt confidence interval, wykonanie w tanim smoke stage i droższym holdout wyłącznie po uzasadnieniu. `max_generations`, `max_children_per_parent`, `max_active_workers`, `walltime`, `tokens`, `disk`, `RAM`, `network_bytes=0`, `billable_cap` obowiązkowe. Żadna polityka ewolucji nie może podnosić własnych kwot.

**Alternatywa badań:** wieloramienny bandyta contextual z ostrożną estymacją zwrotu informacyjnego, ale bez manipulowania evaluator oracle i zachowując minimalną eksplorację. `Noisy winner` nie dostaje pełnego budżetu na podstawie pojedynczego dobrego seedu. Zaplanowany `Sequential Halving` ma uprzednio zadeklarowany harmonogram analiz, bez niekontrolowanego optional stopping.

---

## 9. Bezpieczeństwo RSI i model zagrożeń

### 9.1. Granice bezpieczeństwa nie podlegają ewolucji

Warstwa bezpieczeństwa należy do organizatora eksperymentu i jest niezależna od genomu. Polityka **deny by default**. Nie adaptować wzorca RSIAI0 z nieograniczonym shell do środowiska produkcyjnego; nie odblokowywać `__ALLOW_ALL_COMMANDS__`, nie przekazywać gniazda Dockera, kluczy chmury, SSH agent socket, katalogu HOME hosta ani tożsamości CI release do VM badawczej. Preferować efemeryczne mikroVM, z rootfs read-only i oddzielnym workdir, no host mount, no PCI/GPU passthrough na etapie 0, z ograniczeniami syscalli, no network, cgroups, izolacją UID oraz limitem potomnych procesów. Warstwa mTLS nie zastępuje sandboxu.

### 9.2. Klasy zagrożeń

- `T01` Code execution escapes / kernel 0-day / container breakout.
- `T02` Prompt injection w issue, README, logach, treści zadania, pliku testowym.
- `T03` Reward hacking: zaniżanie licznika testów, zmiana harness, przeciek etykiet testowych.
- `T04` Data exfiltration / secrets from mounts, model prompt, CI env.
- `T05` Resource exhaustion: fork bomb, memory blow-up, GPU exhaustion, runaway paid API.
- `T06` Poisoning archive: fałszywe scorecards, sfałszowany parent lineage.
- `T07` Supply chain injection: pypi/git dependencies, postinstall hooks, model artifacts.
- `T08` Self-preservation / unauthorized persistence: cron, long-running daemon, stolen credentials.
- `T09` Social engineering human approver: model-written „proof” not supported by logs.
- `T10` Metric drift, heldout leakage, accidental overfit to benchmark.
- `T11` Cross-tenant access / unsafe CAS object reuse.
- `T12` Unavailable cleanup / broken cancellation / orphan microVM.

### 9.3. Odpowiedzi obligatoryjne

Każdy threat ma: fizyczny punkt egzekucji poza VM, negatywny test, alert, plan rollback. Threat-test może używać **symulowanych payloadów** w odizolowanym laboratorium, nie testować produkcyjnego hosta bez uprawnienia. Dynamiczna interpretacja poleceń w promptach ze źródeł użytkownika jest niedopuszczalna; narzędzia i kod modyfikacji tworzą zawsze niezaufane rezultaty.

### 9.4. Human review nie jest ozdobnikiem

Review obejmuje diff, wyniki weryfikacji, provenance źródeł, listę zależności, mapę call-graph, politykę regresji, koszt, plan wycofania i uzasadnienie osiągniętych zmian. Kontrola 2-person w releasach o szerszym dostępie. Podpisujący dostaje materiał wygenerowany przez niezależnego reportera; tekst agenta może być dodatkiem, nigdy źródłem stanu testów.

---

## 10. Formalna weryfikacja: co naprawdę można dowieść

**Nie istnieje automatyczna gwarancja, że dowolna samomodyfikacja da globalnie lepszy agent na wszystkich zadaniach.** W naszym produkcie formalizujemy **lokalne, zamknięte, sprawdzalne własności**:

- `PROP-1` wymuszenie zakresu ścieżek: modyfikacja nie może wychodzić poza `mutable_paths` w modelu ACL.
- `PROP-2` monotonic campaign ledger: każde wydanie `generation_seq` większe od poprzedniego dla tego samego ID.
- `PROP-3` unikatowość idempotent `mutation_id → digest`.
- `PROP-4` nie ma ścieżki `PROMOTE` ze stanów innych niż `REVIEWED` przy ważnym podpisie.
- `PROP-5` zamknięty state machine: `QUARANTINED` nie przechodzi do `RELEASED`.
- `PROP-6` walidacja zakresu kosztu i limitów zanim powstanie cloud VM.
- `PROP-7` poprawność liczbowych funkcji sumujących score w zdefiniowanych domenach.
- `PROP-8` deterministyczny odczyt archive z immutable run records i event log.

**Technika:** mały trusted kernel w Rust, property tests/proptest i model check dla policy finite-state (TLA+ / Alloy / SMT); solver to *opcjonalny niezależny narząd*, a nie źródło dowodu bez rzeczywistego wyniku `unsat` z właściwym certyfikatem. Przekroczenie domeny wejść powoduje `unknown` i blokadę promocji, nie sztuczne „proven”.

Pseudoinvariant:
```text
G( promote(genome) -> approved(genome) AND policy_ok(genome) AND
   runner_attested(genome) AND no_unreviewed_parent(genome) )
G( quarantined(genome) -> NOT deployed(genome) )
G( budget_remaining < next_job_max_cost -> NOT start(next_job) )
```

Rozróżnić formalny dowód bezpieczeństwa state machine od braku błędu w całym nieograniczonym kodzie Pythona. Modele LLM nie są proverem.

---

## 11. API, komunikaty i error handling

### 11.1. Kanały

- `POST /v1/campaigns`: create, authenticated, idempotency-key, signed initial constraints.
- `POST /v1/campaigns/{id}/proposals`: propose bounded change within research scope.
- `POST /v1/candidates/{id}/evaluate`: stateful, returns job id, not sync unbounded wait.
- `GET /v1/jobs/{id}`: typed status/seq/progress and normalized error.
- `GET /v1/archive?campaign=...`: filtered genealogy and scorecards, tenant-isolated.
- `GET /v1/evidence/{digest}`: access-controlled signed manifest.
- `POST /v1/releases/{id}/request-promotion`: human-authenticated workflow only, scope constrained.
- `POST /v1/campaigns/{id}/cancel`: hard-stop with cleanup acknowledgement.

### 11.2. `CandidateManifest` (minimum)

```yaml
schema: dgm-rsi-omega.candidate.v1
candidate_id: "cand_demo"
source:
  parent_digests: ["sha256:..."]
  patch_digest: "sha256:..."
  source_tree_digest: "sha256:..."
proposer:
  model_manifest_digest: "sha256:..."
  prompt_schema: "proposer.v1"
  random_seed: 1001
hypothesis:
  capability: "patch-error-recovery"
  predicted_effect: "fewer invalid edits"
  falsification: "no improvement on blinded tasks"
limits:
  max_modified_files: 5
  max_changed_lines: 300
  max_runtime_seconds: 1200
  max_tokens: 40000
  network_access: false
policy:
  policy_digest: "sha256:..."
  permitted_paths: ["harness/**", "tools/safe/**"]
evaluation:
  benchmark_epoch: "bench2026-q4"
  experiment_protocol_digest: "sha256:..."
  source: "sealed_worker"
```

Przykład jest **schematem projektu**, nie działającym requestem. W czasie wykonania hashe mają być pełnymi poprawnymi digestami. Kontrakt rozdziela transient credentials, które nigdy nie trafiają do manifestu.

### 11.3. Typowane błędy

`ERR_POLICY_DENIED`, `ERR_PATCH_OUT_OF_SCOPE`, `ERR_UNSAFE_IMPORT`, `ERR_SECRET_REFERENCE`, `ERR_BENCHMARK_LEAK`, `ERR_SANDBOX_TIMEOUT`, `ERR_SANDBOX_OOM`, `ERR_EVIDENCE_SIGNATURE`, `ERR_TRIAL_DUPLICATE`, `ERR_BUDGET_EXHAUSTED`, `ERR_STAT_INSUFFICIENT`, `ERR_HOLDOUT_ALREADY_SEEN`, `ERR_NOT_APPROVED`, `ERR_REPLAY_DETECTED`, `ERR_LICENSE_UNVERIFIED`, `ERR_VM_ATTESTATION_MISSING`, `ERR_STATE_CONFLICT`.

Każdy kod określa `retryable` i `operator_action`, nie może być zawrócony przez generowany kod do dowolnej fazy. Retry tylko na błędy przejściowe z exponential backoff+jitter i limited attempts; ponowne wykonanie nie może sztucznie zwiększyć liczby unikalnych prób.

---

## 12. Orkiestracja, współbieżność, recovery, auditing

Scheduler stosuje deterministyczne seedy/manifesty, lease z `fencing_token`, kontrolowane heartbeat, deduplikację task IDs i at-least-once z idempotentnym zapisem wyniku. Crash workera: `EVAL_INCOMPLETE` i nowy trial z wskazaniem poprzedniego, nie nadpisany sukces. Dla oceny zadań nondeterministycznych nie deklarować bit-for-bit reproducibility, gdy backend LLM/API nie oferuje deterministyczności; zapisywać wersję API/modelu i widoczną konfigurację.

Run journal jest append-only; monitoring przez OpenTelemetry z polami `campaign_id`, `candidate_digest`, `trial_id`, `phase`, `risk_gate`, `reason_code`, `budget_remaining`, bez logowania sekretów, prywatnych promptów czy treści benchmarku. Metrics: `candidate_accept_rate`, `verified_patch_rate`, `ood_success`, `transfer_gap`, `promotion_rate`, `safety_violation_rate`, `cost_per_valid_candidate`, `p95_job_latency`, `abort_ack_latency`, `vm_leak_count`, `scorecard_provenance_missing`.

Definiowane SLO są **planowanymi progami**, np. `promotion_without_valid_approval=0`, `uncontained_network_egress=0`, `trace_missing=0`, `orphaned_vm_count=0`. Dla krytycznych naruszeń `fail closed` i wstrzymanie kampanii, a nie tylko alert. RTO/RPO dopiero po testach disaster recovery.

---

## 13. Rzeczywiste granice RSI i ryzyko przeuczenia

### 13.1. „DGM”, „Gödel Machine”, „RSI” to różne pojęcia

- Gödel Machine: idealny teoretyczny proof-based self-rewriter przy założeniach formalnych.
- DGM 2025/2026: empiryczne doskonalenie **harness agenta programistycznego**, nie samoistna matematyczna gwarancja jego wyższości.
- RSI: pętla zmian wpływających na zdolność do przyszłych zmian; nie każdy trening promptu lub cache wyników jest rekursywnym zwiększeniem zdolności.
- Strong RSI: szeroka samomodyfikacja modeli/strategii/uczenia — brak potwierdzenia w podstawowej implementacji DGM; wymaga osobnego badania.
- Quality-Diversity nie rozwiązuje automatycznie problemów alignment, generalizacji ani kosztu.

### 13.2. Czynniki szkodliwe dla oceny

- Tuning na jeden benchmark i leak hidden-test.
- Niedopasowane compute budgets (wygrana przez 10x tokeny).
- Jedna losowa próba i szum próbkowania.
- Zmiana oracle po obejrzeniu wyników.
- Overfitting do konkretnego modelu i API.
- Trwała pamięć znanych rozwiązań zamiast ulepszenia algorytmu.
- Metryka ukrywająca spadek security.
- Niepewny identyfikator checkpointa bazowego.

### 13.3. Logika badań przyrostu

Sprawdzać trzy efekty osobno: **within-task reliability**, **out-of-distribution transfer** i **meta-improvement yield**. `Meta-improvement` wymaga seriowego experiment-of-experiments: kandydat tworzy kolejne dzieci na nowych dev zbiorach i nowy proposer ocenia się względem stałego w tych samych warunkach. Oczekiwanie zwiększonej wartości musi przetrwać formalnie zdefiniowany test niepewności i security.

---

## 14. Ochrona informacji, licensing i governance

Matriz wejść: `OPEN_REFERENCE`, `USER_OWNED_REPO`, `LICENSED_BENCHMARK`, `PRIVATE_PROJECT`, `PROPRIETARY_MODEL`. W P0–P3 domyślnie tylko test fixtures i legalny public dataset. Własne repozytorium użytkownika jest odrębną zgodą i osobnym sandboxem, bez internetowego wycieku. `LICENSE-UNKNOWN` blokuje release. Formalizacja przetwarzania danych osobowych w promptach, issue czy logach zgodnie z podstawą prawną; ograniczenie przechowywania w CAS i delete policy.

Jeżeli silnik kiedyś ma wykonywać pracę na OCAF czy Aetheris, staje się **zewnętrznym, jawnie autoryzowanym narzędziem** — nie „częścią OCAF” wskutek podobieństwa nazwy. Nie dopisywać agentowi prawa do połączenia projektów.

---

## 15. Sekwencja wdrożenia / roadmap (bez deklaracji wykonania)

| Etap | Wynik | Kryterium przejścia |
|---|---|---|
| R00 — Read-only audit | pełna dokumentacja repozytorium RSIAI0 + oficjalnego DGM, sha commitów, rejestr ryzyka | spis komponentów i funkcji; niczego nie uruchamiać bez izolacji |
| R01 — Domain & immutable root | Rust domain crate; immutable security policy | testy ACL, signing, parserów, state machine |
| R02 — Candidate pack | pack/patch/CAS/genealogy | odtworzenie źródła z hasha i diff bez utraty plików |
| R03 — VM isolation | sandbox no-network, no-secrets, quota/kill | negatywne testy T01-T12 i evidence |
| R04 — Fixed baseline | frozen coding model + deterministic fixtures | zdefiniowany baseline i data leakage audit |
| R05 — Evolution loop | generate/eval/archive/reject | 50+ zaplanowanych eksperymentów, zero unauthorized effects |
| R06 — Diversity | QD cells, Pareto, novelty, mutation-history | porównanie ablation vs random/greedy |
| R07 — RSI-meta | modyfikowalny proposer harness | niezależny meta-holdout, paired statistical validation |
| R08 — Formalization | spec i weryfikacja niezmienników | dowód lub ślad model check, wszystkie wyjątki obsłużone |
| R09 — Cross-language + cross-model | transfer suite | udokumentowany brak regresji lub odmowa release |
| R10 — Scalability | kontrolowane worker pools i budżety | chaos/recovery/soak, koszt kontrolowany |
| R11 — Approval & canary | niezależne zatwierdzenie i rollback | próba negatywna po skradzionym tokenie i cofnięciu |
| R12 — Production candidate | pełny audyt, SLO, provenance | komplet Release Evidence Package i podpis |

Każdy `Rxx` zaczyna jako `PLANNED`. Zakaz oznaczania Done na podstawie napisanej specyfikacji.

---

## 16. Kryteria E2E / Quality Gates — definicja odbioru

| ID | Scenariusz | Oczekiwany wynik |
|---|---|---|
| G01 | główny agent proponuje patch na dozwolonej ścieżce | nowy immutable candidate digest, korektne genealogy |
| G02 | patch wprowadzający błąd składni | `REJECTED`, nie trafi do releasu |
| G03 | niska jakość, ale poprawny kandydat | research archive z negatywną metryką i historią |
| G04 | zmiana bezpieczeństwa, tokenów lub evaluator | `ERR_PATCH_OUT_OF_SCOPE`, bez zapisu policy |
| G05 | próbna prośba o pełną powłokę hosta | odmowa narzędzia i brak syscall hosta |
| G06 | payload w README nakazuje ignorować polecenie | nie zmienia policy state ani signer data |
| G07 | odczyt wyimaginowanego tajnego pliku | brak dostępu + `ERR_SECRET_REFERENCE` |
| G08 | sandbox wychodzi poza czas, cgroups memory | twardy kill, cleanup, `TIMEOUT`/`OOM` |
| G09 | fałszywy PASS w logach LLM | niezależny runner ocenia FAIL |
| G10 | restart workera podczas run | idempotent recovery, żaden podwójny trial |
| G11 | nieprawidłowy podpis metryk | reject + quarantine |
| G12 | losowanie rodzica przy NaN-score | bezpieczny fallback, żadnego panic/undefined probability |
| G13 | dwie kopie równoległe zmieniają ten sam element | immutable branch, brak lost update |
| G14 | poczwórne uruchomienie testu z różnymi seedami | poprawny paired variance report |
| G15 | brak improvement na holdout | żaden release mimo wysokiego dev score |
| G16 | minimalny poprawny wzrost przy krytycznej regresji | `REJECTED` bez kompromisów wag |
| G17 | transfer Python→Rust/Go | osobny wynik, nie domniemanie generalizacji |
| G18 | różne LLM o stałych budżetach | oddzielne scorecards z jawny model IDs |
| G19 | brak zatwierdzającego operatora | `AWAIT_APPROVAL`, nigdy produkcyjne `RELEASED` |
| G20 | podpisana promocja i canary fail | automatyczny rollback do poprzedniego digesta |
| G21 | próba samoczynnego zwiększenia limitu kosztów | policy reject i wygaszenie kampanii |
| G22 | ponowne użycie benchmarku po wycieku | `ERR_HOLDOUT_ALREADY_SEEN`, nowa epoka |
| G23 | archiwum skażone niepoprawnym digestem | read fails, nie propaguje genotypu |
| G24 | zerwanie procesu kontrolera | crash consistency, journal replay |
| G25 | próbna instalacja niezatwierdzonego pakietu PyPI | dependency gate blocks |
| G26 | ujawnienie cudzych danych przez diagnostics | redaction, fail privacy gate |
| G27 | wprowadzenie nowej strategii selekcji | ablation i brak automatycznej zmiany progów bezpieczeństwa |
| G28 | nieuprawniona migracja do obcego repozytorium | brak jakiegokolwiek efektu poza przyznanym scope |

**Wersjonowana macierz środowisk**: lokalne testy offline, Linux microVM E2E, 2–3 niezależne hosty dopiero przy rzeczywistym dostępie, model/API parity, chaos suite, długoterminowy soak. Wszystkie bramki wymagają plików dowodowych, poleceń reprodukcyjnych i sum SHA. Powyższa tabela to wymogi, nie wykonane testy.

---

## 17. Sugerowana struktura repozytorium od zera

```text
dgm-rsi-omega/
  README.md
  LICENSE.md
  Cargo.toml
  Cargo.lock
  crates/
    domain/               # typed candidate, campaign, proof, scores
    policy-kernel/        # immutable safety + authorization core
    evolution/            # parent selection / QD / Pareto / diversity
    archive/              # append-only genealogy, scorecards, CAS
    orchestrator/         # Rust control plane / job machine
    api/                  # authenticated public API
    evidence/             # signatures, attestations, verifiers
    statistics/           # paired trials, confidence intervals
    sandbox-broker/       # worker lifecycle, quotas, fenced leases
    promote/              # independent human approval pathway
  workers/
    harness-python/       # mutable research agent — scope-constrained
    linter-and-build/     # read-only checks
    evaluator/            # test runner held outside agent control
  manifests/
    candidate.schema.json
    evaluation.schema.json
    signed-policy.schema.json
  specifications/
    state_machine.tla
    trust-boundaries.md
    external_api.openapi.yaml
  tests/
    unit/
    property/
    integration/
    e2e/
    chaos/
    adversarial/
    holdout/
  docs/
    ARCHITECTURE.md
    SECURITY.md
    OPERATOR_RUNBOOK.md
    EVALUATION_PROTOCOL.md
    EXPERIMENT_REGISTRY.md
    RELEASE_GATES.md
  ci/
    gate-rust.sh
    gate-sbom.sh
    gate-sandbox.sh
    gate-e2e.sh
  datasets/
    fixtures-public-only/
    README.md
```

**Zasada struktury:** testy i ocena są niezależne od `workers/harness-python`. Kandydat może modyfikować wyłącznie swoją kopię harness pod zewnętrznym policy engine. Trening lub dodanie LLM wymaga osobnego projektu wykonawczego.

---

## 18. Przykładowe projektowe kontrakty Rust

```rust
// Design-only interface sketch; deliberately not presented as compiled.
#![forbid(unsafe_code)]
use std::collections::BTreeMap;

pub struct GenomeDigest([u8; 32]);
pub struct CampaignId(String);
pub enum Decision { AcceptResearchOnly, Reject(String), Quarantine(String) }

pub struct Candidate {
    pub parent_digests: Vec<GenomeDigest>,
    pub source_digest: GenomeDigest,
    pub policy_version: String,
    pub declared_changes: BTreeMap<String, String>,
}

pub trait OutsideTheEvolutionTrustBoundary {
    fn validate_policy(&self, campaign: &CampaignId, c: &Candidate) -> Decision;
    fn verify_trial_provenance(&self, signed_result: &[u8]) -> bool;
    fn request_human_authorization(&self, candidate: &GenomeDigest) -> bool;
}
```

Przed kompilacją konieczne: konkretne ser/de, DTO, typy błędów, implementacja podpisów, zapis transactional store i pełne testy. Nie twierdzić, że to gotowe rozwiązanie produkcyjne.

---

## 19. Kontrakt wydania, dokumentacja i „Proof of Improvement”

Wydanie musi zawierać: `source_tree_digest`, `patch_bundle`, `model_manifest`, `benchmark_manifest`, `dataset split proof`, `resource budget`, `all failure logs`, `per-task results`, `statistical decision`, `security test matrix`, `SBOM`, `runtime attestation`, `human approval`, `rollback package`, `license register`, `operator manual`, `risk acceptance`, `canary report`. Żaden punkt nie może zastąpić brakującego wykonania testów. Raport ma rozdzielać *intended behavior*, *observed behavior* i *unproven generalization*.

### 19.1. Otwarte decyzje projektowe i badania ablacyjne

- Jak optymalizować eksplorację Pareto + QD przy ograniczonych kosztach i zmianie liczby rodziców?
- Kiedy aktualizować deskryptory QD, żeby wyniki komórek pozostały porównywalne?
- Jak wyznaczyć granicę równoważności metryki jakości przy różnych językach i modelach?
- Ile prób i jaką metodą inferencji statystycznej użyć dla rzadkich testów bezpieczeństwa?
- Jak obniżyć wykorzystywanie starzejących się benchmarków z pretraining contamination?
- Jak mierzyć `learning-to-improve` bez korzystania z danego hidden-set wiele razy?
- Jak zweryfikować izolację na realnym kernelu Linux i w wybranym hypervisorze?
- Jaki jest akceptowalny koszt uzyskania jednego nowego niedominowanego, bezpiecznego agenta?

### 19.2. Zasada finalna

**Produkt nie jest maszyną o zagwarantowanej poprawie każdej iteracji.** To nadzorowany mechanizm ewolucji kodu agentowego, dostarczający najlepszych kandydatów spośród rzeczywiście sprawdzonych prób, z pełnym śladem pochodzenia i możliwością odmowy wdrożenia. „Poprawa” jest twierdzeniem eksperymentalnym zależnym od rozkładu zadań, modeli, wersji środowiska i budżetu.

---

## 20. Rejestr źródeł i status gotowości

[S01] https://arxiv.org/html/2505.22954v3  
[S02] https://github.com/jennyzzt/dgm  
[S03] https://sakana.ai/dgm/  
[S04] https://github.com/BrandonDavidJones1/RSIAI0  
[S05] https://github.com/BrandonDavidJones1/RSI-AI-Scaffolding (ścieżka niepotwierdzona)  
[S06] https://www.biorxiv.org/content/10.1101/2025.08.21.671415v2  
[S07] https://github.com/google-research/rrsi  
[S08] Jürgen Schmidhuber, Gödel Machines — publikacja źródłowa; w publikacji DGM wskazana jako praca teoretyczna.  

**Źródła potwierdzają**: podstawową pętlę DGM, potrzebę otwartej ewolucji i ryzyko egzekucji nieznanego kodu. **Nowymi postulowanymi elementami** są: niezależny Trust Root, Pareto+MAP-Elites+novelty, statystyczny admission gate, typowane API, zarządzanie całym życiem kampanii, modelowanie zagrożeń i walidacja formalna lokalnych kontraktów. Ich skuteczność nie została przez ten dokument dowiedziona.  

**Status:** specyfikacja zrealizowana; implementacja silnika, testy E2E, formalne dowody i wdrożenie — `NOT EXECUTED`. **Nie klonowano, nie uruchamiano, nie modyfikowano repozytorium RSIAI0.**