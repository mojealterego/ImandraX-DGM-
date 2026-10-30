# OMEGA Memory Recovery Gate v1.1

## Scope and trust
This is one-engine memory recovery. Online SQLite backup, exact SHA-256, pinned logical sequence, detached Ed25519 signature verification, and isolated recovery copy. No owner private key enters ImandraX; no autonomous code approval, merge, deployment, live database switch, WORM, HA or independent attestation.

## Steps
1. Keep active state outside Git and place backup on separately protected storage. Export from the same installed CLI using the following JSON as input to cognitive / snapshot-export:

    {"snapshot":"/offline-backups/memory.sqlite3","manifest":"/offline-backups/manifest.json","identity_id":"omega-instance-1"}

2. Example command:

    imandrax-dgm --root . cognitive --state-dir /var/lib/omega --op snapshot-export --payload-file /tmp/export.json

3. Inspect the UNSIGNED manifest and copy it to a separate owner-controlled, trusted device. **Sign it only OFFLINE** with the owner's Ed25519 private key; never store the private key inside runtime, Git, CI, or the proposer.

    signature_hex = private_key.sign(signature_message(manifest_dict)).hex()

The function signature_message is in imandrax_dgm.memory_snapshot; it emits a domain-separated canonical JSON message. This expression is an offline signer protocol, not a runtime auto-sign API.

4. The verifier accepts a pinned owner public key and independent high-water sequence. Use JSON:

    {"snapshot":"/offline-backups/memory.sqlite3","manifest":"/offline-backups/manifest.json","signature_hex":"<128-hex-offline-signature>","owner_public_key_hex":"<64-hex-trusted-public-key>","expected_identity_id":"omega-instance-1","min_system_seq":1}

    imandrax-dgm --root . cognitive --state-dir /var/lib/omega --op snapshot-verify --payload-file /tmp/verify.json

5. For recovery, add "destination":"/recovered/memory-copy.sqlite3" and use snapshot-restore. Existing destinations are rejected; the live database is not replaced.

## Exact trust limits
- The manifest binds identity, consistent database bytes, exact checkpoint sequence, and chain-head digest.
- The owner must pin expected identity, public key and the minimum accepted system sequence **outside the same machine**; otherwise a compromised host can substitute them.
- A valid old owner signature is not enough: a snapshot older than the independently known high-water mark is rejected (ROLLBACK_DENIED).
- A SQLite hash chain alone is not WORM: host compromise may destroy or truncate local storage. This component does not replace remote encrypted storage, immutable retention, HSM/KMS, mutual TLS, RBAC, disaster-recovery drills or independent attestation.
- The verifier parses a signed database and checks its internal journal; signature verification is required before restoration.
- Never treat memory content as trusted program instructions; private or sensitive episodes should not be backed up without the user's explicit retention and encryption policy.
- Production readiness remains BLOCKED pending a separate trust-domain deployment and signed release acceptance.

## Tests
Roundtrip export, detached owner signature, wrong signer/identity, bit tampering, duplicate JSON keys, stale signed state, destination overwrite refusal, isolated recovery and CLI integration. Only an observed CI run may be reported as PASS.
