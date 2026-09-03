#!/usr/bin/env python3
"""Deterministic regression tests for the Full-Matrix candidate tooling.

Required before push (PRE-DISPATCH TOOLING REVIEW + FIX):
  TEST A  real reviewed 64K Run2 log -> extractor -> expected metrics (raw truth)
  TEST B  same log extracted twice -> byte-identical JSON
  TEST C  malformed log missing Total Token Throughput -> non-zero exit (--strict)
  TEST D  canonical runN.command.txt contract: correct -> PASS; wrong cell
          input / output / concurrency / prompts / ignore-eos -> FAIL
  TEST E  Run2/Run3/Run4 fixture values -> mean/min/max/stddev/CV deterministic
          (run1 WARMUP_DISCARD excluded; stored metrics mutation rejected;
          run1.role.txt artifact gate enforced)
  TEST F  matrix-level profile snapshots: all identical -> PASS; one field
          changed in one cell -> FAIL
  TEST G  Runner Prompt command artifact integration: artifact JSON first item
          == "vllm", JSON == executed argv exactly, no artifact-path element;
          pinned $CONTROL_DIR extractor/validator invocation from unrelated cwd

Fixture: scripts/fixtures/followup-64k-run2/run2.log = the review-verified
64K FOLLOW-UP-2 run2 raw log (GitHub Release glm52-od-64k-followup-20260903,
asset final-evidence-64k.tar.gz, SHA256 15bb96cd...43fa5).

No SKIP is allowed; any FAIL -> exit 1.
"""

import contextlib
import io
import json
import math
import re
import statistics
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import bench_common as bc
import extract_bench_metrics as extractor
import validate_matrix_candidate as per_cell
import validate_full_matrix_candidate as matrix_validator

FIXTURE = SCRIPTS / "fixtures" / "followup-64k-run2" / "run2.log"
MATRIX_CONFIG = (
    REPO_ROOT / "docs" / "vllm-ascend-performance" / "models"
    / "glm-5.2-w8a8" / "candidate-matrix-config.json"
)
CFG = bc.load_matrix_config(MATRIX_CONFIG)
CELLS = ["1K", "4K", "16K", "64K"]


def read_bytes(path):
    return io.open(path, "rb").read()


def write_text(path, text):
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


def bench_log_text(ttt, drop_ttt=False):
    """Fixture text with the Total token throughput value replaced (raw format)."""
    text = io.open(FIXTURE, encoding="utf-8", errors="replace").read()
    text = re.sub(
        r"(Total token throughput \(tok/s\):\s*)[0-9][0-9.,]*",
        lambda m: m.group(1) + "{:.2f}".format(ttt),
        text,
    )
    if drop_ttt:
        text = "\n".join(l for l in text.splitlines() if "Total token throughput" not in l) + "\n"
    return text


def build_argv(cell, cfg, overrides=None):
    ov = overrides or {}
    cc = cfg["cells"][cell]
    wl = cfg["workload_contract"]
    return [
        "vllm", "bench", "serve",
        "--backend", str(wl["backend"]),
        "--base-url", "http://127.0.0.1:8000",
        "--endpoint", str(wl["endpoint"]),
        "--model", "glm52-w8a8",
        "--tokenizer", "/data/tiankuan/zyg/model/GLM-5.2-w8a8",
        "--trust-remote-code",
        "--dataset-name", str(ov.get("dataset", wl["dataset"])),
        "--random-input-len", str(ov.get("input", cc["input_len"])),
        "--random-output-len", str(ov.get("out", cc["output_len"])),
        "--random-range-ratio", str(wl["random_range_ratio"]),
        "--request-rate", str(wl["request_rate"]),
        "--max-concurrency", str(ov.get("concurrency", wl["max_concurrency"])),
        "--num-prompts", str(ov.get("prompts", wl["num_prompts"])),
    ] + (["--ignore-eos"] if ov.get("ignore_eos", True) else [])


def quiet(fn):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = fn()
    return rc


