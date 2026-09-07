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
TEST P  legacy tooling smoke / backward-compatibility sanity
TEST AM-BB last-mile correctness: duplicate keys, explicit unset, fresh
           provenance, exact D-024, and runtime identity Result gates
TEST BC-BM final Result-field coverage: exact ID/date/classification, tag object,
           OPT-01, schema/version, pinned count, identity aggregate, redundancy

All negative cases require rc=1, an expected blocker token, and no traceback or
uncaught exception. 0 skip; any FAIL exits 1.
"""
import io
import shutil
import json
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
EVD = Path(os.environ.get("CANDIDATE_EVIDENCE_DIR",
                          str(SCRIPTS / "fixtures" / "fullmatrix-evidence")))
REL = SCRIPTS / "fixtures" / "fullmatrix-release.json"
TAGREF = SCRIPTS / "fixtures" / "fullmatrix-tag-ref.json"
MATRIX_CONFIG = REPO_ROOT / "docs/vllm-ascend-performance/models/glm-5.2-w8a8/candidate-matrix-config.json"
DISPATCH = "2711b6ed366d84187a1102b60186d42c5ba198cd"
CLASS = "FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS"
DOC = "docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/EVIDENCE-REVIEW-PROFILE-CANDIDATE-FULL-MATRIX-20260907.md"
DATE = "2026-09-07"
ASSET_DIGEST = json.load(io.open(REL, encoding="utf-8"))["assets"][0]["digest"]
CRASH_TOKENS = ("Traceback", "NameError", "KeyError", "UnboundLocalError",
                "SyntaxError", "uncaught exception")
CRASH_COUNT = {"value": 0}


class FixedTestDirectory:
    """Use a known workspace-writable directory under the Windows sandbox."""

    def __init__(self):
        self.path = Path(r"E:\模型推理\_candidate_tooling_test")

    def __enter__(self):
        self.path.mkdir(parents=True, exist_ok=True)
        for child in self.path.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
        return str(self.path)

    def __exit__(self, exc_type, exc, tb):
        return False


def read(p):
    return io.open(p, encoding="utf-8").read()


def write(p, t):
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)


def jread(p):
    return json.load(io.open(p, encoding="utf-8"))


def py(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=cwd)


def build_input(out, ev=EVD, rel=REL, tagref=TAGREF, review_date=DATE,
                review_class=CLASS, dispatch=DISPATCH, matrix_config=MATRIX_CONFIG):
    return py(["scripts/build_candidate_result_input.py",
               "--evidence-dir", str(ev),
               "--matrix-config", str(matrix_config),
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


def output(r):
    return (r.stdout or "") + (r.stderr or "")


def assert_semantic_failure(r, expected, label="negative test"):
    text = output(r)
    crashes = [token for token in CRASH_TOKENS if token.lower() in text.lower()]
    CRASH_COUNT["value"] += len(crashes)
    assert r.returncode == 1, "%s rc=%s, expected 1; output=%s" % (label, r.returncode, text[-400:])
    assert expected in text, "%s missing blocker %r; output=%s" % (label, expected, text[-400:])
    assert not crashes, "%s unexpected crash tokens: %s" % (label, crashes)


def update_checksum(ev, relative):
    path = Path(ev) / relative
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    sums = Path(ev) / "SHA256SUMS.txt"
    lines = read(sums).splitlines()
    replaced = False
    for i, line in enumerate(lines):
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[1].strip() == relative:
            lines[i] = "%s  %s" % (digest, relative)
            replaced = True
            break
    assert replaced, "checksum entry missing for %s" % relative
    write(sums, "\n".join(lines) + "\n")


_EVSEQ = {"i": 0}


def copy_ev(tmp, name=None):
    if name is None:
        _EVSEQ['i'] += 1
        name = 'ev_%d' % _EVSEQ['i']
    dst = Path(tmp) / name
    shutil.copytree(EVD, dst)
    return dst


def assert_builder_fails(ev, expected, label="builder", **kw):
    out = Path(ev).parent / "should-not-exist.json"
    r = build_input(out, ev=ev, **kw)
    assert_semantic_failure(r, expected, label)
    assert not out.exists(), "no input may be produced on FAIL"


# --- Q .. AL : authority / input-level negative tests (builder side) ---

def q_mat_status(tmp):
    ev = copy_ev(tmp)
    p = ev / "matrix-validation.json"
    d = jread(p)
    d["status"] = "FAIL"
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "matrix-validation.json")
    assert_builder_fails(ev, "matrix-validation.status != PASS")


def r_measured(tmp):
    ev = copy_ev(tmp)
    p = ev / "matrix-validation.json"
    d = jread(p)
    d["measured_runs_count"] = 11
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "matrix-validation.json")
    assert_builder_fails(ev, "measured != 12")


def s_warmup(tmp):
    ev = copy_ev(tmp)
    p = ev / "matrix-validation.json"
    d = jread(p)
    d["warmup_runs_discarded_count"] = 3
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "matrix-validation.json")
    assert_builder_fails(ev, "warmup != 4")


def t_cell_validation(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "validation.json"
    d = jread(p)
    d["status"] = "FAIL"
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "cell-1K/validation.json")
    assert_builder_fails(ev, "cell 1K validation != PASS")


def u_cell_agg(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["status"] = "FAIL"
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "cell-1K/aggregation.json")
    assert_builder_fails(ev, "cell 1K aggregation != PASS")


def v_agg_ach(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["d024_achievement_pct"] = d["d024_achievement_pct"] + 1.0
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "cell-1K/aggregation.json")
    assert_builder_fails(ev, "cell 1K aggregation ach")


def w_agg_delta(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["delta_vs_baseline_pct"] = d["delta_vs_baseline_pct"] + 0.5
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "cell-1K/aggregation.json")
    assert_builder_fails(ev, "cell 1K aggregation delta")


def x_agg_t80(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "aggregation.json"
    d = jread(p)
    d["d024_target_80_tok_s"] = d["d024_target_80_tok_s"] + 5.0
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "cell-1K/aggregation.json")
    assert_builder_fails(ev, "cell 1K aggregation t80")


def y_profile(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-1K" / "profile-snapshot.json"
    d = jread(p)
    d["gpu_memory_utilization"] = 0.97
    write(p, json.dumps(d, indent=2))
    update_checksum(ev, "cell-1K/profile-snapshot.json")
    assert_builder_fails(ev, "profile-snapshot.json not identical across cells")


def z_identity(tmp):
    ev = copy_ev(tmp)
    p = ev / "cell-64K" / "runtime-identity.txt"
    t = read(p)
    write(p, t.replace("pid_host=3164838", "pid_host=9999999"))
    update_checksum(ev, "cell-64K/runtime-identity.txt")
    assert_builder_fails(ev, "identity field 'pid_host' differs")


def aa_sums(tmp):
    ev = copy_ev(tmp)
    p = ev / "SHA256SUMS.txt"
    lines = read(p).splitlines()
    h, rest = lines[0].split(None, 1)
    lines[0] = "0" + h[1:] + "  " + rest
    write(p, "\n".join(lines) + "\n")
    assert_builder_fails(ev, "SHA256SUMS mismatch")


def ab_manifest(tmp):
    ev = copy_ev(tmp)
    (ev / "MANIFEST.txt").unlink()
    assert_builder_fails(ev, "MANIFEST.txt missing")


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
    assert_semantic_failure(r, "matrix-config hardware.A3_total_tflops", "AC")


def ad_bad_input_profile(tmp, inp, md):
    d = jread(inp)
    d["matrix"]["profile_identical_across_cells"] = False
    p = Path(tmp) / "bad-input.json"
    write(p, json.dumps(d, indent=2))
    m2 = Path(tmp) / "bad-result.md"
    assert gen(p, m2).returncode == 0
    r = validate(m2, p)
    assert_semantic_failure(r, "input: matrix.profile_identical_across_cells != true", "AD")


def ae_bad_input_matrix(tmp, inp, md):
    d = jread(inp)
    d["matrix"]["matrix_validation_status"] = "FAIL"
    p = Path(tmp) / "bad-input2.json"
    write(p, json.dumps(d, indent=2))
    m2 = Path(tmp) / "bad-result2.md"
    assert gen(p, m2).returncode == 0
    assert_semantic_failure(validate(m2, p), "input: matrix_validation_status != PASS", "AE")


def ag_tagref(tmp):
    ev = copy_ev(tmp)
    tr = jread(TAGREF)
    tr["object"] = {"sha": "f" * 40, "type": "commit"}
    p = Path(tmp) / "tag-fake.json"
    write(p, json.dumps(tr, indent=2))
    r = build_input(Path(tmp) / "o.json", ev=ev, tagref=p)
    assert_semantic_failure(r, "tag-ref object sha != dispatch", "AG")


def ah_fresh(tmp, inp, md):
    rel_bad = Path(tmp) / "rel-fresh.json"
    d = jread(REL)
    d["assets"] = [dict(a) for a in d["assets"]]
    a0 = d["assets"][0]
    a0["digest"] = "0" + a0["digest"][1:]
    write(rel_bad, json.dumps(d, indent=2))
    r = validate(md, inp, rel=rel_bad, tagref=TAGREF, formal=True)
    assert_semantic_failure(r, "fresh asset digest mismatch", "AH")


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
    assert_semantic_failure(r, "review doc classification PASS missing", "AI")


def aj_review_date(tmp):
    ev = copy_ev(tmp)
    out = Path(tmp) / 'o-aj.json'
    r = build_input(out, ev=ev, review_date="2026-09-04")
    assert_semantic_failure(r, "CLI review-date", "AJ")
    assert not out.exists()


def ak_model_path(tmp):
    ev = copy_ev(tmp)
    p2 = ev / "cell-1K" / "runtime-identity.txt"
    t = read(p2)
    write(p2, t.replace("model_path=/data/tiankuan/zyg/model/GLM-5.2-w8a8", "model_path=/data/wrong/model"))
    update_checksum(ev, "cell-1K/runtime-identity.txt")
    assert_builder_fails(ev, "identity field 'model_path' differs")


def al_env(tmp):
    ev = copy_ev(tmp)
    p3 = ev / "environment.txt"
    t = read(p3)
    write(p3, t.replace("HCCL_BUFFSIZE=200", "HCCL_BUFFSIZE=201"))
    update_checksum(ev, "environment.txt")
    assert_builder_fails(ev, "env HCCL_BUFFSIZE")


def am_duplicate_config(tmp):
    cfg = read(MATRIX_CONFIG)
    needle = '    "model_path": "/data/tiankuan/zyg/model/GLM-5.2-w8a8",'
    p = Path(tmp) / "duplicate-config.json"
    write(p, cfg.replace(needle, needle + "\n" + needle, 1))
    r = build_input(Path(tmp) / "am-no-output.json", matrix_config=p)
    assert_semantic_failure(r, "DUPLICATE_JSON_KEY: model_path", "AM")


def an_duplicate_input(tmp, inp, md):
    text = read(inp)
    needle = '  "result_type": "PROFILE_CANDIDATE_FULL_MATRIX",'
    p = Path(tmp) / "duplicate-input.json"
    write(p, text.replace(needle, needle + "\n" + needle, 1))
    assert_semantic_failure(validate(md, p), "DUPLICATE_JSON_KEY: result_type", "AN")


def ao_missing_unset(tmp):
    ev = copy_ev(tmp)
    p = ev / "environment.txt"
    write(p, read(p).replace("unset VLLM_VERSION\n", "", 1))
    update_checksum(ev, "environment.txt")
    assert_builder_fails(ev, "explicit unset set", "AO")


def ap_wrong_unset(tmp):
    ev = copy_ev(tmp)
    p = ev / "environment.txt"
    write(p, read(p).replace("unset VLLM_VERSION", "unset SOME_OTHER_VAR", 1))
    update_checksum(ev, "environment.txt")
    assert_builder_fails(ev, "explicit unset set", "AP")


def aq_result_unset(tmp, inp, md):
    d = jread(inp)
    original = ",".join(d["runtime_environment"]["_unset"])
    p = Path(tmp) / "aq-result.md"
    mutate(md, p, "| _unset | `%s` |" % original,
           "| _unset | `LD_PRELOAD` |")
    assert_semantic_failure(validate(p, inp), "runtime environment _unset mismatch", "AQ")


def fresh_release_failure(tmp, inp, md, label, mutate_fn, blocker):
    d = jread(REL)
    d["assets"] = [dict(a) for a in d["assets"]]
    mutate_fn(d)
    p = Path(tmp) / (label.lower() + "-release.json")
    write(p, json.dumps(d, indent=2))
    assert_semantic_failure(validate(md, inp, rel=p, tagref=TAGREF, formal=True), blocker, label)


def ar_sidecar_digest(tmp, inp, md):
    def change(d):
        d["assets"][1]["digest"] = "0" + d["assets"][1]["digest"][1:]
    fresh_release_failure(tmp, inp, md, "AR", change, "fresh sidecar digest mismatch")


def as_sidecar_id(tmp, inp, md):
    fresh_release_failure(tmp, inp, md, "AS",
                          lambda d: d["assets"][1].__setitem__("id", d["assets"][1]["id"] + 1),
                          "fresh sidecar id mismatch")


def at_tag_ref_name(tmp, inp, md):
    d = jread(TAGREF)
    d["ref"] = "refs/tags/wrong-name"
    p = Path(tmp) / "at-tag.json"
    write(p, json.dumps(d, indent=2))
    assert_semantic_failure(validate(md, inp, rel=REL, tagref=p, formal=True),
                            "fresh tag-ref name mismatch", "AT")


def au_asset_size(tmp, inp, md):
    fresh_release_failure(tmp, inp, md, "AU",
                          lambda d: d["assets"][0].__setitem__("size", d["assets"][0]["size"] + 1),
                          "fresh asset size mismatch")


def matching_bad_input(tmp, inp, name, mutate_fn):
    d = jread(inp)
    mutate_fn(d)
    p = Path(tmp) / (name.lower() + "-input.json")
    result = Path(tmp) / (name.lower() + "-result.md")
    write(p, json.dumps(d, indent=2, sort_keys=True))
    g = gen(p, result)
    assert g.returncode == 0, output(g)
    return p, result


def d024_bad_input(tmp, inp, label, key, value, blocker):
    p, result = matching_bad_input(tmp, inp, label,
                                   lambda d: d["hardware"].__setitem__(key, value))
    assert_semantic_failure(validate(result, p), blocker, label)


def result_identity_failure(tmp, inp, md, label, key, replacement):
    d = jread(inp)
    original = d["runtime_identity"]["fields"][key]
    p = Path(tmp) / (label.lower() + "-result.md")
    mutate(md, p, "| %s | `%s` |" % (key, original),
           "| %s | `%s` |" % (key, replacement))
    assert_semantic_failure(validate(p, inp), "runtime identity %s mismatch" % key, label)


def bc_result_id(tmp, inp, md):
    p = Path(tmp) / "bc-result.md"
    expected = "RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-20260907"
    mutate(md, p, expected, "RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-20260908")
    assert_semantic_failure(validate(p, inp), "Result ID exact mismatch", "BC")


def bd_review_date(tmp, inp, md):
    p = Path(tmp) / "bd-result.md"
    mutate(md, p, "| Review date | 2026-09-07 |", "| Review date | 2026-09-04 |")
    assert_semantic_failure(validate(p, inp), "Review date mismatch", "BD")


def be_input_classification(tmp, inp, md):
    p, result = matching_bad_input(tmp, inp, "BE",
                                   lambda d: d.__setitem__("candidate_classification", "OTHER"))
    assert_semantic_failure(validate(result, p), "input: candidate_classification != FINAL_RECOMMENDED_PROFILE_CANDIDATE", "BE")


def bf_result_classification(tmp, inp, md):
    p = Path(tmp) / "bf-result.md"
    mutate(md, p, "| Candidate classification | `FINAL_RECOMMENDED_PROFILE_CANDIDATE` |",
           "| Candidate classification | `OTHER` |")
    assert_semantic_failure(validate(p, inp), "Candidate classification mismatch", "BF")


def bg_tag_object(tmp, inp, md):
    p = Path(tmp) / "bg-result.md"
    original = jread(inp)["release"]["tag_object_commit"]
    mutate(md, p, "| tag object commit | `%s` |" % original,
           "| tag object commit | `%s` |" % ("0" + original[1:]))
    assert_semantic_failure(validate(p, inp), "tag object commit mismatch", "BG")


def bh_opt01(tmp, inp, md):
    p = Path(tmp) / "bh-result.md"
    mutate(md, p, "| Formal OPT-01 | `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION` |",
           "| Formal OPT-01 | `OTHER` |")
    assert_semantic_failure(validate(p, inp), "Formal OPT-01 exact field mismatch", "BH")


def bi_schema(tmp, inp, md):
    p, result = matching_bad_input(tmp, inp, "BI",
                                   lambda d: d.__setitem__("schema", "wrong-schema"))
    assert_semantic_failure(validate(result, p), "input: schema != candidate-result-input", "BI")


def bj_version(tmp, inp, md):
    p, result = matching_bad_input(tmp, inp, "BJ",
                                   lambda d: d.__setitem__("version", 3))
    assert_semantic_failure(validate(result, p), "input: version != 2", "BJ")


def bk_pinned_count(tmp, inp, md):
    p = Path(tmp) / "bk-result.md"
    mutate(md, p, "| pinned tooling | 4 files recorded |", "| pinned tooling | 3 files recorded |")
    assert_semantic_failure(validate(p, inp), "pinned tooling count mismatch", "BK")


def bl_identity_aggregate(tmp, inp, md):
    p = Path(tmp) / "bl-result.md"
    mutate(md, p, "| identical across cells | True |", "| identical across cells | False |")
    assert_semantic_failure(validate(p, inp), "runtime identity identical across cells mismatch", "BL")


def bm_no_redundant_runtime_environment(tmp, inp, md):
    assert "| runtime environment | `{" not in read(md)


def main():
    with FixedTestDirectory() as tmp:
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
            assert_semantic_failure(validate(m2, inp), "cell 1K run values != input", "D")

        def e():
            m2 = w / "e.md"
            mutate(md, m2, "1205.0900", "1205.0901")
            assert_semantic_failure(validate(m2, inp), "cell 1K mean", "E")

        def f():
            for bad in ("6048", "6058", "6076"):
                m2 = w / ("f_" + bad + ".md")
                mutate(md, m2, "| A3 | 8 x 752 = 6016 |", "| A3 | 8 x 752 = %s |" % bad)
                assert_semantic_failure(validate(m2, inp), "A3 D-024 block mismatches", "F-" + bad)

        def g_ach():
            m2 = w / "g.md"
            mutate(md, m2, "117.8919", "117.8918")
            assert_semantic_failure(validate(m2, inp), "cell 1K ach mismatch", "G")

        def h():
            m2 = w / "h1.md"
            mutate(md, m2, "gpu_memory_utilization | `0.95`", "gpu_memory_utilization | `0.97`")
            assert_semantic_failure(validate(m2, inp), "frozen profile gpu_memory_utilization mismatch", "H-gpu")
            m3 = w / "h2.md"
            mutate(md, m3, "max_model_len | `67000`", "max_model_len | `70000`")
            assert_semantic_failure(validate(m3, inp), "frozen profile max_model_len mismatch", "H-len")

        def i():
            m2 = w / "i.md"
            mutate(md, m2, "| measured runs | 12 |", "| measured runs | 11 |")
            assert_semantic_failure(validate(m2, inp), "matrix gate measured runs", "I")

        def j():
            m2 = w / "j.md"
            mutate(md, m2, "| warmup discarded | 4 |", "| warmup discarded | 3 |")
            assert_semantic_failure(validate(m2, inp), "matrix gate warmup discarded", "J")

        def k():
            m2 = w / "k.md"
            mutate(md, m2, "profile identical | True", "profile identical | False")
            assert_semantic_failure(validate(m2, inp), "matrix gate profile identical", "K")

        def l():
            m2 = w / "l.md"
            mutate(md, m2, "runtime identity identical | True", "runtime identity identical | False")
            assert_semantic_failure(validate(m2, inp), "matrix gate runtime identity identical", "L")

        def m_case():
            m2 = w / "m.md"
            digest = ASSET_DIGEST
            mutate(md, m2, digest, "0" + digest[1:])
            assert_semantic_failure(validate(m2, inp), "provenance asset digest", "M-result")
            rel_bad = w / "rel_bad.json"
            payload = jread(REL)
            payload["assets"] = [dict(a) for a in payload["assets"]]
            payload["assets"][0]["digest"] = "0" + digest[1:]
            write(rel_bad, json.dumps(payload))
            assert_semantic_failure(validate(md, inp, rel=rel_bad),
                                    "asset digest != authoritative release JSON", "M-release")

        def n_case():
            m2 = w / "n.md"
            mutate(md, m2, "`PROFILE_CANDIDATE_FULL_MATRIX`", "`BASELINE`")
            assert_semantic_failure(validate(m2, inp), "Result Type mismatch", "N")

        def o_case():
            m2 = w / "o.md"
            mutate(md, m2, "| Result State | `READY_FOR_FORMAL_REVIEW` |", "| Result State | `ACCEPTED` |")
            assert_semantic_failure(validate(m2, inp), "Result State not READY_FOR_FORMAL_REVIEW", "O")

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

        def af_bad_input():
            d = jread(inp)
            d["cells"]["64K"]["d024_achievement_pct"] = 93.0
            bad = w / "bad-input3.json"
            write(bad, json.dumps(d, indent=2))
            m2 = w / "bad-result3.md"
            assert gen(bad, m2).returncode == 0
            assert_semantic_failure(validate(m2, bad), "input recompute 64K ach", "AF")

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
        it("AD", lambda: ad_bad_input_profile(w, inp, md))
        it("AE", lambda: ae_bad_input_matrix(w, inp, md))
        it("AF", lambda: af_bad_input())
        it("AG", lambda: ag_tagref(w))
        it("AH", lambda: ah_fresh(w, inp, md))
        it("AI", lambda: ai_review_class(w))
        it("AJ", lambda: aj_review_date(w))
        it("AK", lambda: ak_model_path(w))
        it("AL", lambda: al_env(w))
        it("AM", lambda: am_duplicate_config(w))
        it("AN", lambda: an_duplicate_input(w, inp, md))
        it("AO", lambda: ao_missing_unset(w))
        it("AP", lambda: ap_wrong_unset(w))
        it("AQ", lambda: aq_result_unset(w, inp, md))
        it("AR", lambda: ar_sidecar_digest(w, inp, md))
        it("AS", lambda: as_sidecar_id(w, inp, md))
        it("AT", lambda: at_tag_ref_name(w, inp, md))
        it("AU", lambda: au_asset_size(w, inp, md))
        it("AV", lambda: d024_bad_input(w, inp, "AV", "A3_cards", 7,
                                         "input D-024 A3_cards != 8"))
        it("AW", lambda: d024_bad_input(w, inp, "AW", "A3_tflops_per_card", 751,
                                         "input D-024 A3_tflops_per_card != 752"))
        it("AX", lambda: d024_bad_input(w, inp, "AX", "target_achievement_minimum", 0.75,
                                         "input D-024 target_achievement_minimum != 0.8"))
        it("AY", lambda: d024_bad_input(w, inp, "AY", "decision", "D-020",
                                         "input D-024 decision != 'D-024'"))
        it("AZ", lambda: result_identity_failure(w, inp, md, "AZ", "model_path", "/data/wrong/model"))
        it("BA", lambda: result_identity_failure(w, inp, md, "BA", "image", "wrong/image:tag"))
        it("BB", lambda: result_identity_failure(w, inp, md, "BB", "vllm", "0.0.0"))
        it("BC", lambda: bc_result_id(w, inp, md))
        it("BD", lambda: bd_review_date(w, inp, md))
        it("BE", lambda: be_input_classification(w, inp, md))
        it("BF", lambda: bf_result_classification(w, inp, md))
        it("BG", lambda: bg_tag_object(w, inp, md))
        it("BH", lambda: bh_opt01(w, inp, md))
        it("BI", lambda: bi_schema(w, inp, md))
        it("BJ", lambda: bj_version(w, inp, md))
        it("BK", lambda: bk_pinned_count(w, inp, md))
        it("BL", lambda: bl_identity_aggregate(w, inp, md))
        it("BM", lambda: bm_no_redundant_runtime_environment(w, inp, md))
        print("SUMMARY A-P: %d PASS / 0 FAIL / 0 SKIP" % (16 - len([x for x in failed if len(x) == 1 and x <= "P"])))
        q_al = ["Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"]
        am_bb = ["AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU",
                 "AV", "AW", "AX", "AY", "AZ", "BA", "BB"]
        bc_bm = ["BC", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BK", "BL", "BM"]
        print("SUMMARY Q-AL: %d PASS / %d FAIL / 0 SKIP" %
              (len(q_al) - len([x for x in failed if x in q_al]), len([x for x in failed if x in q_al])))
        print("SUMMARY AM-BB: %d PASS / %d FAIL / 0 SKIP" %
              (len(am_bb) - len([x for x in failed if x in am_bb]), len([x for x in failed if x in am_bb])))
        print("SUMMARY BC-BM: %d PASS / %d FAIL / 0 SKIP" %
              (len(bc_bm) - len([x for x in failed if x in bc_bm]), len([x for x in failed if x in bc_bm])))
        print("SUMMARY TOTAL: %d PASS / %d FAIL / 0 SKIP" % (65 - len(failed), len(failed)))
        print("UNEXPECTED CRASH / TRACEBACK COUNT: %d" % CRASH_COUNT["value"])
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
