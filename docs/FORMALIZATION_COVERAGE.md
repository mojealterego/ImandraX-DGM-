# Matematyka: indeksowanie ≠ formalne dowodzenie

**Stan 2026-10-29:** MSC2020 zawiera 63 klasy, 534 podklasy i 6006 kodów szczegółowych. Repozytorium przechowuje rzeczywiste 6006 kodów i etykiet z numerami stron w `data/msc2020_6006_coverage.csv`. Skrypt `build_msc_full_index.py` tworzy przeszukiwalną bazę SQLite FTS5. W całym CSV pole `verified_proof` ma wartość `NO`, a `formalized_in_lean` — `NOT_AUDITED`. Nie wolno interpretować tego jako 6006 sprawdzonych twierdzeń.

| Warstwa | Zakres obecny | Status dowodu |
|---|---|---|
| MSC2020 source titles | 6006 szczegółowych etykiet | `SOURCE_INDEXED_NOT_FORMALIZED` |
| Pełna baza matematyczna (opcjonalna) | 19 114 rekordów w zewnętrznym SQLite | Indeks wiedzy, nie biblioteka formalnych dowodów |
| Lean4 `ImandraX.Basic` | Elementarne tożsamości i implikacje | Sprawdzane przez Lean CI |
| Lean4 `ImandraX.Arithmetic` | Arytmetyka naturalna, równości, koniunkcje | Sprawdzane przez Lean CI po push |
| Forki `mathlib4`, `batteries`, `iris-lean`, `mathematics_in_lean` | Przypięte SHA i macierz CI | Testy upstream; nie zastępują własnej formalizacji |
| Clay Millennium Problems | Źródłowa polityka dowodowa | Brak nowego rozwiązania ani certyfikacji |
| 239 wymagań z 14-stronicowego PDF | Zachowana macierz źródłowa w `docs/blueprints/` | Część zaimplementowana, reszta do realizacji |

Każdy przyszły dowód wymaga: typowanego sformułowania twierdzenia i założeń, jawnych aksjomatów, przypiętego toolchain, niezależnego sprawdzenia jądrem Lean, pełnego identyfikatora modułu i artefaktów, podpisu zaufanego runnera, kontroli pochodzenia oraz odrębnej akceptacji publikacji. Wynik symulacji MuJoCo, testu jednostkowego czy odpowiedzi LLM nie jest formalnym dowodem.
