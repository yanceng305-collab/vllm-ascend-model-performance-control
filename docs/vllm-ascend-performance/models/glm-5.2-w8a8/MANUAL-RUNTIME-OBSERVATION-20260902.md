# GLM-5.2-W8A8 MANUAL RUNTIME OBSERVATION

**Date**: 2026-09-02
**Author of record**: PerfControl (Control repo)
**Executor**: User (manual, on A3; no A3PerfRunner execution, no PerfControl server operation)
**Classification**: USER-MANUAL OPERATIONAL RESTORE / EXPLORATORY RUNTIME — NOT an accepted frozen baseline replay, NOT A3PerfRunner formal Task execution, NOT a formal Evidence run, NOT a Formal Result, NOT Formal OPT-01 Screening.

This document is a non-formal observation record. The official baseline (BASELINE.md) and immutable Results are unchanged. Nothing here authorizes a next server execution.

---

## 1. Why the manual restore happened

The vendor needed to restart/use the A3 server while the earlier read-only preflight had found no accepted GLM-5.2-W8A8 serve process (outcome `RUNTIME_IDENTITY_MISMATCH`, Gate A `NO_PROCESS`). With the dispatched Runner not available, User manually restored a GLM-5.2-W8A8 vLLM service inside the existing container for exploratory work.

This is a USER-MANUAL OPERATIONAL RESTORE — not an exact replay of the accepted frozen baseline.

---

## 2. Actual command executed by User (startup success)

```bash
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1

MODEL="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
LOG_PATH="/workspace/glm52_w8a8.log"

nohup vllm serve "$MODEL" \
  --served-model-name glm52-w8a8 \
  --trust-remote-code \
  --max-model-len 70000 \
  --tensor-parallel-size 16 \
  --gpu-memory-utilization 0.9 \
  --quantization ascend \
  --distributed-executor-backend mp \
  --compilation-config '{
    "cudagraph_mode": "FULL_DECODE_ONLY",
    "max_cudagraph_capture_size": 64
  }' \
  --no-enable-prefix-caching \
  --no-enable-log-requests \
  --port 8000 \
  > "$LOG_PATH" 2>&1 &
```

Server startup: SUCCESS.

---

## 3. Deviations from the accepted frozen baseline (explicit)

The frozen baseline launch (BASELINE.md) does NOT contain the following; each is a deviation in this manual run:

1. `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2` (added)
2. `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True` (explicitly set)
3. `OMP_PROC_BIND=false` and `OMP_NUM_THREADS=1` (added)
4. `--served-model-name glm52-w8a8` (explicitly set)
5. `--distributed-executor-backend mp` (added)
6. `--compilation-config` changed to include `"max_cudagraph_capture_size": 64` alongside `"cudagraph_mode": "FULL_DECODE_ONLY"`
7. `--port 8000` (explicit)
8. Log at `/workspace/glm52_w8a8.log` instead of the frozen working-directory `glm52_w8a8.log`

None of these are to be written back to BASELINE.md / RUNBOOK / frozen scripts. They remain immutable.
---

## 4. Graph capture observation (from the actual service log)

- FULL_DECODE_ONLY graph capture: 11 / 11 completed
- graph capture duration: 411 sec
- graph memory: 0.59 GiB

Warning observed in log:

```text
The max_cudagraph_capture_size (64) is smaller than the potential
max tokens required for decode (256).
This may lead to suboptimal performance.
```

Recorded facts:

- `max_cudagraph_capture_size=64` is effective in this run
- runtime reports potential decode requirement: 256
- this is a graph-coverage / scheduler-alignment risk, not a measured value of any scheduler parameter
- `max_num_batched_tokens=256` is explicitly NOT recorded (no such Evidence exists)

---

## 5. max_num_batched_tokens status

Per-User greps executed on `/workspace/glm52_w8a8.log`:

```bash
grep -nE 'max_num_batched_tokens|max-num-batched-tokens|SchedulerConfig' /workspace/glm52_w8a8.log
grep -oE 'max_num_batched_tokens[ =:]+[0-9]+' /workspace/glm52_w8a8.log
```

No effective numeric value obtained from the log.

Formal status: **`max_num_batched_tokens = UNVERIFIED`**.

It is prohibited to infer the value from: the 256 warning, max-model-len, max-num-seqs default, historical 910B, vLLM documentation defaults, or other models.

---

## 6. Official upstream reference (live-verified by PerfControl)

Independent verification on 2026-09-02: `vllm-project/vllm-ascend` at commit `6443b2a38b95390e4f5174ff7ad2f8c3751e040f`, file `docs/source/tutorials/models/GLM5.2.md` (HTTP 200, pinned commit).

Verified official reference content includes:

- `HCCL_OP_EXPANSION_MODE="AIV"`
- `OMP_PROC_BIND=false`, `OMP_NUM_THREADS=1`
- `HCCL_BUFFSIZE=200`
- `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`
- `VLLM_ASCEND_BALANCE_SCHEDULING=1`, `VLLM_ASCEND_ENABLE_MLAPO=1`
- example launch with `--data-parallel-size 2` / `--tensor-parallel-size 8` and `--enable-expert-parallel`
- `--max-num-seqs 48` and `--max-num-batched-tokens 4096`
- `--async-scheduling`, `--additional-config '{"multistream_overlap_shared_expert":true}'`
- low-latency single-node reference: `DP1 / TP16`, Expert Parallel off