def capture(fn):
    """Return (rc, stdout_text, stderr_text) for a callable that returns an rc."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = fn()
    return rc, out.getvalue(), err.getvalue()


def make_cell(root, cell, ttt_map=None, cmd_overrides=None, drop_ttt=False,
              broken_run=None, role="WARMUP_DISCARD"):
    """Build a synthetic cell Evidence dir; returns Path(cell_dir).

    run1.role.txt is written exactly like Runner Prompt Step 4 (WARMUP_DISCARD
    by default) so the validator's artifact-backed discard gate has a real
    input. role=None omits the file; any other string is a wrong value.
    """
    ttt_map = ttt_map or {"run1": 99999.0, "run2": 1000.0, "run3": 1100.0, "run4": 1200.0}
    cell_dir = Path(root) / ("cell-" + cell)
    cell_dir.mkdir(parents=True, exist_ok=True)
    for run in ("run1", "run2", "run3", "run4"):
        text = bench_log_text(ttt_map[run], drop_ttt=drop_ttt)
        if run == broken_run:
            text = text.replace("Successful requests:                     256",
                                "Successful requests:                     255")
        write_text(cell_dir / (run + ".log"), text)
        bc.write_json_deterministic(cell_dir / (run + ".command.txt"),
                                    build_argv(cell, CFG, overrides=cmd_overrides))
        parsed = bc.parse_log(cell_dir / (run + ".log"))
        bc.write_json_deterministic(cell_dir / (run + ".metrics.json"), parsed)
    if role is None:
        pass  # role artifact intentionally absent -> gate must FAIL
    elif role == "WARMUP_DISCARD":
        write_text(cell_dir / "run1.role.txt", "WARMUP_DISCARD\n")
    else:
        write_text(cell_dir / "run1.role.txt", role + "\n")
    return cell_dir


# ================= TEST A: real fixture extraction ===========================

def test_a_real_fixture():
    metrics = bc.parse_log(FIXTURE)
    expected = {
        "successful_requests": 256,
        "failed_requests": 0,
        "benchmark_duration_s": 9676.4,
        "total_input_tokens": 16777216,
        "total_output_tokens": 262144,
        "request_throughput": 0.03,
        "output_token_throughput": 27.09,
        "total_token_throughput": 1760.92,
        "mean_ttft_ms": 2064099.81,
        "p99_ttft_ms": 2429862.46,
        "mean_tpot_ms": 46.16,
        "p99_tpot_ms": 47.34,
        "mean_itl_ms": 46.16,
        "p99_itl_ms": 46.13,
    }
    for key, want in expected.items():
        got = metrics[key]
        assert got == want, "key %s: got %r want %r" % (key, got, want)
    assert bc.required_missing(metrics) == []
    rc = quiet(lambda: extractor.main([str(FIXTURE), "--strict"]))
    assert rc == 0, "extractor --strict rc=%s" % rc
    print("  PASS TEST A: real 64K run2 log -> exact raw-log metrics")


# ==================== TEST B: byte-identical double extraction ===================

def test_b_deterministic():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = Path(tmp) / "m1.json"
        out2 = Path(tmp) / "m2.json"
        r1 = quiet(lambda: extractor.main([str(FIXTURE), "--out", str(out1), "--strict"]))
        r2 = quiet(lambda: extractor.main([str(FIXTURE), "--out", str(out2), "--strict"]))
        assert r1 == 0 and r2 == 0, (r1, r2)
        assert read_bytes(out1) == read_bytes(out2), "JSON differs between extractions"
        # staged regeneration (what the validator does) must also match
        metrics = bc.parse_log(FIXTURE)
        rendered = (json.dumps(metrics, indent=2, sort_keys=True) + "\n").encode("utf-8")
        assert read_bytes(out1) == rendered
    print("  PASS B — extraction byte-identical + matches rewrite")


# ==================== TEST C: malformed log fails closed =============================

def test_c_missing_throughput():
    """Malformed log (Total token throughput removed) -> extractor --strict real FAIL."""
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.log"
        out = Path(tmp) / "bad.metrics.json"
        write_text(bad, bench_log_text(0.0, drop_ttt=True))
        # real invocation, real exit-code assertion, real stderr content
        rc, _out, err = capture(lambda: extractor.main([str(bad), "--out", str(out), "--strict"]))
        assert rc != 0, "extractor --strict must exit non-zero on malformed log (rc=%s)" % rc
        assert "total_token_throughput" in err, (
            "error must name the missing field; got stderr=%r" % err[:300])
        assert not out.exists(), "no derived JSON may be written on strict failure"
    print("  PASS C — missing Total token throughput -> extractor --strict FAIL + names field")


# ==================== TEST D: runN.command.txt contract ==========================

def test_d_contract_gate():
    values = {"run1": 99999.0, "run2": 1000.0, "run3": 1100.0, "run4": 1200.0}
    with tempfile.TemporaryDirectory() as tmp:
        # correct cell must PASS
        good = make_cell(tmp, "64K", ttt_map=values)
        assert quiet(lambda: per_cell.main(["--cell-dir", str(good), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG)])) == 0

        # wrong cell input / output / concurrency / prompts / ignore-eos must FAIL
        cases = [
            ("input", {"input": 4096}),
            ("output", {"out": 2048}),
            ("concurrency", {"concurrency": 32}),
            ("prompts", {"prompts": 128}),
            ("ignore-eos removed", {"ignore_eos": False}),
        ]
        for label, ov in cases:
            cell_dir = make_cell(tmp, "64K", ttt_map=values, cmd_overrides=ov)
            rc = quiet(lambda: per_cell.main(["--cell-dir", str(cell_dir), "--cell", "64K",
                                              "--matrix-config", str(MATRIX_CONFIG)]))
            assert rc == 1, "expected FAIL for %s (rc=%s)" % (label, rc)
            print("    FAIL-expected: %s" % label)
        # wrong run1/run2 counts must FAIL
        cell_bad = make_cell(tmp, "64K", ttt_map=values, broken_run="run3")
        rc = quiet(lambda: per_cell.main(["--cell-dir", str(cell_bad), "--cell", "64K",
                                           "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc == 1, "broken counts must FAIL"
    print("  PASS TEST D: contract gate FAIL-closed on every mutation")


# ==================== TEST E: aggregation determinism + stats ===================

def test_e_aggregation():
    values = {"run1": 99999.0, "run2": 1000.0, "run3": 1100.0, "run4": 1200.0}
    with tempfile.TemporaryDirectory() as tmp:
        cell = make_cell(tmp, "64K", ttt_map=values)
        out = Path(tmp) / "out"
        rc1 = quiet(lambda: per_cell.main(["--cell-dir", str(cell), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG),
                                            "--out-dir", str(out)]))
        assert rc1 == 0, "per-cell must PASS"
        agg1 = read_bytes(out / "aggregation.json")
        val1 = read_bytes(out / "validation.json")

        rc2 = quiet(lambda: per_cell.main(["--cell-dir", str(cell), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG),
                                            "--out-dir", str(out)]))
        assert rc2 == 0
        assert read_bytes(out / "aggregation.json") == agg1, "aggregation not deterministic"
        assert read_bytes(out / "validation.json") == val1, "validation not deterministic"

        agg = bc.read_json(out / "aggregation.json")
        assert agg["run2_tok_s"] == 1000.0
        assert agg["run3_tok_s"] == 1100.0
        assert agg["run4_tok_s"] == 1200.0
        assert abs(agg["formal_value_tok_s"] - 1100.0) < 1e-9, "run1 must be excluded from mean"
        assert agg["min_tok_s"] == 1000.0
        assert agg["max_tok_s"] == 1200.0
        expect_sd = statistics.pstdev([1000.0, 1100.0, 1200.0])
        assert abs(agg["stddev_pop_tok_s"] - expect_sd) < 1e-9
        assert abs(agg["cv_pct"] - (expect_sd / 1100.0 * 100.0)) < 1e-9
        assert agg["run1_excluded"] is True

        val = bc.read_json(out / "validation.json")
        assert val["runs"]["run1"]["role"] == "WARMUP_DISCARD"
        assert val["runs"]["run1"]["in_mean"] is False
        assert val["runs"]["run2"]["role"] == "MEASURED"

        # stored metrics mutation must be rejected (determinism gate)
        stored = bc.read_json(cell / "run2.metrics.json")
        stored["total_token_throughput"] = 9999.0
        bc.write_json_deterministic(cell / "run2.metrics.json", stored)
        rc3 = quiet(lambda: per_cell.main(["--cell-dir", str(cell), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc3 == 1, "stored metrics mutation must FAIL determinism check"

        # run1.role.txt artifact gate: wrong content must FAIL
        cell_wrong_role = make_cell(tmp, "64K", ttt_map=values, role="MEASURED")
        rc4 = quiet(lambda: per_cell.main(["--cell-dir", str(cell_wrong_role), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc4 == 1, "run1.role.txt wrong content must FAIL"
        # run1.role.txt artifact gate: missing file must FAIL
        cell_no_role = make_cell(tmp, "64K", ttt_map=values, role=None)
        rc5 = quiet(lambda: per_cell.main(["--cell-dir", str(cell_no_role), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc5 == 1, "missing run1.role.txt must FAIL"
    print("  PASS TEST E: aggregation deterministic, run1 excluded, role artifact gate enforced")


# ==================== TEST F: matrix profile consistency ======================

def test_f_matrix_gate():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for cell in CELLS:
            values = {"run1": 99999.0, "run2": 1000.0, "run3": 1100.0, "run4": 1200.0}
            cell_dir = make_cell(root, cell, ttt_map=values)
            quiet(lambda: per_cell.main(["--cell-dir", str(cell_dir), "--cell", cell,
                                          "--matrix-config", str(MATRIX_CONFIG),
                                          "--out-dir", str(cell_dir)]))
            profile = {
                "model": "GLM-5.2-W8A8",
                "gpu_memory_utilization": 0.95,
                "max_model_len": 67000,
                "max_cudagraph_capture_size": 96,
                "mtp": "OFF",
                "dp": 2, "tp": 8, "ep": "ON",
                "max_num_seqs": 48,
                "max_num_batched_tokens": 4096,
                "async_scheduling": "ON",
                "multistream_overlap_shared_expert": "ON",
                "cudagraph_level": "FULL_DECODE_ONLY",
                "prefix_cache": "OFF",
            }
            bc.write_json_deterministic(cell_dir / "profile-snapshot.json", profile)
            write_text(cell_dir / "runtime-identity.txt", "same warm service\n")
        rc = quiet(lambda: matrix_validator.main(["--matrix-dir", str(root),
                                                      "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc == 0, "identical profile snapshots must PASS"
        # break one field in one cell -> matrix FAIL
        broken = bc.read_json(root / "cell-64K" / "profile-snapshot.json")
        broken["max_model_len"] = 70000
        bc.write_json_deterministic(root / "cell-64K" / "profile-snapshot.json", broken)
        rc2 = quiet(lambda: matrix_validator.main(["--matrix-dir", str(root),
                                                       "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc2 == 1, "profile drift must FAIL matrix validation"
    print("  PASS TEST F: matrix gate detects profile drift across cells")


# ==================== TEST G: Runner Prompt command artifact integration ==========

# Exact python -c program text from Runner Prompt Step 4 (argv payload = sys.argv[2:],
# self-verifying). Kept verbatim so the test exercises the REAL artifact contract.
PROMPT_ARTIFACT_SNIPPET = """
import json, sys
p = sys.argv[1]
argv = sys.argv[2:]
with open(p, "w", encoding="utf-8", newline="\\n") as f:
    json.dump(argv, f, indent=2)
    f.write("\\n")
