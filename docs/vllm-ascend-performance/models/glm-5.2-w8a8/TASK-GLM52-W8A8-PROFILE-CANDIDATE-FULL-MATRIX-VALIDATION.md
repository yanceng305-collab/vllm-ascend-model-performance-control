# TASK-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION

**Task ID**: GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION  
**Task Type**: PROFILE-LEVEL OPTIMIZATION CANDIDATE — FULL MATRIX validation (formal 4-run)  
**Status**: READY / PENDING USER DISPATCH  
**Created**: 2026-09-03  
**Requires**: Evidence Review PASS of 64K FOLLOW-UP (`EVIDENCE-REVIEW-64K-FOLLOWUP-20260903.md`)  
**Assigned to**: A3PerfRunner  
**Priority**: HIGH

## 1. Governance

- This is a PROFILE-LEVEL optimization candidate validation. It is NOT Formal OPT-01.
- Formal OPT-01 remains `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION` (historical; not unlocked).
- No automatic parameter tuning in this Task: the profile is FROZEN across all four cells.
- No Formal Result is authored in this Task; PerfControl review precedes any machine-generated Formal Candidate Result / Acceptance.

## 2. Frozen candidate profile (identical for all four cells)

| Item | Value |
|---|---|
| model | GLM-5.2-W8A8 |
| model path | /data/tiankuan/zyg/model/GLM-5.2-w8a8 |
| runtime family | nightly-releases-v0.24.0rc-a3 image / vLLM 0.24 (unchanged) |
| gpu-memory-utilization | 0.95 |
| max-model-len | 67000 |
| (note) | 67000 >= required 66560 (64K input+1K output) |
| max_cudagraph_capture_size | 96 |
| MTP / speculative | OFF |
| DP / TP / EP | 2 / 8 / ON |
| max-num-seqs | 48 |
| max-num-batched-tokens | 4096 |
| async scheduling | ON |
| multistream_overlap_shared_expert | ON |
| cudagraph | FULL_DECODE_ONLY |
| prefix cache | OFF |
| HCCL/OMP/allocator/env | inherit the reviewed 64K candidate actual effective profile |

Do NOT tune per-cell for speed: the four cells MUST use the same effective profile.

## 3. Full matrix contract (per cell: same workload contract as accepted baseline)

| Cell | input | output |
|---|---|---|
| 1K-1K | 1024 | 1024 |
| 4K-1K | 4096 | 1024 |
| 16K-1K | 16384 | 1024 |
| 64K-1K | 65536 | 1024 |

All cells: concurrency 64, num-prompts 256, dataset random, random-range-ratio 0, request-rate inf, ignore-eos true, endpoint /v1/completions, client `vllm bench serve`.

Runs per cell: Run1 warmup/discard; Run2, Run3, Run4 measured. Formal value = Mean(Run2, Run3, Run4).

Order recommended: 1K -> 4K -> 16K -> 64K. Do not skip to reuse exploratory data.

## 4. Warm service reuse (preferred)

Current reviewed service (from 64K review):


SERVICE_LEFT_RUNNING=YES  PID 3164838  PORT 8000  LOG /workspace/glm52_od_64k_candidate.log
(profile 0.95/67000/cap96/MTP OFF/DP2/TP8/EP /async/multistream/OFF-prefix)

Prompt flow:

1. verify: service alive (PID/cmdline/API /v1/models), model identity, gpu-memory-utilization=0.95, max-model-len=67000, capture=96, MTP OFF, DP2/TP8/EP, 48/4096, async, multistream, FULL_DECODE_ONLY, prefix OFF;
2. if all match -> REUSE CURRENT WARM SERVICE (no restart, no re-graph-capture);
3. if absent/mismatch -> restore the same frozen candidate (no unplanned tuning).

## 5. Machine artifacts & JSON writer

- If vllm `--save-result` produces runN.json normally: keep it (raw + machine-readable proof).
- If runN.json is 0-byte / missing: record writer anomaly; formal validation still passes when `runN.log` + `runN.metrics.json` + validator all PASS.
- RAW SOURCE: `runN.log`
- MACHINE DERIVED: `runN.metrics.json` via `scripts/extract_bench_metrics.py`
- Do NOT modify vLLM runtime/site-packages/image to fix the writer (would change runtime identity).

## 6. D-023 machine gate extension

Before any Formal acceptance, run per cell:
`python scripts/validate_matrix_candidate.py --cell-dir <cell_dir> --cell <CELL>`

Validator checks:
1. metrics JSON is deterministically regenerable from runN.log;
2. successful_requests == 256 and failed_requests == 0 for Run2/3/4;
3. workload/contract token for the cell present in each run log (input/output/concurrency/prompts/ignore_eos);
4. Run1 explicitly discarded (never in the mean);
5. mean = mean(Run2,3,4) machine-computed;
6. raw values agree with the generated Formal Candidate Result;
7. runtime identity / effective profile identical across the four cells;
8. baseline raw/delta/normalized achievement/80% target all machine-computed (D-024 basis 6016/15824).

## 7. STOP / INVALID policy (formal validation)

- Client client wedge: allow to discard only that run attempt (ABORTED/INVALID) and re-run the same run on the same profile.
- Engine crash / device error / OOM / KV rejection / profile mismatch / correctness failure: do NOT change parameters to rescue;
record evidence and FAIL/STOP per formal candidate validation rules (proves frozen-profile stability).

## 8. Stability metrics (per cell)

Report per measured run (Run2/3/4): total token throughput, output token throughput, mean/P99 TTFT, mean/P99 TPOT, mean ITL, successful/failed. Also compute across Run2-4: min / max / mean / stddev / CV%.

## 9. Acceptance values (machine computed, D-024)

- D-024: A3=6016, H100=15824.
- Accepted baseline: 1K=676.60, 4K=820.76, 16K=957.94, 64K=927.59.
- H100 refs: 1K=2688.71, 4K=4063.45, 16K=4379.60, 64K=5054.66.
- 80% target per cell: machine computed.
- candidate mean / delta / normalized achievement: machine computed; never handwritten.

## 10. Task status / next

Status stays `READY / PENDING USER DISPATCH` until User dispatches with DISPATCH_CONTROL_SHA. Keep the current warm service running.