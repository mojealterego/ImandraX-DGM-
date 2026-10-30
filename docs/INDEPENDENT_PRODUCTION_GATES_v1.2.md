> **Aktualizacja zakresu — desktop/mobile:** obowiązuje [LOCAL_ARCHITECTURE](LOCAL_ARCHITECTURE.md). Hosting, HSM/WORM i multi-host dotyczą opcjonalnego profilu serwerowego. Nie są warunkami działania produktu lokalnego. Instalatory odłożono do zakończenia rozbudowy. Istniejące mechanizmy podpisów i odmowy nie są wyłączane.

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

## GitHub main ruleset — corrected to the owner-approved main-only workflow

The earlier proposal mistakenly imposed an independent PR reviewer and required a pull request. **It was not an owner requirement and has been withdrawn.** No second reviewer, temporary branches or PRs are required for owner-requested direct updates to main.

GitHub API inspection at 2026-10-30: rulesets [] (none active). The installed GitHub source connector cannot administer rulesets. The source file deploy/github-main/ruleset-proposed.json now contains **only** deletion protection and non-fast-forward protection. This is an owner-applied administrative proposal, not enforced merely because it is committed.

There is deliberately no pull_request or required_status_checks rule in this proposal. Required status checks on main can block direct pushes until checks already exist for the incoming commit; in a strict no-other-branches workflow, this would create a deployment deadlock. CI continues to run and provide post-push verifiable evidence, but **post-push CI is not a pre-push gate**. The owner can separately decide on a compatible pre-push signed-commit or release policy; do not silently enable it.

Human approval remains required for agent-generated release/apply/migration and does not require independent PR review or another human reviewer. Evidence runner and external infrastructure trust domains remain independent so that the agent cannot approve its own verification claims.

Actual enforcement requires the repository owner to apply the two rules through Settings → Rules → Rulesets and verify the GitHub API; this connection cannot perform administrative ruleset writes.


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

## Recovered earlier Red Hat pipeline (2026-10-30)

The existing, previously authenticated Red Hat Developer Sandbox workflow belongs to the OCAF repo (mojealterego/ocaf-runtime). It targeted namespace mojealterego-dev at the pinned API https://api.rm3.7wse.p1.openshiftapps.com:6443 using OCAF GitHub Actions secrets named OCAF_SANDBOX_API_URL and OCAF_SANDBOX_TOKEN. The workflows are .github/workflows/ocaf-stage038-redhat-sandbox.yml and .github/workflows/ocaf-stage038-redhat-vm-admission.yml. Previously observed success is historical, not a guarantee the credentials are valid now.

A reusable staging BuildConfig for ImandraX is deploy/openshift-sandbox/build.yaml: a Docker strategy with Git source pinned to the exact reviewed ImandraX commit, ImageStream output, no auto triggers. Staging deployment automation runs only in the original OCAF repository where the existing secrets are scoped. It must verify live RBAC and admission, must never copy access tokens to ImandraX, and must use disposable test signing identities and TLS. The deployment never represents independent production HSM/WORM/DR attestation. Status must be based on a real successful GitHub Actions run.
