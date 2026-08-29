# DeepSeek-V4-Pro-W8A8 Compatibility

## Pinned lane (`vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1`)

Both pinned source trees contain DeepSeek V4 implementation files (`vllm/model_executor/models/deepseek_v4.py` and `vllm_ascend/models/deepseek_v4.py`). This is source-level architecture evidence, not proof that the exact Pro config or W8A8 method is recognized. Exact support is `PENDING_CODEX2_DISCOVERY`.

## Track disposition

`FLAGOS_ALIGNED`: pending Stage 0. If the exact Pro model is unsupported, use `FLAGOS_ALIGNED_BASELINE_BLOCKED_MODEL_UNSUPPORTED`; do not silently upgrade. A newer-only result must be `LATEST_REFERENCE / NON_FLAGOS_ALIGNED_REFERENCE`.

## Evidence

vLLM tag `v0.20.2` commit `bc150f50299199599673614f80d12a196f377655`; vLLM-Ascend tag `v0.20.2rc1` commit `367b8e62da799870a7476ce34f5f7658589a8aad`, queried 2026-08-29.
