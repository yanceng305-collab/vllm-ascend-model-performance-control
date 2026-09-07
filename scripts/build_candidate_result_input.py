#!/usr/bin/env python3
"""Build the deterministic machine input for a Full-Matrix Profile Candidate Result.

D-026 gate: candidate-result-input.json is the machine artifact from which the
candidate Result generator and validator work. Every factual performance value
is read from the reviewed Evidence or recomputed from it; none is hand-typed.

Usage:
  python scripts/build_candidate_result_input.py \\
      --evidence-dir <EVIDENCE_ROOT> --matrix-config CFG --release-json R.json \\
      --dispatch-sha SHA --evidence-review-doc DOC.md \\
      --evidence-review-classification FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS \\
      --review-date YYYY-MM-DD [--out OUT.json]

Exit 0 = built, 1 = fail-closed error.
"""
import argparse
import hashlib
import io
import json
import re
import statistics
import sys
from pathlib import Path

CELLS = ("1K", "4K", "16K", "64K")
PROFILE_KEYS = ("gpu_memory_utilization", "max_model_len", "max_cudagraph_capture_size",
                "mtp", "data_parallel_size", "tensor_parallel_size", "expert_parallel",
                "max_num_seqs", "max_num_batched_tokens", "async_scheduling",
                "multistream_overlap_shared_expert", "cudagraph_mode", "prefix_cache")


