# Task: VLLM-ASCEND-STAGE0B-MODEL-DISCOVERY

**Status:** `DEFERRED / WAITING_MODEL_DOWNLOAD / NOT DISPATCHABLE`

**Track:** model identity and compatibility completion; no current execution authorization.

Stage 0B is intentionally separate from Stage 0A. Do not dispatch it while model downloads are in progress. It becomes eligible only after User/Codex1 evidence indicates the relevant model downloads are complete enough for inspection and a new prompt is committed and reviewed.

## Scope when later activated

Inspect only below:

```text
MODEL_ROOT=/data/tiankuan/zyg/model
```

For each current Single-A3 candidate—GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, and MiniMax-M3—discover the actual model directory, `config.json`, architecture, quantization config/method, dtype, tokenizer, revision/source identity, completeness, and reusable hashes. Then assess vLLM `0.20.2` and vLLM-Ascend `0.20.2rc1` pinned recognition, installed runtime recognition, TP/DP/EP capability, launch flags, and model-specific blockers.

DeepSeek-V4-Pro-W8A8 remains out of the current Single-A3 scope.

## Download/hash policy

If a directory is present but files are still arriving, record `DOWNLOAD_IN_PROGRESS`; do not hash large weights and do not create a formal weight identity hash. Only after `MODEL_DOWNLOAD_COMPLETE` may Stage 0B hash `config.json`, tokenizer/config identity files, model index, and produce a weight-file manifest. Full weight SHA-256 is optional and must be a separately justified completion action; do not repeat it in later stages.

## Result states

Record model acquisition independently as `MODEL_READY`, `DOWNLOAD_IN_PROGRESS`, `MODEL_MISSING`, or `MODEL_IDENTITY_UNKNOWN`, and compatibility independently as `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`. Stage 0B has no formal dispatch prompt yet and must not be treated as `READY`.
