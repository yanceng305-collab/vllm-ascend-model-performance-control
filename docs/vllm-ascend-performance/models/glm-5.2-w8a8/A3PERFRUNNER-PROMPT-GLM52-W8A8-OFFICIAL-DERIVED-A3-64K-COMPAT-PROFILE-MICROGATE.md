# A3PerfRunner Prompt: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE

**For Task**: TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE  
**Runner Role**: A3PerfRunner  
**Created**: 2026-09-02

---

## Role

You are **A3PerfRunner**, the remote execution agent on the A3 server. Per D-021:

**You produce**: Evidence only (execution artifacts, measurements, provenance)  
**You do NOT**: commit the Control repo, push GitHub (except Release Assets per D-022), author Formal Results, or perform Formal Acceptance.

## Task summary

Execute the OFFICIAL-DERIVED A3 profile exploratory microgate:

1. Replace the confirmed User-manual GLM service with the frozen official-derived profile (only with the replacement-safety checks below).
2. Phase A: Capacity Gate under `max-model-len=70000`.
3. Phase B (only after CAPACITY PASS): 16K two-run FAST MICROGATE.
4. Classify, package, upload Evidence (D-022), leave service running.

This is `EXPLORATORY` / `OFFICIAL-DERIVED` — NOT Formal OPT-01, NOT a Formal Result, NOT an accepted baseline replacement.

## Frozen environment & launch (do not redesign)

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
LOG_PATH="/workspace/glm52_official_derived_64k_profile.log"

nohup vllm serve "$MODEL" \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name glm52-w8a8 \
  --trust-remote-code \
  --seed 1024 \
  --data-parallel-size 2 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --max-model-len 70000 \
  --max-num-seqs 48 \
  --max-num-batched-tokens 4096 \
  --gpu-memory-utilization 0.95 \
  --quantization ascend \
  --async-scheduling \
  --additional-config '{
    "multistream_overlap_shared_expert": true
  }' \
  --compilation-config '{
    "cudagraph_mode": "FULL_DECODE_ONLY",
    "max_cudagraph_capture_size": 192
  }' \
  --speculative-config '{
    "num_speculative_tokens": 3,
    "method": "deepseek_mtp",
    "enforce_eager": true
  }' \
  --no-enable-prefix-caching \
  --no-enable-log-requests \
  > "$LOG_PATH" 2>&1 &
```

Notes:

- `max-model-len 70000` is a HARD PROJECT CONSTRAINT; never shrink it.
- `max_num_batched_tokens=4096` is a PROFILE candidate value; it defines nothing about the formal baseline.
- `max_cudagraph_capture_size=192` = project engineering startup-time control (derived 48 x (3+1)); not an upstream recommendation.
- must: no OOM, no KV-capacity rejection, no `max-model-len` rejection.
## Step 1 - Verify dispatch

```text
Task ID: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```

Only proceed when all three are present.

## Step 2 - Replacement safety

Inspect before touching anything:

- `ss -ltnp | grep :8000` / `curl` check of port 8000
- current serve process cmdline (`ps -ef | grep -E 'vllm|serve'`)
- confirm model path `/data/tiankuan/zyg/model/GLM-5.2-w8a8`

STOP immediately (`UNAUTHORIZED_RUNTIME_REPLACEMENT`, no benchmark, package the STOP evidence and upload per D-022) when the current service is NOT clearly the User-manual GLM service on that model path (e.g., non-GLM workload, MiniMax, other user task, or ambiguous ownership).

Only when the current service is confirmed as the User-manual GLM exploratory service (`/data/tiankuan/zyg/model/GLM-5.2-w8a8`) may you stop it and launch the frozen command below. Do not kill any other workload.

Record replacement evidence: before-PID, after-PID, exact stop/start timestamps.

## Step 3 - Launch and Capacity Gate (Phase A)

Launch with the frozen command above. Wait for readiness. Do NOT benchmark yet.

Probe:

```bash
curl -s http://127.0.0.1:8000/v1/models
```

Verify with evidence (from `ps` output, launch log, and `/v1/models`):

- TP8, DP2, EP enabled
- `--max-num-seqs 48`
- `--max-num-batched-tokens 4096`
- async scheduling enabled
- MTP3 (`num_speculative_tokens: 3`, `deepseek_mtp`)
- FULL_DECODE_ONLY enabled
- `max_cudagraph_capture_size=192` effective
- no KV-cache capacity rejection
- no fatal OOM / no engine initialization failure

Extract into `capacity-gate.txt`:

```text
PROCESS_ALIVE=YES/NO
API_READY=YES/NO
served_model=<glm52-w8a8>
tensor_parallel_size=8
data_parallel_size=2
expert_parallel=enabled
max_model_len=70000
max_num_seqs=48
max_num_batched_tokens=4096
async_scheduling=yes
mtp_num_speculative_tokens=3
full_decode_only=yes
capture_max=192
GRAPH_CAPTURE_COUNT=<n>/<total>
GRAPH_CAPTURE_DURATION=<sec>
GRAPH_MEMORY=<GiB>
GRAPH_COVERAGE_WARNING=<present_or_absent + text>
OOM_OR_FATAL=<no|see-log>
```

Decision:

- all good -> `CAPACITY PASS` -> go to Step 4
- any failure (OOM / KV reject / `max-model-len` rejection / DP-TP-EP or MTP incompatibility / engine crash / readiness timeout / fatal graph capture) -> `CAPACITY FAIL`, STOP benchmark, skip to Evidence, upload with `OFFICIAL_DERIVED_PROFILE_CAPACITY_FAIL`.

## Step 4 - 16K FAST MICROGATE (Phase B; only on CAPACITY PASS)

```bash
BASE_URL="http://127.0.0.1:8000"
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
SERVED_MODEL="glm52-w8a8"
RESULT_DIR="<TASK_EVIDENCE_DIR>/benchmark-16k"
mkdir -p "$RESULT_DIR"

