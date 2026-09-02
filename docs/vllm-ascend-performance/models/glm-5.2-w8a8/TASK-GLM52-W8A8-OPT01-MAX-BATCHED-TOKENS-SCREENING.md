# TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING

**Task ID**: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING  
**Task Type**: FAST MICROGATE Optimization Screening  
**Status**: READY  
**Created**: 2026-09-02  
**Assigned to**: A3PerfRunner  
**Priority**: HIGH

**READY status**: Task prepared, awaiting User explicit dispatch (Task ID + DISPATCH_CONTROL_SHA + Authorization: EXECUTE).

---

## Objective

Test candidate value for `--max-num-batched-tokens` parameter using 16K FAST MICROGATE protocol to determine if it merits full validation.

**Hypothesis**: Increasing max-num-batched-tokens from baseline may improve batching efficiency and throughput, based on historical 910B "参数优化" signals suggesting scheduler/batching tuning is effective.

---

## Background

**Current A3 Baseline** (Evidence-backed, formally accepted):
- 16K baseline: **957.94 tok/s** (Mean of Run2/3/4)
- Runtime: vLLM 0.24.0+empty, Image nightly-releases-v0.24.0rc-a3
- Container: model-test-zyg-a3

**Historical Reference** (910B multi-node, NOT directly transferable):
- "参数优化" stages showed 7-12% incremental gains over pooling baseline
- Scheduler/batching parameters likely candidates (CONFOUNDED historical signal)

**OPT-01 Selection Rationale**:
1. Single variable: `--max-num-batched-tokens` only
2. Scheduler/batching most transferable from 910B experience
3. Baseline value needs verification (assume vLLM default)
4. Runtime capability verified (supported in vLLM 0.24)

---

## Scope

### Single Variable Change

**Primary Variable**: `--max-num-batched-tokens`

**Baseline Value**: 131072 (vLLM 0.24 default for long-context, to be verified in preflight)

**Candidate Value**: 262144 (2x baseline)

**Rationale**: 
- 16K input + 1K output = 17K tokens per request
- Baseline 131K allows ~7-8 concurrent requests in preflight batching
- Candidate 262K allows ~15 concurrent requests
- Should improve batching efficiency if scheduler can fill batches

### Unchanged Controls

ALL other parameters identical to accepted baseline:
- Model: GLM-5.2-W8A8
- Runtime: vLLM 0.24.0+empty, same image/container
- TP: 16
- max-model-len: 131072
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

**Pass Criteria**:
- Improvement ≥ 5%: **FAST_MICROGATE_PASS** → proceed to 64K validation
- Improvement 2-5%: **FAST_MICROGATE_INCONCLUSIVE** → add confirmation run
- Improvement < 2%: **NO_MATERIAL_GAIN** → stop candidate

**Rollback Criteria** (immediate stop):
- Throughput regression
- Requests failed > 0
- OOM / service crash
- Runtime instability
- Correctness anomaly

---

## Execution Steps

### 1. Preflight (Read-Only)

Verify current baseline value:
```bash
# Check running service launch command
ps aux | grep vllm
# Or check server logs for --max-num-batched-tokens value
```

**Expected**: 131072 (default) or explicit value
**If different**: Record actual baseline value, adjust candidate accordingly

### 2. Service Restart with Candidate Value

Stop existing service, restart with:
```bash
--max-num-batched-tokens 262144
```

All other args unchanged from baseline.

**Wait**: 2 minutes for service stabilization

### 3. Run Baseline Warmup (Run1)

```bash
python benchmark_serving.py \
  --backend vllm \
  --model /data/tiankuan/zyg/model/GLM-5.2-w8a8 \
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
```

**Decision**:
- ≥5%: PASS
- 2-5%: INCONCLUSIVE (add Run3 confirmation if needed)
- <2%: NO_MATERIAL_GAIN

### 6. Rollback

Restart service with baseline args (max-num-batched-tokens=131072 or omit for default).

---

## Evidence Package

**Screening Evidence** (not formal baseline replacement):
- Run1 output (warmup, discarded)
- Run2 output (screening measurement)
- Runtime identity (confirm unchanged from baseline)
- Exact launch command with candidate value
- Baseline value recorded
- Completed/failed counts
- DISPATCH_CONTROL_SHA

**Transport**: Per D-022, upload as GitHub Release Asset if PASS

**Evidence Type**: `SCREENING EVIDENCE — NOT FORMAL BASELINE`

---

## Success Criteria

**Primary**: Screening run completes successfully, decision rendered (PASS/INCONCLUSIVE/NO_MATERIAL_GAIN)

**Secondary** (if PASS): Evidence package created for PerfControl review

---

## Constraints

- Single variable only (max-num-batched-tokens)
- Read baseline value before changing
- 16K FAST MICROGATE only (not full matrix)
- 2-run protocol (warmup + measured)
- Rollback to baseline after completion
- Do NOT commit Control repo
- Do NOT author Formal Results

---

## Next Steps After PASS

If OPT-01 achieves FAST_MICROGATE_PASS:
1. PerfControl reviews screening Evidence
2. Candidate promoted to 64K validation
3. If 64K also shows improvement, proceed to full 4-cell formal validation (1K/4K/16K/64K)
4. Only then: machine-verified Formal Results per D-023

---

## References

- Historical reference: `references/HISTORICAL-910B-MULTINODE-OPTIMIZATION-REFERENCE.md`
- Baseline Results: `results/RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958.md`
- D-020: Hardware normalization
- D-021: PerfControl/A3PerfRunner separation
- D-022: GitHub Release Asset Evidence Transport
- D-023: Machine-Verified Formal Result Gate
