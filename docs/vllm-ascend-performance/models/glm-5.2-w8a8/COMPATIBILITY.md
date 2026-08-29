# GLM-5.2-W8A8 Compatibility

## Pinned lane (`vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1`)

Public `v0.20.2rc1` support matrix lists `GLM-5` as experimental and marks W8A8 supported. This establishes family-level source evidence only; exact GLM-5.2 architecture/config and installed capability are `PENDING_CODEX2_DISCOVERY`.

No pinned-lane patch requirement is established by public evidence. Any required model patch must be discovered and separately authorized; a newer-only implementation cannot be silently backported into this baseline.

## Track disposition

`FLAGOS_ALIGNED`: pending Stage 0. `LATEST_REFERENCE`: prohibited as a substitute; may be opened only by a separate Decision/Task if pinned support is blocked.

## Evidence

https://github.com/vllm-project/vllm-ascend/blob/v0.20.2rc1/docs/source/user_guide/support_matrix/supported_models.md (tag commit `367b8e62da799870a7476ce34f5f7658589a8aad`, queried 2026-08-29).
