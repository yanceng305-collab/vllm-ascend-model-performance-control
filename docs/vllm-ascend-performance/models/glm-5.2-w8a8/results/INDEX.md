# GLM-5.2-W8A8 Results

## Baseline Matrix Status

**Complete Evidence-backed baseline matrix established** (Evidence run: run-20260902-140958):
- 1K input + 1K output, C64: **676.59 tok/s** (Achievement: 65.84%, BELOW TARGET)
- 4K input + 1K output, C64: **820.76 tok/s** (Achievement: 52.85%, BELOW TARGET)
- 16K input + 1K output, C64: **957.93 tok/s** (Achievement: 57.23%, BELOW TARGET)
- 64K input + 1K output, C64: **927.59 tok/s** (Achievement: 48.01%, BELOW TARGET)

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz`  
**Archive SHA256**: `8818e4ffaf88a23989c36f0a17376843f8078adc522a32bddf682aed401816d2`  
**Evidence Location**: GitHub Release Asset `evidence-test-glm52-run-20260902-140958`  
**DISPATCH_CONTROL_SHA**: `26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5`

**Target**: ≥80% normalized throughput (per Decision D-020). All four cells **BELOW TARGET**; formal baseline established for optimization tracking.

## Baseline Results

| Result ID | Date | Status | Workload | Throughput | Achievement | Disposition |
|---|---|---|---|---|---|---|
| [RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | ACCEPTED | 1K input + 1K output, C64 | 676.59 tok/s | 65.84% | BELOW TARGET |
| [RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | ACCEPTED | 4K input + 1K output, C64 | 820.76 tok/s | 52.85% | BELOW TARGET |
| [RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | ACCEPTED | 16K input + 1K output, C64 | 957.93 tok/s | 57.23% | BELOW TARGET |
| [RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | ACCEPTED | 64K input + 1K output, C64 | 927.59 tok/s | 48.01% | BELOW TARGET |
| [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md) | 2026-09-01 | HISTORICAL | 64K input + 1K output, C64 | 927.45 tok/s | 48.01% | BELOW TARGET |

## Notes

- **Evidence-backed baseline matrix**: All four cells (1K/4K/16K/64K) formally established with Evidence-backed Results from A3PerfRunner Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION, run-20260902-140958).
- **PerfControl Formal Review and Acceptance**: Completed 2026-09-02. Evidence completeness, workload contract, runtime identity, calculation integrity all verified. All four cells formally ACCEPTED.
- **Historical 64K Result**: `RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md` (927.45 tok/s, 2026-09-01) remains valid historical provenance, unchanged and immutable.
- **Performance Assessment**: All cells below 80% normalized target (Decision D-020), establishing performance gap for optimization work.
- **Runtime**: Container `model-test-zyg-a3`, vLLM 0.6.4.post1, vLLM-Ascend 0.6.4.post1+ascend1.0.0rc1, CANN 8.0.0
- **Evidence Transport**: Per Decision D-022 (GitHub Release Asset Evidence Transport)

## Next Steps

- Baseline formally accepted; optimization track may begin
- Optimization Tasks will produce separate OPT Results compared against these immutable baseline Results
- Per Decision D-019: Baseline execution mode complete (USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION)
