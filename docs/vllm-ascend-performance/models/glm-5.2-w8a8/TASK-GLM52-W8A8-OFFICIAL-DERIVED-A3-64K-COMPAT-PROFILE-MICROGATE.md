# TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE

**Task ID**: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE  
**Task Type**: OFFICIAL-DERIVED / 64K-COMPATIBLE / EXPLORATORY OPTIMIZATION PROFILE  
**Status**: READY / PENDING USER DISPATCH  
**Created**: 2026-09-02  
**Assigned to**: A3PerfRunner  
**Priority**: HIGH

**READY status**: Task prepared. It is NOT authorized to run until User explicitly dispatches (Task ID + DISPATCH_CONTROL_SHA + `Authorization: EXECUTE`).

---

## 1. What this Task is (and is not)

This is an **OFFICIAL-DERIVED A3 profile exploratory microgate** for GLM-5.2-W8A8: it validates whether the official vLLM-Ascend GLM-5.2-W8A8 single-node A3 recommendation can start, hold 70K-capacity, and move the accepted 16K baseline under this project's `max-model-len=70000` constraint.

It is **NOT**:

- an accepted baseline replacement
- Formal OPT-01 (Formal OPT-01 stays `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`)
- a single-variable experiment
- an exact byte-for-byte upstream command reproduction
- a Formal Result
- authorization to run 64K automatically

Classification tag used in docs/evidence: `MANUAL EXPLORATORY` / `OFFICIAL-DERIVED` profile — never `Formal OPT-01`.

## 2. Objective

Verify, under the project constraint `max-model-len=70000` (thus 64K-capable), whether the official-derived single-node A3 profile:

1. starts successfully (`CAPACITY PASS`);
2. provides real 70K runtime capacity (no OOM / KV rejection);
3. at 16K/C64 shows a throughput delta vs the accepted baseline `957.94 tok/s`.

## 3. Upstream fact source (live-verified by PerfControl)

- repo: `vllm-project/vllm-ascend`
- pinned commit: `6443b2a38b95390e4f5174ff7ad2f8c3751e040f`
- file: `docs/source/tutorials/models/GLM5.2.md` (HTTP 200, verified)

Verified markers in the pinned doc: `HCCL_OP_EXPANSION_MODE="AIV"`, `OMP_PROC_BIND=false`, `OMP_NUM_THREADS=1`, `HCCL_BUFFSIZE=200`, `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`, `VLLM_ASCEND_BALANCE_SCHEDULING=1`, `VLLM_ASCEND_ENABLE_MLAPO=1`, `--data-parallel-size 2`, `--tensor-parallel-size 8`, `--enable-expert-parallel`, `--max-num-seqs 48`, `--max-num-batched-tokens 4096`, `--gpu-memory-utilization 0.95`, `--async-scheduling`, `multistream_overlap_shared_expert`, `--speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp", "enforce_eager": true}'`, `VLLM_VERSION=0.21.0` (example env), `--max-model-len 20480`.

The upstream example does NOT set `max_cudagraph_capture_size`; therefore any such value added by this project is a project-defined control, not an upstream recommendation.

## 4. Why OFFICIAL-DERIVED (project-necessary modifications)

1. `max-model-len`: upstream 20480 → project frozen **70000** (HARD CONSTRAINT; cannot shrink to boost 16K).
2. VLLM_VERSION: upstream example sets `0.21.0`; actual runtime is vLLM `0.24.0+empty` — `export VLLM_VERSION=...` is FORBIDDEN; start requires `unset VLLM_VERSION`.
3. prefix cache: project benchmark contract keeps it **OFF**.
4. graph capture: upstream FULL_DECODE_ONLY without capture cap; project adds `max_cudagraph_capture_size=192` as an ENGINEERING STARTUP-TIME CONTROL to avoid the ~1h launch.

## 5. capture = 192 classification

`max_cudagraph_capture_size=192` derives: `max-num-seqs 48` x (3 draft + 1 target) = 192 (project engineering derivation).

It is **NOT**:

- an official recommended capture size
- an upstream GLM-5.2 requirement
- a proven-optimal graph size

Documented utility: startup-time control (a manual variant with capture=64 reached 960.45 tok/s vs 957.94 = +0.262021% in 16K/C64 — combined variant, confounded; capture limit is NOT claimed as a performance candidate by itself). After launch, we record the actual graph-coverage warning (if any).
## 6. Frozen launch command (do not redesign)

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

