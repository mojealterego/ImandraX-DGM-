# Roadmap — ImandraX × DGM × RSI Ω

| Etap | Wymaganie | Stan i dowód |
|---|---|---|
| 0.01 | Repozytorium docelowe i publiczny kod referencyjny | PR #1 scalony 2026-10-29; kolejna wersja wyłącznie przez PR |
| 0.02 | 701 publicznych rekordów + klasyfikacja; 3 prywatne wyłączone | Lokalna walidacja CSV/TSV; nie audyt kodu |
| 0.03 | Read-only KnowledgeIndex + provenance | Lokalny test na fixture; 19 114 rekordów tylko w osobnym artefakcie |
| 0.04 | ResearchGate, budżety, whitelist ścieżek | Lokalny test PASS |
| 0.05 | RSIInbox — cykliczne rejestrowanie propozycji bez mutacji kodu | Lokalny test PASS; wymaga uruchomionego procesu |
| 0.06 | Cztery podpisane suites i kryptograficzne zatwierdzenie użytkownika | Lokalny test PASS; bez zewnętrznego serwera authority |
| 0.07 | Archiwum zatwierdzonych generacji DGM, selekcja rodziców | Lokalny test PASS; bez uruchamiania kandydatów |
| 0.08 | Pełna integracja proposerów DGM i RSI z LLM oraz tworzenie patchy | NOT IMPLEMENTED |
| 0.09 | Weryfikator rzeczywistego SHA-256 patcha i stanu źródłowego | NOT IMPLEMENTED |
| 0.10 | Izolowany wykonawca Firecracker no-net z atestacją | NOT IMPLEMENTED |
| 0.11 | Zewnętrzny immutable ledger, signer i policy service | NOT IMPLEMENTED |
| 0.12 | Lean: izolowane toolchains 4.34/4.35/4.36, build + kernel check | NOT RUN |
| 0.13 | MuJoCo / Physics-IQ E2E, wyniki transferowe, statystyka RSI | NOT RUN |
| 0.14 | Security negative E2E, fuzz, SBOM, licencje 704 repozytoriów | NOT RUN |
| 0.15 | Ochrona `main` przed usunięciem i force push, bez wymogu PR | NEEDS REPOSITORY OWNER CONFIGURATION |
| 0.16 | Produkcyjne release/canary/rollback wyłącznie za zgodą użytkownika | NOT IMPLEMENTED |

**Zasada:** nie oznaczać żadnej bramki produkcyjnej jako PASS na podstawie lokalnego pytest. Oryginalne ImandraX G01–G20 i DGM R0–R14 pozostają osobnymi wymaganiami. Zmiany polecone przez właściciela: wyłącznie `main`, bez przymusowego PR i bez dodatkowego recenzenta. RSI nie ma prawa do samodzielnego zastosowania kodu lub zatwierdzenia wydania.

## Postęp v0.3 — tylko stan potwierdzony kodem i lokalnymi testami

| Etap | Dostarczony element | Stan |
|---|---|---|
| 0.17 | OpenAlex metadata research i HTTPS allowlisted LLM | IMPLEMENTED, live credentials NOT CONFIGURED |
| 0.18 | Samodzielne generowanie jednego pliku solvera przez LLM | IMPLEMENTED, live generation NOT RUN |
| 0.19 | Weryfikacja realnego patch SHA i source baseline SHA | IMPLEMENTED, end-to-end signature binding PENDING |
| 0.20 | Docker sandbox no-net z limitami i trusted worker | IMPLEMENTED, real Docker CI verification PENDING |
| 0.21 | DGM quality/novelty ranking i 2 warianty na cykl | IMPLEMENTED, trwała ewolucja wielopokoleniowa PENDING |
| 0.22 | Harmonogram 6h z artefaktami, bez uprawnień zapisu | WORKFLOW PREPARED, DISABLED UNTIL OWNER ACTIVATION |
| 0.23 | HTTPS TLS 1.3 approval authority reference server | IMPLEMENTED, EXTERNAL DEPLOYMENT PENDING |
| 0.24 | Lean kernel build + manualne fork matrix | WORKFLOW PREPARED, CI PENDING |
| 0.25 | MuJoCo CPU smoke real runtime | WORKFLOW PREPARED, CI PENDING |
| 0.26 | GitHub main Ruleset i wymagany CODEOWNERS review | OWNER ACTION REQUIRED, NOT SET |
| 0.27 | Firecracker microVM, WORM, external attestation, hosted 24/7 | NOT IMPLEMENTED |

