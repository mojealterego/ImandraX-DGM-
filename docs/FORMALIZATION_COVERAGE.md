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
