# TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE

**Task ID**: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE  
**Task Type**: OFFICIAL-DERIVED / 64K-COMPATIBLE / EXPLORATORY OPTIMIZATION PROFILE  
**Status**: READY / PENDING USER REDISPATCH  
**Created**: 2026-09-02  
**Revision**: 2026-09-02 (autonomous optimization runner mode)  
**Assigned to**: A3PerfRunner (AUTONOMOUS PERFORMANCE OPTIMIZATION RUNNER)  
**Priority**: HIGH

**READY status**: prepared for User re-dispatch (Task ID + DISPATCH_CONTROL_SHA + `Authorization: EXECUTE`). No server operation begins without it.

---

## 1. What this Task is (and is not)

This Task runs the OFFICIAL-DERIVED A3 profile exploratory optimization track for GLM-5.2-W8A8, with **A3PerfRunner acting as an AUTONOMOUS PERFORMANCE OPTIMIZATION RUNNER** — not a fixed-command executor.

Inside the project HARD BOUNDARIES (Section 7), the Runner observes → diagnoses → forms a hypothesis → modifies parameters → retries → measures → records, iterating until a valuable result is obtained or a real User-decision blocker is hit. Multi-variant exploration within this single Task is allowed; the runner does not stop for ordinary recoverable engineering issues (OOM, KV capacity, graph capture, parameter incompatibility, launch failure, performance regression).

It is **NOT**:

- an accepted baseline replacement
- Formal OPT-01 (stays `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`)
- a Formal Result
- authorization to auto-run 64K

## 2. Objective

1. Get a variant of the official-derived A3 GLM-5.2-W8A8 profile to start and reach `CAPACITY PASS` with `max-model-len >= 70000`.
2. Measure the 16K/C64 FAST MICROGATE per variant.
3. Report the best variants against accepted baseline 957.94 tok/s.

## 3. Upstream fact source (live-verified by PerfControl)

- repo: `vllm-project/vllm-ascend`
- pinned commit: `6443b2a38b95390e4f5174ff7ad2f8c3751e040f`
- file: `docs/source/tutorials/models/GLM5.2.md` (HTTP 200; verified markers: HCCL_OP_EXPANSION_MODE="AIV", OMP_PROC_BIND=false, OMP_NUM_THREADS=1, HCCL_BUFFSIZE=200, PYTORCH_NPU_ALLOC_CONF=expandable_segments:True, VLLM_ASCEND_BALANCE_SCHEDULING=1, VLLM_ASCEND_ENABLE_MLAPO=1, DP2/TP8/EP ON, max-num-seqs 48, max-num-batched-tokens 4096, gpu-mem 0.95, async, multistream, MTP3 (num_speculative_tokens 3 deepseek_mtp), FULL_DECODE_ONLY, VLLM_VERSION=0.21.0 example, max-model-len 20480; `max_cudagraph_capture_size` is NOT set upstream).

The upstream profile is the REFERENCE STARTING POINT, not a frozen mandate.

## 4. Why OFFICIAL-DERIVED (reference derivation)

Upstream must be adapted to the project: (1) max-model-len 20480 → 70000 HARD BOUNDARY; (2) VLLM_VERSION example 0.21.0 is not used (actual runtime vLLM 0.24.0+empty; `unset VLLM_VERSION` required); (3) prefix cache stays OFF per project contract; (4) graph capture gets `max_cudagraph_capture_size=192` as startup-time engineering control (not upstream, not an optimality claim). Any further variance is the runner's optimization freedom per Section 7.2, with a recorded motivation.

## 5. capture = 192 classification

`max_cudagraph_capture_size=192` = project engineering startup-time control (derivation 48 x (3+1)). NOT official recommendation, NOT proven-optimal; runner may adjust (Section 9).

## 6. Initial launch profile (reference start; adjusting is allowed)

The launch below is the INITIAL variant (official-derived reference start). It is not "frozen": parameters in Section 7.2 may be changed by the runner, each with a recorded reason/evidence. Environment blocks stay strict at first launch (unset list).
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

## 7. Project HARD BOUNDARIES vs adjustable parameters

### 7.1 HARD BOUNDARIES (never breach)

1. **Model identity**: `GLM-5.2-W8A8`, model path `/data/tiankuan/zyg/model/GLM-5.2-w8a8`; no weight substitution.
2. **Runtime family**: image `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`, vLLM 0.24 track; no install/upgrade/downgrade of the core runtime, no image swap, no pip override of core runtime, no model code/weight modification, unless User authorizes.
3. **Hardware scope**: only container `model-test-zyg-a3` and its 16 logical NPUs; no impact on other containers/workloads.
4. **64K capability**: the final candidate must keep `max-model-len >= 70000`; do not shrink the FINAL candidate to 20480/32768/65536 to boost 16K. A smaller-context experiment, if truly needed for diagnosis, must be clearly marked `DIAGNOSTIC ONLY / NOT CANDIDATE` and must not be presented as a performance candidate.
5. **Final benchmark contract** (unchanged): input 16384 / output 1024 / concurrency 64 / num-prompts 256 / dataset random / range-ratio 0 / inf / ignore-eos / /v1/completions / client `vllm bench serve`; Run1 warmup discard, Run2 measured; gate metric Total Token Throughput.
6. **64K execution**: still prohibited to auto-run 64K in this Task; on qualification only report `QUALIFIES_FOR_64K_FOLLOWUP`.

