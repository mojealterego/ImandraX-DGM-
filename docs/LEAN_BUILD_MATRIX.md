# Lean 4 integration compatibility — observed default branches (2026-10-29)

| Repository | File | Exact declared Lean | Other declared dependency |
|---|---|---|---|
| `mojealterego/mathlib4` | `lean-toolchain` | `leanprover/lean4:v4.36.0-rc2` | pinned manifest must be read for full build |
| `mojealterego/batteries` | `lean-toolchain` | `leanprover/lean4:v4.36.0-rc2` | independent Batteries package |
| `mojealterego/iris-lean` | `Iris/lean-toolchain` | `leanprover/lean4:v4.35.0` | `Iris/lakefile.toml` requires Batteries `v4.35.0` and Qq `v4.35.0` |
| `mojealterego/mathematics_in_lean` | `lean-toolchain` | `leanprover/lean4:v4.34.0` | `lakefile.toml` requires mathlib `v4.34.0` |

**Finding:** These exact snapshots cannot simply be merged into a single Lake environment with one version of Lean. Each must be built in its own pinned workspace. Cross-workspace theorem transfer must recheck the translated statement/proof in the destination kernel with explicit axioms and hashes.

**Required execution evidence (not performed):** four independent `lake build` logs, compiler versions, `lake-manifest.json` digests, test logs, `#print axioms` checks, negative tests with `sorry` and untrusted axioms, reproducible CI artifacts. Lean and Lake executables were not installed in the available runtime, and GitHub source clones were not materialized. No Lean proof is claimed.