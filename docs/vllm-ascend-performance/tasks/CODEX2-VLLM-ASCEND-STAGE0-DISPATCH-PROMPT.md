# Codex2 Dispatch Prompt: Stage 0 Server Fact Acquisition

You are Codex2 executing `VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION` for Control repo `https://github.com/yanceng305-collab/vllm-ascend-model-performance-control`.

This is the explicit User dispatch for that Task. Execute only the read-only, non-destructive discovery described below. Do not run a model service or benchmark. Do not install, uninstall, upgrade, rebuild, pull, modify, or delete anything.

## Scope

Models: `glm-5.2-w8a8`, `deepseek-v4-pro-w8a8`, `deepseek-v4-flash-w8a8`.

Target lane: `FLAGOS_ALIGNED`, defined by FlagOS `release/0.2`, vLLM `0.20.2`, vLLM-Ascend `0.20.2rc1`, Python >=3.10,<3.12, CANN 9.0.0, PyTorch/torch_npu 2.10.0/2.10.0, Triton Ascend 3.2.1, Mooncake v0.3.8.post1. Newer versions, if observed, are facts only and must be labeled `LATEST_REFERENCE / NON_FLAGOS_ALIGNED_REFERENCE`.

## Allowed probes

Read files/configs; query `npu-smi`, `docker inspect`, package/version metadata, Python read-only imports/introspection, model directories and hashes, vLLM/vLLM-Ascend registries, architecture recognition, device/topology/HBM/network/OS/kernel/HCCL facts, and supported launch flags. Capture exact commands, timestamps, stdout/stderr, and exit codes.

## Required answers

For hardware/runtime: SKU, NPU count, driver, firmware, HBM, topology, OS/kernel, Python, CANN, torch, torch_npu, vLLM, vLLM-Ascend, Triton Ascend, HCCL, Mooncake, image/container ID/digest, and whether the exact aligned tuple exists.

For each model: actual path, config, architecture, revision/SHA, file hashes, quantization method/config, dtype, KV-cache dtype, tokenizer, availability, registry recognition, import/module/source origins, exact capability errors, and supported TP/DP/EP/launch flags discoverable without launching.

Assign one status per model: `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`. State the next eligible stage and distinguish server facts from User decisions.

## Prohibited

No package or system changes, no driver/CANN changes, no model edits, no image pull/rebuild/commit, no service launch, no benchmark, and no long-running workload. Stop and report if a requested fact requires a prohibited action.

## Evidence and Result

Create `<EVIDENCE_ROOT>/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION/<RUN_ID>/` with manifest, commands, logs, inventories, probes, and checksums. Publish one immutable `RESULT-*.md` to the Control repo after execution. Do not include credentials or secrets. Do not rewrite the Result after publication; use a supplement for corrections.
