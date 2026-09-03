# TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP

**Task ID**: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP  
**Task Type**: 64K follow-up validation (exploratory) - Attempt-003-derived memory-headroom candidate  
**Requires**: Evidence Review PASS (16K microgate) of `GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE`  
**Status**: READY / PENDING USER DISPATCH  
**Created**: 2026-09-02  
**Revision**: 2026-09-02 (candidate = gpu-memory-utilization 0.95 / max-model-len 67000)  
**Assigned to**: A3PerfRunner (AUTONOMOUS PERFORMANCE OPTIMIZATION RUNNER)  
**Priority**: HIGH

## 1. Purpose

Validate a memory-headroom 64K candidate derived from Attempt-003, under the project 64K workload (input 65536 + output 1024):

1. capacity at `max-model-len >= 66560` OK;
2. correctness OK (no device errors);
3. 256/256 success;
4. 64K performance vs accepted baseline 927.59 tok/s.

Exploratory; NOT a Formal Result; NOT a 4-run formal matrix.

## 2. Historical Attempt-003 (immutable execution fact - do not rewrite)

Attempt-003 was reviewed PASS. Its ACTUAL effective profile stays recorded exactly:

- gpu-memory-utilization = 0.97
- max-model-len = 70000
- max_cudagraph_capture_size = 96
- MTP = OFF
- DP2 / TP8 / EP ON
- max-num-seqs = 48
- max-num-batched-tokens = 4096
- async ON; multistream_overlap_shared_expert ON; FULL_DECODE_ONLY; prefix cache OFF
- 16K Run2 2116.32 tok/s (machine delta +120.9241% vs 957.94)

These numbers are immutable; do NOT rewrite Attempt-003 into 0.95 / 67000.

## 3. 64K FOLLOW-UP TARGET PROFILE (new candidate)

Classification: **ATTEMPT-003-DERIVED MEMORY-HEADROOM 64K CANDIDATE** (NOT identical to Attempt-003).

| Parameter | Value |
|---|---|
| gpu-memory-utilization | **0.95** |
| max-model-len | **67000** (initial) |
| max_cudagraph_capture_size | 96 |
| MTP / speculative | OFF |
| data-parallel | 2 |
| tensor-parallel | 8 |
| expert parallel | ON |
| max-num-seqs | 48 |
| max-num-batched-tokens | 4096 |
| async scheduling | ON |
| multistream_overlap_shared_expert | ON |
| graph | FULL_DECODE_ONLY |
| prefix cache | OFF |
| other params | inherit from reviewed Attempt-003 |

## 4. 64K capability hard boundary (right-sizing)

Formal workload: input 65536 + output 1024 → **REQUIRED TOTAL SEQUENCE CAPACITY = 66560 tokens**.

- **MINIMUM REQUIRED MAX MODEL LENGTH = 66560**
- 64K follow-up initial candidate: `67000` (small engineering headroom over 66560)
- allowed convergence toward the floor when KV capacity is tight:
  `67000 → 66800 → 66600 → 66560`
- **HARD FLOOR = 66560**: never lower max-model-len below 66560 (e.g., NOT 65536 / 64000), even for performance or memory. A smaller value cannot host 64K input + 1K output.

The prior `>= 70000` engineering conservative value is RELEASED for THIS Task in favor of the real business requirement of 64K + 1K; this is capacity right-sizing, NOT workload reduction. The final 64K workload and benchmark contract (section 8) are unchanged.## 5. gpu-memory-utilization = 0.95: fixed verification target

User decision: this Task verifies whether `gpu-memory-utilization = 0.95` is sufficient when only the real 64K+1K capacity is kept. Therefore:

- `0.95` is the formal target candidate value for this Task;
- do NOT auto-raise it on capacity struggles;
- **preferred remediation order**:
  1. shrink `max-model-len` from 67000 toward the floor in steps (66800 / 66600 / 66560);
  2. inspect actual KV / graph / memory evidence;
  3. keep `capture = 96` (preferred);
  4. keep MTP OFF;
  5. other engineering fixes that do not break the candidate identity (within adjustable set).
