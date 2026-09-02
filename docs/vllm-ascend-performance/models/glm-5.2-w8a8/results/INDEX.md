# GLM-5.2-W8A8 Results

## Baseline Matrix Status

**Complete baseline matrix measured by User** (2026-09-01 to 2026-09-02):
- 1K input + 1K output, C64: 676.60 tok/s (User-provided matrix summary, Evidence confirmation pending)
- 4K input + 1K output, C64: 820.76 tok/s (User-provided matrix summary, Evidence confirmation pending)
- 16K input + 1K output, C64: 957.94 tok/s (User-provided matrix summary, Evidence confirmation pending)
- 64K input + 1K output, C64: 927.45 tok/s (User-measured baseline, recorded below)

**Evidence formalization status**: A3PerfRunner Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION) will extract and formalize raw benchmark Evidence from existing container. Formal Evidence-backed Results pending.

## Baseline Results

| Result ID | Date | Status | Workload | Achievement | Disposition |
|---|---|---|---|---|---|
| [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md) | 2026-09-01 | USER-PROVIDED MEASURED BASELINE | 64K input + 1K output, C64 | 48.01% | BELOW TARGET |

## Notes

- **RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED**: User-provided baseline measurement establishing current 64K performance. Not yet backed by formal A3PerfRunner Evidence. Serves as reference for future optimization Tasks.
- **1K/4K/16K cells**: User-provided matrix summary from XLSX (2026-09-02). Raw benchmark files exist in container `model-test-zyg-a3`. Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION) will formalize Evidence and create formal Results.
- **Evidence Acquisition Task**: Read-only Evidence formalization from existing container. Will NOT re-run benchmarks unless specific Evidence is confirmed missing after review.
- Target: ≥80% normalized throughput relative to H100 reference (per Decision D-020)
- Baseline execution mode: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION (per Decision D-019)

## Pending

- Evidence Acquisition Task execution (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION)
- Evidence-backed Results for 1K/4K/16K/64K cells
- PerfControl Formal Review and Acceptance
- Optimization Tasks (separate OPT Results)
