# IMANDRAX Ω ENGINE — Master Blueprint v1.3 (29.10.2026)

**Zakres:** samodzielny silnik matematyczny; bez OCAF i Aetheris. **Stan:** indeks wiedzy zaimplementowany lokalnie; solver, biblioteki i modele NIE zostały wdrożone.

## CZĘŚĆ A — rozszerzenie normatywne v1.3

# IMANDRAX Ω ENGINE — Mathematical Knowledge, Proof & Scientific Reasoning Architecture v1.3

**Status:** `SPECIFIED`; indeks źródeł i wyszukiwarka FTS: `LOCALLY_IMPLEMENTED_AND_TESTABLE`; integracje solverów, trening modeli, formalne dowody i wdrożenie: `NOT_IMPLEMENTED/NOT_VERIFIED`.  
**Data:** 2026-10-29. **Projekt:** samodzielny IMANDRAX Ω. **Zakaz mieszania zakresów:** brak zależności od OCAF Runtime, Aetheris, DGM–RSI.  
**Wkład:** wszystkie dostarczone PDF, sześć poprzednich plików IMANDRAX v1.2 i 16 wskazanych repozytoriów; granice pokrycia jawnie opisane.

## 0. Rozdzielenie pięciu znaczeń słowa „wiedza”

1. **Taksonomia** — MSC2020 przypisuje tematy i relacje, nie dostarcza dowodów. 6603 kodów w oficjalnym źródle, z czego 6006 szczegółowych.
2. **Komentarz encyklopedyczny** — 6006 opisów z załączonej encyklopedii, plus 307 haseł jej indeksu; nie oznacza recenzowanych twierdzeń ani formalnych aksjomatów.
3. **Biblioteka formalna** — mathlib4/Iris i poprawne proof terms w konkretnym toolchain Lean; tylko teorematy sprawdzone przez jądro mogą uzyskać `PROVED_STRICT` w deklarowanym środowisku.
4. **Wynik obliczeniowy/eksperymentalny** — MuJoCo, Optax, dm_control, RegressLM, representations4d, science-skills, 3d-shapes. Wynik wymaga tolerancji, niepewności, źródła, seeda, replikacji; nie jest dowodem matematycznym.
5. **Hipoteza i badanie** — mathematics_conjectures, AlphaGeometry, otwarte problemy Clay, conjecture search. Hipoteza pozostaje `OPEN` lub `CANDIDATE` do czasu niezależnej weryfikacji.

**Nie wolno** utożsamiać zaindeksowania 6006 kodów z udowodnieniem 6006 twierdzeń ani obecności repozytorium z wdrożeniem jego funkcji.

## 1. Pełny zakres materiałów źródłowych

| Źródło | Faktycznie dostępna zawartość | Artefakt pochodny | Stan |
|---|---|---|---|
| `MSC_2020_261029_010708.pdf` | 224 strony oficjalnej klasyfikacji MR/zbMATH | `MSC2020_OFFICIAL_6603_CODES.jsonl` | 63 klasy, 534 podklasy, 6006 kodów szczegółowych — kompletność identyfikatorów sprawdzona |
| `ENCYKLOPEDIA_WIEDZY_MATEMATYCZNEJ_MSC2020_CLAY_261029_024707.pdf` | 1151 stron, komentarze regułowe i 307 pojęć | `MSC2020_ENCYCLOPEDIA_6006_ENTRIES.jsonl`, `.md`, `MATH_ATLAS_307_CONCEPTS.jsonl` | 6006/6006 kodów zgodnych z MSC2020, 307/307 pojęć |
| `classifications2010_261029_010830.pdf` | 47 stron MSC2010 | `MSC2010_REFERENCE_CODES.jsonl`, `MSC2010_TO_2020_CODE_CROSSWALK.jsonl` | 6198 identyfikatorów wykrytych; zgodność kodu nie dowodzi zgodności znaczenia |
| `Rozumowanie Matematyczne.pdf` | 14 stron | istniejący rejestr 239 `RM-Pxx-yy`, `REASONING_14_PAGES_EXTRACTED.md` | 239 wystąpień; wymogi nadal projektowe |
| `Front Matter.PDF` | 10 stron front matter książki SIAM | `SIAM_FRONT_MATTER_SCOPE.md` | spis treści i wstęp, **bez pełnych rozdziałów** |
| Sześć plików IMANDRAX v1.2 | blueprint, math engine, 14-page traceability, requirements, transcription, security | `IMANDRAX_OMEGA_ENGINE_BLUEPRINT_v1.3.md` | poprzednie wymagania zachowane i rozszerzone |
| 16 repozytoriów `mojealterego/*` | root, README, wybrane moduły, gałąź, SHA, root LICENSE | `REPOSITORY_AUDIT_16.md` | przegląd struktury, **bez pełnego importu kodu i uruchomienia** |

## 2. Architektura referencyjna

```text
                   IMANDRAX Ω — API / CLI / Knowledge UI
                                  │
                   Ω-Request Typing & Intent Router
                                  │
                 Ω-Math Ontology / MSC2020 + 2010 Index
                     │       │       │       │
             Ω-Theorem   Ω-Numeric  Ω-Research  Ω-Physical
              Retrieval    Compute    Hypotheses  Simulation
                 │          │         │           │
             Lean4/SMT  Interval/LP  DDAR/ML   MuJoCo/JAX
                 │          │         │           │
                 └──────────┴─────────┴───────────┘
                                  │
                    Ω-Claim Typing & Evidence Gate
                                  │
                       Ω-Proof/Result Ledger
                                  │
                     Ω-Independent Proof Checker
                                  │
                 PROVED / BOUNDED / ESTIMATED / UNKNOWN
```

**TCB:** parser dowodów, jądro logiki, checker certyfikatów, semantyka typów, wersjonowany rejestr aksjomatów i walidator pochodzenia. Retrieval, LLM, notebooki, biblioteki ML, silniki fizyki, źródła PDF, katalogi linków i zewnętrzne solvery **nie są zaufanym jądrem**.

## 3. Kanoniczny graf wiedzy Ω-MathGraph

### 3.1. Typy węzłów

`MSCClass`, `MSCSubcategory`, `MSCDetail`, `Concept`, `Definition`, `Axiom`, `Theorem`, `Conjecture`, `ProofTerm`, `Lemma`, `Algorithm`, `NumericalMethod`, `OptimizationProblem`, `PhysicsModel`, `Dataset`, `Experiment`, `SoftwareSymbol`, `RepoSnapshot`, `Publication`, `Evidence`, `Assumption`, `Counterexample`, `License`, `ResearchQuestion`.

### 3.2. Typy krawędzi

`IS_A`, `HAS_MSC`, `REFERS_TO`, `DEPENDS_ON`, `FORMALIZES`, `USES_AXIOM`, `PROVED_BY`, `REFUTED_BY`, `APPROXIMATES`, `BENCHMARKED_ON`, `DERIVED_FROM`, `CITES`, `CONTRADICTS`, `EXPERIMENTALLY_SUPPORTS`, `LICENSED_UNDER`, `SAME_CODE_AS_2010`, `REQUIRES_VERIFICATION`.

Każda krawędź `FORMALIZES` musi wskazywać konkretną definicję i dokładny typ w formalnym systemie. Sama zbieżność słów `topology`/`Topology` lub `analysis`/`Analysis` nie wystarcza. Krawędź `SAME_CODE_AS_2010` nie implikuje semantycznej równoważności. Kontradykcja między źródłami nie jest rozstrzygana przez głosowanie LLM.

### 3.3. Rekord kanoniczny

```json
{
  "id": "urn:imandrax:msc2020:15A18",
  "type": "MSCDetail",
  "title": "Eigenvalues, singular values, and eigenvectors",
  "msc2020": ["15A18"],
  "source": {"file_sha256": "sha256-of-user-supplied-pdf", "page": 201, "document": "MSC2020"},
  "claim_kind": "SOURCE_TAXONOMY",
  "assurance": "INDEXED_ONLY",
  "proof_term_digest": null,
  "dependencies": [],
  "license": "CC BY-NC-SA 4.0 when redistributing official MSC data",
  "review_state": "NOT_FORMALIZED"
}
```

Przykład jest kontraktem schematu; numery stron i sumy w rzeczywistych indeksach muszą pochodzić z plików, nie z przykładowego rekordu. `source.file_sha256` obowiązkowe dla rzeczywistych artefaktów.

### 3.4. Bitemporalność i pochodzenie

Każdy fakt ma `valid_from`, `valid_to`, `observed_at`, `source_revision`, `source_digest`, `import_batch_id`, `claim_status`, `evidence_digest`. Stan hipotezy Clay lub repozytorium w 2026 nie może być retroaktywnie podstawiony do archiwalnej wersji MSC2010. Dowód formalny zapisuje `axiom_set_hash`, `theory_version`, `lean_toolchain`, `mathlib_commit`, `kernel_version`.

## 4. Równoległe warstwy reprezentacji matematyki

### 4.1. Typed Math IR

`Nat`, `Int`, `Rational`, `AlgebraicReal`, `Real`, `Complex`, `Interval`, `Float<format,rounding>`, `Probability`, `Measure`, `Unit<SI>`, `Vector<T,n>`, `Matrix<T,m,n>`, `Tensor<T,shape>`, `Manifold<dim>`, `LieGroup`, `HilbertSpace`, `Distribution`, `StochasticProcess`, `DifferentialEquation`, `ControlSystem`, `Graph`, `GeometryConfiguration`, `QuantumState`, `QuantumChannel`, `Theorem<Context,Statement>`.

Dla typów `Float` wynik ma `rounding_mode`, `machine_epsilon`, `overflow/underflow_policy`, `NaN_policy`; dla `Interval` wymagane zaokrąglenie na zewnątrz; dla `QuantumState` warunek `ρ ≽ 0` i `Tr(ρ)=1` w tolerancji lub z dowodem.

### 4.2. Semantyka deklaracji

- `Theorem`: kontekst Γ, formuła φ, dowód p, `Γ ⊢ p : φ`, checker `check(p,Γ,φ)=true`.
- `BoundedProperty`: model M, bound k, własność φ, metoda eksploracji, świadectwo; wniosek dotyczy tylko zakresu `k`.
- `NumericalClaim`: model, dane, algorytm, przedział [l,u], metoda certyfikacji, błąd zaokrąglenia i tolerancja.
- `StatisticalClaim`: rozkład lub założenia o próbie, estymator, n, poziom ufności, korekta wielokrotnych testów.
- `SimulationClaim`: symulator, parametry, seed, krok, warunki brzegowe, ślad i replikacje; nigdy automatycznie `PROVED`.
- `Conjecture`: sformułowanie, źródło, status publiczny, próby dowodu, kontrprzykłady, ograniczenia.

## 5. Natywny Ω-Lean Bridge — cztery repozytoria formalne

### 5.1. Build matrix

1. Przypnij cztery repozytoria po SHA z `REPOSITORY_AUDIT_16.md` i ich własne `lean-toolchain` oraz `lake-manifest.json`.
2. Ustal kompatybilność; **nie zakładaj**, że dowolne HEAD-y mathlib4/batteries/Iris/MIL budują się razem.
3. `lake build` i `lake test` uruchamiaj w izolacji, z cache zawartościowo adresowanym, bez nieweryfikowanego network egress.
4. Indeksuj deklaracje przez środowisko Lean, nie regexem po źródle; zachowuj type, namespace, imports, universe params, docstrings i axioms.
5. Wykonuj `#print axioms`/programową kontrolę zależności i weryfikację proof term w jądrze.
6. W wynikach rozróżniaj dowody konstruktywne, klasyczne i domenowe; `propext`, `Classical.choice`, `Quot.sound` i inne założenia jądra mają jawne klasy.

### 5.2. Proof translation gate

Tłumaczenie DDAR/SMT/CAS → Lean jest niezaufane. `translate(candidate) -> LeanDecl` jest dopuszczalne, ale `PROVED_STRICT` dopiero gdy Lean kernel sprawdzi zamknięty term i zaakceptowane aksjomaty. `unsafe`, `sorry`, `admit`, niezaufane FFI, ukryte aksjomaty i nieudokumentowane `opaque` w krytycznej ścieżce powodują `REJECT` lub `CONDITIONAL`.

### 5.3. Iris — współbieżność i logika separacyjna

Docelowe obowiązki dowodowe: invariants, race freedom w określonym modelu, resource ownership, protocol progress, memory safety dla wybranych modeli. Utrzymuj mapę `source_program -> operational_semantics -> theorem`; nie deklaruj dowodu bezpieczeństwa kodu produkcyjnego bez zweryfikowanej translacji semantyki.

## 6. Ω-Geometry Proof Engine (AlphaGeometry)

Wejście: konfiguracja punktów/linii/okręgów, jawne non-degeneracy assumptions, reguły konstrukcji. Etapy: symbolic deduction (DD), algebraic reasoning (AR), auxiliary construction search (DDAR), niezależna weryfikacja wszystkich kroków, opcjonalna formalizacja Lean. Numeryczne szkice i rysunki są tylko heurystyką.

Wymagania `GEO-001..010`: orientacja, kolinearność, równoległość, prostopadłość, okręgi, równości kątów, degeneracje, wieloznaczne konstrukcje, niezależny checker, replay dowodu. Test negatywny: wprowadź konfigurację z zerową długością odcinka i potwierdź odmowę wnioskowania wymagającego dodatniej długości.

## 7. Ω-Numerical & Optimization Core

### 7.1. Certyfikowane obliczenia

- Exact arithmetic: BigInt/BigRational; redukcja przez gcd, limity rozmiaru liczb.
- Interval arithmetic: arytmetyka z outward rounding, dzielenie przez przedział zawierający zero → wyjątek domenowy lub rozbicie.
- Linear algebra: `Ax=b` i residual `r=b-Ax`, normy, condition number, verified enclosures; nie ogłaszaj równości dokładnej na podstawie małego residuum.
- Nonlinear: interval Newton/Krawczyk z jawnym zakresem i sprawdzeniem warunków.
- ODE/PDE: discretization error, stability, CFL/step, boundary conditions, adaptivity, validated bounds jeśli osiągalne.
- LP/QP: primal/dual feasibility, duality gap, constraint residuals, tolerancje; silna dualność tylko przy hipotezach.

### 7.2. Optax/JAX

Docelowe algorytmy: SGD, momentum, Adam, RMSProp, Adagrad, L-BFGS jeśli dostępny i zweryfikowany, constrained/projection, schedules, second-order, stochastic optimizers. Każdy wynik ma `objective_before/after`, `seed`, `dtype`, `optimizer_state_digest`, `gradient_norm`, `constraint_violation`, `confidence` i `reproducibility_status`. `BEST_FOUND` ≠ `GLOBAL_OPTIMUM`.

### 7.3. Przykładowe certyfikaty

Dla programu liniowego `min cᵀx` przy `Ax=b`, `x≥0`, dual `max bᵀy` przy `Aᵀy≤c`: kandydat optimum dopuszczalny po sprawdzeniu wykonalności prymalnej i dualnej oraz luki `cᵀx−bᵀy≤ε` z tolerancją uwzględniającą błędy liczbowe. Bez dualnego świadectwa wynik to `CANDIDATE`.

## 8. Ω-Physical Systems & Control Laboratory

### 8.1. MuJoCo + Menagerie + dm_control

`ModelManifest` zawiera `mjcf_digest`, `asset_licenses`, `joint_limits`, `contact_model`, `mass_inertia`, `timestep`, `integrator`, `solver_tolerance`, `observation_spec`, `action_spec`, `seed`. `SimulationTrace` ma czas, jednostki, wejścia, stany, energię, kontakty i metryki błędu. **Warunki bezpieczeństwa rzeczywistego robota nie wynikają automatycznie z symulacji.**

### 8.2. Program wynikający z SIAM Front Matter

Przygotować teorie: uśrednianie układów osobliwie perturbowanych, inclusion dynamics, occupational measures, LP/IDLP, dualność, sterowanie z dyskontowaniem, sterowanie z horyzontem długim. Załączony skan zawiera **tylko** spis treści i początek przedmowy; dlatego konkretne lematy autora wymagają pełnego tekstu lub niezależnego wyprowadzenia. Dla układu `ẋ=f(x,y,u,ε), εẏ=g(x,y,u,ε)` trzeba jawnie podać skalę ε, regularność, stabilność warstwy szybkiej i rodzaj zbieżności przed stwierdzeniem błędu uśredniania.

### 8.3. Weryfikacja bezpieczeństwa

Łączyć symulację z model checking i barrier/Lyapunov certificates dla ściśle określonych modeli. `SIMULATED_SAFE_N_EPISODES` nie przechodzi automatycznie w `FORMALLY_SAFE`.

## 9. Ω-Scientific & Statistical Evidence Layer

### 9.1. Science skills

Repozytorium zawiera zestaw skillów badawczych, nie bibliotekę twierdzeń. Każdy adapter musi mieć allowlistę operacji, ograniczenia dostępu do danych, tajne klucze wyłącznie w menedżerze sekretów, kontrolę licencji źródeł i dokładne cytowania. Dostęp do medycznych/biologicznych danych wrażliwych wymaga osobnych polityk.

### 9.2. RegressLM i representations4d

RegressLM to estymator liczb, a 4D Representations to modele percepcji czasoprzestrzennej. Mogą sugerować priorytety solverów i dostarczać obserwacje, ale **nie** mają prawa emitować `PROVED_STRICT`. Wymagaj OOD detection, calibration, unit tests, dataset provenance i drift monitoring.

### 9.3. 3d-shapes, mathematics_dataset

- 3d-shapes: dataset 480 000 obrazów, sześć latent factors; brak danych HDF5 w samym repo. Zastosowanie: identyfikowalność i uogólnienie reprezentacji.
- mathematics_dataset: generatory zadań o poziomie głównie szkolnym. Testy benchmarkowe mają rozdzielone generatory i seed, a odpowiedzi muszą być weryfikowane niezależnie; nie można z nich wywnioskować pokrycia 6006 dziedzin.

