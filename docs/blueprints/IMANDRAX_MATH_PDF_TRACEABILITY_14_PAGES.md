> **GRANICA PROJEKTU (NORMATYWNA):** IMANDRAX Ω ENGINE jest samodzielnym systemem rozumowania matematycznego. Nie jest częścią OCAF Runtime ani Aetheris Photo–Video–Game. Integracje z innymi produktami nie są zakresem tej specyfikacji. Dokument opisuje projekt, nie wytrenowany ani wdrożony silnik.

# Ω-Reasoner — rejestr pokrycia KAŻDEGO pojęcia z pliku „Rozumowanie Matematyczne.pdf”

**Stan:** indeks wymagań (nie implementacja). **Źródło:** załączony PDF, 14 stron.

Każda pozycja oznacza osobne wymaganie śledzone do modułu i sprawdzalne co najmniej przez test klasy. Powtórzenia z materiału pozostają oddzielne (wystąpienia nie są kasowane). Dla podpunktów złożonych/definicji wielowierszowych zachowana jest treść źródłowa w `05_ROZUMOWANIE_MATEMATYCZNE_ZRODLO_MD.md`. Wymagania i kryteria odbioru są projektem IMANDRAX i **nie** występują jako gotowe rozwiązania w załączniku.

## Wymagane kolumny

`ID` = strona i numer wystąpienia; `moduł` = właściciel planowanej implementacji; `kontrakt` = grupa warunków do weryfikacji w odpowiedniej sekcji aneksu M; `test` = grupa testowa (indywidualny test ma identyfikator `ID/<test>`). Stan każdej pozycji: `REQUIREMENT / UNIMPLEMENTED`.

