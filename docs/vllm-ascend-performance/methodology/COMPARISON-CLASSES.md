# Comparison Classes

## `STRICT_REFERENCE`

Use when the H100 and Ascend cells have the same model identity, principal precision/quantization, workload semantics, and metric definition. Workload fields include input/output lengths, concurrency, prompt count, dataset/random generation rule, sampling, `ignore_eos`, and metric definition.

## `ENGINEERING_REFERENCE`

Use when the cells are the same model family/variant and workload is sufficiently aligned, but precision/quantization differs (for example H100 FP8 versus Ascend W8A8). This class requires explicit User approval. The Result must highlight the precision difference and must not call the comparison apples-to-apples. It may support engineering normalization but is not a strict reference.

## `NOT_COMPARABLE`

Use when model identity, workload semantics, or metric definition differ too much to form a defensible engineering reference. Do not calculate normalized PASS/FAIL from this class.

## Allowed platform differences

H100 and Ascend may differ in TP, DP, EP, device count, graph/eager mode, kernels, scheduler, chunked prefill, communication, and platform-specific memory optimization. These are capabilities of the respective stacks, not workload identity fields. Record them explicitly; device-count effects enter the system-level compute normalization.