### 9.4. Matematyka kwantowa

Awesome-Quantum-Computing-Platform jest katalogiem dostawców, SDK i symulatorów. Kontrakt `QuantumBackend`: gate set, noise model, shots, connectivity, transpilation, provenance, measurement uncertainty, backend version. Weryfikacja twierdzeń o unitarności/entanglement wymaga matematycznej semantyki, a nie samego uruchomienia QPU.

## 10. Ω-Conjecture Laboratory i problemy otwarte

`ConjectureCandidate` zawiera formalną formułę, założenia, MSC, literaturę, historię prób, wyniki eksperymentów, niezależne kontrprzykłady i poziom pewności **heurystyki**. Pipeline: candidate → finite falsification → symbolic simplification → lemma discovery → proof attempt → kernel check → independent review. Nie wolno ogłaszać rozwiązania P vs NP, Riemanna, Hodge'a, Birch–Swinnerton-Dyera, Naviera–Stokesa itd. na podstawie regresji ML, tekstu LLM ani nieweryfikowanego preprintu. Statusy Clay w encyklopedii to stan redakcyjny i wymagają aktualnego sprawdzenia u CMI.

## 11. Coverage engine — obowiązkowa pełna śledzalność

### 11.1. Jednostka pokrycia

`CoverageRow = (source_file, source_page, source_hash, source_id, MSC_code, claim_kind, knowledge_record_id, implementation_module, proof_dependency, test_id, review_status)`.

**Trzy niezależne wskaźniki:**

- `source_coverage`: liczba poprawnie zaindeksowanych haseł / liczba haseł źródłowych; dla MSC2020 obecnie 6006/6006.
- `formalization_coverage`: liczba haseł z zaakceptowaną formalizacją / liczba haseł wymagających formalizacji; **niezmierzone**.
- `proof_capability_coverage`: liczba zadań z poprawnym certyfikatem na zewnętrznym benchmarku / liczba zadań benchmarku; **niezmierzone**.

### 11.2. Dla każdego kodu MSC

`SOURCE_INDEXED` → `CONCEPT_REVIEWED` → `DEFINITION_FORMALIZED` → `PROOF_LIBRARY_MAPPED` → `BENCHMARKED` → `CERTIFIED`. Nie wolno automatycznie awansować 6006 pozycji tylko dlatego, że wszystkie mają opis. Obowiązkowa kontrola mapy odsyłaczy i rozbieżności MSC2010→2020.

### 11.3. Dla każdego z 239 punktów 14-stronicowego PDF

Przypisz: `RM-Pxx-yy`, moduł, formalną definicję, MSC primary/secondary, twierdzenia referencyjne, algorytmy, test poprawny, test negatywny, przypadek graniczny, źródło, dowód lub klasę wyniku, stan implementacji. Istniejący rejestr v1.2 stanowi baseline; nowe źródła nie usuwają żadnego punktu.

### 11.4. Dla 307 pojęć MATH

Każde `MATH-0001..MATH-0307` musi mieć osobny rekord, a relacje do MSC muszą być weryfikowane. Komentarz źródłowy nie jest dowodem i nie może być promowany do `THEOREM` bez zewnętrznej formalizacji.

## 12. API i statusy

```json
{
  "request_id": "uuid",
  "task_kind": "THEOREM_PROOF | NUMERIC_CERT | SIMULATION | OPTIMIZATION | RESEARCH",
  "problem": "typed-math-ir",
  "msc_codes": ["15A18"],
  "assumptions": [],
  "proof_policy": {"allowed_axioms": ["classical_declared"], "strict": true},
  "resource_budget": {"cpu_seconds": 300, "memory_mb": 8192},
  "evidence_policy": {"require_source_hashes": true, "require_kernel_check": true}
}
```

Odpowiedź: `job_id`, `status`, `claim_kind`, `assumptions`, `proof_term_uri`, `counterexample_uri`, `numerical_enclosure`, `experiment_manifest`, `source_provenance`, `checker_version`, `limitations`, `cost`, `audit_digest`. `PROVED_STRICT` wymaga zamkniętego proof term, sprawdzenia w jądrze, zgodności hashy środowiska i polityki aksjomatów. `UNKNOWN` jest poprawną odpowiedzią, gdy problem nierozstrzygalny, przekracza budżet lub nie ma certyfikatu.

## 13. Plan wdrożenia i kontrolowane fazy

| Etap | Praca | Obowiązkowy dowód odbioru | Status |
|---|---|---|---|
| K00 | Zabezpieczenie oryginałów, hashe PDF, granice licencji | `EXTRACTION_VALIDATION.json` | Zrobione lokalnie |
| K01 | 6603 kodów MSC2020, 6006 opisów, 307 pojęć, MSC2010, 239 punktów | walidacja liczebności i zgodności zbiorów | Zrobione lokalnie |
| K02 | FTS5 i CLI do przeszukiwania rekordów | testy zapytań, brak wykonywania kodu źródłowego | Zrobione lokalnie |
| K03 | Pełny import wszystkich plików 16 repo po SHA | content manifest + license matrix + SBOM | Do wykonania |
| K04 | Typed Math IR i parsery formalizacji | property-based tests, type safety | Do wykonania |
| K05 | Lean4/mathlib4/batteries/MIL/Iris adapter | odtwarzalny build + proof kernel check | Do wykonania |
| K06 | DDAR/AlphaGeometry adapter | 100% replay + adversarial degeneracy tests | Do wykonania |
| K07 | Certyfikowana arytmetyka i numeryka | interval bounds + independent check | Do wykonania |
| K08 | Optax/JAX optimization | gradient checks, constraints, reproducibility | Do wykonania |
| K09 | MuJoCo/dm_control/Menagerie | determinism, units, trace replay | Do wykonania |
| K10 | Front matter research program | pełne rozdziały lub własne jawne dowody | Do wykonania |
| K11 | Science/Quantum/4D/RegressLM research | calibrated evidence, licenses, safety | Do wykonania |
| K12 | Knowledge graph MSC↔formal library↔repo symbols | precision/recall + manual sample audit | Do wykonania |
| K13 | Conjecture search + formal counterexamples | no false `PROVED`, explicit unknown | Do wykonania |
| K14 | Security/tenant isolation and immutable provenance | fuzz/STRIDE/negative E2E | Do wykonania |
| K15 | Independent evaluation + external benchmarks | reproducible runs and artifacts | Do wykonania |
| K16 | Production rollout | signed approval, rollback, SLO evidence | Do wykonania |

## 14. Krytyczne bramki jakości G01–G20

`G01` pełna zgodność 6006 kodów między encyklopedią i MSC2020; `G02` dokładnie 63/534/6006 w źródle; `G03` 307 indeksów MATH; `G04` 239 identyfikatorów RM; `G05` wszystkie źródła mają SHA-256; `G06` odsyłacze i klasyfikacje zachowują oryginalne znaczenie; `G07` jawna polityka licencji; `G08` lockfile Lean toolchain; `G09` Lean kernel sprawdza wszystkie `PROVED_STRICT`; `G10` brak `sorry` i ukrytych aksjomatów; `G11` poprawne dowody warunków domenowych; `G12` kontrola rounding/interval; `G13` brak promocji symulacji do dowodu; `G14` brak promocji ML do dowodu; `G15` degeneracje geometrii; `G16` unit/shape/physics checks; `G17` seed i reproducibility; `G18` izolacja wykonania i brak sieci w kernel; `G19` fuzz, mutacje, negative E2E; `G20` niezależny audyt i podpis release.

Wykonane lokalnie na tym etapie: **G01–G05 w zakresie walidacji ekstrakcji**, nie certyfikacji systemu. G06–G20 pozostają `NOT_EXECUTED`.

## 15. Testy negatywne i przypadki graniczne

1. Fałszywy proof term; 2. prawdziwe twierdzenie z fałszywym kontekstem; 3. `sorry`; 4. ukryty aksjomat; 5. zmiana `lake-manifest`; 6. niezgodne Lean toolchain; 7. fałszywy `UNSAT`; 8. `NaN` i ±∞; 9. odwracanie macierzy osobliwej; 10. nie-SPD Cholesky; 11. nierówność numeryczna na granicy; 12. dzielenie przez przedział zawierający 0; 13. fałszywa wykonalność LP; 14. brak dualnego świadectwa; 15. niestabilny krok integracji; 16. symulacja z niezgodnymi jednostkami; 17. źle określony kontakt MuJoCo; 18. dataset leakage; 19. regresor bez kalibracji; 20. niezgodność układów współrzędnych 4D; 21. nierozwiązana hipoteza uznana za dowód; 22. błędny kod MSC; 23. błędny crosswalk 2010→2020; 24. licencja per-model Menagerie; 25. brak praw do zewnętrznych danych; 26. prompt injection w science-skills; 27. niewłaściwa klasyfikacja source comment jako theorem; 28. nieautoryzowany dostęp do danych; 29. podmieniony hash PDF; 30. niekompletny skan Front Matter przedstawiony jako cała książka.

## 16. Bezpieczeństwo, licencje i ograniczenia

- Kod repozytoriów: root LICENSE to punkt startowy; wymagane transitive dependencies i per-asset terms. Szczególnie Menagerie, science-skills i zewnętrzne datasety.
- Oficjalne dane MSC2020: w dostarczonej encyklopedii oznaczono CC BY-NC-SA 4.0; komercyjne wykorzystanie i redystrybucja wymagają osobnej analizy licencyjnej. Ten dokument nie przyznaje praw do komercyjnego wykorzystania.
- Biblioteka formalna może korzystać z dopuszczonych aksjomatów; `PROVED_STRICT` oznacza dowód w danej teorii, a nie dowód absolutnej prawdziwości założeń empirycznych.
- Jądro nie może wykonywać notebooków, skryptów ani kodu ze źródeł PDF lub z zewnętrznych repo. Każdy adapter działa w izolacji.
- Oryginalne PDF-y i repozytoria nie są nadpisywane. Każdy import tworzy nową, adresowaną treścią rewizję.

## 17. Granice aktualnego wykonania

**Wykonane:** inspekcja PDF i repozytoriów, ekstrakcja 6006/6006 kodów, 307 pojęć, 6603 oficjalnych identyfikatorów MSC2020, 6198 identyfikatorów MSC2010, zachowanie 239 pozycji PDF, lokalny indeks FTS5 i sprawdzalny manifest.  
**Niewykonane:** pobranie i analiza wszystkich plików 16 repozytoriów, kompilacja Lean, budowa jądra dowodowego, trening modeli, uruchomienie MuJoCo/JAX, pełny audyt semantyczny 6006 opisów, niezależne formalne dowody i produkcyjne wdrożenie.  
**Ograniczenie SIAM:** 10 stron front matter nie zawiera treści rozdziałów, więc nie jest podstawą do twierdzenia o przejęciu wszystkich dowodów z monografii.

## 18. Źródła i ścieżki audytowe

Wszystkie nazwy i SHA repozytoriów: `REPOSITORY_AUDIT_16.md`. Suma kontrolna każdego PDF: `EXTRACTION_VALIDATION.json`. Każdy z 6006 rekordów: `MSC2020_ENCYCLOPEDIA_6006_ENTRIES.jsonl` i wersja `.md`. Wszystkie 6603 kody oficjalne: `MSC2020_OFFICIAL_6603_CODES.jsonl`. Indeks MSC2010 i porównanie identyfikatorów: `MSC2010_REFERENCE_CODES.jsonl`, `MSC2010_TO_2020_CODE_CROSSWALK.jsonl`. 307 haseł: `MATH_ATLAS_307_CONCEPTS.jsonl`. Program SIAM: `SIAM_FRONT_MATTER_SCOPE.md`. Rejestr 239 pojęć: załączony `IMANDRAX_OMEGA_MATH_PDF_TRACEABILITY_14_PAGES.md`.

## 19. Klasyfikacja wszystkich 63 klas MSC2020

Pełny, wygenerowany ze źródła rejestr klas i ścieżek: `MSC2020_63_CLASS_ROUTING.md`.

## 20. Problemy Clay — kontrola statusu

Wszystkie siedem problemów, daty i różnica między zgłoszeniem a akceptacją: `CLAY_MILLENNIUM_STATUS_AND_PROOF_POLICY.md`.


---

## CZĘŚĆ B — wcześniejsza specyfikacja v1.2 zachowana w całości

> **GRANICA PROJEKTU (NORMATYWNA):** IMANDRAX Ω ENGINE jest samodzielnym systemem rozumowania matematycznego. Nie jest częścią OCAF Runtime ani Aetheris Photo–Video–Game. Integracje z innymi produktami nie są zakresem tej specyfikacji. Dokument opisuje projekt, nie wytrenowany ani wdrożony silnik.

# IMANDRAX Ω ENGINE — Production Engineering Blueprint v1.1 (rozszerzenie PDF)

**Data:** 2026-10-25 · **Wersja:** v1.1.0-design · **Zakres:** samodzielny silnik rozumowania matematycznego (bez IMANDRAX i Aetheris).  
**Status:** `SPECIFIED / NOT IMPLEMENTED / NOT BENCHMARKED / NOT DEPLOYED`.
**Właściciel wymagań matematycznych:** użytkownik — `Rozumowanie Matematyczne.pdf` (14 stron).

> **KOREKTA SCOPE.** Wersja 1.0 opisywała silnik wnioskowania. Wersja 1.1 **włącza szczegółowy program matematyczny ze wszystkich 14 stron PDF** jako normatywny zakres produktu: każda z 239 zidentyfikowanych pozycji ma osobny identyfikator `RM-Pxx-yy`, moduł i grupę testową w `07_OMEGA_REASONER_PDF_14_STRON_ELEMENT_PO_ELEMENCIE.md`. Dodatkowo zapisana jest samodzielna specyfikacja subsystemów `06_OMEGA_REASONER_MATH_ENGINEERING_SPEC_v1.1.md`. Nie wolno mylić indeksu wymagań ani projektowanych kontraktów z już działającą implementacją.