## Strona 1 — 23 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P01-01` | Modelowanie matematyczne | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P01-01/MATH` |
| `RM-P01-02` | Algebra liniowa | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P01-02/MATH` |
| `RM-P01-03` | Skalar | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-03/LIN` |
| `RM-P01-04` | Wektor | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-04/LIN` |
| `RM-P01-05` | Przestrzeń wektorowa | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-05/LIN` |
| `RM-P01-06` | Macierz (Matrix) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-06/LIN` |
| `RM-P01-07` | Tensor | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-07/LIN` |
| `RM-P01-08` | Operacje na macierzach (dodawanie, mnożenie) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-08/LIN` |
| `RM-P01-09` | Transpozycja macierzy | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-09/LIN` |
| `RM-P01-10` | Macierz odwrotna | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-10/LIN` |
| `RM-P01-11` | Wyznacznik macierzy (Determinant) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-11/LIN` |
| `RM-P01-12` | Ślad macierzy (Trace) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-12/LIN` |
| `RM-P01-13` | Iloczyn skalarny (Dot product) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-13/LIN` |
| `RM-P01-14` | Iloczyn wektorowy (Cross product) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-14/LIN` |
| `RM-P01-15` | Iloczyn Hadamarda (Element-wise) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-15/LIN` |
| `RM-P01-16` | Wartości własne (Eigenvalues) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-16/LIN` |
| `RM-P01-17` | Wektory własne (Eigenvectors) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-17/LIN` |
| `RM-P01-18` | Rozkład macierzy (Matrix Decomposition) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-18/LIN` |
| `RM-P01-19` | Rozkład SVD (Singular Value Decomposition) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-19/LIN` |
| `RM-P01-20` | Rozkład LU | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-20/LIN` |
| `RM-P01-21` | Rozkład QR | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-21/LIN` |
| `RM-P01-22` | Rozkład Cholesky'ego | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-22/LIN` |
| `RM-P01-23` | Macierz diagonalna | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P01-23/LIN` |

## Strona 2 — 23 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P02-01` | Macierz jednostkowa | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-01/LIN` |
| `RM-P02-02` | Macierz symetryczna | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-02/LIN` |
| `RM-P02-03` | Macierz ortogonalna | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-03/LIN` |
| `RM-P02-04` | Macierz rzadka (Sparse matrix) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-04/LIN` |
| `RM-P02-05` | Norma wektora (L_1, L_2, L_\infty) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-05/LIN` |
| `RM-P02-06` | Odległość euklidesowa | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-06/LIN` |
| `RM-P02-07` | Odległość Manhattan | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-07/LIN` |
| `RM-P02-08` | Podobieństwo kosinusowe (Cosine Similarity) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-08/LIN` |
| `RM-P02-09` | Rachunek różniczkowy | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-09/CALC` |
| `RM-P02-10` | Funkcja ciągła | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-10/CALC` |
| `RM-P02-11` | Granica funkcji | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-11/CALC` |
| `RM-P02-12` | Pochodna funkcji | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-12/CALC` |
| `RM-P02-13` | Pochodna cząstkowa | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-13/CALC` |
| `RM-P02-14` | Reguła łańcuchowa (Chain rule) | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-14/CALC` |
| `RM-P02-15` | Gradient (\nabla) | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-15/CALC` |
| `RM-P02-16` | Hesjan (Macierz Hessego) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-16/LIN` |
| `RM-P02-17` | Jakobian (Macierz Jacobiego) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P02-17/LIN` |
| `RM-P02-18` | Ekstrema lokalne | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-18/CALC` |
| `RM-P02-19` | Ekstrema globalne | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-19/CALC` |
| `RM-P02-20` | Punkt siodłowy | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-20/CALC` |
| `RM-P02-21` | Szereg Taylora | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-21/CALC` |
| `RM-P02-22` | Całka nieoznaczona | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-22/CALC` |
| `RM-P02-23` | Całka oznaczona | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P02-23/CALC` |

## Strona 3 — 23 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P03-01` | Rachunek zdań | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-01/LOG` |
| `RM-P03-02` | Zmienne zdaniowe | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-02/LOG` |
| `RM-P03-03` | Operatory logiczne (AND, OR, NOT, XOR) | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-03/LOG` |
| `RM-P03-04` | Tautologia | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-04/LOG` |
| `RM-P03-05` | Sprzeczność | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-05/LOG` |
| `RM-P03-06` | Rachunek predykatów pierwszego rzędu | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-06/LOG` |
| `RM-P03-07` | Kwantyfikatory (Ogólny, Szczegółowy) | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-07/LOG` |
| `RM-P03-08` | Relacje | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-08/LOG` |
| `RM-P03-09` | Funkcje | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-09/LOG` |
| `RM-P03-10` | Zbiory | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-10/LOG` |
| `RM-P03-11` | Teoria mnogości | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-11/LOG` |
| `RM-P03-12` | Iloczyn kartezjański | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P03-12/LOG` |
| `RM-P03-13` | Grafy (Teoria grafów) | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-13/GRAPH` |
| `RM-P03-14` | Wierzchołki i krawędzie | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-14/GRAPH` |
| `RM-P03-15` | Graf skierowany vs nieskierowany | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-15/GRAPH` |
| `RM-P03-16` | Graf ważony | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-16/GRAPH` |
| `RM-P03-17` | Drzewa (struktura danych) | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-17/GRAPH` |
| `RM-P03-18` | Cykle w grafie | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-18/GRAPH` |
| `RM-P03-19` | Ścieżka w grafie | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-19/GRAPH` |
| `RM-P03-20` | Algorytm Dijkstry (wzmianka matematyczna) | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-20/GRAPH` |
| `RM-P03-21` | Macierz sąsiedztwa | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P03-21/LIN` |
| `RM-P03-22` | Laplasjan grafu | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P03-22/GRAPH` |
| `RM-P03-23` | Teoria prawdopodobieństwa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P03-23/PROB` |

## Strona 4 — 24 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P04-01` | Przestrzeń probabilistyczna | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-01/PROB` |
| `RM-P04-02` | Zdarzenie losowe | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-02/PROB` |
| `RM-P04-03` | Prawdopodobieństwo warunkowe | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-03/PROB` |
| `RM-P04-04` | Niezależność zdarzeń | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-04/PROB` |
| `RM-P04-05` | Twierdzenie Bayesa (fundament AI) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-05/PROB` |
| `RM-P04-06` | Zmienna losowa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-06/PROB` |
| `RM-P04-07` | Dystrybuanta | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-07/PROB` |
| `RM-P04-08` | Gęstość prawdopodobieństwa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-08/PROB` |
| `RM-P04-09` | Wartość oczekiwana | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-09/PROB` |
| `RM-P04-10` | Wariancja | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-10/PROB` |
| `RM-P04-11` | Odchylenie standardowe | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-11/PROB` |
| `RM-P04-12` | Kowariancja | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-12/PROB` |
| `RM-P04-13` | Korelacja | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-13/PROB` |
| `RM-P04-14` | Rozkład normalny (Gaussa) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-14/PROB` |
| `RM-P04-15` | Rozkład Bernoulliego | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-15/PROB` |
| `RM-P04-16` | Rozkład dwumianowy | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-16/PROB` |
| `RM-P04-17` | Rozkład Poissona | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-17/PROB` |
| `RM-P04-18` | Rozkład wykładniczy | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-18/PROB` |
| `RM-P04-19` | Rozkład jednostajny | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-19/PROB` |
| `RM-P04-20` | Rozkład Beta | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-20/PROB` |
| `RM-P04-21` | Rozkład Gamma | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-21/PROB` |
| `RM-P04-22` | Prawo wielkich liczb | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-22/PROB` |
| `RM-P04-23` | Centralne twierdzenie graniczne | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-23/PROB` |
| `RM-P04-24` | Estymacja parametrów | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P04-24/PROB` |

