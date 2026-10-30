# ImandraX Ω — Cognitive Workflows v1.0

**Scope:** same product, same `main`. APEX signed capability manifest unchanged. Bounded research workflows do not perform autonomous approvals, code mutation, imports, shell, external model execution, or deploys.

## Architecture

```text
IntegratedEngine (ONE product)
  ├─ BitemporalGraphMemory (existing persistent SQLite, as-of & tenant)
  │  └─ MultiHopVerifier → explicit EDGE fact per hop
  ├─ TreeOfThoughts → score-constrained beam search (heuristics only)
  ├─ ReWOOPlanner → ontology-only READ steps → async observations
  ├─ CognitiveDecisionCycle → critique/refine & referenced episodic synthesis
  ├─ cascade_plan → offline budget/quality estimation, NO model inference
  ├─ DurableEventQueue → SQLite idempotent enqueue/lease/retry/deadletter
  │  └─ research_handlers → checks local hypothesis references while other events wait
  ├─ ResearchArchive/ResearchCycle (existing DGM, unchanged)
  └─ ApexRegistry / owner-signed epochs (unchanged / not bypassed)
```

## Contracts & threat model

### Tree-of-Thoughts

`ThoughtBranch(node_id,parent,depth,score,sources)`, `TreeOfThoughts(beam_width<=8,max_depth<=8)`. Exact ancestor-depth validation, one root, no cycles, hard cap 64 candidate thoughts. The selected path is **HEURISTIC_PATH_NOT_PROOF**; heuristic scores are supplied inputs, not verified by any model.

### Multi-hop and wrong bridges

`MultiHopVerifier.check` obtains live/as-of EDGE records from the same tenant and validity time. Every (source,target,relation) link must exist explicitly, have provenance and confidence >=0.8; no edge => `BLOCKED_MISSING_BRIDGE`. The graph path is **NOT logical entailment**; data source quality, formal truth and counterfactuals require external independent checks. Relational coincidences and model-generated text cannot establish new edges by themselves.

### ReWOO / ontology-driven tools

`OntologyRegistry` accepts *only* `READ` with enumerated ontologies. Handlers are bound by reviewed Python code, never from a manifest or JSON input. `PlanStep` is a strict data object, references `{"$ref":"step-id","field":"value"}` only to declared predecessors. The planner validates the full DAG before execution, emits waves, runs dependency-independent read handlers concurrently under semaphore + timeout, and fails dependent steps closed if observation missing. Failure returns `INCOMPLETE_NO_SIDE_EFFECT`. Tool functions must be read-only; this is a trusted-process registry and is **not a sandbox**.

### Durable event-driven research

`DurableEventQueue`: SQLite transactional claims, lease token, optimistic ownership via token, retry exponential backoff, idempotency based on event ID and content, dead-letter after budget, explicit event allowlist, event count and payload size caps. The queue is persistent but local; it is not independent WORM and does not provide multi-host HA. `research.check` is the only built-in executed handler and checks whether evidence references are in the same tenant's local memory; it reports `REFERENCES_PRESENT_NOT_PROVED`, never factual certainty. One invocation processes at most one queued event. A scheduler/systemd can call it when separately deployed.

### Correction and synthesis

`critique_and_refine` ranks bounded supplied candidate drafts (maximum 8 rounds) without executing them. `synthesize_episodes` creates a semantic *index/reference* from verified existing EPISODIC rows with source revision numbers, explicitly `inferred_fact=false`. Neither creates unreferenced new truths.

### Cascaded inference

`cascade_plan` prepares an ordered, cost-bounded stage plan with declared quality estimates; no model was loaded or benchmarked. It is advisory, not a trained router or RL cascade. If quality cannot be met, it reports `CASCADE_QUALITY_UNMET`.

## Operator interface

```bash
python -m pip install -e '.[test]'
python -m pytest -q
imandrax-dgm --root . media-audit --limit 120
imandrax-dgm --root . cognitive --state-dir /tmp/omega-cognition --op tot --payload-file tree.json
imandrax-dgm --root . cognitive --state-dir /tmp/omega-cognition --op rewoo-validate --payload-file plan.json
imandrax-dgm --root . cognitive --state-dir /tmp/omega-cognition --op event-process --payload-file now.json
```

`tree.json`: `{"beam_width":2,"max_depth":2,"thoughts":[{"node_id":"root","parent":null,"depth":0,"score":0.8,"sources":["s1"]}]}`.
`now.json`: `{"now":123.0}` uses Unix seconds. For durable operation, use real Unix timestamps and an operator-owned state directory outside source.

## Portfolio due diligence

`media-audit` classifies **all 701 snapshot metadata records**, not the source trees. `data/media_repo_evidence_v10.json` records 12 root README and 8 LICENSE headers from GitHub. Categories: game engines / 3D, photo, video, audio, model training, uncensored research. These are metadata candidates: `source_audit=NOT_DONE`, `integration=BLOCKED`. Special license findings: ComfyUI-LTXVideo (community model license), MaxVideoAi (BSL-1.1), Stable-Diffusion-KMP (AGPL-3.0) — copying code into one product is deferred pending license, model-weights and dependency review. Repo names containing NSFW/Uncensored do not imply an availability of compatible weights or redistribution rights.

Unidentified Google world fork: `NOT_VERIFIED`; do not guess that the user's repository implements Google Genie or that commercial model weights/API have been obtained.

## Remaining production gates

Authentication/RBAC per tenant, encrypted memory at rest, privacy retention/redaction/erasure, external WORM/checkpoint signer, audit across host and process failures, adversarial model prompt injection testing, real resource/time budgets for model inference, measured benchmark suites, GPU and mobile runtime tests, signed APEX epoch migration by offline owner authority, guarded GH main rulesets, and final deployment acceptance. An offline approval or release is NEVER produced by DGM/RSI automatically.

References: ToT NeurIPS 2023 https://papers.nips.cc/paper/2023/hash/271db9922b8d1f4dd7aaef84ed5ac703-Abstract-Conference.html ; ReWOO https://arxiv.org/abs/2305.18323 ; CoALA https://arxiv.org/abs/2309.02427 .
