#!/usr/bin/env python3
"""Deterministic vllm bench serve log -> metrics.json extractor.

D-023 extension for Profile Candidate Full-Matrix validation:
RAW SOURCE   : runN.log (bench stdout, immutable)
MACHINE DERIVED : runN.metrics.json

No timestamps are embedded, so the same input log ALWAYS yields the same
output JSON (deterministic regenerate). Usage:
  python scripts/extract_bench_metrics.py <runN.log> [--out <runN.metrics.json>]
"""

import io
import json
import os
import re
import sys
from pathlib import Path

FIELDS = [
    ("successful_requests", "Successful requests:", "int"),
    ("failed_requests", "Failed requests:", "int"),
    ("benchmark_duration_s", "Benchmark duration", "float"),
    ("total_input_tokens", "Total input tokens:", "int"),
    ("total_output_tokens", "Total generated tokens:", "int"),
    ("request_throughput", "Request throughput", "float"),
    ("output_token_throughput", "Output token throughput", "float"),
    ("total_token_throughput", "Total token throughput", "float"),
    ("mean_ttft_ms", "Mean TTFT", "float"),
    ("p99_ttft_ms", "P99 TTFT", "float"),
    ("mean_tpot_ms", "Mean TPOT", "float"),
    ("p99_tpot_ms", "P99 TPOT", "float"),
    ("mean_itl_ms", "Mean ITL", "float"),
    ("p99_itl_ms", "P99 ITL", "float"),
]


def extract_numbers(line):
    # last numeric token(s) are the value (may be formatted like 1,234.56)
    return re.findall(r"[0-9]+(?:\.[0-9]+)?", line)


def parse_log(path):
    text = io.open(path, encoding="utf-8", errors="replace").read()
    out = {"run_file": os.path.basename(path)}
    for key, label, kind in FIELDS:
        m = re.search(r"^.*" + re.escape(label) + r"[:\s]*([0-9][0-9.,]*)", text, re.M)
        if not m:
            out[key] = None
            continue
        raw = m.group(1)
        try:
            if kind == "int":
                out[key] = int(raw.replace(",", "").split(".")[0])
            else:
                out[key] = float(raw.replace(",", ""))
        except ValueError:
            out[key] = None
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    log = Path(sys.argv[1])
    out = None
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    metrics = parse_log(log)
    js = json.dumps(metrics, indent=2, sort_keys=True)
    if out:
        out.write_text(js + "\n", encoding="utf-8")
        print(js)
        print("WROTE %s" % out, file=sys.stderr)
    else:
        print(js)


if __name__ == "__main__":
    main()