## 7. Parameter classification

**PROJECT HARD CONSTRAINT**

- model: GLM-5.2-W8A8
- max-model-len: `70000` (frozen; never shrink)
- prefix cache: OFF
- endpoint: standard OpenAI completions benchmark
- benchmark workload: unchanged

**UPSTREAM-DERIVED PERFORMANCE PROFILE**

- `HCCL_OP_EXPANSION_MODE=AIV`, `OMP_PROC_BIND=false`, `OMP_NUM_THREADS=1`, `HCCL_BUFFSIZE=200`, `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`
- `VLLM_ASCEND_BALANCE_SCHEDULING=1`, `VLLM_ASCEND_ENABLE_MLAPO=1`
- DP2 + TP8 + Expert Parallel ON; `max-num-seqs 48`; `max-num-batched-tokens 4096`; `gpu-memory-utilization 0.95`
- async scheduling; `multistream_overlap_shared_expert=true`; MTP=3; FULL_DECODE_ONLY

**PROJECT STARTUP-TIME CONTROL**

- `max_cudagraph_capture_size=192` (engineering startup control; not official/optimal claim)

**ENVIRONMENT CONTAMINATION PREVENTION**

- `unset VLLM_VERSION`, `unset LD_PRELOAD`, unset FlashComm overrides, `unset ASCEND_LAUNCH_BLOCKING`

## 8. Container-level clean restart (User-authorized)

