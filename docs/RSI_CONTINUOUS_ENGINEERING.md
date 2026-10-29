# ImandraX × DGM × RSI Ω v0.3 — specyfikacja implementacyjna ciągłego rozwoju

## 0. Zasady nadrzędne

- **Właściciel zatwierdza każdą zmianę**: generator może proponować kod, runner może go wykonać w izolacji, lecz nie istnieje droga `proposal -> merge` ani `proposal -> deployment` bez podpisanej decyzji użytkownika, PR i niezależnych testów.
- **Niezmienny trust root**: agent nie edytuje `src/imandrax_dgm/{rsi,gates,approval_api,sandbox}.py`, `SECURITY.md`, testów, workflows, signerów, trust.json ani ochrony gałęzi. W v0.3 zmienia wyłącznie `research/solver.py` jako propozycję.
- **Rozdział płaszczyzn**: research+LLM (internet, API key, read-only GitHub) ≠ sandbox (bez sieci, bez sekretów) ≠ authority (oddzielny host, klucze publiczne i audyt) ≠ GitHub PR (zatwierdzany przez właściciela).
- **Bez fikcyjnych atestacji**: lokalne testy zwracają `EVALUATED_UNATTESTED`, nie podpisane `PASS` od niezależnego runnera. Podpis wymaga zewnętrznego procesu.

## 1. Przepływ danych i kontrola zaufania

```
[GitHub main, owner-approved source] --read-only--> [Research cycle, OpenAlex API]
                                                    | metadata, DOI, citation URL
                                                    v
[Owner-provided LLM endpoint, API key] --> [JSON proposal, exact source, SHA256 diff]
                                                    |
                                                    v
                                          [ResearchGate + AST guard]
                                                    |
                                                    v
                     [Docker --network none --read-only --cap-drop ALL]
                      /                  |                         \
              regression             heldout                    telemetry
                      \                  |                         /
                       [DGM rank + immutable candidate bundle]
                                          |
                                          v
                         [Artifact for OWNER REVIEW; no auto-PR]
                                          |
                     [Independent runner signed evidence]
                                          |
                      [External TLS Approval Authority]
                                          |
                      [Offline Ed25519 human signature]
                                          |
                         [GitHub PR + required CODEOWNERS]
                                          |
                         [Owner manually merges to main]
```

## 2. Proposer: realne generowanie kodu

`generator.py` używa modelu obsługującego interfejs Chat Completions, z endpointem HTTPS w ścisłej allowliście `RSI_LLM_ALLOWED_HOSTS`. Sekret `RSI_LLM_API_KEY` znajduje się w GitHub Actions Secrets i **nie jest przekazywany do sandboxa**. JSON modelu jest traktowany jako niezaufany: dokładnie jeden plik, ścieżka `research/solver.py`, limit 160 KB, zwięzła hipoteza, ograniczenie tokenów i czasu. Wynik to `GeneratedProposal` z dokładnym tekstem, unified diff, SHA-256 patcha, SHA-256 bazy, identyfikatorem propozycji i pochodzeniem źródeł. Generator nie zapisuje pliku źródłowego.

## 3. Badania i dostęp do internetu

`OpenAlexResearch` pobiera metadane naukowe wyłącznie z `https://api.openalex.org/works`. Limit: 10 rekordów na zapytanie, 512 KB na odpowiedź, timeout 12 s, odrzucanie przekierowań, walidacja identyfikatorów OpenAlex, zapis DOI i roku publikacji. Model widzi je jako **untrusted data**. Brak bezpośredniej dowodowej weryfikacji treści publikacji; bibliografia to materiał do dalszego sprawdzenia.

**ChatGPT Deep Research nie jest udostępnione temu kodowi jako wywoływalne API.** Dostarczono samodzielny moduł badawczy o znacznie węższym zakresie, bez podszywania się pod funkcję produktu ChatGPT. Rozbudowa o wieloetapowe Deep Research wymaga osobnej, rzeczywiście dostępnej usługi i umowy interfejsu, źródeł oraz uprawnień.

## 4. DGM: warianty, selekcja i niezmienność

Każdy cykl generuje maksymalnie 2 warianty (kod pozwala na 1–4). Każdy kandydat przechodzi walidację AST, izolowane testy regresyjne (30 przypadków) i osobny zestaw transferowy/heldout (45 przypadków). Domena referencyjna: `gcd`, `mod_pow`, `is_prime`. Źródłem oczekiwanych wyników są deterministyczne funkcje Pythona po stronie runnera, **nie** odpowiedzi LLM. Ranking: `0.25*regression + 0.65*heldout + 0.10*novelty`. Kandydat musi mieć co najmniej 90% poprawności w obu zestawach; słabszy nie jest promowany do pakietu recenzenckiego. Jest to minimalny benchmark, **nie dowód ogólnej inteligencji ani nowych umiejętności wyłaniających się**.

Wynik zapisuje `research.json`, `evaluation.json`, `proposal.json`, `changes.json`, `cycle_status.json`, `SHA256SUMS.json`. Stan wybranego kandydata: `AWAITING_HUMAN_REVIEW`. Baza wariantów DGM v0.2 pozostaje oddzielna i dopuszcza jedynie podpisane warianty. W v0.3 **nie** zaimplementowano trwałego, międzycyklicznego archiwum generacji ani realnego modelu samodzielnego wyznaczania nowych dziedzin kompetencji.