## Zunifikowana realizacja v0.4 — 2026-10-29, bezpośrednio w `main`

| Etap | Element | Stan |
|---|---|---|
| 0.28 | Zachowanie pełnych blueprintów ImandraX v1.3 i DGM–RSI v1.0 w jednym repozytorium | DONE: `docs/blueprints/` |
| 0.29 | Jeden kontrakt `IntegratedEngine` dla wiedzy, matematyki, DGM i RSI | LOCAL_TEST_PASS |
| 0.30 | Weryfikacja SHA artefaktów i source drift przed `PROPOSED` | LOCAL_TEST_PASS |
| 0.31 | Automatyczne przekazanie źródeł matematycznych do proposera | LOCAL_TEST_PASS |
| 0.32 | Ukrycie wyników heldout przed kolejnymi promptami LLM | LOCAL_TEST_PASS |
| 0.33 | CLI `imandrax-dgm math/evolve` i 63-klasowy bootstrap MSC2020 | LOCAL_TEST_PASS |
| 0.34 | Publiczny research-watch OpenAlex co 6 godzin | WORKFLOW CONFIGURED; LIVE RUN TO VERIFY |
| 0.35 | RSI propozycje kodu co 6 godzin | CONFIGURATION REQUIRED: API key, vars, enable |
| 0.36 | Pełne biblioteki mathlib4/Batteries/Iris/MIL, checkery i wszystkie 6006 dziedzin | NOT IMPLEMENTED |
| 0.37 | Produkcyjne microVM, signer, multi-host, full 704 source audit | NOT IMPLEMENTED |
| 0.38 | Egzekwowany Ruleset main i zewnętrzny podpisujący serwer | NOT CONFIGURED |

Poprzednie wpisy roadmap zachowano jako historię v0.2/v0.3. Wymagania odrębnego PR dotyczą **propozycji generowanych przez autonomiczny RSI**, a nie bezpośrednich zmian kodu zleconych i autoryzowanych przez właściciela w `main`.

## Postęp v0.5 — źródłowa integracja + rzeczywiste wielopokoleniowe badania

| Etap | Dostarczony element | Weryfikacja / stan |
|---|---|---|
| 0.39 | MSC2020: 6006 szczegółowych kodów i stron źródłowych w repo | CSV + deterministyczny SQLite FTS5 + test 6006; SOURCE_INDEXED_ONLY |
| 0.40 | DGM: trwałe badawcze drzewo wariantów z SHA, depth, parent i selekcją | `research_archive.py`, testy RED→GREEN; RESEARCH_ONLY |
| 0.41 | DGM: rodzic z poprzedniej generacji w kolejnym promptowaniu RSI | `generator.py`, `cycle.py`; testy wielopokoleniowe; UNATTESTED |
| 0.42 | Trwały stan pomiędzy okresowymi GitHub Actions | `actions/cache` research-only; zależy od retencji i aktywacji RSI |
| 0.43 | Ciągły proces RSI na dedykowanym hoście | `imandrax-daemon` + systemd template; LOCAL_TEST_PASS, NOT DEPLOYED |
| 0.44 | Lean: nowe kernel-checkable twierdzenia o arytmetyce | CI PASS [https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920434911](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920434911) |
| 0.45 | Cztery forki Lean — automatyczna macierz zgodności | 4/4 CI PASS [https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920435010](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920435010); mathlib4 target `Mathlib.Algebra.Group.Basic`, nie cały mathlib |
| 0.46 | Serwer zatwierdzania na osobnym hoście | Compose + TLS 1.3 + secret files; LOCAL_TEST_PASS, HOST NOT DEPLOYED |
| 0.47 | Rzeczywisty pełny checker dowolnych twierdzeń, 6006 formalizacji | NOT IMPLEMENTED |
| 0.48 | Firecracker/microVM z atestacją, zewnętrzny WORM/KMS/HSM | NOT IMPLEMENTED |
| 0.49 | 704 repozytoria: pełny kod, licencje, SBOM, build i testy | NOT IMPLEMENTED; 701 PUBLIC METADATA ONLY |
| 0.50 | Ruleset `main` wymagający właściciela + niezależny release applier | NOT CONFIGURED / NOT IMPLEMENTED |

