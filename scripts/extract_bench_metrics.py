#!/usr/bin/env python3
"""Deterministic vllm bench serve log -> metrics.json extractor (FIXED).

D-023 extension for Profile Candidate Full-Matrix validation:
  RAW SOURCE        : runN.log (bench stdout, immutable)
  MACHINE DERIVED   : runN.metrics.json

Fixes over the first version:
  * labels that carry units in parentheses are parsed, e.g.
      "Total token throughput (tok/s):   1760.92"
      "Mean TTFT (ms): 2064099.81"
    (the old regex expected the number right after the label, which the
    "(tok/s)" / "(ms)" unit always broke -> all those fields came back null)
  * --strict: any required field missing/unparsable = exit 1 (fail-closed).

Determinism contract: no timestamps; the same log always yields the same
JSON bytes. Usage:
  python scripts/extract_bench_metrics.py <runN.log> [--out <runN.metrics.json>] [--strict]
"""

import sys

from bench_common import (
    parse_log,
    required_missing,
    write_json_deterministic,
)


def run(argv):
    args = [a for a in argv if a != "--strict"]
    strict = "--strict" in argv
    if len(args) < 1:
        print(__doc__, file=sys.stderr)
        return 2
    log = args[0]
    out = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            print("--out requires a path", file=sys.stderr)
            return 2
        out = args[i + 1]

    metrics = parse_log(log)
    missing = required_missing(metrics)
    if strict and missing:
        for key in missing:
            print("MISSING REQUIRED FIELD: %s" % key, file=sys.stderr)
        print("STRICT_EXTRACTION_FAILED %s" % log, file=sys.stderr)
        return 1
    if out:
        write_json_deterministic(out, metrics)
    print(json_dump(metrics))
    return 0


def json_dump(metrics):
    import json

    return json.dumps(metrics, indent=2, sort_keys=True)


def main(argv=None):
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())