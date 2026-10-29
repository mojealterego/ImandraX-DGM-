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
| 0.15 | PR approval i egzekwowanie ruleset w GitHub | NEEDS REPOSITORY OWNER CONFIGURATION |
| 0.16 | Produkcyjne release/canary/rollback wyłącznie za zgodą użytkownika | NOT IMPLEMENTED |

**Zasada:** nie oznaczać żadnej bramki produkcyjnej jako PASS na podstawie lokalnego pytest. Oryginalne ImandraX G01–G20 i DGM R0–R14 pozostają osobnymi wymaganiami. Dalsze zmiany kodu: PR → przegląd → podpis użytkownika → testy → merge wykonany przez użytkownika.

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
