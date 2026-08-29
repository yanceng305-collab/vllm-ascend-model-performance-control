# Task: VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION

**Status:** `READY / AWAITING EXPLICIT USER DISPATCH`

**Track:** discovery only; no performance result and no FlagOS acceptance.

## Authorization boundary

Codex2 may execute this Task only after the User explicitly dispatches this exact Task. Until then, do not connect to or operate any server. This Task is read-only and non-destructive.

## Objective

Discover every server-observable fact required to assess the three planned native vLLM-Ascend models against the `FLAGOS_ALIGNED_BASELINE` (`vLLM 0.20.2` + `vLLM-Ascend 0.20.2rc1`) and to identify the next eligible stage.

## Models

- `glm-5.2-w8a8`
- `deepseek-v4-pro-w8a8`
- `deepseek-v4-flash-w8a8`

## Required read-only probes

1. Hardware: SKU, NPU count, `npu-smi`, driver, firmware, HBM, topology, interconnect/network, OS, kernel.
2. Runtime: Python, CANN, torch, torch_npu, vLLM, vLLM-Ascend, Triton Ascend, HCCL, installed packages, container/image ID and digest.
3. Version lane: whether the exact aligned tuple exists (`vLLM 0.20.2`, `vLLM-Ascend 0.20.2rc1`, Python >=3.10,<3.12, CANN 9.0.0, PyTorch/torch_npu 2.10.0, Triton Ascend 3.2.1, Mooncake v0.3.8.post1). If absent, record the observed tuple and a non-executed preparation gap.
4. Model discovery: locate each model without modifying files; capture path, directory listing, `config.json`, architecture, model revision/SHA, file hashes, quantization config/method, dtype, KV-cache dtype, tokenizer identity, and availability.
5. Capability: using only read-only imports/introspection, determine whether installed vLLM-Ascend recognizes each architecture and quantization; record registry/module/source origins and exact errors. Compare pinned `v0.20.2rc1` public support evidence with current/newer facts; do not infer pinned support from main.
6. Runtime capability: discover supported TP/DP/EP, launch flags, graph/eager options, and whether the current environment meets prerequisites. Do not launch a service.

## Prohibited actions

No `pip install/uninstall`, apt/yum, driver/CANN changes, file/model edits/deletes, image rebuild/commit/pull, model service launch, benchmark, long-running workload, or production-container mutation. Stop and report if a probe would require stateful action.

## Evidence requirements

Create `<EVIDENCE_ROOT>/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION/<RUN_ID>/` with manifest, exact commands, timestamps, stdout/stderr, environment/package/container/device/model inventories, probe outputs, checksums, and a draft Result. Do not put secrets or credentials in Evidence or Control.

## Required immutable Result disposition

For each model report one of `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`, with evidence and next stage. Publish the first `RESULT-*.md` snapshot to Control; after publication it is immutable. Do not create a performance Result or claim PASS/FAIL.

## Return fields

Include Task ID, Run ID, server Evidence root, exact runtime tuple, hardware identity, model identities, capability findings, aligned-lane status per model, first blockers, last successful probe, prohibited actions not taken, and the proposed next Task. Explicitly distinguish `PENDING_CODEX2_DISCOVERY` from User decisions.
