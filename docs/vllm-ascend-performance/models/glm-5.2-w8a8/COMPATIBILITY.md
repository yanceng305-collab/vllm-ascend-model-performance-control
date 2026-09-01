# GLM-5.2-W8A8 Compatibility

## User-verified runtime (Decision D-019)

GLM-5.2-W8A8 uses **User-verified vLLM 0.24.0 / vLLM-Ascend 0.19.1rc2** as the known-good baseline (Decision D-019, effective 2026-09-01). This supersedes the FlagOS-aligned discovery track for GLM baseline performance work.

The FlagOS-aligned `vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1` lane is retained as a **historical reference** and potential migration target, but does not gate GLM baseline establishment or optimization.

## Pinned lane (`vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1`) - Historical Reference

Public `v0.20.2rc1` support matrix lists `GLM-5` as experimental and marks W8A8 supported. This establishes family-level source evidence only; exact GLM-5.2 architecture/config and 0.20.2 compatibility remain unverified. No pinned-lane patch requirement is established by public evidence.

## Track disposition

`USER_VERIFIED_BASELINE`: vLLM 0.24 (active, per D-019). `FLAGOS_ALIGNED`: historical reference, not required for current GLM work. `LATEST_REFERENCE`: prohibited as a substitute; may be opened only by a separate Decision/Task if needed.

## Evidence

https://github.com/vllm-project/vllm-ascend/blob/v0.20.2rc1/docs/source/user_guide/support_matrix/supported_models.md (tag commit `367b8e62da799870a7476ce34f5f7658589a8aad`, queried 2026-08-29).
