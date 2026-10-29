# ImandraX × DGM × RSI Ω

**v0.2 — zweryfikowany lokalnie prototyp badawczy; nie jest produkcyjnym proverem ani działającą autonomiczną maszyną RSI.**

Ten projekt łączy interfejs badawczy ImandraX (indeks wiedzy matematycznej i kontrola pochodzenia danych), zasady ewolucyjnego archiwum DGM oraz **RSI wymagające każdorazowej, kryptograficznie podpisanej zgody użytkownika**. Automatyczne generowanie *propozycji* może działać w pętli; **kod nie może zostać samodzielnie zmieniony, zatwierdzony, uruchomiony ani wdrożony przez agenta**.

## Co działa w v0.2

- Odczyt metadanych 701 publicznych repozytoriów z 704-elementowego katalogu z 29.10.2026 (3 prywatne nie są publikowane).
- `KnowledgeIndex`: odczytowy adapter do opcjonalnego indeksu matematycznego SQLite; **nie jest solverem ani checkerem Lean**.
- `ResearchGate`: limity budżetu, zakresu ścieżek, kontrola referencji, weryfikacja Ed25519 podpisów runnera.
- `ImmutableLedger`: lokalny hash-chain zdarzeń badawczych, z ograniczeniami SQLite.
- `RSIReviewStore`: propozycja → podpisane niezależne wyniki czterech suite → **podpisana decyzja człowieka** → zapis statusu. Domyślnie brak kluczy = odmowa.
- `RSIInbox`: opcjonalna pętla przeglądająca JSON w katalogu propozycji, tylko odczyt i zapis do lokalnego rejestru; żadnego patchowania.
- `ApprovedArchive`: drzewo generacji DGM, do którego wolno dodać wyłącznie wariant z nadal ważną zgodą człowieka; wybór rodzica na podstawie wyniku, transferu i eksploracji.
- Testy regresyjne i negatywne bez dostępu do sieci, bez LLM, bez uruchamiania niezaufanego kodu.

## Nienaruszalna zasada

```text
DGM / RSI agent (niezaufany)
       │
       ├── propozycje + hipotezy + raporty → RSIInbox (read-only)
       │                                          │
       │                                          ▼
       │                               ResearchGate / Evidence
       │                                          │
       │                                          ▼
       │                                HUMAN REVIEW REQUIRED
       │                                          │
       │                                          ▼
       │                           podpis Ed25519 kluczem użytkownika
       │                                          │
       │                                          ▼
       └── brak prawa do commit/push/merge/deploy  APPROVED ≠ DEPLOYED
```

**Każda zmiana kodu, modelu, polityki, testów, promptów, zależności lub wdrożenia wymaga odrębnej akceptacji użytkownika.** Podpis zatwierdza konkretny manifest i hash patcha, nie ogólny kierunek rozwoju. Zmiana choć jednego bajtu wymaga nowego manifestu, pełnych testów i nowej zgody. To jest warunek projektowy; nie istnieje jeszcze niezależny produkcyjny egzekutor wydania.