## Strona 5 — 23 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P05-01` | Metoda największej wiarygodności (MLE) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-01/PROB` |
| `RM-P05-02` | Estymacja MAP (Maximum A Posteriori) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-02/PROB` |
| `RM-P05-03` | Procesy stochastyczne | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P05-03/MARKOV` |
| `RM-P05-04` | Łańcuchy Markowa | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P05-04/MARKOV` |
| `RM-P05-05` | Błądzenie losowe (Random Walk) | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P05-05/MARKOV` |
| `RM-P05-06` | Metody Monte Carlo | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-06/PROB` |
| `RM-P05-07` | Teoria Chaosu (efekt motyla w systemach) | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P05-07/MATH` |
| `RM-P05-08` | Algorytmy min-max | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P05-08/OPT` |
| `RM-P05-09` | Przycinanie alfa-beta | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P05-09/OPT` |
| `RM-P05-10` | Algebra liniowa w AI | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P05-10/MATH` |
| `RM-P05-11` | Macierze i wektory | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P05-11/LIN` |
| `RM-P05-12` | Iloczyn skalarny i normy | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P05-12/LIN` |
| `RM-P05-13` | Wartości własne i wektory własne | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P05-13/LIN` |
| `RM-P05-14` | Rozkład SVD (Singular Value Decomposition) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P05-14/LIN` |
| `RM-P05-15` | Rozkład QR | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P05-15/LIN` |
| `RM-P05-16` | Rachunek różniczkowy w uczeniu maszynowym | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P05-16/CALC` |
| `RM-P05-17` | Pochodne cząstkowe | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P05-17/CALC` |
| `RM-P05-18` | Gradient | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P05-18/CALC` |
| `RM-P05-19` | Hessian | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P05-19/CALC` |
| `RM-P05-20` | Rachunek całkowy w probabilistyce | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-20/PROB` |
| `RM-P05-21` | Prawdopodobieństwo warunkowe | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-21/PROB` |
| `RM-P05-22` | Twierdzenie Bayesa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-22/PROB` |
| `RM-P05-23` | Zmienna losowa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P05-23/PROB` |

