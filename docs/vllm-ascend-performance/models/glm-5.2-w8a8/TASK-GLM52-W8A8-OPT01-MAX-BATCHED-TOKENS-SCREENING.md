# TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING

**Task ID**: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING  
**Task Type**: FAST MICROGATE Optimization Screening  
**Status**: BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION  
**Created**: 2026-09-02  
**Updated**: 2026-09-02  
**Assigned to**: A3PerfRunner  
**Priority**: HIGH

**BLOCKED status**: Preflight GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT completed 2026-09-02 with outcome `RUNTIME_IDENTITY_MISMATCH` (Gate A `NO_PROCESS`) — the accepted GLM-5.2-W8A8 baseline runtime was NOT active at observation time, so effective `max_num_batched_tokens` remains **UNVERIFIED**. Candidate selection is **NOT AUTHORIZED / NOT YET POSSIBLE**. Screening cannot start until the accepted GLM baseline runtime is restored (User-authorized server state change) and the effective value is re-observed and verified.

**Status update (2026-09-02, later)**: preflight found NO_PROCESS (correct at that time). User since manually restored an operating GLM-5.2-W8A8 runtime variant, but it is NOT an exact replay of the accepted baseline; effective `max_num_batched_tokens` remains UNVERIFIED; a manual exploratory 16K microgate (Run1 warmup + Run2 measured) is IN PROGRESS /  RESULT PENDING; formal screening remains BLOCKED; candidate selection NOT YET POSSIBLE until review of the manual observation. See `MANUAL-RUNTIME-OBSERVATION-20260902.md`.

---

## Objective

Test candidate value for `--max-num-batched-tokens` parameter using 16K FAST MICROGATE protocol to determine if it merits full validation.

**Hypothesis**: Increasing max-num-batched-tokens from baseline may improve batching efficiency and throughput, based on historical 910B "参数优化" signals suggesting scheduler/batching tuning is effective.

---

## Background

**Current A3 Baseline** (Evidence-backed, formally accepted):
- 16K baseline: **957.94 tok/s** (Mean of Run2/3/4)
- Runtime: vLLM 0.24.0+empty, vLLM-Ascend 0.19.1rc2.dev1157+g6443b2a38
- Image: quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3
- Container: model-test-zyg-a3
- max-model-len: **70000** (frozen baseline)
- TP: 16

**Historical Reference** (910B multi-node, NOT directly transferable):
- "参数优化" stages showed 7-12% incremental gains over pooling baseline
- Multiple parameters changed simultaneously (CONFOUNDED experiments)
- Actual historical parameter differences from Excel:
  - 池化→参数优化1: max-num-batched-tokens 4096→2048, max-num-seqs 8, speculative tokens 5→4, cudagraph_capture_sizes added [1,2,4,8,12,16]
  - 参数优化1→参数优化2: added enable_fused_mc2, enable_npugraph_ex, expanded cudagraph sizes
  - 参数优化2→参数优化3: added enable_flashcomm1, simplified cudagraph sizes [40,80]
- **CONFOUNDED SIGNAL**: Cannot attribute gains to any single parameter change
- Scheduler/batching parameters are hypothesis only (NOT isolated validation)

**OPT-01 Selection Rationale**:
1. Single variable: `--max-num-batched-tokens` only
2. Scheduler/batching hypothesis from 910B experience (requires independent A3 validation)
3. **Baseline value UNVERIFIED** - requires preflight observation
4. Runtime capability verified (supported in vLLM 0.24)
5. **Candidate selection PENDING** until baseline value verified

---

## Scope

### Single Variable Change

**Primary Variable**: `--max-num-batched-tokens`

**Baseline Value**: UNVERIFIED - requires preflight observation (see GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT)

**Candidate Value**: PENDING baseline value verification

**Candidate Selection Strategy** (after preflight):
- Candidate will be selected based on verified baseline value
- Selection will consider: current runtime capability, workload characteristics (16K input + 1K output), and 910B historical signals (hypothesis only)
- Candidate design by PerfControl after preflight Evidence review

### Unchanged Controls

ALL other parameters identical to accepted baseline:
- Model: GLM-5.2-W8A8
- Runtime: vLLM 0.24.0+empty, same image/container
- TP: 16
- max-model-len: **70000** (frozen baseline)
- Input: 16384 tokens
- Output: 1024 tokens
- Concurrency: 64
- Num prompts: 256
- Dataset: random
- Endpoint: /v1/completions
- ignore-eos: true
- request-rate: inf
- All other vLLM launch args unchanged

---

## FAST MICROGATE Protocol

**Screening Workload**: 16K cell only (not full 1K/4K/16K/64K matrix)

**Run Protocol**:
- **Run 1**: Warmup, discard
- **Run 2**: Measured screening run

**Screening Reference**: 957.94 tok/s (16K baseline)

**Pass Thresholds**:
- **2% threshold**: 977.10 tok/s
- **5% threshold**: 1005.84 tok/s

