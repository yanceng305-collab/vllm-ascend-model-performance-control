#!/usr/bin/env python3
"""FAIL-CLOSED validator for the Full-Matrix Profile Candidate Result.

The Result markdown is RE-parsed and each factual field is compared with the
authority candidate-result-input.json; every derived number is recomputed.
An optional --release-json makes GitHub metadata the extra digest authority.

Exit: 0 PASS, 1 FAIL.
"""
import argparse
import io
import json
import re
import statistics
import sys

from candidate_json import load_json

CELLS = ("1K", "4K", "16K", "64K")
EXPECTED_UNSETS = sorted(("VLLM_VERSION", "LD_PRELOAD",
                          "VLLM_ASCEND_ENABLE_FLASHCOMM1",
                          "VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE",
                          "ASCEND_LAUNCH_BLOCKING"))


def read_json(p):
    return load_json(p)


def kv(content, label):
    """Value of '| label | `value` |'."""
    m = re.search(r"^\| %s \| `([^`]*)` \| *$" % re.escape(label), content, re.M)
    return m.group(1).strip() if m else None


def kvp(content, label):
    """Value of '| label | plain |'."""
    m = re.search(r"^\| %s \| ([^|`]+?) \| *$" % re.escape(label), content, re.M)
    return m.group(1).strip() if m else None


def fmt(v):
    if isinstance(v, bool):
        return str(v)
    return str(v)


def input_eligibility_failures(inp):
    """Fail any hand-made bad candidate-result-input.json on its own."""
    pf = []
    if inp.get("schema") != "candidate-result-input":
        pf.append("input: schema != candidate-result-input")
    if inp.get("version") != 2:
        pf.append("input: version != 2")
    if inp.get("evidence_review_classification") != "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS":
        pf.append("input: evidence_review_classification != PASS")
    if inp.get("result_type") != "PROFILE_CANDIDATE_FULL_MATRIX":
        pf.append("input: result_type != PROFILE_CANDIDATE_FULL_MATRIX")
    if inp.get("result_state") != "READY_FOR_FORMAL_REVIEW":
        pf.append("input: result_state != READY_FOR_FORMAL_REVIEW")
    if inp.get("formal_status_note") != "NOT_YET_FORMALLY_ACCEPTED":
        pf.append("input: formal_status_note mismatch")
    if inp.get("candidate_classification") != "FINAL_RECOMMENDED_PROFILE_CANDIDATE":
        pf.append("input: candidate_classification != FINAL_RECOMMENDED_PROFILE_CANDIDATE")
    if inp.get("opt01_status") != "BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION":
        pf.append("input: opt01_status mismatch")
    ei2 = inp.get("evidence_integrity", {})
    for k in ("sha256sums_ok", "manifest_present", "control_sha_match"):
        if ei2.get(k) is not True:
            pf.append("input: evidence_integrity.%s != true" % k)
    mx = inp.get("matrix", {})
    if mx.get("matrix_validation_status") != "PASS":
        pf.append("input: matrix_validation_status != PASS")
    if mx.get("measured_runs_count") != 12:
        pf.append("input: measured_runs_count != 12")
    if mx.get("warmup_runs_discarded_count") != 4:
        pf.append("input: warmup_runs_discarded_count != 4")
    for k in ("profile_identical_across_cells", "profile_expected_values_match",
              "runtime_identity_identical_across_cells"):
        if mx.get(k) is not True:
            pf.append("input: matrix.%s != true" % k)
    for cell in CELLS:
        c = inp.get("cells", {}).get(cell)
        if not c:
            pf.append("input: cell %s missing" % cell)
            continue
        if c.get("validation_status") != "PASS" or c.get("aggregation_status") != "PASS":
            pf.append("input: cell %s status != PASS" % cell)
        if c.get("target_met") is not True:
            pf.append("input: cell %s target_met != true" % cell)
        if float(c.get("d024_achievement_pct", 0)) < 80.0:
            pf.append("input: cell %s achievement < 80" % cell)
    return pf


