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