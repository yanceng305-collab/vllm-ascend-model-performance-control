# A3PerfRunner Prompt: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP

**For Task**: TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP  
**Runner Role**: A3PerfRunner - AUTONOMOUS PERFORMANCE OPTIMIZATION RUNNER  
**Created**: 2026-09-02  
**Revision**: 2026-09-02 (candidate 0.95 / 67000; floor 66560; MTP OFF)

---

## Role
You produce Evidence only; no Control commit/push (Release assets D-022 only), no Formal Result, no Acceptance.

## Purpose

Validate the ATTEMPT-003-DERIVED MEMORY-HEADROOM 64K CANDIDATE: gpu-memory-utilization 0.95, max-model-len 67000 (floor 66560), capture 96, MTP OFF, DP2/TP8/EP/etc. - under the fixed project 64K workload (65536+1024), vs accepted baseline 927.59 tok/s / 80% target 1537.35.

## Step 1 - Dispatch

Task ID, DISPATCH_CONTROL_SHA, `Authorization: EXECUTE` - all three required.

## Step 2 - Warm reference + switch

1. Verify the current warm Attempt-003 service (PID 257285, port 8000, /workspace/glm52_od_attempt003.log, registry/ps/API).
2. Record identity into `prior-warm-reference.txt` as `PRIOR WARM REFERENCE SERVICE` (0.97/70000, Attempt-003).
3. To switch: stop ONLY the Task-owned Attempt-003 service; never other workloads.
4. Launch the NEW target candidate (Step 3). No 64K runs against the prior service.

## Step 3 - Launch new target candidate

```bash
unset VLLM_VERSION
unset LD_PRELOAD
unset VLLM_ASCEND_ENABLE_FLASHCOMM1
unset VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE
unset ASCEND_LAUNCH_BLOCKING

export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
export HCCL_OP_EXPANSION_MODE="AIV"
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export HCCL_BUFFSIZE=200
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export VLLM_ASCEND_BALANCE_SCHEDULING=1
export VLLM_ASCEND_ENABLE_MLAPO=1

MODEL="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
LOG_PATH="/workspace/glm52_od_64k_candidate.log"

nohup vllm serve "$MODEL" \
  --host 0.0.0.0 --port 8000 --served-model-name glm52-w8a8 \
  --trust-remote-code --seed 1024 \
  --data-parallel-size 2 --tensor-parallel-size 8 --enable-expert-parallel \
  --max-model-len 67000 --max-num-seqs 48 --max-num-batched-tokens 4096 \
  --gpu-memory-utilization 0.95 --quantization ascend --async-scheduling \
  --additional-config '{"multistream_overlap_shared_expert": true}' \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY", "max_cudagraph_capture_size": 96}' \
  --no-enable-prefix-caching --no-enable-log-requests \
  > "$LOG_PATH" 2>&1 &
```## Step 4 - Capacity gate (must pass before 64K)

Verify with evidence:

- gpu-memory-utilization = 0.95 (fixed target; do NOT raise > 0.95)
- max-model-len >= 66560 (initial 67000; converge 67000 -> 66800 -> 66600 -> 66560 if KV tight; floor 66560)
- capture = 96; MTP OFF; DP2/TP8/EP; batched 4096; seqs 48; async ON; multistream ON; FULL_DECODE_ONLY; prefix OFF
- API READY (/v1/models)
- no KV rejection, no fatal OOM, no device correctness error

`capacity-gate.txt` + `graph-capture-evidence.txt`. CAPACITY PASS only then.

If still FAIL at util=0.95 AND max-model-len=66560 -> STOP with `GPU_MEMORY_UTILIZATION_095_INSUFFICIENT_FOR_REQUIRED_64K_PLUS_1K_CAPACITY`; package evidence; upload; end.

## Step 5 - 64K benchmark contract (unchanged)

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

Run1 warmup/discard; Run2 measured. Contract 64x256/65536+1024 random inf ignore-eos.

## Step 6 - machine metrics & disposition

From Run2 raw log/summary (machine; not prose):
- SUCCESSFUL_REQUESTS=256 (expect), FAILED=0
- TOTAL_TOKEN_THROUGHPUT, OUTPUT_TOKEN_THROUGHPUT, REQUEST_THROUGHPUT, DURATION
- DELTA_VS_927_59 = (total/927.59 - 1)*100 (machine)
- 80% target (active D-024 basis): 5054.66/15824*6016*0.80 = 1537.35 (machine)

Dispositions: >=1537.35 -> 64K_FOLLOWUP_PASS (flag for review; formal NOT) ; >927.59 & <1537 -> IMPROVED_BELOW_TARGET; <=927.59 -> NO_IMPROVEMENT; failed/OOM/crash/correctness -> INVALID_OR_ROLLBACK_CANDIDATE; util/floor issue -> STOP token as defined; report to review. Correctness gate 256/0 requires satisfaction.

## Step 7 - record & wrap

Record per result (Required):
REQUESTED_INPUT_TOKENS=65536
REQUESTED_OUTPUT_TOKENS=1024
REQUIRED_TOTAL_SEQUENCE_CAPACITY=66560
EFFECTIVE_MAX_MODEL_LEN=<actual>
GPU_MEMORY_UTILIZATION=0.95
CAPACITY_MARGIN_TOKENS=(effective - 66560)
KV evidence
optimization-summary-64k.txt with attempt/capacity/64K/delta/disposition.
Package tar.gz (control-sha etc), SHA256SUMS/MANIFEST, D-022 release. REPORT with outcome/delta/service state. Default leave newly launched candidate running on PASS/IMPROVED (PID/port/log); do not affect others.

## Constraints
- floor 66560; use util 0.95 only; MTP OFF; benchmark contract unchanged; no 4-run matrix; formal OPT-01 unchanged; no Formal result.