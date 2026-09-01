#!/usr/bin/env python3
"""
Aggregate GLM-5.2-W8A8 benchmark runs.
Computes mean of run2, run3, run4 (run1 is discarded as warmup).
"""

import json
import statistics
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("Usage: summarize-runs.py <cell-result-dir>")

root = Path(sys.argv[1])

files = [
    root / "run2.json",
    root / "run3.json",
    root / "run4.json",
]

runs = []

for path in files:
    if not path.is_file():
        raise SystemExit(f"Missing result: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("completed") != 256:
        raise SystemExit(
            f"{path}: completed={data.get('completed')} != 256"
        )

    if data.get("failed", 0) != 0:
        raise SystemExit(
            f"{path}: failed={data.get('failed')} != 0"
        )

    runs.append(data)

metrics = [
    "duration",
    "request_throughput",
    "output_throughput",
    "total_token_throughput",
    "mean_ttft_ms",
    "median_ttft_ms",
    "p99_ttft_ms",
    "mean_tpot_ms",
    "median_tpot_ms",
    "p99_tpot_ms",
    "mean_itl_ms",
    "median_itl_ms",
    "p99_itl_ms",
]

# Add max_output_tokens_per_s if available
if "max_output_tokens_per_s" in runs[0]:
    metrics.append("max_output_tokens_per_s")

averages = {}

for key in metrics:
    values = [r[key] for r in runs if key in r]
    if len(values) == 3:
        averages[key] = statistics.mean(values)

out_json = root / "average_run2_4.json"
out_txt = root / "average_run2_4.txt"

with out_json.open("w", encoding="utf-8") as f:
    json.dump(
        {
            "aggregation": "mean of run2, run3, run4; run1 discarded",
            "runs_used": [2, 3, 4],
            "metrics": averages,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )

with out_txt.open("w", encoding="utf-8") as f:
    f.write("Aggregation: mean(run2, run3, run4); run1 discarded\n\n")

    for key, value in averages.items():
        f.write(f"{key}: {value:.6f}\n")

    f.write("\nPer-run max_concurrent_requests:\n")

    for idx, run in zip((2, 3, 4), runs):
        if "max_concurrent_requests" in run:
            f.write(
                f"run{idx}: {run['max_concurrent_requests']}\n"
            )

print(f"Aggregation complete: {out_txt}")
