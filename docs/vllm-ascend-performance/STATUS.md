# Project Status

**State:** `BOOTSTRAPPED`

**Blocking status:** `MATERIALS_RECEIVED; NORMALIZATION_INPUTS_INCOMPLETE; STAGE0A_DISCOVERY_PENDING`

**Execution authorization:** no performance execution is ready. A read-only Stage 0 discovery Task is `READY / AWAITING EXPLICIT USER DISPATCH`; no A3/NPU test has been performed.

**Stage 1 status:** `NOT READY`; it requires Stage 0A environment Evidence, Stage 0B/model completion as applicable, official image evidence plus local inventory, and a new complete-command Task. No Stage 1 execution prompt exists.

**Hardware scope:** single Ascend A3/910C server, 8 cards / 16 NPU chips (target scope; server facts remain `PENDING_CODEX2_DISCOVERY`).

## Completed

- Multi-model Control structure created.
- Benchmark contract, metric definitions, source ingestion rules, Evidence rules, and compute-normalization policy drafted.
- User-provided XLSX/DOCX source records hashed and structured H100 cells extracted.
- Public FlagOS/vLLM/vLLM-Ascend version evidence recorded; `FLAGOS_ALIGNED_BASELINE` and `LATEST_REFERENCE` tracks defined.
- Stage 0A environment-first and Stage 0B model-completion discovery policy and Task created.
- Persistent server workspace roots recorded; model downloads may remain in progress without blocking environment preparation.
- Project Model Pool separated from the current Single-A3 candidate set; MiniMax-M3 added.

## Pending gates

1. Resolve source identity conflicts and approve the extracted benchmark method/cells.
2. Freeze a User-approved benchmark contract and comparable compute basis for each cell.
3. Record runtime inventory and model identity per model.
4. User dispatches the read-only Stage 0A/0B Task; Codex2 publishes immutable environment/model-scoped discovery Results.
5. If Stage 0A is sufficient, User may separately authorize a complete-command Stage 1 preparation Task while downloads continue.
6. Create later model/runtime/performance Tasks only from discovery Evidence and explicit decisions.

## Model status

| Model | Status | Execution task |
|---|---|---|
| GLM-5.2-W8A8 | `PENDING_CODEX2_DISCOVERY` | Stage 0A/0B Task |
| DeepSeek-V4-Pro-W8A8 | `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` | None in current Stage 0 |
| DeepSeek-V4-Flash-W8A8 | `PENDING_CODEX2_DISCOVERY` | Stage 0A/0B Task |
| MiniMax-M3 | `PENDING_CODEX2_DISCOVERY` | Stage 0A/0B Task |

DeepSeek-V4-Pro-W8A8 is `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` for this round: retained in the project pool, excluded from single-node Stage 0, and not a blocker for other candidates.

## Current source status

Both requested user files are present and ingested. Their hashes and extracted cells are recorded in [SOURCE-MATERIALS.md](references/SOURCE-MATERIALS.md) and [H100-REFERENCE-INDEX.md](references/H100-REFERENCE-INDEX.md). Original files remain outside this repository and are not modified. No normalized target is calculable yet.