**Weryfikowane źródło techniczne porównawcze:** [ImandraX Docs](https://imandrax.dev/docs/), [Region Decomposition](https://imandrax.dev/docs/region-decomposition/), [Verification](https://imandrax.dev/docs/verification/), [SMT-LIB 2.7](https://smt-lib.org/language.shtml). Projekt jest własny, niezależny od Imandra Inc.; nie kopiuje kodu ani konstrukcji własnościowych.

---

# CZĘŚĆ I — Blueprint bazowy v1.0 (zachowany w całości)

# IMANDRAX Ω ENGINE — Production Engineering Blueprint v1.0

## Niezależny silnik dowodzenia formalnego, automatycznego rozumowania, model checking i matematycznej weryfikacji systemów AI

**Klasa produktu:** autonomiczny system klasy ImandraX, opracowywany niezależnie od Imandra Inc.  
**Identyfikator katalogowy:** `SYS-IMANDRAX-OMEGA-001`  
**Systemy docelowe:** Samodzielny projekt matematyczny IMANDRAX Ω ENGINE; brak zależności od pozostałych projektów.  
**Wersja:** `1.0.0-design` · **Data:** 2026-10-25 · **Język:** polski.  
**Status:** `SPECIFIED / NOT IMPLEMENTED / NOT BENCHMARKED / NOT DEPLOYED`.  
**Pochodzenie:** autorski projekt referencyjny na podstawie publicznych koncepcji formal methods, oficjalnych materiałów ImandraX i pliku użytkownika „Rozumowanie Matematyczne.pdf” (14 stron).  
**Granica prawna:** nazwa „ImandraX” oznacza produkt Imandra Inc. Ten dokument **nie** stanowi forka, reverse engineeringu prywatnych komponentów, deklaracji kompatybilności binarnej ani użycia zastrzeżonego kodu. Nazwa produktu własnego: **IMANDRAX Ω ENGINE**.

> **Zasada nadrzędna:** wynik `PROVED` jest dozwolony wyłącznie po niezależnej kontroli kompletnego obiektu dowodu przez zaufane jądro, przy jawnie ujawnionym i dopuszczonym zbiorze założeń. Odpowiedź LLM, `unsat` od obcego solvera, brak znalezionego kontrprzykładu, sukces testów i przekonująca argumentacja **nie są dowodem matematycznym**.

---

# 0. Kontrakt dokumentu, słownik i klasy dowodów

## 0.1. Słowa normatywne

`MUST` — wymaganie bezwzględne; `MUST NOT` — zakaz; `SHOULD` — wymaganie domyślne z dokumentowanym wyjątkiem; `MAY` — opcja. Statusy i wartości progowe w niniejszym dokumencie są **wymaganiami projektowymi**, nie rezultatami istniejącego wdrożenia.

## 0.2. Rozdzielenie faktów od celów

| Klasa | Przykład | Zasada prezentacji |
|---|---|---|
| `SOURCE_FACT` | ImandraX łączy bounded verification, indukcję i interactive proof | Cytuj źródło pierwotne |
| `DESIGN_DECISION` | Własne jądro dowodów w Rust 2024 | Wymaganie IMANDRAX, nie cecha ImandraX |
| `RESEARCH_HYPOTHESIS` | Dodatkowa automatyzacja przez LLM+CEGAR | Do walidacji eksperymentalnej |
| `ACCEPTANCE_TARGET` | Zero fałszywych `PROVED` w testach mutacyjnych | Kryterium odbioru, nie zmierzony wynik |
| `VERIFIED_EVIDENCE` | Artefakt dowodu z podpisem i wynikiem niezależnego checkera | Dopiero po wykonaniu i zachowaniu dowodu |

## 0.3. Co silnik może, a czego nie wolno obiecywać

Silnik może formalnie rozstrzygać **określone fragmenty** logiki i sprawdzać konkretne dowody, modelować skończone stany, badać ograniczone ślady, dowodzić własności funkcji rekurencyjnych przy poprawnym schemacie indukcji oraz tworzyć kontrprzykłady. Nie może gwarantować rozstrzygnięcia dowolnej formuły wyższych rzędów, dowolnego programu, nieliniowego układu rzeczywistego czy nierozwiązanych problemów matematycznych. Twierdzenia `P vs NP`, hipoteza Riemanna, Hodge'a i Hilberta–Pólyi (wymienione w materiale źródłowym) są **obiektami badań**, a nie testami funkcjonalnymi z założonym sukcesem.

---

# 1. Uzasadnienie i analiza referencyjna ImandraX

Oficjalne ImandraX deklaruje język modelowania oparty na czystym fragmencie OCaml, dowodzenie ograniczone, indukcyjne, interaktywne, dekompozycję regionów, kontrprzykłady i API sesyjne. Dokumentacja rozróżnia `Proved`, `Refuted`, `Verified_upto`, `unknown` i `err`; opisuje Twirp/protobuf HTTP, biblioteki klienckie i MCP. Nie zakładamy, że API lub format wewnętrzny ImandraX jest standardem, który należy kopiować. Źródła: [R1–R4].

## 1.1. Porównanie bez nieudowodnionych przewag

| Obszar | ImandraX — cecha udokumentowana | IMANDRAX Ω ENGINE — proponowane rozwiązanie | Warunek porównania |
|---|---|---|---|
| Logika | Obliczeniowa logika wyższych rzędów i indukcja | Własny mały kernel zależnych typów + reifikacja fragmentów SMT | Audyt spójności i sprawdzenie certyfikatów |
| Bounded reasoning | Unrolling i kontrprzykłady | CDCL(T) + BMC + CEGAR + jawne granice | Identyczne benchmarki i budżety |
| Unbounded reasoning | Inductive waterfall / taktyki | Taktyki + synteza lematów + kontrolowana indukcja | Wskaźnik dowiedzionych problemów, nie deklaracje |
| Region decomposition | Rozłączne regiony zachowania | Partycjonowanie z dwoma certyfikatami: coverage i disjointness | Niezależna weryfikacja każdego regionu |
| Agentic reasoning | Integracje AI | LLM wyłącznie proponuje, kernel weryfikuje | Wstrzykiwanie błędnych „dowodów” musi być odrzucane |
| Bezpieczeństwo | Nie oceniono szczegółów operacyjnych | Wielodzierżawność, sandbox, mTLS, signed proof bundles | Audyt implementacji i testy izolacji |
| Osiągi | Brak porównywalnych danych w tym projekcie | Profile budżetowe i równoległy proof search | Pomiary p50/p95, RAM, energia, timeout |

**Zakaz marketingowy:** „szybszy”, „silniejszy”, „maksymalny” i „bezbłędny” są twierdzeniami niedopuszczalnymi bez powtarzalnych benchmarków i weryfikacji poprawności.

# 2. Cele produktu, profile i nie-cele

## 2.1. Profile produktu

| Profil | Domeny | Dopuszczalne decyzje |
|---|---|---|
| `CORE-PROOF` | rachunek zdań, predykaty, równość, indukcja | dowód sprawdzony / odrzucony / unknown |
| `SMT-DECIDE` | QF_UF, QF_LIA, QF_LRA, QF_BV, wybrane arrays/datatype | SAT z modelem / UNSAT z dowodem / unknown |
| `STATE-VERIFY` | protokoły, automaty, HA, auth, retry | BMC, k-induction, IC3/PDR w obsługiwanych fragmentach |
| `MATH-EXACT` | wymierne, macierze symboliczne, algebra liniowa | certyfikowane tożsamości, przedziały, rozkłady |
| `MATH-NUMERIC` | obliczenia przybliżone, ML, probabilistyka | wynik numeryczny z błędem; nie `PROVED` bez certyfikatu |
| `NEUROSYMBOLIC` | LLM, agent planner, kod źródłowy, DSL | propozycja lematów/specyfikacji; zawsze kernel-gated |

## 2.2. Zasady eksploatacji

- Jeden rdzeń logiczny, wiele niezaufanych strategii wyszukiwania dowodów; nie mnożyć agentów bez mierzalnej korzyści.
- Każda analiza posiada niezmienny `ModelSnapshot`, `AssumptionSet`, `ProofPolicy`, `ResourceBudget` i `TenantContext`.
- Tryb `strict` **MUST** odrzucać dowody z niezweryfikowanymi aksjomatami, oracle steps, lukami w certyfikacie i niezgodną wersją semantyki.
- Operacje wytwarzające efekt uboczny (zmiana kodu, publikacja, podpisanie, wdrożenie) nie należą do samego prover; wykonuje je osobny autoryzowany executor po polityce i zatwierdzeniu właściwym dla operacji.
- Model wejściowy może być złośliwy; kompilacja ani uruchomienie modelu nie może wykonywać dowolnego kodu hosta.

# 3. Model formalny i zaufana baza obliczeniowa (TCB)

## 3.1. Rdzeń logiczny `Ω-Core`

Wybór projektowy: predykaty i dowody są wyrażane w typowanej teorii `λΠ` z hierarchią uniwersów `Type u`, `Prop`, typami indukcyjnymi, równością, eliminatorami i konstruktorami rekurencyjnymi. Jądro **nie** wykonuje dowolnej rekurencji ogólnej; programy rekurencyjne są elaborowane do dopuszczalnych eliminatorów po sprawdzeniu dodatniości i warunków definicyjnych. Część klasycznej logiki, arytmetyki i rozszerzeń SMT jest realizowana przez dowodowe adaptery, nie ukryte `assume true`.

**Podstawowe osądy:**

\[
\Gamma \vdash t : T, \qquad \Gamma \vdash p : \mathrm{Prop}, \qquad \Gamma \vdash \pi : p.
\]

**Poprawność (soundness) — cel:**

\[
\mathrm{KernelCheck}(E,\pi,p)=\mathrm{accept}\ \Rightarrow\ E\vdash p
\]

przy założeniu poprawnej implementacji kernela, spójności jawnych aksjomatów `E` oraz modelu zaufania sprzętu/kompilatora. Powyższa implikacja jest **kontraktem do udowodnienia/testowania**, a nie już potwierdzonym twierdzeniem o implementacji IMANDRAX.

## 3.2. Minimalne elementy TCB

1. Parser *kanonicznego* formatu termów kernela; parser wygodnego DSL pozostaje poza TCB.
2. Sprawdzanie typów, podstawień, redukcji beta/iota/zeta, porównania definicyjnego i uniwersów.
3. Sprawdzanie dodatniości induktywnych definicji, poprawności eliminatorów i ograniczeń rekurencji.
4. Weryfikacja proof DAG, tożsamości definicji i hashy środowiska.
5. Dokładna semantyka wbudowanych reguł i certyfikatów arytmetycznych; żadnego „trusted external SMT”.
6. Implementacja kontroli założeń, która nie dopuści do awansu `AXIOMATIC` na `PROVED_STRICT`.
7. Warstwa parsowania długości, limitów i integralności pakietu dowodu.

**Poza TCB:** heurystyki LLM, e-graph, solver CDCL, wyszukiwarka lematów, optymalizator, parser natural language, planner agentów, telemetry, UI, model selection. Ich błędy mogą obniżyć kompletność/wydajność, lecz nie powinny zmienić fałszu w zaakceptowany dowód.

## 3.3. Polityka aksjomatów

- `NO_AXIOMS`: jedynie konstrukcje definicyjne i zatwierdzone reguły kernela; cel rygorystyczny.
- `CLASSICAL_DECLARED`: wyraźnie zadeklarowane aksjomaty klasyczne, ujęte w `AssumptionSet` i odcisku dowodu.
- `DOMAIN_ASSUMPTIONS`: fizyczne, operacyjne lub biznesowe hipotezy jawne w raporcie; wynik oznaczony `CONDITIONAL_PROOF`.
- `ORACLE` / `sorry` / `admit` / `trust`: zabronione w `PROVED`; może istnieć wyłącznie w przestrzeni roboczej, a rezultat ma status `UNTRUSTED`.

**Niebezpieczna ścieżka:** `unsat` z solvera, `trust` w LFSC, niezależnie od nazwy formatu, **nie** jest automatycznie akceptowany. Tylko w pełni obsłużone reguły i kontrola kompletności certyfikatu pozwalają na dowód. Dokumentacja cvc5 wskazuje, że niektóre wersje/formaty LFSC mogą zawierać trust steps [R7].

# 4. Warstwy architektoniczne i granice zaufania

```text
┌─────────────────────────────────────────────────────────────────────┐
└────────────────────────────────┬────────────────────────────────────┘
                                 │ authenticated, typed request
┌────────────────────────────────▼────────────────────────────────────┐
│ API Gateway: mTLS/OIDC · tenant policy · quota · idempotency · WAF  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ scoped capability token
┌────────────────────────────────▼────────────────────────────────────┐
│ Session Manager · Model Registry · Snapshot Store · Event Journal  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ immutable AST/IR
┌────────────────────────────────▼────────────────────────────────────┐
│ OML Frontend: parser → elaborator → typechecker → Ω-IR / SMT-LIB    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ proof obligations
┌────────────────────────────────▼────────────────────────────────────┐
│ Reasoning Orchestrator / Portfolio Scheduler                        │
│ CDCL(T) · BMC · PDR · induction · e-graphs · CEGAR · tactics · AI    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ untrusted candidates and proofs
┌────────────────────────────────▼────────────────────────────────────┐
│ Certificate Translator · Counterexample Replay · Region Verifier   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ canonical proof term
┌────────────────────────────────▼────────────────────────────────────┐
│ Ω-CORE PROOF KERNEL [TCB] → checked theorem / reject / unknown     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ signed, immutable evidence
┌────────────────────────────────▼────────────────────────────────────┐
│ Proof Ledger · CAS/Blob Store · Metrics · Audit · Reproducibility   │
└─────────────────────────────────────────────────────────────────────┘
```

## 4.1. Granice procesu

- `omega-gateway`: ingress HTTP/gRPC, policy enforcement, request validation; bez dostępu do sekretów solvera poza scoped token.
- `omega-sessiond`: tworzy sesje i snapshoty, zarządza stanem i lease; write-ahead journal.
- `omega-frontend`: parsuje OML, buduje typowany AST, elaboruje DSL do Ω-IR.
- `omega-solverd`: równoległe workery obliczeniowe w izolowanych procesach/VM; niezaufane.
- `omega-kerneld`: minimalny proces weryfikacji, uruchamiany z tylko-do-odczytu proof bundle, bez sieci i pluginów.
- `omega-certd`: translacja certyfikatów i replay modeli; wynik niezaufany do czasu kernela.
- `omega-ledger`: zapisuje podpisane wyniki i provenance, ale nie ma uprawnień do wystawiania `PROVED` bez podpisu kernela.
- `omega-agentd`: LLM agent do proponowania specyfikacji, lematów i napraw; żaden agent nie może zmieniać statusu dowodu.

## 4.2. Diagram stanów zadania

```text
RECEIVED → AUTHORIZED → VALIDATED → SNAPSHOTTED → QUEUED → RUNNING
                  ↘ REJECTED                        │       │
                                                    │       ├→ CANDIDATE
                                                    │       │      ↓
                                                    │       │   CHECKING
                                                    │       │    ├→ PROVED_STRICT
                                                    │       │    ├→ CONDITIONAL_PROOF
                                                    │       │    ├→ REFUTED_VALIDATED
                                                    │       │    └→ INVALID_CERTIFICATE
                                                    │       ├→ BOUNDED_SAFE
                                                    │       ├→ UNKNOWN
                                                    │       ├→ TIMEOUT
                                                    │       ├→ CANCELLED
                                                    │       └→ ERROR
                                                    └→ RESOURCE_EXHAUSTED
```

Każde przejście jest zapisywane atomowo z monotonicznym numerem wersji; powtórzone żądanie z tym samym kluczem idempotencji nie tworzy kolejnego logicznego zadania. `PROVED_STRICT` i `REFUTED_VALIDATED` są terminalne dla danego `ModelSnapshot`; zmiana modelu tworzy nowy snapshot, a nie nadpisuje historii.

# 5. Język modelowania `OML` i reprezentacja pośrednia `Ω-IR`

## 5.1. Język źródłowy

OML to nowy język deklaratywny **inspirowany dziedziną problemu**, nie składnia IML skopiowana z ImandraX. Składnia referencyjna (projekt do implementacji):

```oml
module RetryPolicy {
  type State = { attempt: Nat, limit: Nat, authorized: Bool }

  pure fn may_retry(s: State) -> Bool =
    s.authorized && s.attempt < s.limit;

  theorem retry_requires_auth(s: State) : Prop =
    may_retry(s) ==> s.authorized;
}
```

Wymagania: typy algebraiczne, rekordy, wzorce, funkcje czyste, kwantyfikatory, `let`, typy parametryczne, kontrakty `requires/ensures`, predykaty temporalne i jawne parametry liczbowe. Rekurencja tylko po udowodnionym warunku terminacji. Funkcje zewnętrzne (np. GPU, I/O, LLM) muszą być reprezentowane przez abstrakcyjne kontrakty z jawnie oznaczonymi założeniami, a nie wykonywane w jądrze.

## 5.2. Potok kompilacji

`UTF-8 → lexer → lossless CST → parser AST → name resolution → type inference → monomorphization/specialization (gdy konieczne) → normalized typed Ω-IR → obligations → canonical proof environment`.

Wymagane atrybuty AST: stabilne identyfikatory, zakresy źródłowe, typ, `source_hash`, `module_hash`, `semantic_version`, identyfikator właściciela i klasa zaufania. Nazwy wprowadzane przez makra są higieniczne; nie wolno ukryć aksjomatu przez alias, import ani ekspansję makra.

## 5.3. Model pamięci Ω-IR

- Typowany, niezmienny DAG; hash-consing oraz arena z indeksami generacyjnymi (ochrona przed use-after-free).
- Symbole w tablicy internowania, de Bruijn indices lub równoważny mechanizm eliminujący variable capture.
- Kanoniczne serializowanie: stały porządek pól, endianness, jednoznaczne typy liczb, rozróżnienie `-0.0`, `NaN` i `Inf` tam, gdzie dopuszczone.
- Normalizacja tylko przez reguły semantycznie zachowujące znaczenie; agresywne przekształcenia muszą emitować lemat równości.
- Granice rozmiaru AST, głębokości, liczby typów, liczby symboli i zagnieżdżenia rekursji są egzekwowane przed alokacją.

# 6. Proof Kernel: reguły, algorytm i kontrakty

## 6.1. Reguły pierwotne

`Var`, `Sort`, `Pi`, `Lam`, `App`, `Let`, `Eq.refl`, `Eq.rec`, `Inductive.ctor`, `Inductive.rec`, `Universe`, `Weakening`, `Conversion`. Każda reguła ma sprawdzalny warunek boczny; jądro nie przyjmuje tekstowej etykiety „tautologia” jako dowodu. `Decidable`/klasyczne eliminacje są realizowane w jawnej bibliotece aksjomatów lub z konstruktywnego termu dowodu.

**Warunek niezawodności:** parser certyfikatu jest fuzzowany i ma limit czasu, pamięci, stosu i wielkości alokacji; sprawdzanie wielkich DAG odbywa się iteracyjnie, nie przez nieograniczoną rekurencję stosu.

## 6.2. Schemat checkera (kontrakt, nie gotowa implementacja)

```rust
pub enum ProofVerdict {
    Accepted { theorem_digest: [u8; 32], assumptions_digest: [u8; 32] },
    Rejected { error_code: KernelErrorCode },
}

pub trait ProofKernel: Send + Sync {
    fn check(
        &self,
        environment: &CanonicalEnvironment,
        goal: &CanonicalProposition,
        proof: &CanonicalProof,
        policy: &ProofPolicy,
    ) -> ProofVerdict;
}
```

Każde wywołanie jest deterministyczne względem kanonicznych bajtów wejścia, wersji semantyki i konfiguracji kernela. Implementacja `ProofKernel` musi sprawdzić zgodność `goal` z dokładnym typem wyprowadzonego termu oraz dopuszczalność **wszystkich** zależności i aksjomatów.

## 6.3. Odrębna implementacja kontrolna

Wymagane są co najmniej dwa niezależne tory sprawdzania dla reprezentatywnych certyfikatów: podstawowy kernel Rust i drugi checker o możliwie niezależnej implementacji (np. Lean/OCaml albo osobny checker Rust bez współdzielenia algorytmu). Niezgodność to `INTEGRITY_FAILURE`, nie głosowanie większościowe. Tylko checker wyznaczony jako TCB może emitować produkcyjny status, a niezależny checker stanowi dodatkowy gate w CI i audycie.

# 7. Native SMT/CDCL(T) — architektura solvera

## 7.1. Fragmenty i semantyka

| Teoria / logika | Faza 1 | Faza 2 | Ograniczenie |
|---|---|---|---|
| Propositional SAT | CDCL, proof logging | portfolio, incremental | `UNSAT` wymaga sprawdzonego proof trace |
| QF_UF | congruence closure | proof-producing e-graph | równość z poprawnymi regułami kongruencji |
| QF_LIA | exact rationals + integer cuts | branch-and-bound/cutting planes | certyfikat integer arithmetic |
| QF_LRA | simplex na wymiernych | incremental optimization | brak niekontrolowanego float w dowodzie |
| QF_BV | bit-blasting + SAT | native word-level reasoning | poprawność szerokości i overflow |
| QF_AUFLIA | ograniczony fragment arrays + UF | extensionality/lemmas | quantified arrays często `UNKNOWN` |
| Datatypes | constructors, testers, selectors | recursive data | sprawdzona definicja typów |
| Nonlinear real | `UNKNOWN` lub sound interval | CAD/δ-sat jako badanie | δ-sat ≠ dokładne SAT |
| IEEE-754 FP | bit-precise SMT dla wspieranych operacji | proof-carrying FP transforms | różne rounding modes, NaN, signed zero |
| Quantifiers/HOL | ograniczona instancjacja | proof-guided induction | nie gwarantować decyzyjności |

Zgodność parsera SMT-LIB: projektować według specyfikacji **SMT-LIB 2.7**, zachowując negocjację wersji i testy regresji 2.6 [R5]. Zgodność syntaktyczna nie oznacza obsługi każdej teorii.

## 7.2. CDCL i proof logging

- Watched literals; VSIDS/EVSIDS; clause minimization; restart policy Luby lub dynamiczna; learned clause database reduction.
- Wszystkie decyzje i implikacje deterministycznie odtwarzalne w profilu `reproducible` przy ustalonym seed, kolejności wątków i wersji solvera.
- Dla SAT model jest oceniany w oryginalnej formule po odwróceniu preprocessingu.
- Dla UNSAT proof trace w formacie sprawdzalnym przez niezależny checker (np. LRAT w czysto boolowskiej części); teorie wymagają własnych certyfikatów lematu lub translacji do kernela.
- `UNSAT` bez kompletnego proof trace → `UNTRUSTED_UNSAT`/`UNKNOWN`, nigdy `PROVED`.

## 7.3. DPLL(T) i propagacja teorii

```text
normalize → Tseitin CNF → CDCL assignment
                              ↓
                    theory propagation
                      /           \
               consistent       conflict
                  ↓                ↓
             continue         proof lemma
                                  ↓
                             learn clause
```

Teoria publikuje `Explanation` z dowodem implikacji/konfliktu, a nie arbitralne „conflict=true”. Łączenie teorii wymaga poprawnej semantyki współdzielonych symboli i założeń (Nelson–Oppen lub kontrolowana kombinacja); jeśli warunki kombinacji nie są spełnione, solver zwraca `UNKNOWN`.

## 7.4. Inkremetalność

`push`, `pop`, assumption literals, scoped lemmas, per-query resource budget. Zależność lematu od lokalnych założeń jest przechowywana; po `pop` nie wolno użyć go w silniejszym kontekście bez rekonstrukcji dowodu. Cache obejmuje semantyczny hash środowiska, nie wyłącznie tekst formuły.

# 8. Unbounded proof search i indukcja

## 8.1. Ω-Waterfall (własna strategia)

`normalize → rewrite (proof-producing) → destructor elimination → forward chaining → bounded counterexample search → generalization candidate → lemma discovery → induction synthesis → kernel check`.

Każda faza ma budżet i własny ślad. Reguły rewrite muszą zachowywać typ i emitować dowód równości; e-graph nie jest TCB. Generalizacja jest hipotezą, której błędność może zostać obalona przed próbą indukcji. System nie podejmuje nieograniczonych prób dowodu.

## 8.2. Indukcja i terminacja

- Indukcja strukturalna po ADT i listach: schemat generowany z eliminatora typu.
- Indukcja funkcyjna: schemat wynika z definicji rekurencyjnej dopuszczonej przez kernel.
- Termination obligations: dobrze ufundowana relacja `≺`, miara `μ : State → Nat` lub krotka leksykograficzna; dla ordinalnych miar rozszerzenie wyłącznie z osobnym formalnym fundamentem.
- Recursion with fuel: użyteczna do bounded search, **nie** zastępuje dowodu terminacji.
- Mutual recursion: call graph i dowód zmniejszania miary dla wszystkich cykli.

## 8.3. Lemma mining

Heurystyki mogą proponować: invariant strengthening, interpolant, cut lemma, algebraic normalization, abstract invariant, induction hypothesis. Każdy kandydat jest sprawdzany pod kątem kontrprzykładów i dopiero po pełnym dowodzie trafia do zaufanej bazy reguł. Provenance lematu obejmuje źródło, generator, model LLM i licencję danych; generator nie jest źródłem prawdy.

# 9. Model checking: BMC, k-induction, IC3/PDR i CEGAR

## 9.1. Semantyka systemu przejść

Definicja: `M = (S, I, T, AP, L)` — stany, stany początkowe, relacja przejścia, zbiór atomowych własności i etykietowanie. Dla własności bezpieczeństwa `P : S → Bool` celem jest:

\[
\forall s\in Reach(M),\;P(s).
\]

**BMC** dla granicy `k` sprawdza spełnialność:

\[
I(s_0)\land\bigwedge_{i=0}^{k-1}T(s_i,s_{i+1})\land
\bigvee_{i=0}^{k}\neg P(s_i).
\]

Jeśli formuła jest SAT, kandydat śladu jest **odtwarzany** w semantyce oryginalnego modelu. Jeśli UNSAT, wynik `BOUNDED_SAFE(k)` dotyczy wyłącznie długości śladu ≤ `k`; nie stanowi dowodu nieograniczonego.

## 9.2. k-induction

Wymaga (i) podstawy: brak złych stanów dla długości do `k`; (ii) kroku: z `P(s_0)…P(s_k)` i kolejnych `T` wynika `P(s_{k+1})`, przy odpowiednich założeniach o osiągalności. Sam niespełniony krok nie dowodzi błędności własności; może wskazywać na konieczność wzmocnienia invariantów. Wszystkie przesłanki muszą być reprezentowane w obiekcie dowodu.

## 9.3. IC3/PDR

Wspierany fragment: skończone automaty, bitwektory i teorie, dla których solver potrafi zweryfikować lemata. Algorytm buduje ramki `F_0,…,F_n`, utrzymując indukcyjne nadprzybliżenia zbiorów osiągalnych; uzyskanie punktu stałego i dowodów inkluzji pozwala wystawić certyfikat bezpieczeństwa. Nie należy twierdzić, że PDR zawsze zakończy pracę.

## 9.4. CEGAR

Abstrakcja `α : S → Ŝ` jest poprawnym nadprzybliżeniem zachowań. Kontrprzykład abstrakcyjny może być pozorny; konkretyzacja i replay rozróżniają prawdziwy błąd od spurious trace. Refinement dodaje predykaty/relacje i musi zachować soundness. Timeout i brak postępu → `UNKNOWN`.

## 9.5. Własności temporalne

Obsługa LTL/CTL*/TLA-style nie jest domyślną deklaracją pełnego solvera. Profil początkowy: safety invariants oraz bounded response. Liveness wymaga jawnych założeń fairness i środowiska; własność `eventually` bez fairness może być fałszywa w obecności dowolnego schedulera. Wydanie `LIVENESS_PROVED` wymaga osobnego, sprawdzalnego certyfikatu ranking/automata/fairness.

# 10. Dekompozycja regionów zachowania (Ω-Region)

Dla deterministycznej funkcji `f : D → O` tworzony jest zbiór regionów `R_1,…,R_n` i etykiet semantycznych `B_i`.

**Pełność pokrycia:**

\[
\forall x\in D,\quad R_1(x)\lor\cdots\lor R_n(x).
\]

**Rozłączność:**

\[
\forall i\ne j,\forall x\in D,\quad\neg(R_i(x)\land R_j(x)).
\]

**Poprawność opisu regionu:**

\[
\forall x\in D,\quad R_i(x)\Rightarrow B_i(f(x)).
\]

Każda własność jest osobnym `ProofObligation`. Partycje bez sprawdzonego coverage i disjointness otrzymują status `PARTIAL_DECOMPOSITION`. Przy zmiennych ciągłych, nieskończonych domenach i nierozstrzygalnych predykatach nie wolno obiecywać skończonej kompletnej partycji.

## 10.1. Algorytm projektowy

1. Buduj DAG ścieżek sterowania i strażników warunkowych.
2. Upraszczaj strażniki z zachowaniem dowodu równoważności.
3. Łącz ścieżki semantycznie równoważne wyłącznie po dowodzie.
4. Eliminuj regiony UNSAT po sprawdzeniu certyfikatu.
5. Generuj `cover_certificate`, `disjoint_certificate` i per-region behavior proof.
6. Wylicz minimalny zbiór testów brzegowych, nie zastępując nim dowodów.
7. W przypadku niepełnego solvera oznacz niezbadane regiony i zwróć `PARTIAL`.

# 11. Matematyka dokładna, algebra liniowa, rachunek różniczkowy

## 11.1. Exact arithmetic

Domena `Int`, `Nat`, `Rat` i algebraiczne liczby rzeczywiste (opcjonalnie). `Rat` ma postać `p/q` z `q>0`, `gcd(|p|,q)=1`; dzielenie przez zero jest błędem modelu, a nie niezdefiniowanym zachowaniem hosta. Każda transformacja algebraiczna uwzględnia dziedzinę (np. skracanie `x/x` wymaga `x ≠ 0`).

## 11.2. Macierze i tensory

- `Vector n α`, `Matrix m n α` z wymiarami w typach; mnożenie dopuszczone tylko dla zgodnych kształtów.
- Dokładne tożsamości: liniowość, łączność w odpowiednich pierścieniach, własności śladu, transpozycji i determinantów.
- SVD, QR, LU, Cholesky: dla zmiennoprzecinkowej implementacji rezultat ma certyfikowane residuum/przedział, a nie dowód „dokładnej” równości liczb rzeczywistych.
- Cholesky wymaga dodatniej określoności; odrzucenie niepoprawnego założenia i dowód SPD przez odpowiedni certyfikat (np. dokładna arytmetyka) jest osobnym zadaniem.
- Wartości własne dla macierzy ogólnych: wyniki przybliżone z granicami błędu; nie deklarować symbolicznej rozwiązywalności dowolnego wielomianu.

## 11.3. Analiza i różniczkowanie

Symboliczny silnik może dowodzić reguł różniczkowania w formalnej bibliotece przy odpowiednich założeniach ciągłości/różniczkowalności. `autodiff` jest transformatorem programów, nie automatycznym dowodem pochodnej. Hessian, Jacobian i reguła łańcuchowa wymagają zgodności wymiarów, semantyki granic i warunków różniczkowalności. Całkowanie symboliczne jest częściowe; dla numerycznego wyniku podawać błąd i metodę certyfikacji.

## 11.4. Interval arithmetic

Przedziały `[a,b]` z directed rounding i uwzględnieniem błędów konwersji. Dla operacji `f` wymagane:

\[
\{f(x):x\in X\}\subseteq \widehat f(X).
\]

Błędne ustawienie rounding mode lub niepoprawna obsługa `NaN/Inf` unieważnia certyfikat. Weryfikator nie może ufać wynikowi z GPU bez formalnie ustalonej semantyki i błędu; GPU służy do przyspieszenia wyszukiwania, nie jako arbitralne źródło prawdy.

# 12. Prawdopodobieństwo, statystyka, modele generatywne i ML

## 12.1. Formalne modele prawdopodobieństwa

`ProbabilitySpace(Ω,F,P)` wymaga aksjomatów miary. Rozkłady Bernoulliego, dwumianowy, Poissona, normalny, Beta, Gamma, wykładniczy i jednostajny są reprezentowane jako obiekty biblioteki matematycznej z jawnymi dziedzinami parametrów. Przykładowo `Normal(μ,σ)` wymaga `σ>0`. Zależności Bayesowskie i prawdopodobieństwo warunkowe wymagają dodatniego prawdopodobieństwa zdarzenia warunkującego.

## 12.2. Rozróżnienie rodzajów pewności

| Wynik | Znaczenie | Czy `PROVED`? |
|---|---|---|
| Formalne twierdzenie o rozkładzie | Wynik w aksjomatycznej teorii prawdopodobieństwa | Tak, po kernel check |
| Monte Carlo z CI | Estymator i przedział ufności przy założeniach | Nie |
| Bayesian posterior | Warunkowy rozkład wynikający z modelu i prioru | Nie jako fakt o świecie |
| Test statystyczny p-value | Własność procedury i danych pod hipotezą | Nie |
| VC/PAC bound | Formalny bound dla klasy modeli i warunków | Tak dla twierdzenia, nie dla dowolnego wdrożenia |
| Kalibracja ArcFace | Empiryczne EER/FAR/FRR i confidence | Nie |
| Wynik sieci neuronowej | Predykcja zależna od wag/danych | Nie |

## 12.3. Verifiable ML

- Kontrakty wymiarów i zakresów dla tensorów.
- Sprawdzenie finite outputs, granic pamięci, zgodności quantization/dequantization.
- Interval bound propagation / abstract interpretation dla ograniczonych sieci, przy jawnych założeniach numerycznych.
- Dla dużych modeli transformer/diffusion: częściowe własności, certyfikowane lokalne bounds, nie pełny dowód „braku halucynacji”.
- Reguły transformacji modeli (ONNX graph rewrite, fusion) muszą emitować dowód równoważności albo testy parytetu z **wyraźnym statusem empirycznym**.

# 13. Wnioskowanie neurosymboliczne i system agentowy

## 13.1. Role logiczne

| Rola | Odpowiedzialność | Uprawnienia |
|---|---|---|
| `Orchestrator` | kolejkowanie i limity | bez prawa do `PROVED` |
| `SpecSynthesizer` | natural language → OML | tylko draft |
| `Planner` | plan rozkładu problemu | tylko draft |
| `LemmaMiner` | hipotezy lematów | tylko draft |
| `SolverExecutor` | uruchamianie taktyk/SMT/BMC | untrusted |
| `CounterexampleCritic` | analiza kontrprzykładów | untrusted |
| `Verifier` | translacja i kernel-check | prawo do wydania certyfikatu po kontroli |
| `PolicyEngine` | egzekwowanie polityk dostępu i aksjomatów | prawo do odrzucenia |
| `EvidenceLedger` | trwałość i audyt | append-only |

**Niezmiennik:** żaden prompt ani rezultat LLM nie jest uprawnieniem do pominięcia `Verifier` i `PolicyEngine`.

## 13.2. Cykl agentowy

`Request → NL spec candidate → formal typecheck → assumption disclosure → bounded falsification → candidate repair → unbounded proof search → certificate check → publish evidence`.

Warunki stopu: `max_iterations`, `max_tokens`, `max_solver_seconds`, `max_cost`, `max_concurrent_workers`, `deadline`, `cancel_token`, brak poprawy `progress_score`. Heurystyka oceny postępu **nie** może anulować pracy kernela w połowie wydania statusu. Pętla musi zakończyć się wynikiem `UNKNOWN`/`TIMEOUT`, a nie „zwiększaniem autonomii” bez końca.

## 13.3. Formalne kontrakty zamiast obietnic LLM

LLM może wygenerować specyfikację błędną względem intencji użytkownika. Dlatego wymagane są: źródło wymagania, cytat, mapping requirement→obligation, review różnic semantycznych, testy negatywne i podpisane zatwierdzenie specyfikacji przez uprawnioną osobę/system polityki, jeśli wynik ma wpływać na produkcję. Dowód **poprawności błędnej specyfikacji** nie oznacza poprawności biznesowej.


## 14.1. Tenant isolation

Niech `read(t,object)` oznacza dozwolony odczyt. Własność:

\[
\forall t,o,\quad read(t,o)\Rightarrow owner(o)=t\lor delegated(t,o).
\]

Model obejmuje token capability, delegację, odwołanie i replay. Wersja temporalna wymaga, by token po odwołaniu nie umożliwiał nowych odczytów po osiągnięciu gwarantowanego punktu propagacji revocation. Nie wolno dowodzić natychmiastowego globalnego revocation, jeśli infrastruktura działa eventual-consistently.

## 14.2. Fencing i HA PostgreSQL

Dla każdej epoki `e` i zasobu `r`:

\[
\forall a,b,\quad ActiveWriter(a,r,e)\land ActiveWriter(b,r,e)\Rightarrow a=b.
\]

Dowód musi uwzględniać awarie sieci, opóźnienia, restart, lease, zegary, fencing token i semantykę storage. Nie wolno zakładać, że sama większość w klastrze automatycznie chroni przed starym writerem bez fencing na zasobie.

## 14.3. mTLS i rotacja certyfikatów

Invarianta: `AcceptedConnection ⇒ PeerIdentityValidated ∧ AuthorizedForTenant ∧ CertWithinValidity ∧ NotRevokedUnderPolicy`. Rotacja bez przestoju wymaga overlap okresów zaufania, atomic swap materiału TLS, obsługi połączeń długotrwałych i określonej polityki odwołania. Formalny model dowodzi tylko własności przy założonej semantyce bibliotek i systemu; rzeczywiste testy sieciowe pozostają konieczne.

## 14.4. Zenoh reconnect/retry

Niezmienniki: retry bounded, exponential backoff z jitterem, idempotentny message ID, monotonic sequence, brak cross-tenant delivery, brak replay. Liveness `eventually reconnected` jest warunkowa od dostępności sieci i fairness; w trwałym partition nie jest gwarantowana.

## 14.5. PQC i polityka kryptograficzna

Silnik może modelować stany negocjacji ML-KEM/ML-DSA i wymagania hybrydowe, lecz **nie dowodzi bezpieczeństwa kryptograficznego całej implementacji** samym sprawdzeniem automatu protokołu. Proof obligations: brak downgrade, wersjonowanie algorytmów, poprawność polityki akceptacji, zarządzanie kluczami, rozdział dowodu protokołu od dowodu prymitywu. Wymiana produkcyjnego mTLS wymaga osobnej decyzji opartej na standardach, testach i threat modelu.


**Niezależność:** Ω-Reasoner jest usługą dowodową dla OmniFlow Ω i nie zastępuje schedulerów, dekoderów RAW, inferencji GPU ani modeli generatywnych. Nie jest osobną aplikacją użytkownika; UI i workflow należą do wspólnego ekosystemu Aetheris.

## 15.1. OmniGraph Ω / OmniFlow Ω

Dowody przed uruchomieniem grafu:

1. `DAG_ACYCLIC` dla grafów bez zadeklarowanych opóźnień/feedback; cykle dozwolone wyłącznie przy jawnej semantyce czasu i stanie.
2. `TYPE_SAFE_EDGES`: zgodność kształtu tensorów, kolorystyki, rozdzielczości, timebase, FPS i profilu VAE.
3. `NO_UNBOUNDED_MEMORY` dla grafów o znanych granicach zasobów; w innych przypadkach `ESTIMATED` zamiast `PROVED`.
4. `LICENSE_POLICY`: użycie modelu jest dopuszczone przez zewnętrzną politykę/licencję; weryfikator potwierdza jedynie spójność formalnego opisu polityki.
5. `NO_CROSS_TENANT_ASSET_READ` w każdym dopuszczalnym stanie grafu.
6. `EXPORT_DETERMINISM` tylko przy ustalonej wersji modelu, sterownika, seed i określonym backendzie deterministycznym.

## 15.2. Ω-VAE

- `latent_schema_id` musi zgadzać się z oczekiwaniami modelu generatywnego; nie ma automatycznej zgodności różnych VAE.
- `color_space`, `transfer_function`, `white_point`, `alpha_semantics`, `bit_depth`, `scaling_factor` i `temporal_stride` są typowanymi polami.
- Ścieżka `Ω-R` jest oznaczana `LOSSLESS` tylko jeśli istnieje sprawdzony residual, poprawna arytmetyka rekonstrukcji i bit-exact round-trip.
- Kafelkowanie 400 MP: formalnie sprawdza się pokrycie pikseli, brak brakujących kafli, bounds i indeksowanie; **równość jakości** tiled vs monolithic wymaga dodatkowych warunków modelu albo pomiarów, nie wynika z samego overlap.
- `Decode(Encode(x)) = x` nie jest twierdzeniem dla stratnego VAE; wymagany osobny kontrakt z metrykami jakości i tolerancjami.

## 15.3. CodeFormer Ω

- Tryb `Faithful Documentary` nie może automatycznie podmienić nieobserwowalnych detali na twierdzenie o faktycznej treści oryginału.
- Formalnie można dowieść: zachowanie oryginału, poprawność maski uprawnień, zgodność mapy zmian, brak nadpisania pliku NEF, etykietowanie rekonstrukcji i limit zakresu modyfikacji.
- Nie można formalnie dowieść „prawdziwej twarzy” z zasłoniętego lub nieodwracalnie zniszczonego obrazu bez dodatkowej informacji.

## 15.4. ArcFace Ω R100++

- Kontrakty embeddingu `R^512`, normalizacji, progu, wersji modelu i referencji.
- Formalna walidacja zgodności wymiarów i polityk; skuteczność FAR/FRR/EER jest **empiryczna**, zależna od zbioru testowego i warunków wdrożenia.
- `IdentityGuard` nie może zaakceptować fałszywej gwarancji tożsamości wyłącznie na podstawie cosine similarity.
- Wrażliwe embeddingi i wzorce twarzy podlegają ograniczeniom dostępu, retencji i minimalizacji danych; logi dowodów nie powinny przechowywać ich w postaci jawnej.

## 15.5. NEF Nikon D810 / 16-bit / ICC

Weryfikowalne niezmienniki: nienaruszalność oryginalnego NEF (SHA-256), brak zamiany profilu ICC bez jawnego transformu, kolejność linearizacji/white balance, zgodność wymiarów obrazu, zakresu i metadanych. Gamut clipping, banding, kolor i rozdzielczość końcowa wymagają osobnych testów obrazowych i walidacji barwnej. Żaden dowód grafu nie zastępuje pomiaru ΔE na rzeczywistych obrazach.

## 15.6. GeoDepth Ω / Depth Anything 3 — geometria 3D/4D

- Sprawdzalne kontrakty: zgodność układów współrzędnych, jednostek, transformacji kamery, orientacji osi, czasu, intrinsics/extrinsics, bounds depth i dopuszczalności reprojekcji.
- Przy geometrii projektowej dowód algebraiczny może potwierdzić poprawność transformacji i zależności macierzowych przy danych założeniach, ale **nie** prawdziwość głębi oszacowanej przez sieć neuronową.
- Niepewność depth/disparity, brakujące piksele, occlusions i temporal consistency są reprezentowane jawnie; ocena jakości na rzeczywistych scenach pozostaje empiryczna.
- Integracja jest kontraktowa z własnym GeoDepth Ω, nie wymaga wykonywania silnika Depth Anything ani ComfyUI wewnątrz kernela.


## 16.1. Wersjonowanie


## 16.2. Kontrakt żądania

```json
{
  "api_version": "1.0",
  "request_id": "2e4a31cf-2452-42f9-bd36-2d63f77f5a20",
  "idempotency_key": "verification-tenant-a-20261025-001",
  "tenant_id": "tenant-a",
  "model": {
    "language": "oml/1",
    "source_sha256": "c78ac5f55ef50bd6a989e930b7c64ecb4a76db1bdc7847ccaa09724c0f17c3d5",
    "snapshot_id": "snapshot-001"
  },
  "goal": "RetryPolicy.retry_requires_auth",
  "policy": {
    "proof_mode": "strict",
    "axioms": "none",
    "external_solvers": "certificate_only"
  },
  "budget": {
    "wall_clock_ms": 30000,
    "cpu_ms": 120000,
    "memory_bytes": 1073741824,
    "max_steps": 1000000,
    "max_parallel_workers": 4
  }
}
```

**Uwaga:** pola identyfikacyjne w przykładzie są danymi demonstracyjnymi schematu, nie identyfikatorami istniejącej sesji; `source_sha256` w prawdziwym żądaniu musi być obliczony z rzeczywistych bajtów.

## 16.3. Kontrakt odpowiedzi

```json
{
  "api_version": "1.0",
  "request_id": "2e4a31cf-2452-42f9-bd36-2d63f77f5a20",
  "job_id": "job-001",
  "status": "UNKNOWN",
  "proof": null,
  "evidence": {
    "model_snapshot_id": "snapshot-001",
    "reason_code": "SOLVER_INCOMPLETE",
    "kernel_attestation_ref": null
  }
}
```

**Kontrakt, nie rzeczywisty wynik:** odpowiedź ilustruje bezpieczne `UNKNOWN`, gdy nie powstał dowód. Serwer nie może wygenerować `PROVED_STRICT` bez dowodu, weryfikacji i podpisanego potwierdzenia.

## 16.4. Operacje i semantyka

| Operacja | Metoda | Semantyka |
|---|---|---|
| `CreateSession` | POST `/v1/sessions` | zwraca lease, TTL, tenant-bound session ID |
| `SubmitModel` | POST `/v1/models` | immutable model snapshot, hash |
| `Verify` | POST `/v1/jobs:verify` | asynchroniczny job i idempotency key |
| `FindInstance` | POST `/v1/jobs:instance` | świadek SAT, walidacja replay |
| `Decompose` | POST `/v1/jobs:decompose` | regiony i dowody coverage/disjointness |
| `GetJob` | GET `/v1/jobs/{id}` | odczyt stanu, ETag, tenant ACL |
| `CancelJob` | POST `/v1/jobs/{id}:cancel` | idempotentne żądanie anulowania |
| `GetProof` | GET `/v1/proofs/{digest}` | immutable proof bundle, digest check |
| `CheckProof` | POST `/v1/proofs:check` | niezależne sprawdzenie, bez solvera |

## 16.5. Błędy

`INVALID_MODEL`, `TYPE_ERROR`, `UNSUPPORTED_THEORY`, `UNKNOWN`, `TIMEOUT`, `RESOURCE_EXHAUSTED`, `INVALID_CERTIFICATE`, `ASSUMPTION_POLICY_VIOLATION`, `TENANT_ACCESS_DENIED`, `CONFLICT`, `REPLAY_DETECTED`, `INTERNAL_ERROR`. Każdy błąd ma stabilny kod maszynowy, bezpieczny komunikat, `trace_id`, retryability i zanonimizowany kontekst. `UNKNOWN` nie jest HTTP 500, lecz poprawnym rezultatem zadania rozumowania.

# 17. Format dowodu `Ω-PROOF` i łańcuch dowodowy

## 17.1. Proof Bundle

```text
omega-proof-bundle/
├── manifest.cbor                 # canonical CBOR; schema_version, algorithms
├── model.omlir                   # canonical typed model / references
├── environment.omlenv           # definitions and trusted library digests
├── assumptions.cbor             # exact assumptions and policy classification
├── theorem.omlprop              # canonical proposition
├── proof.omlp                   # DAG proof term / certificate translation
├── witnesses/                   # checked counterexamples when relevant
├── region-certificates/         # cover, disjointness, behavior
├── provenance.cbor              # toolchain, solver, seed, model hash
├── kernel-attestation.cose      # signature over checked result + digests
└── sbom.spdx.json               # build provenance where applicable
```

Manifest jest podpisany dopiero po weryfikacji wszystkich hashy i dowodu. `kernel-attestation` jest związany z: `theorem_digest`, `environment_digest`, `assumptions_digest`, `proof_digest`, `kernel_binary_digest`, `policy_digest`, `tenant_id`, `result`, `timestamp`, `nonce`. Podpis nie dowodzi poprawności kernela; potwierdza pochodzenie konkretnej decyzji kernela.

## 17.2. Proof DAG i canonical hashing

`NodeId = H(domain_separator || schema_version || opcode || typed_children || canonical_payload)`. Użycie jawnego domain separation eliminuje pomylenie digestu dowodu z digestem modelu. Referencje do dzieci muszą wskazywać istniejące węzły i tworzyć DAG; cykle są odrzucane. Odczyt nie może przyjąć `duplicate keys`, niekanonicznego CBOR ani różnych reprezentacji tej samej liczby. Wspierane algorytmy hashy i podpisów są wersjonowane; migracja jest operacją jawnego przeliczenia i ponownego podpisania.

## 17.3. Cache i poprawność

`CacheKey = H(Goal || ModelSnapshot || Environment || Axioms || SemanticsVersion || ProofPolicy)`. Cache `PROVED` jest przenoszalny tylko przy identycznym kontekście i poprawnym certyfikacie; cache wyników `UNKNOWN`/`TIMEOUT` jest zależny od budżetu i konfiguracji. Zmiana wersji reguł lub biblioteki dowodowej unieważnia odpowiednie wpisy. Cache nie zastępuje ponownego sprawdzenia certyfikatu w krytycznych operacjach.

# 18. Wydajność, współbieżność i plan zasobów

## 18.1. ResourceBudget

`wall_time`, `cpu_time`, `memory_peak`, `proof_bytes`, `term_nodes`, `max_smt_queries`, `max_llm_tokens`, `max_workers`, `max_recursive_depth`, `max_disk_bytes`, `max_network_bytes`. Każdy limit ma licznik atomowy i twardą granicę. Pamięć kernela jest odseparowana od pamięci workerów solvera. OOM workera nie może unieważnić innej sesji ani doprowadzić do wystawienia fałszywego `PROVED`.

## 18.2. Scheduling

- Fair scheduling per tenant, weighted quotas, oddzielne pule dla krótkich interaktywnych i długich batch.
- Work stealing wyłącznie w obrębie polityki tenant i capability; worker nigdy nie pobiera cudzych modeli bez uprawnienia.
- Portfolio solverów: różne strategie/seed; pierwszy sprawdzony wynik kończy pracę, pozostałe są anulowane.
- `SAT` i `UNSAT` sprzeczne w dwóch workerach → `INTEGRITY_FAILURE`, freeze dowodów, artefakty do analizy.
- Proof search z możliwością checkpointowania (snapshot taktyki, solver trail, lemma DB, zobowiązania) z wersjonowaniem semantyki; nie odtwarzać obcych, niespójnych checkpointów.

## 18.3. Target SLO (cele, nie pomiary)

| SLI/SLO | Cel do ustalenia w benchmarku | Mechanizm |
|---|---|---|
| API availability | ≥ 99.9% miesięcznie, po wdrożeniu HA | multi-replica ingress, health probes |
| P95 enqueue | ≤ 250 ms przy zadanym profilu obciążenia | bounded queues, autoscaling |
| Kernel false acceptance | 0 przypadków w suite negatywnym | independent checkers, fuzzing |
| Resource isolation | 0 cross-tenant leaks w testach adversarial | namespaces, sandbox, ACL |
| Proof reproducibility | 100% na pinned toolchain dla zestawu deterministic | canonical IR, seed, env hashes |
| Correct cancellation | 100% jobów zwalnia zasoby w określonym deadline | cooperative + forced kill |

Powyższe wartości są **proponowanymi progami akceptacyjnymi**; nie są dowodem, że system je spełnia.

# 19. Bezpieczeństwo, zero trust i supply chain

## 19.1. Model zagrożeń

Atakujący: nieuprawniony tenant, złośliwy użytkownik OML, podmieniony model z repozytorium, prompt injection w dokumentacji, złośliwy LLM, nieuczciwy solver, złośliwy proof bundle, niepoprawny plugin, compromised CI, osoba z uprawnieniem do logów. Chronione zasoby: prawdziwość `PROVED`, klucze, modele użytkownika, prywatne dane, repozytoria, tajemnice, ścieżki dowodów i integralność audytu.
## 19.2. Reguły wykonawcze

- Każdy komponent dostaje minimalne capability, z oddzielnymi tożsamościami usługowymi i politykami tenant.
- mTLS między usługami, OIDC/OAuth dla użytkowników, RBAC/ABAC na poziomie zasobów, rotacja certyfikatów i audyt.
- Solver workery w izolacji procesowej lub microVM; brak outbound network domyślnie; read-only rootfs, seccomp, cgroups, no-new-privileges, ograniczony `/proc` i syscall allowlist.
- Proof kernel w odrębnym sandboxie bez pluginów, bez dostępu do sekretów, bez dynamicznego ładowania kodu.
- Parser OML/SMT/CBOR/Protobuf traktuje wszystkie bajty jako niezaufane; limity i fuzzing.
- Rozwiązania dostawców SMT/LLM mogą być użyte tylko jako **niezaufane** backendy; egress i transfer danych zależny od świadomej polityki prywatności.
- Artifact registry: SBOM, pin digest, signature verification, reproducible builds, dependency policy, vulnerability scan, brak nieautoryzowanego dynamicznego pobierania kodu.
- Zapisy i checkpointy są atomowe, walidowane, tenant-scoped; path traversal i symlinki są odrzucane przez bezpieczny resolver.
- Secrets: KMS/HSM/keystore, krótkie TTL, żadnych kluczy w promptach, logach ani proof bundles.

## 19.3. Adversarial proof injection

Scenariusz: solver zwraca fałszywe `unsat`, LLM produkuje `theorem p by trust`, proof bundle zawiera podmieniony environment hash, a sesja odwołuje się do innego tenant. Oczekiwane: `INVALID_CERTIFICATE` / `ASSUMPTION_POLICY_VIOLATION` / `TENANT_ACCESS_DENIED`; zero publikacji certyfikatu i zapis bezpiecznego zdarzenia audytowego. Dowody zawierające nierozpoznaną regułę lub „opaque trusted step” są odrzucane w `strict`.

# 20. Observability, diagnostyka i audyt

## 20.1. Metryki

`omega_jobs_total{result,tenant_class}`, `omega_job_duration_seconds{strategy}`, `omega_proof_check_seconds{kernel_version}`, `omega_solver_conflicts_total{theory}`, `omega_unknown_total{reason}`, `omega_invalid_certificates_total`, `omega_counterexample_replay_total{status}`, `omega_memory_peak_bytes`, `omega_tenant_denied_total`, `omega_queue_depth`, `omega_model_typecheck_errors_total`, `omega_region_coverage_certificates_total`.

**Zakaz:** nie umieszczać surowych tenant IDs, formuł, obrazów, embeddingów, nazw plików, sekretów lub tokenów w etykietach metryk. Unikać high-cardinality label explosions.

## 20.2. Trace i audyt

OpenTelemetry trace przez gateway→session→solver→kernel→ledger; trace ID jest publicznie bezpieczny, a dane modelu są szyfrowane i dostępne według RBAC. Append-only event journal zawiera `timestamp`, `actor`, `tenant_scope`, `operation`, `resource_digest`, `policy_decision`, `result_code`, `proof_digest`, `kernel_digest`, `prev_event_hash`. Łańcuch hashy wykrywa modyfikację, ale nie zastępuje ochrony storage ani kontroli dostępu.

## 20.3. Reproducibility capsule

Każdy benchmark i istotny dowód przechowuje: commit SHA, wersję Rust, lockfile, wersje solverów, wersję DSL/IR, system, CPU/GPU, seed, limits, input digests, wybrane strategie i ślad decyzji. Dane prywatne mogą pozostać w bezpiecznym storage; publiczny raport zawiera tylko hashe i metadane dopuszczone polityką.

# 21. Architektura wdrożeniowa: mobilnie, chmura, HA

## 21.1. Android/Termux

Profil `OMEGA-EDGE`: lokalne parsowanie i walidacja małych modeli, mały kernel do sprawdzania gotowych certyfikatów, odczyt statusów i szyfrowany cache. Nie zakłada się, że smartfon rozwiąże wielogodzinne zadania SMT/HOL lub przeprowadzi pełny trening AI. Brak dostępnego `openssl`/pełnego `/proc` w Termux nie może być mylony z zaliczonym testem produkcyjnego mTLS; testy integracyjne muszą odbyć się na docelowym Linuxie.

## 21.2. Linux/Cloud

Profil `OMEGA-CLOUD`: `omega-gateway` + `sessiond` + `solverd` (worker pool) + `kerneld` (separate security domain) + `ledger`. PostgreSQL HA na metadane i sesje; content-addressed object storage na artefakty; opcjonalny Zenoh do zdarzeń; Kubernetes dla schedulerów i izolacji. Brak wymogu, by weryfikator kernela polegał na działającym brokerze przy sprawdzaniu dowodu offline.

## 21.3. HA i recovery

- Durable queue: `at-least-once` delivery z idempotentnym job ID; nie obiecywać exactly-once execution.
- Checkpoint co zdefiniowaną liczbę kroków lub czas; atomic commit i wersjonowanie snapshotów.
- Worker crash → job wraca do kolejki z incremented attempt, zachowuje identyczny `ModelSnapshot`.
- Proof check restart → niepublikowany certyfikat pozostaje nieważny; retry check od kanonicznych bajtów.
- Network partition → nie dopuścić do dwóch sprzecznych, aktywnych writerów ledger; fencing na warstwie storage.
- Shutdown: stop intake → drain/cancel → flush journal → zeroize secrets → release leases.

# 22. Repozytorium referencyjne i moduły Rust 2024

```text
imandrax-omega-engine/
├── Cargo.toml                     # workspace, rust-version pinned, edition=2024
├── Cargo.lock                     # tracked and audited
├── rust-toolchain.toml
├── README.md
├── LICENSES/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FORMAL_SEMANTICS.md
│   ├── THREAT_MODEL.md
│   ├── PROOF_POLICY.md
│   ├── API_CONTRACTS.md
│   ├── OPERATIONS.md
│   └── CERTIFICATION.md
├── crates/
│   ├── omega-syntax/             # lexer/CST/parser, untrusted
│   ├── omega-oml/                # typed AST, elaboration
│   ├── omega-ir/                 # canonical Ω-IR, hashes
│   ├── omega-kernel/             # TCB, forbid(unsafe_code)
│   ├── omega-proof-format/       # canonical proof bundle
│   ├── omega-certificate/        # proof translators
│   ├── omega-sat/                # CDCL + LRAT
│   ├── omega-smt/                # DPLL(T) and theory plugins
│   ├── omega-induction/          # tactics and lemmas
│   ├── omega-model-check/        # BMC/k-induction/PDR
│   ├── omega-region/             # region decomposition
│   ├── omega-math/               # exact rationals, matrices, intervals
│   ├── omega-agent/              # untrusted neurosymbolic planner
│   ├── omega-session/            # durable sessions
│   ├── omega-policy/             # ABAC/axioms/capabilities
│   ├── omega-gateway/            # gRPC/REST
│   ├── omega-aetheris-adapter/   # OmniFlow/Ω-VAE/CodeFormer/ArcFace
│   ├── omega-observability/      # OTel and audit
│   └── omega-cli/                # command-line and offline check
├── proto/omega/v1/
├── schemas/oml/
├── examples/verified/
├── examples/refuted/
├── tests/unit/
├── tests/contract/
├── tests/e2e/
├── tests/adversarial/
├── tests/differential/
├── tests/fuzz/
├── tests/performance/
├── benchmarks/
├── deployments/kubernetes/
├── deployments/systemd/
└── .github/workflows/
```

Wersja docelowa: `#![forbid(unsafe_code)]` w TCB i modułach, w których to możliwe. Wyjątki `unsafe` w FFI/solverach nie są dziedziczone przez kernel i wymagają odrębnego audytu. `Rust 2024` nie dowodzi braku błędów logicznych; testy i kontrola proof kernel są niezależne.

# 23. Testy, property-based i formalne dowody poprawności

## 23.1. Testy kernela — bezwzględna bramka

| ID | Scenariusz | Oczekiwany rezultat |
|---|---|---|
| K-001 | Poprawny dowód `p → p` | `Accepted` |
| K-002 | Fałszywy dowód `False` z pustego kontekstu | `Rejected` |
| K-003 | Dowód innego twierdzenia podmieniony w bundle | `Rejected` |
| K-004 | Ukryty `axiom`, `admit`, `trust` | `Rejected` w strict |
| K-005 | Cykl w proof DAG | `Rejected` bez OOM |
| K-006 | Niekanoniczny CBOR/duplikat klucza | `Rejected` |
| K-007 | Podmieniony hash definicji/środowiska | `Rejected` |
| K-008 | Capture zmiennej podczas podstawienia | `Rejected` |
| K-009 | Niepoprawna dodatniość typu indukcyjnego | `Rejected` |
| K-010 | Niedozwolona rekurencja | `Rejected` |
| K-011 | Użycie lematu po `pop` assumptions | `Rejected` |
| K-012 | Przekroczenie budżetu parsera | Controlled resource error |
| K-013 | Sprzeczne wersje semantyki | `Rejected` |
| K-014 | Sfałszowana atestacja kernela | `Rejected` |
| K-015 | Unknown opcode/extension | `Rejected` |

## 23.2. Solver i matematyka

- `SAT-001`: poprawność LRAT; celowo uszkodzone proof trace nie przechodzi.
- `SMT-001`: QF_LIA `x>0 ∧ x<0` → UNSAT z certyfikatem.
- `SMT-002`: integer overflow w BV jest modulo `2^w`, a nie w `Int`.
- `SMT-003`: `x/x=1` bez `x≠0` nie jest akceptowaną ogólną tożsamością.
- `SMT-004`: `NaN`, signed zero i rounding modes w FP nie są utożsamiane z rzeczywistymi.
- `BMC-001`: UNSAT do k=10 → `BOUNDED_SAFE(10)`, nie `PROVED_STRICT`.
- `PDR-001`: certyfikat invariantów sprawdzony na oryginalnym modelu.
- `REG-001`: pokrycie regionów bez dowodu → `PARTIAL_DECOMPOSITION`.
- `REG-002`: dwa regiony nakładające się → `INVALID_REGION_PARTITION`.
- `PROB-001`: Bayes z `P(B)=0` odrzucony jako niepoprawne założenie.
- `LIN-001`: Cholesky dla macierzy niedodatnio określonej → odmowa certyfikatu.
- `INT-001`: directed rounding obejmuje wynik referencyjny z arytmetyki dokładnej.

## 23.3. Testy bezpieczeństwa

- Fuzzing parserów OML, SMT-LIB, Protobuf, CBOR, proof DAG i AST depth.
- Prompt injection w dokumentach źródłowych: nie może zmienić polityki dowodu ani wywołać nieautoryzowanego narzędzia.
- Cross-tenant session/proof ID guessing i confused deputy.
- Race: cancel vs finish, snapshot mutation vs verify, lease expiry vs write.
- Symlink/path traversal w artifact store i cache.
- Exhaustion: głębokie termy, eksplozja rewrite, ogromne bigint, billion-literal CNF, memory bomb.
- Fault injection: kill solver, kill kernel, partition network, stale fencing, corrupted journal, expired mTLS cert.
- Supply chain: podmieniony solver/FFI, dependency confusion, unsigned model, compromised cache.

## 23.4. Benchmarking

Publiczne zestawy SMT-COMP/SMT-LIB, SV-COMP (dla obsługiwanych fragmentów), TPTP (po formalnej translacji), własne proof tasks i scenariusze IMANDRAX. Metryki: solved rate, soundness, proof-check time, counterexample validity, memory peak, p50/p95/p99 latency, throughput, energy, cost, regression rate. Benchmark porównawczy ImandraX jest dopuszczalny **wyłącznie** z uprawnionym dostępem, zgodnie z licencją, na tym samym korpusie i przy jawnych budżetach.

# 24. CI/CD i polityka wydania

```text
lint/format → build locked → unit → property-based → fuzz corpus
→ kernel adversarial → independent proof checker
→ solver differential → model-check regression
→ API contract → integration IMANDRAX/Aetheris
→ mTLS/tenant isolation → chaos/network tests
→ SBOM/SLSA provenance → signed artifact → staging E2E
→ operator acceptance → production deployment
```

**Fail-closed:** nie można wyłączyć bramki kernela przez flagę środowiskową, override LLM ani „temporary bypass” w release. Wydanie bez testów rzeczywistej infrastruktury ma status `LOCAL_VALIDATED`, nie `PRODUCTION_VERIFIED`. Audyt kodu, formalny proof i test E2E są odrębnymi kategoriami dowodów; nie zastępują się nawzajem.

# 25. Etapy realizacji i kryteria odbioru

| Etap | Zakres | Kryterium ukończenia | Stan |
|---|---|---|---|
| ΩR-00 | formalna semantyka, threat model, RFC kontraktów | recenzowane specyfikacje, baseline | SPECIFIED |
| ΩR-01 | parser OML + typed IR + canonical serialization | parser fuzz, deterministyczne hashe | NOT IMPLEMENTED |
| ΩR-02 | mały kernel i format proof DAG | wszystkie K-001..K-015, drugi checker | NOT IMPLEMENTED |
| ΩR-03 | CDCL + LRAT + QF_UF/LIA/LRA | certyfikaty sprawdzane, differential tests | NOT IMPLEMENTED |
| ΩR-04 | BMC/k-induction/CEGAR | validated traces i invariants | NOT IMPLEMENTED |
| ΩR-05 | indukcja, terminacja, tactics | dowody funkcji rekurencyjnych | NOT IMPLEMENTED |
| ΩR-06 | region decomposition | proof of coverage/disjointness | NOT IMPLEMENTED |
| ΩR-07 | exact math / interval / ML contracts | property-based, numeric enclosures | NOT IMPLEMENTED |
| ΩR-08 | neurosymbolic planner | zero trust bypass, bounded loops | NOT IMPLEMENTED |
| ΩR-10 | Aetheris OmniFlow/Ω-VAE/Face | real NEF, models, GPU contract tests | NOT IMPLEMENTED |
| ΩR-11 | telemetry, checkpoint, HA, performance | chaos, SLO, signed artifacts | NOT IMPLEMENTED |
| ΩR-12 | staging/production gate | full acceptance, no unresolved critical | NOT IMPLEMENTED |

Etapy nie są automatycznie tożsame z numeracją Roadmapy `imandrax-runtime` (np. 0.38–0.45). Integracja musi respektować istniejącą Roadmapę i nie renumerować etapów bez autoryzacji.

# 26. Kryteria końcowe „production-grade”

Wydanie produkcyjne jest możliwe dopiero po wykazaniu **wszystkich** warunków:

1. Jądro odrzuca niepoprawne dowody, a wszystkie produkcyjne `PROVED_STRICT` mają kompletne, ponownie sprawdzalne certyfikaty.
2. Istnieje udokumentowany model logiki i jawna polityka aksjomatów; brak ukrytych `trust` i oracle.
3. Kontrprzykłady są odtwarzane na oryginalnej semantyce, a bounded wyniki nie są promowane do unbounded.
4. Wspierane teorie i granice solvera są jednoznacznie zdefiniowane; `UNKNOWN` jest normalnym wynikiem.
5. Sesje, proof bundles, cache i worker pool są izolowane tenantowo; nie ma nieautoryzowanego odczytu.
6. Parser, kernel, solver i gateway przechodzą fuzzing, property-based, regression, differential i fault injection.
7. mTLS, cert rotation, retry, fencing, journal recovery i audyt są przetestowane na docelowej infrastrukturze.
8. Benchmarki mają jawne dane, sprzęt, wersje, budżety i artefakty; brak nieudowodnionych przewag nad ImandraX.
10. Nieprzetestowane funkcje są oznaczone jako planowane, bez deklaracji „gotowe”.

# 27. Ograniczenia epistemiczne i ryzyka naukowe

**Nierozstrzygalność:** ogólna poprawność dowolnego programu i dowolne twierdzenie wyższych rzędów nie mają uniwersalnej, zawsze kończącej się procedury decyzyjnej.  
**Niezupełność:** w odpowiednio silnych, spójnych systemach formalnych istnieją twierdzenia, których nie da się w danym systemie udowodnić ani obalić.  
**Model vs rzeczywistość:** dowód dotyczy modelu i założeń; nie gwarantuje, że implementacja, sterownik GPU lub sieć zachowuje się identycznie.  
**Dane statystyczne:** kalibracja, Monte Carlo i metryki ML nie są zamiennikami dowodów logicznych.  
**LLM:** generuje hipotezy i szkice; brak możliwości uznania samego tekstu za certyfikat.  
**Złożoność:** zadania SMT/HOL mogą wymagać zasobów rosnących wykładniczo lub gorzej; żadne „maksimum” nie eliminuje granic obliczalności.  
**Zaufanie:** mały kernel zmniejsza TCB, ale nie usuwa ryzyka błędów kompilatora, sprzętu, kryptografii ani aksjomatów.

# 28. Macierz źródeł i literatura pierwotna

| ID | Źródło | Zakres wykorzystania |
|---|---|---|
| R1 | https://imandrax.dev/docs/ | funkcje ImandraX i logika referencyjna |
| R2 | https://imandrax.dev/docs/verification/ | bounded/unbounded/interactive verification |
| R3 | https://imandrax.dev/docs/api/http-api/ | statusy, sesje, protobuf/Twirp; tylko punkt odniesienia |
| R4 | https://pmc.ncbi.nlm.nih.gov/articles/PMC7324025/ | publikacja systemowa Imandra, unrolling, induction, HOL |
| R5 | https://smt-lib.org/papers/smt-lib-reference-v2.7-r2025-07-07.pdf | standard składni/semantyki SMT-LIB |
| R6 | https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/ | idea małego kernela i separacji elaboracji |
| R7 | https://cvc5.github.io/docs/cvc5-1.3.4/proofs/proofs.html | formaty proof production i ryzyka translacji |
| R8 | https://cvc5.github.io/docs/cvc5-1.3.2/proofs/output_lfsc.html | LFSC i trust steps, polityka fail-closed |
| U1 | `Rozumowanie Matematyczne.pdf`, strony 1–14 | wymagane dziedziny matematyczne i wnioskowanie |
| U2 | `01_CODEFORMER_OMEGA_v1.0.md` | własny model rekonstrukcji i faithfulness |
| U3 | `02_ARCFACE_R100_OMEGA_v1.0.md` | embedding, identyfikacja i identity guard |
| U4 | `03_AETHERIS_OMNIFLOW_OMEGA_v1.1.md` | niezależny silnik grafowy i scheduler |
| U5 | `04_AETHERIS_OMEGA_VAE_v1.0.md` | latent contracts, RAW/HDR, 400 MP |
| U6 | `05_GEODEPTH_OMEGA_DEPTH_ANYTHING_3_v1.0.md` | depth/geometry, camera and 4D contracts |

**Pochodzenie zakresu:** źródło U1 jest listą pojęć, nie kompletną formalną specyfikacją. Architektura kernela, formaty i bramki są **autorskimi decyzjami projektowymi**. Publiczna dokumentacja ImandraX służy wyłącznie analizie funkcjonalnej; nie zakłada się znajomości kodu własnościowego.

# 29. Końcowa decyzja architektoniczna

**Rekomendowany rdzeń:** mały, audytowalny proof kernel w Rust 2024, niezaufany portfolio solverów SMT/model checking/indukcji, formalne certyfikaty i izolowane warstwy AI. **Najważniejsza przewaga projektowa do wykazania:** dowody przenoszalne, sprawdzalne offline i powiązane z rzeczywistymi kontraktami IMANDRAX/Aetheris, nie obietnica „rozwiązania całej matematyki”.

**Stan wydania dokumentu:** `SPECIFICATION COMPLETE / ENGINE IMPLEMENTATION NOT STARTED IN THIS DELIVERABLE`. Żadnego testu kompilacji, dowodzenia ani wdrożenia silnika nie należy uznawać za przeprowadzony na podstawie niniejszej specyfikacji.



---

# 30. Rozszerzenie obowiązkowe: program matematyczny z załącznika użytkownika

To jest integralny aneks normatywny do architektury Ω-Reasoner, nie ogólny słowniczek matematyki. Program pojęciowy z PDF otrzymuje moduły obliczeń, warunki domenowe, status pewności, modele dowodów i testy negatywne. **Wszystkie 14 stron przeanalizowano**. Rozpiska każdego z 239 wystąpień: `07_OMEGA_REASONER_PDF_14_STRON_ELEMENT_PO_ELEMENCIE.md`.

## M-00. Wymagania matematyczne przeniesione z załącznika, bez pominięć

Katalog 14-stronicowego źródła to **lista pojęć**: od skalarów, tensorów, rozkładów macierzy i gradientów, przez rachunek predykatów, grafy, Bayesa i modele Markowa, po statystyczne uczenie maszynowe, optymalizację, rachunek numeryczny, backpropagation i otwarte hipotezy matematyczne. Nie zawiera gotowego formalnego systemu aksjomatów, dowodów ani definicji API. Projekt IMANDRAX Ω ENGINE **dodaje** te elementy jako autorskie wymagania. Cały oryginalny tekst strony po stronie jest w `05_ROZUMOWANIE_MATEMATYCZNE_ZRODLO_MD.md`, a poniżej i w `04_OMEGA_REASONER_MATH_REQUIREMENTS_TRACEABILITY.md` zapisano ich architektoniczną interpretację.

**Punkty krytyczne:** 1–2 algebra i analiza; 3 logika, zbiory i grafy; 4–5 probabilistyka i wnioskowanie; 6–7 entropia, SLT, statystyka i optymalizacja; 8–9 Bayes, Kalman, sygnały, EM, precyzja; 9–10 hipotezy otwarte i tryby wnioskowania; 11–12 search/metaheurystyka i PAC; 13 modele graficzne/generatywne; 14 perceptron, aktywacje i backpropagation.

## M-01. Formalna taksonomia roszczeń (`ClaimKind`)

Żądanie modelu **MUST** deklarować kategorię oczekiwanego wyniku oraz rozróżniać założenia od danych wejściowych:

```rust
// IDL referencyjny, NIE kod wdrożony
pub enum ClaimKind {
    LogicalTheorem,
    ModelSafety,
    ModelReachability,
    NumericBound,
    StatisticalGuarantee,
    EmpiricalEstimate,
    OptimalityCertificate,
    HeuristicCandidate,
    OpenResearchConjecture,
}
pub enum Assurance {
    ProvedStrict,
    ConditionalProof,
    BoundedSafe,
    RefutedValidated,
    NumericCertified,
    StatisticalBound,
    Estimated,
    CandidateOnly,
    Unknown,
    Invalid,
}
```

**Prawa przejścia:** `LogicalTheorem → ProvedStrict` tylko po sprawdzeniu przez Ω-Core bez niedozwolonych aksjomatów; `ModelSafety → BoundedSafe` tylko dla dokładnie określonego horyzontu, nigdy „safe forever”; `NumericBound → NumericCertified` tylko z niezależnym sprawdzeniem otaczających przedziałów z directed rounding; `StatisticalGuarantee → StatisticalBound` po zweryfikowaniu warunków twierdzenia i założeń o danych, nie empirycznego świata; `EmpiricalEstimate → Estimated`; `HeuristicCandidate → CandidateOnly`; `OpenResearchConjecture → Unknown` aż do rzeczywiście sprawdzonego dowodu. `OptimalityCertificate` wymaga dual feasibility + primal feasibility + duality gap lub innego prawidłowego certyfikatu dla zadeklarowanego fragmentu.

**Istotne rozróżnienie:** jeżeli model danych ma błędne założenia, poprawny formalny dowód dowodzi jedynie poprawności formuły w tym modelu. Dowód nie certyfikuje sam prawdziwości założeń opisujących świat fizyczny, człowieka, jakość zdjęcia ani prawa.

## M-02. Matematyczny system typów `OmegaMathType`

**Typy skalarne:** `Nat`, `Int`, `Rational`, `RealSymbolic`, `AlgebraicReal`, `Interval<Real>`, `Float<format,rounding>`, `Complex<Rational|Real>`, `Probability<[0,1]>`, `LogProbability`, `Unit<Q>`; `Bool` i `Prop` są różne. Właściwości kodowania i niezależności od platformy: integer exact `BigInt`, rational w postaci zredukowanej `BigRational`, przedziały jako para skończonych granic lub ±∞ z flagą otwartości, jawne signed zero i IEEE NaN/Inf w typie float.

**Typy struktur:** `Vector<T,n>`, `Matrix<T,m,n>`, `Tensor<T,[d_0,..d_k]>`, `SparseMatrix<T,m,n,CSR|CSC>`, `SymmetricMatrix<T,n>`, `SPDMatrix<T,n,Certificate>`, `LinearOperator<Dom,Cod>`, `Graph<Vertex,Weight,Directedness>`, `ProbabilitySpace<Ω,Σ,P>`, `Distribution<T>`, `StochasticProcess<T,Index>`, `Function<Domain,Codomain,Effect=Pure>`, `DifferentiableFunction<k>`, `MeasureSpace`, `HilbertSpace`, `Kernel<PositiveSemidefinite>`, `ParameterSpace<Bounds>`, `OptimizationProblem<Objective,Constraints>`.

**Wymóg shape safety:** `mul(Matrix[m,n],Matrix[n,p])->Matrix[m,p]`; mnożenie `Matrix[m,n] × Matrix[p,q]` przy `n≠p` odrzucane przez typechecker, nie przez przypadkową awarię GPU. `trace`/`det` tylko kwadratowe. `inverse(A)` wymaga dowodu `det(A)≠0` albo wyniku `Option<InvertibleMatrix>`. `Cholesky` wymaga SPD świadectwa; dla wartości floating zwraca przedział certyfikujący poprawność rozkładu w zadanej normie, albo niepowodzenie. Cosine similarity ma niezerowe normy obu wektorów. `ln` ma domenę dodatnią lub pracuje w odrębnym kompleksowym type. `P(A|B)` wymaga `P(B)>0`.

**Units/refinement:** jawne `Seconds`, `Frames`, `Pixels`, `Radians`, `Degrees`, `Meters`, `Millimeters`, `Nits`, `EV`, `Byte`, `Samples`; unikać `add(3 frames,4 seconds)` bez konwersji z `frame_rate`. Prawdopodobieństwo `p` musi spełniać `0≤p≤1`. Macierz transformacji `CameraIntrinsics` musi być dodatnia gdzie wymagane; ortogonalność `RᵀR=I` jest claim sprawdzanym, nie wywodzonym z nazwy typu.

**Proof-relevant types:** `Finite(n)`, `NonZero`, `Positive`, `PSD`, `SPD`, `StochasticMatrix`, `RowStochastic`, `ContinuousOn(I)`, `DifferentiableOn(I)`, `BoundedDerivative(k,I,B)`, `IntegrableOn(I)`, `LipschitzOn(I,L)`, `ConvexOn(D)`, `Independent(A,B)`, `Measurable(f)`, `AlmostSurely`, `ValidReduction(target,source)`. Bez poprawnych konstruktorów weryfikujących świadectwo nie wolno tworzyć tych typów z niezaufanego JSON.

## M-03. System pojęć algebraicznych i tensorowych [PDF s.1–2, 5, 7–8]

### M-03.1. Operacje dokładne i algebraiczne

- Skalar, wektor, tensor: canonical shape, dtype, jednostka i semantyka; aliasing i overflow wymiarów `n*m*sizeof(T)` sprawdzane przed alokacją.
- Macierze ogólne, diagonalne, jednostkowe, symetryczne, ortogonalne i rzadkie: reguły konstrukcji oraz preserving operators (`transpose`, `dot`, `cross`, `Hadamard`, `sum`, `matmul`, `trace`, `det`, `inverse`).
- Testy algebraiczne w `BigRational`: `A(B+C)=AB+AC`, `(AB)ᵀ=BᵀAᵀ`, `tr(AB)=tr(BA)` dla zgodnych kwadratowych produktów, `det(AB)=det(A)det(B)` dla kwadratowych; nie wnioskować ich bitowo dla FP16 przez błędy zaokrągleń.
- Normy `L₁`, `L₂`, `L∞`, odległość euklidesowa, Manhattan, podobieństwo kosinusowe: nonnegativity, triangle inequality dla właściwych norm, brak dzielenia przez zero; porównanie wymaga tej samej metryki i identycznego preprocessing.
- Iloczyn wektorowy jest 3D lub w odpowiednio zdefiniowanej algebrze; nie jest generycznym iloczynem dowolnych tensorów.

### M-03.2. SVD / LU / QR / Cholesky / Eigen

`omega-linear` ma dwie ścieżki: `SymbolicExact` — dla obsługiwanych dziedzin dokładnych; `CertifiedNumeric` — dla floating/real z przedziałowymi boundami. SVD `A≈UΣVᵀ`: checker weryfikuje `||A-UΣVᵀ||≤ε`, `||UᵀU−I||≤ε_U`, `||VᵀV−I||≤ε_V`, niemalejąco/niemaleniem zadeklarowany porządek singular values. `Eigen` weryfikuje `||Av−λv||`, normę i separation of eigenvalues, jeśli claim o pojedynczości; kondycjonowanie i błędy zależne od bliskości wartości własnych. QR: orthogonality+triangularity+residual. LU: jawna permutacja `PA=LU`, pivot assumptions. Cholesky: `A≈LLᵀ`, dodatnia diagonal, SPD validation. Każdy numeric result ma error bound, platform digest i interval rounding mode. **Nie wolno wydać `PROVED_STRICT` na podstawie numerycznego `np.allclose`.**

### M-03.3. Tensor operations dla AI

Broadcasting nie może automatycznie przestawiać osi, układ `NCHW` kontra `NHWC`, dtype `BF16` kontra `FP32`, stride i alias analysis jawne. Formalizować spec operatorów: `Conv2d` z padding/dilation/stride i shape preservation; matrix multiply z tolerancją; attention scaling i mask; softmax z logsumexp. Gdzie gpu kernel ma nondeterminism, zachować statystyczny regression test, nie pozorowany dowód bitowej powtarzalności.

## M-04. Analiza matematyczna i automatyczne różniczkowanie [PDF s.2,5,8]

`omega-calculus` implementuje symboliczne różniczkowanie na AST dla wyrażeń należących do obsługiwanego języka, z generowaniem warunków dziedzinowych i różniczkowalności. Reguła łańcuchowa: dla `h=f∘g`, `Dh(x)=Df(g(x))·Dg(x)` pod warunkami istnienia pochodnych; `∇f` dla funkcji skalarnej, `J_f` dla wektorowej, `H_f=J_{∇f}` przy odpowiedniej gładkości. `ReLU` ma jawnie zadany subgradient albo przedział w punkcie zero, bez fałszywego twierdzenia o pochodnej klasycznej.

`Taylor`: dla `f∈C^{k+1}` i `x∈I`, reszta |R_{k+1}(x)| ograniczona przez `M |x−x₀|^{k+1}/(k+1)!` przy certyfikacie `|f^{(k+1)}|≤M`. `Limit` i `Continuity`: wymagają jawnej topologii i przedziału, nie traktować samplingu jako dowodu granicy. Całki nieoznaczone to funkcje pierwotne z certyfikacją przez różniczkowanie przy warunkach; oznaczone to certyfikowane przedziały dla całek z zadeklarowaną miarą/regularnością albo `UNKNOWN`.

`Optimization extrema`: punkt stacjonarny (`∇f=0`) nie implikuje minimum; `Hessian≻0` w punkcie daje lokalną wystarczającą przesłankę przy wymogach gładkości, a globalne minimum wymaga np. convexity na convex domain. Siodło identyfikowane przez odpowiednie widmo Hessian z certyfikowanymi znakami; zero eigenvalues = wniosek niejednoznaczny.

Dwa mechanizmy: `SymDiff(expr,var)` emitujące `ProofObligation`, `ADGraph` używany w kontraktach NN. Mechanizm walidacji AD: (1) source symbolic derivative albo przedział; (2) porównanie z reverse/forward AD; (3) różnice skończone **tylko test diagnostyczny**, nie dowód. `BlackBoxGrad` bez modelu funkcji ma status `Estimated`.

## M-05. Logika klasyczna, zbiory, grafy, search [PDF s.3,10–11]

**Podstawa formalna:** wyraźne rozdzielenie syntax (`Formula`) i semantics (`Interpretation`). Klasyczny rachunek zdań, FOL z prawidłowym zakresem kwantyfikatorów, równość, sorty, funkcje, relacje, konstrukcje zbiorów (`Empty`, `Union`, `Intersection`, `Difference`, `Product`, `Subset`) z określoną dziedziną. Nie dodawać bez ograniczeń teorii mnogości przez swobodną komprehensję (ryzyko paradoksów); preferować typowane skończone zbiory i świadomie dobrany system aksjomatów dla nieskończonych.

`Graph`: skierowany/nieskierowany, ważony/bez wag, pętla/cykl, ścieżka, drzewo, adjacency matrix, Laplacian (wybór `D−A` i graph conventions zapisany w type metadata). Dijkstra: kontrakt nonnegative finite edge weights; directedness i disconnected nodes. Warunki pre/post: ścieżka od źródła, sum of weights, każdy znaleziony `dist[v]` minimalny względem wszystkich dopuszczonych ścieżek (dla danej skończonej instancji). `ShortestPathProof`: sprawdzalne witness paths, feasible distances, triangle inequalities dla każdej krawędzi, equality na krawędziach ścieżki. Ten certyfikat działa również jako checker wyniku niezaufanego algorytmu.

`StateSpaceSearch`: BFS/Dijkstra/A* z rozdziałem heurystyk admissible i non-admissible; lower bound tylko jeśli dowód `h(s)≤cost*(s)` przy odpowiednim systemie; pruning alfa-beta dla skończonych gier z fixed zero-sum utility; minimax ma dowód wyłącznie przy pełnym finite game tree. Genetyczne i heurystyczne solvery zwracają `CandidateOnly` dopóki optimum nie ma zewnętrznego certyfikatu.

## M-06. Prawdopodobieństwo, statystyka i teoria informacji [PDF s.4–8,12–13]

### M-06.1. Semantyka probabilistyki

`ProbabilitySpace(Ω,Σ,P)` z aksjomatami miary (nieujemność, normalizacja, σ-addytywność dla teorii ogólnej); w praktycznym kernalu P0 skończony dyskretny fragment z rozkładami `Rational` o sprawdzonej sumie 1. Późniejsze modele ciągłe mają zdefiniowane σ-algebry, measurability i integrability. `Conditional(A|B)` wyłącznie gdy `P(B)>0`, `Independence(A,B)` jako oddzielne założenie lub sprawdzona tożsamość.

Zmienne losowe, dystrybuanta CDF, density PDF, E[X], Var(X), Cov(X,Y), Corr(X,Y) z warunkami istnienia momentów. `Corr` wymaga niezerowych wariancji. Rozkłady Normal/Bernoulli/Binomial/Poisson/Exponential/Uniform/Beta/Gamma: wszystkie parametry walidowane i zapisane w `DistributionDescriptor` z support i normalizer constraints. Formalna własność p.d.f. musi odróżniać gęstość od masy; Bayes dla gęstości wymaga dominującej miary i normalizacji posterior.

### M-06.2. Twierdzenia i estimatory

`Bayes`: `P(A|B)=P(B|A)P(A)/P(B)` przy `P(B)>0`. `MLE` jest argmax log-likelihood (możliwy wielowartościowy lub nieistniejący), a `MAP` argmax posterior zależny od prior — nie „prawdziwy parametr”. LLN/CLT z wymienionymi warunkami (np. iid+moment zależnie od wariantu); `MonteCarloEstimate` zawiera sampling design, RNG/seed, effective sample size, uncertainty/CI i błąd oszacowania; high confidence empirical nie jest `ProvedStrict`. `p-value` jest miarą zgodności danych przy null model, **nie prawdopodobieństwem prawdziwości hipotezy zerowej**. Hipotezy statystyczne i cross-validation: k-fold grouping, leakage controls, confidence intervals oraz niepewność modelu.

### M-06.3. Informacja i uczenie statystyczne

Entropia Shannon `H(P)=−Σ p_i log p_i` z przyjętą podstawą log i `0 log 0=0`; cross-entropy `H(P,Q)` gdy support(P)⊆support(Q), KL `D_KL(P||Q)=Σ p log(p/q)` z wartością `+∞` w przypadku utraty support. Mutual information `I(X;Y)=D_KL(P_{XY}||P_X P_Y)` tylko przy spełnieniu definicji i z obsługą nieskończoności. Regression `bias²+variance+noise` jedynie przy określonym estimator/model/loss. VC dimension, Rademacher complexity i PAC bounds wymagają właściwej definicji hipotez, sampling assumptions i współczynnika ufności; wynik jest warunkową gwarancją dla modelu i procedury losowania, nie potwierdzeniem prawdziwości pojedynczej klasyfikacji.

## M-07. Łańcuchy Markowa, HMM, Kalman, modele probabilistyczne [PDF s.5,8–9,13]

`MarkovChain(S,P)`: `P[i,j]≥0`, `Σ_j P[i,j]=1`; `RandomWalk` jest określony przez transition law. `HMM`: rozkład początkowy π, transition A, emission B, stany ukryte i observed alphabet z poprawnymi normalizatorami. Forward/Backward/Viterbi obliczane w log-domain (logsumexp) i porównywane z enumeracją na małych przypadkach. Algorytm Viterbi zwraca ścieżkę **maksymalnej wiarygodności w zadanym modelu**, a nie „faktyczny ukryty stan”. `ExpectationMaximization` gwarantuje nondecreasing objective przy prawidłowym exact E/M i regular conditions; implementacje przybliżone nie mają automatycznej gwarancji monotoniczności. Zapis `iteration objective`, convergence diagnostics i local-optimality warnings.

`Kalman`: poprawne shape macierzy F,H,Q,R, warunki symetrii/PSD kowariancji, update predykcyjny i pomiarowy (preferowana numerycznie forma Joseph dla kowariancji), obsługa singular innovation covariance, brak inverse gdy matrix ill-conditioned. `Smoother` osobnym trybem offline bez future leakage do causal filter. Nie traktować szacunku pozycji i uncertainty covariance jako matematycznego dowodu prawdziwej trajektorii świata.

`GraphicalProbabilisticModel`: Bayesian network ma DAG i conditional probability distributions z walidacją, factor graph określa product-of-factors, inference engine wybiera exact variable elimination dla małych przypadków, variational inference/loopy BP lub MCMC jako approximate z `Estimated` i diagnostyką zbieżności. `Chaos`: testy wrażliwości na warunki początkowe i propagacji przedziałów; z teorii chaosu nie wynika prawo do arbitralnych prognoz długoterminowych.

## M-08. Optymalizacja, teoria gier i heurystyki [PDF s.5–7,9,11]

**Klasy:** LP, QP, optymalizacja wypukła, nierówności/wielomiany, constrained NLP, black-box optimization, meta-optimization, Bayesian optimization, minimax/alpha-beta, Nash equilibria (gry skończone) i heurystyki PSO/GA/simulated annealing.

`LP`: matematyczne wejście `min cᵀx, Ax≤b, Ex=d`; solver emituje primal candidate, dual variables oraz certyfikat optymalności lub Farkas infeasibility w exact rationals. Sprawdzenie feasibility, dual feasibility i duality gap w checker. `QP`: gwarancje convex tylko dla `Q⪰0`; KKT warunkowo, przy jawnie określonych regularity/constraint qualifications; bez kwalifikacji warunków KKT nie są automatycznym dowodem globalnego optimum. `Lagrange`: optymalność ograniczona qualification i convexity; `ProjectedGradient` wymaga przynależności do feasible set i warunków zbieżności. `Newton/Quasi-Newton`: diagnostyka Hessian, line search, trust region, kondycjonowanie.

`SGD`, `Momentum`, `Nesterov`, `Adam`, `RMSProp`, `Adagrad`, coordinate descent: każdy update ma jawny tensor equation, epsilon, learning rate schedule, finite precision semantics, optimizer state i test referencyjny na małym problemie. Warianty Adam z bias correction sprawdzane względem symbolic timestep; no silent `state-reset`. Żaden z tych algorytmów nie obiecuje globalnego optimum w ogólnym niekonwek­sowym ML.

`BlackBox/BayesianOptimization`: posterior model i acquisition function (EI/UCB/PI) z identyfikacją niepewności; optimum po budget kończy statusem `CandidateOnly`. `PSO/GA/Evolutionary/SimulatedAnnealing`: unikatowy seed, ograniczenia budżetu, kontrola feasible region, sortowanie fitness, bounded generations i raport incumbent candidate. `GameTheory`: wymiana reguł gry/utility invalidates result; Nash equilibrium dla skończonej gry z certyfikatem payoff inequality, lub `Unknown` gdy problem poza zakresem.

## M-09. Analiza numeryczna, FFT, splot, precyzja [PDF s.8–9]

`IEEE-FP` nie jest real numbers: FP16/BF16/FP32/FP64 mają rounding, subnormal, overflow, underflow, ±0 i NaN. Dowód w ℝ **nie jest** automatycznie dowodem programu wykonywanego w floating-point. `FPExpr` ma semantykę IEEE (w granicach operatorów, flags, modes). `roundoff_cert`: forward error interval i, gdzie potrzebne, backward error z conditioning. Brak rigorous bound → `Estimated`, nie `NumericCertified`. `fast-math`, fused multiply-add, denormal flush, parallel reductions wpływają na wynik; kompilator nie może ich ukrywać przy roszczeniu o poprawność numeryczną.

`FFT`: sprawdzanie inwersji z tolerancją i jawnie wybraną normalizacją; dla N punktów istnieje definicja DFT exact w pierścieniu/kompleksie, implementacja FFT ma dokumentować reorder, zero-padding, windowing, overflow i błąd. `Convolution`: granice, padding, stride, kernel flip vs cross-correlation, dystrybucja i temporal causality. `Regularization`: Ridge/Tikhonov, Lasso, Elastic Net mają jawne normy i domain; λ≥0, a L1 jest nieróżniczkowalna w zero. `Whitening`: covariance PSD, epsilon and regularization, zero eigenvalue policy; `OrthogonalProjection`: algebraiczna idempotencja P²=P i (dla projekcji ortogonalnej) Pᵀ=P. `ManifoldLearning MDS/Isomap`: output jest estymowaną reprezentacją i nie gwarantuje zachowania prawdziwej topologii bez warunków.

## M-10. Matematyczne kontrakty AI: perceptron, NN, VAE, ArcFace, Depth [PDF s.5–6,9,13–14]

`NeuralNetContract` posiada warstwę symboliczną (operator, input/output shape, activation, quantization, semantic preprocessing) oraz layer `NumericEnvelope` (lokalne granice propagacji błędu). `Perceptron`: `sign(w·x+b)` lub jawna nonlinearity; `ReLU/Sigmoid/Tanh` z poprawnymi bounded output (Sigmoid∈(0,1), tanh∈(-1,1) dla finite real), overflow-safe logsumexp i stabilny tanh; subgradient ReLU w zerze jawny. `Backprop`: reverse-mode AD chain rule, sprawdzane Jacobians dla differentiable subgraphs; dla większych modeli compositional bounds (IBP, linear relaxation, branch-and-bound z certyfikatem); dokładna weryfikacja ogólnej dużej NN może być zbyt kosztowna.

**Ω-VAE:** sprawdzenie `(mu, logvar)` shape, KL formuły przy `σ²>0`, prawidłowy clipping i preprocessing HDR, bounds `LatentSchema`, samopodobieństwo nie dowodzi bezstratności. `Ω-R` proof: bit-exact residual roundtrip na przyjętym integer buffer, a nie wiara w lossy decoder. `ArcFace Ω`: sprawdzalne `||embedding||₂≈1`, cosine defined, input/alignment contracts; próg biometryczny jest ustalany empirycznie, nie aksjomatem. `CodeFormer Ω`: modyfikacja w trybie faithful ma provenance i opaque original reference; weryfikacja policy no synthesized identity claims. `GeoDepth Ω`: ograniczenia dodatniej głębi i fizyczne jednostki, consistency poses i reprojection residual; monocular metric depth może być nieidentyfikowalne bez źródła skali. `OmniFlow Ω`: shape & color contract, acyclic graph proof, bounded allocation, typed node effects; brak ComfyUI jako zależności wykonawczej. Odpowiednio: `proof_of_contract` dotyczy dokładnie formalnego modelu, a `benchmark_validated` realnych wag i plików.

## M-11. Dedukcja, indukcja, abdukcja, probabilistyczny search [PDF s.9–11]

**Dedukcja:** dowód wynikający z logicznego następstwa Γ⊢φ; tylko formalny proof term (lub pełny weryfikowalny certyfikat) jest źródłem `ProvedStrict`. **Indukcja matematyczna:** baza P(0), krok ∀n(P(n)→P(n+1)) i jawna dziedzina Nat; indukcja strukturalna po rekursywnych typach wymaga termination/well-founded order. **Indukcja empiryczna:** generalizacja z przykładów i danych, nie jest dowodem indukcyjnym w logice. **Abdukcja:** generowanie najlepszego wyjaśnienia oznaczone `Hypothesis`, z rankingiem, priors i alternatywami, nawet gdy `argmin Cost`. **Probabilistic reasoning:** wnioskowanie w zadanym modelu miary, wynik `Posterior/CI`, nie logiczna konieczność. **State-space heuristic search:** zobowiązanie nie mieszać znalezienia kandydata z udowodnieniem kompletności przeszukania.

### M-11.1. Formalna reguła niepromowania

```text
neural_proposal          → HYPOTHESIS
SMT model candidate      → COUNTEREXAMPLE_CANDIDATE
counterexample replay    → REFUTED_VALIDATED (tylko w obsługiwanym modelu)
heuristic optimum        → CANDIDATE_ONLY
Monte-Carlo estimate     → ESTIMATED
validated confidence     → STATISTICAL_BOUND
SMT unsat without proof  → UNKNOWN/UNVERIFIED
proof certificate pass   → PROVED_STRICT (dla ustalonego Γ ⊢ φ)
```

Gdy `solver.unsat` nie ma pełnego proof log, ten wynik pozostaje **niezweryfikowany w trybie strict**. Jeżeli użyto zewnętrznego lub nieudowodnionego aksjomatu, wynik jest `ConditionalProof`, ze zbiorem aksjomatów w manifeście. „Axiom-free” jest prawdziwe tylko gdy wszelkie bazowe definicje i zasady są jawne i zgodne z wybraną logiką.

## M-12. Otwarte problemy matematyczne i granice naukowe [PDF s.9–10]

Zawiera: hipoteza Riemanna, podejście Hilberta–Pólyi, hipoteza Hodge'a oraz P vs NP. **Wymaganie:** można tworzyć formalne definicje, przeszukiwać skończone przykłady, generować lematy i kontrprzykłady dla *niepoprawnych twierdzeń pośrednich*, ale nigdy deklarować „rozwiązano” bez kompletnych formalnych i matematycznych przesłanek. Dla Riemann i Hodge istnieją subtelne kwestie wyboru aksjomatów, matematycznej formalizacji i ekwiwalencji; zweryfikowanie skończonego zakresu zer funkcji albo klas kohomologii nie stanowi rozwiązania hipotezy. Hilbert–Pólya jest programem/spekulatywną drogą badawczą, nie samodzielnym dowiedzionym twierdzeniem. `P≠NP` ani `P=NP` nie wynika z eksperymentów SAT benchmark. `OpenProblemRecord`: definicja formalna i wersja, known results, proof obligations, unverified conjectures, assumptions, frontier, human mathematical review status. Brak certyfikatu = UNKNOWN.

## M-13. Silnik kompozycji dowodów i certyfikatów

Pipeline: `user/PDF/DSL → parse → elaboration → typed Ω-IR → obligations → portfolio solvers → proof candidate → canonical proof DAG → minimal Ω-Core checker → immutable theorem record`. Każde obliczenie zewnętrzne emitujące przybliżenie musi przekazać `CalculationCertificate` z rounding controls albo zostać oznaczone statusem pomocniczym. Wychodzenie z `UNKNOWN` do „proved” przez LLM prohibited.

**Deductive kernel soundness objective:** `if Check(Γ,p,φ)=true then Γ⊢φ` w semantyce zaakceptowanego formalnego systemu. Samo napisanie takiej specyfikacji nie jest dowodem soundness implementacji. Minimalne funkcje `check_type`, `check_rule`, `check_axiom_policy`, `check_binding_scope`, `check_numeric_certificate`, `check_proof_dependencies`, `check_theorem_hash`. TCB ma izolowany proces bez sieci, privilege separation, żadnych pluginów i total parsers, a wyniki wszystkich solverów są traktowane jako niezaufane.

`Ω-ProofBundle` obligatoryjnie: `kernel_version_sha`, `logic_profile`, `axiom_set_hash`, `assumption_set`, `problem_hash`, `proof_dag_hash`, `dependency_hashes`, `solver_advisory_info`, `check_result`, `signature_metadata`, `replay_command`, `test_vectors`. Użytkownik musi móc lokalnie uruchomić **checker** bez chmury, nawet jeśli solver pracował zdalnie. Zmiana jednego założenia zmienia hash problemu i unieważnia poprzednie dowody tej formuły jako nowe twierdzenie.

## M-14. Dwie kompletne ścieżki przykładów: dowód i pomiar

### M-14.1. Dijkstra: formalny certyfikat wyniku (PDF s.3)

Dane `G=(V,E,w≥0)`, `source=s`, `d(s)=0`, `d(v)=∞` dla nieosiągalnych i finite `d(v)` dla reachable. Świadectwo zawiera osiągalność, parent pointers i `d(v)≤d(u)+w(u,v)` dla każdej krawędzi, równość na krawędziach w drzewie shortest-path, brak cykli w drzewie i właściwą obsługę infinity. Checker weryfikuje constraints; dla każdego osiągalnego v uzyskuje dolne ograniczenie przez inequalities na dowolnej ścieżce oraz górne przez witness path. Przy finite signed/wage types algebra musi wykluczać overflow. **Wynik:** validated optimal paths w skończonym grafie, nie wymaga zaufania do kodu Dijkstra.

### M-14.2. Bayes: obliczenie dokładne vs estymacja (PDF s.4,12)

Dane `P(A)=1/10`, `P(B|A)=9/10`, `P(B|¬A)=1/5`. Exact rational: `P(B)=(9/10)(1/10)+(1/5)(9/10)=27/100`, więc `P(A|B)=(9/100)/(27/100)=1/3`. Checker weryfikuje arytmetykę i twierdzenie Bayesa pod warunkami rozłączności A i ¬A, `P(B)>0`. Jeżeli prawdopodobieństwa wejściowe zostały wyestymowane z danych i mają niepewność, wynik 1/3 jest wnioskiem **warunkowym** dla wpisanych liczb; nie dowodzi faktycznej częstości w świecie.

### M-14.3. Float: przykład błędnej intuicji exact real (PDF s.9)

Dla zdefiniowanego IEEE binary32 `a=2²⁴`, `b=1`, typowe round-to-nearest-even `fl(a+b)=a`, ale w ℤ `a+b>a`. Teza `fl(a+b)>a` nie jest prawdziwa w zadanej semantyce. Ten wektor jest obowiązkowym testem negatywnym i musi zwrócić valid counterexample. Analogicznie `NaN==NaN` false przy właściwej semantyce IEEE, a nie classical equality w sort Real.

## M-15. Akceptacja technologiczna powiązana z 14 stronami PDF

### M-15.1. Testy bazowe

- `M-LIN-*`: typowanie tensorów, shape mismatch, wyznacznik na niekwadratowej, SVD/QR/LU/Cholesky certificate, zero-vector cosine, condition number.
- `M-CALC-*`: chain rule, Jacobian/Hessian shapes, nondifferentiability ReLU/abs, Taylor bound, integral domain failure, saddle point vs minimum.
- `M-LOG-*`: tautology, contradiction, quantifier capture, set paradox prevention, typed graph, Dijkstra positive/negative weights, temporal induction validity.
- `M-PROB-*`: Bayes denominators, conditional distributions, support mismatch KL→∞, CDF monotonicity, HMM normalizers, Monte Carlo CI, LLN/CLT assumptions.
- `M-STAT-*`: p-value interpretation, CV leakage, PAC bound preconditions, VC/Rademacher formal statement, correlation zero-variance failure.
- `M-OPT-*`: LP primal/dual/Farkas certificates, QP convexity, KKT qualification, stochastic optimizer updates, nonconvex local-only, metaheuristic CandidateOnly.
- `M-NUM-*`: IEEE 754 false identities, directed interval rounding, LU residual, unstable softmax, FP16 overflow, FFT normalization, convolution border semantics.
- `M-ML-*`: perceptron activation bounds, backprop chain rule, adversarial local bounds, VAE KL, ArcFace cosine contract, Depth unit conversion.
- `M-META-*`: proof kernel malformed terms, invented theorem, bounded≠unbounded, open conjecture UNKNOWN, LLM fake proof, out-of-budget.

### M-15.2. Gate P0→P4

| Gate | Wymaganie | Metoda walidacji | Dowód wynikowy |
|---|---|---|---|
| `M-G0` | Wszystkie 14 stron PDF rozliczone | per-page requirements index + source MD | manifest coverage |
| `M-G1` | Brak fałszywych dowodów | adversarial proof term corpus, property tests | kernel rejection logs |
| `M-G2` | Minimalny fragment SMT sound | proof logs niezależnie sprawdzone | proof bundles |
| `M-G3` | Wszystkie operacje liczbowe typowane | fuzz DType/Shape/Unit, overflow | typecheck report |
| `M-G4` | Certified numerical operations | interval rounding, residual bounds | certification vectors |
| `M-G5` | Statystyka nie promuje się do proof | status machine tests | negative suite |
| `M-G7` | Zmiany modelu/aksjomatów invalidują dowody | mutation tests | immutable ledger records |
| `M-G8` | Dowody złożone mają jawne założenia | proof transparency / no implicit oracle | audited assumption manifest |
| `M-G9` | Niezależność od własnościowego ImandraX | SBOM/license scan; no copied implementation | IP compliance report |
| `M-G10` | E2E IMANDRAX: mTLS/HA/retry/PQC policy | true two-host scenarios po wdrożeniu | external evidence |
| `M-G11` | E2E Aetheris: real NEF and GPU | real output, measured color, exact hashes | visual and numeric report |

Wszystkie te bramki są **przewidziane, niezaliczone**. Każde „PASS” wymaga logu z konkretnej wersji kodu, testu i danych.

## M-16. Poziomy dostępności matematycznych kompetencji

| Poziom | Przykłady | Implementacyjny status |
|---|---|---|
| `P0/Kernel` | FOL subset, equality, propositional, exact integers/rationals, finite types, cert parser, SAT proof checker | REQUIREMENT |
| `P1/Formal` | SMT QF-LIA/LRA, bitvectors, BMC, induction, graph reachability, region partition | REQUIREMENT |
| `P2/Certified Numeric` | interval arithmetic, matrices, SVD residuals, numerical analysis, IEEE FP | REQUIREMENT |
| `P3/Prob/ML` | finite probability, Bayes, HMM, Kalman, ML shape/backprop contracts, basic LP/QP | REQUIREMENT |
| `P4/Research` | higher-order math, measure-theoretic probability, nonlinear problems, general NN verification, open conjectures | RESEARCH / UNKNOWN |

**Warunek ukończenia specyfikacji:** wszystkie wymienione zagadnienia z PDF mają ścieżkę wdrożenia i walidacji, bez fikcyjnych obietnic, że problem o nieograniczonej złożoności obliczeniowej staje się decydowalny przez marketingowo silniejszy komputer.

## M-17. Źródła i klasyfikacja pochodzenia

- **Załącznik użytkownika:** `Rozumowanie Matematyczne.pdf` (14 stron); dostarcza zakres pojęć, nie dowody poprawności. Rozmieszczenie tematów zachowano w mapie `04_*` i oryginalnej transkrypcji `05_*`.
- **Oficjalna technologia porównawcza:** https://imandrax.dev/docs/ , https://imandrax.dev/docs/region-decomposition/ i https://imandrax.dev/docs/verification/ (weryfikacja, refutacja, dekompozycja regionów, indukcja, taktyki, model checking); wykorzystane jako benchmark funkcji, **bez kopiowania** implementacji lub składni licencjonowanej.
- **SMT-LIB:** https://smt-lib.org/language.shtml — standard języka solverów, profil zgodności ma wskazywać dokładną wersję (np. 2.7) i fragment.
- **Wymagania stworzone dla IMANDRAX Ω ENGINE:** typy, API, certyfikaty, proof kernel, status machine, matryce testów oraz integracje są autorskim projektem, którego wykonanie należy osobno wykazać.


# 31. Zasada kompletności i uczciwy status

W całym wydaniu v1.1 wszystkie moduły, struktury, testy, API i certyfikaty są wymaganiami projektowymi. Do stwierdzenia ukończenia potrzebne są rzeczywisty kod jądra dowodowego, kompilowalny DSL, proof-producing solver lub sprawdzalny translacyjny certyfikat, testy adversarial, testy numeryczne z directed rounding, testy matematyczne z dołączonym PDF, a następnie testy sieciowe/E2E na docelowej infrastrukturze. Brak formalnego dowodu, który weryfikator potrafi sprawdzić, powoduje UNKNOWN/CONDITIONAL, nie PROVED. 