# SECURITY — ImandraX × DGM × RSI Ω

## Główna zasada: użytkownik jest jedyną władzą zatwierdzającą

Każda zmiana artefaktu wykonywalnego, kodu, promptów, polityki, kluczy, zależności, benchmarków, modelu, konfiguracji lub wdrożenia wymaga osobnej, świadomej zgody właściciela. Proposer DGM/RSI **nie posiada klucza zatwierdzającego**, uprawnień do `main`, sekretów CI, runnera ani zaufanego checkera. Zatwierdzenie wymaga podpisu Ed25519 na kanonicznym JSON zawierającym: identyfikator propozycji, SHA-256 manifestu, SHA-256 patcha, SHA-256 źródła bazowego, hash polityki, tożsamość recenzenta, decyzję i termin ważności.

### Implementowane w v0.2

- Brak API `apply`, `deploy`, `merge` lub automatycznej promocji; tylko propozycje, podpisy, archiwum metadanych.
- Fail closed przy braku publicznych kluczy użytkownika i runnera.
- Cztery niezależnie podpisane suites (`STATIC_CHECK`, `REGRESSION`, `SECURITY`, `HELDOUT`) z wynikiem `PASS` wymagane przed `APPROVE`.
- Podpisane decyzje `APPROVE`/`REJECT` są końcowe dla danej propozycji. Wygasły podpis traci ważność autoryzacyjną.
- Whitelist ścieżek badawczych i blokada `security`, `policy`, `tests`, `release`, `.github`, `keys`, `ci` itd. Identyfikatory są immutowalne.
- Podpisy runnera i recenzenta muszą należeć do różnych kluczy.
- Lokalny rejestr audytowy append-only z hash-chain; nie jest zabezpieczeniem przed administratorem bazy.

### Czego nie zapewnia lokalny prototyp

SQLite w tym samym procesie nie jest odporną na przejęcie granicą uprawnień. Proposer musi działać w **innym procesie i innym kontekście bezpieczeństwa**, a w produkcji również na niezależnym hoście/VM. `RSIInbox` ma ograniczenia plików i symlinków, lecz nie gwarantuje ochrony przed wyścigami filesystemu ani przed atakiem lokalnego właściciela katalogu. Nie uruchamiać niezaufanego patcha na hoście. `APPROVED` jest zapisem podpisanej decyzji, **nie** wdrożeniem. Przed zastosowaniem patcha wymagany jest osobny trusted applier sprawdzający rzeczywiste SHA-256 plików, baseline i podpisy, z rollbackiem.

### GitHub

Dla `main` włącz w Settings → Rules → Rulesets: PR required, minimum 1 review przez właściciela, CODEOWNERS, status CI, zakaz force push, brak bypass dla botów, restricted direct pushes. Sam plik `CODEOWNERS` nie wymusza zatwierdzenia, jeśli nie ma reguły GitHub. Agentom nie wolno używać tokenów z prawem merge ani admin. Początkowy kod powinien być oceniony w PR przed połączeniem.

### Nie uruchamiać

`mojealterego/RSIAI0` domyślnie opisuje konfigurację real shell z nieograniczonymi poleceniami. Upstream `dgm` jest badawczym eksperymentem, nie bezpiecznym modułem do osadzenia w zaufanej usłudze. Oba traktować jako **niezaufane źródła**. Nie kopiować sekretów ani prywatnej listy repozytoriów do publicznego repo.