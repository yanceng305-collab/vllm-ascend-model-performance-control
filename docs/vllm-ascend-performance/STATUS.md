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

**Status**: BASELINE ESTABLISHED (Evidence-backed baseline matrix formally accepted 2026-09-02, corrected 2026-09-02)

**Execution mode**: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → **OPTIMIZATION** (current phase)

**Evidence-backed baseline matrix** (Evidence run: run-20260902-140958, corrected):
- 1K: **676.60 tok/s**, Achievement: 65.84% (BELOW TARGET)
- 4K: 820.76 tok/s, Achievement: 52.85% (BELOW TARGET)
- 16K: **957.94 tok/s**, Achievement: 57.23% (BELOW TARGET)
- 64K: 927.59 tok/s, Achievement: 48.01% (BELOW TARGET)

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz` (SHA256: `8818e4ffa...01816d2`)  
**Evidence Location**: GitHub Release `evidence-test-glm52-run-20260902-140958` (Decision D-022)

**Runtime Identity** (corrected): Container `model-test-zyg-a3`, Image `nightly-releases-v0.24.0rc-a3`, vLLM `0.24.0+empty`

**Target**: ≥80% normalized throughput for all cells (Decision D-020)

**Correction Note**: Original Results (commit 371f5f0) contained runtime identity transcription error (incorrectly recorded as vLLM 0.6.4.post1; actual: vLLM 0.24.0+empty) and two calculation rounding errors (1K: 676.59→676.60; 16K: 957.93→957.94). Correction Supplement created; original Results superseded but unchanged.

**Next steps**:
1. Optimization track may proceed (corrected baseline formally accepted)
2. Root cause analysis and profiling
3. Target achievement: ≥80% for all cells

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
- D-022: GitHub Release Asset Evidence Transport
