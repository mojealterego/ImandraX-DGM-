# ImandraX × DGM × RSI Ω — jeden silnik matematyczno-ewolucyjny

**Wersja kodu:** `0.7.0` • **Gałąź robocza i docelowa:** `main` • **Data integracji:** 2026-10-29  
**Stan:** `INTEGRATED_RESEARCH_PROTOTYPE_WITH_PERSISTENT_RESEARCH_GENEALOGY`; nie jest produkcyjnym proverem, autonomiczną AGI ani wdrożonym samodoskonalącym się serwerem.

## OMEGA Unified APEX v0.7 — warstwa ciągłości i integracji

Dostarczono ApexRuntime, ApexRegistry, ApexAudit, ApexFlow i wersjonowane kontrakty silników. To **jeden produkt** z odseparowanymi domenami zaufania: odczyt ImandraX, historia DGM oraz niewiązany domyślnie port RSI. Nowe silniki są wyłącznie opisem danych, dopóki zatwierdzony kod nie powiąże ich portów. Zmiana manifestu wymaga podpisu Ed25519 właściciela i stanu PAUSED. System nie ma w tej warstwie samodzielnego merge, self-approval ani deploy.

- Interfejs lokalny: `imandrax-apex --state-dir /ścieżka/poza/repo --root . status` oraz polecenia `start|pause|stop|verify|manifests|math|formal|history`.
- Nowe testy: `tests/test_apex_v07.py` oraz integracyjny `tests/test_apex_real_integration_v07.py`.
- Pełny kontrakt i blokady produkcyjne: [docs/OMEGA_UNIFIED_APEX_v0.7.md](docs/OMEGA_UNIFIED_APEX_v0.7.md).
- **Cyfrowy byt** jest nazwą celu architektonicznego: trwały identyfikator, audyt, ciągłość stanu, ograniczone badania; NIE jest deklaracją świadomości. Kolejne silniki pozostają odłożone do zakończenia obecnych bramek.


## Nowe w v0.5 — jeden silnik, nie trzy aplikacje

- **6006 rzeczywistych szczegółowych kodów MSC2020 w repozytorium** (`data/msc2020_6006_coverage.csv`); deterministyczny `build_msc_full_index.py` buduje wyszukiwalny indeks FTS5, a `IntegratedEngine` używa go do matematycznego ugruntowania propozycji. To klasyfikacja, **nie 6006 formalnych twierdzeń**.
- **Wielopokoleniowe badania DGM** (`ResearchArchive`): SQLite przechowuje źródła i metryki niezaufanych wariantów, parent SHA-256, bazowy commit i głębokość do 12; następnym rodzicem może zostać oceniony wariant z poprzedniego cyklu. Żaden wariant badawczy nie jest samoczynnie zatwierdzany ani stosowany w kodzie.
- **Pętla działająca jako proces** (`imandrax-daemon`): obsługa powtarzanych kampanii, trwałego stanu, limitu prób, zatrzymania po błędach i wykrywania zmian kodu bazowego. Do uruchomienia na dedykowanym hoście wymagane są konfiguracja i zgoda właściciela. W tym repo nie ma uruchomionej usługi 24/7.
- **Niezależna authority**: konfiguracja kontenera TLS 1.3 i sekretów plikowych w `deploy/authority/`; sprawdzane są rzeczywiste podpisy Ed25519. Konfiguracja nie oznacza wdrożenia serwera.
- **Lean**: dodatkowy moduł formalnej arytmetyki i CI; macierz czterech przypiętych repozytoriów uruchamia się po zmianach dowodów oraz tygodniowo. **Nie jest to pełna kompilacja wszystkich bibliotek ani formalizacja całej matematyki.**

Dokumentacja: [Unified Engine v0.5](docs/UNIFIED_ENGINE_v0.5.md), [Formalization coverage](docs/FORMALIZATION_COVERAGE.md), [Authority deployment](deploy/authority/README.md), [Daemon deployment](deploy/daemon/README.md).

## Jeden produkt, trzy domeny zaufania

```text
                           IMANDRAX × DGM × RSI Ω
                        imandrax-dgm (jedno CLI/API)
                                    |
                +-------------------+-------------------+
                |                   |                   |
         IMANDRAX MATH          DGM EVOLUTION       RSI PROPOSER
       MSC2020 / 2010         kandydaci, ocena     LLM + OpenAlex
       źródła, arytmetyka     ranking, genealogia  Docker bez sieci
       Lean / MuJoCo*         eksperymenty*        badania cykliczne
                |                   |                   |
                +-------------------+-------------------+
                                    |
                      Artifact binding SHA-256
                                    |
                   RSIReviewStore: PROPOSED (no approval)
                                    |
                   niezależne dowody + podpis użytkownika
                                    |
                  ApprovedArchive (tylko zaakceptowane)
                                    |
               osobny proces wdrożenia za zgodą właściciela*
```

`*` Odrębne bramki i infrastruktura — nie wszystkie wdrożone. **DGM nie jest uprawniony do modyfikowania reguł dowodzenia, podpisów, benchmarków, polityk, CI ani własnych uprawnień.**

