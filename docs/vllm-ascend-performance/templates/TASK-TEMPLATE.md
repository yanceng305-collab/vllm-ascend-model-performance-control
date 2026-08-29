# Task Template

**Task ID:** `...`

**Status:** `DRAFT | READY / AWAITING EXPLICIT USER DISPATCH | DISPATCHED | COMPLETE`

**Track:** `FLAGOS_ALIGNED | LATEST_REFERENCE`

**Objective:**

## Frozen identity

| Field | Value / evidence |
|---|---|
| Model / revision / SHA | |
| Quantization / dtype / KV cache dtype | |
| vLLM / vLLM-Ascend | |
| CANN / torch / torch_npu / Triton / Mooncake | |
| Hardware / devices / topology | |
| TP / DP / EP | |
| Image / container | |
| Benchmark contract / cell | |

## Authorization and scope

State the exact User dispatch requirement, allowed actions, prohibited actions, stop conditions, and whether the Task is read-only. `READY` is not authorization.

## Evidence requirements

Record Task/Run IDs, exact commands, timestamps, environment and artifact manifests, checksums, raw logs, server Evidence root, and the Control Result path. Do not commit secrets or large raw data.

## Return and disposition

Require the immutable Result to state last successful gate, first blocker, raw values, comparison class, track, and next stage. Codex1 reviews the Result independently; execution PASS is not acceptance.
