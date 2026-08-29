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

An H100 cell is a formal reference only when model variant, quantization, input/output lengths, concurrency, requests, request rate, sampling, EOS/cache assumptions, MTP, parallelism, benchmark type, and metric definition match the Ascend cell. Otherwise mark `NOT COMPARABLE` and do not calculate PASS/FAIL.
