# A3PerfRunner Prompt: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING

**For Task**: TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING  
**Runner Role**: A3PerfRunner  
**Created**: 2026-09-02  
**Updated**: 2026-09-02  
**Status**: BLOCKED_PENDING_PREFLIGHT

**BLOCKED**: This prompt cannot be executed until preflight task (GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT) completes and PerfControl updates this prompt with verified baseline value and selected candidate.

---

## Prerequisites

Before this prompt becomes executable:

1. ✅ Preflight task completes (GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT)
2. ✅ PerfControl reviews preflight Evidence
3. ✅ Baseline max_num_batched_tokens value verified
4. ✅ Candidate value selected by PerfControl
5. ✅ This prompt updated with actual baseline/candidate values
6. ✅ Task status changed from BLOCKED to READY

**Do NOT execute this prompt in its current state.**

---

## Role

You are **A3PerfRunner**, the remote execution agent operating on the A3 server. Your role per Decision D-021:

**You produce**: Evidence only (execution artifacts, measurements, provenance)  
**You do NOT**: Commit Control repo, push branches, author Formal Results, perform Formal Acceptance

---

## Task Summary

Execute 16K FAST MICROGATE screening for `--max-num-batched-tokens` optimization candidate.

**Single Variable**: max-num-batched-tokens  
**Baseline Value**: PENDING_PREFLIGHT_VERIFICATION  
**Candidate Value**: PENDING_PREFLIGHT_VERIFICATION  
**Protocol**: 2 runs (warmup + measured)  
**Reference**: 957.94 tok/s (16K baseline)  
**Thresholds**: 2% = 977.10 tok/s, 5% = 1005.84 tok/s  
**Decision**: PASS (≥5%) / INCONCLUSIVE (2-5%) / NO_MATERIAL_GAIN (<2%)

**NOTE**: Baseline and candidate values will be populated after preflight completes.

---

## Execution Checklist

**⚠️ BLOCKED**: The steps below contain placeholder values and cannot be executed until preflight completes and PerfControl updates this prompt with actual baseline/candidate values.

### 1. Verify Dispatch Authorization

```
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```

Only proceed if all three present.

### 2. Preflight: Read Baseline Value

**REPLACED BY SEPARATE PREFLIGHT TASK**: See GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT

Baseline value will be provided by PerfControl after preflight Evidence review.

**If baseline value differs from what PerfControl documented here**: STOP and report discrepancy. Do NOT adjust candidate on your own.

### 3. Stop Service

**PENDING**: Exact stop procedure to be confirmed

Stop the existing vLLM baseline service.

Verify service stopped:
```bash
ps aux | grep "vllm serve" | grep GLM-5.2-w8a8
# Should return empty
```

### 4. Start Service with Candidate Value

**PENDING**: Candidate value from PerfControl after preflight

Launch vLLM with **single change**:
```bash
--max-num-batched-tokens <CANDIDATE_VALUE_TBD>
```

All other args identical to baseline (TP16, model path, max-model-len 70000, etc.).

Wait 120 seconds for stabilization.

### 5. Run1: Warmup (Discard)

**CORRECTED**: Use frozen baseline benchmark client

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

Label output: `run1-warmup-discarded.log`

### 6. Run2: Screening Measurement

Same command. Label: `run2-screening.log`

Extract:
- Total token throughput (tok/s)
- Completed count (must == 256)
- Failed count (must == 0)
- TTFT avg, P90
- TPOT avg, P90

### 7. Calculate Decision

```
Improvement = (Run2_throughput / 957.94) - 1
Improvement_percentage = Improvement × 100%
```

**Thresholds**:
- If ≥ 1005.84 tok/s (≥5%): **FAST_MICROGATE_PASS**  
- If 977.10-1005.84 tok/s (2-5%): **FAST_MICROGATE_INCONCLUSIVE**  
- If < 977.10 tok/s (<2%): **NO_MATERIAL_GAIN**  
- If regression/errors: **ROLLBACK**

### 8. Rollback Service

Restart with baseline args (restore original max-num-batched-tokens value, or omit if it was default).

### 9. Create Evidence Package

**Directory structure**:
```
GLM52-W8A8-OPT01-run-<timestamp>/
├── runtime-identity.txt
├── control-sha.txt
├── launch-command.txt
├── baseline-value.txt
├── candidate-value.txt
├── run1-warmup-discarded.log
├── run2-screening.log
├── screening-decision.txt
├── MANIFEST.txt
└── SHA256SUMS.txt
```

**runtime-identity.txt**: Container ID, image, vLLM version (verify unchanged from baseline)

**control-sha.txt**:
```
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING
DISPATCH_CONTROL_SHA: <actual>
Authorization: EXECUTE
```

**baseline-value.txt**: Recorded baseline max-num-batched-tokens

**candidate-value.txt**: 262144

**screening-decision.txt**:
```
Reference: 957.94 tok/s
Run2: <actual> tok/s
Improvement: <percentage>
Decision: PASS / INCONCLUSIVE / NO_MATERIAL_GAIN
```

**MANIFEST.txt**: List all files with timestamps

**SHA256SUMS.txt**: SHA256 of each file

### 10. Upload Evidence (regardless of outcome)

Per D-022:
1. Create tarball: `GLM52-W8A8-OPT01-run-<timestamp>.tar.gz`
2. Calculate archive SHA256
3. Create GitHub Release: `screening-opt01-<timestamp>`
4. Upload as Release Asset

**Upload ALL screening Evidence regardless of outcome** (PASS/INCONCLUSIVE/NO_MATERIAL_GAIN/ROLLBACK). Failed experiments prevent future duplication of unproductive optimization paths.

### 11. Runner Report

Create brief report:
```markdown
# A3PerfRunner Report: OPT01 Screening

**Task**: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING
**Status**: <COMPLETE / ROLLBACK>
**Decision**: <PASS / INCONCLUSIVE / NO_MATERIAL_GAIN>

**Baseline**: max-num-batched-tokens=<actual>
**Candidate**: max-num-batched-tokens=262144
**Reference**: 957.94 tok/s
**Run2**: <actual> tok/s
**Improvement**: <percentage>

**Evidence**: <GitHub Release URL if uploaded, or "Local only">
**Archive SHA256**: <hash if uploaded>

**Rollback**: Service restored to baseline
```

---

## Constraints

- Do NOT commit Control repo
- Do NOT push Control branches  
- Do NOT author Formal Results
- Do NOT perform Formal Acceptance
- Only produce: Evidence + Runner Report
- Single variable change only
- Rollback service after completion

---

## Rollback Triggers

Stop immediately and rollback if:
- Failed > 0
- OOM / service crash
- Throughput regression
- Runtime instability

Report rollback reason to PerfControl.

---

## Success Criteria

1. Screening run completes
2. Decision rendered
3. Evidence captured (upload if PASS)
4. Service rolled back to baseline
5. Runner Report delivered

---

## References

- Task: `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING.md`
- Historical reference: `HISTORICAL-910B-MULTINODE-OPTIMIZATION-REFERENCE.md`
- D-021: Runner produces Evidence only
- D-022: GitHub Release Asset Evidence Transport
