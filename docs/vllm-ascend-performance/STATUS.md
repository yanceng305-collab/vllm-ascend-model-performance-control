# Project Status

**State:** `BOOTSTRAPPED; GLM-5.2-W8A8 USER-VERIFIED BASELINE ESTABLISHED`

**Blocking status:** `GLM: BASELINE_MEASURED_BELOW_TARGET; DeepSeek/MiniMax: STAGE0A_DISCOVERY_PENDING`

**Lifecycle:** 
- GLM-5.2-W8A8: `USER-VERIFIED BASELINE MODE; FAST_PREFLIGHT → RUN_FROZEN_COMMANDS → OPTIMIZATION`
- DeepSeek-V4-Flash-W8A8: Stage 0A `READY / AWAITING EXPLICIT USER DISPATCH`; Stage 0B `DEFERRED / WAITING_MODEL_DOWNLOAD`
- MiniMax-M3: Stage 0A `READY / AWAITING EXPLICIT USER DISPATCH`; Stage 0B `DEFERRED / WAITING_MODEL_DOWNLOAD`
- DeepSeek-V4-Pro-W8A8: `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE`

**Hardware scope:** single Ascend A3/910C server, 8 cards / 16 NPU chips (GLM verified; other models pending discovery).

## Agent Roles (Effective 2026-09-01; final architecture frozen 2026-09-02 per D-021)

- **PerfControl** (formerly Codex1): sole writer of the formal GitHub Control repo — Control repo, GitHub, Decisions, Tasks, Prompts, STATUS/INDEX, formal Result authoring, Formal Review, Formal Acceptance, commit, push
- **A3PerfRunner** (formerly Codex2): A3 server execution, container operation/inspection, benchmark (Task-authorized only), raw data collection, runtime identity, logs, SHA256, Evidence manifest/summary/report/bundle. No Control Git commits, no GitHub push, no server Git SHA parity requirement, no formal Result authoring, no Acceptance.

**Result authorship split**: Runner produces Evidence; PerfControl produces formal Results (see Decision D-021). Historical references use "Codex1" and "Codex2" as aliases.

## Completed

- Multi-model Control structure created.
- Benchmark contract, metric definitions, source ingestion rules, Evidence rules, and compute-normalization policy drafted.
- User-provided XLSX/DOCX source records hashed and structured H100 cells extracted.
- Public FlagOS/vLLM/vLLM-Ascend version evidence recorded; `FLAGOS_ALIGNED_BASELINE` and `LATEST_REFERENCE` tracks defined.
- Stage 0A environment-first discovery Task and committed prompt created for DeepSeek/MiniMax; Stage 0B model-completion Task deferred until downloads are ready.
- Persistent server workspace roots recorded; model downloads may remain in progress without blocking environment preparation.
- Project Model Pool separated from the current Single-A3 candidate set; MiniMax-M3 added.
- **GLM-5.2-W8A8 User-verified baseline established (2026-09-01)**:
  - Container creation, vLLM 0.24 runtime, TP16 launch, graph compilation, 64K benchmark completed by User
  - Baseline frozen: container command, server launch command, benchmark workload, scripts
  - 64K measured performance: 927.45 tok/s (historical; active basis D-024 achievement 48.27% on 927.59)
  - Hardware compute basis established (Decision D-020)
  - RUNBOOK and executable scripts created
  - Baseline vs optimization separation enforced (Decision D-019)

## GLM-5.2-W8A8 Current Status

**Status**: BASELINE ESTABLISHED (Evidence-backed baseline matrix formally accepted 2026-09-02, corrected 2026-09-02)

**Execution mode**: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → **OPTIMIZATION** (current phase)

