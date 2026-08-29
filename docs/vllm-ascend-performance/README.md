# vLLM-Ascend Performance Control

This project establishes reproducible, auditable native vLLM-Ascend baselines for multiple models. It separates shared methodology from model-specific identities, target cells, Tasks, immutable Results, and Formal Reviews.

## Acceptance chain

The Control claim is bounded to the exact model/runtime/hardware/workload identity recorded in an accepted Result. A benchmark process reporting `PASS` is not itself an accepted baseline; Codex1 must complete an independent Formal Review.

## Model namespaces

- `models/glm-5.2-w8a8/`
- `models/deepseek-v4-pro-w8a8/`
- `models/deepseek-v4-flash-w8a8/`

Additional models use the same slugged namespace after a User Decision.