Wpisy historyczne 0.08–0.16 i 0.27–0.38 pozostają źródłową historią. Żadna nowa implementacja nie nadaje RSI prawa do zmiany `main` bez użytkownika. Formalizacja matematyki jest procesem otwartym, nie da się uczciwie uznać wszystkich dziedzin za udowodnione przez samą obecność taksonomii.

## Etap 0.51–0.56: formalna kontrola twierdzeń — v0.6

| Etap | Implementacja | Warunek zakończenia |
|---|---|---|
| 0.51 | Pełny cel `Mathlib` z przypiętym SHA | `lake build Mathlib` w GitHub Actions, artefakty runu; **NOT VERIFIED przed CI** |
| 0.52 | Niezależne jądra dla własnych dowodów | `lake check --paranoid` PASS, nie tylko `lake build`; **NOT VERIFIED przed CI** |
| 0.53 | Własny projekt Mathlib i 9 twierdzeń | `lake build ImandraXMathlib` + checker; **NOT VERIFIED przed CI** |
| 0.54 | Związanie 6006 kodów MSC2020 z nazwanymi twierdzeniami | Walidacja źródeł PASS, bez fałszywego statusu 6006 dowodów |
| 0.55 | Rejestr dowodów z Ed25519 i source SHA | Testy negatywne, zewnętrzny signer; **lokalne testy nie są atestacją** |
| 0.56 | Pełne sprawdzenie każdego modułu wszystkich czterech bibliotek niezależnymi jądrami | **NOT DONE**; wymaga dużej pamięci, eksportów i kompletnego audytu, osobne toolchains |

Uwaga: `mathlib4` jako jedna biblioteka formalizuje ogromną część matematyki, ale nie wszystkie znane twierdzenia, a tym bardziej nie nierozwiązane problemy. Żadne narzędzie nie może automatycznie nadać statusu rozwiązania problemom milenijnym.

**Korekta weryfikacji v0.6:** `proofs` miało wcześniej brak `defaultTargets` — `lean-action` wykonywał `Nothing to build`. Zostało naprawione; stare sukcesy nie stanowią dowodu kompilacji tych modułów. Rzeczywista weryfikacja od nowego przebiegu CI.

**CI v0.6 — obserwacja:** `lake build Mathlib` wykonał **18 183 zadania i zakończył się sukcesem** (run 40924696557), natomiast `leanchecker Mathlib` zakończył się sygnałem 139 na standardowym runnerze. To **nie** jest PASS niezależnego sprawdzenia całej biblioteki. Następny workflow sprawdza osobny ograniczony moduł, a pełny replay wymaga dalszej diagnostyki i/lub hosta o większej pamięci. Nowy workspace `proofs_mathlib` miał problem startowy z brakującym `lake-manifest.json`; konfiguracja instaluje teraz Lean z istniejącego projektu `proofs`, następnie wykonuje `lake update` w nowym workspace.

| 0.57 | Jedno API `IntegratedEngine.math` dla formalnych deklaracji | `FORMAL_PROOF_STATUS` + `FormalEvidenceRegistry`, testy fail-closed; lokalnie PASS, atestacje zewnętrzne nadal wymagane |

**v0.6 GitHub CI:** `mathlib-full-build` PASS i `imandrax-mathlib-proofs` PASS w [40926332569](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40926332569). `lake check --paranoid` na eksportach: **NOT PASSED**, najpierw ograniczenia `bubblewrap`, potem błędny katalog narzędzi w Docker; poprawka w toku.

## OMEGA Unified APEX v0.7 — integracja kolejnych silników po zamknięciu istniejących bramek

