# GLM-5.2-W8A8 Results

## Baseline Results

| Result ID | Date | Status | Workload | Achievement | Disposition |
|---|---|---|---|---|---|
| [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md) | 2026-09-01 | USER-PROVIDED MEASURED BASELINE | 64K input + 1K output, C64 | 48.01% | BELOW TARGET |

## Notes

- **RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED**: User-provided baseline measurement establishing current 64K performance. Not yet backed by formal A3PerfRunner Evidence. Serves as reference for future optimization Tasks.
- Target: ≥80% normalized throughput relative to H100 reference (per Decision D-020)
- Baseline execution mode: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION (per Decision D-019)

## Pending

- Complete baseline matrix: 1K, 4K, 16K input cells
- A3PerfRunner Evidence-backed reproduction using frozen scripts
- Optimization Tasks (separate OPT Results)
