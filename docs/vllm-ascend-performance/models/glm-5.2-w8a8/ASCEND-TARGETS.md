# GLM-5.2-W8A8 Ascend Targets

**Status**: CALCULABLE (per Decision D-020, effective 2026-09-01)

**Comparison class**: `ENGINEERING_REFERENCE` (H100 FP8 vs A3 W8A8)

**Primary acceptance metric**: Normalized Total Token Throughput

## Hardware Compute Basis (Decision D-020)

**A3/910C**: 756 TFLOPS per physical card @ FP16 (suitable precision for W8A8 comparison)  
**A3 system**: 8 physical cards × 756 = **6048 TFLOPS**

**H100**: 989 TFLOPS per physical card @ FP8 (customer baseline precision)  
**H100 system**: 16 cards × 989 = **15824 TFLOPS**

**Measured A3 compute** (ascend-dmi -f -t fp16 -q --all): 6019.718 TFLOPS (recorded as evidence; 6048 TFLOPS is official normalization basis)

**Compute ratio**: R = 6048 / 15824 = 0.382267

## Normalization Formula

```
A3_Normalized = TotalTokenThroughput_A3 / 8 cards / 756 TFLOPS/card
H100_Normalized = TotalTokenThroughput_H100 / 16 cards / 989 TFLOPS/card

Achievement = A3_Normalized / H100_Normalized

Pass condition: Achievement >= 0.80
```

## Target Cells

### 64K Cell (baseline measured)

**H100 reference** (SRC-B-GLM-64K):
- Total token throughput: 5054.66 tok/s
- H100 normalized: 5054.66 / 15824 = 0.319431 tok/s per TFLOPS

**A3 target (80%)**:
- Target normalized: 0.80 × 0.319431 = 0.255545 tok/s per TFLOPS
- Target absolute: 0.255545 × 6048 = 1545.54 tok/s

**A3 measured baseline** (User-provided):
- Total token throughput: 927.45 tok/s
- A3 normalized: 927.45 / 6048 = 0.153373 tok/s per TFLOPS
- Achievement: 0.153373 / 0.319431 = 48.01%
- **Disposition**: BELOW TARGET (need ≥80%)

**Gap to target**: 1545.54 - 927.45 = 618.09 tok/s (need 66.6% improvement)

### 1K Cell (pending measurement)

**H100 reference** (SRC-B-GLM-1K): TBD

Target calculable once H100 reference extracted from source materials.

### 4K Cell (pending measurement)

**H100 reference** (SRC-B-GLM-4K): TBD

Target calculable once H100 reference extracted from source materials.

### 16K Cell (pending measurement)

**H100 reference** (SRC-B-GLM-16K): TBD

Target calculable once H100 reference extracted from source materials.

## Target Summary Table

| Cell | H100 Total Throughput (tok/s) | H100 Normalized (tok/s per TFLOPS) | Target Normalized (80%) | Target Absolute A3 (tok/s) | A3 Measured (tok/s) | Achievement | Disposition |
|---|---|---|---|---|---|---|---|
| 1K | TBD | TBD | TBD | TBD | Pending | - | - |
| 4K | TBD | TBD | TBD | TBD | Pending | - | - |
| 16K | TBD | TBD | TBD | TBD | Pending | - | - |
| 64K | 5054.66 | 0.319431 | 0.255545 | 1545.54 | 927.45 | 48.01% | BELOW TARGET |

## Notes

- Targets use exact unrounded values for comparison. Display rounding must not change disposition.
- Decision D-020 establishes User-approved unified hardware compute basis for GLM-5.2-W8A8.
- This is model-specific and does not automatically apply to DeepSeek, MiniMax, or future models.
- 1K/4K/16K H100 reference values to be extracted from User source materials (SOURCE-MATERIALS.md).
- Primary gate: Normalized Total Token Throughput ≥ 80% of H100 normalized reference.
- Secondary/observational metrics: TTFT, TPOT, ITL (not automatic gates per PERFORMANCE-NORMALIZATION-POLICY.md unless explicitly promoted).
