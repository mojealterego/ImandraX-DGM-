# SECURITY — ImandraX × DGM × RSI Ω

## Główna zasada: użytkownik jest jedyną władzą zatwierdzającą

Każda zmiana artefaktu wykonywalnego, kodu, promptów, polityki, kluczy, zależności, benchmarków, modelu, konfiguracji lub wdrożenia wymaga osobnej, świadomej zgody właściciela. Proposer DGM/RSI **nie posiada klucza zatwierdzającego**, uprawnień do `main`, sekretów CI, runnera ani zaufanego checkera. Zatwierdzenie wymaga podpisu Ed25519 na kanonicznym JSON zawierającym: identyfikator propozycji, SHA-256 manifestu, SHA-256 patcha, SHA-256 źródła bazowego, hash polityki, tożsamość recenzenta, decyzję i termin ważności.

### Implementowane w v0.2–v0.4

- Brak API `apply`, `deploy`, `merge` lub automatycznej promocji; tylko propozycje, podpisy, archiwum metadanych.
- Fail closed przy braku publicznych kluczy użytkownika i runnera.
- Cztery niezależnie podpisane suites (`STATIC_CHECK`, `REGRESSION`, `SECURITY`, `HELDOUT`) z wynikiem `PASS` wymagane przed `APPROVE`.
- Podpisane decyzje `APPROVE`/`REJECT` są końcowe dla danej propozycji. Wygasły podpis traci ważność autoryzacyjną.
- Whitelist ścieżek badawczych i blokada `security`, `policy`, `tests`, `release`, `.github`, `keys`, `ci` itd. Identyfikatory są immutowalne.
- Podpisy runnera i recenzenta muszą należeć do różnych kluczy.
- Lokalny rejestr audytowy append-only z hash-chain; nie jest zabezpieczeniem przed administratorem bazy.

### Czego nie zapewnia lokalny prototyp

SQLite w tym samym procesie nie jest odporną na przejęcie granicą uprawnień. Proposer musi działać w **innym procesie i innym kontekście bezpieczeństwa**, a w produkcji również na niezależnym hoście/VM. `RSIInbox` ma ograniczenia plików i symlinków, lecz nie gwarantuje ochrony przed wyścigami filesystemu ani przed atakiem lokalnego właściciela katalogu. Nie uruchamiać niezaufanego patcha na hoście. `APPROVED` jest zapisem podpisanej decyzji, **nie** wdrożeniem. Przed zastosowaniem patcha wymagany jest osobny trusted applier sprawdzający rzeczywiste SHA-256 plików, baseline i podpisy, z rollbackiem.

### GitHub — obowiązująca decyzja właściciela v0.4

Zmiany bezpośrednio zlecone przez właściciela są rozwijane w `main`, bez nowych gałęzi. **Autonomiczny RSI nie posiada uprawnień do zapisu `main`** i nie może automatycznie zastosować patcha nawet po zaliczeniu testów. Właściciel zatwierdza dokładny manifest, a dopiero niezależny operator stosuje patch po weryfikacji SHA. GitHub Ruleset należy skonfigurować zgodnie z `docs/MAIN_RULESET_REQUIRED.md`; `CODEOWNERS` sam nie wymusza zatwierdzenia. 

### Nie uruchamiać

`mojealterego/RSIAI0` domyślnie opisuje konfigurację real shell z nieograniczonymi poleceniami. Upstream `dgm` jest badawczym eksperymentem, nie bezpiecznym modułem do osadzenia w zaufanej usłudze. Oba traktować jako **niezaufane źródła**. Nie kopiować sekretów ani prywatnej listy repozytoriów do publicznego repo.

## v0.3 — egress, wykonanie i approval

- **Brak auto-merge:** zaplanowany workflow ma `contents:read`; model nie posiada tokenu zapisu ani klucza prywatnego zatwierdzającego.
- **Separacja internetu:** research i LLM mogą korzystać z sieci, lecz Docker candidate ma `--network none` i nie otrzymuje sekretów.
- **Brak automatycznego podpisu:** unsigned local test reports nie są akceptowane jako niezależne PASS attestation.
- **Approval API:** TLS 1.3 i role bearer, lecz do zatwierdzenia nadal wymagany jest niezależny podpis Ed25519 użytkownika.
- **Docker ≠ Firecracker:** to ograniczony runner badawczy, nie dowód odporności na ucieczkę z kontenera.
- **GitHub main nadal niechroniony:** właściciel musi ustawić Ruleset zgodnie z `docs/MAIN_RULESET_REQUIRED.md`.