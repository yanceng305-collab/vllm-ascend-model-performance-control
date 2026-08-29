# Immutable Result Template

**Result ID:** `RESULT-...`

**Task / Run ID:** `...`

**Track:** `FLAGOS_ALIGNED | LATEST_REFERENCE` (newer lane must also say `NON_FLAGOS_ALIGNED_REFERENCE`)

**Experiment status:** `PASS | FAIL | STOP | PARTIAL`

## Exact identity

Record model revision/SHA, quantization, runtime versions, image/container digest, hardware/SKU/device count, topology, TP/DP/EP, launch command/config, benchmark tool/version, and contract cell.

## Evidence pointers

1. Code/runtime source pointer.
2. Control Task/Result/Review pointer.
3. Server Evidence root, manifest, and checksums.

## Raw and normalized performance

| Field | Value |
|---|---|
| H100 raw metric / unit | |
| Ascend raw metric / unit | |
| H100 compute basis and source | |
| Ascend compute basis and source | |
| Comparison class | `STRICT_REFERENCE | ENGINEERING_REFERENCE | NOT_COMPARABLE` |
| Direction / gate class | |
| Compute ratio `R` | |
| Normalized equivalent | |
| 80% target / allowed maximum | |
| Exact achievement | |
| Cell disposition | `PASS | FAIL | NOT_COMPARABLE` |

Use unrounded values for disposition. Preserve differences, missing inputs, first blocker, and uncovered scope. This file is immutable after first publication; corrections are supplements or new Results.
