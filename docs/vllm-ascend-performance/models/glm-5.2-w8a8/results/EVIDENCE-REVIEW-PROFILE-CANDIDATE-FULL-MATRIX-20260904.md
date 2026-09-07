# Control Evidence Review: GLM52-W8A8 PROFILE-CANDIDATE FULL-MATRIX VALIDATION

**Reviewer**: PerfControl · **Date**: 2026-09-04
**Task**: `GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION`
**Dispatch Control SHA**: `2711b6ed366d84187a1102b60186d42c5ba198cd` (live verified; tag object commit equals it)

## 1. Release provenance (live GitHub API)

| key | value |
|---|---|
| release id | 382481190 |
| tag | `glm52-od-profile-full-matrix-20260903` |
| tag object commit | `2711b6ed366d84187a1102b60186d42c5ba198cd` |
| release name | GLM52-W8A8 FULL-MATRIX CANDIDATE VALIDATION: PASS |
| published | 2026-09-04T04:41:56Z |
| asset id | 543798263 |
| asset | `fullmatrix-evidence.tar.gz` (53550 bytes) |
| asset digest | `sha256:01eb1b5f7163fe52956483fae2316851e4fcdaaa064c43301af3c69deb94ee03` |
| sidecar id / size | 543798262 / 93 |
| sidecar digest | `sha256:bea018e159b2df844df896643e30e985b9b07d9eb9545543bc1341dbaaf644bc` |

Digests: GitHub metadata == **local recompute** == sidecar == Runner prose (match).

## 2. Archive integrity / identity

- Unpacked into an isolated dir; original asset untouched; MANIFEST.txt + SHA256SUMS.txt present.
- `SHA256SUMS.txt` verification **92/92 PASS** (0 bad).
- control-sha.txt == dispatch SHA; pinned tooling (4 scripts from dispatch-SHA blobs) == script-sha256sums.txt.
- runN.json present (writer anomaly did not recur).

## 3. Gates (independent re-run)

- raw re-extraction 16/16 `--strict` exit 0; regenerated metrics == evidence metrics;
- Run2/3/4 counts 256/0 every cell (Run1 parses);
- per-cell validators: 4x exit 0; regenerated validation/aggregation == evidence
  (only the absolute `cell_dir` differs);
- matrix validator: exit 0; measured=12; warmup discarded=4; profile identical;
  identity identical; all cells PASS; equal to evidence (only `matrix_dir` differs);
- frozen profile (== Task §2): gpu 0.95, len 67000, capture 96, MTP OFF, DP 2, TP 8, EP true,
  48 / 4096, async ON, multistream ON, FULL_DECODE_ONLY, prefix OFF; 0.97/70000 absent;
- warm reuse REUSE=YES; identity across cells identical (PID 3164838 ×6, 3164833 ×0 —
  prose tail `PID=3164833` is a typo; evidence PID 3164838, matches Task);
- client wedge: none in evidence (16/16 clean) → `NOT_APPLICABLE`.

## 4. Machine numbers

| cell | run2 | run3 | run4 | mean | min | max | std | CV% | delta% | ach% | 80% tgt | met |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1K | 1198.14 | 1194.81 | 1222.32 | 1205.0900 | 1194.81 | 1222.32 | 12.259062 | 1.0173 | 78.1097 | 117.8919 | 817.7593 | True |
| 4K | 1631.80 | 1629.85 | 1627.29 | 1629.6467 | 1627.29 | 1631.80 | 1.846805 | 0.1133 | 98.5534 | 105.4890 | 1235.8804 | True |
| 16K | 1935.41 | 1934.05 | 1937.61 | 1935.6900 | 1934.05 | 1937.61 | 1.466788 | 0.0758 | 102.0680 | 116.2545 | 1332.0361 | True |
| 64K | 1772.28 | 1756.94 | 1769.89 | 1766.3700 | 1756.94 | 1772.28 | 6.739026 | 0.3815 | 90.4257 | 91.9175 | 1537.3526 | True |

Latencies (run2): see per-cell info below.

- 1K: TTFT 3754.81 / 9350.11 ms, TPOT 103.16 / 107.52 ms, ITL 103.16 ms, req 0.5900 / s, out 599.07 tok/s
- 4K: TTFT 74073.16 / 138934.62 ms, TPOT 112.03 / 186.03 ms, ITL 112.03 ms, req 0.3200 / s, out 326.36 tok/s
- 16K: TTFT 432808.83 / 540634.43 ms, TPOT 78.09 / 80.09 ms, ITL 78.09 ms, req 0.1100 / s, out 113.85 tok/s
- 64K: TTFT 2064983.47 / 2432340.60 ms, TPOT 46.29 / 47.43 ms, ITL 46.29 ms, req 0.0300 / s, out 27.27 tok/s

## 5. Anomalies

- PID prose mismatch resolved — evidence single PID 3164838; no re-run.
- Manifest prose PASS-vs-not wording: artifact `matrix-validation.json` status=PASS and the
  independent re-run also exit 0 → evidence artifact is authoritative (prose only).

## 6. Classification

- **FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS**
- Candidate **`0.95 / 67000 = FINAL_RECOMMENDED_PROFILE_CANDIDATE`**
- No Formal Result; no Acceptance; OPT-01 still `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`.
- Next stage (separate dispatch): `MACHINE-GENERATED FORMAL CANDIDATE RESULT STAGE`.