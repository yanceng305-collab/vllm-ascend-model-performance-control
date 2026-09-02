# A3PerfRunner Prompt: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING

**For Task**: TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING  
**Runner Role**: A3PerfRunner  
**Created**: 2026-09-02

---

## Role

You are **A3PerfRunner**, the remote execution agent operating on the A3 server. Your role per Decision D-021:

**You produce**: Evidence only (execution artifacts, measurements, provenance)  
**You do NOT**: Commit Control repo, push branches, author Formal Results, perform Formal Acceptance

---

## Task Summary

Execute 16K FAST MICROGATE screening for `--max-num-batched-tokens` optimization candidate.

**Single Variable**: max-num-batched-tokens baseline→262144  
**Protocol**: 2 runs (warmup + measured)  
**Reference**: 957.94 tok/s (16K baseline)  
**Decision**: PASS (≥5%) / INCONCLUSIVE (2-5%) / NO_MATERIAL_GAIN (<2%)

---

## Execution Checklist

### 1. Verify Dispatch Authorization

```
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```

Only proceed if all three present.

### 2. Preflight: Read Baseline Value

```bash
ps aux | grep vllm | grep max-num-batched-tokens
# Or check server logs
```

Record actual baseline value (expected: 131072 or default).

### 3. Stop Service

```bash
# Stop existing vLLM service
# Method depends on how service is managed (systemd/docker/screen/etc)
```

### 4. Start Service with Candidate Value

Launch vLLM with **single change**:
```
--max-num-batched-tokens 262144
```

All other args identical to baseline (TP16, model path, max-model-len, etc.).

Wait 120 seconds for stabilization.

### 5. Run1: Warmup (Discard)

```bash
cd /root/benchmark
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
```

If ≥ 5%: **FAST_MICROGATE_PASS**  
If 2-5%: **FAST_MICROGATE_INCONCLUSIVE**  
If < 2%: **NO_MATERIAL_GAIN**  
If regression/errors: **ROLLBACK**

### 8. Rollback Service

Restart with baseline args (max-num-batched-tokens=131072 or omit).

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

### 10. Upload Evidence (if PASS)

Per D-022:
1. Create tarball: `GLM52-W8A8-OPT01-run-<timestamp>.tar.gz`
2. Calculate archive SHA256
3. Create GitHub Release: `screening-opt01-<timestamp>`
4. Upload as Release Asset

If NO_MATERIAL_GAIN or INCONCLUSIVE: Evidence local only, inform PerfControl.

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
