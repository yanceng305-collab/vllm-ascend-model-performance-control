# Result: GLM-5.2-W8A8 1K Baseline (Evidence-Backed)

**Result ID**: `RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958`  
**Model**: GLM-5.2-W8A8  
**Workload**: 1024 input tokens, 1024 output tokens  
**Task**: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION  
**Evidence Run**: run-20260902-140958  
**DISPATCH_CONTROL_SHA**: 26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5  
**Result Created**: 2026-09-02  
**Created By**: PerfControl  
**Status**: ACCEPTED (Baseline Established)

---

## Evidence-Backed Performance

**Primary Metric**: Total Token Throughput (tokens/second, higher is better)

### Raw Evidence (Run 2, 3, 4)

From Evidence package `run-20260902-140958`:

- **Run 2**: 675.16 tok/s (completed: 256, failed: 0)
- **Run 3**: 678.84 tok/s (completed: 256, failed: 0)
- **Run 4**: 675.79 tok/s (completed: 256, failed: 0)

### Independent Calculation

**Mean (Run2, Run3, Run4)**: **676.59 tok/s**

(Run1 discarded as warmup per contract)

---

## Normalized Achievement (Decision D-020)

**Hardware Compute Basis**:
- A3/910C System: 6048 TFLOPS (8 cards × 756 TFLOPS FP16)
- H100 System: 15824 TFLOPS (8 cards × 1979 TFLOPS FP8)

**H100 Reference** (1K input, 1024 output): 2688.71 tok/s

**Achievement Calculation**:
```
Achievement = (A3_throughput / A3_compute) / (H100_throughput / H100_compute)
            = (676.59 / 6048) / (2688.71 / 15824)
            = 65.84%
```

**Target**: ≥80% (per Decision D-020)

**Status**: **BELOW TARGET** (65.84% < 80%)

---

## Workload Contract

- **Input tokens**: 1024
- **Output tokens**: 1024
- **Max concurrency**: 64
- **Num prompts**: 256
- **Dataset**: random
- **Endpoint**: `/v1/completions`
- **ignore_eos**: true
- **Request rate**: inf
- **Random range ratio**: 0
- **Runs**: 4 (run1 warmup/discard, mean of run2/run3/run4)

---

## Runtime Identity

From Evidence `runtime-identity.txt`:

**Container**: `model-test-zyg-a3`

**Image Digest**: (recorded in Evidence runtime-identity.txt)

**Runtime Versions**:
- vLLM: 0.6.4.post1
- vLLM-Ascend: 0.6.4.post1+ascend1.0.0rc1
- CANN: 8.0.0
- torch: 2.1.0
- torch_npu: 2.1.0.post6
- Python: 3.10.x

(Full versions in Evidence package)

---

## Evidence Provenance

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz`  
**Archive SHA256**: `8818e4ffaf88a23989c36f0a17376843f8078adc522a32bddf682aed401816d2`  
**Evidence Location**: GitHub Release Asset `evidence-test-glm52-run-20260902-140958`  
**Transport**: Per Decision D-022 (GitHub Release Asset Evidence Transport)

**Evidence Contents**:
- `MANIFEST.txt`: Complete artifact inventory
- `COMMANDS.txt`: Execution command log
- `SHA256SUMS.txt`: All artifact checksums
- `control-sha.txt`: Task ID, DISPATCH_CONTROL_SHA, Authorization
- `runtime-identity.txt`: Container/image/version snapshot
- `1K/run1.log`, `1K/run2.log`, `1K/run3.log`, `1K/run4.log`: Benchmark output logs
- `1K/average_run2_4.txt`: Runner-computed aggregation
- `COMPARISON-REPORT.txt`: User-provided vs Evidence-backed comparison
- `RUNNER-REPORT.txt`: A3PerfRunner final report
- `EVIDENCE-GATE-STATUS.txt`: Completeness verification

**Evidence Integrity**: All checksums verified. Completeness gate: PASS.

---

## Comparison with User-Provided Values

**User-Provided (XLSX, 2026-09-02)**: 676.60 tok/s  
**Evidence-Backed (Mean Run2-4)**: 676.59 tok/s  
**Difference**: -0.01 tok/s (0.00% variance)

**Assessment**: Values match within rounding precision. Evidence-backed calculation confirms User-measured baseline.

---

## Formal Review

**PerfControl Review Date**: 2026-09-02

**Evidence Quality**: ✓ PASS
- All four runs present and complete
- Run2/3/4: completed==256, failed==0
- Workload contract verified (1024in/1024out, 256 prompts, ignore_eos=true)
- Runtime identity captured
- SHA256 checksums verified

**Calculation Integrity**: ✓ PASS
- Independent recalculation from raw Evidence
- Mean(Run2, Run3, Run4) = 676.59 tok/s
- Matches Runner calculation
- Matches User-provided value (within rounding)

**Provenance**: ✓ PASS
- DISPATCH_CONTROL_SHA recorded: 26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5
- Task ID recorded: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
- Authorization: EXECUTE
- Evidence archive SHA256 verified

---

## Formal Acceptance

**Status**: **ACCEPTED**

**Rationale**: Evidence completeness, workload contract, runtime identity, and calculation integrity all verified. This Result establishes the formal 1K baseline for GLM-5.2-W8A8 on A3/910C hardware with the verified runtime (vLLM 0.6.4.post1+ascend).

**Performance Assessment**: Current throughput (676.59 tok/s) achieves 65.84% of the normalized target. This is **below the 80% threshold** per Decision D-020, establishing a performance gap for optimization work.

**Next Steps**: Baseline formally accepted. Optimization Tasks may now compare against this immutable baseline.

---

## Immutability

This Result is **immutable**. Any corrections, re-measurements, or optimizations require new Evidence captures and new Result documents.

**Historical Note**: This is the first formal Evidence-backed Result for the 1K cell. User-measured value (676.60 tok/s, 2026-09-02) remains valid historical provenance.

---

## References

- Task: `docs/vllm-ascend-performance/models/glm-5.2-w8a8/TASK-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION.md`
- Prompt: `docs/vllm-ascend-performance/models/glm-5.2-w8a8/A3PERFRUNNER-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION-PROMPT.md`
- Decision D-019: Baseline execution mode
- Decision D-020: Hardware compute basis and normalization
- Decision D-021: PerfControl/A3PerfRunner separation
- Decision D-022: GitHub Release Asset Evidence Transport
- Evidence Archive: GitHub Release `evidence-test-glm52-run-20260902-140958`
