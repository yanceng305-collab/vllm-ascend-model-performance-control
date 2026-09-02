# Stage 0 Server Fact Acquisition

## Purpose

Stage 0 is split into `Stage 0A — Environment / Host / Container Fact Acquisition` and `Stage 0B — Model Identity / Compatibility Completion`, not merely an environment inventory. Stage 0A is the current environment-first task; Stage 0B is deferred until downloads are complete enough for inspection. Together they collect all server-observable facts needed before runtime preparation, model launch, correctness, or performance Tasks.

## Applicability

**Stage 0 required / normal path:**
- DeepSeek-V4-Flash-W8A8
- MiniMax-M3
- Future unverified models
- New or unknown server environments

**GLM-5.2-W8A8:**  
Stage 0 capability is retained for new servers, hardware changes, unknown runtimes, or when provenance re-acquisition is required. However, under Decision D-019 User-verified known-good baseline on the current server/runtime, Stage 0 does NOT gate GLM-5.2-W8A8 performance execution.

**Current execution scope:** One Ascend A3/910C server with 8 cards / 16 NPU chips. DeepSeek-V4-Pro-W8A8 is a retained multi-node candidate and is out of Stage 0 scope. Stage 0A does not require model downloads to be complete; Stage 0B records incomplete downloads as `DOWNLOAD_IN_PROGRESS`.

## Default boundary

Stage 0 is `READ-ONLY / NON-DESTRUCTIVE` and requires explicit User dispatch of an A3PerfRunner Task.

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

`SERVER-OBSERVABLE != USER INPUT REQUIRED`. PerfControl creates the discovery Task; A3PerfRunner obtains these facts after dispatch.

## Separate dispositions

The environment disposition is independent of model acquisition: `ENV_READY`, `ENV_PREPARATION_REQUIRED`, or `ENV_BLOCKED`. Model acquisition is independent per candidate: `MODEL_READY`, `DOWNLOAD_IN_PROGRESS`, `MODEL_MISSING`, or `MODEL_IDENTITY_UNKNOWN`. Compatibility remains independently `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`.
