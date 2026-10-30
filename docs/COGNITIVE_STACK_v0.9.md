# OMEGA Cognitive Stack v0.9 — ImandraX × DGM × RSI Ω

**Zakres:** ta sama aplikacja / ten sam pakiet; `main` pozostaje jedyną gałęzią docelową. Nie zmieniono istniejącego podpisywanego zestawu manifestów APEX, ponieważ wymaga to zgody właściciela i migracji w stanie PAUSED.

## Ugruntowanie i architektura

- **CoALA:** Theodore Sumers et al., *Cognitive Architectures for Language Agents*, https://arxiv.org/abs/2309.02427 — pamięć i cykl decyzji są różnymi modułami.
- **Generative Agents:** Park et al., 2023, https://arxiv.org/abs/2304.03442 — obserwacja, refleksja i planowanie. `derive_summary` implementuje wyłącznie deterministyczny zapis z referencjami, nie generatywną inferencję LLM.
- **JEPA:** https://github.com/mojealterego/awesome-jepa — katalog literatury (CC BY 4.0), NIE wytrenowany model ani embeddingi. Bez importu kodu lub wag.
- **R2-Reasoner:** https://github.com/tsinghua-fib-lab/R2-Reasoner — model-router (MIT); nasza `route_subtasks` to odrębny, ograniczony planner offline bez wytrenowanego R2 lub wywołań API. Wyników benchmarków autorów nie przenosimy na ImandraX.
- Pinned source metadata: `data/research_sources_v09.json`. Nie dodajemy zewnętrznego R2 do katalogu 701 forków użytkownika, który jest osobną migawką.

## Faktycznie zaimplementowane

| Potrzeba | Kontrakt i moduł | Stan |
|---|---|---|
| Bitemporal store | `BitemporalGraphMemory.put/query`, `valid_from/valid_to`, `recorded_at`, `as_of_seq` | LOCAL SQLITE |
| Bitemporal graph / Knowledge Graph | `kind=EDGE`, `graph(subject,...)` i filtr tenantu | LOCAL GRAPH FACTS; brak grafowego DB / GraphRAG |
| CoALA / General / Working / Long-term memory | Trwałe typy `WORKING`, `SEMANTIC`, `GENERAL`, `PROCEDURAL`; `query(limit)` | TYPED STORE; brak automatycznej retencji i osobnego zarządzania working-memory |
| Episodic / Retrospective correction | `EPISODIC` + `REFLECTION`, `reflect()` | OPERATOR INPUT ONLY |
| Generative memory | `derive_summary` z provenance i `verified=false` | DETERMINISTIC SUMMARY, nie LLM generation |
| Self correction / Reflexion loop | `reflect` zapisuje niezatwierdzoną korektę `applied=false` | NO AUTOMATIC UPDATE |
| Point-in-time recovery | `checkpoint()`, `clone_at(dest,as_of_seq)` | LOGICAL COPY; bez podmiany live store |
| Graph of Thoughts | `GraphOfThoughts` waliduje 32-węzłowy DAG i porządek | DATA-ONLY DAG |
| Decision cycle / Cognitive modulation | `CognitiveDecisionCycle.decide` waży jawne atrybuty | ADVISORY ONLY; bez wykonania akcji |
| Digital genotype / Mutation loop / Fitness function | `DigitalGenotype`, `mutation_loop`, `fitness` | 4 allowlisted parametry, bez zmiany kodu |
| DGM Engine / AlphaEvolve | Dotychczasowy `ResearchCycle` + `ResearchArchive` | EXISTING BOUNDED RESEARCH; bez automatycznego mergowania |
| R2 routing | `route_subtasks`, ograniczone wyszukiwanie beam-256 | OFFLINE RESEARCH ADAPTER; bez RL/treningu |
| JEPA / World model | Rejestr źródeł, brak runtime wag | NOT IMPLEMENTED |
| Holographic memory | Brak specyfikacji właściwości i testów | NOT IMPLEMENTED |
| Shimi Index | Niejednoznaczna nazwa; brak jednoznacznej specyfikacji | NOT IMPLEMENTED |

## Semantyka czasu i korekty

Dla faktu `f` przechowujemy `valid_from <= t_valid < valid_to` i moment zaobserwowania `recorded_at <= t_system`. Zawsze wybierana jest najnowsza rewizja faktu **widoczna w danym czasie systemowym**, a dopiero potem sprawdzana jej ważność. Wsteczna korekta nie usuwa wcześniejszego stanu wiedzy. `expected_seq` gwarantuje optimistic concurrency, `request_id` idempotencję, append-only triggery ograniczają przypadkową mutację.

Przykład operatora:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
# w input.json: {"tenant":"lab","fact_id":"observation-1","kind":"EPISODIC",
# "subject":"engine","predicate":"observed","value":{"result":"pass"},
# "valid_from":"2026-10-30T00:00:00Z","request_id":"run-1","provenance":"operator"}
imandrax-dgm --root . cognitive --state-dir /tmp/imandrax-cognitive \
  --op remember --payload-file ./input.json
# odczyt: podaj osobny JSON z tenant i valid_at
imandrax-dgm --root . cognitive --state-dir /tmp/imandrax-cognitive \
  --op recall --payload-file ./query.json
```

`cognitive` wykonuje tylko jawne polecenia lokalnego operatora. Nie daje RSI dostępu do pamięci bez polityki, nie podpina portu APEX i nie przejmuje jego klucza podpisującego.

## Ograniczenia produkcyjne

1. SQLite bez zewnętrznego WORM, KMS, szyfrowania at-rest i atestacji. Administrator hosta może usunąć triggery; hash-chain wykrywa zmianę treści w istniejącym ciągu, lecz nie gwarantuje wykrycia wymazania całej bazy. Potrzebne są podpisane checkpointy poza hostem.
2. Granica tenantu jest filtrem zapytań: sama biblioteka zakłada zaufanego operatora, a **nie** pełną autoryzację użytkowników/API. Wystawienie jej sieciowo wymaga ACL/RBAC, uwierzytelnienia, kluczy tenantów i szyfrowania.
3. Nie ma automatycznego TTL, usuwania danych osobowych, embeddingów, JEPA, GraphRAG, wektorowego wyszukiwania, prawdziwej pamięci holograficznej, reprodukowalnego benchmarku routera ani uruchomionych na GPU modeli.
4. Żaden oceniony `DigitalGenotype` ani decyzja/plan nie może samoczynnie mutować repozytorium, wywołać shell, zatwierdzić zmian RSI ani wdrożyć kodu.
5. Podłączenie nowych capability do `ApexRegistry` wymaga osobnej podpisanej migracji epoki z zachowaniem trwałej tożsamości. NIE nadpisywać bazy istniejącej instancji nowym digestem.

## Testy

`tests/test_cognitive_memory_v09.py`, `test_cognition_v09.py`, `test_adaptive_evolution_v09.py`, `test_cognitive_cli_v09.py`: czas historyczny, korekta, tenant, graph, konflikty, idempotencja, uszkodzenie łańcucha, clone PIT, pętla mutacji bez auto-apply, cykle DAG, ograniczony routing i CLI. Wyniki po uruchomieniu GitHub Actions należy odnotować w ROADMAP, nie wywodzić sukcesu z samej obecności kodu.
