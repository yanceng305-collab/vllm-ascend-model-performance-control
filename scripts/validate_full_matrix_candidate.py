#!/usr/bin/env python3
"""Full-matrix candidate validation (matrix level).

SCOPE (matrix level only):
  * all four cells (1K/4K/16K/64K) present and their per-cell
    validation.json + aggregation.json both PASS (per-cell metrics scope is
    the per-cell validator's job, not re-verified here)
  * frozen-profile consistency ACROSS cells: profile-snapshot.json must be
    identical in all four cells (a single field changed => FAIL)
  * runtime identity identical across the four cells (same warm service)
  * run1 WARMUP_DISCARD count == 4 (never in any mean)
  * aggregation formal value == mean(run2, run3, run4) in each aggregation.json
  * D-024 basis exactly 6016 / 15824 from candidate-matrix-config.json;
    nothing is hardcoded in this script

Per-cell metrics validation: scripts/validate_matrix_candidate.py.
A Formal Result comparison is a LATER stage (Formal Candidate Result gate).
This script does NOT verify any Formal Result.

Output: matrix-validation.json (deterministic, no timestamps).
Exit: 0 = PASS, 1 = FAIL.
"""

import argparse
import io
import json
import sys
from pathlib import Path

from bench_common import load_matrix_config, write_json_deterministic

CELLS = ["1K", "4K", "16K", "64K"]


def _read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def _read_text(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _canonical(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--matrix-dir", required=True, help="evidence root with cell-1K ... cell-64K")
    parser.add_argument("--matrix-config", required=True, help="candidate-matrix-config.json path")
    parser.add_argument("--out", default=None, help="write matrix-validation.json here")
    args = parser.parse_args(argv)

    cfg = load_matrix_config(args.matrix_config)
    root = Path(args.matrix_dir)
    problems = []
    cells_report = {}
    profile_snapshots = {}
    identities = {}
    warmups = 0
    measured = 0

    for cell in CELLS:
        cell_dir = root / ("cell-" + cell)
        if not cell_dir.is_dir():
            problems.append("missing cell dir: %s" % cell)
            continue
        vpath = cell_dir / "validation.json"
        apath = cell_dir / "aggregation.json"
        ppath = cell_dir / "profile-snapshot.json"
        ipath = cell_dir / "runtime-identity.txt"
        if not (vpath.exists() and apath.exists()):
            problems.append("%s: validation.json/aggregation.json missing" % cell)
            continue
        v = _read_json(vpath)
        a = _read_json(apath)
        if v.get("status") != "PASS":
            problems.append("%s: per-cell validation FAIL" % cell)
        if a.get("status") != "PASS":
            problems.append("%s: aggregation status FAIL" % cell)
        runs = v.get("runs", {})
        for r in ("run2", "run3", "run4"):
            if r in runs:
                measured += 1
        if runs.get("run1", {}).get("role") == "WARMUP_DISCARD":
            warmups += 1
        else:
            problems.append("%s: run1 not WARMUP_DISCARD" % cell)
        if not (a.get("run2_tok_s") is not None and a.get("run3_tok_s") is not None
                and a.get("run4_tok_s") is not None):
            problems.append("%s: aggregation missing run2/3/4 values" % cell)
        else:
            m2 = (a["run2_tok_s"] + a["run3_tok_s"] + a["run4_tok_s"]) / 3.0
            if abs(a.get("formal_value_tok_s", -1.0) - m2) > 1e-9:
                problems.append("%s: formal value != mean(run2,3,4)" % cell)
        if not ppath.exists():
            problems.append("%s: profile-snapshot.json missing" % cell)
        else:
            profile_snapshots[cell] = _read_json(ppath)
        if not ipath.exists():
            problems.append("%s: runtime-identity.txt missing" % cell)
        else:
            identities[cell] = _read_text(ipath)

        cells_report[cell] = {
            "validation_status": v.get("status"),
            "aggregation_status": a.get("status"),
            "mean_tok_s": a.get("mean_tok_s"),
            "delta_vs_baseline_pct": a.get("delta_vs_baseline_pct"),
            "d024_achievement_pct": a.get("d024_achievement_pct"),
            "target_met": a.get("target_met"),
        }

    profile_identical = False
    if len(profile_snapshots) == 4:
        cans = {cell: _canonical(profile_snapshots[cell]) for cell in CELLS}
        profile_identical = len(set(cans.values())) == 1
        if not profile_identical:
            problems.append("profile snapshots differ across cells: " + ", ".join(
                "%s=%s..." % (cell, cans[cell][:24]) for cell in CELLS))
    else:
        problems.append("require profile-snapshot.json in all 4 cells")

    identity_identical = False
    if len(identities) == 4:
        identity_identical = len(set(identities.values())) == 1
        if not identity_identical:
            problems.append("runtime-identity.txt differs across cells")

    if warmups != 4:
        problems.append("warmup WARMUP_DISCARD count %d != 4" % warmups)
    if measured != 12:
        problems.append("measured runs count %d != 12" % measured)

    hw = cfg["hardware"]
    assert hw["A3_total_tflops"] == 6016 and hw["H100_total_tflops"] == 15824  # load_matrix_config guarantees

    matrix = {
        "tool": "validate_full_matrix_candidate.py",
        "scope": "matrix-level",
        "matrix_dir": str(root),
        "cells": cells_report,
        "profile_identical_across_cells": profile_identical,
        "runtime_identity_identical_across_cells": identity_identical,
        "warmup_runs_discarded_count": warmups,
        "measured_runs_count": measured,
        "d024_exact_basis": {"A3_total_tflops": hw["A3_total_tflops"],
                              "H100_total_tflops": hw["H100_total_tflops"]},
        "formal_result_boundary": "This gate validates Evidence only; Formal Result comparison is a later stage.",
        "status": "PASS" if not problems else "FAIL",
    }
    if problems:
        matrix["problems"] = problems

    print(json.dumps(matrix, indent=2, sort_keys=True))
    if args.out:
        write_json_deterministic(args.out, matrix)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())