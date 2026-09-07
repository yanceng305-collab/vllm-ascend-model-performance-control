#!/usr/bin/env python3
"""Mandatory regression tests for Full-Matrix Profile Candidate Result tooling.

Fixture: scripts/fixtures/fullmatrix-evidence (immutable reviewed D-025 tree)
+ scripts/fixtures/fullmatrix-release.json (GitHub release metadata).

TEST A  build candidate input PASS + deterministic
TEST B  generator deterministic
TEST C  generated Result -> validator PASS
TEST D  run2/3/4 throughput mutated -> FAIL
TEST E  mean mutated -> FAIL
TEST F  A3 6016 -> 6048 / 6058 / 6076 -> FAIL
TEST G  achievement mutated -> FAIL
TEST H  frozen profile 0.95 -> 0.97 / 67000 -> 70000 -> FAIL
TEST I  measured 12 -> 11 -> FAIL
TEST J  warmup 4 -> 3 -> FAIL
TEST K  profile-identical false -> FAIL
TEST L  runtime identity mismatch -> FAIL
TEST M  asset digest changed -> FAIL
TEST N  Result Type BASELINE -> FAIL
TEST O  Status ACCEPTED -> FAIL
TEST P  old baseline tooling regression

0 skip; any FAIL exits 1.
"""
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
EVD = SCRIPTS / "fixtures" / "fullmatrix-evidence"
REL = SCRIPTS / "fixtures" / "fullmatrix-release.json"
MATRIX_CONFIG = REPO_ROOT / "docs/vllm-ascend-performance/models/glm-5.2-w8a8/candidate-matrix-config.json"
DISPATCH = "2711b6ed366d84187a1102b60186d42c5ba198cd"
CLASS = "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS"
DOC = "docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/EVIDENCE-REVIEW-PROFILE-CANDIDATE-FULL-MATRIX-20260907.md"
DATE = "2026-09-07"
ASSET_DIGEST = json.load(io.open(REL, encoding="utf-8"))["assets"][0]["digest"]


def read(p):
    return io.open(p, encoding="utf-8").read()


def write(p, t):
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)


def jread(p):
    return json.load(io.open(p, encoding="utf-8"))


def py(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=cwd)


def build_input(out):
    return py(["scripts/build_candidate_result_input.py",
               "--evidence-dir", str(EVD),
               "--matrix-config", str(MATRIX_CONFIG),
               "--release-json", str(REL),
               "--dispatch-sha", DISPATCH,
               "--evidence-review-doc", DOC,
               "--evidence-review-classification", CLASS,
               "--review-date", DATE,
               "--out", str(out)], cwd=str(REPO_ROOT))


def gen(inp, out):
    return py(["scripts/generate_candidate_result.py", "--input", str(inp), "--out", str(out)],
              cwd=str(REPO_ROOT))


def validate(md, inp, rel=None):
    args = ["scripts/validate_candidate_result.py", "--result", str(md), "--input", str(inp)]
    if rel:
        args += ["--release-json", str(rel)]
    return py(args, cwd=str(REPO_ROOT))


