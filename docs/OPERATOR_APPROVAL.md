# Operator approval — instrukcja

**RSI nigdy nie zatwierdza siebie.** Operator przechowuje prywatny klucz Ed25519 poza agentem, jego katalogiem roboczym i CI. W środowisku agenta wolno przechowywać wyłącznie publiczny klucz w pliku konfiguracji poza repozytorium (przykład poniżej). Produkcja wymaga zewnętrznego procesu authority.

`/secure/trust.json` (przykład; wartości są placeholderami, **nie** kluczami):

```json
{"runners": {"runner-01": "<64 znaków hex klucza publicznego>"}, "reviewers": {"user-01": "<64 znaków hex klucza publicznego>"}}
```

## Format propozycji

```json
{
  "candidate_id": "research-001",
  "parent_digest": "<64 znaki hex SHA-256 bazowego drzewa>",
  "patch_digest": "<64 znaki hex SHA-256 dokładnego patcha>",
  "paths": ["harness/planner.py"],
  "hypothesis": "Zmiana strategii wyszukiwania lematów na podstawie błędów",
  "max_tokens": 1000,
  "max_runtime_seconds": 60
}
```

Zarejestruj: `python -m imandrax_dgm.rsi_cli --db local-rsi-review.sqlite3 submit --candidate candidate.json`.

Runner z niezależnego klucza podpisuje dokładny `canonical_payload(payload)` i wystawia JSON:

```json
{
  "payload": {
    "candidate_digest": "<manifest_digest z wyniku submit>",
    "source_digest": "<parent_digest>",
    "suite": "STATIC_CHECK",
    "result": "PASS",
    "runner_id": "runner-01"
  },
  "signer_id": "runner-01",
  "signature_hex": "<128 znaków hex podpisu Ed25519>"
}
```

Wymagane są cztery osobne atestacje `STATIC_CHECK`, `REGRESSION`, `SECURITY`, `HELDOUT` i realne wyniki niezależnego wykonawcy. **Nie generuj fikcyjnych PASS.** W v0.2 runner i izolowane testy nie są jeszcze zbudowane.

Pakiet recenzenta: `python -m imandrax_dgm.rsi_cli --db local-rsi-review.sqlite3 packet --id research-001`. Po obejrzeniu pełnego diffu i dowodów operator podpisuje *kanoniczny JSON* z dodatkowymi polami `decision`, `reviewer_id`, `expires_at` (Unix UTC). Odpowiedź:

```json
{"payload": {"proposal_id":"...", "manifest_digest":"...", "policy_digest":"...", "base_digest":"...", "patch_digest":"...", "decision":"APPROVE", "reviewer_id":"user-01", "expires_at":2000000000}, "signer_id":"user-01", "signature_hex":"..."}
```

Rejestracja: `python -m imandrax_dgm.rsi_cli --db local-rsi-review.sqlite3 --trust /secure/trust.json decide --file signed-decision.json`.

**Ważne:** podpisane zatwierdzenie nie zapisuje ani jednego bajtu w repozytorium i nie uruchamia kodu. Przed rzeczywistą zmianą należy zweryfikować rzeczywisty patch, niezależny checker, policy, GitHub PR i ruleset. Brak któregokolwiek elementu = brak wdrożenia.

## Aktualizacja v0.4 — tryb `main` bez dodatkowych gałęzi

Właściciel wybrał bezpośrednie prace inżynieryjne na `main`. **RSI nadal nie może samodzielnie zastosować zmian**. Słowo „PR” w historycznych krokach powyżej oznacza opcjonalny kanał ręcznej recenzji, nie obowiązek tworzenia gałęzi przy bezpośrednim poleceniu właściciela. Wymagania kryptograficzne, testowe i niezależne sprawdzenie patcha pozostają bez zmian.