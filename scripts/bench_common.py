#!/usr/bin/env python3
"""Shared deterministic parsing/config for the Full-Matrix candidate tooling.

D-023 machine-gate extension (Profile-level Full-Matrix Candidate Validation):
  RAW SOURCE      : runN.log (immutable bench stdout) + runN.command.txt (canonical argv)
  MACHINE DERIVED : runN.metrics.json / validation.json / aggregation.json / matrix-validation.json

Determinism contract:
  * No timestamps, no random values, no wall-clock input in any derived JSON.
  * Same input files ALWAYS yield byte-identical derived JSON.
Fail-closed contract:
  * Any required metric field missing/unparsable = hard failure by the caller.
  * vLLM bench labels carry units in parentheses, e.g.
      "Total token throughput (tok/s):    1760.92"
    and the parser below handles that form (the previous regex did not).
"""

import io
import json
import re
from pathlib import Path

# (json_key, [label alternates], kind) — labels are matched at line start so
# "Peak output token throughput (tok/s): " can never shadow "Output token throughput (tok/s): ".
FIELDS = [
    ("successful_requests", ["Successful requests", "Total completed"], "int"),
    ("failed_requests", ["Failed requests", "Total failed"], "int"),
    ("benchmark_duration_s", ["Benchmark duration"], "float"),
    ("total_input_tokens", ["Total input tokens"], "int"),
    ("total_output_tokens", ["Total generated tokens", "Total output tokens"], "int"),
    ("request_throughput", ["Request throughput"], "float"),
    ("output_token_throughput", ["Output token throughput"], "float"),
    ("total_token_throughput", ["Total token throughput"], "float"),
    ("mean_ttft_ms", ["Mean TTFT"], "float"),
    ("p99_ttft_ms", ["P99 TTFT"], "float"),
    ("mean_tpot_ms", ["Mean TPOT"], "float"),
    ("p99_tpot_ms", ["P99 TPOT"], "float"),
    ("mean_itl_ms", ["Mean ITL"], "float"),
    ("p99_itl_ms", ["P99 ITL"], "float"),
]

REQUIRED_KEYS = [k for k, _labels, _kind in FIELDS]


def bench_labels():
    """Ordered list of (label, kind) used when re-checking required coverage."""
    return [(label, kind) for _key, labels, kind in FIELDS for label in labels]


def required_missing(metrics):
    """Keys that are missing or non-finite in a parsed metrics dict."""
    import math

    bad = []
    for key in REQUIRED_KEYS:
        v = metrics.get(key)
        if v is None:
            bad.append(key)
        elif isinstance(v, float) and not math.isfinite(v):
            bad.append(key)
    return bad


def parse_log(path):
    """Deterministic metrics dict from a raw bench log (None for missing fields)."""
    text = io.open(path, encoding="utf-8", errors="replace").read()
    return parse_bench_text(text)


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json_deterministic(path, obj):
    """json.dumps(sort_keys=True, indent=2) with a fixed trailing newline and no
    platform line-ending translation (byte-deterministic across OSes)."""
    js = json.dumps(obj, indent=2, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(js + "\n")
    return js


def json_bytes(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_file(path):
    import hashlib

    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_matrix_config(path):
    """Matrix workload/normalization contract from candidate-matrix-config.json.

    All baseline/delta/achievement authoritative inputs come from this Control
    artifact (itself derived from the accepted baseline Results and D-024 yaml);
    validators never hardcode values.
    """
    cfg = read_json(path)
    for cell in ("1K", "4K", "16K", "64K"):
        if cell not in cfg.get("cells", {}):
            raise ValueError("matrix config missing cell %s" % cell)
    hw = cfg.get("hardware", {})
    for key in ("A3_total_tflops", "H100_total_tflops", "target_achievement_minimum"):
        if key not in hw:
            raise ValueError("matrix config missing hardware.%s" % key)
    if hw["A3_total_tflops"] != 6016 or hw["H100_total_tflops"] != 15824:
        raise ValueError("matrix config must use exact D-024 basis 6016 / 15824")
    wl = cfg.get("workload_contract", {})
    for key in ("max_concurrency", "num_prompts", "random_range_ratio",
                "request_rate", "endpoint", "dataset", "ignore_eos"):
        if key not in wl:
            raise ValueError("matrix config missing workload_contract.%s" % key)
    return cfg


def expected_successful(cfg):
    return int(cfg["workload_contract"]["num_prompts"])


def contract_problems(command_tokens, cell, cfg):
    """Fail-closed contract check of the canonical argv for one cell.

    ``command_tokens``: JSON list from runN.command.txt. Every required
    flag/value pair must be present in order (argv positional semantics).
    """
    cell_cfg = cfg["cells"][cell]
    wl = cfg["workload_contract"]
    exp_in = int(cell_cfg["input_len"])
    exp_out = int(cell_cfg["output_len"])
    problems = []

    pairs = [
        ("--backend", str(wl["backend"])),
        ("--dataset-name", str(wl["dataset"])),
        ("--random-input-len", str(exp_in)),
        ("--random-output-len", str(exp_out)),
        ("--random-range-ratio", str(wl["random_range_ratio"])),
        ("--request-rate", str(wl["request_rate"])),
        ("--max-concurrency", str(wl["max_concurrency"])),
        ("--num-prompts", str(wl["num_prompts"])),
        ("--endpoint", str(wl["endpoint"])),
    ]
    for flag, want in pairs:
        try:
            i = command_tokens.index(flag)
        except ValueError:
            problems.append("flag %s missing" % flag)
            continue
        nxt = command_tokens[i + 1] if i + 1 < len(command_tokens) else None
        if nxt != want:
            problems.append("%s value %r != expected %r" % (flag, nxt, want))
    if "--ignore-eos" not in command_tokens:
        problems.append("flag --ignore-eos missing")
    return problems


def _to_number(raw: str, kind: str):
    """'1,234.56' -> 1234.56 (float) / 1234 (int)."""
    cleaned = raw.replace(",", "")
    if kind == "int":
        return int(cleaned.split(".")[0])
    return float(cleaned)


def line_value(text, label):
    """Value of ``label`` in a bench result line; tolerant of a unit in parens.

    Anchored to start-of-line so a longer sibling label (e.g. "Peak output
    token throughput") can never shadow the exact label.
    """
    m = re.search(
        r"^\s*" + re.escape(label) + r"(?:\s*\([^)\n]*\))?\s*[:=]\s*([0-9][0-9.,]*)",
        text,
        re.M,
    )
    return m.group(1) if m else None


def parse_bench_text(text, label_kind_pairs=FIELDS):
    """Extract every metric; a value that is absent/unparseable becomes None."""
    out = {}
    for key, labels, kind in label_kind_pairs:
        out[key] = None
        for label in labels:
            raw = line_value(text, label)
            if raw is None:
                continue
            try:
                out[key] = _to_number(raw, kind)
            except ValueError:
                out[key] = None
            if out[key] is not None:
                break
    return out