## Strona 6 — 24 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P06-01` | Rozkład normalny (Gaussa) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-01/PROB` |
| `RM-P06-02` | Rozkład Bernoulliego | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-02/PROB` |
| `RM-P06-03` | Rozkład dwumianowy | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-03/PROB` |
| `RM-P06-04` | Rozkład Poissona | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-04/PROB` |
| `RM-P06-05` | Rozkład wykładniczy | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-05/PROB` |
| `RM-P06-06` | Prawo wielkich liczb | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-06/PROB` |
| `RM-P06-07` | Centralne twierdzenie graniczne | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-07/PROB` |
| `RM-P06-08` | Entropia (Shannon) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-08/PROB` |
| `RM-P06-09` | Kullback-Leibler Divergence (KL) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-09/PROB` |
| `RM-P06-10` | Cross-Entropy | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P06-10/PROB` |
| `RM-P06-11` | Miary podobieństwa (cosine, L2, L1) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P06-11/LIN` |
| `RM-P06-12` | Teoria informacji w AI | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P06-12/STAT` |
| `RM-P06-13` | Teoria uczenia statystycznego (SLT) | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P06-13/STAT` |
| `RM-P06-14` | VC-dimension | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P06-14/STAT` |
| `RM-P06-15` | Rademacher Complexity | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P06-15/STAT` |
| `RM-P06-16` | Bias-Variance Decomposition | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P06-16/STAT` |
| `RM-P06-17` | Optymalizacja wypukła | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-17/OPT` |
| `RM-P06-18` | Programowanie liniowe | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-18/OPT` |
| `RM-P06-19` | Programowanie kwadratowe | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-19/OPT` |
| `RM-P06-20` | Gradient Descent | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-20/OPT` |
| `RM-P06-21` | Stochastic Gradient Descent (SGD) | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-21/OPT` |
| `RM-P06-22` | Momentum | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-22/OPT` |
| `RM-P06-23` | Nesterov Accelerated Gradient | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P06-23/CALC` |
| `RM-P06-24` | Adam | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P06-24/OPT` |

## Strona 7 — 22 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P07-01` | RMSProp | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-01/OPT` |
| `RM-P07-02` | Adagrad | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-02/OPT` |
| `RM-P07-03` | Optymalizacja nieliniowa | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-03/OPT` |
| `RM-P07-04` | Metody drugiego rzędu (Newton, quasi- Newton) | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P07-04/MATH` |
| `RM-P07-05` | Lagrange Multipliers | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-05/OPT` |
| `RM-P07-06` | Metody projekcyjne | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-06/OPT` |
| `RM-P07-07` | Optymalizacja z ograniczeniami | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-07/OPT` |
| `RM-P07-08` | Meta-optymalizacja (hyperparameter optimization) | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-08/OPT` |
| `RM-P07-09` | Bayesian Optimization | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-09/OPT` |
| `RM-P07-10` | Black-Box Optimization | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-10/OPT` |
| `RM-P07-11` | Teoria gier w AI | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-11/OPT` |
| `RM-P07-12` | Równowaga Nasha w kontekście uczenia | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P07-12/OPT` |
| `RM-P07-13` | Przestrzenie Hilberta w ML | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P07-13/LIN` |
| `RM-P07-14` | Kernel Trick | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P07-14/LIN` |
| `RM-P07-15` | Rozkład Cholesky'ego | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P07-15/LIN` |
| `RM-P07-16` | Whitening (wybielanie danych) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P07-16/LIN` |
| `RM-P07-17` | Transformacje ortogonalne | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P07-17/LIN` |
| `RM-P07-18` | Rzutowanie na podprzestrzeń | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P07-18/LIN` |
| `RM-P07-19` | Manifold Learning (MDS, Isomap) | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P07-19/STAT` |
| `RM-P07-20` | Wariancja i odchylenie standardowe | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P07-20/PROB` |
| `RM-P07-21` | Mutual Information | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P07-21/PROB` |
| `RM-P07-22` | Estymacja maksymalnej wiarygodności | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P07-22/PROB` |

## Strona 8 — 23 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P08-01` | (MLE) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P08-01/PROB` |
| `RM-P08-02` | Wnioskowanie Bayesowskie (Bayesian | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P08-02/PROB` |
| `RM-P08-03` | Inference) | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P08-03/MATH` |
| `RM-P08-04` | Macierz kowariancji | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-04/LIN` |
| `RM-P08-05` | Korelacja Pearsona | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P08-05/PROB` |
| `RM-P08-06` | Testowanie hipotez statystycznych | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P08-06/STAT` |
| `RM-P08-07` | p-value w analizie danych | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P08-07/STAT` |
| `RM-P08-08` | Dystrybuanta | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P08-08/PROB` |
| `RM-P08-09` | Funkcja gęstości prawdopodobieństwa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P08-09/PROB` |
| `RM-P08-10` | Tensory i operacje tensorowe | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-10/LIN` |
| `RM-P08-11` | Iloczyn wektorowy | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-11/LIN` |
| `RM-P08-12` | Iloczyn Hadamarda | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-12/LIN` |
| `RM-P08-13` | Macierz odwrotna i wyznacznik | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-13/LIN` |
| `RM-P08-14` | Ślad macierzy (Trace) | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-14/LIN` |
| `RM-P08-15` | Macierz Jacobiego | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P08-15/LIN` |
| `RM-P08-16` | Ekstrema lokalne i globalne | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P08-16/CALC` |
| `RM-P08-17` | Punkt siodłowy | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P08-17/CALC` |
| `RM-P08-18` | Reguła łańcuchowa (Chain Rule) dla pochodnych | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P08-18/CALC` |
| `RM-P08-19` | Szereg Taylora w aproksymacji funkcji | `omega-calculus` | Pochodna/całka z warunkami istnienia i poprawnym zakresem domen; [M-04] | `RM-P08-19/CALC` |
| `RM-P08-20` | Metody Monte Carlo | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P08-20/PROB` |
| `RM-P08-21` | Łańcuchy Markowa (Markov Chains) | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P08-21/MARKOV` |
| `RM-P08-22` | Procesy stochastyczne | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P08-22/MARKOV` |
| `RM-P08-23` | Filtrowanie Kalmana | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P08-23/MARKOV` |

