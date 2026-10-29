# Ochrona `main` w modelu pracy wybranym przez właściciela

**Decyzja właściciela 2026-10-29:** rozwój kodu zlecany bezpośrednio odbywa się **na `main`**, bez obowiązkowego tworzenia dodatkowych gałęzi i PR. Dotychczasowe instrukcje „PR dla każdej zmiany” są w tym zakresie nieaktualne.

**Ważne rozróżnienie:** autonomiczny RSI **nigdy nie dostaje tokenu zapisu do repozytorium**. Proponuje i testuje kod w izolacji, a użytkownik podpisuje osobną decyzję. Nie ma API automatycznego zastosowania zmian. Właściciel może następnie osobiście wdrożyć zatwierdzony patch do `main`, po niezależnym sprawdzeniu bazowego SHA i pełnych testach.

## Rekomendowana konfiguracja w Settings → Rules → Rulesets

1. Target: `main`; **block force pushes and deletions**.
2. Wymagaj podpisanych commitów, jeśli obsługiwane, oraz włącz skanowanie sekretów i Dependabot.
3. Nie przyznawaj botom RSI, LLM ani wykonawcom Docker tokenów `contents:write`, `workflows:write` lub `administration:write`.
4. Dla bezpośrednich zmian właściciela ustal świadomą, ograniczoną regułę dostępu/bypass zgodną z dostępnym planem GitHub. Bez tego reguła „PR required” może blokować żądany tryb pracy bezpośrednio na `main`.
5. Testy GitHub Actions (`unit-and-negative`, `isolated-docker-e2e`, `mujoco-physics-e2e`, `lean-proof-kernel`) muszą przejść po zmianie. W trybie direct-push status checks nie zastępują niezależnej akceptacji RSI.
6. Utrzymuj podpis użytkownika Ed25519 **poza GitHub Actions i repozytorium**. Sprawdzaj manifest, policy digest, patch SHA, bazowy SHA, 4 podpisane suites i termin ważności.
7. **Nigdy nie włączaj automatycznego apply/merge/deploy**, nawet po przejściu testów.

**Stan weryfikowany przed zmianą:** `main` raportował `protected: false`, Rulesets były puste. GitHub App nie miał uprawnień administracyjnych do konfiguracji ochrony. Nie twierdzimy, że reguły zostały włączone.