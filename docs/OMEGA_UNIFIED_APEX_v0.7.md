# OMEGA Unified APEX — kontrakt architektoniczny v0.7

**Repozytorium:** `mojealterego/ImandraX-DGM-` · **Gałąź:** `main` · **Produkt:** jeden wspólny silnik ImandraX × DGM × RSI Ω.

## Cel

APEX jest warstwą sterowania, stanem operacyjnym i rejestrem możliwości dla jednego, rozbudowywanego systemu. Przygotowuje kontrakty pozwalające w przyszłości integrować około dziesięciu dodatkowych silników **bez** włączania ich kodu, narzędzi ani uprawnień do procesu autonomicznego w chwili odczytania manifestu. Dopiero audytowana integracja konkretnego modułu i zgoda właściciela umożliwią jego montaż.

Termin „cyfrowy byt” w tej dokumentacji oznacza **ciągłość tożsamości instancji, pamięć zdarzeń, deterministyczne zachowanie, kontrolowany cykl życia, możliwość uczenia się poprzez odrębny proces badań i zdolność komunikacji między modułami**. Nie stanowi deklaracji świadomości, osobowości prawnej ani sentiencji.

## Zaimplementowane w v0.7

1. **EngineManifest/Capability**: wersjonowane, typowane deskryptory; przestrzenie nazw, listy zależności, deterministyczna kolejność inicjalizacji, wykrywanie cykli i konfliktów. Rejestr zamraża się przed użyciem. `apex_manifest.py` przyjmuje tylko ograniczony, ścisły JSON; nie wykonuje Python ani nie instaluje zależności.
2. **Jawny montaż portów**: zatwierdzony kod aplikacji wiąże deskryptor z konkretną funkcją. Niezwiązany port nie działa. Integracje `imandrax.math`, `imandrax.formal`, `dgm.history` prowadzą do istniejącego `IntegratedEngine`; `rsi.proposals` pozostaje niewiązany, aby nie tworzyć alternatywnej drogi do LLM, GitHub czy wdrożeń.
3. **Tożsamość i stan**: lokalnie generowany trwały `identity_id`, FSM `CREATED → ACTIVE ↔ PAUSED → STOPPED`, przechowywane w SQLite. Po restarcie aplikacja odzyskuje stan i nie samoczynnie uruchamia zatrzymanej instancji.
4. **Audyt**: append-only trigger SQLite i łańcuch SHA-256 z czasem UTC, odciskiem wejścia i wyniku. Raw input/output i klucze nie trafiają do dziennika. Weryfikacja odtwarza historię stanu. To ochrona przed przypadkową zmianą, **nie zewnętrzny WORM ani dowód przeciw administratorowi hosta**.
5. **Owner-signed manifest epoch**: jeśli dodajemy kolejny silnik, `manifest_digest` jest zmieniany dopiero po zatrzymaniu działania do stanu `PAUSED` i podpisaniu kanonicznego komunikatu przez klucz Ed25519 właściciela. Weryfikowany jest wcześniej przypięty publiczny odcisk klucza. Ręczne odtworzenie podpisu nie pozwala na replay przy innym epoch. Dla instancji bez przypiętego klucza migracja jest zablokowana.
6. **Deny-by-default dispatcher**: z portów można uruchamiać wyłącznie odczyt lub odseparowane badania włączane świadomie. `MUTATION`, `AUTHORITY`, self-approval, auto-merge, deploy, shell i dynamiczny import są zabronione. Limit 16 KiB żądania, 64 KiB wyniku; walidacja kanonicznego JSON. Identyfikatory żądań chronią przed powtórnym zaakceptowaniem tego samego rekordu.
7. **ApexFlow**: wieloetapowy, deterministyczny graf działań do 32 węzłów, walidowany w całości **przed** wykonaniem. Nie interpoluje odpowiedzi modeli w kod, nie podnosi uprawnień i nie wykonuje zmian repozytorium.
8. **Operacyjny CLI**: `imandrax-apex` to dodatkowe wejście do *tego samego pakietu*, nie niezależny silnik. Umożliwia odczyt manifestów, status, aktywację/pauzę/zatrzymanie, kontrolę audytu oraz (w istniejącym stanie ImandraX) wywołania matematyczne i odczyt genealogii DGM.

## Model zaufania

