# Persistent research-only worker (optional, dedicated host)

`imandrax-daemon` is an **actual bounded loop**, not a simulated background task. Each cycle obtains mathematical references from the ImandraX index, retrieves public OpenAlex metadata, requests LLM-generated candidate code, evaluates it in a no-network Docker sandbox, persists untrusted DGM genealogy, and creates review-only artifacts. It cannot approve, apply, merge or deploy its own code.

**Not deployed**. The `imandrax-rsi.service` file is a template for an independently provisioned Linux host. It requires: a pinned Git checkout, the pinned SQLite knowledge index, an owner-provided HTTPS LLM endpoint and API key, an immutable Docker image digest, Docker runtime and dedicated persistent state volume. Set `RSI_DAEMON_ENABLED=true` explicitly. `RSI_BASE_COMMIT` must equal `git rev-parse HEAD`; the solver source must be clean.

**Critical security:** Docker socket access is root-equivalent on typical Linux hosts. Run on a **dedicated disposable worker VM**, never on the authority host or a multi-tenant machine. The proposer has internet access, the candidate container has `--network none`. Research state is not a WORM log. No signing keys or GitHub write tokens may be mounted. Stop or update the service under owner control; pinned source revisions are intentionally not auto-updated.

The interval defaults to six hours; max three consecutive failures halt the loop. This is a daemon implementation, **not evidence of a deployed 24/7 service**, microVM isolation, or an independently attested test runner. The systemd unit does not include a host-level sandbox bypass of Docker privileges; review it before use.
