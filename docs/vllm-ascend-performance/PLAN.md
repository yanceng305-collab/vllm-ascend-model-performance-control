# Project Plan

## Stage 0: Server Fact Acquisition / Compatibility Discovery

Codex2 performs a dispatched, read-only, non-destructive discovery of hardware, runtime tuple, model identity, installed capabilities, and aligned-version readiness. Gate: immutable discovery Result answers the required questions in `methodology/SERVER-FACT-ACQUISITION.md`.

## Bootstrap prerequisite

Control structure, public-source evidence, benchmark contract, normalization policy, source records, and model placeholders are maintained continuously. No performance execution-ready Task is created before Stage 0.

## Stage 1: FlagOS-aligned runtime preparation

Only if Stage 0 proves the aligned environment is absent. Stateful installation, image rebuild, or upgrade requires a separate Task and explicit User authorization.

## Stage 2: Model launch / load correctness

Codex2 executes an explicitly dispatched Task covering the frozen native vLLM-Ascend runtime and bounded model loading checks. Gate: immutable Result and independent Review.

## Stage 3: Functional smoke

Run bounded service/function checks before performance. Gate: immutable Result and independent Review.

## Stage 4: Performance baseline

Run the frozen workload and repetitions. Preserve raw Ascend values, raw H100 references, comparison class, exact normalization inputs, and calculation outputs. Gate: per-cell `PASS`, `FAIL`, or `NOT COMPARABLE` plus Review.

## Stage 5: Performance optimization / retest

Optimization and retest are separate bounded Tasks. Any changed identity requires a new Decision and Result chain.

## Stage 6: Formal performance acceptance

Codex1 independently reviews the immutable Result, comparison class, exact normalization, and claim boundary. Accepted identity and Evidence pointers become the reusable native baseline.

Performance claims are never extended from one cell to untested cells.
