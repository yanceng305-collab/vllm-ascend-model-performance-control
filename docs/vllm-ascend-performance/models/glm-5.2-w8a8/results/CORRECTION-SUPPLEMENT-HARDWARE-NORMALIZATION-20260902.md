# Correction Supplement: GLM-5.2-W8A8 Hardware Normalization (D-024)

**Supplement ID**: `CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902`
**Correction Date**: 2026-09-02
**Created By**: PerfControl (machine-driven)

**Correction cause**: User corrected a wrong hardware compute input.

## Basis change

- old basis = 756 x 8 = 6048 (D-020, now SUPERSEDED for A3 compute)
- new basis = 752 x 8 = 6016 (D-024, active)
- H100 unchanged = 989 x 16 = 15824
- measured A3 = 6019.718 (evidence/reference only; not the denominator)

## Derived values (machine-computed from config + accepted raw data)

| Cell | A3 raw (tok/s) | H100 ref (tok/s) | 80% target A3 (tok/s) | Achievement | Disposition |
|---|---|---|---|---|---|
| 1K | 676.60 | 2688.71 | 817.76 | 66.19% | BELOW TARGET |
| 4K | 820.76 | 4063.45 | 1235.88 | 53.13% | BELOW TARGET |
| 16K | 957.94 | 4379.60 | 1332.04 | 57.53% | BELOW TARGET |
| 64K | 927.59 | 5054.66 | 1537.35 | 48.27% | BELOW TARGET |

## Unchanged provenance

- raw benchmark throughput: unchanged
- Evidence archive: GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz
- archive SHA256: 8818e4ffaf88a23989c36f0a17376843f8078adc522a32bddf682aed401816d2
- runtime identity: unchanged
- original Result documents: immutable
- old correction supplement: immutable
- D-024 supersedes D-020 for A3 compute basis
- active values shall use D-024 basis 6016
- DISPATCH_CONTROL_SHA: 26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5