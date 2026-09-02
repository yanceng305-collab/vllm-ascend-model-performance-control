# GLM-5.2-W8A8 Ascend Targets

**Status**: CALCULABLE (active basis per Decision D-024, effective 2026-09-02)

**Comparison class**: `ENGINEERING_REFERENCE` (H100 FP8 vs A3 W8A8)

**Primary acceptance metric**: Normalized Total Token Throughput

## Hardware Compute Basis (active, Decision D-024)

D-024 corrects the A3 compute-basis portion of D-020 (historical; D-020 preserved).

**A3/910C**: 752 TFLOPS per physical card @ FP16  
**A3 system**: 8 physical cards x 752 = **6016 TFLOPS**

**H100** (unchanged): 989 TFLOPS per physical card @ FP8  
**H100 system**: 16 cards x 989 = **15824 TFLOPS**

**measured A3**: 6019.718 TFLOPS (ascend-dmi) - evidence/reference ONLY; never a normalization denominator. The superseded basis 8 x 756 = 6048 (D-020) is historical provenance only.

**Compute ratio**: R = 6016 / 15824 = 0.380182

## Normalization Formula

```
A3_Normalized = TotalTokenThroughput_A3 / 8 cards / 752 TFLOPS/card
H100_Normalized = TotalTokenThroughput_H100 / 16 cards / 989 TFLOPS/card
Achievement = A3_Normalized / H100_Normalized
Pass condition: Achievement >= 0.80
```

All derived active values below were machine-computed from hardware-normalization-config.yaml (752/6016) plus model-workload references and accepted raw data; no manual transcription of factual arithmetic.

## Target Cells
### 1K Cell

- H100 reference: **2688.71 tok/s**
- A3 80% target: **817.76 tok/s** (machine recomputed)
- A3 accepted: 676.60 tok/s
- Achievement: **66.19%** (machine recomputed)
- Disposition: **BELOW TARGET** (gap 141.16 tok/s)

### 4K Cell

- H100 reference: **4063.45 tok/s**
- A3 80% target: **1235.88 tok/s**
- A3 accepted: 820.76 tok/s
- Achievement: **53.13%**
- Disposition: **BELOW TARGET** (gap 415.12 tok/s)

### 16K Cell

- H100 reference: **4379.60 tok/s**
- A3 80% target: **1332.04 tok/s**
- A3 accepted: 957.94 tok/s
- Achievement: **57.53%**
- Disposition: **BELOW TARGET** (gap 374.10 tok/s)

### 64K Cell

- H100 reference: **5054.66 tok/s**
- A3 80% target: **1537.35 tok/s**
- A3 accepted: 927.59 tok/s
- Achievement: **48.27%**
- Disposition: **BELOW TARGET** (gap 609.76 tok/s)
## Target Summary Table

| Cell | H100 ref (tok/s) | 80% target A3 (tok/s) | A3 raw (tok/s) | Achievement | Disposition |
|---|---|---|---|---|---|
| 1K | 2688.71 | 817.76 | 676.60 | 66.19% | BELOW TARGET |
| 4K | 4063.45 | 1235.88 | 820.76 | 53.13% | BELOW TARGET |
| 16K | 4379.60 | 1332.04 | 957.94 | 57.53% | BELOW TARGET |
| 64K | 5054.66 | 1537.35 | 927.59 | 48.27% | BELOW TARGET |

## Notes

- Achievements and 80% targets are machine-computed on the D-024 basis (6016); the prior D-020-basis figures (65.84% / 52.85% / 57.23% / 48.01% on 6048) are superseded for active tracking and retained only in historical records.
- Decision D-024 supersedes D-020 for the A3 compute basis; H100 unchanged.
- All four accepted baseline cells remain BELOW TARGET (need >= 80%); optimization gap persists.
- measured 6019.718 TFLOPS is evidence only and never becomes the denominator.
- 64K also has a historical immutable Result (2026-09-01) with originally recorded (old-basis) values; see RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md.
- Machine source: docs/vllm-ascend-performance/hardware-normalization-config.yaml, docs/vllm-ascend-performance/model-workload-references.yaml, results index + correction supplement.
