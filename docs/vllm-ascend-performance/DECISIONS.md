# Decisions

## D-001 Control scope

This repository is a native vLLM-Ascend model performance baseline Control plane. It is not a FlagOS adaptation repository and does not contain implementation forks.

## D-002 User normalization policy

For comparable higher-is-better metrics, the minimum target is `H100 metric * (Ascend comparable system compute / H100 comparable system compute) * 0.80`. For lower-is-better metrics, use the inverse latency formulation only when the approved benchmark contract explicitly makes that metric a gate. This is a User-defined performance acceptance heuristic, not a claim that theoretical compute ratios equal end-to-end LLM performance.

## D-003 No guessed inputs

Unknown public facts are researched by PerfControl; unknown server-observable facts are `PENDING_A3PERFRUNNER_DISCOVERY`; only policy, authorization, private material, engineering-reference approval, or true business decisions are `USER INPUT REQUIRED`. Missing comparable compute prevents a normalized target from being calculated.

Historical note: `PENDING_CODEX2_DISCOVERY` was the original term for `PENDING_A3PERFRUNNER_DISCOVERY` (per D-018 effective 2026-09-01). Immutable historical artifacts preserve the original terminology.

## D-004 No execution at bootstrap

Bootstrap performs no A3/NPU operation, package installation, model launch, or benchmark. A3PerfRunner execution requires a READY Task and explicit User dispatch.

## D-005 FlagOS-aligned version baseline

The primary baseline is `flagos-ai/vllm-plugin-FL@release/0.2` aligned to `vLLM 0.20.2` and `vLLM-Ascend 0.20.2rc1`, with the compatibility-row Python/CANN/PyTorch/torch_npu/Triton/Mooncake constraints recorded in `methodology/VERSION-BASELINE.md`. Newer versions are not silently substituted.

## D-006 Dual performance tracks

`FLAGOS_ALIGNED` is the formal migration baseline. `LATEST_REFERENCE` is a separately labeled `NON_FLAGOS_ALIGNED_REFERENCE` for support/blocker investigation only; it cannot replace, mix with, or pass the aligned lane.

## D-007 Fact ownership

PerfControl retrieves public facts. A3PerfRunner retrieves server-observable facts after User dispatch through a read-only Stage 0 Task. User is asked only for policy, private material, authorization, engineering-reference approval, or true business decisions.

## D-008 Comparison classes

Use `STRICT_REFERENCE`, `ENGINEERING_REFERENCE`, or `NOT_COMPARABLE`. Platform implementation parameters may differ; workload semantics and metric definitions remain the comparability contract.

## D-009 Stage 0 boundary

Stage 0 is read-only/non-destructive Server Fact Acquisition and Compatibility Discovery. Stateful preparation, model launch, and benchmark require separate dispatched Tasks and explicit User authorization.

## D-010 Single-A3 candidate scope

The current single-node target is Ascend A3/910C, 8 cards / 16 NPU chips. The current Stage 0 candidate set is GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, and MiniMax-M3. DeepSeek-V4-Pro-W8A8 remains in the project pool as `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE`, is excluded from this round's Stage 0 execution scope, and cannot block the three candidates.

## D-011 Prompt-as-Control-Artifact

Any long A3PerfRunner dispatch prompt must first be committed as a Markdown file in this Control repository. The committed GitHub file is the sole formal handoff artifact and must bind repo, Task, prompt path, Control commit, scope, allowed/prohibited actions, outputs, Evidence, and Result rules. PerfControl terminal output must link the file rather than substitute an uncommitted prompt.

## D-012 ChatGPT review and handoff

The workflow is PerfControl Task/prompt creation -> commit/push -> User gives the result to ChatGPT -> ChatGPT live-queries GitHub and independently reviews SHA, Task, prompt, scope, safety, and Evidence rules -> ChatGPT either returns the committed prompt unchanged to User or requests PerfControl revision -> User sends the reviewed Control artifact to A3PerfRunner. The committed prompt, not terminal text, is authoritative.


## D-013 Persistent workspace and Evidence paths

