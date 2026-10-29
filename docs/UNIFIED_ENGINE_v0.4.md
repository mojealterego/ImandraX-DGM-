# ImandraX × DGM × RSI Ω — zintegrowany kontrakt systemowy v0.4

**Status:** implementacja badawcza części interfejsów i kontrolowanego cyklu; nie gotowy produkcyjny system samodoskonalenia.

## 1. Cel integracji

Jedna aplikacja/CLI, jeden rejestr kampanii, jeden schemat wyników, jedna historia propozycji. Trzy oddzielone granice zaufania: (A) matematyczna wiedza i weryfikacja, (B) generowanie i eksperymenty DGM/RSI, (C) niezależne zatwierdzanie. Połączenie produktu **nie** oznacza złączenia kluczy i uprawnień.

## 2. Schemat wywołania

`IntegratedEngine` (`src/imandrax_dgm/engine.py`) udostępnia:

1. `math(MathTask(kind='LOOKUP' | 'EXACT_COMPUTE' | 'FORMAL_THEOREM'))`: klasyfikuje dowód, zwraca dane źródłowe, wykonuje ograniczoną dokładną arytmetykę lub jawnie informuje o braku formalnej weryfikacji.
2. `evolve(campaign_id, root, base_commit, output, source_refs, cycle)`: wymaga prawdziwych referencji matematycznych, przekazuje je jako **niezaufane dane** do proposera, wykonuje ograniczony cykl DGM, waliduje artefakty SHA-256, rejestruje propozycję w `RSIReviewStore` oraz append-only journal.
3. `register_review_artifacts(...)`: sprawdza ścisłe powiązanie z SHA commita, SHA bazowego źródła, SHA patcha, wynikami testów i wybranym kandydatem; nie nadaje statusu `APPROVED`.
4. `archive_approved(...)`: wymaga nadal ważnego, podpisanego upoważnienia użytkownika i czterech niezależnych atestacji testowych.

## 3. Typowanie twierdzeń

| Klasa | Dopuszczalne określenie | Zakaz |
|---|---|---|
| Indeks MSC/encyklopedia | `SOURCE_INDEXED` | Nie oznaczać jako udowodnione |
| Arytmetyka deterministyczna (gcd, mod_pow, primality ≤1e6) | `COMPUTED_EXACT` w podanym zakresie | Nie mylić z formalnym dowodem Lean |
| Twierdzenie bez checkera | `PROOF_NOT_CHECKED` | Nie oznaczać jako `PROVED_STRICT` |
| MuJoCo/JAX | `EMPIRICAL_BENCHMARK` po prawdziwym teście | Nie wyciągać twierdzeń o świecie fizycznym z samej symulacji |
| Lokalna ocena DGM | `EVALUATED_UNATTESTED` | Nie używać jako dowodu release |
| RSI | `PROPOSED`, ewentualnie `APPROVED` po podpisie | Nie wykonywać auto-apply/merge/deploy |

## 4. Źródła i zakres matematyczny

- `MSC2020` — 63 klasy, 534 podklasy, 6006 kodów szczegółowych.
- Indeks pełny — 19 114 rekordów (MSC2020 official 6603, encyclopedia 6006, MSC2010 6198, MATH-307 307), dostępny jako opcjonalna lokalna baza.
- `Rozumowanie Matematyczne.pdf` — 239 wymagań z 14 stron, pełne śledzenie w `docs/blueprints/IMANDRAX_MATH_PDF_TRACEABILITY_14_PAGES.md`.
- 16 repozytoriów referencyjnych: mathlib4, batteries, iris-lean, mathematics_in_lean, mujoco, optax, mujoco_menagerie, science-skills, dm_control, regress-lm, representations4d, Awesome-Quantum-Computing-Platform, mathematics_conjectures, alphageometry, mathematics_dataset, 3d-shapes.
- 704 repozytoria właściciela: 701 publicznych rekordów w `data/repositories_public_701.tsv`, 3 prywatne bez publikowania nazw; przegląd kodu **nie jest** pełny.

**Niezależność matematycznego checkera:** kod propozycji RSI nie może być uruchamiany w zaufanym procesie sprawdzania dowodów. Formalny dowód wymaga niezależnego, przypiętego Lean kernel, jawnego zestawu aksjomatów i identyfikatorów źródeł.

## 5. DGM + RSI — realny przebieg

1. Użytkownik lub harmonogram otwiera kampanię, wskazuje źródła MSC i bazowy SHA commita.
2. Retrieval OpenAlex zbiera publiczne metadane; źródła są nieufne, cytowane i ograniczone budżetem.
3. Proposer LLM generuje jedynie zmieniony `research/solver.py` i hipotezę; inne pliki odrzuca `ResearchGate`.
4. `DockerSandbox` uruchamia kandydatów bez sieci, z read-only FS, ograniczeniami zasobów i bez kluczy.
5. `ResearchCycle` ocenia regresję/heldout, zachowuje wszystkie wyniki, ale **nie podaje wyniku heldout z powrotem do LLM**, aby ograniczyć przeciek i przeuczenie.
6. `IntegratedEngine` waliduje hash każdego artefaktu, zgodność patcha i bazowego źródła, selekcję kandydata i matematyczne referencje.
7. `RSIReviewStore` rejestruje `PROPOSED`; niezależne podpisane suites: STATIC_CHECK, REGRESSION, SECURITY, HELDOUT.
8. Właściciel osobiście podpisuje decyzję Ed25519 dla dokładnego manifestu, polityki, bazowego źródła i patcha. Klucz prywatny nigdy nie trafia do LLM/CI.
9. `ApprovedArchive` może dodać zatwierdzony wariant do puli rodziców DGM. Nie daje to prawa do deploymentu.

## 6. Ciągłe badania

GitHub Actions `rsi-research-cycle.yml` ma harmonogram co sześć godzin. Job `public-research-watch` działa bez sekretów, pobiera metadane OpenAlex i archiwizuje raport. Job `bounded-rsi-proposer` jest **wyłączony do chwili ustawienia `RSI_CYCLE_ENABLED=true` i sekretów LLM**. Każdy run jest efemeryczny; nie jest to stały proces 24/7. Nie należy opisywać go jako natywnego ChatGPT Deep Research.

## 7. Niezrealizowane bramki

- Produkcyjny niezależny checker Lean dla dowolnych twierdzeń, SMT/geometry proof replay.
- Pełne 4 izolowane toolchain Lean z mathlib4, batteries, iris-lean, mathematics_in_lean.
- Zaawansowane JAX/Optax/MuJoCo/dm_control i testy transferowe; CI ma tylko ograniczony smoke.
- Atakoodporne Firecracker/microVM, atestacja hosta, KMS/HSM, niezmienny zewnętrzny ledger.
- Pełna ewolucja wielopokoleniowa, zmiana własnego proposera z zachowaniem metryki przyszłych potomków.
- Ochrona GitHub `main` przez Ruleset wymagający recenzji właściciela dla zmian autonomicznych.
- Ukończona walidacja semantyczna 6006 haseł i audyt kodu 704 repozytoriów.

**Priorytet:** dobudowywać kolejne silniki jako adaptery w tym samym repozytorium i kontrakcie, bez dopisywania OCAF lub Aetheris i bez automatycznego scalania zmian generowanych przez RSI.