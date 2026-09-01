# DeepSeek-V4-Flash-W8A8 Compatibility

## Pinned lane (`vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1`)

Both pinned source trees contain DeepSeek V4 implementation files. The exact Flash architecture/config, weight quantization, and W8A8 path remain `PENDING_A3PERFRUNNER_DISCOVERY`; the source H100 note about FP8 KV cache does not identify model-weight quantization.

No pinned-lane patch requirement is established by public evidence. If a model-specific patch or newer-only support is found, it must be recorded as a separate decision and `LATEST_REFERENCE`, not folded into the aligned result.

## Track disposition

`FLAGOS_ALIGNED`: pending Stage 0 with a quantization-resolution gate. Newer support, if needed, is a separate `LATEST_REFERENCE / NON_FLAGOS_ALIGNED_REFERENCE` and cannot replace the aligned lane.

## Evidence

vLLM tag `v0.20.2` commit `bc150f50299199599673614f80d12a196f377655`; vLLM-Ascend tag `v0.20.2rc1` commit `367b8e62da799870a7476ce34f5f7658589a8aad`, queried 2026-08-29.
