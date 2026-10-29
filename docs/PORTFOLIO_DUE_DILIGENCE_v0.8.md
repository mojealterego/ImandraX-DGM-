# OMEGA Unified APEX — portfolio due diligence v0.8

**Zakres:** jeden produkt ImandraX × DGM × RSI Ω, gałąź main; wstępny audyt metadanych i plików root. Bez montażu nowych silników.

## Dane i poziom dowodów

- `data/repositories_public_701.tsv`: istniejący katalog 701 publicznych repozytoriów. Trzy prywatne pozycje z historycznego zestawienia nie są ujawniane.
- `data/portfolio_root_evidence_v1.json`: 18 odczytanych README i 15 odczytanych plików licencyjnych, z blob SHA-1 uzyskanymi z GitHub 2026-10-30. Blob SHA pliku nie jest przypięciem commitu ani audytem drzewa.
- `src/imandrax_dgm/portfolio.py`: ścisły parser, walidacja źródeł, deterministyczne raportowanie.
- `imandrax-dgm --root . portfolio --limit 20`: raport JSON bez uruchamiania obcego kodu.

## Granice zaufania

Metadane repozytorium oraz README służą wyłącznie selekcji kandydatów. Marker licencji to klasyfikacja wstępna pliku, a nie ocena zgodności prawnej, zależności czy licencji poszczególnych zasobów.

Raport **zawsze** wskazuje `NOT_INTEGRATED` oraz wymagane bramki: pin SHA commitu, niezależny audyt źródeł i bezpieczeństwa, licencje, SBOM, reprodukowalne testy, izolowany adapter E2E oraz podpis właściciela dla migracji epoki APEX. Żaden plik evidence nie może samodzielnie podnieść uprawnień, zatwierdzić RSI, zamontować portu ani wykonać merge/deploy.

## Kolejność

1. Najpierw zamknąć istniejące bramki Lean/checker, zewnętrznej authority, Ruleset main, izolacji i E2E.
2. Priorytety P0/P1 wyznaczają kolejność audytu, nie kolejność automatycznego importowania kodu.
3. RSIAI0 i podobne systemy self-modification pozostają niezaufanymi referencjami badawczymi.
4. Nowy adapter wymaga audytu i podpisanej migracji manifestu bez zmiany tożsamości instancji.

**Ograniczenie:** nie jest to audyt całego kodu 701 repozytoriów ani potwierdzenie, że większość z nich można bezpiecznie zintegrować.