def recompute_from_input(inp):
    """Independent recompute of every derived cell value from raw runs + config."""
    probs = []
    hw = inp.get("hardware", {})
    expected = {"A3_cards": 8, "A3_tflops_per_card": 752, "A3_total_tflops": 6016,
                "H100_cards": 16, "H100_tflops_per_card": 989, "H100_total_tflops": 15824,
                "target_achievement_minimum": 0.80, "decision": "D-024"}
    for key, want in expected.items():
        if hw.get(key) != want:
            probs.append("input D-024 %s != %r" % (key, want))
    unset = inp.get("runtime_environment", {}).get("_unset")
    if unset != EXPECTED_UNSETS:
        probs.append("input runtime_environment._unset != exact expected set")
    for cell in CELLS:
        c = inp.get("cells", {}).get(cell)
        if not c:
            continue
        t = [c["runs"][r]["total_token_throughput"] for r in ("run2", "run3", "run4")]
        mean = statistics.fmean(t)
        sd = statistics.pstdev(t)
        cv = (sd / mean * 100.0) if mean else 0.0
        b = float(c["baseline_tok_s"])
        h = float(c["h100_reference_tok_s"])
        delta = (mean / b - 1.0) * 100.0
        ach = (mean / 6016.0) / (h / 15824.0) * 100.0
        t80 = h / 15824.0 * 6016.0 * 0.80
        met = ach >= 80.0
        for key, stored, mine in (("mean", c["mean_tok_s"], mean),
                                  ("min", c["min_tok_s"], min(t)),
                                  ("max", c["max_tok_s"], max(t)),
                                  ("std", c["stddev_pop_tok_s"], sd),
                                  ("cv", c["cv_pct"], cv),
                                  ("delta", c["delta_vs_baseline_pct"], delta),
                                  ("ach", c["d024_achievement_pct"], ach),
                                  ("t80", c["d024_target_80_tok_s"], t80)):
            if abs(float(stored) - mine) > 1e-6:
                probs.append("input recompute %s %s %.9f != %.9f" % (cell, key, float(stored), mine))
        if met != c.get("target_met"):
            probs.append("input recompute %s target_met mismatch" % cell)
    return probs


