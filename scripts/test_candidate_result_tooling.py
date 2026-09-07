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
import shutil
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
EVD = SCRIPTS / "fixtures" / "fullmatrix-evidence"
REL = SCRIPTS / "fixtures" / "fullmatrix-release.json"
TAGREF = SCRIPTS / "fixtures" / "fullmatrix-tag-ref.json"
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


def build_input(out, ev=EVD, rel=REL, tagref=TAGREF, review_date=DATE,
                review_class=CLASS, dispatch=DISPATCH):
    return py(["scripts/build_candidate_result_input.py",
               "--evidence-dir", str(ev),
               "--matrix-config", str(MATRIX_CONFIG),
               "--release-json", str(rel),
               "--tag-ref-json", str(tagref),
               "--dispatch-sha", dispatch,
               "--evidence-review-doc", DOC,
               "--evidence-review-classification", review_class,
               "--review-date", review_date,
               "--out", str(out)], cwd=str(REPO_ROOT))


def gen(inp, out):
    return py(["scripts/generate_candidate_result.py", "--input", str(inp), "--out", str(out)],
              cwd=str(REPO_ROOT))


def validate(md, inp, rel=None, tagref=None, formal=False):
    args = ["scripts/validate_candidate_result.py", "--result", str(md), "--input", str(inp)]
    if rel:
        args += ["--release-json", str(rel)]
    if tagref:
        args += ["--tag-ref-json", str(tagref)]
    if formal:
        args.append("--formal")
    return py(args, cwd=str(REPO_ROOT))


def mutate(src, dst, old, new):
    t = read(src)
    assert old in t, "pattern missing: %s" % old[:60]
    write(dst, t.replace(old, new))


_EVSEQ = {"i": 0}


def copy_ev(tmp, name=None):
    if name is None:
        _EVSEQ['i'] += 1
        name = 'ev_%d' % _EVSEQ['i']
    dst = Path(tmp) / name
    shutil.copytree(EVD, dst)
    return dst


def assert_builder_fails(ev, **kw):
    out = Path(ev).parent / "should-not-exist.json"
    r = build_input(out, ev=ev, **kw)
    assert r.returncode != 0, "builder must FAIL (rc=0)"
    assert not out.exists(), "no input may be produced on FAIL"


# --- Q .. AL : authority / input-level negative tests (builder side) ---