Freeze `WORK_ROOT=/data/tiankuan/zyg`, `MODEL_ROOT=/data/tiankuan/zyg/model`, `EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`, and `TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control` as the project workspace policy. Stage 0 uses the persistent Evidence root and never `/tmp` as formal fallback. A3PerfRunner inspects candidate models only under `MODEL_ROOT`; incomplete downloads are `DOWNLOAD_IN_PROGRESS` and do not block environment-first preparation.

## D-014 Single-A3 Container Contract

For one A3/910C server with 8 cards / 16 NPU chips, freeze the privileged host-network, 512g shared-memory, `/dev/davinci0` through `/dev/davinci15`, manager/devmm/hisi device mapping, driver/DCMI/HCCN mounts, `/data/tiankuan:/data/tiankuan`, and `/home:/home` contract in `methodology/SINGLE-A3-CONTAINER-CONTRACT.md`. Prohibit `/data:/data` and `/root/.cache:/root/.cache`. Fixed model container names are `vllm-ascend-glm5.2-zyg`, `vllm-ascend-deepseek-v4-flash-zyg`, and `vllm-ascend-minimax-m3-zyg`. Image identity is selected only from official evidence plus Stage 0 inventory; no tag is guessed. Contract changes require a new Decision and User authorization.

## D-015 Execution Command Completeness

From Stage 1 onward, every server-operation Task must include complete, directly executable commands, resolved paths/identities, logging, readiness checks, and cleanup. This applies to runtime preparation, model launch, functional smoke, performance cells, and optimization/retest. Stage 6 formal review requires no server command. A3PerfRunner may not improvise or replace abstract instructions with unrecorded commands, and Stage 4 Results are never overwritten.

## D-016 Environment-first Stage 0 split

Stage 0A is the sole current READY Task and covers read-only environment/host/container discovery only. Stage 0B is `DEFERRED / WAITING_MODEL_DOWNLOAD / NOT_DISPATCHABLE` and covers model identity/compatibility only after downloads are complete enough. Stage 0A's environment Result can unlock a separately authorized Stage 1 while models continue downloading; model state cannot block environment readiness.

## D-017 Model download/hash policy

During `DOWNLOAD_IN_PROGRESS`, do not hash large weights or issue compatibility verdicts. After `MODEL_DOWNLOAD_COMPLETE`, Stage 0B may produce identity hashes and a reusable weight manifest; full weight SHA-256 is optional and separately justified. Never use hashes captured while files are being written as formal provenance.

## D-018 Agent role naming

Effective 2026-09-01, the formal agent role names are **PerfControl** (Control plane agent) and **A3PerfRunner** (A3 execution agent). These supersede the bootstrap names "Codex1" and "Codex2" respectively.

- **PerfControl** = Control repo, planning, methodology, Task/prompt authoring, Result review, Acceptance, status governance, GitHub source-of-truth maintenance.
- **A3PerfRunner** = A3 server execution, command execution, Evidence collection, raw log preservation, Result reporting.

Historical references: "Codex1" is PerfControl's historical alias; "Codex2" is A3PerfRunner's historical alias. Existing immutable Results, submitted prompts, and Evidence pointers retain their original naming and are not rewritten. All active/current documentation, README, PLAN, STATUS, methodology, future Tasks, future prompts, and future Results use the new formal names.

Future prompt filenames should use the pattern `A3PERFRUNNER-<TASK>-PROMPT.md` rather than `CODEX2-<TASK>-PROMPT.md`.

## D-019 GLM-5.2-W8A8 User-verified baseline override

Effective 2026-09-01, GLM-5.2-W8A8 has a **USER-VERIFIED KNOWN-GOOD BASELINE** that supersedes the FlagOS-aligned 0.20.2 discovery-first approach for this model only.

User has completed on A3:
1. Container creation with verified image `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`
2. vLLM 0.24.0+empty / vLLM-Ascend 0.19.1rc2.dev1157+g6443b2a38 runtime verification
3. GLM-5.2-W8A8 TP16 successful launch with FULL_DECODE_ONLY graph mode
4. Graph compilation success
5. 64K input + 1K output + C64 benchmark completion
6. Real baseline performance measurement
7. A3 FP16 compute measurement via ascend-dmi

GLM-5.2-W8A8 execution mode: **USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS/SCRIPTS → EVIDENCE → RESULT → OPTIMIZATION**.