| Etap | Kontrakt/element | Stan |
|---|---|---|
| 0.70 | Wspólny rejestr silników i wersjonowane manifesty | IMPLEMENTED / CI PENDING |
| 0.71 | DAG zależności silników, wykrywanie cykli, jawne wiązanie portów | IMPLEMENTED / CI PENDING |
| 0.72 | Stabilny identyfikator instancji, SQLite state machine, replay audit | IMPLEMENTED / CI PENDING |
| 0.73 | Podpis Ed25519 zmiany manifestu z przypiętym kluczem właściciela | IMPLEMENTED / CI PENDING |
| 0.74 | Bounded APEX Flow, fail-closed capability dispatch, denied mutation/release | IMPLEMENTED / CI PENDING |
| 0.75 | Dostęp do istniejącego IntegratedEngine przez porty ImandraX/DGM | CODE COMPLETE / REAL CI PENDING |
| 0.76 | Produkcyjny WORM/HSM i osobna policy authority z atestacją | NOT DEPLOYED |
| 0.77 | Ruleset ochrony main + wymagany podpis właściciela dla przyszłych migracji | MAIN RULESET NOT CONFIGURED |
| 0.78 | Trwała osobista pamięć z retencją i usuwaniem danych | NOT IMPLEMENTED; wymaga zgody użytkownika |
| 0.79 | Dodatkowe silniki, adaptery i podpisane migracje epok | BLOCKED UNTIL CURRENT ENGINE RELEASE GATES PASS |

Lokalny ApexAudit z łańcuchem hash nie jest WORM. ApexRuntime nie może autoryzować zmian repozytorium. Nie nazywać systemu świadomym cyfrowym bytem na podstawie implementacji kontraktów.

## Etap 0.80–0.83: portfolio due diligence v0.8

| Etap | Zakres | Stan |
|---|---|---|
| 0.80 | Katalog 701 publicznych repozytoriów i klasyfikacja P0–P4 | IMPLEMENTED EARLIER / METADATA ONLY |
| 0.81 | Evidence 18 README i 15 LICENSE z blob SHA | ROOT FILES INSPECTED / NOT CODE AUDIT |
| 0.82 | `PortfolioAudit`, fail-closed, testy negatywne i CLI `portfolio` | CI PASS 143/143, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40975311219 |
| 0.83 | Pełny audyt kodu, SBOM, licencje zależności, reprodukowalne testy, podpisane epoki | NOT IMPLEMENTED / BLOCKED BY 0.76–0.79 |

Zapis evidence nie przyznaje uprawnień do wykonania kodu, montażu portów ani zmian generowanych przez RSI. Dokumentacja: `docs/PORTFOLIO_DUE_DILIGENCE_v0.8.md`.

## Etap 0.90–0.98 — OMEGA Cognitive Stack v0.9

| Etap | Zakres | Stan |
|---|---|---|
| 0.90 | Bitemporal store, append-only history, as-of time, optimistic concurrency | IMPLEMENTED / CI PASS 170/170 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40980910805) |
| 0.91 | Bitemporal graph, scoped edges, episodic/semantic/procedural/working/general tags | IMPLEMENTED / CI PASS 170/170 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40980910805); AUTHN/RBAC NOT IMPLEMENTED |
| 0.92 | Point-in-time clone and local integrity verification | IMPLEMENTED / CI PASS 170/170 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40980910805); NOT EXTERNAL BACKUP |
| 0.93 | CoALA cognitive cycle, correction/reflexion, deterministic summary | IMPLEMENTED / CI PASS 170/170 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40980910805); NO LLM INFERENCE |
| 0.94 | Graph of Thoughts DAG and offline R2-inspired bounded router | IMPLEMENTED / CI PASS 170/170 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40980910805); NO RL TRAINING |
| 0.95 | Digital genotype, bounded mutation/fixed fitness | IMPLEMENTED / CI PASS 170/170 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40980910805); NO CODE APPLICATION |
| 0.96 | Source registration of awesome-jepa and R2-Reasoner | READ-ONLY REFERENCES; NOT MODEL INTEGRATION |
| 0.97 | JEPA inference, holographic memory, Shimi Index, vector GraphRAG | NOT IMPLEMENTED / SPECIFICATION AND MODELS REQUIRED |
| 0.98 | Signed APEX capability-epoch migration, production authority, multi-tenant isolation | NOT IMPLEMENTED / OWNER-SIGNATURE AND INFRASTRUCTURE REQUIRED |

Nie zmieniono `core_manifests` i jego digestu: istniejąca tożsamość APEX pozostaje nienaruszona. Pełne szczegóły `docs/COGNITIVE_STACK_v0.9.md`.

## OMEGA Cognitive Workflows v1.0 — nowy zakres

