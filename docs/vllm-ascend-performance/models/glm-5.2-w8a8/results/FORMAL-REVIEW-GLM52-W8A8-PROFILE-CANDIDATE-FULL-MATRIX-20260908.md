# Formal Review: GLM52-W8A8 Profile-Candidate Full-Matrix Result

**Reviewer**: PerfControl
**Review date**: 2026-09-08
**Classification**: `FORMAL_CANDIDATE_RESULT_REVIEW_PASS`

## Reviewed Artifacts

- Result: `RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-20260907.md`
- Result blob SHA: `0f46a8da08c90ecf8b8c9221541b226691ba4f04`
- Canonical input: `CANDIDATE-RESULT-INPUT-GLM52-W8A8-FULL-MATRIX-20260907.json`
- Canonical input blob SHA: `1fda31070e72d99b041ff5d755a440f0eb09486b`
- Result-generation commit: `06271d0bccbae2a69ffc13eddd95089227d6c042`
- Result-generation Control SHA: `688b87e927b24a008075335a782a62fe4dff104d`
- Evidence dispatch SHA: `2711b6ed366d84187a1102b60186d42c5ba198cd`

## Fresh Provenance

Fresh GitHub metadata was obtained for Release `glm52-od-profile-full-matrix-20260903`:

| field | value |
|---|---|
| release id | `382481190` |
| release name | `GLM52-W8A8 FULL-MATRIX CANDIDATE VALIDATION: PASS` |
| published_at | `2026-09-04T04:41:56Z` |
| primary asset | `543798263` / `fullmatrix-evidence.tar.gz` / 53550 bytes |
| primary digest | `sha256:01eb1b5f7163fe52956483fae2316851e4fcdaaa064c43301af3c69deb94ee03` |
| sidecar | `543798262` / `fullmatrix-evidence.tar.gz.sha256` / 93 bytes |
| sidecar digest | `sha256:bea018e159b2df844df896643e30e985b9b07d9eb9545543bc1341dbaaf644bc` |
| tag ref | `refs/tags/glm52-od-profile-full-matrix-20260903` |
| tag object | `commit` / `2711b6ed366d84187a1102b60186d42c5ba198cd` |

The downloaded archive SHA256 matched both the fresh Release digest and the sidecar value. The isolated Evidence unpack had `SHA256SUMS.txt` 92/92 PASS, `matrix-validation.json` PASS with 12 measured and 4 warmup runs, and four `run1.role.txt` files all set to `WARMUP_DISCARD`.

## Validation Gates

- Formal validator with fresh Release/tag-ref: `FORMAL_CANDIDATE_RESULT_VALIDATION_PASS`.
- Candidate tooling: A-BM `65/65 PASS`, `0 FAIL`, `0 SKIP`, unexpected crash/traceback `0`.
- Matrix tooling: `7/7 PASS`, `0 FAIL`, `0 SKIP`.
- Canonical input: schema `candidate-result-input`, version `2`; result type `PROFILE_CANDIDATE_FULL_MATRIX`; state `READY_FOR_FORMAL_REVIEW`; formal note `NOT_YET_FORMALLY_ACCEPTED`.
- Evidence Review classification: `FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS`.

## Independent Recompute

The following values were independently recomputed from canonical input raw Run2/Run3/Run4 values and the D-024 config, without invoking the generator or validator calculation path.

| cell | raw Run2 / Run3 / Run4 | mean | min | max | population stddev | CV% | baseline delta% | achievement% | 80% target | target_met |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1K | 1198.14 / 1194.81 / 1222.32 | 1205.0900 | 1194.8100 | 1222.3200 | 12.259062 | 1.0173 | 78.1097 | 117.8919 | 817.7593 | True |
| 4K | 1631.80 / 1629.85 / 1627.29 | 1629.6467 | 1627.2900 | 1631.8000 | 1.846805 | 0.1133 | 98.5534 | 105.4890 | 1235.8804 | True |
| 16K | 1935.41 / 1934.05 / 1937.61 | 1935.6900 | 1934.0500 | 1937.6100 | 1.466788 | 0.0758 | 102.0680 | 116.2545 | 1332.0361 | True |
| 64K | 1772.28 / 1756.94 / 1769.89 | 1766.3700 | 1756.9400 | 1772.2800 | 6.739026 | 0.3815 | 90.4257 | 91.9175 | 1537.3526 | True |

All four achievements are at least 80%. Baselines are the accepted corrected values 676.60 / 820.76 / 957.94 / 927.59. D-024 is exact: A3 `8 x 752 = 6016`, H100 `16 x 989 = 15824`, target `0.80`, decision `D-024`. No historical baseline was modified.

## Profile, Runtime, and Environment

Frozen candidate profile remains 0.95 utilization, 67000 max model length, capture size 96, MTP OFF, DP2/TP8/EP ON, 48 sequences, 4096 batched tokens, async scheduling ON, multistream overlap ON, `FULL_DECODE_ONLY`, prefix cache OFF. Runtime model path is `/data/tiankuan/zyg/model/GLM-5.2-w8a8`.

Runtime identity is consistent: container `model-test-zyg-a3`; image `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`; vLLM `0.24.0`; plugin `ascend`; pid `3164838`; port `8000`; log `/workspace/glm52_od_64k_candidate.log`.

The canonical/result environment matches exactly, including explicit `_unset`: `ASCEND_LAUNCH_BLOCKING`, `LD_PRELOAD`, `VLLM_ASCEND_ENABLE_FLASHCOMM1`, `VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE`, and `VLLM_VERSION`.

## Boundary

Result state remains `READY_FOR_FORMAL_REVIEW`; formal note remains `NOT_YET_FORMALLY_ACCEPTED`; candidate remains `FINAL_RECOMMENDED_PROFILE_CANDIDATE`; Formal OPT-01 remains `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`. No A3, SSH, docker, benchmark, Evidence rerun, Release modification, factual Result/input edit, or Formal Acceptance was performed.

**Final Review classification**: `FORMAL_CANDIDATE_RESULT_REVIEW_PASS`
**Next stage**: `FORMAL_CANDIDATE_ACCEPTANCE`
**Acceptance status**: `NOT_YET_FORMALLY_ACCEPTED`
