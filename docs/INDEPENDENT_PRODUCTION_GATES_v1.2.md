# OMEGA v1.2 — independent trust gates and Red Hat Sandbox staging

**Status:** code/specification and GitHub CI only, NOT deployed. No owner private key has entered this repository, Docker image, CI or Red Hat cluster. All source-controlled JSON and YAML are templates, not effective policy.

## Red Hat Sandbox: scope and security boundary

The Developer Sandbox is a 30-day evaluation service on shared OpenShift. It can validate application startup, HTTPS endpoints, network policy and pod restart/recovery scenarios in one namespace. It is **not** a safe location for a real owner signing key, production KMS/HSM trust roots, irreplaceable records, real customer data or a permanent WORM archive. A PVC in a single namespace does not demonstrate multi-host/high-availability recovery or immutable storage.

The source is deploy/openshift-sandbox/staging.yaml. It describes one isolated, non-root, read-only-rootfs container, ClusterIP-only service, no Route, deny-all egress, label-restricted ingress, disabled Kubernetes service-account token, short memory budgets and a single PVC. It has no secret values, addresses or accounts; the image digest placeholder must be replaced.

**OpenShift account access and image signing are deliberately not fabricated.** After sign-in at https://developers.redhat.com/developer-sandbox/ and selection of your authorized namespace:
1. Build/publish reviewed code from deploy/authority/Dockerfile into a container registry, resolve the immutable image SHA-256 digest and replace the staging manifest placeholder. Review the image's base layer digest and scanning reports first.
2. Generate *staging-only*, distinct public Ed25519 keys for runner/reviewer identities outside the runtime, and supply matching public trust JSON. **Never upload an owner's actual signing private key.**
3. Create staging secrets and ConfigMap in your namespace, keeping secret files entirely outside Git:
   - \`oc create configmap omega-staging-trust --from-file=trust.json=/secure/staging-trust.json\`
   - \`oc create secret generic omega-staging-tokens --from-file=proposer_token=/secure/proposer_token --from-file=runner_token=/secure/runner_token --from-file=reviewer_token=/secure/reviewer_token\`
   - \`oc create secret tls omega-staging-tls --cert=/secure/staging.crt --key=/secure/staging.key\`
4. \`oc apply -f deploy/openshift-sandbox/staging.yaml\`. This is a **manual operator action** after explicit connection and permission; these instructions have not been run. If PVC or SecurityContext admission is denied by Sandbox quotas, inspect allowed SCC and volume permissions; do not escalate to privileged SCC.
5. \`oc rollout status deployment/omega-staging-authority\` and \`oc get pods -o wide\`. Exercise signed and negative API flows from a temporary test client pod with the label \`omega-authority-client=true\` and a trust-valid staging TLS cert. No external Route is created.
6. For staging fault drills, delete the pod, verify a new pod can read its independent state from PVC, inspect logs, assert no approved decision is forged and that stale/invalid signatures are denied. Record pod IDs, Node names, timestamps, manifest/image digest and the measured recovery duration. This is **single-cluster staging**, not a two-host proof.
7. Delete staging secrets and workloads when finished. Red Hat Sandbox does not replace an approved production hosting contract.

Red Hat official sandbox documentation: https://developers.redhat.com/developer-sandbox/FAQ
and https://developers.redhat.com/developer-sandbox

## GitHub main ruleset

GitHub API inspection at 2026-10-30: rulesets \`[]\`. The installed GitHub connector cannot create an administrative ruleset, even though it can write source code.

**Template:** deploy/github-main/ruleset-proposed.json, ready for review by the owner. It calls for:
- no deletion or force push to main;
- exact required CI checks for all six jobs;
- one independent approving PR review and approval of the final commit.

**Conflict with existing branch policy:** a GitHub PR-based approval ruleset cannot coexist with a strict *no other branches* policy for the same repository. To activate this strict ruleset, the owner must authorize a temporary review branch for changes or change the chosen workflow; otherwise GitHub will reject direct-to-main commits. The template is **not applied**. With an unconfigured ruleset, release admission remains blocked. A self-review is not an independent reviewer approval.

Owner action: open GitHub repository **Settings → Rules → Rulesets**, configure the proposed controls subject to supported plan and GitHub validation, and verify API \`GET /repos/mojealterego/ImandraX-DGM-/rulesets\` reports \`enforcement=active\`. Never infer policy enforcement from a committed template.

## Independent admission from signatures

\`src/imandrax_dgm/release_admission.py\` verifies seven **separately pinned** Ed25519 public keys and domain-separated, expiring receipts for the *same* source commit and artifact SHA-256. Required roles: RULESET, AUTHORITY, HSM_KMS, WORM, MULTI_HOST_DR, INDEPENDENT_TESTS, OWNER. Duplicate keys and role spoofing are rejected. The gate never signs, modifies source, issues deployment tokens or reports \`release_authorized=true\`, even when all receipt signatures validate: it returns \`READY_FOR_EXTERNAL_OPERATOR_REVIEW_NOT_DEPLOYED\`.

A cryptographic signature attests who signed **a claim**, not that the claimed physical deployment really happened. Receipt signers must be independent of the proposer and must review real external evidence. Trust roots must be pinned outside the repo/agent, and key custody, revocation and expiry procedures must be independently maintained.

## Minimum external evidence required before production

| Role | Concrete evidence | Trust boundary |
|---|---|---|
| RULESET | Repository API response showing active protection and green protected-branch required checks; PR independent approval | GitHub owner/admin |
| AUTHORITY | Independent host, TLS 1.3 authenticated API, signed role separation, health and negative tests | Host away from proposer |
| HSM_KMS | Actual managed key ID, attested/non-exportable key policy and recorded signature verification; rotation and revocation tests | Independent KMS/HSM provider |
| WORM | Bucket/container immutability retention policy, legal-hold/retention-negative tests, off-site archive digest | Independent storage provider |
| MULTI_HOST_DR | Two independent physical hosts / failure domains; time-stamped host-failure / failover / restore results and integrity checks | Independent test runner |
| INDEPENDENT_TESTS | Signed original logs of regression, security, heldout, artifact hash and reproducibility suites | Unrelated runner key and isolated test resources |
| OWNER | Owner-reviewed diff/source pin, independent approval and offline digital signature | Owner-controlled external device |

Until these are configured and **observed on real external systems**, the accurate status remains BLOCKED_NOT_DEPLOYED. Running CI locally or GitHub-hosted Python tests does not upgrade the evidence tier.

## Admission and rollback

The approved artifact must be immutable and pinned to its exact SHA-256. A deployment receipt must bind the same commit, image digest, deployment resource UID, owner decision, timestamp and rollback target. Emergency rollback requires **a separate authorized procedure**, no automatic DGM/RSI promotion. For memory backup restore consult docs/MEMORY_RECOVERY_GATE_v1.1.md.

Invariants:
- fail closed on missing/expired/untrusted signature or mismatched source/artifact;
- no deploy by a research agent;
- multi-host evidence cannot be replaced with two containers on one runner or pods in one shared cluster;
- no sensitive production signing keys in Sandbox, source code or CI;
- protect main only through an *actual enforced* platform control, never by a JSON file.