| Etap | Przedmiot | Stan |
|---|---|---|
| 1.00 | Tree-of-Thoughts bounded beam + Graph-of-Thoughts existing | IMPLEMENTED; CI PASS 188/188 tests, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574 |
| 1.01 | ReWOO DAG, ontologia i readonly tool dispatch | IMPLEMENTED; CI PASS 188/188 tests, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574 |
| 1.02 | Multi-hop evidence links, anti-false-bridge | IMPLEMENTED; CI PASS 188/188 tests, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574 |
| 1.03 | Critique/refine, retrospection, procedural memory contracts | IMPLEMENTED RESEARCH ONLY; CI PASS 188/188 tests, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574 |
| 1.04 | Durable event queue, lease/idempotency/retry/deadletter | IMPLEMENTED LOCAL; CI PASS 188/188 tests, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574 |
| 1.05 | Async verification of bounded hypotheses in waiting periods | IMPLEMENTED ON-DEMAND; NO 24/7 DAEMON |
| 1.06 | Episodic-to-semantic reference synthesis | IMPLEMENTED; NOT SEMANTIC LEARNING |
| 1.07 | Cascaded offline inference routing (no model execution) | IMPLEMENTED; CI PASS 188/188 tests, 5/5 jobs: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574 |
| 1.08 | 701 inventory multimedia/game/model triage, 12 README, 8 root LICENSE | METADATA AND ROOT FILES ONLY; CODE AUDIT NOT DONE |
| 1.09 | World model fork from Google / Genie source identification | NOT VERIFIED; NO IMPORT |
| 1.10 | Unattended integration, owner-signed APEX migration, actual models & production HA | BLOCKED; NO OWNER SIGNATURE / ATTESTATION |

Nie zmieniono podpisywanego zestawu manifestów APEX. `readme/LICENSE` to nie pełna zgodność licencji, szczególnie dla BSL-1.1, AGPL-3.0 i LTX. Szczegóły: `docs/COGNITIVE_WORKFLOWS_v1.0.md`.

**v1.0 CI evidence:** `203c17d17d7451d5cdbce6b38ef31d42451a5b06` / [run 40983359574](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40983359574): 188 Python tests PASS, 5/5 CI jobs PASS. Nie potwierdza produkcyjnych bramek 1.09–1.10.

## Domykanie krytycznych bramek v1.1

| Etap | Rezultat | Stan |
|---|---|---|
| 1.11 | Online SQLite backup pamięci i manifest SHA-256 | IMPLEMENTED; CI PASS 196/196 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40987408743) |
| 1.12 | Weryfikacja podpisu Ed25519 właściciela i powiązanie z tożsamością | IMPLEMENTED; CI PASS 196/196 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40987408743); OFFLINE SIGNER REQUIRED |
| 1.13 | Anti-rollback z zewnętrznym high-watermark | IMPLEMENTED; CI PASS 196/196 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40987408743); EXTERNAL TRUST ROOT REQUIRED |
| 1.14 | Odzyskiwanie podpisanej kopii bez nadpisywania live state | IMPLEMENTED; CI PASS 196/196 tests, 5/5 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40987408743) |
| 1.15 | Zewnętrzny WORM/KMS/HSM/zaszyfrowane backupy/testy multi-host | NOT DEPLOYED / PRODUCTION BLOCKER |
| 1.16 | Ruleset GitHub main; właścicielski podpis wydania RSI (osobna bramka) | NOT CONFIGURED; repository rulesets API returned zero on 2026-10-30 |

Podpis snapshotu nie jest podpisem aprobaty kodu i nie może zastąpić podpisanego zatwierdzenia RSI.

**v1.1 weryfikacja:** `eb9f3c248a831b39e1fe17683a3915fe61ef4c56` (5/5 jobs, 196/196 testów): https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40987408743. Nie jest to dowód wykonania produkcyjnych etapów 1.15–1.16, ani podpis właściciela.

| 1.17 | Wheel/sdist, kontrola Name/Version, ścieżek archiwów, SHA-256 | IMPLEMENTED; CI PASS 201/201 tests, 6/6 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40988032432) |
| 1.18 | Czysty venv: instalacja wheel i rzeczywisty CLI inventory na 701 rekordach | IMPLEMENTED; CI PASS 201/201 tests, 6/6 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40988032432); REQUIRES EXTERNAL --root RESOURCES |
| 1.19 | Reproducible builds (bit-identical), podpisane provenance/SBOM zależności, artifact signing | NOT IMPLEMENTED / RELEASE BLOCKER |

