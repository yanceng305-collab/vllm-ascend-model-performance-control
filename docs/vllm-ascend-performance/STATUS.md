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
  - 64K measured performance: 927.45 tok/s (48.01% achievement vs 80% target)
  - Hardware compute basis established (Decision D-020)
  - RUNBOOK and executable scripts created
  - Baseline vs optimization separation enforced (Decision D-019)

## GLM-5.2-W8A8 Current Status

**Execution mode**: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION

**64K baseline** (User-measured):
- Total token throughput: 927.45 tok/s
- Normalized throughput: 0.153373 tok/s per TFLOPS
- Achievement vs H100: 48.01% (target: ≥80%)
- **Disposition**: BELOW TARGET

**Next steps**:
1. Complete baseline matrix (1K/4K/16K/64K) Evidence Acquisition via A3PerfRunner (User dispatch with Task ID + DISPATCH_CONTROL_SHA + Authorization: EXECUTE)
2. A3PerfRunner produces Evidence (raw artifacts, MANIFEST, COMMANDS, SHA256SUMS, runtime identity, Run2/3/4 calculations, comparison summary, final report)
3. PerfControl receives Evidence, independently recalcs, authors four formal Evidence-backed `RESULT-*.md` (one per cell), updates INDEX/STATUS
4. Formal Review and Formal Acceptance per cell (PerfControl)
5. Root cause analysis and profiling
6. Optimization track (separate OPT Tasks)

Stage 0 discovery is NOT required for GLM baseline performance work. GLM uses vLLM 0.24 as User-verified runtime. FlagOS-aligned 0.20.2 remains as historical reference only.

## Pending Gates

1. **GLM-5.2-W8A8**: 
   - Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION) `READY` — awaiting User dispatch (Task ID + DISPATCH_CONTROL_SHA + Authorization: EXECUTE) for A3PerfRunner Evidence capture
   - PerfControl then authors formal Evidence-backed Results (1K/4K/16K/64K), reviews and accepts per cell
   - Root cause analysis (observed: KV cache ~85%, scheduling constraints)
   - Optimization Tasks to achieve ≥80% target
2. **DeepSeek-V4-Flash / MiniMax-M3**: 
   - User dispatch Stage 0A environment discovery
   - After models ready, dispatch Stage 0B
   - Establish baselines and targets

## Model Status

| Model | Status | Current work | Execution mode |
|---|---|---|---|
| GLM-5.2-W8A8 | USER-VERIFIED BASELINE; 64K@48.01% | Baseline matrix + optimization | Known-good baseline, no Stage 0 |
| DeepSeek-V4-Pro-W8A8 | `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` | None (excluded from single-A3) | N/A |
| DeepSeek-V4-Flash-W8A8 | `PENDING_A3PERFRUNNER_DISCOVERY` | Stage 0A awaiting dispatch | Discovery first |
| MiniMax-M3 | `PENDING_A3PERFRUNNER_DISCOVERY` | Stage 0A awaiting dispatch | Discovery first |

DeepSeek-V4-Pro-W8A8 is `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` for this round: retained in project pool, excluded from single-node Stage 0, not a blocker for other candidates.

## Current Source Status

Both requested user files are present and ingested. Their hashes and extracted cells are recorded in [SOURCE-MATERIALS.md](references/SOURCE-MATERIALS.md) and [H100-REFERENCE-INDEX.md](references/H100-REFERENCE-INDEX.md). Original files remain outside this repository and are not modified. GLM-5.2-W8A8 normalized targets are calculable per Decision D-020.

## Decisions

See [DECISIONS.md](DECISIONS.md) for all formal decisions, including:
- D-018: Agent role naming (PerfControl / A3PerfRunner)
- D-019: GLM-5.2-W8A8 User-verified baseline override
- D-020: GLM-5.2-W8A8 hardware compute basis and normalization policy
- D-021: Local PerfControl / Remote A3PerfRunner Separation (final role architecture; Runner produces Evidence, PerfControl produces formal Results)
