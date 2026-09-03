#!/usr/bin/env python3
"""Per-cell Full-Matrix candidate validation (Profile Candidate Full-Matrix Validation).

Scope of THIS script (per-cell only):
  * raw run1..run4 logs exist and every required metric field parses
  * successful_requests == expected (256) and failed_requests == 0
  * workload contract verified from the CANONICAL artifact runN.command.txt
    (never trusted from the tee'd log, which may lack the CLI argv)
  * run1 is machine-identified WARMUP_DISCARD and excluded from aggregation
  * runN.metrics.json (stored) == deterministic re-extraction from runN.log
  * mean/min/max/stddev/CV computed from run2/run3/run4 only
  * delta / D-024 achievement / 80% target computed from Control
    candidate-matrix-config.json (no hardcoded values in this script)

Cross-cell frozen-profile consistency is NOT this script's scope:
scripts/validate_full_matrix_candidate.py (matrix level) does that.

Artifacts (--out-dir): <cell-dir>/validation.json + <cell-dir>/aggregation.json.
Both deterministic: no timestamps, sorted keys.

Exit: 0 = PASS, 1 = FAIL.
"""

import argparse
import io
import json
import statistics
import sys
from pathlib import Path

from bench_common import (
    contract_problems,
    load_matrix_config,
    parse_log,
    required_missing,
    sha256_file,
    write_json_deterministic,
)

MEASURED_RUNS = ("run2", "run3", "run4")
WARMUP_RUN = "run1"
ALL_RUNS = (WARMUP_RUN,) + MEASURED_RUNS


def _read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_command_tokens(cmd_path):
    """runN.command.txt holds the exact executed argv as a JSON list."""
    try:
        tokens = _read_json(cmd_path)
    except Exception:
        return None
    if not isinstance(tokens, list) or not all(isinstance(t, str) for t in tokens):
        return None
    return tokens


def validate_cell(cell_dir, cell, cfg, matrix_config_sha):
    """Return (validation, aggregation, problems)."""
    cell_dir = Path(cell_dir)
    problems = []
    runs_report = {}
    expected_success = int(cfg["workload_contract"]["num_prompts"])

    for run in ALL_RUNS:
        log_path = cell_dir / (run + ".log")
        cmd_path = cell_dir / (run + ".command.txt")
        metrics_path = cell_dir / (run + ".metrics.json")
        role = "WARMUP_DISCARD" if run == WARMUP_RUN else "MEASURED"
        entry = {"role": role, "in_mean": run in MEASURED_RUNS}
        run_problems = []

        if not log_path.exists():
            run_problems.append(run + ".log missing")
        if not cmd_path.exists():
            run_problems.append(run + ".command.txt missing")

        parsed = parse_log(log_path) if log_path.exists() else {}
        entry["metrics"] = parsed
        entry["log_sha256"] = sha256_file(log_path) if log_path.exists() else None

        if log_path.exists():
            missing = required_missing(parsed)
            if missing:
                run_problems.append("required fields missing: " + ",".join(missing))
            if parsed.get("successful_requests") != expected_success:
                run_problems.append(
                    "successful_requests=%r != %s" % (parsed.get("successful_requests"), expected_success)
                )
            if parsed.get("failed_requests") != 0:
                run_problems.append("failed_requests=%r != 0" % parsed.get("failed_requests"))

        if cmd_path.exists():
            tokens = _load_command_tokens(cmd_path)
            if tokens is None:
                run_problems.append(run + ".command.txt is not a JSON argv list")
            else:
                cp = contract_problems(tokens, cell, cfg)
                if cp:
                    run_problems.append("contract: " + "; ".join(cp))

        if metrics_path.exists():
            stored = _read_json(metrics_path)
            if stored != parsed:
                run_problems.append(run + ".metrics.json != deterministic re-extraction")
        else:
            run_problems.append(run + ".metrics.json missing (run extractor with --strict)")

        entry["status"] = "PASS" if not run_problems else "FAIL"
        if run_problems:
            entry["problems"] = run_problems
            problems.append("%s [%s]: %s" % (run, role, "; ".join(run_problems)))
        runs_report[run] = entry

    totals = []
    for run in MEASURED_RUNS:
        v = runs_report[run]["metrics"].get("total_token_throughput")
        if v is not None and v > 0:
            totals.append(v)
    if len(totals) != 3:
        problems.append("need 3 measured runs with valid total_token_throughput (got %d)" % len(totals))
    if runs_report[WARMUP_RUN]["role"] != "WARMUP_DISCARD":
        problems.append("run1 role must be WARMUP_DISCARD")

    validation = {
        "tool": "validate_matrix_candidate.py",
        "scope": "per-cell",
        "cell": cell,
        "cell_dir": str(cell_dir),
        "matrix_config_sha256": matrix_config_sha,
        "expected_successful_requests": expected_success,
        "runs": runs_report,
        "formal_value_definition": "Mean(run2, run3, run4) total_token_throughput (tok/s)",
        "status": "PASS" if not problems else "FAIL",
    }
    if problems:
        validation["problems"] = problems

    aggregation = None
    if not problems:
        mean = statistics.fmean(totals)
        sd = statistics.pstdev(totals)
        cv = (sd / mean * 100.0) if mean else 0.0
        baseline = float(cfg["cells"][cell]["baseline_tok_s"])
        h100_ref = float(cfg["cells"][cell]["h100_tok_s"])
        A3 = float(cfg["hardware"]["A3_total_tflops"])
        H100 = float(cfg["hardware"]["H100_total_tflops"])
        target_min = float(cfg["hardware"]["target_achievement_minimum"])
        delta = (mean / baseline - 1.0) * 100.0
        ach = (mean / A3) / (h100_ref / H100) * 100.0
        target80 = (h100_ref / H100) * A3 * target_min
        aggregation = {
            "cell": cell,
            "formal_value_tok_s": mean,
            "run2_tok_s": totals[0],
            "run3_tok_s": totals[1],
            "run4_tok_s": totals[2],
            "mean_tok_s": mean,
            "min_tok_s": min(totals),
            "max_tok_s": max(totals),
            "stddev_pop_tok_s": sd,
            "cv_pct": cv,
            "baseline_tok_s": baseline,
            "delta_vs_baseline_pct": delta,
            "d024_achievement_pct": ach,
            "d024_target_80_tok_s": target80,
            "target_met": ach >= target_min * 100.0,
            "run1_excluded": True,
            "status": "PASS",
        }

    return validation, aggregation, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cell-dir", required=True, help="cell evidence dir (cell-1K, ...)")
    parser.add_argument("--cell", required=True, choices=["1K", "4K", "16K", "64K"])
    parser.add_argument("--matrix-config", required=True, help="candidate-matrix-config.json path")
    parser.add_argument("--out-dir", default=None, help="write validation.json + aggregation.json here")
    args = parser.parse_args(argv)

    cfg = load_matrix_config(args.matrix_config)
    config_sha = sha256_file(args.matrix_config)
    validation, aggregation, problems = validate_cell(args.cell_dir, args.cell, cfg, config_sha)

    report = {"validation": validation, "aggregation": aggregation}
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.out_dir:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        write_json_deterministic(out_dir / "validation.json", validation)
        write_json_deterministic(out_dir / "aggregation.json", aggregation)
    if problems:
        for p in problems:
            print("FAIL:", p, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())