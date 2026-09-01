# vLLM-Ascend Performance Control

This project establishes reproducible, auditable native vLLM-Ascend baselines for multiple models. It separates shared methodology from model-specific identities, target cells, Tasks, immutable Results, and Formal Reviews.

The primary performance lane is `FLAGOS_ALIGNED`: vLLM `0.20.2` plus vLLM-Ascend `0.20.2rc1`, aligned to FlagOS `release/0.2`. Newer versions are tracked only as a separately labeled `LATEST_REFERENCE` and never silently promoted to the migration baseline.

**Model-specific exception (Decision D-019)**: GLM-5.2-W8A8 uses a User-verified vLLM 0.24 runtime for current native performance work. The FlagOS-aligned 0.20.2 lane is retained as a historical/migration reference for GLM.

## Acceptance chain

The Control claim is bounded to the exact model/runtime/hardware/workload identity recorded in an accepted Result. A benchmark process reporting `PASS` is not itself an accepted baseline; PerfControl must complete an independent Formal Review.

## Project Model Pool

- `models/glm-5.2-w8a8/`
- `models/deepseek-v4-pro-w8a8/`
- `models/deepseek-v4-flash-w8a8/`
- `models/minimax-m3/`

Additional models use the same slugged namespace after a User Decision.

## Current Single-A3 Execution Candidates

The current target is one Ascend A3/910C server with 8 cards / 16 NPU chips. Only these models enter the current single-node Stage 0 scope:

- **GLM-5.2-W8A8**: Has User-verified baseline (D-019). Execution mode is **FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION**. Discovery-first capability retained for new servers but does not gate current GLM work.
- **DeepSeek-V4-Flash-W8A8**: Requires discovery-first flow (Stage 0A → Stage 0B).
- **MiniMax-M3**: Requires discovery-first flow (Stage 0A → Stage 0B).

DeepSeek-V4-Pro-W8A8 remains in the Project Model Pool as `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE`. It is retained for future multi-node resources, is excluded from the current Stage 0 execution scope, and cannot block the three single-node candidates.

The only READY task is the read-only [Stage 0A Environment Discovery Task](tasks/VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY.md), with its committed [historical A3PerfRunner prompt](tasks/CODEX2-VLLM-ASCEND-STAGE0A-DISPATCH-PROMPT.md) (note: prompt uses historical "Codex2" naming per D-018). Stage 0B is deferred until model downloads are complete enough for inspection; it has no dispatchable prompt. Stage 0A is environment-first and does not require model downloads to be complete.

Reusable [Task](templates/TASK-TEMPLATE.md) and immutable [Result](templates/RESULT-TEMPLATE.md) templates are provided for later stages.

The committed-prompt handoff sequence is defined in [ChatGPT Review and Handoff](methodology/CHATGPT-REVIEW-AND-HANDOFF.md).

Server path policy, the Single-A3 container contract, and complete-command requirements are defined in [Workspace and Evidence Paths](methodology/WORKSPACE-AND-EVIDENCE-PATHS.md), [Single-A3 Container Contract](methodology/SINGLE-A3-CONTAINER-CONTRACT.md), and [Execution Command Completeness](methodology/EXECUTION-COMMAND-COMPLETENESS.md).

Model download and identity hashing follows [Model Hash Policy](methodology/MODEL-HASH-POLICY.md); an active download never blocks environment preparation.

Official A3 image carrier evidence and the unresolved tag/digest boundary are recorded in [Image Identity Evidence](methodology/IMAGE-IDENTITY-EVIDENCE.md).