for RUN in 1 2; do
  vllm bench serve \
    --backend vllm \
    --base-url "$BASE_URL" \
    --endpoint /v1/completions \
    --model "$SERVED_MODEL" \
    --tokenizer "$MODEL_PATH" \
    --trust-remote-code \
    --dataset-name random \
    --random-input-len 16384 \
    --random-output-len 1024 \
    --random-range-ratio 0 \
    --request-rate inf \
    --max-concurrency 64 \
    --num-prompts 256 \
    --ignore-eos \
    --save-result \
    --result-dir "$RESULT_DIR" \
    --result-filename "run${RUN}.json" \
    2>&1 | tee "$RESULT_DIR/run${RUN}.log"
done
```

Run1 = warmup / discarded; Run2 = measured.

Machine-extract Run2 key metrics into `benchmark-16k/run2-summary.txt`:

```text
SUCCESSFUL_REQUESTS=256
FAILED_REQUESTS=0
TOTAL_TOKEN_THROUGHPUT=<tok/s>
OUTPUT_TOKEN_THROUGHPUT=<tok/s>
REQUEST_THROUGHPUT=<req/s>
MAX_CONCURRENCY=64
MEAN_TTFT=<ms>
P99_TTFT=<ms>
MEAN_TPOT=<ms>
MEAN_ITL=<ms>
```

If Run2 shows failed requests, OOM, service crash, correctness failure, or workload mismatch, treat as failure path (Step 6, `PROFILE_MICROGATE_INVALID_OR_ROLLBACK_CANDIDATE`).
## Step 5 - 16K disposition (exploratory classification)

Reference: accepted baseline **957.94 tok/s**; manual combined variant 960.45 tok/s.

Run2 Total Token Throughput:

- `>= 1005.84` -> `PROFILE_MICROGATE_PASS` -> `QUALIFIES_FOR_64K_FOLLOWUP`
- `977.10` - `1005.83` -> `PROFILE_MICROGATE_INCONCLUSIVE`
- `< 977.10` (no errors) -> `PROFILE_MICROGATE_NO_MATERIAL_GAIN`
- clearly below accepted baseline -> `PROFILE_MICROGATE_REGRESSION`
- failed requests / OOM / crash / correctness failure / workload mismatch -> `PROFILE_MICROGATE_INVALID_OR_ROLLBACK_CANDIDATE`

Never label these as `Formal OPT-01 PASS/FAIL` — this is OFFICIAL-DERIVED profile exploratory classification.

## Step 6 - No automatic 64K

Even on `PROFILE_MICROGATE_PASS`, do NOT run 64K in this Task. Report `QUALIFIES_FOR_64K_FOLLOWUP` and STOP benchmark selection; User + ChatGPT decide next.

## Step 7 - Service policy

After CAPACITY PASS + completed 16K run:

- LEAVE the official-derived GLM service running (`SERVICE_LEFT_RUNNING=YES`)
- record PID, port 8000, log path `/workspace/glm52_official_derived_64k_profile.log`

On launch/engine failure: clean up only the Task-owned failed process; do not affect other workloads.

## Step 8 - Evidence package (all outcomes)

Evidence dir contents:

- `control-sha.txt` (Task ID + DISPATCH_CONTROL_SHA + Authorization)
- `environment.txt` (env values set; full unset list)
- `launch-command.txt` (exact frozen command)
- `replacement-evidence.txt` (before/after PID, timestamps)
- `runtime-identity.txt`
- `startup.log` (full launch log)
- `graph-capture-evidence.txt`
- `capacity-gate.txt`
- `api-readiness.txt` (`/v1/models` output)
- `benchmark-16k/run1.json` + `run1.log` (warmup)
- `benchmark-16k/run2.json` + `run2.log` (measured)
- `benchmark-16k/run2-summary.txt` (machine-extracted metrics)
- `benchmark-command.txt`
- `disposition.txt`
- `MANIFEST.txt`
- `SHA256SUMS.txt`

Package: single immutable `.tar.gz`; compute archive SHA256; create GitHub Release Asset per D-022 (tag `glm52-od-profile-16k-<run-id>`), regardless of outcome.

## Step 9 - Runner report

```markdown
# A3PerfRunner Report: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE
Task: ...
Outcome: <CAPACITY_PASS/FAIL + MICROGATE disposition>
Phase A: CAPACITY PASS/FAIL (details)
16K Run2: <TOTAL_TOKEN_THROUGHPUT> tok/s vs accepted 957.94 (delta %)
Disposition: <PROFILE_MICROGATE_* / UNAUTHORIZED_RUNTIME_REPLACEMENT>
SERVICE_LEFT_RUNNING=YES  PID=... PORT=8000 LOG=...
Evidence: <release link>  Archive SHA256: <hex>
Server state: <unchanged-during-run / see notes>
```

## Constraints

- EXECUTE only after User dispatch.
- Do NOT commit Control repo; do NOT push GitHub except Release Asset (D-022).
- Do NOT lower `max-model-len` below 70000.
- Do NOT run 64K in this Task.
- Do NOT make any formal-baseline claim from this exploratory profile.
- Upload Evidence on EVERY outcome (PASS / INCONCLUSIVE / NO_MATERIAL_GAIN / REGRESSION / INVALID / CAPACITY_FAIL / STOP).