### 7.2 Autonomously adjustable (with recorded reason + evidence)

- data-parallel-size, tensor-parallel-size, expert parallel
- max-num-seqs, max-num-batched-tokens
- gpu-memory-utilization
- speculative / MTP token count
- cudagraph mode, max_cudagraph_capture_size
- async scheduling, prefix cache
- VLLM_ASCEND_BALANCE_SCHEDULING, VLLM_ASCEND_ENABLE_MLAPO
- multistream_overlap_shared_expert
- HCCL_BUFFSIZE and other HCCL tuning variables
- OMP settings
- allocator settings / memory engineering controls
- other vLLM / vLLM-Ascend supported runtime flags

Each change needs a technical reason and must not violate §7.1. Multiple strongly coupled parameters may be changed together (stated as a bundle with the reason); isolated single-variable confirmation may be deferred to a later isolation experiment.

### 7.3 Environment cleanliness

The initial launch keeps the strict `unset` block. Later environment adjustments (e.g., HCCL/OMP/allocator knobs) are allowed within §7.2; record each actual value.

## 8. Container-level clean restart (User-authorized)

User authorized `docker restart model-test-zyg-a3` for this Task (dedicated test container) to stop the old exploratory GLM service and get a clean runtime state.

Frozen sequence:

1. Host: confirm unique container: `docker ps -a --filter "name=^/model-test-zyg-a3$"` else STOP `TARGET_CONTAINER_NOT_FOUND_OR_AMBIGUOUS`.
2. Before restart record: `docker inspect model-test-zyg-a3`, `npu-smi info`.
3. Execute `docker restart model-test-zyg-a3` (only this container).
4. Confirm RUNNING: `docker ps --filter "name=^/model-test-zyg-a3$"`.
5. Host `npu-smi info` to confirm the NPUs used by the Task have no stale inference process (pre-launch quiescence gate). Short wait and re-check allowed; DO NOT kill residual processes yourself. Persisting residues produce `NPU_NOT_QUIESCENT_AFTER_CONTAINER_RESTART` STOP (keep evidence).
6. Only then `docker exec -it model-test-zyg-a3 bash` and launch.

Scope: restart right of `model-test-zyg-a3` only; no other containers, no host workloads.
## 9. Autonomous capacity & optimization loop (Phase gate)

### 9.1 Recoverable issues are feedback, not blockers

OOM, KV-capacity rejection, graph capture failures, parameter incompatibility, service launch failure, scheduler issues, and performance regression are ordinary optimization feedback that the Runner MUST diagnose and resolve autonomously whenever possible. STOP is reserved for the §9.5 list.

Loop: `OBSERVE → DIAGNOSE → FORM HYPOTHESIS → MODIFY → RETRY → MEASURE → RECORD`.

### 9.2 Known capacity baseline (2026-09-02)

The initial official-derived launch (`gpu-memory-utilization=0.95`, max-model-len=70000) failed with KV-cache capacity rejection: ~6.30 GiB needed vs ~6.28 GiB available; vLLM estimated maximum length 69632. Evidence: GitHub Release `glm52-od-profile-16k-20260902-144217` (authoritative archive SHA256 read live from metadata: `3d41a2254317bc887787ee7969d121558309229a2034c0bd05150bfc81500f63`).

This is a recoverable capacity-engineering shortfall. Runner picks the first remedy on log evidence (e.g., `gpu-memory-utilization` 0.95 → 0.96, or alternative well-justified option: graph capture size, batching/scheduling, topology, MTP, allocator settings). The next candidate must reach `CAPACITY PASS` with `max-model-len >= 70000`, service READY, no fatal OOM/KV rejection.

### 9.3 Multi-variant exploration inside this Task

Multiple variants may be explored sequentially in this single Task (no new Task per parameter). Strongly coupled parameters may be bundled (record the coupling rationale). Causal single-variable confirmation is deferred to later isolation experiments. Smaller-context diagnostics are allowed only when clearly marked `DIAGNOSTIC ONLY / NOT CANDIDATE`.

### 9.4 Optimization attempt record (mandatory per attempt)

ATTEMPT_ID, OBJECTIVE, OBSERVED_PROBLEM, HYPOTHESIS, PARAMETERS_BEFORE, PARAMETERS_CHANGED, PARAMETERS_AFTER, REASON_FOR_CHANGE, SUPPORTING_EVIDENCE, EXACT_LAUNCH_COMMAND, START_TIME, END_TIME, CAPACITY_RESULT, 16K_RESULT (if run), TOTAL_TOKEN_THROUGHPUT, FAILED_REQUESTS, NEXT_DECISION.

