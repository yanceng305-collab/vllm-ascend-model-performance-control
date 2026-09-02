# Correction Supplement: GLM-5.2-W8A8 Baseline Evidence-Backed Results

**Supplement ID**: `CORRECTION-SUPPLEMENT-BASELINE-EVIDENCE-run-20260902-140958`  
**Correction Date**: 2026-09-02  
**Created By**: PerfControl  
**Reason**: Runtime identity transcription error and calculation rounding correction  

---

## Scope

This supplement corrects errors in the four baseline Results created from Evidence run `run-20260902-140958`:

1. `RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958.md`
2. `RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-run-20260902-140958.md`
3. `RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958.md`
4. `RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-run-20260902-140958.md`

**Original Results Status**: SUPERSEDED by this correction (original files remain unchanged per immutability rules)

---

## Corrections

### 1. Runtime Identity (All Four Cells)

**Error**: Original Results incorrectly recorded runtime as:
- vLLM: 0.6.4.post1
- vLLM-Ascend: 0.6.4.post1+ascend1.0.0rc1
- CANN: 8.0.0

**Correction**: Actual runtime identity from Evidence `runtime-identity.txt`:
- **Image**: `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`
- **Image SHA256**: `sha256:220a47883e42efacb201117d21ba95cc9693d539788ad0345d766e6dc9f4d7bf`
- **vLLM Version**: `0.24.0+empty`
- **vLLM-Ascend**: (0.19.1rc2 series, embedded in nightly-releases-v0.24.0rc-a3 image)
- **Container**: `model-test-zyg-a3` (ID: 096ffe238e57...)

**Root Cause**: PerfControl transcription error during initial Result authoring.

**Impact**: Runtime identity now matches frozen baseline identity (Decision D-019). No performance value changes.

---

### 2. Calculation Precision Corrections

#### 1K Cell

**Error**: Original Result recorded Mean(Run2,Run3,Run4) = 676.59 tok/s

**Correction**:
- Run 2: 675.16 tok/s
- Run 3: 678.84 tok/s
- Run 4: 675.79 tok/s
- **Corrected Mean**: (675.16 + 678.84 + 675.79) / 3 = **676.5966666...** = **676.60 tok/s** (rounded to 2 decimal places)

**Root Cause**: Incorrect rounding during transcription.

**Impact**: Corrected value 676.60 matches User-provided XLSX value exactly. Achievement remains 65.84% (H100 reference 2688.71, normalized calculation unchanged).

---

#### 4K Cell

**Status**: No correction needed.
- Run 2: 820.62, Run 3: 820.49, Run 4: 821.17
- Mean: 820.76 tok/s (correctly recorded in original Result)

---

#### 16K Cell

**Error**: Original Result recorded Mean(Run2,Run3,Run4) = 957.93 tok/s

**Correction**:
- Run 2: 956.91 tok/s
- Run 3: 959.19 tok/s
- Run 4: 957.71 tok/s
- **Corrected Mean**: (956.91 + 959.19 + 957.71) / 3 = **957.9366666...** = **957.94 tok/s** (rounded to 2 decimal places)

**Root Cause**: Incorrect rounding during transcription.

**Impact**: Corrected value 957.94 matches User-provided XLSX value exactly. Achievement remains 57.23% (H100 reference 4379.60, normalized calculation unchanged).

---

#### 64K Cell

**Status**: No correction needed.
- Run 2: 927.45, Run 3: 927.92, Run 4: 927.41
- Mean: 927.59 tok/s (correctly recorded in original Result)

---

### 3. H100 Compute Basis Provenance

**Error**: Some references in original Results may have cited "8 cards × 1979 TFLOPS".

**Correction**: Per Decision D-020, the sole formal definition is:
- **H100 System**: 15824 TFLOPS total
- **Derived from**: 16 × H100 × 989 TFLOPS FP8

Do not use "8 × 1979" formulation. The 15824 TFLOPS total is the authoritative basis.

---

## Corrected Performance Summary

| Cell | Corrected Mean (tok/s) | H100 Reference (tok/s) | Achievement | Status |
|---|---|---|---|---|
| 1K | **676.60** | 2688.71 | 65.84% | BELOW TARGET |
| 4K | 820.76 | 4063.45 | 52.85% | BELOW TARGET |
| 16K | **957.94** | 4379.60 | 57.23% | BELOW TARGET |
| 64K | 927.59 | 5054.66 | 48.01% | BELOW TARGET |