## Strona 9 — 22 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P09-01` | Transformata Fouriera w przetwarzaniu sygnałów | `omega-numeric` | IEEE/interval proof albo NumericEstimate z jawnie podanym błędem; [M-09] | `RM-P09-01/NUM` |
| `RM-P09-02` | Splot (Convolution) matematyczny | `omega-numeric` | IEEE/interval proof albo NumericEstimate z jawnie podanym błędem; [M-09] | `RM-P09-02/NUM` |
| `RM-P09-03` | Grafy probabilistyczne | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P09-03/MARKOV` |
| `RM-P09-04` | Algorytm Expectation-Maximization (EM) | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P09-04/MARKOV` |
| `RM-P09-05` | Metoda spadku wzdłuż współrzędnych | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-05/OPT` |
| `RM-P09-06` | Regularyzacja Tichonowa (Ridge) | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-06/OPT` |
| `RM-P09-07` | Regularyzacja Lasso | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-07/OPT` |
| `RM-P09-08` | Elastic Net | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-08/OPT` |
| `RM-P09-09` | Optymalizacja roju cząstek (PSO) | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-09/OPT` |
| `RM-P09-10` | Algorytmy genetyczne (podstawy matematyczne) | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-10/OPT` |
| `RM-P09-11` | Symulowane wyżarzanie (Simulated | `omega-math` | Jawny typ wejścia/wyjścia, warunki domenowe i test negatywny; [M-02] | `RM-P09-11/MATH` |
| `RM-P09-12` | Annealing) | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P09-12/OPT` |
| `RM-P09-13` | Teoria grafów w AI | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P09-13/GRAPH` |
| `RM-P09-14` | Laplasjan grafu | `omega-graphs,omega-model-check` | Skończony graf, reachability/shortest-path witness i preconditions; [M-05] | `RM-P09-14/GRAPH` |
| `RM-P09-15` | Macierz sąsiedztwa | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P09-15/LIN` |
| `RM-P09-16` | Wektoryzacja obliczeń | `omega-linear` | Typowane wymiary i świadectwo algebry dokładnej lub numeryczny residual bound; [M-03] | `RM-P09-16/LIN` |
| `RM-P09-17` | Precyzja numeryczna (FP32, FP16, BF16) | `omega-numeric` | IEEE/interval proof albo NumericEstimate z jawnie podanym błędem; [M-09] | `RM-P09-17/NUM` |
| `RM-P09-18` | Błędy zaokrągleń w uczeniu | `omega-numeric` | IEEE/interval proof albo NumericEstimate z jawnie podanym błędem; [M-09] | `RM-P09-18/NUM` |
| `RM-P09-19` | Stabilność numeryczna algorytmów | `omega-numeric` | IEEE/interval proof albo NumericEstimate z jawnie podanym błędem; [M-09] | `RM-P09-19/NUM` |
| `RM-P09-20` | Matematyczne podstawy AGI | `omega-research` | Nie rościć rozstrzygnięcia hipotezy; wyniki jedynie ze sprawdzonym kompletnym dowodem; [M-12] | `RM-P09-20/META-OPEN` |
| `RM-P09-21` | Hipoteza Riemanna | `omega-research` | Nie rościć rozstrzygnięcia hipotezy; wyniki jedynie ze sprawdzonym kompletnym dowodem; [M-12] | `RM-P09-21/META-OPEN` |
| `RM-P09-22` | Hipoteza Hilberta-Pólyi | `omega-research` | Nie rościć rozstrzygnięcia hipotezy; wyniki jedynie ze sprawdzonym kompletnym dowodem; [M-12] | `RM-P09-22/META-OPEN` |

## Strona 10 — 8 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P10-01` | Hipoteza Hodge'a | `omega-research` | Nie rościć rozstrzygnięcia hipotezy; wyniki jedynie ze sprawdzonym kompletnym dowodem; [M-12] | `RM-P10-01/META-OPEN` |
| `RM-P10-02` | P = NP | `omega-research` | Nie rościć rozstrzygnięcia hipotezy; wyniki jedynie ze sprawdzonym kompletnym dowodem; [M-12] | `RM-P10-02/META-OPEN` |
| `RM-P10-03` | Logika wnioskowania automatycznego | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P10-03/LOG` |
| `RM-P10-04` | Wnioskowanie dedukcyjne | `omega-agent,omega-kernel` | Jednoznacznie rozróżnij dedukcję, abdukcję, estymatę i heurystykę; [M-11] | `RM-P10-04/REASON` |
| `RM-P10-05` | Wnioskowanie indukcyjne | `omega-agent,omega-kernel` | Jednoznacznie rozróżnij dedukcję, abdukcję, estymatę i heurystykę; [M-11] | `RM-P10-05/REASON` |
| `RM-P10-06` | Wnioskowanie abdukcyjne | `omega-agent,omega-kernel` | Jednoznacznie rozróżnij dedukcję, abdukcję, estymatę i heurystykę; [M-11] | `RM-P10-06/REASON` |
| `RM-P10-07` | Wnioskowanie probabilistyczne | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P10-07/PROB` |
| `RM-P10-08` | Przeszukiwanie przestrzeni stanów | `omega-agent,omega-kernel` | Jednoznacznie rozróżnij dedukcję, abdukcję, estymatę i heurystykę; [M-11] | `RM-P10-08/REASON` |

