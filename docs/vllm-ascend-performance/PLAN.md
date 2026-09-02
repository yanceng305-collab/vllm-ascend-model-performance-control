# Project Plan

## Model-Specific Execution Modes

**GLM-5.2-W8A8 (Decision D-019)**: Has a User-verified known-good baseline. Execution mode is **FAST PREFLIGHT → RUN FROZEN COMMANDS/SCRIPTS → EVIDENCE → RESULT → OPTIMIZATION**. Stage 0 discovery capability is retained for new servers/hardware but does not gate GLM performance work.

**DeepSeek-V4-Flash-W8A8, MiniMax-M3, and future unverified models**: Use the discovery-first flow (Stage 0A → Stage 0B → Stage 1+).

## Stage 0A: Environment / Host / Container Fact Acquisition

A3PerfRunner performs a dispatched, read-only, non-destructive discovery of the single-node A3/910C target (8 cards / 16 NPU chips), host/runtime tuple, existing images and containers, required host mounts, workspace capacity, and aligned-version readiness. Stage 0A does not require model downloads to be complete. Gate: an immutable environment Result records `ENV_READY`, `ENV_PREPARATION_REQUIRED`, or `ENV_BLOCKED` and the evidence-based next step.

**Applicability**: Required for DeepSeek/MiniMax and new environments. Optional for GLM on known-good hardware (per D-019).

## Stage 0B: Model Identity / Compatibility Completion

After model downloads are complete enough for inspection, A3PerfRunner performs a separate read-only discovery under the fixed `MODEL_ROOT` for DeepSeek-V4-Flash-W8A8 and MiniMax-M3. A model directory that is present but incomplete is `DOWNLOAD_IN_PROGRESS`; it does not block 0A or a separately authorized Stage 1 preparation, but 0B remains deferred. Gate: model-scoped immutable Results record `MODEL_READY`, `DOWNLOAD_IN_PROGRESS`, `MODEL_MISSING`, or `MODEL_IDENTITY_UNKNOWN`, plus pinned-runtime recognition and next stage.

**Applicability**: Required for DeepSeek/MiniMax. Not required for GLM-5.2-W8A8 which has frozen baseline artifacts (per D-019). DeepSeek-V4-Pro-W8A8 remains a multi-node candidate and is excluded from current single-A3 Stage 0 scope.

## Bootstrap prerequisite

Control structure, public-source evidence, benchmark contract, normalization policy, source records, and model placeholders are maintained continuously. 

For **DeepSeek-V4-Flash-W8A8, MiniMax-M3, and future unverified models**, no performance execution-ready Task is created before their respective Stage 0 discovery gates are satisfied.

**GLM-5.2-W8A8** operates under Decision D-019 User-verified known-good baseline and is not subject to this discovery-first prerequisite.

## Stage 1: FlagOS-aligned runtime preparation

Only if Stage 0A proves the aligned environment is absent or incomplete. Stateful installation, image pull, container creation, image rebuild, or upgrade requires a separate Task with complete commands and explicit User authorization. Stage 1 is not READY in the current Control state.

## Stage 2: Model launch / load correctness

A3PerfRunner executes an explicitly dispatched Task covering the frozen native vLLM-Ascend runtime and bounded model loading checks. The Task must include the complete launch, readiness, logging, and cleanup commands. Gate: immutable Result and independent Review.

**For GLM**: Uses frozen baseline commands from `models/glm-5.2-w8a8/RUNBOOK.md` and `scripts/`.

## Stage 3: Functional smoke

Run bounded service/function checks before performance. The Task must include complete endpoint/request, expected-result, timeout, evidence-capture, and cleanup commands. Gate: immutable Result and independent Review.

## Stage 4: Performance baseline

Run the frozen workload and repetitions. The Task must include complete `vllm bench serve` commands or a deterministic command-generation rule for every cell. Preserve raw Ascend values, raw H100 references, comparison class, exact normalization inputs, and calculation outputs. Gate: per-cell `PASS`, `FAIL`, or `NOT COMPARABLE` plus Review.

**For GLM**: Uses frozen benchmark matrix from `scripts/bench-glm52-matrix.sh` (1K/4K/16K/64K input, 1024 output, C64).

## Stage 5: Performance optimization / retest

Optimization and retest are separate bounded Tasks. Each Task must list changed parameters and complete re-test commands; Stage 4 Results are never overwritten. Any changed identity requires a new Decision and Result chain.

## Stage 6: Formal performance acceptance

PerfControl independently reviews the immutable Result, comparison class, exact normalization, and claim boundary. Accepted identity and Evidence pointers become the reusable native baseline.

Performance claims are never extended from one cell to untested cells.
