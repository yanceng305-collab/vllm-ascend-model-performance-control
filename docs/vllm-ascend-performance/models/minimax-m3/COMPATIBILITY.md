# MiniMax-M3 Compatibility

## Pinned lane (`vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1`)

Live GitHub tree queries on 2026-08-29 show vLLM `v0.20.2` model files `minimax_m2.py`, `minimax_text_01.py`, and `minimax_vl_01.py`, but no file named or clearly identified as MiniMax-M3. The vLLM-Ascend `v0.20.2rc1` model directory lists DeepSeek V4 files but no MiniMax module. Therefore exact MiniMax-M3 architecture and quantization support are not established in the pinned lane.

## Track disposition

`FLAGOS_ALIGNED`: `PENDING_CODEX2_DISCOVERY`; if the exact model is unsupported, status becomes `FLAGOS_ALIGNED_BASELINE_BLOCKED_MODEL_UNSUPPORTED`. A newer implementation, if investigated, must be a separate `LATEST_REFERENCE / NON_FLAGOS_ALIGNED_REFERENCE` and cannot replace the aligned lane.

## Evidence

- vLLM `v0.20.2` tree: https://github.com/vllm-project/vllm/tree/v0.20.2 (tag commit `bc150f50299199599673614f80d12a196f377655`, queried 2026-08-29).
- vLLM-Ascend `v0.20.2rc1` model tree: https://github.com/vllm-project/vllm-ascend/tree/v0.20.2rc1/vllm_ascend/models (tag commit `367b8e62da799870a7476ce34f5f7658589a8aad`, queried 2026-08-29).
