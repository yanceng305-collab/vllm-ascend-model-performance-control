# Metric Definitions

| Direction | Examples | Typical interpretation |
|---|---|---|
| `HIGHER_IS_BETTER` | output tokens/s, total tokens/s, request throughput, samples/s | Larger value is better; use scaled 80% target when the cell is comparable. |
| `LOWER_IS_BETTER` | TTFT, TPOT, ITL, request latency | Smaller value is better; inverse normalization is opt-in per contract. |

For each metric, freeze the numerator/denominator, tokenizer accounting, inclusion of prompt and generated tokens, warm-up treatment, aggregation, units, and gate class. Do not compare values with different definitions.
