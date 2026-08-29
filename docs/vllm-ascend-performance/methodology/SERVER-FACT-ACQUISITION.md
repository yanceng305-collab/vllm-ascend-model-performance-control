# Stage 0 Server Fact Acquisition

## Purpose

Stage 0 is `Server Fact Acquisition / Compatibility Discovery`, not merely an environment inventory. It collects all server-observable facts needed before runtime preparation, model launch, correctness, or performance Tasks.

For this revision the execution scope is one Ascend A3/910C server with 8 cards / 16 NPU chips and three independent candidates: GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, and MiniMax-M3. DeepSeek-V4-Pro-W8A8 is a retained multi-node candidate and is out of scope.

## Default boundary

Stage 0 is `READ-ONLY / NON-DESTRUCTIVE` and requires explicit User dispatch of a Codex2 Task.

### Allowed

- Read files and model `config.json`.
- Query versions, packages, containers, devices, topology, HBM, HCCL, OS, kernel, and network.
- Run `npu-smi`, `docker inspect`, `pip show/list`, and read-only Python import/capability probes.
- Inspect vLLM-Ascend model registry and architecture recognition.
- Save command output, logs, manifests, and checksums under the server Evidence root.

### Prohibited

- Install/uninstall packages or modify system configuration.
- Delete or modify files/models, commit containers, or change drivers/CANN.
- Start a formal model service or run a long benchmark.
- Modify a production container.

Any stateful preparation, image rebuild, model launch, or benchmark requires a separate Task and User approval.

## Required answers

The immutable Stage 0 Result must answer:

1. Hardware SKU, NPU count, topology, HBM, driver, and firmware.
2. Runtime tuple: OS/kernel, Python, CANN, torch, torch_npu, vLLM, vLLM-Ascend, Triton Ascend, HCCL, image/container identity.
3. Whether the aligned `vLLM 0.20.2 + vLLM-Ascend 0.20.2rc1` environment already exists.
4. If absent, the evidence-based preparation plan, without performing it.
5. Model path, config, architecture, revision/SHA, file hashes, quantization, dtype, KV-cache dtype, tokenizer, and availability.
6. Whether official `v0.20.2rc1` source recognizes the architecture and quantization; record support evidence separately from current main/newer releases.
7. Actual supported TP/DP/EP and launch parameters discoverable in the installed runtime.
8. Aligned status: `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`.
9. The next eligible stage.

`SERVER-OBSERVABLE != USER INPUT REQUIRED`. Codex1 creates the discovery Task; Codex2 obtains these facts after dispatch.