**Pass Criteria**:
- Improvement ≥ 5% (≥1005.84 tok/s): **FAST_MICROGATE_PASS** → proceed to 64K validation
- Improvement 2-5% (977.10-1005.84 tok/s): **FAST_MICROGATE_INCONCLUSIVE** → add confirmation run
- Improvement < 2% (<977.10 tok/s): **NO_MATERIAL_GAIN** → stop candidate

**Rollback Criteria** (immediate stop):
- Throughput regression
- Requests failed > 0
- OOM / service crash
- Runtime instability
- Correctness anomaly

---

## Execution Steps

**NOTE**: This task is currently BLOCKED pending baseline value preflight. The steps below will be finalized after preflight completes and candidate is selected.

### 1. Preflight (Separate Task)

See: `GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT.md`

Preflight will determine actual baseline max_num_batched_tokens value through read-only observation.

### 2. Service Restart with Candidate Value

**PENDING**: Candidate value selection after preflight

Stop existing service, restart with candidate max-num-batched-tokens value.

All other args unchanged from baseline.

**Wait**: 2 minutes for service stabilization

### 3. Run Baseline Warmup (Run1)

```bash
vllm bench serve \
  /data/tiankuan/zyg/model/GLM-5.2-w8a8 \
  --backend vllm \
  --endpoint /v1/completions \
  --dataset-name random \
  --random-input-len 16384 \
  --random-output-len 1024 \
  --random-range-ratio 0 \
  --num-prompts 256 \
  --request-rate inf \
  --max-concurrency 64 \
  --ignore-eos
```

**Warmup**: Discard Run1 output

### 4. Run Screening Measurement (Run2)

Same command, Run2 = measured screening run.

**Capture**:
- Full benchmark output
- Total token throughput
- TTFT avg/P90
- TPOT avg/P90
- Completed/failed counts
- Any errors

### 5. Calculate Improvement

```
Improvement = (Run2_throughput / 957.94) - 1
Improvement_percentage = Improvement × 100%
```

**Decision**:
- ≥5% (≥1005.84 tok/s): PASS
- 2-5% (977.10-1005.84 tok/s): INCONCLUSIVE (add Run3 confirmation if needed)
- <2% (<977.10 tok/s): NO_MATERIAL_GAIN
- Regression or errors: ROLLBACK

### 6. Rollback

Restart service with baseline args (restore original max-num-batched-tokens value or omit if it was default).

---

## Evidence Package

**Screening Evidence** (not formal baseline replacement):
- Run1 output (warmup, discarded)
- Run2 output (screening measurement)
- Runtime identity (confirm unchanged from baseline)
- Exact launch command with candidate value
- Baseline value recorded from preflight
- Candidate value used
- Completed/failed counts
- DISPATCH_CONTROL_SHA

**Transport**: Per D-022, upload as GitHub Release Asset regardless of outcome (PASS/INCONCLUSIVE/NO_MATERIAL_GAIN/ROLLBACK)

**Evidence Type**: `SCREENING EVIDENCE — NOT FORMAL BASELINE`

**Preservation rationale**: All optimization attempts (successful or not) provide valuable learning. Failed experiments prevent future duplication of unproductive paths.

---

## Success Criteria

**Primary**: Screening run completes successfully, decision rendered (PASS/INCONCLUSIVE/NO_MATERIAL_GAIN)

**Secondary** (if PASS): Evidence package created for PerfControl review

---

## Constraints

- Single variable only (max-num-batched-tokens)
- Baseline value must be verified via preflight before execution
- Candidate selection by PerfControl after preflight review
- 16K FAST MICROGATE only (not full matrix)
- 2-run protocol (warmup + measured)
- Benchmark client: `vllm bench serve` (inherit from frozen baseline)
- Rollback to baseline after completion
- Do NOT commit Control repo
- Do NOT author Formal Results
- Evidence upload regardless of outcome

---

## Next Steps After PASS

If OPT-01 achieves FAST_MICROGATE_PASS:
1. PerfControl reviews screening Evidence
2. Candidate promoted to 64K validation
3. If 64K also shows improvement, proceed to full 4-cell formal validation (1K/4K/16K/64K)
4. Only then: machine-verified Formal Results per D-023

---

## Prerequisites

**BLOCKED until**:
- GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT completes
- PerfControl reviews preflight Evidence
- Baseline value verified
- Candidate value selected and documented
- This Task updated to READY status

---

## References

- Preflight Task: `GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT.md`
- Historical reference: `references/HISTORICAL-910B-MULTINODE-OPTIMIZATION-REFERENCE.md`
- Baseline: `BASELINE.md`
- Baseline Results: `results/RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958.md`
- D-020: Hardware normalization
- D-021: PerfControl/A3PerfRunner separation
- D-022: GitHub Release Asset Evidence Transport
- D-023: Machine-Verified Formal Result Gate
