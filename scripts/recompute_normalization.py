#!/usr/bin/env python3
"""Deterministic GLM-5.2-W8A8 normalization recompute (D-024 basis 752/6016)."""

import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "docs/vllm-ascend-performance/hardware-normalization-config.yaml"
MCFG = ROOT / "docs/vllm-ascend-performance/model-workload-references.yaml"
OLD = ROOT / "docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/CORRECTION-SUPPLEMENT-BASELINE-EVIDENCE-run-20260902-140958.md"
OUT = ROOT / "docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902.md"


def load_yaml(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def grab(text, pat):
    m = re.search(pat, text)
    return m.group(1).strip() if m else "UNKNOWN"


def main():
    cfg = load_yaml(CFG)
    mcfg = load_yaml(MCFG)
    text = OLD.read_text(encoding="utf-8")

    a3_cards = int(cfg["a3"]["cards"])
    a3_per = int(cfg["a3"]["tflops_per_card_fp16"])
    a3_total = int(cfg["a3"]["total_tflops"])
    h1_cards = int(cfg["h100"]["cards"])
    h1_per = int(cfg["h100"]["tflops_per_card_fp8"])
    h1_total = int(cfg["h100"]["total_tflops"])
    target_min = float(cfg["normalization"]["target_achievement_minimum"])

    h100 = {}
    for w in mcfg["models"]["GLM-5.2-W8A8"]["h100_references"].values():
        h100[w["cell_name"]] = float(w["throughput_tok_s"])

    raw = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*(\w+)\s*\|\s*\*{0,2}([\d.]+)\*{0,2}\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)%\s*\|", line)
        if m:
            raw[m.group(1)] = float(m.group(2))
    assert all(k in raw for k in ["1K", "4K", "16K", "64K"]), raw

    dispatch = grab(text, r"DISPATCH_CONTROL_SHA[^a-f0-9]*([a-f0-9]{40})")
    arch_sha = grab(text, r"Archive\s+SHA256[^0-9a-f]{0,30}([0-9a-f]{64})")
    arch_name = grab(text, r"(GLM52-W8A8-BASELINE-EVIDENCE-run-[-\w.]+\.tar\.gz)")
    loc = grab(text, r"Evidence Location[^`]*`([^`]+)`")

    cells = ["1K", "4K", "16K", "64K"]
    res = {}
    R = a3_total / h1_total
    for c in cells:
        a3n = raw[c] / a3_total
        hn = h100[c] / h1_total
        ach = (a3n / hn) * 100
        equiv = h100[c] * R
        t80 = equiv * target_min
        disp = "MEETS TARGET" if ach >= target_min * 100 else "BELOW TARGET"
        res[c] = dict(a3=raw[c], h100=h100[c], a3n=a3n, hn=hn, ach=ach, equiv=equiv, t80=t80, disp=disp)

    manual16 = 960.45
    base16 = raw["16K"]
    delta16 = (manual16 / base16 - 1) * 100

    print("A3_CARDS=%d A3_PER_CARD=%d A3_TOTAL=%d" % (a3_cards, a3_per, a3_total))
    print("H_CARDS=%d H_PER=%d H_TOTAL=%d" % (h1_cards, h1_per, h1_total))
    print("R=%.6f TARGET_MIN=%.2f" % (R, target_min))
    for c in cells:
        r = res[c]
        print((c + "=RAW %.2f H100 %.2f T80 %.2f ACH %.4f%% DISP %s") % (r["a3"], r["h100"], r["t80"], r["ach"], r["disp"]))
    print("MANUAL16_DELTA_PCT %.6f" % delta16)
    print("MANUAL16_RAW %.2f ACCEPTED16 %.2f" % (manual16, base16))
    print("DISPATCH %s" % dispatch)
    print("ARCHIVE_SHA %s" % arch_sha)
    print("ARCHIVE_NAME %s" % arch_name)
    print("EVID_LOC %s" % loc)

    lines = []
    lines.append("# Correction Supplement: GLM-5.2-W8A8 Hardware Normalization (D-024)")
    lines.append("")
    lines.append("**Supplement ID**: `CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902`")
    lines.append("**Correction Date**: 2026-09-02")
    lines.append("**Created By**: PerfControl (machine-driven)")
    lines.append("")
    lines.append("**Correction cause**: User corrected a wrong hardware compute input.")
    lines.append("")
    lines.append("## Basis change")
    lines.append("")
    lines.append("- old basis = 756 x 8 = 6048 (D-020, now SUPERSEDED for A3 compute)")
    lines.append("- new basis = 752 x 8 = 6016 (D-024, active)")
    lines.append("- H100 unchanged = 989 x 16 = 15824")
    lines.append("- measured A3 = 6019.718 (evidence/reference only; not the denominator)")
    lines.append("")
    lines.append("## Derived values (machine-computed from config + accepted raw data)")
    lines.append("")
    lines.append("| Cell | A3 raw (tok/s) | H100 ref (tok/s) | 80% target A3 (tok/s) | Achievement | Disposition |")
    lines.append("|---|---|---|---|---|---|")
    for c in cells:
        r = res[c]
        lines.append("| %s | %.2f | %.2f | %.2f | %.2f%% | %s |" % (c, r["a3"], r["h100"], r["t80"], r["ach"], r["disp"]))
    lines.append("")
    lines.append("## Unchanged provenance")
    lines.append("")
    lines.append("- raw benchmark throughput: unchanged")
    lines.append("- Evidence archive: %s" % arch_name)
    lines.append("- archive SHA256: %s" % arch_sha)
    lines.append("- runtime identity: unchanged")
    lines.append("- original Result documents: immutable")
    lines.append("- old correction supplement: immutable")
    lines.append("- D-024 supersedes D-020 for A3 compute basis")
    lines.append("- active values shall use D-024 basis 6016")
    lines.append("- DISPATCH_CONTROL_SHA: %s" % dispatch)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("WROTE %s" % OUT.name)


if __name__ == "__main__":
    main()