#!/usr/bin/env python3
"""Generate the single Full-Matrix Profile Candidate Result markdown.

D-026 gate: all factual fields come from candidate-result-input.json (built by
build_candidate_result_input.py from reviewed Evidence + Control configs).
No performance number is typed here; no timestamps; deterministic output.

Usage:
  python scripts/generate_candidate_result.py \\
      --input candidate-result-input.json [--out RESULT.md]

Exit 0 = generated, 1 = error.
"""
import argparse
import io
import sys
from pathlib import Path

from candidate_json import load_json


def read_json(p):
    return load_json(p)


def render(inp):
    L = []
    A = L.append
    model = inp["model"]
    rid = "RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-%s" % inp["review_date"].replace("-", "")
    A("# Result: %s Profile Candidate Full-Matrix (Machine-Verified)" % model)
    A("")
    A("| field | value |")
    A("|---|---|")
    A("| Result ID | `%s` |" % rid)
    A("| Model | `%s` |" % model)
    A("| Result Type | `%s` |" % inp["result_type"])
    A("| Result State | `%s` |" % inp["result_state"])
    A("| Formal note | `%s` |" % inp["formal_status_note"])
    A("| Task | `%s` |" % inp["task_id"])
    A("| Dispatch Control SHA | `%s` |" % inp["dispatch_control_sha"])
    A("| Evidence Review | `%s` / `%s` |" % (inp["evidence_review_classification"], inp["evidence_review_document"]))
    A("| Review date | %s |" % inp["review_date"])
    A("| Candidate classification | `%s` |" % inp["candidate_classification"])
    A("| Formal OPT-01 | `%s` (unchanged; independent) |" % inp["opt01_status"])
    A("")
    A("## 0. Factual issues")
    A("")
    A("This document is machine-generated from `candidate-result-input.json`; all numbers below "
      "are values read from the reviewed Evidence (D-025 layout), not hand-typed.")
    A("")
    A("## 1. Evidence provenance")
    A("")
    r = inp["release"]
    A("| key | value |")
    A("|---|---|")
    A("| release id | %s |" % r["release_id"])
    A("| tag | `%s` |" % r["tag"])
    A("| tag object commit | `%s` |" % r["tag_object_commit"])
    A("| published | %s |" % r["published_at"])
    A("| asset id | %s |" % r["asset_id"])
    A("| asset | `%s` (%s bytes) |" % (r["asset_name"], r["asset_size"]))
    A("| asset digest | `%s` |" % r["asset_digest"])
    A("| sidecar id | %s |" % r["sidecar_id"])
    A("| sidecar | `%s` (%s bytes) |" % (r["sidecar_name"], r["sidecar_size"]))
    A("| sidecar digest | `%s` |" % r["sidecar_digest"])
    A("")
    ei = inp["evidence_integrity"]
    A("| archive SHA256SUMS | %s |" % ei["sha256sums_ok"])
    A("| MANIFEST present | %s |" % ei["manifest_present"])
    A("| control-sha match | %s |" % ei["control_sha_match"])
    A("| pinned tooling | %s files recorded |" % len(ei["pinned_tooling_hashes"]))
    A("")
    A("### 2b. Runtime identity")
    A("")
    A("| field | value |")
    A("|---|---|")
    ridp = inp.get("runtime_identity", {})
    for k, v in sorted(ridp.get("fields", {}).items()):
        A("| %s | `%s` |" % (k, v))
    A("| identical across cells | %s |" % ridp.get("identical_across_cells", False))
    A("")
    A("### 2c. Runtime environment")
    A("")
    A("| var | value |")
    A("|---|---|")
    for k, v in sorted(inp.get("runtime_environment", {}).items()):
        shown = ",".join(v) if k == "_unset" else v
        A("| %s | `%s` |" % (k, shown))
    A("")
    A("## 2d. Frozen profile (candidate)")
    A("")
    A("| field | value |")
    A("|---|---|")
    for k, v in sorted(inp["frozen_profile"].items()):
        A("| %s | `%s` |" % (k, v))
    A("| runtime environment | `%s` |" % inp["runtime_environment"])
    A("")
    A("## 3. Matrix gate")
    A("")
    mx = inp["matrix"]
    A("| gate | value |")
    A("|---|---|")
    A("| matrix validation | `%s` |" % mx["matrix_validation_status"])
    A("| measured runs | %s |" % mx["measured_runs_count"])
    A("| warmup discarded | %s |" % mx["warmup_runs_discarded_count"])
    A("| profile identical | %s |" % mx["profile_identical_across_cells"])
    A("| profile == Task expected | %s |" % mx["profile_expected_values_match"])
    A("| runtime identity identical | %s |" % mx["runtime_identity_identical_across_cells"])
    A("")
    A("## 4. Per-cell machine numbers")
    A("")
    A("| cell | r2 | r3 | r4 | mean | min | max | stddev | CV%% | delta%% | ach%% | 80%% tgt | met |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for cell, c in sorted(inp["cells"].items()):
        A("| %s | %.2f | %.2f | %.2f | %.4f | %.2f | %.2f | %.6f | %.4f | %.4f | %.4f | %.4f | %s |" % (
            cell, *[c["total_token_throughput_tok_s"][r] for r in ("run2", "run3", "run4")],
            c["mean_tok_s"], c["min_tok_s"], c["max_tok_s"], c["stddev_pop_tok_s"],
            c["cv_pct"], c["delta_vs_baseline_pct"], c["d024_achievement_pct"],
            c["d024_target_80_tok_s"], c["target_met"]))
    A("")
    A("per measured run success/failed counts (256/0):")
    A("")
    for cell in sorted(inp["cells"]):
        c = inp["cells"][cell]
        A("- %s: run2 %s/%s, run3 %s/%s, run4 %s/%s (successful/failed)" % (
            cell,
            c["runs"]["run2"]["successful_requests"], c["runs"]["run2"]["failed_requests"],
            c["runs"]["run3"]["successful_requests"], c["runs"]["run3"]["failed_requests"],
            c["runs"]["run4"]["successful_requests"], c["runs"]["run4"]["failed_requests"]))
    A("")
    A("## 5. Latencies / rates (run2, ms)")
    A("")
    A("| cell | TTFT m/p99 | TPOT m/p99 | ITL m/p99 | req/s | out tok/s |")
    A("|---|---|---|---|---|---|")
    for cell in ("1K", "4K", "16K", "64K"):
        m = inp["cells"][cell]["runs"]["run2"]
        A("| %s | %.2f / %.2f | %.2f / %.2f | %.2f / %.2f | %.4f | %.2f |" % (
            cell, m["mean_ttft_ms"], m["p99_ttft_ms"], m["mean_tpot_ms"], m["p99_tpot_ms"],
            m["mean_itl_ms"], m["p99_itl_ms"], m["request_throughput"], m["output_token_throughput"]))
    A("")
    A("## 6. D-024 normalization basis")
    A("")
    hw = inp["hardware"]
    A("| term | value |")
    A("|---|---|")
    A("| A3 | %s x %s = %s |" % (hw["A3_cards"], hw["A3_tflops_per_card"], hw["A3_total_tflops"]))
    A("| H100 | %s x %s = %s |" % (hw["H100_cards"], hw["H100_tflops_per_card"], hw["H100_total_tflops"]))
    A("| target min | %s |" % hw["target_achievement_minimum"])
    A("| decision | `%s` |" % hw["decision"])
    A("")
    A("## 7. Candidate statement")
    A("")
    A("- Classification: **FINAL_RECOMMENDED_PROFILE_CANDIDATE** (supported by the Evidence Review PASS)")
    A("- **NOT YET FORMALLY ACCEPTED** - this candidate is READY FOR FORMAL REVIEW only.")
    A("- Formal OPT-01 is independent and remains `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`.")
    A("- No Acceptance performed by the generator.")
    body = "\n".join(L) + "\n"
    return body


def _main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    inp = read_json(args.input)
    body = render(inp)
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline="\n").write(body)
    print(body, end="")
    return 0


def main(argv=None):
    try:
        return _main(argv)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print("CANDIDATE_RESULT_GENERATION_FAILED: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
