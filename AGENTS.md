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
- **PerfControl** (formerly Codex1) is the sole writer of the formal GitHub Control repo: it maintains the Control repo, GitHub, contracts, targets, Tasks, Prompts, STATUS/INDEX, Result documents, Reviews, Decisions, Formal Acceptance, commit, and push. PerfControl does not run A3/NPU performance tests.
- **A3PerfRunner** (formerly Codex2) is execution-and-Evidence-only: it executes dispatched server Tasks, inspects/operates containers, benchmarks only when a Task explicitly authorizes it, collects raw data and runtime identity, computes SHA256, and produces the Evidence manifest/summary/bundle. Per Decision D-022, A3PerfRunner may upload immutable Evidence bundles as GitHub Release Assets (transport/storage channel only). It does not commit the Control repo, does not push GitHub (except Release Assets per D-022), does not require server Git SHA parity with Control, does not perform Formal Acceptance, and does not author formal GitHub Results.
- **ChatGPT** provides independent review and coordination; it is not the formal Acceptance authority.

**DISPATCH_CONTROL_SHA** identifies the formal Control Task version for a Runner execution. PerfControl verifies it locally before dispatch (`local Control HEAD == origin/main == DISPATCH_CONTROL_SHA`); the Runner only records it in Evidence provenance and does not require a local Control repo or server Git parity.

**Result authorship split**: Runner produces Evidence; PerfControl produces formal Results. After receiving Evidence, PerfControl independently reproduces calculations, authors formal `RESULT-*.md` documents, updates INDEX/STATUS, performs Formal Review/Acceptance, and commits/pushes.

**Historical naming**: "Codex1" is PerfControl's historical alias; "Codex2" is A3PerfRunner's historical alias. Existing immutable Results, submitted prompts, and Evidence pointers retain their original naming. All active/current documentation uses the formal names PerfControl and A3PerfRunner.

`READY` is documentation readiness, not authorization. No execution occurs without explicit User dispatch.

## Evidence and immutability

Every formal run must preserve independent pointers to: (1) code/runtime source identity, (2) Control Task/Result/Review, and (3) server Evidence root and manifest. A3PerfRunner's Evidence root and manifest are immutable once created; corrections or additional evidence are supplements or new Evidence captures, and execution history is never rewritten. Formal `RESULT-*.md` documents are authored locally by PerfControl after Evidence review; the first snapshot of each formal Result is immutable. PerfControl Acceptance updates only the result index, status, Review, and Decision records.

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