```text
Użytkownik / podpis poza agentem
           │
           ▼
  Operator + niezależna authority (istniejące RSIReviewStore)
           │ zaufanie NIE jest delegowane do APEX
           ▼
 [ Manifest epoch / APEX identity / capability registry ]
           │ tylko porty READ / opt-in RESEARCH
     ┌─────┼─────────┐
     │     │         │
  ImandraX DGM       RSI proposer (port niewiązany)
  math     genealogy  │
     └─────┴──────────┘
       │ audit: hash-chain, wyniki tylko badawcze
       ▼
  zero automatycznego merge, release, self-approval
```

**Zastrzeżenia:** manifest nie jest podpisanym pakietem wykonywalnym; `bind` jest wyłącznie lokalnym interfejsem kodu zaufanej aplikacji. Prawdziwa izolacja nieufnego kodu jest w oddzielnym Docker/VM, nie w `ApexRegistry`. SQLite może zostać wymieniony przez administratora z dostępem do plików. Do odpornej na przejęcie infrastruktury potrzebny jest HSM/KMS, WORM i atestacja z niezależnego hosta.

## Kontrakt dla następnych silników (brak automatycznego montowania)

```json
{
  "engine_id": "example-engine",
  "version": "1.0.0",
  "dependencies": ["imandrax"],
  "capabilities": [
    {"name":"example-engine.inspect","access":"READ","input_fields":["query"]}
  ]
}
```

Każdy kolejny moduł wymaga jawnego rekordu `EngineManifest`, zdefiniowanych typów danych, audytu licencji, polityki uprawnień, analizy granic zaufania, walidacji wejścia/wyjścia, testów błędów, mierzalnych kryteriów ukończenia oraz podpisanej migracji manifestu. **Nawet prawidłowy manifest jest tylko opisem możliwości.** Nie jest automatycznie uruchamiany ani instalowany.

## Uruchomienie lokalne

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/test_apex_v07.py
# katalog stanu musi znajdować się poza drzewem repozytorium
imandrax-apex --root "$PWD" --state-dir /var/lib/imandrax-apex status
imandrax-apex --root "$PWD" --state-dir /var/lib/imandrax-apex manifests
imandrax-apex --root "$PWD" --state-dir /var/lib/imandrax-apex start
imandrax-apex --root "$PWD" --state-dir /var/lib/imandrax-apex math --operation gcd --arguments '{"a":84,"b":18}'
imandrax-apex --root "$PWD" --state-dir /var/lib/imandrax-apex verify
imandrax-apex --root "$PWD" --state-dir /var/lib/imandrax-apex pause
```

CLI nie uruchamia usług sieciowych ani nie potwierdza 24/7. Przykładowe `/var/lib/...` wymaga rzeczywistych uprawnień do zapisu na hoście i zbudowanego indeksu matematyki, jeżeli potrzebne jest odpytywanie źródeł.

## Bramy blokujące produkcję (nie wolno oznaczyć jako ukończonych)

- Niezależny serwer zatwierdzania na **rzeczywistym drugim hoście**, z własnym TLS 1.3 i wydzielonym kluczem podpisującym w HSM/KMS, wraz z testem odmowy przy braku podpisu.
- Ochrona `main` przez ruleset, wymuszony CI, wyłączenie obejść i role właściciela. `CODEOWNERS` bez Ruleset nie wystarcza.
- Proces RSI uruchomiony 24/7 przez docelowego operatora; model, API, stałe koszty, monitoring, retry i awaryjny kill switch.
- Weryfikator całej biblioteki Mathlib niezależnymi jądrami na serwerze z odpowiednią pamięcią, z opublikowanymi artefaktami i podpisem niezależnego runnera. Zestaw własnych dowodów i pełna kompilacja nie dowodzą formalizacji wszystkich dziedzin matematyki.
- Testy E2E na Firecracker/no-net i zewnętrzny audyt bezpieczeństwa wielodzierżawności.
- Osobne polityki prywatności, retencji, wymazywania pamięci i świadomej zgody przed przechowywaniem danych osobistych.

## Kierunek dalszych prac

Przed scaleniem następnego silnika należy zakończyć powyższe bramki, zarejestrować wyniki w `docs/ROADMAP.md` i pozostawić jeden `main`. **Status PROVED_STRICT wymaga prawdziwego dowodu sprawdzonego przez niezależne jądro dla konkretnej deklaracji; nie może wynikać z liczby MSC czy wyniku LLM.**