Status of that 4096: **OFFICIAL upstream recommended reference candidate only**. It must NOT be recorded as the accepted baseline effective `max_num_batched_tokens` (the baseline never explicitly passed this parameter; its effective value remains UNVERIFIED).
---

## 7. Manual 16K exploratory microgate — COMPLETED (2026-09-02)

Workload: input 16384, output 1024, concurrency 64, num-prompts 256, dataset random, random-range-ratio 0, request-rate inf, ignore-eos true, endpoint /v1/completions, client `vllm bench serve`. Run1 warmup/discard; Run2 measured (exploratory).

Run2 summary (as provided by User):

- Successful requests: 256
- Failed requests: 0
- Benchmark duration: 4639.94 s
- Total input tokens: 4194304
- Total generated tokens: 262144
- Request throughput: 0.06 req/s
- Output token throughput: 56.50 tok/s
- Peak output token throughput: 88.00 tok/s
- Peak concurrent requests: 65
- **Total token throughput: 960.45 tok/s**
- Mean TTFT: 959813.80 ms; median 1092897.84 ms; P99 1097525.24 ms
- Mean TPOT: 64.23 ms; median 64.55 ms; P99 65.40 ms
- Mean ITL: 64.23 ms; median 49.28 ms; P99 737.46 ms

Disposition (machine-computed from Run2 value):

- accepted 16K baseline reference: **957.94 tok/s**
- delta = (960.45 / 957.94 - 1) x 100% = **+0.262021%** (≈ +0.262%)
- thresholds: +2% = 977.10 tok/s; +5% = 1005.84 tok/s
- classification: **MANUAL EXPLORATORY MICROGATE: NO_MATERIAL_GAIN**
- wording: slight positive delta / essentially flat; below the +2% material-gain threshold; NOT a regression; 256 success / 0 failed; no correctness/service failure observed from the benchmark summary.

Boundary on capture=64 (confounded, not isolated):

- under this manual runtime variant (`max_cudagraph_capture_size=64` plus the other manual deviations: jemalloc LD_PRELOAD, PYTORCH_NPU_ALLOC_CONF, OMP settings, explicit mp backend, served-model-name/port, capture max 64), the 16K/C64 exploratory run gave 960.45 tok/s — essentially flat vs the accepted 957.94 tok/s.
- classification: **NO MATERIAL CHANGE OBSERVED FOR THE COMBINED MANUAL VARIANT** — NOT `capture64 isolated PASS`; the variant is confounded and no single-parameter conclusion is drawn.

This is a MANUAL EXPLORATORY MICROGATE. It is NOT formal OPT-01 screening, NOT A3PerfRunner formal Evidence, NOT a Formal Result, and it does not unlock OPT-01.

---

## 8. Future candidate families (record only, no authorization)

Following review of the completed manual 16K exploratory result, no winner is selected and no next server execution is authorized by this observation record:

- **A — Scheduler candidate**: `max_num_batched_tokens=4096`. Source: upstream official GLM-5.2-W8A8 reference (verified). Status: `REFERENCE CANDIDATE ONLY`.
- **B — Graph/scheduler alignment**: `max_num_seqs=64` combined with `max_cudagraph_capture_size=64`. Rationale: the accepted project benchmark uses max concurrency 64; runtime warning shows capture 64 < potential decode requirement 256. Status: `CANDIDATE FOR CONTROLLED TEST ONLY`.
- **C — Official Ascend runtime knobs**: `HCCL_OP_EXPANSION_MODE=AIV`, `HCCL_BUFFSIZE=200`, `OMP_PROC_BIND=false`, `OMP_NUM_THREADS=1` (observed in official upstream reference).
- **D — Later optimization families**: async scheduling, MLAPO, balance scheduling, multistream overlap, MTP (reference only).



---

## 9. Formal OPT-01 status (as of this record)

Formal OPT-01 screening remains **BLOCKED / NOT YET AUTHORIZED**.

Accurate reason summary:

- the original read-only preflight failed because the accepted GLM runtime was absent (NO_PROCESS, correctly recorded);
- User has since manually restored an operational GLM-5.2-W8A8 runtime variant;
- that runtime is NOT an exact replay of the accepted baseline;
- `max_num_batched_tokens` remains UNVERIFIED;
- a manual exploratory 16K microgate has COMPLETED (960.45 tok/s; +0.262% vs accepted; MANUAL EXPLORATORY MICROGATE: NO_MATERIAL_GAIN; see section 7);
- formal candidate selection / screening waits for review of the completed manual observation.

This record does not modify the completed preflight Task record (its NO_PROCESS finding was correct at that time) and does not retroactively change any disposition.

---

_End of observation record. Non-formal, non-baseline, non-A3PerfRunner Evidence._
