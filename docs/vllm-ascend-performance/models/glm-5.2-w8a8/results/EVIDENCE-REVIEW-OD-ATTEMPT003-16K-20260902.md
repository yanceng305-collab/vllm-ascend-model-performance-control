# Control Evidence Review: GLM52-W8A8 Official-Derived Attempt-003 (16K)

**Review date**: 2026-09-02
**Reviewer**: PerfControl
**Evidence Release**: glm52-od-profile-16k-20260902-173728 (D-022)
**Task**: GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE
**DISPATCH_CONTROL_SHA (from control-sha.txt)**: `4b7cc685ee9d17e9be3082ad7d6b6bf88246a36d`

## 1. Transport authority

GitHub Release metadata (live API): archive `final-evidence-20260902-173728.tar.gz`, size 182281, digest `881d372520d0bbc863a109162404b063d3cc95da60d0bf6ecdfb52d67cf75266`. Local recompute: same value — MATCH.

Runner prose reported digest `5e07077d6e6446893f0d17a23402a7bf18d74b8dd73e31d51ce8c8fea58b2d32` — does NOT match Release metadata.

Recorded: `PROVENANCE_TRANSCRIPTION_DISCREPANCY`; GitHub Release asset metadata is the transport authority. No re-run triggered. This record uses the machine-read GitHub value only.

## 2. Attempt-003 reviewed profile (from evidence)

- model GLM-5.2-W8A8; runtime family: existing accepted vLLM 0.24 A3 runtime
- max-model-len: 70000; topology DP2/TP8/EP ON; gpu-memory-utilization 0.97; max_cudagraph_capture_size 96; max-num-seqs 48; max-num-batched-tokens 4096
- MTP/speculative: OFF; async scheduling ON; multistream_overlap_shared_expert ON; graph FULL_DECODE_ONLY
- prefix cache: OFF per project contract; actual effective config preferred if different
- CAPACITY PASS; /v1/models PASS

## 3. 16K Run2 machine extraction

run2.log: `Total token throughput (tok/s): 2116.32`
- Successful 256; Failed 0
- Output token throughput 124.49; request 0.12 req/s; duration 2099 s; total input tokens 4194304; total generated 262144

Machine delta vs accepted 957.94 tok/s:
```
(2116.32 / 957.94 - 1) * 100
```
= **+120.9241%** (≈ +120.92%)

## 4. run2.json absent / empty

01: Attempt-003 bench dir contains run1.log, run1.json, run2-summary.txt, run2.log; NO run2.json.
Reason: benchmark writer (JSON) bug.

- benchmark executed normally: 256/0, command matches contract, token counts consistent.
- `SOURCE_OF_TRUTH_FOR_THIS_EXPLORATORY_RUN = run2.log`
- Any later Formal Result / formal candidate validation MUST fix the writer and use machine-readable raw artifacts.

## 5. MTP finding (attempt-002 / 002R)

- util 0.97 + capture 96 + MTP3 ON: CAPACITY PASS; 16K C64 all 256 requests failed ("Never received valid chunk"), device-level "vector core execution is abnormal" logged; single-request probe OK.
- Attempt-003 with MTP off: 0 device errors, 256/0.

Formal wording: `MTP3 + current DP2/TP8/EP high-concurrency path = SUSPECTED INSTABILITY under load` (evidence-supported correlation / suspected trigger; not proven root cause; isolation remains future work).

## 6. Classification

- Candidate: STRONG EXPLORATORY CANDIDATE (Attempt-003 profile)
- 16K: PROFILE_MICROGATE_PASS (>= 1005.84); QUALIFIES_FOR_64K_FOLLOWUP=YES
- Formal OPT-01 remains BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION (unchanged)

## 7. Disposition

**PASS** for exploratory qualification. Caveats: run2.json writer bug (does not invalidate); MTP = suspected trigger. Not a Formal Result; no baseline change.

Next: 64K follow-up Task reusing warm Attempt-003 service (SERVICE_LEFT_RUNNING=YES; PID 257285; port 8000; log /workspace/glm52_od_attempt003.log).

_End of review._