## Co faktycznie jest zaimplementowane

| Warstwa | Implementacja | Ograniczenie |
|---|---|---|
| ImandraX | `KnowledgeIndex`, MSC2020/2010, 6006 kodów MSC2020 w repo + opcjonalna zewnętrzna baza 19 114 rekordów | Indeks nie dowodzi twierdzeń |
| ImandraX | `IntegratedEngine.math`: źródła, dokładna ograniczona arytmetyka, jawne `PROOF_NOT_CHECKED` | Formalne dowody wymagają niezależnego jądra Lean |
| ImandraX | `UnifiedResearchEngine`, katalog 701 publicznych repozytoriów, kontrola źródeł, hash-chain | 704 repozytoria zinwentaryzowane; 3 prywatne nie są publikowane |
| DGM | `ResearchCycle`, trwały `ResearchArchive` wielopokoleniowy, regresja i heldout, `ApprovedArchive` | Metryki lokalne nie są podpisanymi atestacjami |
| RSI | `ProposalGenerator` z HTTPS LLM allowlist i OpenAlex | Klucze API użytkownika wymagane; brak natywnego API ChatGPT Deep Research |
| RSI | `DockerSandbox`: read-only, no-net, no-new-privileges, limity CPU/RAM/procesów | Docker nie zastępuje mikroVM ani niezależnej atestacji |
| Approval | `RSIReviewStore` + TLS 1.3 reference authority, Ed25519 i 4 suites; Compose dla osobnego hosta | Zewnętrzny serwer i klucze nie są wdrożone |
| Unified | `IntegratedEngine.evolve`: indeks → LLM/DGM → testy → weryfikacja hash → `PROPOSED` | Brak auto-apply/merge/deploy |
| Research watch | GitHub Actions co 6h i opcjonalny `imandrax-daemon` z trwałym stanem | Harmonogram GitHub nie gwarantuje 24/7; kod RSI wymaga konfiguracji |

## Instalacja i testy

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m compileall -q src scripts
python scripts/build_msc_full_index.py --output /tmp/imandrax-msc.sqlite3
imandrax-dgm --root . math --knowledge-db /tmp/imandrax-msc.sqlite3 \
  --kind LOOKUP --source MSC2020-OFFICIAL --code 00-01
imandrax-dgm --root . math --knowledge-db /tmp/imandrax-msc.sqlite3 \
  --kind EXACT_COMPUTE --operation gcd --arguments '{"a":84,"b":36}'
```

**Pełny indeks 19 114 rekordów:** [Google Drive — IMANDRAX_MATH_KNOWLEDGE_FTS.sqlite3](https://drive.google.com/file/d/1P9G-NPCYBbHp6FfxuDlLupyz-tyWfVE5/view). Pobierz go lokalnie i podaj jego ścieżkę przez `--knowledge-db`. Nie jest dołączony do publicznego repozytorium ze względu na zakres i licencjonowanie materiałów źródłowych. `build_msc_full_index.py` tworzy 6006 szczegółowych etykiet klasyfikacji MSC2020, lecz **nie** 19 114 pełnych rekordów ani bibliotekę dowodów.

## Zintegrowany cykl RSI — tylko propozycje

```bash
# Po skonfigurowaniu RSI_LLM_ENDPOINT, RSI_LLM_MODEL,
# RSI_LLM_API_KEY, RSI_LLM_ALLOWED_HOSTS i RSI_SANDBOX_IMAGE:
imandrax-dgm --root . evolve \
  --knowledge-db /tmp/imandrax-msc.sqlite3 \
  --state-dir /tmp/imandrax-state \
  --campaign-id research-001 \
  --source MSC2020-OFFICIAL --code 00-01 \
  --base-commit "$(git rev-parse HEAD)" \
  --output /tmp/imandrax-review-001 --max-candidates 2