def fresh_provenance_failures(inp, rel, tagref):
    """Formal mode: fresh GitHub snapshots must equal the input provenance."""
    pf = []
    r = inp.get("release", {})
    if tagref.get("ref") != "refs/tags/" + str(r.get("tag")):
        pf.append("fresh tag-ref name mismatch")
    tag_obj = ""
    obj = tagref.get("object") or {}
    tag_obj = obj.get("sha", "")
    if tag_obj != r.get("tag_object_commit"):
        pf.append("tag-ref object sha != input tag_object_commit")
    if tag_obj != inp.get("dispatch_control_sha"):
        pf.append("tag-ref object sha != dispatch_control_sha")
    if obj.get("type") != "commit":
        pf.append("tag-ref object type != commit")
    if rel.get("id") != r.get("release_id"):
        pf.append("fresh release id mismatch")
    for key, input_key in (("tag_name", "tag"), ("name", "release_name"), ("published_at", "published_at")):
        if rel.get(key) != r.get(input_key):
            pf.append("fresh release %s mismatch" % key)
    assets = {a["name"]: a for a in rel.get("assets", [])}
    asset = assets.get("fullmatrix-evidence.tar.gz")
    if not asset:
        pf.append("fresh release missing asset")
    else:
        for k in ("id", "name", "size", "digest"):
            if asset.get(k) != r.get("asset_%s" % k):
                pf.append("fresh asset %s mismatch" % k)
    side = assets.get("fullmatrix-evidence.tar.gz.sha256")
    if not side:
        pf.append("fresh release missing sidecar")
    else:
        for k in ("id", "name", "size", "digest"):
            if side.get(k) != r.get("sidecar_%s" % k):
                pf.append("fresh sidecar %s mismatch" % k)
    return pf


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--result", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--release-json", default=None,
                    help="fresh GitHub release metadata JSON (digest authority)")
    ap.add_argument("--tag-ref-json", default=None,
                    help="fresh GitHub tag-ref JSON (tag object authority)")
    ap.add_argument("--formal", action="store_true",
                    help="pre-commit formal mode: both fresh snapshots REQUIRED")
    args = ap.parse_args(argv)

    try:
        inp = read_json(args.input)
        content = io.open(args.result, encoding="utf-8").read()
        problems = input_eligibility_failures(inp)
        problems += recompute_from_input(inp)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print("FORMAL_CANDIDATE_RESULT_VALIDATION_FAILED")
        print(" - machine validation blocker: %s" % exc)
        return 1
    if args.formal and (not args.release_json or not args.tag_ref_json):
        problems.append("--formal requires --release-json and --tag-ref-json")
    elif args.formal:
        try:
            problems += fresh_provenance_failures(inp, read_json(args.release_json),
                                                  read_json(args.tag_ref_json))
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            problems.append("fresh provenance blocker: %s" % exc)

    # .1 type / identity
    if kv(content, "Result Type") != "PROFILE_CANDIDATE_FULL_MATRIX":
        problems.append("Result Type mismatch")
    rid = kv(content, "Result ID") or ""
    if "PROFILE" not in rid.upper():
        problems.append("Result ID missing PROFILE: %r" % rid)
    if "BASELINE" in rid.upper():
        problems.append("Result ID must not be BASELINE: %r" % rid)
    expected_id = "RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-%s" % inp["review_date"].replace("-", "")
    if rid != expected_id:
        problems.append("Result ID exact mismatch: %r != %r" % (rid, expected_id))
    if kv(content, "Result State") != "READY_FOR_FORMAL_REVIEW":
        problems.append("Result State not READY_FOR_FORMAL_REVIEW")
    if kv(content, "Formal note") != "NOT_YET_FORMALLY_ACCEPTED":
        problems.append("Formal note not NOT_YET_FORMALLY_ACCEPTED")
    if kv(content, "Model") != inp["model"]:
        problems.append("model mismatch")
    if kv(content, "Task") != inp["task_id"]:
        problems.append("task mismatch")
    if kv(content, "Dispatch Control SHA") != inp["dispatch_control_sha"]:
        problems.append("dispatch SHA mismatch")
    m_er = re.search(r"^\| Evidence Review \| `([^`]+)` / `([^`]+)` \| *$", content, re.M)
    if not m_er or m_er.group(1) != inp["evidence_review_classification"] or \
       m_er.group(2) != inp["evidence_review_document"]:
        problems.append("Evidence Review reference mismatch")
    if kvp(content, "Review date") != inp["review_date"]:
        problems.append("Review date mismatch")
    if kv(content, "Candidate classification") != inp["candidate_classification"]:
        problems.append("Candidate classification mismatch")
    if "FINAL_RECOMMENDED_PROFILE_CANDIDATE" not in content:
        problems.append("candidate classification statement missing")
    if kv(content, "Formal OPT-01") != inp["opt01_status"]:
        problems.append("Formal OPT-01 exact field mismatch")
    if "NOT YET FORMALLY ACCEPTED" not in content:
        problems.append("NOT_YET_FORMALLY_ACCEPTED missing")

    # . provenance
    r = inp["release"]
    for key, want in [("release id", r["release_id"]), ("asset id", r["asset_id"]),
                      ("sidecar id", r["sidecar_id"])]:
        got = kvp(content, key)
        if got != str(want):
            problems.append("provenance %s: %r != %r" % (key, got, str(want)))
    for key, want in [("asset digest", r["asset_digest"]),
                      ("sidecar digest", r["sidecar_digest"]), ("tag", r["tag"])]:
        got = kv(content, key)
        if got != str(want):
            problems.append("provenance %s: %r != %r" % (key, got, str(want)))
    if kv(content, "tag object commit") != str(r["tag_object_commit"]):
        problems.append("tag object commit mismatch")
    m_a = re.search(r"^\| asset \| `([^`]+)` \(([0-9]+) bytes\) \| *$", content, re.M)
    if not m_a or m_a.group(1) != r["asset_name"] or int(m_a.group(2)) != r["asset_size"]:
        problems.append("asset line mismatch")
    if kvp(content, "published") != r["published_at"]:
        problems.append("published mismatch")
    m_side = re.search(r"^\| sidecar \| `([^`]+)` \(([0-9]+) bytes\) \| *$", content, re.M)
    if not m_side or m_side.group(1) != r["sidecar_name"] or int(m_side.group(2)) != r["sidecar_size"]:
        problems.append("sidecar line mismatch")
    if args.release_json:
        auth = read_json(args.release_json)
        a = next((x for x in auth.get("assets", []) if x["name"] == "fullmatrix-evidence.tar.gz"), None)
        if not a or a["digest"] != r["asset_digest"]:
            problems.append("asset digest != authoritative release JSON")

    # . integrity block
    ei = inp["evidence_integrity"]
    for key, flag in (("archive SHA256SUMS", ei["sha256sums_ok"]),
                      ("MANIFEST present", ei["manifest_present"]),
                      ("control-sha match", ei["control_sha_match"])):
        if kvp(content, key) != fmt(flag):
            problems.append("integrity %s mismatch" % key)
    pinned = kvp(content, "pinned tooling")
    expected_pinned = "%s files recorded" % len(ei["pinned_tooling_hashes"])
    if pinned != expected_pinned:
        problems.append("pinned tooling count mismatch")

    # . frozen profile
    for k, v in sorted(inp["frozen_profile"].items()):
        if kv(content, k) != str(v):
            problems.append("frozen profile %s mismatch" % k)

    # . matrix gate
    mx = inp["matrix"]
    pairs = [("matrix validation", str(mx["matrix_validation_status"])),
             ("measured runs", str(mx["measured_runs_count"])),
             ("warmup discarded", str(mx["warmup_runs_discarded_count"])),
             ("profile identical", str(mx["profile_identical_across_cells"])),
             ("profile == Task expected", str(mx["profile_expected_values_match"])),
             ("runtime identity identical", str(mx["runtime_identity_identical_across_cells"]))]
    for label, want in pairs:
        got = kv(content, label) if label == "matrix validation" else kvp(content, label)
        if got != want:
            problems.append("matrix gate %s: %r != %r" % (label, got, want))
    if mx["measured_runs_count"] != 12:
        problems.append("measured != 12")
    if mx["warmup_runs_discarded_count"] != 4:
        problems.append("warmup != 4")

    # . per cell rows: r2 r3 r4 mean min max std cv delta ach t80 met
    row_re = re.compile(
        r"^\| (1K|4K|16K|64K) \| ([0-9]+\.[0-9]{2}) \| ([0-9]+\.[0-9]{2}) \| ([0-9]+\.[0-9]{2}) \| "
        r"([0-9]+\.[0-9]{4}) \| ([0-9]+\.[0-9]{2}) \| ([0-9]+\.[0-9]{2}) \| "
        r"([0-9]+\.[0-9]{6}) \| ([0-9]+\.[0-9]{4}) \| (-?[0-9]+\.[0-9]{4}) \| "
        r"([0-9]+\.[0-9]{3,4}) \| ([0-9]+\.[0-9]{4}) \| (True|False) \|$"
    )
    found = {}
    for line in content.splitlines():
        m = row_re.match(line)
        if m:
            found[m.group(1)] = m.groups()[1:]
    for cell in CELLS:
        if cell not in found:
            problems.append("cell row missing: %s" % cell)
            continue
        g = found[cell]
        c = inp["cells"][cell]
        r2, r3, r4 = map(float, g[0:3])
        mean, mnv, mxv, sd, cv, delta, ach, t80 = map(float, g[3:11])
        met = g[11] == "True"
        tol4 = 5e-5  # printed with %.4f
        tol6 = 5e-7  # printed with %.6f
        if abs((r2 + r3 + r4) / 3.0 - mean) > tol4:
            problems.append("cell %s mean not recomputed equal (%.6f vs %.6f)" % (cell, mean, (r2+r3+r4)/3))
        if met != c["target_met"]:
            problems.append("cell %s met mismatch" % cell)
        if c["total_token_throughput_tok_s"]["run2"] != r2 or \
           c["total_token_throughput_tok_s"]["run3"] != r3 or \
           c["total_token_throughput_tok_s"]["run4"] != r4:
            problems.append("cell %s run values != input" % cell)
        for key, got, want, tol in (("mean", mean, c["mean_tok_s"], tol4),
                               ("min", mnv, c["min_tok_s"], tol4),
                               ("max", mxv, c["max_tok_s"], tol4),
                               ("std", sd, c["stddev_pop_tok_s"], tol6),
                               ("cv", cv, c["cv_pct"], tol4),
                               ("delta", delta, c["delta_vs_baseline_pct"], tol4),
                               ("ach", ach, c["d024_achievement_pct"], tol4),
                               ("t80", t80, c["d024_target_80_tok_s"], tol4)):
            if abs(float(got) - float(want)) > tol:
                problems.append("cell %s %s mismatch" % (cell, key))
        if ach < 80.0:
            problems.append("cell %s achievement < 80%%" % cell)

    # . counts lines
    cnt_re = re.compile(r"- (%s): run2 (\d+)/(\d+), run3 (\d+)/(\d+), run4 (\d+)/(\d+) .*" % "|".join(CELLS))
    counts = {}
    for line in content.splitlines():
        m = cnt_re.match(line)
        if m:
            counts[m.group(1)] = m.groups()[1:]
    for cell in CELLS:
        c = inp["cells"][cell]
        want = tuple((str(c["runs"][r]["successful_requests"]), str(c["runs"][r]["failed_requests"])) for r in ("run2","run3","run4"))
        want_flat = [v for t in want for v in t]
        if counts.get(cell) != tuple(want_flat):
            problems.append("cell %s counts mismatch" % cell)

    # . latencies (run2)
    lat = {}
    lat_re = re.compile(r"^\| (%s) \| ([0-9]+\.[0-9]{2}) / ([0-9]+\.[0-9]{2}) \| "
                        r"([0-9]+\.[0-9]{2}) / ([0-9]+\.[0-9]{2}) \| "
                        r"([0-9]+\.[0-9]{2}) / ([0-9]+\.[0-9]{2}) \| "
                        r"([0-9]+\.[0-9]{2,4}) \| ([0-9]+\.[0-9]{2}) \|$" % "|".join(CELLS))
    for line in content.splitlines():
        m = lat_re.match(line)
        if m:
            lat[m.group(1)] = m.groups()[1:]
    for cell in CELLS:
        m = inp["cells"][cell]["runs"]["run2"]
        if cell not in lat:
            problems.append("latency row missing %s" % cell)
        else:
            g = lat[cell]
            want = ["%.2f" % m["mean_ttft_ms"], "%.2f" % m["p99_ttft_ms"],
                    "%.2f" % m["mean_tpot_ms"], "%.2f" % m["p99_tpot_ms"],
                    "%.2f" % m["mean_itl_ms"], "%.2f" % m["p99_itl_ms"],
                    "%.4f" % m["request_throughput"], "%.2f" % m["output_token_throughput"]]
            got = [g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7]]
            if got != want:
                problems.append("cell %s latency mismatch" % cell)

    # Runtime identity and environment are factual Result fields.
    identity = inp["runtime_identity"]["fields"]
    for key, want in sorted(identity.items()):
        if kv(content, key) != str(want):
            problems.append("runtime identity %s mismatch" % key)
    if kvp(content, "identical across cells") != str(inp["runtime_identity"]["identical_across_cells"]):
        problems.append("runtime identity identical across cells mismatch")
    for key, want in sorted(inp.get("runtime_environment", {}).items()):
        expected_value = ",".join(want) if key == "_unset" else str(want)
        if kv(content, key) != expected_value:
            problems.append("runtime environment %s mismatch" % key)

    # D-024 block
    hw = inp["hardware"]
    m3 = re.match(r"(\d+) x (\d+) = (\d+)", kvp(content, "A3") or "")
    if not m3 or [int(x) for x in m3.groups()] != [hw["A3_cards"], hw["A3_tflops_per_card"], hw["A3_total_tflops"]]:
        problems.append("A3 D-024 block mismatches")
    m4 = re.match(r"(\d+) x (\d+) = (\d+)", kvp(content, "H100") or "")
    if not m4 or [int(x) for x in m4.groups()] != [hw["H100_cards"], hw["H100_tflops_per_card"], hw["H100_total_tflops"]]:
        problems.append("H100 D-024 block mismatches")
    if kvp(content, "target min") != str(hw["target_achievement_minimum"]):
        problems.append("D-024 target minimum mismatch")
    if kv(content, "decision") != hw["decision"]:
        problems.append("D-024 decision mismatch")

    if problems:
        print("FORMAL_CANDIDATE_RESULT_VALIDATION_FAILED")
        for p in problems:
            print(" -", p)
        return 1
    print("FORMAL_CANDIDATE_RESULT_VALIDATION_PASS")
    return 0


def main(argv=None):
    try:
        return _main(argv)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print("FORMAL_CANDIDATE_RESULT_VALIDATION_FAILED")
        print(" - machine validation blocker: %s" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
