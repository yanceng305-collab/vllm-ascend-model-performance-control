# A3PerfRunner Prompt: GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION (Rev 2 — pinned tooling + canonical command artifact)

**For Task**: TASK-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION  
**Runner Role**: A3PerfRunner  
**Created**: 2026-09-03 (Rev 2: PRE-DISPATCH TOOLING REVIEW + FIX)

---

## Role

You produce Evidence only. No Control commit/push (Release assets per D-022 are allowed), no Formal Result authoring, no Acceptance.

## Step 1 - Dispatch

Task ID: GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION  
DISPATCH_CONTROL_SHA: <from User — must already be live-verified by verifying agent>  
Authorization: EXECUTE

Only proceed when all three are present.

## Step 2 - Pinned tooling (no drift from main)

Get the tools at the EXACT DISPATCH_CONTROL_SHA, never from drifting main:

```bash
CONTROL_DIR="<TASK_WORK_ROOT>/control"
git clone https://github.com/yanceng305-collab/vllm-ascend-model-performance-control "$CONTROL_DIR"
git -C "$CONTROL_DIR" checkout --detach "$DISPATCH_CONTROL_SHA"
git -C "$CONTROL_DIR" rev-parse HEAD > control-sha.txt   # MUST equal DISPATCH_CONTROL_SHA
sha256sum "$CONTROL_DIR/scripts/extract_bench_metrics.py" \
          "$CONTROL_DIR/scripts/validate_matrix_candidate.py" \
          "$CONTROL_DIR/scripts/validate_full_matrix_candidate.py" \
          "$CONTROL_DIR/scripts/bench_common.py" > script-sha256sums.txt
```

- All extractor/validator invocations below MUST use `python3` invoked from `"$CONTROL_DIR"` so the pinned scripts are what run.
- Record `control-sha.txt`, `script-sha256sums.txt` at the Evidence root.

## Step 3 - Warm service check (preferred path)

Verify the current reviewed warm service:

- PID 3164838; port 8000; log /workspace/glm52_od_64k_candidate.log
- `/v1/models` reachable; model `glm52-w8a8`; `max_model_len` 67000
- effective profile: gpu-memory-utilization=0.95, capture=96, MTP OFF, DP2/TP8/EP, seqs 48, batched 4096, async ON, multistream ON, FULL_DECODE_ONLY, prefix OFF

If EXACTLY matches: reuse (NO restart, NO re-graph-capture) for the whole matrix.
If missing / identity mismatch / profile mismatch: restore the same frozen candidate (Task §2); parameter values must not change.

Record `warm-reuse.txt`: REUSE=YES/NO + verification output.

## Step 4 - Full matrix execution (per cell)

For each cell in order 1K -> 4K -> 16K -> 64K (input [1024|4096|16384|65536], output 1024):

```bash
BASE_URL="http://127.0.0.1:8000"
SERVED_MODEL="glm52-w8a8"
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
CELL_DIR="<TASK_EVIDENCE_DIR>/cell-<CELL>"
mkdir -p "$CELL_DIR"
for RUN in 1 2 3 4; do
  BENCH_ARGS=(vllm bench serve --backend vllm --base-url "$BASE_URL" --endpoint /v1/completions \
    --model "$SERVED_MODEL" --tokenizer "$MODEL_PATH" --trust-remote-code \
    --dataset-name random --random-input-len <INPUT> --random-output-len 1024 \
    --random-range-ratio 0 --request-rate inf --max-concurrency 64 --num-prompts 256 \
    --ignore-eos --save-result --result-dir "$CELL_DIR" --result-filename "run${RUN}.json")

  # 1) CANONICAL command artifact FIRST: the exact argv that will execute (JSON list)
  python3 -c 'import json,sys; json.dump(sys.argv[1:], open(sys.argv[1],"w"), indent=1)' \
    "$CELL_DIR/run${RUN}.command.txt" "${BENCH_ARGS[@]}" || exit 1

  # 2) execute with that exact argv; log covers tee (log may omit argv — contract comes from command.txt)
  "${BENCH_ARGS[@]}" 2>&1 | tee "$CELL_DIR/run${RUN}.log"
done
```

