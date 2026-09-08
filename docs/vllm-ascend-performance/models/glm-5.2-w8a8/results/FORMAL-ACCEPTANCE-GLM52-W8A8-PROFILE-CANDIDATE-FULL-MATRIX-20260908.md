# Formal Acceptance: GLM52-W8A8 Profile Candidate Full-Matrix

**Acceptance date**: 2026-09-08
**Authority**: PerfControl
**Acceptance classification**: `FORMAL_CANDIDATE_ACCEPTANCE_PASS`

## Accepted Subject

This acceptance covers only the exact `GLM-5.2-W8A8` `PROFILE_CANDIDATE_FULL_MATRIX`
profile candidate:

- Accepted profile: `0.95 / 67000`
- Model: `GLM-5.2-W8A8`
- `gpu_memory_utilization=0.95`
- `max_model_len=67000`
- `max_cudagraph_capture_size=96`
- MTP OFF; DP2; TP8; EP ON
- `max_num_seqs=48`; `max_num_batched_tokens=4096`
- async scheduling ON; multistream overlap shared expert ON
- cudagraph mode `FULL_DECODE_ONLY`; prefix cache OFF
- model path `/data/tiankuan/zyg/model/GLM-5.2-w8a8`

This does not generalize to other GLM profiles or configurations.

## Reviewed Chain

| artifact | value |
|---|---|
| Machine Result | `RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-20260907.md` |
| Result blob SHA | `0f46a8da08c90ecf8b8c9221541b226691ba4f04` |
| Canonical input | `CANDIDATE-RESULT-INPUT-GLM52-W8A8-FULL-MATRIX-20260907.json` |
| Canonical input blob SHA | `1fda31070e72d99b041ff5d755a440f0eb09486b` |
| Result-generation commit | `06271d0bccbae2a69ffc13eddd95089227d6c042` |
| Formal Review | `FORMAL-REVIEW-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-20260908.md` |
| Formal Review commit | `d516cc4e28e2196b22f3de7ad45616fbaaac48d2` |
| Evidence dispatch SHA | `2711b6ed366d84187a1102b60186d42c5ba198cd` |

## Fresh Provenance and Gates

Fresh GitHub provenance remained unchanged:

- Release `382481190`, tag `glm52-od-profile-full-matrix-20260903`, name `GLM52-W8A8 FULL-MATRIX CANDIDATE VALIDATION: PASS`.
- Primary asset `543798263`, `fullmatrix-evidence.tar.gz`, 53550 bytes, digest `sha256:01eb1b5f7163fe52956483fae2316851e4fcdaaa064c43301af3c69deb94ee03`.
- Sidecar `543798262`, `fullmatrix-evidence.tar.gz.sha256`, 93 bytes, digest `sha256:bea018e159b2df844df896643e30e985b9b07d9eb9545543bc1341dbaaf644bc`.
- Tag ref `refs/tags/glm52-od-profile-full-matrix-20260903`, object type `commit`, SHA `2711b6ed366d84187a1102b60186d42c5ba198cd`.

Acceptance gates:

- Evidence Review: `FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS`.
- Machine generation: `FORMAL_CANDIDATE_RESULT_GENERATED_AND_MACHINE_VALIDATED`.
- Formal Review: `FORMAL_CANDIDATE_RESULT_REVIEW_PASS`.
- Fresh formal validator: `FORMAL_CANDIDATE_RESULT_VALIDATION_PASS`.
- Matrix: 12 measured, 4 warmup discarded; all measured runs 256 successful / 0 failed.

## Accepted Performance Scope

| cell | mean tok/s | D-024 achievement | target_met |
|---|---:|---:|---|
| 1K | 1205.0900 | 117.8919% | True |
| 4K | 1629.6467 | 105.4890% | True |
| 16K | 1935.6900 | 116.2545% | True |
| 64K | 1766.3700 | 91.9175% | True |

All four cells meet the D-024 80% minimum. This acceptance references the existing
machine Result; it is not a new benchmark Result and introduces no new measurements.

## Governance Boundary

The machine Result remains immutable with generation-time state
`READY_FOR_FORMAL_REVIEW` and formal note `NOT_YET_FORMALLY_ACCEPTED`. Acceptance is
carried by this separate artifact and the INDEX/STATUS records.

Formal OPT-01 remains exactly:

`BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`

This acceptance does not unlock, accept, close, or infer completion of OPT-01. No A3,
SSH, docker, benchmark, Evidence rerun, Release modification, Result/input edit, or
historical baseline modification was performed.

**Accepted profile**: `0.95 / 67000`
**Acceptance scope**: `PROFILE_CANDIDATE_FULL_MATRIX`
**Final classification**: `FORMAL_CANDIDATE_ACCEPTANCE_PASS`
