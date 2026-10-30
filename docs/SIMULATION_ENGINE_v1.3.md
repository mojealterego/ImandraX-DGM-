# Silnik symulacyjny v1.3

`imandrax-dgm simulate` jest uruchamialną ścieżką całego istniejącego silnika:
MSC → ProposalGenerator → ResearchCycle → ocena → ResearchArchive →
wiązanie patcha i SHA → RSIReviewStore w stanie PROPOSED. Ponowne utworzenie
IntegratedEngine między cyklami sprawdza trwałość genealogii SQLite.

## Uruchomienie bez infrastruktury

```bash
python -m pip install -e '.[test]'
imandrax-dgm --root . simulate --output /tmp/imandrax-sim
```

Wymagany jest checkout Git z katalogiem `data` i `research/solver.py`, także
przy instalacji wheel. Nie są potrzebne klucze LLM ani usługa authority.
`--generations 1|2` ogranicza liczbę cykli. Nowy katalog poza repozytorium
chroni istniejące wyniki; ponowne uruchomienie wymaga nowej ścieżki.

Proposer jest deterministycznym scenariuszem: błędny solver zwracający None,
algorytm Euklidesa i iteracyjne potęgowanie, następnie potęgowanie binarne.
Nie jest to trenowanie modelu ani dowód samodoskonalenia. Tryb `reference`
porównuje dokładne źródła ze skończoną listą wbudowanych implementacji i wywołuje
zaufaną funkcję. Obcy kod jest odrzucany bez wykonania. Nie jest to sandbox.

## Rzeczywiste wykonanie w Docker

```bash
docker pull python:3.12-slim
SIM_IMAGE=$(docker image inspect python:3.12-slim --format '{{index .RepoDigests 0}}')
imandrax-dgm --root . simulate --backend docker --image "$SIM_IMAGE" \
  --output /tmp/imandrax-sim-docker
```

Obraz jest przypięty przez digest. Wykonawca stosuje brak sieci, read-only,
użytkownika 65534, usunięte capabilities i limity zasobów. Kopia zaufanego
worker.py jest czytelna dla użytkownika kontenera, bez zmiany uprawnień pliku
źródłowego. Błąd wykonania nie powoduje cichego przełączenia na tryb reference.
Tryb Docker także używa scenariusza zamiast LLM. Nie zastępuje microVM.

## Raport i zakres dowodów

- Każdy cykl: 30 przypadków regresji i 45 przypadków selekcji na kandydata.
- Osobny korpus 300 przypadków: API dokładnej arytmetyki i obie poprawne funkcje.
- Kontrola odrzucenia błędnego kandydata, genealogii, dziennika i braku autoryzacji.
- `report.json`: status SIMULATION_PASS lub SIMULATION_FAIL; kod wyjścia 0 lub 1.
- Artefakty generacji: propozycja, patch, metryki i źródła wraz z SHA-256.
- Główny SHA256SUMS obejmuje raport, indeks, bazy i artefakty generacji.

Korpusy i ziarna są publiczne, a testy skończone. Wyniki są dowodami empirycznymi
w zakresie scenariusza; nie są dowodem formalnym twierdzeń ani niezależną
atestacją. Nie potwierdzają produkcyjnego hostingu, HSM/WORM, zewnętrznego
signera ani ogólnej inteligencji. `release_authorized` pozostaje false.

CI odtwarza tryb referencyjny, rzeczywisty Docker oraz instalację z wheel.
Pełne wdrożenie zewnętrzne i pozostałe otwarte pozycje roadmap nie są zamknięte
przez wynik tej symulacji.

## Lokalna walidacja 2026-10-30

218 testów PASS; zbudowano wheel i sdist 1.3.0; wykonano pełną symulację
z wheel w nowym virtualenv. Tryb reference i rzeczywisty Docker: SIMULATION_PASS,
300/300 przypadków API oraz 300/300 dla każdego z dwóch solverów transferowych.
MuJoCo 3.3.6: 200 kroków, wynik powtarzalny. Lean w tej sesji nie uruchamiano.

Raporty w [evidence/v1.3](../evidence/v1.3/) zapisują faktyczne base_commit
oraz hashe plików implementacji, również dla przebiegu wykonanego przed commitem.
Raport build wskazuje commit implementacji. To lokalne, niepodpisane evidence;
wyniki GitHub CI należy odczytać osobno po push.
