#!/usr/bin/env python3
"""Build the deterministic machine input for a Full-Matrix Profile Candidate Result.

D-026 FAIL-CLOSED BUILD:
Any eligibility condition that is not satisfied makes the builder exit != 0 and
no candidate-result-input.json is produced. Deriver values are recomputed from
raw Run2/3/4 + candidate-matrix-config.json and cross-checked against the
Evidence aggregation artifacts; release provenance comes from two GitHub
metadata snapshots (--release-json, --tag-ref-json); the Evidence Review
document is parsed (Date, classification, dispatch, tag, digest, boundary).

Usage:
  python scripts/build_candidate_result_input.py \\
      --evidence-dir <EVD> --matrix-config <CFG> \\
      --release-json <release-meta.json> --tag-ref-json <tag-ref.json> \\
      --dispatch-sha <40hex> \\
      --evidence-review-doc <EVIDENCE-REVIEW-....md> \\
      --evidence-review-classification FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS \\
      --review-date YYYY-MM-DD [--out OUT.json]
Exit 0 = built; 1 = FAIL-CLOSED blocker.
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
MEAS = ("run2", "run3", "run4")
PROFILE_KEYS = ("gpu_memory_utilization", "max_model_len", "max_cudagraph_capture_size",
                "mtp", "data_parallel_size", "tensor_parallel_size", "expert_parallel",
                "max_num_seqs", "max_num_batched_tokens", "async_scheduling",
                "multistream_overlap_shared_expert", "cudagraph_mode", "prefix_cache")
IDENTITY_KEYS = ("container", "image", "vllm", "vllm_ascend_plugin", "model_path",
                 "pid_host", "port", "log")
ENV_KEYS = ("ASCEND_RT_VISIBLE_DEVICES", "HCCL_OP_EXPANSION_MODE", "OMP_PROC_BIND",
            "OMP_NUM_THREADS", "HCCL_BUFFSIZE", "PYTORCH_NPU_ALLOC_CONF",
            "VLLM_ASCEND_BALANCE_SCHEDULING", "VLLM_ASCEND_ENABLE_MLAPO")
EXPECTED_D024 = {"A3_cards": 8, "A3_tflops_per_card": 752, "A3_total_tflops": 6016,
                 "H100_cards": 16, "H100_tflops_per_card": 989, "H100_total_tflops": 15824,
                 "target_achievement_minimum": 0.80, "decision": "D-024"}


def die(msg):
    print("FAIL_CLOSED: %s" % msg, file=sys.stderr)
    sys.exit(1)


def read_json(p):
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def read_text(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def sha256_file(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_metrics(t):
    mean = statistics.fmean(t)
    sd = statistics.pstdev(t)
    cv = (sd / mean * 100.0) if mean else 0.0
    return {"mean": mean, "min": min(t), "max": max(t),
            "stddev": sd, "cv": cv}


def parse_identity(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^(\w[\w_]*)\s*=\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def parse_env(text):
    """Retain KEY=VALUE and unset names from a shell env block.
     - 'unset X' accumulates; 'export X=Y' or 'X=Y' set value.
    """
    env = {}
    unsets = []
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)(?:=(.*))?$", s)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        if val is None:
            env.pop(key, None)
            unsets.append(key)
            continue
        env[key] = val.strip().strip('"').strip("'")
    return env, unsets


def hard_require(cond, msg):
    """FAIL-CLOSED: any unmet eligibility condition aborts the build."""
    if not cond:
        die(msg)


def d024_check(hw):
    for k, want in (("A3_cards", 8), ("A3_tflops_per_card", 752),
                    ("A3_total_tflops", 6016), ("H100_cards", 16),
                    ("H100_tflops_per_card", 989), ("H100_total_tflops", 15824),
                    ("target_achievement_minimum", 0.80), ("decision", "D-024")):
        got = hw.get(k)
        if got != want:
            die("matrix-config hardware.%s = %r (expected %r)" % (k, got, want))


def parse_review_doc(path, dispatch, tag, asset_digest):
    """Machine parse of the Evidence Review markdown (fail-closed)."""
    t = read_text(path)
    m = re.search(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})", t)
    if not m:
        die("review doc missing **Date**")
    checks = {
        "classification PASS": "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS" in t,
        "FINAL_RECOMMENDED_PROFILE_CANDIDATE": "FINAL_RECOMMENDED_PROFILE_CANDIDATE" in t,
        "dispatch sha": dispatch in t,
        "release tag": tag in t,
        "asset digest": asset_digest in t,
        "no Formal Result boundary": "No Formal Result" in t,
        "Acceptance boundary": "no acceptance" in t.lower(),
    }
    for name, ok in checks.items():
        hard_require(ok, "review doc %s missing" % name)
    return {"doc_date": m.group(1)}


def build(ev_dir, cfg, rel_dict, tagref_dict, dispatch, doc_path, cli_class, cli_date):
    ev = Path(ev_dir)

    # 1) control-sha
    m = re.search(r"DISPATCH_CONTROL_SHA:\s*([0-9a-f]{40})",
                  read_text(ev / "control-sha.txt"))
    if not m or m.group(1) != dispatch:
        die("control-sha.txt != dispatch SHA")

    # 2) archive integrity
    if not (ev / "MANIFEST.txt").exists():
        die("MANIFEST.txt missing")
    sums_raw = read_text(ev / "SHA256SUMS.txt")
    hard_require(sums_raw.strip(), "SHA256SUMS.txt empty")
    sums = {}
    for line in sums_raw.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            sums[parts[1].strip()] = parts[0]
    bad = [r for r, h in sums.items() if sha256_file(ev / r) != h]
    hard_require(not bad, "SHA256SUMS mismatch on " + ", ".join(bad[:3]))

    # 3) script hashes recorded
    scripts = []
    for line in read_text(ev / "script-sha256sums.txt").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            scripts.append({"file": parts[1].strip(), "sha256": parts[0]})
    scripts.sort(key=lambda s: s["file"])

    # 4) matrix gates
    mx = read_json(ev / "matrix-validation.json")
    hard_require(mx.get("status") == "PASS", "matrix-validation.status != PASS")
    hard_require(mx.get("measured_runs_count") == 12, "measured != 12")
    hard_require(mx.get("warmup_runs_discarded_count") == 4, "warmup != 4")
    for k in ("profile_identical_across_cells", "runtime_identity_identical_across_cells"):
        hard_require(bool(mx.get(k)), "matrix %s not true" % k)

    # 5) D-024 config
    hw = cfg["hardware"]
    d024_check(hw)

    # 6) provenance (release + tag-ref, both required)
    rel = rel_dict
    tagref = tagref_dict
    tag_obj = tagref.get("object", {}).get("sha")
    hard_require(bool(tag_obj), "tag-ref JSON missing object.sha")
    hard_require(tag_obj == dispatch, "tag-ref object sha != dispatch")
    assets = {a["name"]: a for a in rel.get("assets", [])}
    asset = assets.get("fullmatrix-evidence.tar.gz")
    side = assets.get("fullmatrix-evidence.tar.gz.sha256")
    hard_require(asset and side, "release JSON missing assets")
    hard_require(rel.get("tag_name") == "glm52-od-profile-full-matrix-20260903",
                 "release tag != expected tag")
    release = {"release_id": rel.get("id"), "tag": rel.get("tag_name"),
               "release_name": rel.get("name"), "published_at": rel.get("published_at"),
               "tag_object_commit": tag_obj,
               "asset_id": asset["id"], "asset_name": asset["name"],
               "asset_size": asset["size"], "asset_digest": asset["digest"],
               "sidecar_id": side["id"], "sidecar_digest": side["digest"]}

    # 7) Evidence Review document parse
    doc = parse_review_doc(doc_path, dispatch, rel.get("tag_name"), asset["digest"])
    hard_require(cli_class == "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS",
                 "CLI classification != PASS token")
    hard_require(cli_date == doc["doc_date"],
                 "CLI review-date %s != review doc Date %s" % (cli_date, doc["doc_date"]))

    # 8) runtime identity fields + model_path + environment
    id_by = {}
    for cell in CELLS:
        id_by[cell] = parse_identity(read_text(ev / ("cell-" + cell) / "runtime-identity.txt"))
    fields = {}
    for k in IDENTITY_KEYS:
        vs = {id_by[c].get(k) for c in CELLS}
        hard_require(len(vs) == 1 and None not in vs, "identity field %r differs" % k)
        fields[k] = vs.pop()
    expected_env = cfg["frozen_profile"].get("environment", {})
    env_text = read_text(ev / "environment.txt")
    env_parsed, unsets = parse_env(env_text)
    for k in ENV_KEYS:
        hard_require(k in expected_env, "config missing expected env %s" % k)
        want = str(expected_env[k])
        got = env_parsed.get(k)
        hard_require(got == want, "env %s = %r expected %r" % (k, got, want))
    for u in expected_env.get("_unset", []):
        hard_require(u not in env_parsed, "expected unset %s present" % u)

    # model_path gate (identity vs config expected)
    hard_require(fields["model_path"] == cfg["frozen_profile"].get("model_path"),
                 "model_path mismatch identity=%r config=%r" % (
                     fields["model_path"], cfg["frozen_profile"].get("model_path")))

    # 9) cells: independent recompute of derived metrics
    cells = {}
    for cell in CELLS:
        cd = ev / ("cell-" + cell)
        val = read_json(cd / "validation.json")
        agg = read_json(cd / "aggregation.json")
        hard_require(val.get("status") == "PASS", "cell %s validation != PASS" % cell)
        hard_require(agg.get("status") == "PASS", "cell %s aggregation != PASS" % cell)
        run_metrics = {}
        for run in MEAS:
            met = read_json(cd / (run + ".metrics.json"))
            hard_require(met["successful_requests"] == 256 and met["failed_requests"] == 0,
                         "cell %s run %s counts != 256/0" % (cell, run))
            run_metrics[run] = met
        t = [run_metrics[r]["total_token_throughput"] for r in MEAS]
        calc = compute_metrics(t)
        b = float(cfg["cells"][cell]["baseline_tok_s"])
        h = float(cfg["cells"][cell]["h100_tok_s"])
        delta = (calc["mean"] / b - 1.0) * 100.0
        ach = (calc["mean"] / 6016.0) / (h / 15824.0) * 100.0
        t80 = h / 15824.0 * 6016.0 * 0.80
        metb = ach >= 80.0
        hard_require(metb, "cell %s achievement %.4f < 80" % (cell, ach))
        cross = [("mean", calc["mean"], agg.get("mean_tok_s")),
                 ("min", calc["min"], agg.get("min_tok_s")),
                 ("max", calc["max"], agg.get("max_tok_s")),
                 ("stddev", calc["stddev"], agg.get("stddev_pop_tok_s")),
                 ("cv", calc["cv"], agg.get("cv_pct")),
                 ("delta", delta, agg.get("delta_vs_baseline_pct")),
                 ("ach", ach, agg.get("d024_achievement_pct")),
                 ("t80", t80, agg.get("d024_target_80_tok_s")),
                 ("met", metb, agg.get("target_met"))]
        for key, mine, theirs in cross:
            if theirs is None or abs(float(theirs) - mine) > 1e-6:
                die("cell %s aggregation %s %.9f != recomputed %.9f" % (cell, key, theirs, mine))
        cells[cell] = {
            "cell_name": cfg["cells"][cell].get("cell_name", cell + "-1K"),
            "input_len": cfg["cells"][cell]["input_len"],
            "output_len": cfg["cells"][cell]["output_len"],
            "runs": {r: {"successful_requests": run_metrics[r]["successful_requests"],
                         "failed_requests": run_metrics[r]["failed_requests"],
                         "total_token_throughput": run_metrics[r]["total_token_throughput"],
                         "mean_ttft_ms": run_metrics[r]["mean_ttft_ms"],
                         "p99_ttft_ms": run_metrics[r]["p99_ttft_ms"],
                         "mean_tpot_ms": run_metrics[r]["mean_tpot_ms"],
                         "p99_tpot_ms": run_metrics[r]["p99_tpot_ms"],
                         "mean_itl_ms": run_metrics[r]["mean_itl_ms"],
                         "p99_itl_ms": run_metrics[r]["p99_itl_ms"],
                         "request_throughput": run_metrics[r]["request_throughput"],
                         "output_token_throughput": run_metrics[r]["output_token_throughput"]}
                     for r in MEAS},
            "total_token_throughput_tok_s": {"run2": t[0], "run3": t[1], "run4": t[2]},
            "mean_tok_s": calc["mean"], "min_tok_s": calc["min"], "max_tok_s": calc["max"],
            "stddev_pop_tok_s": calc["stddev"], "cv_pct": calc["cv"],
            "baseline_tok_s": b, "delta_vs_baseline_pct": delta,
            "h100_reference_tok_s": h, "d024_achievement_pct": ach,
            "d024_target_80_tok_s": t80, "target_met": metb,
            "validation_status": "PASS", "aggregation_status": "PASS",
            "recomputed_from_raw": True,
        }

    # 10) frozen profile identity vs snapshots
    snaps = [read_json(ev / ("cell-" + c) / "profile-snapshot.json") for c in CELLS]
    hard_require(len({json.dumps(s, sort_keys=True) for s in snaps}) == 1,
                 "profile-snapshot.json not identical across cells")
    for k in PROFILE_KEYS:
        hard_require(snaps[0].get(k) == cfg["frozen_profile"].get(k),
                     "profile %s %r != expected %r" % (k, snaps[0].get(k), cfg["frozen_profile"].get(k)))

    result = {
        "schema": "candidate-result-input", "version": 2,
        "result_type": "PROFILE_CANDIDATE_FULL_MATRIX",
        "model": cfg["model"], "task_id": cfg["task_id"],
        "dispatch_control_sha": dispatch,
        "evidence_review_document": doc_path,
        "evidence_review_classification": "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS",
        "review_date": doc["doc_date"],
        "release": release,
        "evidence_integrity": {"sha256sums_ok": True, "manifest_present": True,
                               "control_sha_match": True,
                               "pinned_tooling_hashes": scripts},
        "frozen_profile": {k: cfg["frozen_profile"][k] for k in PROFILE_KEYS},
        "runtime_identity": {"fields": fields,
                             "identical_across_cells": True},
        "runtime_environment": {k: env_parsed.get(k) for k in ENV_KEYS},
        "matrix": {"matrix_validation_status": "PASS",
                   "measured_runs_count": 12, "warmup_runs_discarded_count": 4,
                   "profile_identical_across_cells": True,
                   "profile_expected_values_match": True,
                   "runtime_identity_identical_across_cells": True},
        "cells": cells,
        "hardware": {k: hw[k] for k in ("A3_cards", "A3_tflops_per_card", "A3_total_tflops",
                                        "H100_cards", "H100_tflops_per_card",
                                        "H100_total_tflops", "target_achievement_minimum")},
        "opt01_status": "BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION",
        "candidate_classification": "FINAL_RECOMMENDED_PROFILE_CANDIDATE",
        "result_state": "READY_FOR_FORMAL_REVIEW",
        "formal_status_note": "NOT_YET_FORMALLY_ACCEPTED",
    }
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--matrix-config", required=True)
    ap.add_argument("--release-json", required=True,
                    help="GitHub release metadata JSON snapshot (authority)")
    ap.add_argument("--tag-ref-json", required=True,
                    help="GitHub tag-ref JSON snapshot (authority for tag_object_commit)")
    ap.add_argument("--dispatch-sha", required=True)
    ap.add_argument("--evidence-review-doc", required=True)
    ap.add_argument("--evidence-review-classification", required=True)
    ap.add_argument("--review-date", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    cfg = read_json(args.matrix_config)
    rel = read_json(args.release_json)
    tagref = read_json(args.tag_ref_json)
    result = build(args.evidence_dir, cfg, rel, tagref, args.dispatch_sha,
                   args.evidence_review_doc, args.evidence_review_classification,
                   args.review_date)
    out = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline="\n").write(out)
    print(out, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())