## Strona 11 — 6 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P11-01` | Algorytmy heurystyczne | `omega-agent,omega-kernel` | Jednoznacznie rozróżnij dedukcję, abdukcję, estymatę i heurystykę; [M-11] | `RM-P11-01/REASON` |
| `RM-P11-02` | Funkcje kosztu | `omega-kernel,omega-logic` | Poprawne typowanie, kontekst Γ, kernel certificate lub Unknown; [M-05] | `RM-P11-02/LOG` |
| `RM-P11-03` | Optymalizacja gradientowa | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P11-03/OPT` |
| `RM-P11-04` | Optymalizacja stochastyczna | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P11-04/OPT` |
| `RM-P11-05` | Algorytmy ewolucyjne | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P11-05/OPT` |
| `RM-P11-06` | Algorytmy genetyczne | `omega-optimization` | Primal/dual certificate lub CandidateOnly z limitem iteracji; [M-08] | `RM-P11-06/OPT` |

## Strona 12 — 8 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P12-01` | Entropia Shannona | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P12-01/PROB` |
| `RM-P12-02` | Divergencja Kullbacka-Leiblera (KL) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P12-02/PROB` |
| `RM-P12-03` | Walidacja krzyżowa (Cross-Validation) | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P12-03/STAT` |
| `RM-P12-04` | Twierdzenie Bayesa | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P12-04/PROB` |
| `RM-P12-05` | Estymacja maksymalnej wiarygodności (MLE) | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P12-05/PROB` |
| `RM-P12-06` | VC-wymiar (Vapnik-Chervonenkis) | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P12-06/STAT` |
| `RM-P12-07` | PAC Learning (Probably Approximately Correct) | `omega-prob,omega-ml-contracts` | Jawne założenia losowania/modelu; wynik bound albo estimate, nie theorem o świecie; [M-06] | `RM-P12-07/STAT` |
| `RM-P12-08` | Prawo wielkich liczb | `omega-prob` | Prawidłowa przestrzeń miary, support i normalizacja, jawne założenia; [M-06] | `RM-P12-08/PROB` |

