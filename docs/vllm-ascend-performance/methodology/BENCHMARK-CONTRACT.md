# Benchmark Contract

This is the contract template. User-provided method material and an explicit Decision must fill or approve every field before a performance Task can become `READY`.

## Required workload identity

| Field | Value |
|---|---|
| Model / variant | `USER INPUT REQUIRED` |
| Quantization / precision | `USER INPUT REQUIRED` |
| Input tokens | `USER INPUT REQUIRED` |
| Output tokens | `USER INPUT REQUIRED` |
| Concurrency | `USER INPUT REQUIRED` |
| Request count | `USER INPUT REQUIRED` |
| Request rate | `USER INPUT REQUIRED` |
| Benchmark tool/version | `USER INPUT REQUIRED` |
| Sampling parameters | `USER INPUT REQUIRED` |
| `ignore_eos` | `USER INPUT REQUIRED` |
| Prefix/cache assumptions | `USER INPUT REQUIRED` |
| MTP | `USER INPUT REQUIRED` |
| Graph/eager mode | `USER INPUT REQUIRED` |
| TP/DP/EP | `USER INPUT REQUIRED` |
| Warm-up | `USER INPUT REQUIRED` |
| Repetitions/statistic | `USER INPUT REQUIRED` |

## Required metrics

Each metric must declare a name, unit, direction (`HIGHER_IS_BETTER` or `LOWER_IS_BETTER`), gate class (`PRIMARY GATE`, `SECONDARY REFERENCE`, or `OBSERVATIONAL ONLY`), and exact aggregation rule. Unspecified fields remain unknown; suggestions are not frozen policy.

## Source-observed method (not yet frozen)

The supplied DOCX shows one `vllm bench serve` case using a random dataset, input length 4,096, output length 1,024, maximum concurrency 64, 256 prompts, and `ignore_eos`. Reported fields include request/s, output/peak/total tokens/s, and mean/median/P99 TTFT, TPOT, and ITL. These values are source observations only. Warm-up, repeat count, outlier handling, aggregation choice, request-rate sweep, sampling, prefix cache, MTP, and graph/eager mode are not specified and require User Decision before a Task is `READY`.

## Cell comparability

An H100 cell is a reference when model identity/variant, input/output lengths, concurrency, prompt count, dataset/random generation rule, sampling, `ignore_eos`, benchmark type, and metric definition are aligned. TP, DP, EP, device count, graph/eager mode, kernel, scheduler, chunked prefill, communication, and platform-specific memory optimization may differ and must be recorded rather than used to reject comparability.

Assign one [comparison class](COMPARISON-CLASSES.md): `STRICT_REFERENCE` when principal precision/quantization also matches; `ENGINEERING_REFERENCE` when the same model family/variant and workload align but precision differs and User approval is recorded; or `NOT_COMPARABLE` when model/workload/metric differences are too large. Only the first two classes may supply a normalized engineering target, and the Result must state the class and differences.
