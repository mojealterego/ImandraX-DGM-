# IMANDRAX Ω — audyt 16 repozytoriów i plan integracji wiedzy

**Wersja:** 1.3-design | **Data przeglądu:** 2026-10-29 | **Zakres:** tylko samodzielny silnik IMANDRAX Ω, bez OCAF i Aetheris.

**Metoda:** zweryfikowano przez połączenie GitHub metadane 16 publicznych repozytoriów `mojealterego/*`, ich gałęzie domyślne, bieżące identyfikatory commitów, główne katalogi, pliki README i root LICENSE. Sprawdzono także kluczowe katalogi modułów. **Nie pobrano wszystkich plików źródłowych, wag, modeli ani datasetów; nie uruchomiono ich testów.** Dlatego status repozytoriów: `SOURCE_DISCOVERED_AND_STRUCTURALLY_REVIEWED`, a nie `FULLY_INGESTED` lub `INTEGRATED`.

## 1. Rejestr źródeł z niezmiennymi identyfikatorami

| Nr | Repozytorium | Gałąź | SHA commit | Licencja / szczególna uwaga |
|---:|---|---|---|---|
| 01 | [mathlib4](https://github.com/mojealterego/mathlib4) | master | `d0207795ac79006da92d98544e1ce915ae386160` | Apache-2.0 |
| 02 | [batteries](https://github.com/mojealterego/batteries) | main | `6d971e7e6b3f7d0a501c5418815aa9022edd3499` | Apache-2.0 |
| 03 | [iris-lean](https://github.com/mojealterego/iris-lean) | master | `fb21a8af4727bd42190072a5ed2836cbe9fb844e` | Apache-2.0 |
| 04 | [mathematics_in_lean](https://github.com/mojealterego/mathematics_in_lean) | master | `cff01285931648054c4fe6817baed0ccd45c0372` | Apache-2.0 |
| 05 | [mujoco](https://github.com/mojealterego/mujoco) | main | `e3c0953f9f2b5a00a30d01b58f715f5e36d9a07d` | Apache-2.0 |
| 06 | [optax](https://github.com/mojealterego/optax) | main | `9a1f892f52e28c18eec4d72b1001731cf20da532` | Apache-2.0 |
| 07 | [mujoco_menagerie](https://github.com/mojealterego/mujoco_menagerie) | main | `f3b6013629c7b94f8ee93fd977b161fa8350f9bc` | **Różne licencje per model i katalog; root LICENSE zawiera rozdzielne sekcje** |
| 08 | [science-skills](https://github.com/mojealterego/science-skills) | main | `4de6786171f1479026da5d3a00f110703c8ba35e` | Kod Apache-2.0; inne materiały CC BY 4.0; dodatkowe warunki per skill i zewnętrzne źródło |
| 09 | [dm_control](https://github.com/mojealterego/dm_control) | main | `3948bd0ab4a857dbb5989a1b8d20bac920551136` | Apache-2.0 |
| 10 | [regress-lm](https://github.com/mojealterego/regress-lm) | main | `76a386e13e4d3ef1254de06d9efaa4e05ae6d057` | Apache-2.0 |
| 11 | [representations4d](https://github.com/mojealterego/representations4d) | main | `d5bf6bad6a781bbfb5edb1ac98b53feb2a8dcf5d` | Apache-2.0 |
| 12 | [Awesome-Quantum-Computing-Platform](https://github.com/mojealterego/Awesome-Quantum-Computing-Platform) | main | `67e54c30eb130e6adfd7ad8876cbea6faa8eaba2` | MIT; **katalog linków, nie implementacja sprzętu kwantowego** |
| 13 | [mathematics_conjectures](https://github.com/mojealterego/mathematics_conjectures) | main | `8302f29101019434e5a0a25807a4e42cd9d96414` | Kod Apache-2.0; README deklaruje CC BY 4.0 dla danych/wag |
| 14 | [alphageometry](https://github.com/mojealterego/alphageometry) | main | `6777cb586cbb46beed28db12dc72c69770b68337` | Apache-2.0; repo **AlphaGeometry (2024), nie pełne AlphaGeometry2** |
| 15 | [mathematics_dataset](https://github.com/mojealterego/mathematics_dataset) | master | `427f45075f84b8b9774950196ad63867ca20ffb3` | Apache-2.0; generator danych szkolnych, zewnętrzne dane osobno |
| 16 | [3d-shapes](https://github.com/mojealterego/3d-shapes) | master | `de26b40d35330adc15816ccfaa516361f789d76b` | Apache-2.0; **480 000 obrazów w zewnętrznym HDF5**, nie w repo |

**Ważne:** licencje określono z plików LICENSE/README w repozytoriach. Ostateczny audyt musi sprawdzić również pliki per asset, per model, transitive dependencies i zasady dostawców zewnętrznych.

## 2. Szczegółowa macierz architektoniczna

### R01 — mathlib4: formalna biblioteka matematyczna Lean 4

Odczytane moduły główne: `Mathlib/Algebra`, `AlgebraicGeometry`, `AlgebraicTopology`, `Analysis`, `CategoryTheory`, `Combinatorics`, `Computability`, `Control`, `Dynamics`, `Geometry`, `GroupTheory`, `InformationTheory`, `LinearAlgebra`, `Logic`, `MeasureTheory`, `ModelTheory`, `NumberTheory`, `Probability`, `RepresentationTheory`, `SetTheory`, `Topology`, `Tactic` i pozostałe katalogi. **Cel:** `Ω-Lean Bridge` do wyszukiwania i importu twierdzeń, typecheckingu oraz kontroli aksjomatów. Kontrakt: indeks symboli `.lean`, namespace, typ, zależności, docstring, MSC primary/secondary, hash pliku i commit; kompilacja `lake build` w spójnym toolchain; jądro Lean zatwierdza dowód. **Zakaz:** `sorry`, `admit`, ukryte dodatkowe aksjomaty w ścieżce `PROVED_STRICT`.

### R02 — batteries: infrastruktura i taktyki Lean

Odczytane katalogi `Batteries/Classes`, `Control`, `Data`, `Lean`, `Linter`, `Logic`, `Tactic`, `Util`. **Cel:** narzędzia parsera, struktury danych, diagnostyka i taktyki. Kontrakt: wersja `lean-toolchain` i `lake-manifest` zgodna z mathlib4; test `lake test`, lint. **Ryzyko:** taktyka jest generatorem dowodu, nie niezależnym dowodem; ostateczne sprawdzenie w Lean kernel.

### R03 — iris-lean: logika separacyjna dla programów współbieżnych

Odczytane `Iris/Iris`, `IrisMath`, `IrisTest`, dokumentacja `proofmode`, `tactics`, `compatibility`. Repo opisuje MoSeL, IProp, HeapLang, invariants i later credits. **Cel:** dowody bezpieczeństwa pamięci, niezmienników współbieżności i własności zasobów. Kontrakt: odrębny model operacyjny programu, reguły separation logic, logiczna poprawność w Lean; rozdzielenie `Iris` i `IrisMath`. **Ryzyko:** twierdzenie o modelu HeapLang nie dowodzi automatycznie poprawności binarki Rust/C++.

### R04 — mathematics_in_lean: korpus dydaktyczny formalizacji

Katalogi `MIL/C01_Introduction` do `C13_Integration_and_Measure_Theory`, w tym logika, zbiory, liczby, struktury, grupy, pierścienie, algebra liniowa, topologia, rachunek różniczkowy, całkowanie. **Cel:** tutorial/evaluation/curriculum dla automatyzacji formalizacji. Kontrakt: rozdziel przykłady i rozwiązania `MIL_solutions`; niedozwolony leakage testów; metryki proof-completion, nie tylko poprawność tekstu.

### R05 — mujoco: fizyka układów dynamicznych i kontaktu

Odczytane `include`, `src`, `mjx`, `model`, `plugin`, `python`, `test`. **Cel:** cyfrowe laboratorium dla mechaniki, układów różniczkowych, kontaktu, stabilności, sterowania i identyfikacji parametrów. Kontrakt: stan, sterowanie, krok integracji, tolerancje solvera, jednostki SI, deterministyczny seed i jawna dyskretyzacja. **Nie jest to solver formalnych twierdzeń**: ślad symulacji ≠ dowód globalnego bezpieczeństwa rzeczywistego robota.

### R06 — optax: algorytmy optymalizacji różniczkowalnej

Odczytane `optax/_src`, `transforms`, `schedules`, `losses`, `projections`, `second_order`, `tree`, `experimental`, `contrib`. **Cel:** optymalizacja gradientowa i adaptacyjna, Lagrangian/constraints, uczenie polityk i modeli. Kontrakt: funkcja celu, gradient, dtype, seed, optimizer state, schemat aktualizacji, ograniczenia, checkpoint; dla deklaracji optymalności certyfikat primal-dual/convexity, jeśli dostępny. **Nie** utożsamiać poprawy funkcji celu z dowodem optimum globalnego.

### R07 — mujoco_menagerie: modele obiektów i robotów

Odczytano liczne katalogi robotów (`franka_emika_panda`, `franka_fr3`, `anybotics_anymal`, `unitree`, `boston_dynamics_spot` i inne), format MJCF, pliki scen, meshe i lokalne licencje. **Cel:** kontrolowane benchmarki dynamiki, identyfikacji, trajektorii i reachability. Kontrakt: identyfikator modelu + commit + hash XML + licencja katalogu + parametry fizyczne + test sanity. **Ryzyko:** różne warunki licencyjne i niejednolita wierność modeli.

### R08 — science-skills: naukowe narzędzia i workflow

Odczytano `skills/` z 40 katalogami, m.in. `alphafold_database_fetch_and_analyze`, `alphagenome`, `chembl_database`, `clinical_trials_database`, `clinvar_database`, `ensembl_database`, `literature_search_arxiv`, `openalex`, `pubmed_database`, `pdb_database`, `uniprot_database`, `pymol`. **Cel:** retrieval evidence i provenance w dziedzinach biologii, chemii i nauk stosowanych. Kontrakt: allowlista skill, zakres danych, źródło, timestamp, warunki API i licencji, cytowania, privacy, brak automatycznego wykonywania kodu z promptu. **Wynik badań** ≠ dowód matematyczny.

### R09 — dm_control: zadania kontrolne i środowiska RL

Odczytane `dm_control/suite`, `mujoco`, `mjcf`, `composer`, `locomotion`, `manipulation`, `viewer`, `rl`. **Cel:** benchmarki sterowania, optymalizacji polityk, system identification, robustness i multiagent control. Kontrakt: jawny `task_id`, `seed`, model, observation/action spec, reward, time-limit, trace. Uwaga README: pakiet nie obsługuje trybu `pip install -e` w typowym przepływie.

### R10 — regress-lm: regresja liczbowa z wejść tokenizowalnych

Odczytane `regress_lm/core.py`, `rlm.py`, `tokenizers.py`, `vocabs.py`, testy i `pytorch/`. **Cel:** heurystyki prognozujące czas solvera, koszt symulacji, wybór strategii i priorytetyzację dowodów. Kontrakt: skalowanie targetów, kalibracja niepewności, drift, OOD, metryki MAE/RMSE i pin modelu. **Predykcja nie jest certyfikatem poprawności.**

### R11 — representations4d: reprezentacje czasoprzestrzenne wizyjne

Odczytane `representations4d/genception`, `models`, `utils`, README o MAE, MooG, RVM, Omnivorous i GenCeption. **Cel:** obserwacje do geometrii i dynamiki, reprezentacja sceny 3D+czas, identyfikacja stanów symulowanych. Kontrakt: układ współrzędnych, jednostki, timestamp, niepewność, provenance. **Wizja 4D nie jest formalnym dowodem twierdzenia o czterowymiarowej geometrii.**

### R12 — Awesome-Quantum-Computing-Platform: katalog infrastruktury kwantowej

Root zawiera README i zasoby. **Cel:** metadane o SDK/QPU/symulatorach, kryteria wyboru backendu, provenance i dostępność. **To curated directory, a nie implementacja QPU, algorytmu ani gwarantowane aktualne ceny**. Wszelkie claimy o przewadze kwantowej muszą mieć niezależne benchmarki i model błędu.

### R13 — mathematics_conjectures: hipotezy wspomagane ML

Repo zawiera dwa notebooki: `knot_theory.ipynb`, `representation_theory.ipynb` towarzyszące publikacji o wspomaganiu intuicji matematycznej. **Cel:** `Ω-Conjecture Laboratory` — generowanie hipotez, filtrowanie przypadków, poszukiwanie kontrprzykładów i przekazywanie do formalizacji. **Zakaz:** `MODEL_PREDICTED` → `PROVED` bez certyfikatu.

### R14 — alphageometry: geometria syntetyczna i DDAR

Odczytane `dd.py`, `ddar.py`, `geometry.py`, `graph.py`, `numericals.py`, `beam_search.py`, `defs.txt`, `rules.txt`, `alphageometry.py`, testy. **Cel:** generowanie i sprawdzanie ścieżek rozumowania w geometrii olimpijskiej. Kontrakt: aksjomaty geometrii, model konstrukcji, degeneracje, sprawdzalny proof trace, translacja do Lean lub checker o zweryfikowanej semantyce. **Uwaga:** wskazane repo odwołuje się do AlphaGeometry2, ale nie jest pełną implementacją AlphaGeometry2.

### R15 — mathematics_dataset: generator zadań matematycznych

Odczytane `mathematics_dataset/modules`, `generate.py`, `generate_settings.py`, `sample`, `util`. **Cel:** automatyczne benchmarki arytmetyki, algebry, rachunku, porównań, pomiarów, liczb, wielomianów i prawdopodobieństwa. Kontrakt: generowanie z seed, rozdzielone train/dev/test, niezależny evaluator i zapobieganie kontaminacji. **Poziom szkolny** — nie reprezentuje całej matematyki MSC2020.

### R16 — 3d-shapes: zbiór syntetycznych obrazów 3D

README opisuje **480 000 obrazów 64×64×3** z sześcioma niezależnymi czynnikami: barwa podłogi, barwa ściany, barwa obiektu, skala, kształt i orientacja. Repo zawiera opis i notebook, nie pełny plik HDF5. **Cel:** eksperymenty disentanglement i identyfikowalności latentów; nie jest to formalna baza geometrii różniczkowej. Kontrakt: oddzielna licencja danych, kontrola pochodzenia i metryki OOD.

## 3. Bramy przed rzeczywistą integracją kodu

- `GH-01`: pobrać każdy commit **po SHA** i zapisać content manifest z hashami wszystkich używanych plików (nie HEAD).
- `GH-02`: sprawdzić licencje na poziomie plików, danych, modeli i assetów; dokumentować obowiązki attribution.
- `GH-03`: wykonać SBOM, skan zależności i statyczną analizę kodu; bez automatycznego uruchamiania `setup.py`, notebooków i skryptów z repo.
- `GH-04`: rozdzielić warstwy `PROOF`, `NUMERIC_CERT`, `SIMULATION`, `STATISTICS`, `HEURISTIC`, `DATASET`, `DIRECTORY`.
- `GH-05`: Lean toolchain/lake manifests dla mathlib4, batteries, Iris, MIL — spójny lockfile i odtwarzalna kompilacja.
- `GH-06`: testy interfejsów oraz izolacja procesów i danych; brak sieci w proof kernel.
- `GH-07`: test mutacji: uszkodzony proof term, błędna jednostka, niepoprawna granica numeryczna, niekompletna hipoteza, symulacja przedstawiona jako dowód — wszystkie mają być odrzucone.
- `GH-08`: dopiero po przejściu CI/E2E zmienić status z `SOURCE_DISCOVERED` na `INTEGRATED`; obecnie żaden z 16 nie ma tego statusu.