Stage 0 discovery capability is retained for new servers, new hardware, unknown runtimes, and unverified models (DeepSeek, MiniMax), but does not block GLM-5.2-W8A8 current performance work.

Baseline artifacts (container command, server launch command, benchmark workload, scripts) are frozen as model-specific known-good references. Optimizations are tracked as separate OPT Tasks with independent Results compared against the frozen baseline.

The FlagOS-aligned 0.20.2 track remains as historical/migration reference but does not gate GLM-5.2-W8A8 native 0.24-based performance testing.

## D-020 GLM-5.2-W8A8 hardware compute basis

Effective 2026-09-01, the **User-approved unified hardware compute basis** for GLM-5.2-W8A8 normalization:

**A3/910C**: 756 TFLOPS per physical card @ FP16 (suitable precision for W8A8 comparison)  
**A3 system**: 8 physical cards × 756 = **6048 TFLOPS**

**H100**: 989 TFLOPS per physical card @ FP8 (customer baseline precision)  
**H100 system**: 16 cards × 989 = **15824 TFLOPS**

**Measured A3 compute** (ascend-dmi -f -t fp16): 6019.718 TFLOPS (recorded as measured evidence; 6048 TFLOPS is the official normalization basis).

**Primary acceptance metric**: Normalized Total Token Throughput  
**Formula**: `NormalizedThroughput = TotalTokenThroughput / PhysicalCardCount / UnifiedHardwareComputePerCard`  
**Pass condition**: `(A3_Normalized / H100_Normalized) >= 0.80`

This is model-specific and does not apply automatically to DeepSeek, MiniMax, or future models.

## D-021 Local PerfControl / Remote A3PerfRunner Separation

Effective 2026-09-02, the final role architecture is frozen. Formal GitHub Control repo writes are local-only and are performed solely by PerfControl. The A3 server role is execution-and-Evidence-only. The Control repo and the server do not migrate between PerfControl and A3PerfRunner.

Core rules:

```text
Control/GitHub writes are local-only.
Runner/server is execution-and-Evidence-only.
Server Git SHA parity with Control is not required.
DISPATCH_CONTROL_SHA is provenance, not server Git-state identity.
Formal Results are authored by PerfControl after Evidence review.
```

**PerfControl (local)**:
- Owns the Control repo, GitHub, Decisions, Tasks, Prompts, STATUS/INDEX, formal `RESULT-*.md` authoring, Formal Review, Formal Acceptance, commit, and push.
- PerfControl is the sole role allowed to write the formal GitHub Control repo.
- Before dispatching a Task, PerfControl verifies `local Control HEAD == origin/main == DISPATCH_CONTROL_SHA`; only after verification may User dispatch.

**A3PerfRunner (A3 server)**:
- Owns server Task execution, container inspection, benchmark execution (only when the Task explicitly authorizes it), raw data collection, runtime identity, logs, SHA256, Evidence manifest, Evidence summary/report, and Evidence bundle.
- Does not maintain formal Control Git history, does not require server HEAD to equal the GitHub SHA, does not commit the Control repo, does not push GitHub, does not perform Formal Acceptance, and does not create formal GitHub Results.

**DISPATCH_CONTROL_SHA semantics**: it identifies the formal Control Task version that the Runner execution corresponds to. PerfControl verifies it locally before dispatch; the Runner records it into Evidence provenance. The Runner does not need to own the corresponding Git commit.

**Result authorship**: Runner produces Evidence; PerfControl produces formal Results. After the Runner delivers Evidence, PerfControl independently reproduces the calculations, authors the one-per-cell formal `RESULT-*.md` documents, updates INDEX/STATUS, performs Formal Review, performs Formal Acceptance, and commits/pushes to GitHub.

**Legacy**: The Stage 0A `CODEX2-...` prompt artifact explicitly remains historical per D-018 and the tasks `README`; immutable historical Results and records are not covered by this Decision and are not rewritten. Where earlier decisions describe A3PerfRunner actions such as "Result reporting," D-021 governs: the Runner delivers Evidence and a Runner Report; formal `RESULT-*.md` authoring belongs to PerfControl.
