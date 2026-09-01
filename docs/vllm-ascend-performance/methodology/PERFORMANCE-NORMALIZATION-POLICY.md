# Performance Normalization Policy

This is the User-defined performance acceptance heuristic for comparable cells. It is a compute-scaled reference, not a scientific assertion that theoretical compute ratios predict end-to-end LLM performance. Bandwidth, memory, KV cache, interconnect, collectives, kernels, attention, MoE communication, quantization, scheduler, batching, graph, and software stack can dominate observed results.

## Comparable compute basis

Only use `C_H100` and `C_ASCEND` when both are supported by User-approved data, official NVIDIA/Huawei specifications, official product documentation, or another auditable source. Both must use a defensible precision and model compute path; include device count; keep dense/sparse mode consistent; and never mix single-device with multi-device or different H100 SKUs. For W8A8, prefer a comparable W8A8-relevant compute basis. Record source URL, access date, SKU, precision, dense/sparse mode, per-device value, device count, and system total. `ENGINEERING_REFERENCE` permits a documented precision difference in the performance cell, but does not make the compute basis identical by assertion.

```text
C_system = C_per_device * device_count
R = C_ASCEND_system / C_H100_system
```

If a credible comparable basis cannot be established, target is `UNKNOWN / USER INPUT REQUIRED` and the cell cannot pass the normalized gate.

## Higher-is-better metrics

Default gate policy: output token throughput is `PRIMARY GATE`; total token throughput and request throughput are `SECONDARY REFERENCE` when applicable; TTFT, TPOT, ITL, and latency percentiles are `OBSERVATIONAL / GUARDRAIL` unless a future approved Contract explicitly promotes one to a gate.

For throughput-like metrics such as tokens/s, output tokens/s, total throughput, request throughput, or samples/s:

```text
Equivalent_Ascend = P_H100 * R
Target_80 = P_H100 * R * 0.80
Achievement = P_ASCEND / Equivalent_Ascend * 100%
PASS iff P_ASCEND >= Target_80
```

Use exact, unrounded values for comparison. Display rounding must never change the disposition.

## Lower-is-better metrics

Latency metrics such as TTFT, TPOT, ITL, and request latency are not automatically gates. If the approved contract explicitly applies the normalized policy:

```text
Equivalent_Ascend_Latency = H100_Latency / R
Allowed_80_Latency = H100_Latency / (R * 0.80)
PASS iff Ascend_Latency <= Allowed_80_Latency
```

Otherwise classify the metric as `SECONDARY REFERENCE` or `OBSERVATIONAL ONLY` and do not infer a normalized PASS/FAIL.

## Required Result fields

Every formal performance Result must show raw Ascend value, raw H100 value, both compute bases, device counts, ratio, normalized equivalent, 80% target/allowed maximum, exact measured value, achievement, direction, gate class, and disposition.

## Model-Specific Override: GLM-5.2-W8A8 (Decision D-020)

**GLM-5.2-W8A8** uses a model-specific normalization policy that overrides the generic methodology:

**Hardware compute basis**:
- A3: 8 cards × 756 TFLOPS (FP16) = **6048 TFLOPS**
- H100: 16 cards × 989 TFLOPS (FP16) = **15824 TFLOPS**

**Primary acceptance metric**: **Normalized Total Token Throughput** (not Output Token Throughput)

**Normalization formula**:
```text
A3_Normalized = TotalThroughput_A3 / 8 / 756
H100_Normalized = TotalThroughput_H100 / 16 / 989
Achievement = A3_Normalized / H100_Normalized
```

**Pass condition**: `Achievement >= 0.80`

This model-specific policy takes precedence over generic methodology for all GLM-5.2-W8A8 Results. See Decision D-020 and `models/glm-5.2-w8a8/ASCEND-TARGETS.md` for details.