- `runN.command.txt` is the canonical workload-contract artifact; the validator reads the contract from it, never from the tee'd log.
- runN.json (if produced): keep; 0-byte/absent is a recorded writer anomaly, not a FAIL when log+metrics+validator PASS.

For EVERY run (including run1): machine-derived metrics:

```bash
python scripts/extract_bench_metrics.py "$CELL_DIR/runN.log" --out "$CELL_DIR/runN.metrics.json" --strict
```

- `--strict` = any required metric field missing => exit 1; abort and re-run that run attempt.

Run1 is EXPLICITLY machine-identified as discard:

```bash
echo "WARMUP_DISCARD" > "$CELL_DIR/run1.role.txt"
```

Run2/3/4 are the only MEASURED runs; Formal value = Mean(Run2, Run3, Run4).

## Step 5 - Run quality gates (Run2/3/4)

- successful_requests == 256, failed_requests == 0 (upstream gate message)
- runN.log kept raw; runN.json (if produced) kept; runN.metrics.json made by extractor --strict
- client wedge (tqdm stuck): mark attempt ABORTED/INVALID, re-run SAME profile (not a parameter change)
- engine crash / device error / OOM / KV rejection / correctness / profile mismatch: record; DO NOT change parameters; STOP the cell; report FAIL per formal rules

## Step 6 - Per-cell machine verification (no hand numbers)

```bash
python3 "$CONTROL_DIR/scripts/validate_matrix_candidate.py" \
  --cell-dir "$CELL_DIR" --cell <CELL> \
  --matrix-config "$CONTROL_DIR/docs/vllm-ascend-performance/models/glm-5.2-w8a8/candidate-matrix-config.json" \
  --out-dir "$CELL_DIR"
```

Exit 0 = PASS, 1 = FAIL. Produces `validation.json` + `aggregation.json` inside the cell dir (deterministic: no timestamps). It verifies NOTHING about a Formal Result (later stage).

Per cell also record:
- `"$CELL_DIR/profile-snapshot.json"` — the effective frozen profile of the running service (field names as in the matrix validator example)
- `"$CELL_DIR/runtime-identity.txt"` — container/image/vLLM/PID/port/log

## Step 7 - Matrix-level verification

After all four cells:

```bash
python3 "$CONTROL_DIR/scripts/validate_full_matrix_candidate.py" \
  --matrix-dir "$TASK_EVIDENCE_DIR" \
  --matrix-config "$CONTROL_DIR/docs/vllm-ascend-performance/models/glm-5.2-w8a8/candidate-matrix-config.json" \
  --out "$TASK_EVIDENCE_DIR/matrix-validation.json"
```

Exit 0 = PASS. Checks per-cell validations, identical profile snapshots, identical runtime identity, run1 discard count == 4, formal value == Mean(run2,3,4).

## Step 8 - Evidence bundle (all outcomes)

Per cell dir: run1-4.log; run1-4.command.txt; run1-4.metrics.json; validation.json; aggregation.json; profile-snapshot.json; runtime-identity.txt; run1.role check; control-sha.txt; script-sha256sums.txt.
Root: warm-reuse.txt, matrix-validation.json; MANIFEST.txt; SHA256SUMS.txt; then single tar.gz per D-022 with `.sha256` sidecar.

## Step 9 - Runner report

Per cell: mean/delta%/achievement%/stability (stddev,CV), 256/0; matrix: profile_identical, identity_identical, measured 12, warmup 4.
Keep warm service running after the matrix (SERVICE_LEFT_RUNNING=YES + PID/port/log) unless failure requires stopping Task-owned processes only.

## Constraints

- Frozen profile; no per-cell tuning
- Run1 machine role is WARMUP_DISCARD, never in any mean
- Do not modify vLLM/site-packages/image to fix the JSON writer bug
- D-024 basis machine inputs from candidate-matrix-config.json (6016 / 15824 / 80%)
- Formal OPT-01 remains BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION; untouched
- This Task produces Evidence ONLY; Control review precedes any Formal Result/  Acceptance
- No Control commit/push by the Runner