```

Pętla: **matematyczne źródła → ograniczone badania internetowe → propozycja kodu → statyczna kontrola → izolowane testy → wiązanie SHA-256 → rejestr `PROPOSED` → niezależna weryfikacja → podpis użytkownika → dopiero zatwierdzone archiwum.**

Zapis `PROPOSED` **nie jest** zgodą na modyfikację `main`. Nawet podpis użytkownika w rejestrze nie jest automatycznym wdrożeniem; odrębny proces wydania musi sprawdzić ten sam kod i uprawnienia.

## Dokumentacja źródłowa — zachowana bez utraty wymagań

- [Wspólna architektura v0.5](docs/UNIFIED_ENGINE_v0.5.md) i [architektura historyczna v0.4](docs/UNIFIED_ENGINE_v0.4.md)
- [Macierz integracyjna ImandraX/DGM/RSI](docs/INTEGRATION_MATRIX.md)
- [Roadmap](docs/ROADMAP.md), [Bezpieczeństwo](SECURITY.md), [Approval](docs/OPERATOR_APPROVAL.md)
- [Oryginalne plany ImandraX v1.3 i DGM–RSI v1.0](docs/blueprints/README.md), w tym 239 wymagań z 14-stronicowego PDF
- [Routing 63 klas MSC2020](docs/MSC2020_63_CLASS_ROUTING.md), [Wersje Lean](docs/LEAN_BUILD_MATRIX.md)

**Uwaga o dokumentach historycznych:** wcześniejsze blueprints określały ImandraX i DGM jako odrębne projekty. Zachowano je jako niezmienione źródła wymagań. Obowiązującym zakresem jest odtąd **jeden silnik ImandraX × DGM × RSI Ω**, nie OCAF ani Aetheris.

## CI i tryb ciągły

- `python-ci.yml`: testy Python, Docker, MuJoCo, Lean w GitHub Actions. **Nie oznaczać ich jako PASS bez sprawdzenia konkretnych runów.**
- `rsi-research-cycle.yml`: harmonogram co 6 godzin. Publiczny research-watch nie wymaga kluczy; generowanie kodu wymaga jawnego `RSI_CYCLE_ENABLED=true` i konfiguracji API. Żaden job nie posiada `contents: write`.
- `main` jest jedyną gałęzią docelową dla zmian wykonywanych na zlecenie użytkownika. **Zmiany generowane autonomicznie przez RSI wymagają osobistego zatwierdzenia użytkownika**. Ochrona Ruleset GitHub i niezależna infrastruktura zatwierdzania są nadal konieczne.

## Status i granice

Brak wdrożenia niezależnego proof checker dla wszystkich dziedzin MSC, produkcyjnej atestowanej wielopokoleniowej ewolucji, pełnej kompilacji wszystkich forków Lean, atestowanej mikroVM, niezależnego serwera na hostingu, automatycznego bezpiecznego release i pełnego audytu kodu 704 repozytoriów. Warianty RSI pozostają wyłącznie propozycjami do osobistej akceptacji. Projekt nie deklaruje osiągnięcia AGI ani gwarantowanego rozwoju „umiejętności wyłaniających się”.

## Zweryfikowane CI dla v0.5 — 2026-10-29

- [Główne CI](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920434911): **4/4 PASS** (Python, Docker no-net, MuJoCo CPU, własne moduły Lean).
- [Cztery przypięte forki Lean](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920435010): **4/4 PASS** — `Batteries` (396 jobs), `Iris` (321), `MIL` (3598), `Mathlib.Algebra.Group.Basic` i zależności (627). **Nie jest to pełna kompilacja całego mathlib4 ani dowód wszystkich twierdzeń.**

## Formalizacja i niezależne jądra — v0.6

- `proofs_mathlib/`: osobna, przypięta wersją Lean 4.36.0-rc2 przestrzeń Lake z rzeczywistymi twierdzeniami importującymi Mathlib; osobne przestrzenie są niezbędne, ponieważ `iris-lean` i `mathematics_in_lean` wymagają innych toolchains. **Jedno repozytorium i jeden silnik nie oznaczają jednego niekompatybilnego toolchain.**
- `.github/workflows/lean-full-formal-verification.yml`: **próba pełnej kompilacji `lake build Mathlib`** (zamiast jednego podmodułu), `leanchecker` oraz `lake check --paranoid` dla własnych dowodów. Dopóki konkretne runy CI nie przejdą, status tych nowych bramek to **NOT VERIFIED**.
- `src/imandrax_dgm/formal_verification.py`: rejestr dowodów z domyślną odmową; wymagany hash źródła, przypięty commit i **podpis Ed25519 zewnętrznego, zaufanego runnera**. Sam wynik LLM ani wynik `pytest` nie mogą nadać statusu dowodu.
- `scripts/proof_coverage_report.py`: ścisła macierz 6006 tematów MSC i **9 kandydatów na dowody** przypisanych do 7 kodów. Dopóki nie ma niezależnego potwierdzenia, liczba dowodów w rejestrze to **0**, a nie 6006.

Pełna formalizacja **całej matematyki** nie jest zamkniętym zadaniem możliwym do oznaczenia jako wykonane; możliwe jest stopniowe formalizowanie konkretnych twierdzeń i dowodów. Nowy checker nie jest systemem odkrywania dowodów, lecz ich niezależnej weryfikacji.

**Korekta audytowa:** weryfikacja v0.6 wykryła, że wcześniejszy krok CI własnych twierdzeń Lean uruchamiał Lake bez domyślnego celu (`Nothing to build`). Dodano obowiązkowy `defaultTargets = ["ImandraX"]`. Poprzedni zielony wynik CI dla tej części nie jest dowodem kompilacji; decydują wyniki po tej poprawce.

**Jedno API dla dowodów:** `IntegratedEngine.math(MathTask(kind="FORMAL_PROOF_STATUS", statement="ImandraXMathlib.polynomial_square"))` odczytuje wpis rejestru `FormalEvidenceRegistry`. Bez podpisanego wyniku zewnętrznego checkera zwraca `UNVERIFIED`, nigdy nie traktuje dowolnego zdania naturalnego jako dowodu. CLI `imandrax-dgm math --kind FORMAL_PROOF_STATUS --statement ...` udostępnia ten sam odczyt.
