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