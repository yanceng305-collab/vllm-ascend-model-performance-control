# A3PerfRunner Prompt: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP

**For Task**: TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP  
**Runner Role**: A3PerfRunner — AUTONOMOUS PERFORMANCE OPTIMIZATION RUNNER  
**Created**: 2026-09-02

---

## Role

You produce Evidence only; you do NOT commit/push the Control repo (Release assets per D-022 allowed), no Formal Results, no Acceptance.

## Purpose

Validate the reviewed Attempt-003 candidate under the project 64K workload: capacity/correctness/256-0/performance vs accepted 64K baseline 927.59 tok/s. No auto anything beyond the single 64K two-run.

## Step 1 — Dispatch

```text
Task ID: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```
only with all three.

## Step 2 — Service reuse check (preferred path)

Current warm Attempt-003 service: PID 257285, port 8000, log /workspace/glm52_od_attempt003.log, SERVICE_LEFT_RUNNING=YES (from prior Evidence).

1. `ps -p 257285 -o pid,cmd` / `ss -ltnp | grep :8000` and `curl /v1/models`; note PID/cmdline/served model; identify actual env; 
2. verify: gpu-memory-utilization=0.97, max_cudagraph_capture_size=96, max-num-seqs=48, batched=4096, MTP off, async on, multistream on, DP2/TP8/EP, max-len >= 70000 (read effective config; log signature).
3. If the live service EXACTLY matches your reviewed candidate: REUSE. No restart, no re-graph-capture. Proceed Step 3 directly. 
4. If service missing / identity mismatch / profile mismatch: restore the reviewed candidate (bounded autonomous remediation within HARD BOUNDARIES, same adjustable set; keep max-model-len >= 70000), record restoration evidence.
5. Do NOT stop other workloads. Only touch this Task's service.

## Step 3 — 64K benchmark (Run1 warmup / Run2 measured)

```bash
BASE_URL="http://127.0.0.1:8000"
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
SERVED_MODEL="glm52-w8a8"
RESULT_DIR="<TASK_EVIDENCE_DIR>/benchmark-64k"
mkdir -p "$RESULT_DIR"
for RUN in 1 2; do
  vllm bench serve --backend vllm --base-url "$BASE_URL" --endpoint /v1/completions \
    --model "$SERVED_MODEL" --tokenizer "$MODEL_PATH" --trust-remote-code \
    --dataset-name random --random-input-len 65536 --random-output-len 1024 \
    --random-range-ratio 0 --request-rate inf --max-concurrency 64 --num-prompts 256 \
    --ignore-eos --save-result --result-dir "$RESULT_DIR" --result-filename "run${RUN}.json" \
    2>&1 | tee "$RESULT_DIR/run${RUN}.log"
done
```

## Step 4 — machine metrics

Run2 machine extraction (from summary + raw log if json writer bug):
- SUCCESSFUL_REQUESTS=256, FAILED=0
- TOTAL_TOKEN_THROUGHPUT
- OUTPUT_TOKEN_THROUGHPUT, REQUEST_THROUGHPUT, DURATION
- DELTA 64K = (TOTAL_TOKEN_THROUGHPUT/927.59 - 1)*100 (machine)
- 80% absolute target vs active D-024 basis (6016/15824; H100 64K reference 5054.66): recompute 5054.66/15824*6016*0.80 = 1537.35.

Disposition: `64K_FOLLOWUP_PASS` (>=1537.35) / IMPROVED_BELOW_TARGET / NO_IMPROVEMENT / INVALID_OR_ROLLBACK_CANDIDATE. If correctness issue or device errors: record + classification per gates.

## Step 5 — Autonomous if recoverable

Recoverable issues (OOM/KV/graph/scheduler/launch/perf) are feedback: diagnose/modify/retry within Hard Boundaries; record reason/evolute per attempt; never lower max-model-len<70000 for the final; DIAGNOSTIC ONLY labels for any smaller context.

True STOP → user only per parent boundary list.

## Step 6 — wrap-up

`.tar.gz` evidence (incl 64K logs + summary + control-sha + profile)/SHA256SUMS/MANIFEST upload to GitHub Release (D-022). RUNNER REPORT with: outcome, delta vs 927.59, 64K correction, service state. Default leave service running when PASS/IMPROVED: provide PID/port/log.