**Evidence-backed baseline matrix** (Evidence run: run-20260902-140958, corrected; active basis D-024, 6016):
- 1K: **676.60 tok/s**, Achievement: 66.19% (BELOW TARGET)
- 4K: 820.76 tok/s, Achievement: 53.13% (BELOW TARGET)
- 16K: **957.94 tok/s**, Achievement: 57.53% (BELOW TARGET)
- 64K: 927.59 tok/s, Achievement: 48.27% (BELOW TARGET)

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz` (SHA256: `8818e4ffa...01816d2`)  
**Evidence Location**: GitHub Release `evidence-test-glm52-run-20260902-140958` (Decision D-022)

**Runtime Identity** (corrected): Container `model-test-zyg-a3`, Image `nightly-releases-v0.24.0rc-a3`, vLLM `0.24.0+empty`

**Target**: ≥80% normalized throughput for all cells (active basis D-024, 6016; D-020 A3 basis historical)

**Correction Note**: Original Results (commit 371f5f0) contained runtime identity transcription error (incorrectly recorded as vLLM 0.6.4.post1; actual: vLLM 0.24.0+empty) and two calculation rounding errors (1K: 676.59→676.60; 16K: 957.93→957.94). Correction Supplement created; original Results superseded but unchanged.

**Hardware basis correction (2026-09-02, D-024)**: User corrected the A3/910C compute input; active basis is 752 TFLOPS/card × 8 = **6016 TFLOPS** (was 756 × 8 = 6048). H100 unchanged (989 × 16 = 15824). Measured 6019.718 TFLOPS remains evidence-only. Active achievements/80% targets above are machine-recomputed on 6016 (see [CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902](models/glm-5.2-w8a8/results/CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902.md)); immutable Results and the first correction supplement remain unchanged.

**Next steps**:
1. Optimization track may proceed (corrected baseline formally accepted)
2. Root cause analysis and profiling
3. Target achievement: ≥80% for all cells

**OPT-01 Preflight (2026-09-02, read-only)**: outcome `RUNTIME_IDENTITY_MISMATCH` / Gate A `NO_PROCESS`; effective `max_num_batched_tokens` **UNVERIFIED**; the accepted GLM-5.2-W8A8 baseline runtime was NOT active at observation time (container serving another workload). OPT-01 screening remains **BLOCKED**; candidate selection NOT AUTHORIZED. Evidence transport: GitHub Release `preflight-opt01-20260902-085628` (D-022). `READ-ONLY PREFLIGHT EVIDENCE — NOT FORMAL BASELINE RESULT`. Re-observation requires User authorization to restore the accepted GLM baseline runtime.

**Manual runtime observation (2026-09-02)**: User manually restored a GLM-5.2-W8A8 vLLM service on A3 (USER-MANUAL OPERATIONAL RESTORE / EXPLORATORY). It is NOT an exact replay of the accepted frozen baseline (deviations: `LD_PRELOAD` jemalloc, `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`, `OMP_PROC_BIND=false`, `OMP_NUM_THREADS=1`, `--served-model-name glm52-w8a8`, `--distributed-executor-backend mp`, `max_cudagraph_capture_size=64`, `--port 8000`, log `/workspace/glm52_w8a8.log`). Graph capture 11/11 (411 s; 0.59 GiB); warning: capture 64 < potential decode requirement 256 (alignment risk, not a measured value). `max_num_batched_tokens` remains **UNVERIFIED**. Manual 16K exploratory microgate **COMPLETED (2026-09-02)**: Run2 total token throughput 960.45 tok/s vs accepted 957.94, machine-computed delta **+0.262%** → **MANUAL EXPLORATORY MICROGATE: NO_MATERIAL_GAIN** (below +2% material-gain threshold; not regression; 256 success / 0 failed; not formal OPT-01 screening). Formal OPT-01 screening remains **BLOCKED / NOT YET AUTHORIZED**. Official upstream reference (GLM5.2.md, commit `6443b2a38b95390e4f5174ff7ad2f8c3751e040f`) independently verified; its `--max-num-batched-tokens 4096` recorded as `RECOMMENDED / REFERENCE CANDIDATE ONLY`, NOT the baseline effective value.

**New exploratory Task (2026-09-02)**: `GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE` created as **READY / PENDING USER REDISPATCH** (Task + A3PerfRunner Prompt committed in the model dir). Official-derived upstream A3 GLM-5.2-W8A8 profile under the frozen `max-model-len=70000`: startup + 70K capacity gate, then 16K two-run microgate, no auto-64K; leave service running. Independent of formal OPT-01 (still BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION); no server execution yet. Runner mode (2026-09-02): AUTONOMOUS OPTIMIZATION RUNNER - autonomous diagnose/modify/retry within HARD BOUNDARIES; initial 0.95 profile capacity FAIL (KV ~6.30 vs ~6.28 GiB; est. max len 69632; Release `glm52-od-profile-16k-20260902-144217`) is the known recoverable starting point; status READY / PENDING USER REDISPATCH. No normalization/Decision change. Evidence Review (2026-09-02) of Attempt-003 PASSED; 64K follow-up Task created (READY / PENDING USER DISPATCH). 64K Evidence review (2026-09-03) PASS; full-matrix validation recommended next.

Stage 0 discovery is NOT required for GLM baseline performance work. GLM uses vLLM 0.24.0+empty as frozen baseline runtime. FlagOS-aligned 0.20.2 remains as historical reference only.

## Pending Gates

1. **GLM-5.2-W8A8**: 
   - Baseline formally accepted (all four cells: 1K/4K/16K/64K)
   - Optimization track ready to begin per cell
   - Root cause analysis (observed: KV cache ~85%, scheduling constraints)
   - Optimization Tasks to achieve ≥80% target
2. **DeepSeek-V4-Flash / MiniMax-M3**: 
   - User dispatch Stage 0A environment discovery
   - After models ready, dispatch Stage 0B
   - Establish baselines and targets

## Model Status

| Model | Status | Current work | Execution mode |
|---|---|---|---|
| GLM-5.2-W8A8 | USER-VERIFIED BASELINE; 64K@48.27% | Baseline matrix + optimization | Known-good baseline, no Stage 0 |
| DeepSeek-V4-Pro-W8A8 | `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` | None (excluded from single-A3) | N/A |
| DeepSeek-V4-Flash-W8A8 | `PENDING_A3PERFRUNNER_DISCOVERY` | Stage 0A awaiting dispatch | Discovery first |
| MiniMax-M3 | `PENDING_A3PERFRUNNER_DISCOVERY` | Stage 0A awaiting dispatch | Discovery first |

DeepSeek-V4-Pro-W8A8 is `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` for this round: retained in project pool, excluded from single-node Stage 0, not a blocker for other candidates.

## Current Source Status

Both requested user files are present and ingested. Their hashes and extracted cells are recorded in [SOURCE-MATERIALS.md](references/SOURCE-MATERIALS.md) and [H100-REFERENCE-INDEX.md](references/H100-REFERENCE-INDEX.md). Original files remain outside this repository and are not modified. GLM-5.2-W8A8 normalized targets are calculable per Decision D-020 (active basis per D-024).

## Decisions

See [DECISIONS.md](DECISIONS.md) for all formal decisions, including:
- D-018: Agent role naming (PerfControl / A3PerfRunner)
- D-019: GLM-5.2-W8A8 User-verified baseline override
- D-020: GLM-5.2-W8A8 hardware compute basis and normalization policy
- D-021: Local PerfControl / Remote A3PerfRunner Separation (final role architecture; Runner produces Evidence, PerfControl produces formal Results)
- D-022: GitHub Release Asset Evidence Transport
- D-023: Machine-Verified Formal Result Gate (eliminates AI transcription errors)
- D-024: GLM-5.2-W8A8 A3/910C hardware compute basis correction (active basis 752 × 8 = 6016; supersedes the A3 compute-basis portion of D-020)
- D-025: Full-Matrix Formal Evidence Contract (canonical runN.command.txt artifact + pinned DISPATCH_CONTROL_SHA script acquisition + two-stage per-cell/matrix validation)


- Full-matrix candidate validation Task prepared (2026-09-03): profile candidate (0.95/67000) 4-run matrix; extractor+validator scripts; READY / PENDING USER DISPATCH.
- Pre-dispatch tooling review + fix (2026-09-03): the 64K real raw evidence (Release `glm52-od-64k-followup-20260903`, asset SHA256 `15bb96cd...43fa5`, live verified) exposed an extractor regex bug — labels with unit parentheses (e.g. `Total token throughput (tok/s):`) parsed as null. Extractor rewritten (unit-paren tolerant, `--strict` fail-closed, deterministic); per-cell validator scoped to per-cell (contract from `runN.command.txt`, Run1 `WARMUP_DISCARD` gate, D-024 inputs from `candidate-matrix-config.json`); matrix-level validator `validate_full_matrix_candidate.py` added (cross-cell profile-snapshot identity only). Regression suite `scripts/test_matrix_tooling.py` A–F PASS on real fixture + synthetic cells. Runner Prompt Rev 2 documents pinned checkout at DISPATCH_CONTROL_SHA + canonical argv artifact. Task stays `READY / PENDING USER DISPATCH` (no server execution; warm service untouched).
- Pre-dispatch final patch (2026-09-03): `runN.command.txt` serialization fixed to `sys.argv[2:]` (first JSON element is `vllm`, exact executed argv, self-verifying) with a prompt-integration regression (TEST G); all tool invocations in the Runner Prompt pinned to `"$CONTROL_DIR/scripts/..."`; per-cell validator now enforces the `run1.role.txt` artifact gate (exists + content `WARMUP_DISCARD`); TEST C made a real fail-closed regression (extractor `--strict` invoked, rc != 0, missing field named). Suite `scripts/test_matrix_tooling.py` A–G = 7 passed / 0 failed / 0 skipped. Task remains `READY / PENDING USER DISPATCH`; candidate profile unchanged (0.95/67000); no server action; no Formal Result; Formal OPT-01 untouched.
