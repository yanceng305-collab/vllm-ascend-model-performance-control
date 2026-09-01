# vLLM-Ascend Model Performance Control

## Mission

This repository is the Control plane for accepted native vLLM-Ascend model correctness and performance baselines on Ascend hardware. It is not a FlagOS implementation or model fork.

## Reading order

1. `README.md`
2. `docs/vllm-ascend-performance/STATUS.md`
3. `docs/vllm-ascend-performance/PLAN.md`
4. `docs/vllm-ascend-performance/DECISIONS.md`
5. `docs/vllm-ascend-performance/methodology/`
6. the relevant model directory

## Roles and authorization

- **User** owns model/runtime/hardware decisions, source materials, server authorization, acceptance policy, and explicit dispatch.
- **PerfControl** (formerly Codex1) maintains this Control repo, contracts, targets, Tasks, Reviews, and stage gates. PerfControl does not run A3/NPU performance tests by default.
- **A3PerfRunner** (formerly Codex2) may inventory servers, launch runtimes, benchmark, collect server Evidence, and publish an immutable Result only after receiving a `READY` Task and explicit User dispatch.
- **ChatGPT** provides independent review and coordination; it is not the formal Acceptance authority.

**Historical naming**: "Codex1" is PerfControl's historical alias; "Codex2" is A3PerfRunner's historical alias. Existing immutable Results, submitted prompts, and Evidence pointers retain their original naming. All active/current documentation uses the formal names PerfControl and A3PerfRunner.

`READY` is documentation readiness, not authorization. No execution occurs without explicit User dispatch.

## Evidence and immutability

Every formal run must preserve independent pointers to: (1) code/runtime source identity, (2) Control Task/Result/Review, and (3) server Evidence root and manifest. A3PerfRunner's first `RESULT-*.md` snapshot is immutable. Corrections or additional evidence are supplements or new Results; execution history is never rewritten. PerfControl Acceptance updates only the result index, status, Review, and Decision records.

## Scope boundaries

Do not commit model weights, images, large raw logs, profiling files, credentials, secrets, or server-local build output. Keep stable Evidence pointers, small manifests, checksums, contracts, Results, Reviews, and Decisions.

Do not guess model paths, SHAs, vLLM/vLLM-Ascend/CANN versions, hardware SKU, card count, TP/DP/EP, image, compute basis, or benchmark parameters. Public unknowns are researched by PerfControl; server-observable unknowns are tracked as `PENDING_A3PERFRUNNER_DISCOVERY`; only genuine User decisions or inaccessible private materials use `UNKNOWN / USER INPUT REQUIRED`.

Public facts are PerfControl-owned research: official version matrices, release notes, model registries, support lists, hardware specifications, commits, tags, issues, and PRs. Server-observable facts are A3PerfRunner-owned discovery: devices, runtime packages, containers, model files/configuration, capability probes, and topology. Mark these `PENDING_A3PERFRUNNER_DISCOVERY`, not User input. User decisions are limited to acceptance policy, private materials, engineering-reference approval, dispatch, stateful-change authorization, and unresolved business choices.

## Workspace and command rules

Server project roots are fixed: `WORK_ROOT=/data/tiankuan/zyg`, `MODEL_ROOT=/data/tiankuan/zyg/model`, `EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`, and `TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control`. A3PerfRunner must inspect model directories only under `MODEL_ROOT`; it must not search the whole server or guess subdirectory names. Model download state is independent from environment readiness.

The Single-A3 container contract is defined in `methodology/SINGLE-A3-CONTAINER-CONTRACT.md`. Do not use `/data:/data` or `/root/.cache:/root/.cache`. From Stage 1 onward, formal execution Tasks must include complete commands under `methodology/EXECUTION-COMMAND-COMPLETENESS.md`; A3PerfRunner may not improvise core commands or permanently alter the contract.

Stage 0A is environment-only and is the sole READY discovery Task. Stage 0B is deferred until downloads are complete enough for model inspection. Follow `methodology/MODEL-HASH-POLICY.md`: never hash large weights while downloads are active.

## Prompt-as-Control-Artifact

Any long A3PerfRunner dispatch prompt must be committed as a Markdown file in this repository before handoff. The committed GitHub file is the formal version and must bind the repository, Task ID/path, prompt path, Control commit, scope, allowed/prohibited actions, expected outputs, Evidence, and Result rules. PerfControl must not use terminal-only prompt text as the handoff. After push, ChatGPT independently live-queries and reviews the committed Task/prompt before returning it to User for A3PerfRunner dispatch.

Do not operate A3/NPU servers, install runtime packages, start models, or run benchmarks as part of repository bootstrap.
