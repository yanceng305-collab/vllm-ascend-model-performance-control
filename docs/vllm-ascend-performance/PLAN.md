# Project Plan

## Stage 0: Control bootstrap

Create repository structure, roles, evidence rules, benchmark contract, normalization policy, source records, and model placeholders. Gate: no execution-ready Task.

## Stage 1: Input freeze

User approves the benchmark method, H100 reference cells, model identities, runtime inventory, hardware identities, and comparable compute bases. Gate: every intended cell is either comparable with complete inputs or explicitly `NOT COMPARABLE`.

## Stage 2: Native runtime correctness

Codex2 executes only an explicitly dispatched Task covering the frozen native vLLM-Ascend runtime and bounded correctness checks. Gate: immutable Result and independent Review.

## Stage 3: Performance cells

Run the frozen workload and repetitions. Preserve raw Ascend values, raw H100 references, exact normalization inputs, and calculation outputs. Gate: per-cell `PASS`, `FAIL`, or `NOT COMPARABLE` plus Review.

## Stage 4: Accepted baseline and handoff

Freeze the accepted identity and Evidence pointers for future migration repositories. Any changed identity requires a new Decision and Result chain.

Performance claims are never extended from one cell to untested cells.