Zapis `build_evidence.json` ma `release_authorized=false`; **nie zastępuje** niezależnych podpisów, Ruleset ani zgody właściciela.

**v1.1 release-artifact evidence (2026-10-30):** 201/201 Python tests, 6/6 jobs, real wheel/sdist built and clean-venv wheel CLI smoke PASS. Workflow: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40988032432. Downloadable unsigned artifacts retained by GitHub Actions (`omega-v1.1-unsigned-package-evidence`). This is not SBOM/compliance certification, reproducible-build proof, or a signed production release. Existing external-host and GitHub ruleset gates remain unresolved.

## OMEGA-PANOPTICON — domykanie bramek zewnętrznych v1.2 (2026-10-30)

| Etap | Element | Zweryfikowany status |
|---|---|---|
| 1.20 | Red Hat OpenShift Sandbox, staging-only Deployment, Service, NetworkPolicy, PVC; bez sekretnych danych | SPECIFIED + REPO IMPLEMENTED; CI PASS 209/209, 7/7 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40989888953); NOT EXTERNALLY DEPLOYED; NOT DEPLOYED |
| 1.21 | GitHub main Ruleset tylko non-fast-forward i deletion; bez PR/recenzenta | PROPOSED ONLY; LIVE API: [] (UNPROTECTED); OWNER ACTION REQUIRED |
| 1.22 | Seven independent Ed25519 release gate receipts bound to commit & artifact digest | IMPLEMENTED; CI PASS 209/209, 7/7 jobs (https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40989888953); NOT EXTERNALLY DEPLOYED; NO EXTERNAL SIGNERS |
| 1.23 | Signed HSM/KMS, WORM and independent authority host | NOT DEPLOYED; NO EXTERNAL ENDPOINT / KEY / STORAGE EVIDENCE |
| 1.24 | Physical multi-host failure injection and recovery with trusted independent logs | NOT EXECUTED; sandbox shared cluster NOT SUFFICIENT |
| 1.25 | Owner-signed production release, independently stored trust anchors and GitHub enforcement | BLOCKED; NO SELF APPROVAL |

Korekta 2026-10-30: usunięto niezamówiony wymóg niezależnego recenzenta PR, pull_request i required_status_checks z proponowanego ruleset. Obowiązuje `main` bez dodatkowych gałęzi. CI post-push ≠ skuteczny gate pre-push. Plik JSON nadal nie oznacza aktywnej ochrony GitHub. Details in `docs/INDEPENDENT_PRODUCTION_GATES_v1.2.md`.

**v1.2 in-repository CI evidence**: [run 40989888953](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40989888953), head `c5bb62b5425d1074b9d44602d450848d7878aca0`: 209 Python tests PASS, 7/7 CI jobs PASS; 8 tests of release signature gate and OpenShift policy pass. Prowadzi to do CI-VERIFIED TEMPLATE + OFFLINE GATE ONLY, **not** Red Hat deployment, active Ruleset, KMS/WORM or genuine multi-host disaster recovery.

| 1.26 | Reuse old OCAF Red Hat OpenShift connection for isolated ImandraX staging; source-pinned BuildConfig | BUILD SPEC PREPARED; LIVE EXECUTION PENDING; NO SECRET COPIES |

## v1.3 — odtwarzalna symulacja całego silnika

Dodano `imandrax-dgm simulate`, automatyczny indeks MSC, dwa cykle z trwałą
 genealogią, rzeczywistą ocenę arytmetyki, negatywnego kandydata i raport SHA-256.
Dostępne są jawne tryby: zamknięty zestaw funkcji referencyjnych oraz Docker
bez sieci z przypiętym obrazem. Generator pozostaje scenariuszem, nie LLM.
Naprawiono odnajdywanie Docker w `/usr/local/bin` i odczyt worker.py przy 0600.
Wyniki nie zamykają bramek formalnych ani produkcyjnych.
Instrukcja: [SIMULATION_ENGINE_v1.3](SIMULATION_ENGINE_v1.3.md).