- If CAPACITY PASS still fails at `gpu-memory-utilization = 0.95` AND `max-model-len = 66560`, STOP and report:

  `GPU_MEMORY_UTILIZATION_095_INSUFFICIENT_FOR_REQUIRED_64K_PLUS_1K_CAPACITY`

  then User + ChatGPT decide whether raising to 0.96 / 0.97 is allowed. Do NOT raise utilization above 0.95 yourself.

Rationale: Attempt-003 (0.97 / 70000) proved strong performance but 0.97 is aggressive; this follow-up removes the un-needed context headroom (70000 vs 66560) to try a more conservative 0.95 while keeping the real business workload. This is MEMORY/HEADROOM AND CAPACITY RIGHT-SIZING - not performance cheating, not workload reduction.

## 6. Capacity gate (before any 64K benchmark)

Confirm all (evidence):

- gpu-memory-utilization = 0.95
- max-model-len >= 66560 (target first 67000)
- capture = 96
- MTP OFF
- DP2 / TP8 / EP ON
- max-num-batched-tokens = 4096
- max-num-seqs = 48
- async ON; multistream ON; FULL_DECODE_ONLY; prefix cache OFF
- API READY (/v1/models)
- no KV rejection, no fatal OOM, no device correctness error

Only CAPACITY PASS proceeds to the 64K benchmark.

## 7. Warm service reuse policy (PRIOR WARM REFERENCE SERVICE)

The current warm Attempt-003 service (SERVICE_LEFT_RUNNING=YES; PID 257285; port 8000; log /workspace/glm52_od_attempt003.log; profile 0.97/70000) may stay up until dispatch; do not close it now. However it is NO LONGER the target candidate:

1. on dispatch, verify identity and record it as `PRIOR WARM REFERENCE SERVICE`;
2. to switch, stop only the Task-owned Attempt-003 service (never other workloads);
3. launch the new 0.95 / 67000 target candidate;
4. complete graph capture / readiness / capacity gate;
5. then run the 64K benchmark.

Never benchmark the 0.97/70000 service as the 64K candidate.

## 8. 64K benchmark contract (UNCHANGED)

- input 65536; output 1024; concurrency 64; num-prompts 256; dataset random; range-ratio 0; inf; ignore-eos; endpoint /v1/completions; client vllm bench serve
- Run1 warmup/discard; Run2 measured; gate metric = Total Token Throughput
- accepted baseline 927.59; active 80% target (D-024 basis 6016/15824; H100 64K ref 5054.66) = 1537.35 tok/s (machine recompute)

Do NOT modify the workload because max-model-len changed 70000->67000.

## 9. Result record (+ evidence)

Evidence / Runner Report must record:

REQUESTED_INPUT_TOKENS=65536
REQUESTED_OUTPUT_TOKENS=1024
REQUIRED_TOTAL_SEQUENCE_CAPACITY=66560
EFFECTIVE_MAX_MODEL_LEN=<actual>
GPU_MEMORY_UTILIZATION=0.95
CAPACITY_MARGIN_TOKENS=<effective_max_model_len - 66560>
KV cache evidence

this can prove full 64K + 1K workload support even though max-model-len < 70000.

Fill per attempt: attempt-xxx.md (OBJECTIVE/OBSERVED/HYPOTHESIS/PARAMS_BEFORE/CHANGED/AFTER/REASON/EVIDENCE/EXACT_CMD/START/END/CAPACITY_RESULT/64K_RESULT/NEXT). `optimization-summary-64k.txt` with Attempt/Effective profile/Capacity/64K total/delta vs 927/58/disposition.

## 10. Autonomy + STOP conditions

Same autonomous policy as parent (diagnose/modify/retry; multiple param bundles OK; DIAGNOSTIC ONLY marks). In this Task:

- never raise util > 0.95
- never go below floor 66560
- MTP stays OFF, capture 96 preferred
- True STOP (return to user) incl. the 0.95-insufficient token

## 11. Governance

- 64K Task stays exploratory; formal OPT-01 remains BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION
- no Formal Result; D-022 evidence; STATUS READY / PENDING USERDISPATCH