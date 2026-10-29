# Matematyka: indeksowanie ≠ formalne dowodzenie

**Stan 2026-10-29:** MSC2020 zawiera 63 klasy, 534 podklasy i 6006 kodów szczegółowych. Repozytorium przechowuje rzeczywiste 6006 kodów i etykiet z numerami stron w `data/msc2020_6006_coverage.csv`. Skrypt `build_msc_full_index.py` tworzy przeszukiwalną bazę SQLite FTS5. W całym CSV pole `verified_proof` ma wartość `NO`, a `formalized_in_lean` — `NOT_AUDITED`. Nie wolno interpretować tego jako 6006 sprawdzonych twierdzeń.

| Warstwa | Zakres obecny | Status dowodu |
|---|---|---|
| MSC2020 source titles | 6006 szczegółowych etykiet | `SOURCE_INDEXED_NOT_FORMALIZED` |
| Pełna baza matematyczna (opcjonalna) | 19 114 rekordów w zewnętrznym SQLite | Indeks wiedzy, nie biblioteka formalnych dowodów |
| Lean4 `ImandraX.Basic` | Elementarne tożsamości i implikacje | Sprawdzane przez Lean CI |
| Lean4 `ImandraX.Arithmetic` | Arytmetyka naturalna, równości, koniunkcje | GitHub Lean CI PASS: https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920434911 |
| Forki `mathlib4`, `batteries`, `iris-lean`, `mathematics_in_lean` | Przypięte SHA i macierz CI | Testy upstream; nie zastępują własnej formalizacji |
| Clay Millennium Problems | Źródłowa polityka dowodowa | Brak nowego rozwiązania ani certyfikacji |
| 239 wymagań z 14-stronicowego PDF | Zachowana macierz źródłowa w `docs/blueprints/` | Część zaimplementowana, reszta do realizacji |

Każdy przyszły dowód wymaga: typowanego sformułowania twierdzenia i założeń, jawnych aksjomatów, przypiętego toolchain, niezależnego sprawdzenia jądrem Lean, pełnego identyfikatora modułu i artefaktów, podpisu zaufanego runnera, kontroli pochodzenia oraz odrębnej akceptacji publikacji. Wynik symulacji MuJoCo, testu jednostkowego czy odpowiedzi LLM nie jest formalnym dowodem.

## Potwierdzona macierz Lean — 2026-10-29

GitHub Actions: [pinned upstream compatibility](https://github.com/mojealterego/ImandraX-DGM-/actions/runs/40920435010). Wszystkie cztery joby zakończyły się sukcesem na przypiętych commitach:

| Repozytorium | Kompilacja | Zweryfikowany zakres |
|---|---|---|
| `mathlib4` | PASS — 627 jobs | `Mathlib.Algebra.Group.Basic` i jego zależności, **nie pełny mathlib** |
| `batteries` | PASS — 396 jobs | Cel `Batteries` |
| `iris-lean` | PASS — 321 jobs | Cel `Iris` |
| `mathematics_in_lean` | PASS — 3598 jobs | Cel `MIL` |

Zaliczenie kompilacji upstream nie oznacza importu tych bibliotek do jednego proof checker ImandraX ani formalizacji 6006 klas/kodów.

## Nowa infrastruktura dowodowa v0.6 (status przed uruchomieniem CI)

1. `proofs_mathlib` — oddzielny workspace dla pełnego Mathlib, przypięty do `mojealterego/mathlib4@d0207795ac79006da92d98544e1ce915ae386160` i Lean 4.36.0-rc2. Własne twierdzenia znajdują się w `ImandraXMathlib/Foundations.lean`. **9 twierdzeń to kandydaci źródłowi, nie 6006 formalizacji.**
2. `lean-full-formal-verification.yml` — trzy zadania: `lake check --paranoid` na własnych bazowych dowodach; pełne `lake build Mathlib` z `leanchecker Mathlib`; oraz kompilacja i `lake check --paranoid` nowych twierdzeń z importem Mathlib. Zaliczenie `lake build Mathlib` nie jest równoważne niezależnemu ponownemu sprawdzeniu wszystkich zależności przez każde jądro.
3. `formal_verification.py` — typowany rejestr z hashem SHA-256 i podpisem Ed25519 zewnętrznego runnera. Odmawia oznaczenia dowodu jako zweryfikowanego bez podpisu i zgodności commitów. Ten rejestr nie zastępuje samego uruchomienia checkera ani zaufanego serwera podpisów.
4. `proof_coverage_report.py` — walidacja 6006 kodów MSC2020 i powiązań z nazwanymi deklaracjami. Kategorie MSC są tematami, a nie twierdzeniami. Nie wolno uznać całego MSC za udowodniony po sprawdzeniu jednego twierdzenia.

Źródła narzędzi: Lean 4.35.0 release notes oraz Lean Reference Manual, `lake check --paranoid` (oddzielne jądra `nanoda`, `lean4lean`, `con-leche`, `con-ron`). Należy nadal odróżniać replay przez `leanchecker` (ten sam kernel) od niezależnych implementacji.

### Audyt CI — wykryta i naprawiona fałszywie pozytywna kompilacja

Pierwszy przebieg v0.6 wykazał, że dotychczasowy `proofs/lakefile.toml` nie miał `defaultTargets`, a `lean-action` zgłaszał `Nothing to build`. Z tego powodu wcześniejszy status `lean-proof-kernel PASS` nie był wystarczającym dowodem kompilacji własnych twierdzeń. Wprowadzono `defaultTargets = ["ImandraX"]`, a nowy workflow wymaga jawnego `leanchecker --fresh ImandraX` oraz `lake check --paranoid`. Również nowy workspace Mathlib wymaga wygenerowania manifestu Lake przed uruchomieniem zautomatyzowanej konfiguracji; zastosowano `auto-config: false` i jawne `lake update`. Wyniki po naprawie należy odczytać z nowego przebiegu GitHub Actions, nie z poprzednich PASS.