## 5. Sandbox i ryzyko wykonania

Wykonawca `DockerSandbox` nie używa powłoki ani poleceń podanych przez model. Wywołuje `docker run` z `--network none`, `--read-only`, `--cap-drop ALL`, `no-new-privileges`, PID 64, RAM 512 MB, CPU 1, użytkownikiem 65534, readonly bind-mounts i tmpfs. Ustawia timeout 90 s, ogranicza stdout, a przy przekroczeniu czasu żąda `docker rm -f`. Kod modelu nie otrzymuje żadnych sekretów ani tokenów.

**Ograniczenie krytyczne:** Docker na zwykłym hostcie nie jest granicą równoważną Firecracker/microVM. Wersja produkcyjna wymaga dedykowanych, efemerycznych microVM, oddzielnego hosta, kontrolowanego obrazu `@sha256`, zewnętrznego monitoringu, niezależnego signer service i testów ucieczki z izolacji. Workflow CI używa nieprzypiętego `python:3.12-slim` tylko w trybie eksperymentalnym; produkcja odrzuca obraz bez SHA-256 digest.

## 6. Niezależny serwer zatwierdzania

`approval_api.py` dostarcza serwer TLS 1.3, trzy odrębne tokeny ról `proposer`, `runner`, `reviewer`, limity żądań 64 KB, brak CORS, brak logowania sekretów i API tylko do odczytu pakietów, rejestrowania propozycji, dowodów i decyzji. Decyzje są sprawdzane kryptograficznie przez istniejący `RSIReviewStore` (Ed25519). Token recenzenta **nie wystarczy** do zatwierdzenia; podpis musi pochodzić od osobnego klucza użytkownika. Serwer nie przechowuje prywatnego klucza użytkownika.

Nie wdrożono serwera na zewnętrzny host: brak przekazanych przez właściciela certyfikatów, adresu serwera i konfiguracji trwałego storage. SQLite z lokalnym audit trigger to **prototyp**, nie nieusuwalny audyt w rozproszonym systemie.

## 7. Proces w tle i jego aktywacja

Workflow `rsi-research-cycle.yml` ma cron `17 */6 * * *` (UTC), czyli **co 6 godzin**, i ręczne `workflow_dispatch`. Domyślnie jest **WYŁĄCZONY** warunkiem `vars.RSI_CYCLE_ENABLED == 'true'`. Po zaakceptowaniu PR, ochronie main i skonfigurowaniu `RSI_LLM_API_KEY`, `RSI_LLM_ENDPOINT`, `RSI_LLM_MODEL`, `RSI_LLM_ALLOWED_HOSTS` można aktywować generowanie. Workflow ma `contents: read`, nie może automatycznie pisać kodu do repozytorium, a wyniki zapisuje jako artefakty Actions przez 30 dni. To periodyczny runner, nie stale uruchomiony daemon 24/7. GitHub może opóźniać cron i wyłączyć harmonogram po 60 dniach bezczynności publicznego repozytorium.

## 8. Lean i MuJoCo — odrębne weryfikatory

- `proofs/` jest osobnym projektem Lake/Lean 4 przypiętym do `v4.36.0-rc2`. Workflow `lean-proof-kernel` buduje prawdziwy moduł Lean, lecz nie dowodzi poprawności dowolnego kodu RSI.
- `lean-upstream-manual.yml` umożliwia **ręczny** test czterech przypiętych commitów forków (`mathlib4`, `batteries`, `iris-lean`, `mathematics_in_lean`) w ich własnych toolchainach, bez łączenia niezgodnych wersji Lean.
- `mujoco-physics-e2e` instaluje prawdziwe MuJoCo i wykonuje deterministyczny CPU smoke test wahadła, bez renderingu.
- Dopiero logi zakończonych GitHub Actions mogą stanowić dowód rzeczywistych buildów; sam plik workflow nie jest takim dowodem.

## 9. Kryteria zakończenia produkcyjnego (obecnie niespełnione)

1. Aktywny ruleset `main`, PR review właściciela, required CI i brak bot bypass.
2. Zewnętrzny, wdrożony serwer approval + niezależny hardware-backed signer; audyt w zewnętrznym WORM store.
3. MicroVM sandbox z blokadą egress, ucieczki, sekrety poza VM, certyfikowany obraz i dowód braku dostępu do Docker socket.
4. Trwały, podpisany archiwum DGM, selekcja zatwierdzonych rodziców, statystyczne porównania z baseline i kontrola regression drift.
5. E2E od LLM do wygenerowanego diffu, wykonania w sandboxie, atestacji, podpisu człowieka i PR, wraz z testami negatywnymi replay i TOCTOU.
6. Kompilacja mathlib4 i pozostałych Lean forków, testy MuJoCo na odpowiednich benchmarkach, oraz pełny audyt licencji i bezpieczeństwa 704 repozytoriów.
7. Monitorowanie kosztów, kwot, modeli, metryk jakości, retencji danych, alarmów i procedury kill-switch.

**Status:** v0.3 = działający lokalnie prototyp generowania/ewaluacji z mechanizmami odmowy; bez deklaracji wdrożenia produkcyjnego, bez automatycznego merge, bez uruchomionego w tle procesu przed akceptacją PR.