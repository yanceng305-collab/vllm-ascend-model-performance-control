# RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED

**Result ID**: RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED  
**Date**: 2026-09-01  
**Status**: USER-PROVIDED MEASURED BASELINE  
**Model**: GLM-5.2-W8A8  
**Workload**: 65536 input + 1024 output, C64, 256 prompts

## Provenance

This Result records User-provided measured baseline performance for GLM-5.2-W8A8 on A3 with 64K input workload. The benchmark was executed by User prior to formal A3PerfRunner Task dispatch. Raw benchmark stdout/JSON and full Evidence are not yet ingested into Control Evidence pointers. This Result establishes the measured baseline for comparison purposes.

When A3PerfRunner executes the frozen baseline scripts (see RUNBOOK.md), it will produce a new Evidence-backed Result that can be compared against this User-measured baseline.

## Runtime Identity

| Field | Value |
|---|---|
| Image | `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3` |
| vLLM | 0.24.0+empty |
| vLLM-Ascend | 0.19.1rc2.dev1157+g6443b2a38 |
| vLLM-Ascend commit | 6443b2a38b95390e4f5174ff7ad2f8c3751e040f |
| Container | model-test-zyg-a3 |
| Model path | /data/tiankuan/zyg/model/GLM-5.2-w8a8 |

## Configuration

| Parameter | Value |
|---|---|
| Tensor parallel size | 16 |
| Max model length | 70000 |
| GPU memory utilization | 0.9 |
| Quantization | ascend |
| Prefix caching | OFF |
| Request logging | OFF |
| Graph mode | FULL_DECODE_ONLY |

## Workload

| Parameter | Value |
|---|---|
| Input tokens | 65536 |
| Output tokens | 1024 |
| Max concurrency | 64 |
| Num prompts | 256 |
| Dataset | random |
| Endpoint | /v1/completions |
| ignore_eos | true |
| Request rate | inf |
| Random range ratio | 0 |

## Raw Results

| Metric | Value | Unit |
|---|---|---|
| Successful requests | 256 | requests |
| Failed requests | 0 | requests |
| Benchmark duration | 18372.35 | seconds |
| Total input tokens | 16777216 | tokens |
| Total generated tokens | 262144 | tokens |
| Request throughput | 0.01 | req/s |
| Output token throughput | 14.27 | tok/s |
| **Total token throughput** | **927.45** | **tok/s** |
| Peak output token throughput | 24.00 | tok/s |
| Peak concurrent requests | 65 | requests |
| Mean TTFT | 3982603.58 | ms |
| Median TTFT | 4546936.22 | ms |
| P99 TTFT | 4551097.37 | ms |
| Mean TPOT | 44.42 | ms |
| Median TPOT | 44.38 | ms |
| P99 TPOT | 44.72 | ms |
| Mean ITL | 44.42 | ms |
| Median ITL | 44.47 | ms |
| P99 ITL | 45.30 | ms |

## Hardware Compute Basis (Decision D-020)

**A3 system**: 8 physical cards × 756 TFLOPS/card = **6048 TFLOPS** (User-approved unified basis)  
**Measured A3 compute** (ascend-dmi): 6019.718 TFLOPS

**H100 system**: 16 cards × 989 TFLOPS/card = **15824 TFLOPS**

**Comparison class**: ENGINEERING_REFERENCE (H100 FP8 vs A3 W8A8)

## Normalized Performance Analysis

**Primary acceptance metric**: Normalized Total Token Throughput

### A3 Normalized Throughput

```
A3_Normalized = 927.45 tok/s / 8 cards / 756 TFLOPS/card
              = 927.45 / 6048
              = 0.153373 tok/s per TFLOPS
```

### H100 Reference (SRC-B-GLM-64K)

User-provided H100 reference cell shows:
- Total token throughput: 5054.66 tok/s (from User source material)
- 16 H100 cards, FP8 precision

```
H100_Normalized = 5054.66 tok/s / 16 cards / 989 TFLOPS/card
                = 5054.66 / 15824
                = 0.319431 tok/s per TFLOPS
```

### Achievement

```
Achievement = A3_Normalized / H100_Normalized
            = 0.153373 / 0.319431
            = 0.4801
            = 48.01%
```

### Target and Disposition

**Target (80% of H100 normalized)**: 0.80 × 0.319431 = 0.255545 tok/s per TFLOPS  
**Measured A3**: 0.153373 tok/s per TFLOPS  
**Achievement**: 48.01%

**Disposition**: **BELOW TARGET / FAIL**

User acceptance target is ≥80%. Current baseline achieves 48.01%.

## Observed Symptoms

During 64K+C64 execution, the following was observed:

- Running: 1 request
- Waiting: 63 requests
- KV cache usage: ~85%

**A3 Mean TPOT**: 44.42 ms  
**H100 Mean TPOT** (reference): 42.32 ms

These observations suggest potential scheduling/capacity constraints. However, root cause analysis requires additional profiling and controlled optimization experiments. This is recorded as an observed symptom, not a confirmed root cause.

## Next Steps

1. **Baseline reproduction**: A3PerfRunner executes frozen baseline scripts to produce Evidence-backed Result
2. **1K/4K/16K cells**: Complete baseline measurement matrix
3. **Root cause analysis**: Profiling to identify bottlenecks (KV cache, scheduling, communication, kernel performance)
4. **Optimization track**: Separate OPT Tasks with controlled parameter changes, each producing independent Results compared against this baseline
5. **Target**: Achieve ≥80% normalized throughput (0.255545 tok/s per TFLOPS or higher)

## Notes

- This is a USER-PROVIDED MEASURED BASELINE, not yet backed by formal A3PerfRunner Evidence in Control repo
- Raw benchmark JSON/logs exist on A3 server but are not yet ingested into Evidence pointers
- Baseline is frozen; optimizations must be tracked as separate OPT Tasks
- See Decision D-019 for GLM-5.2-W8A8 baseline execution mode
- See Decision D-020 for hardware compute basis and normalization policy