got = json.load(open(p, encoding="utf-8"))
assert got == argv and got and got[0] == "vllm", "command artifact corruption"
"""


def test_g_prompt_command_contract():
    """Prompt-step artifact generation == executed argv; pinned $CONTROL_DIR invocations."""
    import subprocess as sp
    with tempfile.TemporaryDirectory() as tmp:
        values = {"run1": 99999.0, "run2": 1000.0, "run3": 1100.0, "run4": 1200.0}
        cell = make_cell(tmp, "64K", ttt_map=values)  # gives logs + role + metrics (command files overwritten below)
        base_url = "http://127.0.0.1:8000"
        cmd_artifacts = []
        for run in ("run1", "run2", "run3", "run4"):
            # EXACT argv array as the Runner Prompt Step 4 builds it
            bench_args = [
                "vllm", "bench", "serve",
                "--backend", "vllm",
                "--base-url", base_url,
                "--endpoint", "/v1/completions",
                "--model", "glm52-w8a8",
                "--tokenizer", "/data/tiankuan/zyg/model/GLM-5.2-w8a8",
                "--trust-remote-code",
                "--dataset-name", "random",
                "--random-input-len", "65536",
                "--random-output-len", "1024",
                "--random-range-ratio", "0",
                "--request-rate", "inf",
                "--max-concurrency", "64",
                "--num-prompts", "256",
                "--ignore-eos",
                "--save-result",
                "--result-dir", str(cell),
                "--result-filename", "run%s.json" % run,
            ]
            artifact = cell / (run + ".command.txt")
            # run the REAL prompt snippet (subprocess, exact code path)
            r = sp.run([sys.executable, "-c", PROMPT_ARTIFACT_SNIPPET, str(artifact)] + bench_args,
                       capture_output=True, text=True)
            assert r.returncode == 0, "artifact snippet failed: %s" % r.stderr
            cmd_artifacts.append((artifact, bench_args))

        for artifact, bench_args in cmd_artifacts:
            tokens_now = bc.read_json(artifact)
            assert tokens_now and tokens_now[0] == "vllm", "artifact first element must be 'vllm'"
            assert tokens_now == bench_args, "artifact must equal executed argv exactly"
            assert all(t != str(artifact) for t in tokens_now), (
                "artifact path must not appear as an argv element")
        # contract validator PASS on the same cell using these artifacts
        rc = quiet(lambda: per_cell.main(["--cell-dir", str(cell), "--cell", "64K",
                                            "--matrix-config", str(MATRIX_CONFIG)]))
        assert rc == 0, "cell must PASS with prompt-generated artifacts (rc=%s)" % rc

        # pinned $CONTROL_DIR extractor invocation: absolute path, unrelated cwd
        r2 = sp.run([sys.executable, str(SCRIPTS / "extract_bench_metrics.py"),
                     str(cell / "run2.log"), "--out", str(Path(tmp) / "pinned.json"), "--strict"],
                    capture_output=True, text=True, cwd=str(Path(tmp)))
        assert r2.returncode == 0, "pinned extractor invocation failed: %s" % r2.stderr
        r3 = sp.run([sys.executable, str(SCRIPTS / "validate_matrix_candidate.py"),
                     "--cell-dir", str(cell), "--cell", "64K",
                     "--matrix-config", str(MATRIX_CONFIG)],
                    capture_output=True, text=True, cwd=str(Path(tmp)))
        assert r3.returncode == 0, "pinned per-cell validator invocation failed: %s" % r3.stderr
        assert "64K" in r3.stdout
    print("  PASS TEST G: prompt artifact == executed argv (first item vllm), pinned $CONTROL invocations work")


# ======================= main ==================================================

def main():
    tests = [
        (test_a_real_fixture, "TEST A"),
        (test_b_deterministic, "TEST B"),
        (test_c_missing_throughput, "TEST C"),
        (test_d_contract_gate, "TEST D"),
        (test_e_aggregation, "TEST E"),
        (test_f_matrix_gate, "TEST F"),
        (test_g_prompt_command_contract, "TEST G"),
    ]
    failed = 0
    for fn, label in tests:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("  FAIL %s: %r" % (label, e))
        else:
            print("  OK %s" % label)
    print("SUMMARY: %d passed, %d failed" % (len(tests) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())