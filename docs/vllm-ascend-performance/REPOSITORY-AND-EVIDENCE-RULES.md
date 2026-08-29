# Repository and Evidence Rules

## Control contents

Commit stable source-material records, contracts, small manifests, checksums, immutable Results, Formal Reviews, Decisions, and stable server Evidence pointers. Do not commit weights, Docker images, large raw logs, profiling files, credentials, or secrets.

## Three evidence pointers

Every formal Result links to:

1. **Code/runtime:** repository, commit/tree, package/image identity, and checksums.
2. **Control:** Task, Result, result index, Review, and acceptance commit.
3. **Server Evidence:** absolute Evidence root, run manifest, command/config capture, environment inventory, logs, and checksums.

## Task and dispatch

Codex1 writes a bounded Task after identities and contract inputs are frozen. `READY` means the document is complete enough for dispatch; it is not authorization. Codex2 may execute only after explicit User dispatch naming the Task.

## Result immutability

Codex2 publishes the first `RESULT-*.md` snapshot once. It must include raw values and exact normalized calculations. Never rewrite it. Append a supplement or create a follow-up Result for corrections/additional evidence. Codex1 Acceptance changes the index, Status, Review, and Decision records only.

## Acceptance states

Keep these dimensions separate: experiment result (`PASS`, `FAIL`, `STOP`, `PARTIAL`), Control sync (`SYNCED` or `PENDING`), and Codex1 disposition (`ACCEPTED`, `REJECTED`, `NEEDS-FOLLOWUP`, or `PENDING`).

## Claim boundaries

Acceptance is per exact cell and identity. Do not extrapolate to other sequence lengths, concurrency, runtime versions, hardware SKUs, quantization, parallelism, or cache/MTP/graph modes.

## Version lanes and discovery ownership

Every Task and Result declares either `FLAGOS_ALIGNED` or `LATEST_REFERENCE`. The former is pinned to the official FlagOS-aligned tuple; the latter is `NON_FLAGOS_ALIGNED_REFERENCE` and cannot enter FlagOS acceptance. Codex1 owns public-source facts. Codex2 owns server-observable facts after explicit dispatch. User input is reserved for policy, authorization, private material, engineering-reference approval, and unresolved business decisions.

## Persistent workspace and command completeness

Use the User-approved roots `WORK_ROOT=/data/tiankuan/zyg`, `MODEL_ROOT=/data/tiankuan/zyg/model`, `EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`, and `TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control`. Do not use `/tmp` as formal Evidence fallback, search beyond `MODEL_ROOT` for model discovery, reuse another project's run directory, or mount `/data:/data` / `/root/.cache:/root/.cache`.

From Stage 1, every server-operation Task must include complete directly executable commands and resolved identities for its scope, logging, readiness, and cleanup. Abstract verbs without commands are not dispatch-ready. Stage 0 may write only task-owned Evidence bookkeeping; it may not create containers or change runtime.