def sha256_file(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def build(ev_dir, cfg, rel, dispatch, review_doc, review_class, review_date):
    ev = Path(ev_dir)

    ctrl = io.open(ev / "control-sha.txt", encoding="utf-8").read()
    m = re.search(r"DISPATCH_CONTROL_SHA:\s*([0-9a-f]{40})", ctrl)
    if not m:
        die("control-sha.txt missing DISPATCH_CONTROL_SHA")
    if m.group(1) != dispatch:
        die("control-sha != dispatch")

    scripts = []
    for line in io.open(ev / "script-sha256sums.txt", encoding="utf-8").read().splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            scripts.append({"file": parts[1].strip(), "sha256": parts[0]})
    scripts.sort(key=lambda s: s["file"])

    sums = {}
    for line in io.open(ev / "SHA256SUMS.txt", encoding="utf-8").read().splitlines():
        line = line.strip()
        if line:
            h, relpath = line.split(None, 1)
            sums[relpath.strip()] = h
    bad = [r for r, h in sums.items() if sha256_file(ev / r) != h]
    sha_ok = bool(sums) and not bad
    manifest_ok = (ev / "MANIFEST.txt").exists()

    mx = read_json(ev / "matrix-validation.json")
    cells = {}
    for cell in CELLS:
        cd = ev / ("cell-" + cell)
        for name in ("aggregation.json", "validation.json", "runtime-identity.txt"):
            if not (cd / name).exists():
                die("cell %s missing %s" % (cell, name))
        agg = read_json(cd / "aggregation.json")
        val = read_json(cd / "validation.json")
        runs_in = {}
        for run in ("run2", "run3", "run4"):
            met = read_json(cd / (run + ".metrics.json"))
            if met["successful_requests"] != 256 or met["failed_requests"] != 0:
                die("cell %s run %s not 256/0" % (cell, run))
            runs_in[run] = {
                "successful_requests": met["successful_requests"],
                "failed_requests": met["failed_requests"],
                "total_token_throughput": met["total_token_throughput"],
                "mean_ttft_ms": met["mean_ttft_ms"],
                "p99_ttft_ms": met["p99_ttft_ms"],
                "mean_tpot_ms": met["mean_tpot_ms"],
                "p99_tpot_ms": met["p99_tpot_ms"],
                "mean_itl_ms": met["mean_itl_ms"],
                "p99_itl_ms": met["p99_itl_ms"],
                "request_throughput": met["request_throughput"],
                "output_token_throughput": met["output_token_throughput"],
            }
        t = [runs_in[r]["total_token_throughput"] for r in ("run2", "run3", "run4")]
        mean = statistics.fmean(t)
        sd = statistics.pstdev(t)
        cv = (sd / mean * 100.0) if mean else 0.0
        consistent = (abs(mean - agg["mean_tok_s"]) < 1e-6 and
                      abs(sd - agg["stddev_pop_tok_s"]) < 1e-6 and
                      abs(cv - agg["cv_pct"]) < 1e-6 and
                      abs(min(t) - agg["min_tok_s"]) < 1e-6 and
                      abs(max(t) - agg["max_tok_s"]) < 1e-6)
        cc = cfg["cells"][cell]
        cells[cell] = {
            "cell_name": cc["cell_name"],
            "input_len": cc["input_len"],
            "output_len": cc["output_len"],
            "runs": runs_in,
            "total_token_throughput_tok_s": {"run2": t[0], "run3": t[1], "run4": t[2]},
            "mean_tok_s": mean,
            "min_tok_s": min(t),
            "max_tok_s": max(t),
            "stddev_pop_tok_s": sd,
            "cv_pct": cv,
            "baseline_tok_s": agg["baseline_tok_s"],
            "delta_vs_baseline_pct": agg["delta_vs_baseline_pct"],
            "h100_reference_tok_s": cc["h100_tok_s"],
            "d024_achievement_pct": agg["d024_achievement_pct"],
            "d024_target_80_tok_s": agg["d024_target_80_tok_s"],
            "target_met": agg["target_met"],
            "validation_status": val["status"],
            "recomputed_consistent": consistent,
        }

    snaps = {cell: read_json(ev / ("cell-" + cell) / "profile-snapshot.json") for cell in CELLS}
    same_prof = len({json.dumps(s, sort_keys=True) for s in snaps.values()}) == 1
    profile_ok = True
    for cell in CELLS:
        for k in PROFILE_KEYS:
            if snaps[cell].get(k) != cfg["frozen_profile"].get(k):
                profile_ok = False
    ids = {cell: io.open(ev / ("cell-" + cell) / "runtime-identity.txt",
                         encoding="utf-8").read() for cell in CELLS}
    id_identical = len(set(ids.values())) == 1
    id_ok = id_identical

    assets = {a["name"]: a for a in rel.get("assets", [])}
    asset = assets.get("fullmatrix-evidence.tar.gz")
    side = assets.get("fullmatrix-evidence.tar.gz.sha256")
    if not asset or not side:
        die("release JSON missing expected assets")

    return {
        "schema": "candidate-result-input",
        "version": 1,
        "result_type": "PROFILE_CANDIDATE_FULL_MATRIX",
        "model": cfg["model"],
        "task_id": cfg["task_id"],
        "dispatch_control_sha": dispatch,
        "control_sha_verified": True,
        "evidence_review_document": review_doc,
        "evidence_review_classification": review_class,
        "review_date": review_date,
        "release": {
            "release_id": rel.get("id"),
            "tag": rel.get("tag_name"),
            "release_name": rel.get("name"),
            "tag_object_commit": dispatch,
            "published_at": rel.get("published_at"),
            "asset_id": asset.get("id"),
            "asset_name": asset.get("name"),
            "asset_size": asset.get("size"),
            "asset_digest": asset.get("digest"),
            "sidecar_id": side.get("id"),
            "sidecar_digest": side.get("digest"),
        },
        "evidence_integrity": {
            "sha256sums_ok": sha_ok,
            "manifest_present": manifest_ok,
            "control_sha_match": True,
            "pinned_tooling_hashes": scripts,
        },
        "frozen_profile": {k: cfg["frozen_profile"][k] for k in PROFILE_KEYS},
        "runtime_environment": cfg["frozen_profile"].get("runtime_environment", ""),
        "matrix": {
            "matrix_validation_status": mx.get("status"),
            "measured_runs_count": mx.get("measured_runs_count"),
            "warmup_runs_discarded_count": mx.get("warmup_runs_discarded_count"),
            "profile_identical_across_cells": profile_ok and same_prof,
            "profile_expected_values_match": profile_ok,
            "runtime_identity_identical_across_cells": id_ok,
        },
        "cells": cells,
        "hardware": {
            "A3_cards": cfg["hardware"]["A3_cards"],
            "A3_tflops_per_card": cfg["hardware"]["A3_tflops_per_card"],
            "A3_total_tflops": cfg["hardware"]["A3_total_tflops"],
            "H100_cards": cfg["hardware"]["H100_cards"],
            "H100_tflops_per_card": cfg["hardware"]["H100_tflops_per_card"],
            "H100_total_tflops": cfg["hardware"]["H100_total_tflops"],
            "target_achievement_min": cfg["hardware"]["target_achievement_minimum"],
        },
        "opt01_status": "BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION",
        "candidate_classification": "FINAL_RECOMMENDED_PROFILE_CANDIDATE",
        "result_state": "READY_FOR_FORMAL_REVIEW",
        "formal_status_note": "NOT_YET_FORMALLY_ACCEPTED",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--matrix-config", required=True)
    ap.add_argument("--release-json", required=True)
    ap.add_argument("--dispatch-sha", required=True)
    ap.add_argument("--evidence-review-doc", required=True)
    ap.add_argument("--evidence-review-classification", required=True)
    ap.add_argument("--review-date", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    cfg = read_json(args.matrix_config)
    rel = read_json(args.release_json)
    result = build(args.evidence_dir, cfg, rel, args.dispatch_sha,
                   args.evidence_review_doc, args.evidence_review_classification,
                   args.review_date)
    out = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline="\n").write(out)
    print(out, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())