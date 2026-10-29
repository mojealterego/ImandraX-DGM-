# Wymagana ochrona `main` — ręczna konfiguracja właściciela

**Stan na 2026-10-29:** GitHub API zwraca `rulesets: []`, a `branches/main` raportuje `protected: false`. Dostęp GitHub App nie pozwala odczytać/zmienić ochrony branchy (HTTP 403). **Żadna polityka nie została ustawiona automatycznie.**

Otwórz `https://github.com/mojealterego/ImandraX-DGM-/settings/rules`, utwórz **New branch ruleset**:

1. Name: `imandrax-main-human-review`; enforcement: **Active**; target branches: `main` (dokładny wzorzec).
2. Require a pull request before merging: **ON**; minimum approvals **1**; **require review from Code Owners**; **dismiss stale approvals**; **require approval of the most recent reviewable push**.
3. Require status checks: **ON**, wymagane `unit-and-negative`, `isolated-docker-e2e`, `mujoco-physics-e2e`, `lean-proof-kernel` po ich pierwszym wykonaniu. Preferuj wymagane źródło GitHub Actions dla każdego checka.
4. Block force pushes and branch deletions. Require conversation resolution. Nie przyznawaj botom ani aplikacjom uprawnień bypass. Nie wyłączaj reguły dla administratorów, jeśli nie jest to konieczne do odzyskiwania dostępu.
5. Zweryfikuj na niechronionej gałęzi testowej, że PR bez zatwierdzenia i PR z niezaliczonym CI nie mogą być scalone.
6. Oddzielnie utrzymuj **podpisaną decyzję Ed25519** w zewnętrznym RSI Approval Authority. GitHub review nie zastępuje kryptograficznego podpisu, a podpis nie zastępuje GitHub review.
7. Dopiero po aktywacji ochrony, konfiguracji sekretów i zaakceptowaniu kodu w PR ustaw zmienną repozytorium `RSI_CYCLE_ENABLED=true`. Harmonogram zacznie działać dopiero z workflow w domyślnej gałęzi.

**Uwaga:** w repozytorium należącym do indywidualnego konta część opcji rulesets może zależeć od planu i widoczności. Jeśli GitHub nie udostępnia wymaganej ochrony, traktuj automatyczną promocję zmian jako zabronioną; przejdź na ręczną procedurę PR.