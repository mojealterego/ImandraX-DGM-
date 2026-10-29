# Macierz integracyjna ImandraX × DGM × RSI Ω

| ID | Wymaganie ze specyfikacji | Kod / źródło | Weryfikacja | Stan |
|---|---|---|---|---|
| IM-01 | MSC2020 63 klasy | `scripts/build_msc_class_index.py`, `docs/MSC2020_63_CLASS_ROUTING.md` | Test 63 klas | IMPLEMENTED CLASS BOOTSTRAP |
| IM-02 | 6006 kodów szczegółowych MSC2020 | `data/msc2020_6006_coverage.csv`, `scripts/build_msc_full_index.py` | Test FTS5 6006 rekordów | IMPLEMENTED CLASSIFICATION ONLY; 19 114 EXTERNAL |
| IM-03 | 239 wymagań z 14 stron | `docs/blueprints/IMANDRAX_MATH_PDF_TRACEABILITY_14_PAGES.md` | Zapis planu | SPECIFIED, NOT ALL IMPLEMENTED |
| IM-04 | Katalog 704 repozytoriów | `data/repositories_public_701.tsv` + raport wcześniejszy | Test 701 publicznych, 3 prywatne wyłączone | METADATA ONLY |
| IM-05 | Exact bounded arithmetic | `engine.py::math` | `test_integrated_engine_v04.py` | IMPLEMENTED LIMITED |
| IM-06 | Formalne dowodzenie | `proofs/ImandraX/{Basic,Arithmetic}.lean`, Lean kernel CI | CI GitHub po push | SMALL FORMAL SUBSET ONLY |
| IM-07 | Symulacja MuJoCo | `scripts/mujoco_smoke.py` | CI GitHub po push | LIMITED SMOKE |
| DGM-01 | Generacja wariantów kodu | `generator.py` | Testy generatora | IMPLEMENTED LIMITED TO ONE FILE |
| DGM-02 | Empiryczna ocena wariantów | `cycle.py`, `sandbox.py` | Testy, Docker CI | IMPLEMENTED RESEARCH ONLY |
| DGM-03 | Quality/novelty ranking | `generator.py::score_population` | Testy jednostkowe | IMPLEMENTED REFERENCE |
| DGM-04 | Archiwum genealogiczne | `evolution.py::ApprovedArchive` + `research_archive.py::ResearchArchive` | Testy autoryzacji i wielopokoleniowego research | IMPLEMENTED RESEARCH GENEALOGY; RELEASE OWNER-GATED |
| RSI-01 | LLM proposer z internetem | `research_engine.py` | Testy HTTPS/allowlist | IMPLEMENTED, NEEDS CREDENTIALS |
| RSI-02 | Cykliczne badania | `scripts/research_watch.py` i GitHub schedule | Testy offline; run GitHub po push | SCHEDULED PUBLIC METADATA |
| RSI-03 | Źródła ImandraX → proposer DGM | `engine.py`, `cycle.py` | Test integracyjny | IMPLEMENTED |
| RSI-04 | SHA patcha, bazowego kodu i artefaktów | `engine.py::register_review_artifacts` | Negatywne testy tamper/drift | IMPLEMENTED |
| RSI-05 | 4 podpisane suites | `rsi.py::RSIReviewStore` | Testy Ed25519 | IMPLEMENTED REFERENCE |
| RSI-06 | Podpis użytkownika dla każdej zmiany | `rsi.py`, `approval_api.py` | Testy odrzucenia self-approval | IMPLEMENTED REFERENCE; EXTERNAL HOST NOT DEPLOYED |
| RSI-07 | Samoczynne wdrożenie po testach | **Niedozwolone** | Brak endpointu apply/merge/deploy | DISABLED BY DESIGN |
| OPS-01 | Pętla ciągła / microVM | `daemon.py`, `deploy/daemon/`; Docker bez sieci | Testy pętli i izolacji | DAEMON CODE READY; NOT DEPLOYED; MICROVM NOT IMPLEMENTED |
| OPS-02 | Main GitHub Ruleset | Konfiguracja właściciela | Odczyt API | NOT CONFIGURED |
| OPS-03 | Niezależna authority TLS | `deploy/authority/`, token-file loader | TLS1.3 handshake test + Ed25519 | REFERENCE DEPLOYMENT READY; NOT HOSTED |
| OPS-04 | 4 repozytoria Lean | `lean-upstream-manual.yml` (push + tygodniowy harmonogram) | Wyniki GitHub Actions po push | PINNED MATRIX; FULL BUILDS NOT YET VERIFIED |

Szczegółowe oryginalne wymagania ImandraX v1.3, DGM–RSI v1.0 i 14 stron PDF pozostają w `docs/blueprints/`. Nie wolno utożsamiać macierzy mapowania z ukończeniem wszystkich modułów.