## Strona 13 — 6 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P13-01` | Modele probabilistyczne | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P13-01/MARKOV` |
| `RM-P13-02` | Sieci Bayesowskie | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P13-02/MARKOV` |
| `RM-P13-03` | Modele Markowa | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P13-03/MARKOV` |
| `RM-P13-04` | Ukryte modele Markowa (HMM) | `omega-prob-graphs` | Normowane przejścia/emisje; exact na małym modelu, estimated na dużym; [M-07] | `RM-P13-04/MARKOV` |
| `RM-P13-05` | Modele generatywne podstawowe | `omega-ml-contracts` | Obliczyć typy, Jacobian/operator, jawne warunki aktywacji i numeryczną otoczkę; [M-10] | `RM-P13-05/NN` |
| `RM-P13-06` | Modele dyskryminacyjne | `omega-ml-contracts` | Obliczyć typy, Jacobian/operator, jawne warunki aktywacji i numeryczną otoczkę; [M-10] | `RM-P13-06/NN` |

## Strona 14 — 4 pozycji

| ID | Pojęcie z PDF | Moduł | Kontrakt / niezbędny sprawdzian | Test |
|---|---|---|---|---|
| `RM-P14-01` | Teoria perceptronu | `omega-ml-contracts` | Obliczyć typy, Jacobian/operator, jawne warunki aktywacji i numeryczną otoczkę; [M-10] | `RM-P14-01/NN` |
| `RM-P14-02` | Funkcje aktywacji | `omega-ml-contracts` | Obliczyć typy, Jacobian/operator, jawne warunki aktywacji i numeryczną otoczkę; [M-10] | `RM-P14-02/NN` |
| `RM-P14-03` | Nieliniowe funkcje aktywacji | `omega-ml-contracts` | Obliczyć typy, Jacobian/operator, jawne warunki aktywacji i numeryczną otoczkę; [M-10] | `RM-P14-03/NN` |
| `RM-P14-04` | Backpropagation (Propagacja wsteczna) | `omega-ml-contracts` | Obliczyć typy, Jacobian/operator, jawne warunki aktywacji i numeryczną otoczkę; [M-10] | `RM-P14-04/NN` |

## Kontrola liczności i zakresu

- **14 / 14 stron** ujętych; **239** wystąpień pojęć (z zachowaniem powtórzeń).
- Liczba pozycji w tym spisie jest kontrolowana przez skrypt budujący na podstawie lokalnej kopii oryginalnego PDF. Wpisy na stronach 10–14, zawierające wielowierszowe definicje, przepisano jako osobne nagłówki terminów.
- Przejście do `VERIFIED` wymaga dla każdej pozycji konkretnego zestawu testów i artefaktu z CI; samo przypisanie modułu nie stanowi dowodu działania.

### Rozkład grup

| Grupa | Wystąpienia |
|---|---:|
| `CALC` | 22 |
| `GRAPH` | 11 |
| `LINEAR` | 53 |
| `LOGIC` | 14 |
| `MARKOV` | 12 |
| `MATH` | 7 |
| `NN` | 6 |
| `NUM` | 5 |
| `OPEN` | 5 |
| `OPT` | 31 |
| `PROB` | 57 |
| `REASON` | 5 |
| `STAT` | 11 |

## Dodatkowe ograniczenia poprawności

- Kategoria przypisana słownikowo jest **indeksem organizacyjnym** i nie definiuje matematycznego znaczenia pojęcia. Przykładowo `Gradient Descent` to moduł optymalizacji, nie sama operacja różniczkowania.
- Jeśli termin jest złożony (np. „matematyczne podstawy AGI”), jego pełna semantyka musi zostać określona w ADR; domyślnie oznaczyć `RESEARCH` bez obietnicy formalizacji wszystkiego.
- Kategorie połączone, np. rachunek całkowy w probabilistyce, wymagają dwóch kontraktów: calculus i probabilistic measure. Nie dowodzić twierdzeń statystycznych przez samą arytmetykę.
- Sformułowania i definicje z PDF są zachowane jako źródło, natomiast architektura/kontrakty/testy to autorskie rozszerzenie.