Attempt numbering: `Attempt-001`, `Attempt-002`, ... (multi-variable bundles OK; causal isolation later).

### 9.5 TRUE STOP conditions (return to User)

- Control SHA / Task authorization does not hold
- target container identity ambiguous or not `model-test-zyg-a3`
- would require touching other container/workload
- hardware anomaly
- NPU not quiescent involving non-Task-owned workload
- core runtime/image/model or weights must change
- cannot keep `max-model-len >= 70000`
- benchmark correctness cannot be guaranteed
- all reasonable optimization directions exhausted
- 64K formal run needed
- User needs to make a high-cost / high-risk decision

Everything else (OOM, KV rejection, graph capture failures, parameter incompatibility, service launch fail, performance regression) is NOT an automatic STOP.

## 10. 16K FAST MICROGATE (per capacity-passing variant)

Contract kept; client `vllm bench serve` (base-url 127.0.0.1:8000, served-model glm52-w8a8, tokenizer model path); Run1 warmup/discard; Run2 measured. Per variant after its capacity PASS.

```bash
BASE_URL="http://127.0.0.1:8000"
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
SERVED_MODEL="glm52-w8a8"
RESULT_DIR="<TASK_EVIDENCE_DIR>/benchmark-16k"
mkdir -p "$RESULT_DIR"
for RUN in 1 2; do
  vllm bench serve \
    --backend vllm --base-url "$base-url" --endpoint /v1/completions \
    --model "$SERVED_MODEL" --tokenizer "$MODEL_PATH" --trust-remote-code \
    --dataset-name random --random-input-len 16384 --random-output-len 1024 \
    --random-range-ratio 0 --request-rate inf --max-concurrency 64 --num-prompts 256 \
    --ignore-eos --save-result --result-dir "$RESULT_DIR" --result-filename "run${RUN}.json" \
    2>&1 | tee "$RESULT_DIR/run${RUN}.log"
done
```

## 11. 16K disposition (exploratory classification)

- 957.94 tok/s accepted baseline; Run2 Total Token Throughput:
  - `>= 1005.84` → `PROFILE_MICROGATE_PASS` → `QUALIFIES_FOR_64K_FOLLOWUP`
  - `977.10 <= x < 1005.84` → `PROFILE_MICROGATE_INCONCLUSIVE`
  - `957.94 <= x < 977.10` → `PROFILE_MICROGATE_NO_MATERIAL_GAIN`
  - `< 957.94` → `PROFILE_MICROGATE_REGRESSION`
  - failed requests / OOM / crash / correctness / workload mismatch → `PROFILE_MICROGATE_INVALID_OR_ROLLBACK_CANDIDATE`

One REGRESSION does not end the session; the Runner may continue to next variant. Never mark "Formal OPT-01 PASS/FAIL".

## 12. No automatic 64K

Even on `>= 1005.84` only report `QUALIFIES_FOR_64K_FOLLOWUP`, STOP selection. 64K requires User + ChatGPT decision.

## 13. Service policy

After capacity PASS + 16K completed, default LEAVE SERVICE RUNNING (esp. PASS / INCONCLUSIVE) to avoid re-capture ("graph" expensive). Runner may clean up to its own Task-owned service to test next variant. Never affect other workloads.

## 14. Evidence

Per attempt: Attempt-001..., logs, config, capacity gate, benchmark JSON/log; per Task: `optimization-summary.txt` with a table

| Attempt | Effective profile | Capacity | 16K Total tok/s | Delta vs 957.94 | Disposition | Next action |

plus:

BEST_CAPACITY_VALID_PROFILE
BEST_16K_PROFILE
BEST_16K_TOTAL_TOKEN_THROUGHPUT=<tok/s>
QUALIFIES_FOR_64K_FOLLOWUP=YES/NO

Plus unchanged evidence base: control-sha, environment, unset list, launch commands, replacement evidence, runtime identity, startup log per attempt, graph capture evidence, capacity gate, api readiness, Run1/2, benchmark command, SHA256SUMS, MANIFEST etc. Archive single .tar.gz; SHA256SUMS; MANIFEST; upload per D-022.

## 15. Formal OPT-01 unchanged

Formal OPT-01 remains `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`; accepted baseline `max_num_batched_tokens` remains UNVERIFIED. Exploratory results do not unlock it; a strong candidate path is decided by PerfControl in the future.

## 16. Constraints

- Readiness only on User dispatch.
- HARD BOUNDARIES §7.1; adjustments are §7.2 + §9.
- max-model-len final must stay >= 70000; DIAGNOSTIC ONLY marks smaller-context tries.
- No automatic 64K.
- No Formal Result; no immutable changes; no D-024 change.
- Evidence on every outcome + D-022 upload.