def q_mat_status(tmp):
    ev = copy_ev(tmp)
    p = ev / "matrix-validation.json"
    d = jread(p)
    d["status"] = "FAIL"
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def r_measured(tmp):
    ev = copy_ev(tmp)
    p = ev / "matrix-validation.json"
    d = jread(p)
    d["measured_runs_count"] = 11
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def s_warmup(tmp):
    ev = copy_ev(tmp)
    p = ev / "matrix-validation.json"
    d = jread(p)
    d["warmup_runs_discarded_count"] = 3
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def t_cell_validation(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "validation.json"
    d = jread(p)
    d["status"] = "FAIL"
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def u_cell_agg(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["status"] = "FAIL"
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def v_agg_ach(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["d024_achievement_pct"] = d["d024_achievement_pct"] + 1.0
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def w_agg_delta(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["delta_vs_baseline_pct"] = d["delta_vs_baseline_pct"] + 0.5
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def x_agg_t80(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["d024_target_80_tok_s"] = d["d024_target_80_tok_s"] + 5.0
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def y_profile(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "profile-snapshot.json"
    d = jread(p)
    d["gpu_memory_utilization"] = 0.97
    write(p, json.dumps(d, indent=2))
    assert_builder_fails(ev)


def z_identity(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-64K" / "runtime-identity.txt"
    t = read(p)
    write(p, t.replace("pid_host=3164838", "pid_host=9999999"))
    assert_builder_fails(ev)


def aa_sums(tmp):
    ev = copy_ev(tmp)
    p = ev / "SHA256SUMS.txt"
    lines = read(p).splitlines()
    h, rest = lines[0].split(None, 1)
    lines[0] = "0" + h[1:] + "  " + rest
    write(p, "\n".join(lines) + "\n")
    assert_builder_fails(ev)


def ab_manifest(tmp):
    ev = copy_ev(tmp)
    (ev / "MANIFEST.txt").unlink()
    assert_builder_fails(ev)


def ac_config(tmp):
    ev = copy_ev(tmp)
    cfg = jread(MATRIX_CONFIG)
    cfg["hardware"]["A3_total_tflops"] = 6048
    p = Path(tmp) / "cfg-bad.json"
    write(p, json.dumps(cfg, indent=2))
    r = py(["scripts/build_candidate_result_input.py",
            "--evidence-dir", str(ev), "--matrix-config", str(p),
            "--release-json", str(REL), "--tag-ref-json", str(TAGREF),
            "--dispatch-sha", DISPATCH, "--evidence-review-doc", DOC,
            "--evidence-review-classification", CLASS, "--review-date", DATE,
            "--out", str(Path(tmp) / "nope.json")], cwd=str(REPO_ROOT))
    assert r.returncode != 0


def ad_bad_input_profile(tmp, inp, md):
    d = jread(inp)
    d["matrix"]["profile_identical_across_cells"] = False
    p = Path(tmp) / "bad-input.json"
    write(p, json.dumps(d, indent=2))
    m2 = Path(tmp) / "bad-result.md"
    assert gen(p, m2).returncode == 0
    r = validate(m2, p)
    assert r.returncode != 0, "validator must fail on bad input even if result matches"


def ae_bad_input_matrix(tmp, inp, md):
    d = jread(inp)
    d["matrix"]["matrix_validation_status"] = "FAIL"
    p = Path(tmp) / "bad-input2.json"
    write(p, json.dumps(d, indent=2))
    m2 = Path(tmp) / "bad-result2.md"
    assert gen(p, m2).returncode == 0
    assert validate(m2, p).returncode != 0


def ag_tagref(tmp):
    ev = copy_ev(tmp)
    tr = jread(TAGREF)
    tr["object"] = {"sha": "f" * 40, "type": "commit"}
    p = Path(tmp) / "tag-fake.json"
    write(p, json.dumps(tr, indent=2))
    r = build_input(Path(tmp) / "o.json", ev=ev, tagref=p)
    assert r.returncode != 0


def ah_fresh(tmp, inp, md):
    rel_bad = Path(tmp) / "rel-fresh.json"
    d = jread(REL)
    d["assets"] = [dict(a) for a in d["assets"]]
    a0 = d["assets"][0]
    a0["digest"] = "0" + a0["digest"][1:]
    write(rel_bad, json.dumps(d, indent=2))
    r = validate(md, inp, rel=rel_bad, tagref=TAGREF, formal=True)
    assert r.returncode != 0, "fresh digest mismatch must fail formal gate"


def ai_review_class(tmp):
    ev = copy_ev(tmp)
    doc_bad = Path(tmp) / "doc-bad.md"
    t = read(Path(REPO_ROOT) / DOC)
    t = t.replace("FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS",
                  "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_FAIL")
    write(doc_bad, t)
    r = py(["scripts/build_candidate_result_input.py",
            "--evidence-dir", str(ev), "--matrix-config", str(MATRIX_CONFIG),
            "--release-json", str(REL), "--tag-ref-json", str(TAGREF),
            "--dispatch-sha", DISPATCH,
            "--evidence-review-doc", str(doc_bad),
            "--evidence-review-classification", CLASS, "--review-date", DATE,
            "--out", str(Path(tmp) / "o.json")], cwd=str(REPO_ROOT))
    assert r.returncode != 0


def aj_review_date(tmp):
    ev = copy_ev(tmp)
    out = Path(tmp) / 'o-aj.json'
    r = build_input(out, ev=ev, review_date="2026-09-04")
    assert r.returncode != 0, 'builder must fail on review-date mismatch'
    assert not out.exists()


def ak_model_path(tmp):
    ev = copy_ev(tmp)
    p2 = ev / "cell-1K" / "runtime-identity.txt"
    t = read(p2)
    write(p2, t.replace("model_path=/data/tiankuan/zyg/model/GLM-5.2-w8a8", "model_path=/data/wrong/model"))
    assert_builder_fails(ev)


def al_env(tmp):
    ev = copy_ev(tmp)
    p3 = ev / "environment.txt"
    t = read(p3)
    write(p3, t.replace("HCCL_BUFFSIZE=200", "HCCL_BUFFSIZE=201"))
    assert_builder_fails(ev)


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
            r = validate(md, inp, rel=REL, tagref=TAGREF, formal=True)
            assert r.returncode == 0, r.stdout[-200:] + r.stderr[-200:]

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

        def ad_bad_input():
            d = jread(inp)
            d["matrix"]["profile_identical_across_cells"] = False
            bad = w / "bad-input.json"
            write(bad, json.dumps(d, indent=2))
            m2 = w / "bad-result.md"
            assert gen(bad, m2).returncode == 0
            assert validate(m2, bad).returncode != 0

        def ae_bad_input():
            d = jread(inp)
            d["matrix"]["matrix_validation_status"] = "FAIL"
            bad = w / "bad-input2.json"
            write(bad, json.dumps(d, indent=2))
            m2 = w / "bad-result2.md"
            assert gen(bad, m2).returncode == 0
            assert validate(m2, bad).returncode != 0

        def af_bad_input():
            d = jread(inp)
            d["cells"]["64K"]["d024_achievement_pct"] = 93.0
            bad = w / "bad-input3.json"
            write(bad, json.dumps(d, indent=2))
            m2 = w / "bad-result3.md"
            assert gen(bad, m2).returncode == 0
            assert validate(m2, bad).returncode != 0

        def ah_fresh():
            rel_bad = w / "rel-fresh.json"
            d = jread(REL)
            d["assets"] = [dict(a) for a in d["assets"]]
            a0 = d["assets"][0]
            a0["digest"] = "0" + a0["digest"][1:]
            write(rel_bad, json.dumps(d, indent=2))
            r = validate(md, inp, rel=rel_bad, tagref=TAGREF, formal=True)
            assert r.returncode != 0

        it("Q", lambda: q_mat_status(w))
        it("R", lambda: r_measured(w))
        it("S", lambda: s_warmup(w))
        it("T", lambda: t_cell_validation(w))
        it("U", lambda: u_cell_agg(w))
        it("V", lambda: v_agg_ach(w))
        it("W", lambda: w_agg_delta(w))
        it("X", lambda: x_agg_t80(w))
        it("Y", lambda: y_profile(w))
        it("Z", lambda: z_identity(w))
        it("AA", lambda: aa_sums(w))
        it("AB", lambda: ab_manifest(w))
        it("AC", lambda: ac_config(w))
        it("AD", lambda: ad_bad_input())
        it("AE", lambda: ae_bad_input())
        it("AF", lambda: af_bad_input())
        it("AG", lambda: ag_tagref(w))
        it("AH", lambda: ah_fresh())
        it("AI", lambda: ai_review_class(w))
        it("AJ", lambda: aj_review_date(w))
        it("AK", lambda: ak_model_path(w))
        it("AL", lambda: al_env(w))
        print("SUMMARY: %d failed / 38 total (A-P + Q-AL)" % len(failed))
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())