**Runtime**: Container `model-test-zyg-a3`, Image `nightly-releases-v0.24.0rc-a3`, vLLM `0.24.0+empty`

**Target**: ≥80% normalized throughput (Decision D-020). All cells BELOW TARGET.

---

## Corrected Formal Review

**PerfControl Review Date**: 2026-09-02 (correction review)

**Evidence Quality**: ✓ PASS (unchanged from original review)
- All four runs present and complete
- Run2/3/4: completed==256, failed==0
- Workload contract verified
- Runtime identity captured
- SHA256 checksums verified

**Calculation Integrity**: ✓ PASS (corrected)
- Independent recalculation from raw Evidence logs
- 1K: Mean(675.16, 678.84, 675.79) = 676.60 tok/s
- 4K: Mean(820.62, 820.49, 821.17) = 820.76 tok/s
- 16K: Mean(956.91, 959.19, 957.71) = 957.94 tok/s
- 64K: Mean(927.45, 927.92, 927.41) = 927.59 tok/s
- Matches User-provided XLSX values exactly (1K/4K/16K/64K)

**Provenance**: ✓ PASS (corrected)
- DISPATCH_CONTROL_SHA recorded: 26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5
- Task ID recorded: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
- Runtime identity: vLLM 0.24.0+empty, Image nightly-releases-v0.24.0rc-a3
- Evidence archive SHA256 verified

**Frozen Baseline Identity Match**: ✓ YES
- Evidence runtime (vLLM 0.24.0+empty) matches frozen baseline identity (Decision D-019)
- No BASELINE_IDENTITY_UNVERIFIED condition

---

## Corrected Formal Acceptance

**Status**: **ACCEPTED** (corrected baseline)

**Rationale**: After correction review, Evidence completeness, workload contract, runtime identity, and calculation integrity all verified. Runtime identity matches frozen baseline (vLLM 0.24.0+empty). Corrected calculations match User-provided XLSX values exactly.

This corrected baseline establishes the formal reference for GLM-5.2-W8A8 on A3/910C hardware with the frozen runtime (vLLM 0.24.0+empty, nightly-releases-v0.24.0rc-a3).

**Performance Assessment**: Current throughput achieves 48.01%-65.84% of normalized targets across cells. All cells **below the 80% threshold** per Decision D-020, establishing performance gap for optimization work.

**Optimization Track**: With corrected baseline formally accepted, optimization Tasks may now proceed.

---

## Disposition of Original Results

The four original Result files remain **unchanged and immutable** per `REPOSITORY-AND-EVIDENCE-RULES.md`:

- `RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958.md` → **SUPERSEDED** (runtime identity + calculation error; use corrected 676.60)
- `RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-run-20260902-140958.md` → **SUPERSEDED** (runtime identity error only; value 820.76 correct)
- `RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958.md` → **SUPERSEDED** (runtime identity + calculation error; use corrected 957.94)
- `RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-run-20260902-140958.md` → **SUPERSEDED** (runtime identity error only; value 927.59 correct)

**Authoritative Values**: Use corrected values from this Supplement for all baseline tracking and optimization comparisons.

---

## Evidence Provenance (Unchanged)

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz`  
**Archive SHA256**: `8818e4ffaf88a23989c36f0a17376843f8078adc522a32bddf682aed401816d2`  
**Evidence Location**: GitHub Release Asset `evidence-test-glm52-run-20260902-140958`  
**Transport**: Per Decision D-022 (GitHub Release Asset Evidence Transport)  
**DISPATCH_CONTROL_SHA**: `26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5`

---

## References

- Original Results: `RESULT-GLM52-W8A8-{1K,4K,16K,64K}-BASELINE-EVIDENCE-run-20260902-140958.md` (superseded, unchanged)
- Task: `TASK-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION.md`
- Decision D-019: Baseline execution mode
- Decision D-020: Hardware compute basis and normalization
- Decision D-021: PerfControl/A3PerfRunner separation
- Decision D-022: GitHub Release Asset Evidence Transport
- Evidence Archive: GitHub Release `evidence-test-glm52-run-20260902-140958`
- Repository Rule: `REPOSITORY-AND-EVIDENCE-RULES.md` (immutability and correction policy)
