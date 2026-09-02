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

> **Provenance note (2026-09-02)**: the A3 compute-basis portion of D-020 below is **SUPERSEDED** by D-024 (A3/910C corrected to 752 TFLOPS/card × 8 = 6016 TFLOPS). H100 basis (989 × 16 = 15824) unchanged. D-020 remains preserved as historical record; the value `756 / 6048` must not be used as the active normalization basis.

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

## D-023 Machine-Verified Formal Result Gate

**Effective**: 2026-09-02

To prevent AI transcription errors in Formal Results (runtime identity, benchmark values, normalization calculations), PerfControl MUST use machine-verified Evidence ingestion and Result generation.

**Scope**: All Formal Results created from Evidence bundles (GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, MiniMax-M3, and all future models).

**Prohibited Manual Fields**: AI agents are **prohibited** from manually filling the following factual fields in Formal Results:
- Runtime/image identity and versions
- DISPATCH_CONTROL_SHA
- Run2/Run3/Run4 raw throughput values
- Completed/failed counts
- Mean(Run2, Run3, Run4) calculation
- Evidence archive SHA256
- Hardware normalization basis (A3/H100 TFLOPS)
- Normalized throughput calculations
- Achievement percentage

**Required Components**:

1. **Machine-readable normalization source**: `docs/vllm-ascend-performance/hardware-normalization-config.yaml`
   - Authoritative A3/H100 compute basis per Decision D-020
   - Target achievement threshold
   - Sole source for all Result generators and validators

2. **Evidence validation script**: `scripts/validate_evidence.py`
   - Auto-extracts runtime identity from `runtime-identity.txt`
   - Auto-extracts DISPATCH_CONTROL_SHA from `control-sha.txt`
   - Auto-extracts Run2/Run3/Run4 throughput/completed/failed from benchmark logs
   - Machine-computes Mean(Run2, Run3, Run4) with full precision
   - Outputs machine-readable validated Evidence summary (JSON)

3. **Result generator script**: `scripts/generate_result.py`
   - Consumes validated Evidence JSON and normalization config
   - Auto-generates all factual Result fields (no manual transcription)
   - Machine-computes achievement percentage from the authoritative `hardware-normalization-config.yaml`. For GLM-5.2-W8A8, the active A3 compute basis is governed by D-024, which supersedes the A3 compute-basis portion of D-020.
   - AI authoring limited to: analysis, Formal Review rationale, Next Steps

4. **Pre-commit Result validator**: `scripts/validate_result.py`
   - Verifies Evidence runtime == Result runtime
   - Verifies raw Run2/Run3/Run4 values == Result values
   - Recomputes mean and verifies == Result mean
   - Verifies normalization basis == hardware-normalization-config.yaml
   - Recomputes achievement and verifies == Result achievement
   - Verifies DISPATCH_CONTROL_SHA == Evidence provenance
   - Verifies archive SHA256 == Evidence provenance
   - Exits with code 1 (`FORMAL_RESULT_VALIDATION_FAILED`) if any check fails

**Process**:

1. PerfControl downloads and verifies Evidence bundle (SHA256)
2. PerfControl runs `validate_evidence.py` → produces `validated-evidence.json`
3. PerfControl runs `generate_result.py` for each cell → produces draft Result markdown with all factual fields auto-generated
4. AI reviews draft Result, may edit only: analysis sections, Formal Review rationale, Next Steps
5. Before commit: PerfControl runs `validate_result.py` on each Result markdown
6. If validation PASS: proceed with commit/push
7. If validation FAIL: `FORMAL_RESULT_VALIDATION_FAILED`, block commit, investigate error

**Formal Acceptance**: Results with validation failures MUST NOT receive Formal Acceptance. Optimization track MUST NOT begin until corrected Results pass validation.

**Historical Results**: This Decision does not retroactively invalidate historical Results created before 2026-09-02. They remain valid with their original provenance. Future Results MUST use machine-verified gate.

**Rationale**: The correction review (commit cc97d55) identified AI transcription errors in runtime identity (vLLM version) and calculation rounding (1K/16K cells). Machine verification eliminates this entire class of error.

## D-022 GitHub Release Asset Evidence Transport

**Effective**: 2026-09-02

A3PerfRunner is authorized to use **GitHub Release Assets** as an immutable Evidence transport and storage channel.

