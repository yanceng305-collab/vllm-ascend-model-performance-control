# Control Evidence Review: GLM52-W8A8 64K FOLLOW-UP (MEMORY-HEADROOM 0.95 / 67000)

**Review date**: 2026-09-03
**Reviewer**: PerfControl
**Task**: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-FOLLOWUP
**Evidence Release**: glm52-od-64k-followup-20260903
**DISPATCH_CONTROL_SHA (from control-sha.txt)**: `2656bcc7d23d6bad613cf1a7e42c7e60c1a785d5`

## 1. Transport authority

GitHub live metadata: tag `glm52-od-64k-followup-20260903`, name "GLM52 OD 64K Follow-up: PASS (1760.92 tok/s)", asset `final-evidence-64k.tar.gz` (size 12264), digest `15bb96cd7408c9761656df56861471688a082b0d8d9c011b17e3bd94b4543fa5`. Downloaded local recompute = same value. **MATCH — PASS**.

## 2. Runner prose transcription discrepancies (recorded, no re-run)

1. Prose tag `glm52-od-64k-followup-06-click` vs actual `glm52-od-64k-followup-20260903`.
2. Prose SHA `...cd94b4543fa5` vs GitHub metadata SHA `16df568861471688a082b0d8d9c011b17e3bd94b282...` -> final authoritative value read from API: `15bb96cd7408c9761656df56861471688a082b0d8d9c011b17e3bd94b4543fa5`.
3. Prose formula used `5054.66 / 15824 * 6076 * 0.80`; D-024 A3 basis is `6016`; correct formula `5054.66 / 15824 * 6016 * 0.80`.

Classification: `PROVENANCE / PROSE TRANSCRIPTION DISCREPANCIES`. No benchmark re-run triggered. Formal values use GitHub metadata + machine computation only.

## 3. Reviewed effective candidate (from archive)

- model GLM-5.2-W8A8; gpu-memory-utilization = 0.95
- effective max-model-len = 67000 (floor 66560; required sequence capacity 66560; margin 440)
- capture = 96; MTP = OFF; DP2/TP8/EP ON; max-num-seqs 48; max-num-batched-tokens 4096
- async scheduling ON; multistream_overlap_shared_expert ON; FULL_DECODE_ONLY; prefix cache OFF

## 4. Capacity

- CAPACITY PASS (API READY HTTP200; /v1/models max_model_len=67000)
- no KV rejection; max concurrency for 67000 tokens per request = 1.37x (log)
- no fatal OOM; no device correctness error

## 5. Runs

- Run1: 256 success / 0 fail (warmup, discarded)
- Run2: 256 success / 0 fail

Machine-extracted (run2.log + run2-summary):

- TOTAL_TOKEN_THROUGHPUT = 1760.92 tok/s
- OUTPUT_TOKEN_THROUGHPUT = 27.09 tok/s
- REQUEST_THROUGHPUT = 0.0312 req/s
- MEAN_TTFT = 2064099.81 ms; P99_TTFT = 2429862.46 ms
- MEAN_TPOT = 46.16 ms; P99_TPOT = 47.90 ms; MEAN_ITL = 46.16 ms

## 6. Machine recompute (authoritative)

- delta = (1760.92 / 927.59 - 1) x 100 = **+89.8382%** (approx +89.84%)
- achievement (D-024) = (1760.92 / 6016) / (5054.66 / 15824) x 100 = **91.6359%** (approx 91.63%)
- 80% absolute target = 5054.66 / 15824 * 6016 * 0.80 = **1537.35 tok/s**

## 7. Client wedge / json writer anomaly

- First 64K bench attempt: client wedged at tqdm 128/256 (server kept completing) -> ABORTED / INVALID ATTEMPT (`64K-FOLLOWUP-1`), not mixed into the valid Run2 metrics.
- Clean relaunch of same profile -> full Run1 + Run2 (`64K-FOLLOWUP-2` = the record above).
- run2.json 0-byte/absent (bench `--save-json` writer quirk observed on this stack). run2.log complete, 256/0, command correct, token/duration/throughput internally consistent -> exploratory qualification stands.

`SOURCE_OF_TRUTH_FOR_THIS_EXPLORATORY_RUN = run2.log`

Formal validation later MUST resolve a machine-readable result artifact.

## 8. Classification

- **STRONG EXPLORATORY CANDIDATE**
- 64K: `64K_FOLLOWUP_PASS` (1760.92 >= 1537.35)
- candidate: `MEMORY-HEADROOM 0.95 / 67000 PROFILE`
- conclusion: 0.95 + 67000 satisfies the real 64K input + 1K output requirement; 0.97 / 70000 (Attempt-003, 16K 2116.32) stays as historical Evidence and is NOT the current first-choice candidate.

## 9. Next phase recommendation

Full-matrix candidate validation of the 0.95/67000/96/MTP-OFF/DP2-TP8-EP/48/4096 profile (contract unchanged per cell):

- Recommended: fill the JSON writer bug first, then run **formal 4-run validation** per cell (Run1 discard; Mean(Run2,Run3,Run4)) with D-023 machine-verified Evidence (all four cells).
- Fallback if writer cannot be fixed timely: interim **exploratory 2-run matrix** (Run2 measured per cell), clearly marked exploratory.

## 10. Options / governance

- Formal OPT-01 stays `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION` unless governance decides to create a new profile-level OPT.
- No Formal Results were created.
- SERVICE_LEFT_RUNNING=YES (PID 3164838; port 8000; log /workspace/glm52_od_64k_candidate.log) - retain until User decides.
- D-024 basis not changed; PROVENANCE transcription issues only.

_End of 64K follow-up review._