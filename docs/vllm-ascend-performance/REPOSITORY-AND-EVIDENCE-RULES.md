# Repository and Evidence Rules

## Control contents

Commit stable source-material records, contracts, small manifests, checksums, immutable Results, Formal Reviews, Decisions, and stable server Evidence pointers. Do not commit weights, Docker images, large raw logs, profiling files, credentials, or secrets.

## Three evidence pointers

Every formal Result links to:

1. **Code/runtime:** repository, commit/tree, package/image identity, and checksums.
2. **Control:** Task, Result, result index, Review, and acceptance commit.
3. **Server Evidence:** absolute Evidence root, run manifest, command/config capture, environment inventory, logs, and checksums.

## Task and dispatch

PerfControl writes a bounded Task after identities and contract inputs are frozen. `READY` means the document is complete enough for dispatch; it is not authorization. Before dispatch, PerfControl verifies `local Control HEAD == origin/main == DISPATCH_CONTROL_SHA`, then User supplies the explicit dispatch authorization (Task ID, `DISPATCH_CONTROL_SHA`, `Authorization: EXECUTE`). A3PerfRunner may execute only after this explicit User dispatch. The Runner is not required to hold a local Control repo and does not verify server Git state against `DISPATCH_CONTROL_SHA`; the SHA is Evidence provenance, not a server Git-state identity.

## Result authorship and immutability

Runner produces Evidence; PerfControl produces formal Results. A3PerfRunner's Evidence root, manifest, commands, checksums, and runtime identity are immutable once created; never rewrite them. Corrections or additional evidence are supplements or new Evidence captures. After receiving Evidence, PerfControl independently recalcs the values, authors the formal `RESULT-*.md` snapshot once, and afterwards never rewrites it; corrections are supplement documents or follow-up Results. PerfControl Acceptance changes only the index, Status, Review, and Decision records. The server never commits or pushes the Control repo.

## Acceptance states

Keep these dimensions separate: experiment result (`PASS`, `FAIL`, `STOP`, `PARTIAL`), Control sync (`SYNCED` or `PENDING`), and PerfControl disposition (`ACCEPTED`, `REJECTED`, `NEEDS-FOLLOWUP`, or `PENDING`).

## Claim boundaries

Acceptance is per exact cell and identity. Do not extrapolate to other sequence lengths, concurrency, runtime versions, hardware SKUs, quantization, parallelism, or cache/MTP/graph modes.

## Version lanes and discovery ownership

Every Task and Result declares either `FLAGOS_ALIGNED` or `LATEST_REFERENCE`. The former is pinned to the official FlagOS-aligned tuple; the latter is `NON_FLAGOS_ALIGNED_REFERENCE` and cannot enter FlagOS acceptance. PerfControl owns public-source facts. A3PerfRunner owns server-observable facts after explicit dispatch. User input is reserved for policy, authorization, private material, engineering-reference approval, and unresolved business decisions.

**Model-specific exception (Decision D-019)**: GLM-5.2-W8A8 current native performance work uses User-verified vLLM 0.24 runtime, not the FlagOS-aligned 0.20.2 baseline.

## Persistent workspace and command completeness

Use the User-approved roots `WORK_ROOT=/data/tiankuan/zyg`, `MODEL_ROOT=/data/tiankuan/zyg/model`, `EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`, and `TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control`. Do not use `/tmp` as formal Evidence fallback, search beyond `MODEL_ROOT` for model discovery, reuse another project's run directory, or mount `/data:/data` / `/root/.cache:/root/.cache`.

From Stage 1, every server-operation Task must include complete directly executable commands and resolved identities for its scope, logging, readiness, and cleanup. Abstract verbs without commands are not dispatch-ready. Stage 0 may write only task-owned Evidence bookkeeping; it may not create containers or change runtime.
