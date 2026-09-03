# TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP

**Task ID**: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP  
**Task Type**: 64K follow-up validation (exploratory) of Attempt-003 candidate  
**Requires**: Evidence Review PASS (16K microgate) of `GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE`  
**Status**: READY / PENDING USER DISPATCH  
**Created**: 2026-09-02  
**Assigned to**: A3PerfRunner (AUTONOMOUS PERFORMANCE OPTIMIZATION RUNNER)  
**Priority**: HIGH

## 1. Purpose

Validate the reviewed Attempt-003 candidate profile under the project's final 64K workload:

1. capacity at max-model-len 70000 OK;
2. correctness OK (no device errors);
3. 256/256 success;
4. 64K performance vs accepted 64K baseline 927.59 tok/s.

This is exploratory 64K follow-up; NOT a Formal Result, NOT 4-run formal matrix.

## 2. Reviewed candidate profile (recorded; from evidence review)

- model GLM-5.2-W8A8; runtime accepted vLLM 0.24 family
- max-model-len 70000; DP2/TP8/EP ON; gpu-memory-utilization 0.97; max_cudagraph_capture_size 96; max-num-seqs 48; max-num-batched-tokens 4096; MTP OFF; async ON; multistream_overlap_shared_expert ON; FULL_DECODE_ONLY; prefix cache OFF

## 3. Service reuse (preferred)

Current Attempt-003 service: `SERVICE_LEFT_RUNNING=YES`, PID 257285, port 8000, log /workspace/glm52_od_attempt-003.log.

Prompt flow:

1. verify service alive (ps/API), PID/cmdline, model identity, exact effective profile, /v1/models, max-model-len>=70000, no residual device errors; compare against your reviewed candidate
2. if the running service EXACTLY matches the Attempt-003 candidate profile: reuse it (NO restart, NO re-graph-capture);
3. only if service absent / identity mismatch / profile mismatch: the runner restores the reviewed candidate (bounded autonomous remediation within HARD BOUNDARIES);
4. max-model-len >= 70000 is a HARD BOUNDARY for the final candidate: never lowered to force 64K.

## 4. 64K benchmark contract

- input 65536; output 1024; concurrency 64; num-prompts 256; dataset random; range-ratio 0; inf; ignore-eos; /v1/completions; client vllm bench serve
- Run1 warmup/discard; Run2 measured

Accepted 64K baseline: 927.59 tok/s  
D-024 normalized target (80%): machine-computed (see §5)

## 5. Machine-computed metrics (not handwriting)

- delta vs accepted 64K baseline = (Run2_total / 927.59 - 1) * 100 (machine)
- active D-024 normalization: A3 basis 6016 (752x8); H100 basis 15824 (989x16); H100 64K reference 5054.66; 80% absolute target = 5054.66 / 15824 * 6016 * 0.80 (machine)
  → 1537.35 tok/s (recomputed by the same formula in Control; value embedded here only as the current machine value)

## 6. Autonomous policy

Runner remains AUTONOMOUS OPTIMIZATION RUNNER within HARD boundaries. Recoverable 64K issues (OOM/KV/graph/scheduler/performance) are feedback: diagnose/modify/retry with recorded he, evidence; do not wait User for recoverable issues. Parameters may be adjusted (same adjustable list as the parent micro gate: DP/TP/EP, seqs, batched tokens, gpu-mem, capture, async, MTP, allocator...). Never lower max-model-len < 70000 for 64K; smaller context diagnostics clearly MUST be marked DIAGNOSTIC ONLY / NOT CANDIDATE.

## 7. 64K exploratory disposition

- Run2 Total Token Throughput vs 927.59:
  - * >= 1537.35 (80% target, machine-computed) → QUALIFICATION: above target → `64K_FOLLOWUP_PASS` (formal NOT; flag for review)
  - > 927.59 but < 1537 → `64K_FOLLOWUP_IMPROVED_BELOW_TARGET` (report delta)
  - <= 927.59 → `64K_FOLLOWUP_NO_IMPROVEMENT` (report delta)
  - failed/OOM/crash/correctness → `64K_FOLLOWUP_INVALID_OR_ROLLBACK_CANDIDATE`
- Correctness gates: 256/0 unless failing; otherwise flag.

No auto anything beyond 64K run; report to PerfControl + User.

## 8. Evidence (all outcomes) + SERVICE_LEFT_RUNNING default

Devices/attemp-metric files per parent Task; control-sha; profile photo; use snapshots; capacity/update; bench run1/run2 json|log|summary; machine extraction; optimization-summary update or new 64K summary; service-left-running YES + PID/port/log if reuse. D-022 upload tar.gz.

## 9. Status notes

- Formal OPT-01 unchanged (BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION).
- This branch remains exploratory until governance sees the 64K result.
- No Formal result authored here.