def mutate(src, dst, old, new):
    t = read(src)
    assert old in t, "pattern missing: %s" % old[:60]
    write(dst, t.replace(old, new))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        w = Path(tmp)
        inp = w / "input.json"
        built = build_input(inp)
        if built.returncode != 0:
            print("FIXTURE FAIL: builder rc=%s %s" % (built.returncode, built.stderr[:400]))
            return 1
        md = w / "result.md"
        g = gen(inp, md)
        if g.returncode != 0:
            print("FIXTURE FAIL: generator rc=%s %s" % (g.returncode, g.stderr[:400]))
            return 1
        failed = []

        def it(name, fn):
            try:
                fn()
                print("PASS %s" % name)
            except AssertionError as e:
                failed.append(name)
                print("FAIL %s: %s" % (name, e))

        def a():
            out2 = w / "input2.json"
            assert build_input(out2).returncode == 0
            assert read(inp) == read(out2)
            d = jread(inp)
            assert d["result_type"] == "PROFILE_CANDIDATE_FULL_MATRIX"
            assert d["matrix"]["measured_runs_count"] == 12
            assert d["matrix"]["warmup_runs_discarded_count"] == 4

        def b():
            md2 = w / "result2.md"
            assert gen(inp, md2).returncode == 0
            assert read(md2) == read(md)

        def c():
            r = validate(md, inp, rel=REL)
            assert r.returncode == 0, r.stdout[-160:] + r.stderr[-160:]

        def d():
            m2 = w / "d.md"
            mutate(md, m2, "| 1K | 1198.14 |", "| 1K | 1198.15 |")
            assert validate(m2, inp).returncode != 0

        def e():
            m2 = w / "e.md"
            mutate(md, m2, "1205.0900", "1205.0901")
            assert validate(m2, inp).returncode != 0

        def f():
            for bad in ("6048", "6058", "6076"):
                m2 = w / ("f_" + bad + ".md")
                mutate(md, m2, "| A3 | 8 x 752 = 6016 |", "| A3 | 8 x 752 = %s |" % bad)
                assert validate(m2, inp).returncode != 0, bad

        def g_ach():
            m2 = w / "g.md"
            mutate(md, m2, "117.8919", "117.8918")
            assert validate(m2, inp).returncode != 0

        def h():
            m2 = w / "h1.md"
            mutate(md, m2, "gpu_memory_utilization | `0.95`", "gpu_memory_utilization | `0.97`")
            assert validate(m2, inp).returncode != 0
            m3 = w / "h2.md"
            mutate(md, m3, "max_model_len | `67000`", "max_model_len | `70000`")
            assert validate(m3, inp).returncode != 0

        def i():
            m2 = w / "i.md"
            mutate(md, m2, "| measured runs | 12 |", "| measured runs | 11 |")
            assert validate(m2, inp).returncode != 0

        def j():
            m2 = w / "j.md"
            mutate(md, m2, "| warmup discarded | 4 |", "| warmup discarded | 3 |")
            assert validate(m2, inp).returncode != 0

        def k():
            m2 = w / "k.md"
            mutate(md, m2, "profile identical | True", "profile identical | False")
            assert validate(m2, inp).returncode != 0

        def l():
            m2 = w / "l.md"
            mutate(md, m2, "runtime identity identical | True", "runtime identity identical | False")
            assert validate(m2, inp).returncode != 0

        def m_case():
            m2 = w / "m.md"
            digest = ASSET_DIGEST
            mutate(md, m2, digest, "0" + digest[1:])
            assert validate(m2, inp).returncode != 0
            rel_bad = w / "rel_bad.json"
            payload = jread(REL)
            payload["assets"] = [dict(a) for a in payload["assets"]]
            payload["assets"][0]["digest"] = "0" + digest[1:]
            write(rel_bad, json.dumps(payload))
            assert validate(md, inp, rel=rel_bad).returncode != 0

        def n_case():
            m2 = w / "n.md"
            mutate(md, m2, "`PROFILE_CANDIDATE_FULL_MATRIX`", "`BASELINE`")
            assert validate(m2, inp).returncode != 0

        def o_case():
            m2 = w / "o.md"
            mutate(md, m2, "| Result State | `READY_FOR_FORMAL_REVIEW` |", "| Result State | `ACCEPTED` |")
            assert validate(m2, inp).returncode != 0

        def p_case():
            for f in ("validate_evidence.py", "generate_result.py", "validate_result.py"):
                r = py(["-m", "py_compile", str(SCRIPTS / f)])
                assert r.returncode == 0, (f, r.stderr)
            r = py(["scripts/validate_evidence.py"], cwd=str(REPO_ROOT))
            assert r.returncode != 0
            r = py(["scripts/generate_result.py"], cwd=str(REPO_ROOT))
            assert r.returncode != 0
            r = py(["scripts/validate_result.py"], cwd=str(REPO_ROOT))
            assert r.returncode != 0

        it("A", a)
        it("B", b)
        it("C", c)
        it("D", d)
        it("E", e)
        it("F", f)
        it("G", g_ach)
        it("H", h)
        it("I", i)
        it("J", j)
        it("K", k)
        it("L", l)
        it("M", m_case)
        it("N", n_case)
        it("O", o_case)
        it("P", p_case)
        print("SUMMARY: %d failed / 16" % len(failed))
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())