User explicitly authorized `docker restart model-test-zyg-a3` for this Task (the project's dedicated test container) to stop the old exploratory GLM service and obtain a clean runtime state. No separate vLLM PID / Python-worker kill is needed.

Frozen execution order:

1. On the HOST confirm the target container exists and matches uniquely:

   docker ps -a --filter "name=^/model-test-zyg-a3$"

   else STOP: `TARGET_CONTAINER_NOT_FOUND_OR_AMBIGUOUS`.

2. Before restart record:

   docker inspect model-test-zyg-a3

   and:

   npu-smi info

   as before-evidence.

3. User already authorized, so execute:

   docker restart model-test-zyg-a3

   Do NOT restart any other container.

4. After restart confirm the container RUNNING:

   docker ps --filter "name=^/model-test-zyg-a3$"

5. On the HOST run `npu-smi info` and confirm all NPUs used by this Task have no stale inference process. This is the mandatory pre-launch quiescence gate. If residual processes remain just after restart, allow a short wait and re-check. Do NOT kill residual processes yourself. If residual NPU processes persist after a reasonable wait, STOP with `NPU_NOT_QUIESCENT_AFTER_CONTAINER_RESTART` and keep evidence.

6. Only when BOTH (container RUNNING) and (NPU processes quiescent) hold, do:

   docker exec -it model-test-zyg-a3 bash

   then run the frozen launch command (section 6).

Scope guard: the restart permission is strictly limited to the container `model-test-zyg-a3`. Restarting/stopping/removing any other container, or killing host workloads not owned by this container, is PROHIBITED and is NOT covered by this authorization.

### replacement-evidence.txt fields

Must include at least:

TARGET_CONTAINER=model-test-zyg-a3
USER_AUTHORIZED_CONTAINER_RESTART=YES
CONTAINER_BEFORE_STATUS=<...>
CONTAINER_RESTART_COMMAND=docker restart model-test-zyg-a3
CONTAINER_RESTART_RESULT=<...>
CONTAINER_AFTER_STATUS=<...>
NPU_BEFORE=<path to saved before evidence>
NPU_AFTER_RESTART=<path to saved after-evidence>
NPU_QUIESCENT_BEFORE_NEW_LAUNCH=YES/NO
OLD_PROCESS_KILL_USED=NO

Do not fabricate any of these fields.
## 9. Phase A - Capacity Gate (after launch)

Do NOT benchmark first. Verify, with evidence:

- process remains alive
- API readiness PASS (`/v1/models` reachable)
- served model is correct
- actual runtime/model identity correct
- TP8, DP2, EP enabled
- `max-model-len=70000`
- `max-num-seqs=48`
- `max-num-batched-tokens=4096`
- async scheduling enabled
- MTP3 enabled
- FULL_DECODE_ONLY enabled
- `max_cudagraph_capture_size=192` effective
- no fatal OOM
- no KV-cache capacity rejection
- no engine initialization failure

Retain: full launch log, graph capture count, graph capture duration, graph memory, graph-coverage warning (if present), KV lines, SchedulerConfig/effective-config lines.

`CAPACITY PASS` = service becomes READY with `max-model-len=70000` and no capacity/OOM/fatal rejection.

`CAPACITY FAIL` = OOM / KV insufficient / max-model-len rejection / DP-TP-EP incompatibility / MTP incompatibility / engine crash / readiness timeout / fatal graph capture failure.

On CAPACITY FAIL: STOP benchmark; still package Evidence and upload via D-022 with disposition `OFFICIAL_DERIVED_PROFILE_CAPACITY_FAIL`.

## 10. Phase B - 16K Fast Microgate (only after CAPACITY PASS)

Contract: input 16384, output 1024, max concurrency 64, num prompts 256, dataset random, random-range-ratio 0, request-rate inf, ignore-eos true, endpoint /v1/completions, client `vllm bench serve`.

Runs: Run1 warmup/discard, Run2 measured.

```bash
BASE_URL="http://127.0.0.1:8000"
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
SERVED_MODEL="glm52-w8a8"
RESULT_DIR="<TASK_EVIDENCE_DIR>/Benchmark-16k"

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

## 11. 16K disposition (exploratory classification)

Reference: accepted baseline 957.94 tok/s; manual combined variant 960.45 tok/s.

Run2 Total Token Throughput:

- `>= 1005.84` → `PROFILE_MICROGATE_PASS` → `QUALIFIES_FOR_64K_FOLLOWUP`
- `977.10` - `1005.83` → `PROFILE_MICROGATE_INCONCLUSIVE`
- `< 977.10` (no regression/no errors) → `PROFILE_MICROGATE_NO_MATERIAL_GAIN`
- clearly below accepted baseline → `PROFILE_MICROGATE_REGRESSION`
- failed requests / OOM / crash / correctness failure / workload mismatch → `PROFILE_MICROGATE_INVALID_OR_ROLLBACK_CANDIDATE`

This is OFFICIAL-DERIVED PROFILE exploratory classification; never write "Formal OPT-01 PASS/FAIL".

## 12. No automatic 64K

Even at 16K >= +5%, this Task does NOT run 64K. It only reports `QUALIFIES_FOR_64K_FOLLOWUP` and STOPS; User + ChatGPT decide the next step (64K is expensive).

## 13. Service exit policy (default: leave running)

After CAPACITY PASS and completed 16K run, LEAVE the official-derived GLM service running (its startup/capture is expensive; keep warm for a possible 64K follow-up). Runner Report MUST state `SERVICE_LEFT_RUNNING=YES` + PID + port + log path.

Only cleanup a Task-owned FAILED process; do not affect other workloads.

## 14. Evidence (all outcomes)

Task ID, DISPATCH_CONTROL_SHA, authorization, date/run-id, exact environment, unset-environment list, exact launch command, runtime identity, process identity, service-replacement evidence, startup log, graph capture evidence, capacity gate, effective config evidence, API readiness, Run1 JSON/log, Run2 JSON/log, benchmark exact command, machine-extracted Run2 key metrics, disposition, SHA256SUMS, MANIFEST, Runner final report.

Transport per D-022 as one immutable `.tar.gz` GitHub Release Asset. Runner does not write the Control repo; PerfControl does not run server commands.

## 15. Relationship to Formal OPT-01

Formal OPT-01 remains `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`; accepted baseline `max_num_batched_tokens` remains UNVERIFIED. This Task is an independent exploratory branch. The profile's explicit `--max-num-batched-tokens 4096` is a profile candidate value only, and must not be reinterpreted as "baseline effective max_num_batched_tokens = 4096".

## 16. Constraints

- READ ONLY / Control-side: this Task/documentation does not start server operations; only User dispatch + A3PerfRunner begin them.
- Do NOT create a Formal Result.
- Do NOT modify accepted raw baseline / immutable Results / D-023 normalization values (752/6016 per D-024).
- Do NOT lower max-model-len below 70000 ("to make the profile benchmark look better").
- Do NOT run 64K within Task.
- Evidence is preserved on every outcome and uploaded via D-022.
