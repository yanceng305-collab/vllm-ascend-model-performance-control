# Performance Normalization Policy

This is the User-defined performance acceptance heuristic for comparable cells. It is a compute-scaled reference, not a scientific assertion that theoretical compute ratios predict end-to-end LLM performance. Bandwidth, memory, KV cache, interconnect, collectives, kernels, attention, MoE communication, quantization, scheduler, batching, graph, and software stack can dominate observed results.

## Comparable compute basis

Only use `C_H100` and `C_ASCEND` when both are supported by User-approved data, official NVIDIA/Huawei specifications, official product documentation, or another auditable source. Both must use comparable precision and the model's main compute path; include device count; keep dense/sparse mode consistent; and never mix single-device with multi-device or different H100 SKUs. For W8A8, prefer a comparable W8A8-relevant compute basis. Record source URL, access date, SKU, precision, dense/sparse mode, per-device value, device count, and system total.

```text
C_system = C_per_device * device_count
R = C_ASCEND_system / C_H100_system
```

If a credible comparable basis cannot be established, target is `UNKNOWN / USER INPUT REQUIRED` and the cell cannot pass the normalized gate.

## Higher-is-better metrics

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
