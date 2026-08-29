# vLLM-Ascend Performance Control

This project establishes reproducible, auditable native vLLM-Ascend baselines for multiple models. It separates shared methodology from model-specific identities, target cells, Tasks, immutable Results, and Formal Reviews.

The primary performance lane is `FLAGOS_ALIGNED`: vLLM `0.20.2` plus vLLM-Ascend `0.20.2rc1`, aligned to FlagOS `release/0.2`. Newer versions are tracked only as a separately labeled `LATEST_REFERENCE` and never silently promoted to the migration baseline.

## Acceptance chain

The Control claim is bounded to the exact model/runtime/hardware/workload identity recorded in an accepted Result. A benchmark process reporting `PASS` is not itself an accepted baseline; Codex1 must complete an independent Formal Review.

## Model namespaces

- `models/glm-5.2-w8a8/`
- `models/deepseek-v4-pro-w8a8/`
- `models/deepseek-v4-flash-w8a8/`

Additional models use the same slugged namespace after a User Decision.

The next stage is the read-only [Stage 0 Server Fact Acquisition Task](tasks/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION.md). It is `READY` for documentation but awaits explicit User dispatch.
