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

### 1K Cell (User-provided matrix summary)

**H100 reference** (SRC-B-GLM-1K):
- Total token throughput: 2688.71 tok/s
- H100 normalized: 2688.71 / 15824 = 0.169913422649141 tok/s per TFLOPS

**A3 target (80%)**:
- Target normalized: 0.80 × 0.169913422649141 = 0.135930738119313 tok/s per TFLOPS
- Target absolute: 0.135930738119313 × 6048 = 822.108304209564 tok/s

**A3 measured** (User-provided matrix summary, pending Evidence confirmation):
- Total token throughput: 676.60 tok/s
- A3 normalized: 676.60 / 6048 = 0.111874338624339 tok/s per TFLOPS
- Achievement: 0.111874338624339 / 0.169913422649141 = 0.658403534580168 = 65.84%
- **Disposition**: BELOW TARGET (need ≥80%)

**Gap to target**: 822.11 - 676.60 = 145.51 tok/s (need 21.5% improvement)

### 4K Cell (User-provided matrix summary)

**H100 reference** (SRC-B-GLM-4K):
- Total token throughput: 4063.45 tok/s
- H100 normalized: 4063.45 / 15824 = 0.256790318503539 tok/s per TFLOPS

**A3 target (80%)**:
- Target normalized: 0.80 × 0.256790318503539 = 0.205432254802831 tok/s per TFLOPS
- Target absolute: 0.205432254802831 × 6048 = 1242.45413405552 tok/s

**A3 measured** (User-provided matrix summary, pending Evidence confirmation):
- Total token throughput: 820.76 tok/s
- A3 normalized: 820.76 / 6048 = 0.135714285714286 tok/s per TFLOPS
- Achievement: 0.135714285714286 / 0.256790318503539 = 0.528532396593113 = 52.85%
- **Disposition**: BELOW TARGET (need ≥80%)

**Gap to target**: 1242.45 - 820.76 = 421.69 tok/s (need 51.4% improvement)

### 16K Cell (User-provided matrix summary)

**H100 reference** (SRC-B-GLM-16K):
- Total token throughput: 4379.60 tok/s
- H100 normalized: 4379.60 / 15824 = 0.276769464105157 tok/s per TFLOPS

**A3 target (80%)**:
- Target normalized: 0.80 × 0.276769464105157 = 0.221415571284126 tok/s per TFLOPS
- Target absolute: 0.221415571284126 × 6048 = 1339.11897407125 tok/s

**A3 measured** (User-provided matrix summary, pending Evidence confirmation):
- Total token throughput: 957.94 tok/s
- A3 normalized: 957.94 / 6048 = 0.158401322751323 tok/s per TFLOPS
- Achievement: 0.158401322751323 / 0.276769464105157 = 0.572301291989664 = 57.23%
- **Disposition**: BELOW TARGET (need ≥80%)

**Gap to target**: 1339.12 - 957.94 = 381.18 tok/s (need 39.8% improvement)

### 64K Cell (User-measured baseline)

**H100 reference** (SRC-B-GLM-64K):
- Total token throughput: 5054.66 tok/s
- H100 normalized: 5054.66 / 15824 = 0.319429979777553 tok/s per TFLOPS

**A3 target (80%)**:
- Target normalized: 0.80 × 0.319429979777553 = 0.255543983822042 tok/s per TFLOPS
- Target absolute: 0.255543983822042 × 6048 = 1545.52998326107 tok/s

**A3 measured baseline** (User-measured, recorded in RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED):
- Total token throughput: 927.45 tok/s (User-measured 2026-09-01)
- A3 normalized: 927.45 / 6048 = 0.153373015873016 tok/s per TFLOPS
- Achievement: 0.153373015873016 / 0.319429979777553 = 0.480136050156740 = 48.01%
- **Disposition**: BELOW TARGET (need ≥80%)

**Gap to target**: 1545.53 - 927.45 = 618.08 tok/s (need 66.6% improvement)

**Note on 64K provenance**: 
- Original User-measured Result (2026-09-01): 927.45 tok/s (immutable, recorded in RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md)
- User-provided matrix summary XLSX (2026-09-02): 927.59 tok/s
- Difference: 0.14 tok/s (0.015%)
- This minor difference does not affect disposition or normalized achievement materially
- When A3PerfRunner Evidence-backed Result is produced, it will use the exact value calculated from Run2/Run3/Run4 JSON aggregation

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
| 1K | 2688.71 | 0.169913 | 0.135931 | 822.11 | 676.60 † | 65.84% | BELOW TARGET |
| 4K | 4063.45 | 0.256790 | 0.205432 | 1242.45 | 820.76 † | 52.85% | BELOW TARGET |
| 16K | 4379.60 | 0.276769 | 0.221416 | 1339.12 | 957.94 † | 57.23% | BELOW TARGET |
| 64K | 5054.66 | 0.319430 | 0.255544 | 1545.53 | 927.45 * | 48.01% | BELOW TARGET |

**Legend**:
- `*` User-measured baseline (2026-09-01), Evidence-backed Result pending
- `†` User-provided matrix summary (2026-09-02), Evidence confirmation pending

## Notes

- Targets use exact unrounded values for comparison. Display rounding must not change disposition.
- Decision D-020 establishes User-approved unified hardware compute basis for GLM-5.2-W8A8.
- This is model-specific and does not automatically apply to DeepSeek, MiniMax, or future models.
- All four baseline matrix cells (1K/4K/16K/64K) are now measured by User:
  - 64K: User-measured baseline (2026-09-01), recorded in RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md
  - 1K/4K/16K: User-provided matrix summary from XLSX (2026-09-02), pending Evidence confirmation
- A3PerfRunner Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION) will formalize Evidence for all four cells
- Primary gate: Normalized Total Token Throughput ≥ 80% of H100 normalized reference
- Secondary/observational metrics: TTFT, TPOT, ITL (not automatic gates per PERFORMANCE-NORMALIZATION-POLICY.md unless explicitly promoted)
- All four cells currently BELOW TARGET; optimization track to be initiated after Evidence-backed baseline is formally established
