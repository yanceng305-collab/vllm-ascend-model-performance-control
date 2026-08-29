# Project Status

**State:** `BOOTSTRAPPED`

**Blocking status:** `MATERIALS_RECEIVED; NORMALIZATION_INPUTS_INCOMPLETE`

**Execution authorization:** `NO EXECUTION READY`; no Codex2 performance Task exists and no A3/NPU test has been performed.

## Completed

- Multi-model Control structure created.
- Benchmark contract, metric definitions, source ingestion rules, Evidence rules, and compute-normalization policy drafted.
- User-provided XLSX/DOCX source records hashed and structured H100 cells extracted.

## Pending gates

1. Resolve source identity conflicts and approve the extracted benchmark method/cells.
2. Freeze a User-approved benchmark contract and comparable compute basis for each cell.
3. Record runtime inventory and model identity per model.
4. Create a formal `READY` Task only after the preceding inputs are complete; still requires explicit User dispatch.
5. Execute, publish immutable Results, review, and accept bounded baselines.

## Model status

| Model | Status | Execution task |
|---|---|---|
| GLM-5.2-W8A8 | `WAITING FOR INPUTS` | None |
| DeepSeek-V4-Pro-W8A8 | `WAITING FOR INPUTS` | None |
| DeepSeek-V4-Flash-W8A8 | `WAITING FOR INPUTS` | None |

## Current source status

Both requested user files are present and ingested. Their hashes and extracted cells are recorded in [SOURCE-MATERIALS.md](references/SOURCE-MATERIALS.md) and [H100-REFERENCE-INDEX.md](references/H100-REFERENCE-INDEX.md). Original files remain outside this repository and are not modified. No normalized target is calculable yet.
