#!/usr/bin/env python3
"""Profile Candidate Full-Matrix validation (D-023 extension)."""

import argparse
import io
import json
import math
import os
import statistics
import sys

from extract_bench_metrics import parse_log

A3_TOTAL = 6016
H100_TOTAL = 15824
TARGET_MIN = 0.80

BASELINES = {
    "1K": {"baseline_raw": 676.60, "h100": 2688.71},
    "4K": {"baseline_raw": 820.76, "h100": 4063.45},
    "16K": {"baseline_raw": 957.94, "h100": 4379.60},
    "64K": {"baseline_raw": 927.59, "h100": 5054.66},
}

EXPECTED = {
    "1K": ("1024", "1024"),
    "4K": ("4096", "1024"),
    "16K": ("16384", "1024"),
    "64K": ("65536", "1024"),
}


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def has_contract(text, cell):
    p = EXPECTED[cell]
    pats = ["--random-input-len " + p[0],
            "--random-output-len " + p[1],
            "--max-concurrency 64",
            "--num-prompts 256",
            "--ignore-eos"]
    return all(x in text for x in pats)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cell-dir", required=True)
    parser.add_argument("--cell", required=True, choices=["1K", "4K", "16K", "64K"])
    parser.add_argument("--baselines-json", default=None)
    args = parser.parse_args()
    cell = args.cell
    base = read_json(args.baselines_json)[cell] if args.baselines_json else BASELINES[cell]

    problems = []
    totals = []

    for run in ("run2", "run3", "run4"):
        log_path = os.path.join(args.cell_dir, run + ".log")
        mj_path = os.path.join(args.cell_dir, run + ".metrics.json")
        if not os.path.exists(log_path):
            problems.append(run + ".log missing")
            continue
        text = io.open(log_path, encoding="utf-8", errors="replace").read()
        parsed = parse_log(log_path)
        if not has_contract(text, cell):
            problems.append("contract mismatch in " + run + ".log")
        if os.path.exists(mj_path):
            stored = read_json(mj_path)
            if stored != parsed:
                problems.append(run + ".metrics.json not deterministic")
        else:
            problems.append(run + ".metrics.json missing")
        if parsed["successful_requests"] != 256 or parsed["failed_requests"] != 0:
            problems.append(run + " counts wrong")
        tt = parsed["total_token_throughput"]
        if tt is None or math.isnan(tt) or tt <= 0:
            problems.append(run + " throughput missing")
        else:
            totals.append(tt)

    if len(totals) != 3:
        problems.append("need 3 measured runs")

    for p in problems:
        print("FAIL:", p)
    if problems:
        sys.exit(1)

    mean = statistics.mean(totals)
    sd = statistics.pstdev(totals)
    cv = (sd / mean * 100) if mean else 0.0
    delta = (mean / base["baseline_raw"] - 1) * 100
    ach = (mean / A3_TOTAL) / (base["h100"] / H100_TOTAL) * 100
    target80 = (base["h100"] / H100_TOTAL) * A3_TOTAL * TARGET_MIN

    print(json.dumps({
        "cell": cell,
        "runs": {"run2": totals[0], "run3": totals[1], "run4": totals[2]},
        "mean": mean,
        "min": min(totals),
        "max": max(totals),
        "stddev": sd,
        "cv_pct": cv,
        "delta_vs_baseline_pct": delta,
        "d024_achievement_pct": ach,
        "d024_target_80_tok_s": target80,
        "status": "PASS" if ach >= TARGET_MIN * 100 else "BELOW_TARGET",
    }, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()