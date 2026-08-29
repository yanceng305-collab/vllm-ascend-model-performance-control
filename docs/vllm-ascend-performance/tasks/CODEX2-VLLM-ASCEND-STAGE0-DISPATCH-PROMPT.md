# Codex2 Dispatch Prompt: Stage 0A/0B Server Fact Acquisition

You are Codex2 executing `VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION` for Control repo `https://github.com/yanceng305-collab/vllm-ascend-model-performance-control`.

## Control binding and drift gate

- Task ID: `VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION`
- Task path: `docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION.md`
- Prompt path: `docs/vllm-ascend-performance/tasks/CODEX2-VLLM-ASCEND-STAGE0-DISPATCH-PROMPT.md`
- Control lineage anchor: `17672b16f665f74ff6ad45ab344a8054fc75dc9b`
- Formal artifact rule: this committed Markdown file is the authoritative handoff; terminal text is not a substitute.

At execution start, live query/fetch the Control repo, verify the current `main` HEAD, and read the current Task and this prompt from that checkout. Record the verified SHA as `CONTROL_SHA_VERIFIED`. If files differ from this artifact or a newer HEAD changes scope/safety, report drift and STOP; do not execute an old prompt.

This prompt is dispatch-ready but is not authorization by itself. Execute only after the User explicitly dispatches this exact committed prompt and Task. Execute only read-only, non-destructive discovery; do not create containers, start models, benchmark, install, upgrade, pull images, or modify runtime.

## Scope and sequencing

Hardware target: one Ascend A3/910C server, 8 cards / 16 NPU chips.

Current Single-A3 candidates: `glm-5.2-w8a8`, `deepseek-v4-flash-w8a8`, and `minimax-m3`. `deepseek-v4-pro-w8a8` is a project-pool `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` and is explicitly out of scope.

Run two independent discovery tracks:

### Stage 0A — Environment / Host / Container Fact Acquisition

Prioritize hardware, `/dev/davinci0`–`/dev/davinci15`, host OS/distribution, Docker version, driver, firmware, CANN, Python, torch/torch_npu, existing vLLM/vLLM-Ascend, existing images and containers, image IDs/digests/tags, container prerequisites, required host mount sources, `/data/tiankuan` existence/free space, `/home`, and the `FLAGOS_ALIGNED` runtime gap. Stage 0A does not require model downloads to be complete.

### Stage 0B — Model Identity / Compatibility Completion

Inspect only under `MODEL_ROOT` and do not search the entire server. For each in-scope model, locate actual directories without guessing names; capture path, directory listing, config, architecture, revision/SHA, file hashes, quantization config/method, dtype, KV-cache dtype, tokenizer, and completeness. If a directory exists but files are still arriving, record `DOWNLOAD_IN_PROGRESS`; do not convert that into an environment blocker. If absent, record `MODEL_MISSING`.

## Frozen workspace roots

```text
WORK_ROOT=/data/tiankuan/zyg
MODEL_ROOT=/data/tiankuan/zyg/model
EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control
TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control
```

Use `MODEL_ROOT` for model discovery and `TASK_WORK_ROOT` for any task-owned non-runtime scratch bookkeeping that is strictly necessary and safe. Do not ask the User to replace paths or IDs.

## Allowed read-only probes

Read files/configs; query `npu-smi`, `docker version`, `docker images --no-trunc`, `docker ps -a`, `docker inspect`, package/version metadata, Python imports/introspection, model directories/hashes, vLLM/vLLM-Ascend registries, architecture recognition, device/topology/HBM/network/OS/kernel/HCCL facts, supported launch flags, filesystem existence, and disk capacity. Capture exact commands, timestamps, stdout/stderr, and exit codes.

For image readiness, public official evidence currently shows vLLM-Ascend `v0.20.2rc1` workflow carriers `Dockerfile.a3` and `Dockerfile.a3.openEuler`, and tag-triggered version image publishing. It does not establish a final usable image digest for this server. Record local image inventory and mark image selection unresolved unless both official evidence and server evidence support it. If no direct aligned A3 image is usable, record `NO_DIRECT_ALIGNED_IMAGE`; do not silently select a newer image.

## Required answers and independent dispositions

Record environment disposition separately as `ENV_READY`, `ENV_PREPARATION_REQUIRED`, or `ENV_BLOCKED`.

For each in-scope model record acquisition state `MODEL_READY`, `DOWNLOAD_IN_PROGRESS`, `MODEL_MISSING`, or `MODEL_IDENTITY_UNKNOWN`, plus compatibility status `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`. One model's state must not automatically fail another.

Compare pinned `vLLM 0.20.2` / `vLLM-Ascend 0.20.2rc1` facts separately from any newer `LATEST_REFERENCE / NON_FLAGOS_ALIGNED_REFERENCE`. Do not infer pinned support from current main.

## Prohibited actions

No `docker pull`, `docker run`, image build/commit, service launch, benchmark, pip/apt/yum changes, driver/CANN changes, model edits/deletes, runtime configuration changes, or long-running workload. Stage 0 may create only its own Evidence directory and files; it must not modify or delete other Evidence.

## Evidence root and run ID

Use `EVIDENCE_ROOT` above. If a clearly belonging project Evidence workspace already exists under that root, record the read-only selection evidence; never reuse another project's run. Otherwise use the same fixed root. Generate a UTC run ID automatically at execution start in `YYYYMMDDTHHMMSSZ` form and create `EVIDENCE_ROOT/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION/YYYYMMDDTHHMMSSZ/` without overwriting an existing run. Creating this task-owned directory and writing Evidence files is allowed bookkeeping.

## Immutable Result

Write manifest, verified Control SHA, exact commands, timestamps, logs, inventories, probes, selected Evidence root, environment disposition, model-scoped states, checksums, first blockers, last successful probes, prohibited actions not taken, and next eligible stages. Publish one immutable `RESULT-*.md` to Control after execution. Do not include secrets. Do not rewrite the Result; use a supplement for corrections. Do not create a performance Result or claim PASS/FAIL.
