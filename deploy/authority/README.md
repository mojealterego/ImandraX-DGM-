# Independent human approval authority — deployment blueprint

**State:** deployable reference configuration; **not deployed** and **not a production attestation or release authority**. This service verifies independent Ed25519 signatures; it does **not** sign on the user's behalf, apply code, merge GitHub commits or run model proposals.

## Host separation and trust

Run this on a **dedicated host** with separate credentials and no Docker socket shared with the proposer/evaluator. In the checked-in Compose configuration the TLS 1.3 API binds only to `127.0.0.1:9443` on the host; reach it through a reviewed SSH tunnel or mutually authenticated private network. Do not expose the service directly to the internet without a properly configured, rate-limited gateway, network ACLs, monitoring, certificate rotation and independent security review.

1. Create `config/trust.json` containing `{"runners":{"runner-01":"<32-byte-Ed25519-public-key-in-hex>"},"reviewers":{"user-01":"<different-32-byte-public-key-in-hex>"}}`. Only **public** keys belong here. The human signing **private key must remain on the user's own device**, never in this service or in GitHub Actions.
2. Create `secrets/proposer_token`, `secrets/runner_token`, `secrets/reviewer_token` with distinct cryptographically random values of at least 32 characters; create `secrets/tls.crt` and `secrets/tls.key` for a valid server certificate. All these files must remain outside Git and be access-restricted on the host.
3. Create `state/` owned by UID 10001 (or adapt the runtime UID), then review Compose hardening and deploy with `docker compose -f deploy/authority/compose.yaml up -d --build` **on the independent host**.
4. Verify TLS 1.3 and that requests without the correct role token return 401. Test signed `STATIC_CHECK`, `REGRESSION`, `SECURITY`, `HELDOUT` and a separately signed owner decision; test negative cases and expiration.
5. Implement durable encrypted backups, external append-only audit replication, token/certificate rotation, health checks, monitoring and incident response before declaring production readiness. SQLite with local triggers is not WORM or a tamper-proof audit log.

**Security caveats:** Docker Compose file-based secrets can be exposed to other processes inside the same container. Use a single-purpose container and restrict host file permissions. Docker isolation is not a substitute for a hardened microVM or separate physical trust boundary. The TLS service authenticates evidence origin but cannot independently establish that the claimed test suite actually ran on an attested host. GitHub `main` ruleset is still an owner-controlled configuration.