## Instalacja / testy

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m compileall -q src
python -m imandrax_dgm.cli inventory
python -m imandrax_dgm.rsi_cli --db ./local-rsi-review.sqlite3 status --id example
```

Ostatnia komenda zgłosi brak propozycji, dopóki jej nie dodasz. `inventory` pokazuje **701 publicznych rekordów**, a nie prywatną pełną listę. Dane 19 114 rekordów matematycznych dostępne są w odrębnym pakiecie badawczym, **nie są publikowane jako binarny SQLite w tym repo**. Testy używają małej syntetycznej bazy.

## Kontrolowany RSI — przebieg

1. Zewnętrzny proposer zapisuje do `inbox/candidate.json` manifest `Candidate` z realnym SHA-256 patcha i stanu bazowego; nie ma uprawnień do repo produkcyjnego.
2. Operator uruchamia `imandrax-rsi --db local-rsi-review.sqlite3 tick --inbox inbox` albo `watch --inbox inbox --interval 30 --max-cycles 0` (proces działa tylko, gdy jest uruchomiony; `Ctrl+C` zatrzymuje).
3. Niezależny runner, docelowo w odizolowanej mikroVM, wystawia **podpisane** wyniki `STATIC_CHECK`, `REGRESSION`, `SECURITY`, `HELDOUT`. Brak dowodów = brak zgody.
4. `imandrax-rsi --db ... --trust /secure/trust.json packet --id candidate-id` zwraca pakiet do podpisania przez człowieka.
5. Użytkownik **osobiście** sprawdza `details --id candidate-id`, pełny diff, dowody, licencje i ryzyka; podpisuje pakiet **poza środowiskiem agenta**. `decide --file signed-decision.json` rejestruje decyzję, ale nie zmienia kodu.
6. Dopiero odrębna, niezależna infrastruktura z obowiązkowym PR, ochroną `main` i dodatkową weryfikacją SHA może zastosować zatwierdzony patch. **Nie jest zaimplementowana w v0.2.**

Dokumenty: [Security](SECURITY.md), [Operator approval](docs/OPERATOR_APPROVAL.md), [Roadmap](docs/ROADMAP.md), [Architecture](docs/UNIFIED_ARCHITECTURE.md), [Lean matrix](docs/LEAN_BUILD_MATRIX.md).

## Co nie zostało wykonane

- Uruchomienie upstream `dgm`, `RSIAI0` lub generowanie kodu przez LLM.
- Produkcyjne nieprzerwane RSI, worker w Firecracker, pełne testy MuJoCo, kompilacje Lean/mathlib, formalna weryfikacja twierdzeń.
- Weryfikacja pełnego kodu wszystkich 704 repozytoriów, audyt SBOM, automatyczne benchmarki transferowe, niezależny signer i release authority.
- Egzekwowanie branch protection na GitHub (ustawienie repozytorium wymaga osobnego działania właściciela).

**Zewnętrzne repozytoria są materiałem porównawczym, nie bezwarunkowo importowanymi zależnościami.** Nie uruchamiać `RSIAI0` w trybie real/unrestricted. Zob. [źródłowe badanie DGM](https://arxiv.org/abs/2505.22954).

## v0.3 — automatyczny proposer + izolowany runner + niezależna authority (PR do akceptacji)

- `python -m imandrax_dgm.cycle_cli --root . --base-commit <40-znakowy-SHA> --output /tmp/rsi-review --max-candidates 2` generuje kod przez skonfigurowany model, pobiera metadane OpenAlex, uruchamia kandydatów w Docker bez sieci i zapisuje artefakty recenzenckie; **nie zmienia `research/solver.py`**.
- Wymagane zmienne: `RSI_LLM_ENDPOINT`, `RSI_LLM_MODEL`, `RSI_LLM_API_KEY`, `RSI_LLM_ALLOWED_HOSTS`, `RSI_SANDBOX_IMAGE` (w produkcji obraz przypięty `@sha256`).
- `.github/workflows/rsi-research-cycle.yml` uruchamia ograniczony cykl co 6 godzin **dopiero po merge do main i ręcznym włączeniu `RSI_CYCLE_ENABLED=true`**. Nie ma automatycznego PR, merge ani deploy.
- `python -m imandrax_dgm.authority_cli --trust /secure/trust.json --db /secure/review.db --cert /secure/tls.crt --key /secure/tls.key` uruchamia TLS 1.3 API zatwierdzania. Należy uruchomić na osobnym serwerze, z oddzielnymi kluczami i trzema silnymi tokenami ról; **nie jest wdrożone**.
- GitHub CI: unit/negative, rzeczywiste Docker no-net, MuJoCo CPU, Lean Lake build; osobny manualny workflow dla czterech forków Lean.
- Szczegółowa specyfikacja i ograniczenia: [`docs/RSI_CONTINUOUS_ENGINEERING.md`](docs/RSI_CONTINUOUS_ENGINEERING.md), [`docs/MAIN_RULESET_REQUIRED.md`](docs/MAIN_RULESET_REQUIRED.md).