**Scope**: This Decision supplements D-021 (local PerfControl / remote A3PerfRunner separation) by formalizing how Evidence bundles cross the network boundary when direct SCP/shared-storage is unavailable.

**Rules**:

1. **PerfControl remains the sole formal Control Git writer**. A3PerfRunner is still prohibited from:
   - `git commit` the Control repo
   - `git push` the Control repo
   - Modifying STATUS / Task / Result / Decision documents in Git

2. **A3PerfRunner may upload Evidence bundles as GitHub Release Assets**:
   - Each Evidence bundle is uploaded as a single immutable `.tar.gz` asset
   - Release tag naming convention: `evidence-<task-slug>-<run-id>` (e.g., `evidence-test-glm52-run-20260902-140958`)
   - Asset filename convention: `<TASK_ID>-EVIDENCE-<run-id>.tar.gz`
   - Each asset must record in its internal provenance: Task ID, DISPATCH_CONTROL_SHA, Evidence run ID, asset filename, asset SHA256
   - Runner must communicate the release tag, asset filename, and expected SHA256 to PerfControl

3. **Release Assets are Evidence transport, not formal Control Git state**:
   - Assets do not replace formal Results (which remain in `docs/.../results/` within Git)
   - Assets are immutable: no overwrite, no deletion by the Runner; corrections require a new run ID and new asset
   - PerfControl downloads the asset, independently verifies SHA256, and only then proceeds with Evidence review

4. **PerfControl Evidence ingestion workflow**:
   - `gh release download <tag> --pattern <asset-filename>`
   - Verify SHA256 matches Runner-provided expected value
   - If mismatch: STOP, report `EVIDENCE_INTEGRITY_FAILURE`
   - If match: unpack (without modifying the original archive), perform Evidence completeness/contract/identity gates, independently recalculate aggregations, author formal Results, perform Formal Review and Acceptance, commit and push Git

5. **Evidence bundle integrity**:
   - MANIFEST.txt, COMMANDS.txt, SHA256SUMS.txt, runtime-identity.txt, control-sha.txt (Task ID + DISPATCH_CONTROL_SHA + Authorization)
   - Per-cell raw artifacts (run1-run4 JSON, logs)
   - Per-cell independent Run2/Run3/Run4 aggregation calculations
   - Completeness status, comparison summary, final Runner Report
   - All internal checksums verified before upload

**Rationale**: This Decision enables Evidence delivery when SSH password-based authentication blocks direct SCP, without compromising the D-021 separation (PerfControl = Git writer, Runner = execution/Evidence only). GitHub Release Assets provide authenticated, checksummed, immutable storage that both roles can access programmatically.

**Not covered by this Decision**: Runner uploading anything other than Evidence bundles (e.g., partial logs, interim drafts, or formal Results) to GitHub Releases; such actions remain prohibited.

## D-024 GLM-5.2-W8A8 A3/910C Hardware Compute Basis Correction

**Effective**: 2026-09-02

**Status**: Corrects the A3 compute-basis portion of Decision D-020; supersedes it for all current and future GLM-5.2-W8A8 normalization. D-020 remains preserved as historical provenance.

1. User previously supplied the A3/910C basis as `756 TFLOPS / physical card @ FP16`.
2. User has now **explicitly corrected that input as erroneous**.
3. The correct active A3/910C basis is **752 TFLOPS / physical card @ FP16**.
4. The 8-card A3 system basis is **8 × 752 = 6016 TFLOPS**.
5. The H100 basis remains unchanged: **16 × 989 = 15824 TFLOPS**.
6. The measured A3 value **6019.718 TFLOPS** (ascend-dmi) remains evidence/reference **ONLY**; it is never used as the normalization denominator.
7. D-024 supersedes the A3 compute-basis portion of D-020 for all current/future GLM-5.2-W8A8 normalization.
8. D-020 remains preserved as historical provenance (see D-020 section note above); it is not deleted.
9. Existing immutable Results are NOT rewritten; active normalized values are corrected via the new hardware normalization correction supplement and current active documentation (`hardware-normalization-config.yaml`, POLICY, ASCEND-TARGETS, STATUS, INDEX).
10. All derived normalization values are machine-computed from `hardware-normalization-config.yaml` (now 752/6016) plus accepted raw data — no manual transcription.

**Rationale**: User identified `756/6048` as an input error and provided the corrected A3/910C specification `752 × 8 = 6016`.
