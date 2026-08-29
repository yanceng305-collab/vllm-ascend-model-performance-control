# Codex2 Dispatch Prompt: Stage 0A Environment / Host / Container Fact Acquisition

You are Codex2 executing `VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY` for Control repo `https://github.com/yanceng305-collab/vllm-ascend-model-performance-control`.

## Control binding and drift gate

- Task ID: `VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY`
- Task path: `docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY.md`
- Prompt path: `docs/vllm-ascend-performance/tasks/CODEX2-VLLM-ASCEND-STAGE0A-DISPATCH-PROMPT.md`
- Control lineage anchor: `e354d443dc44bac3f4d71cc13b6f02c9f3ecaa0c`
- Formal artifact rule: this committed Markdown file is the authoritative handoff; terminal text is not a substitute.

At execution start, live query/fetch the Control repo, verify current `main` HEAD, and read the current Task and this prompt from that checkout. Record the verified SHA as `CONTROL_SHA_VERIFIED`. If files differ from this artifact or a newer HEAD changes scope/safety, report drift and STOP; do not execute an old prompt.

This prompt is dispatch-ready but is not authorization by itself. Execute only after the User explicitly dispatches this exact committed prompt and Task. Execute only read-only, non-destructive discovery. The only permitted writes are this Task's own Evidence directory/files and its immutable environment Result.

## Scope

Hardware target: one Ascend A3/910C server, single node, 8 cards / 16 NPU chips. This Stage 0A covers environment, host, Docker, image inventory, mount/device prerequisites, workspace capacity, and FlagOS-aligned runtime readiness only.

Do not perform Stage 0B model identity/compatibility discovery. Do not inspect model configs or tokenizer code. Current model downloads may continue independently.

## Frozen workspace roots

```text
WORK_ROOT=/data/tiankuan/zyg
MODEL_ROOT=/data/tiankuan/zyg/model
EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control
TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control
```

Do not search the entire server. At most, lightly confirm `MODEL_ROOT` existence, disk usage, visible top-level directory names, and obvious download activity; do not read model contents or hash weights.

## Stage 0A read-only probes

### Hardware

Query exact Ascend SKU, physical card count, logical NPU count, `npu-smi`, HBM, topology, firmware, driver, and existence of `/dev/davinci0` through `/dev/davinci15`, `/dev/davinci_manager`, `/dev/devmm_svm`, and `/dev/hisi_hdc`.

### Host and workspace

Query OS/distribution, kernel, architecture, safe hostname, disk layout/free capacity relevant to `WORK_ROOT`, `MODEL_ROOT`, and `EVIDENCE_ROOT`, `/data/tiankuan` existence, and `/home` existence.

### Runtime

Query Python, CANN, torch, torch_npu, vLLM, vLLM-Ascend, Triton Ascend, HCCL, Mooncake, and relevant package versions. Determine whether the exact `FLAGOS_ALIGNED` tuple exists: FlagOS `release/0.2`, vLLM `0.20.2`, vLLM-Ascend `0.20.2rc1`, Python >=3.10,<3.12, CANN 9.0.0, PyTorch/torch_npu 2.10.0/2.10.0, Triton Ascend 3.2.1, Mooncake v0.3.8.post1.

### Docker and images

Query Docker version and safe `docker info` fields, `docker images --no-trunc`, `docker ps -a`, relevant local vLLM-Ascend image IDs/tags/digests, and fixed-name conflicts for `vllm-ascend-glm5.2-zyg`, `vllm-ascend-deepseek-v4-flash-zyg`, and `vllm-ascend-minimax-m3-zyg`. Do not pull images, create containers, or inspect/modify runtime state beyond safe metadata queries.

### Container contract prerequisites

Verify existence/readability of `/usr/local/dcmi`, `/usr/local/Ascend/driver/tools/hccn_tool`, `/usr/local/bin/npu-smi`, `/usr/local/Ascend/driver/lib64/`, `/usr/local/Ascend/driver/version.info`, `/etc/ascend_install.info`, and `/etc/hccn.conf`.

### Official image boundary

Public vLLM-Ascend `v0.20.2rc1` evidence defines A3 carriers `Dockerfile.a3` and `Dockerfile.a3.openEuler`, but does not provide a final image digest for this server. Record local image evidence and mark selection unresolved unless official evidence and local inventory align. If no direct aligned A3 image is usable, record `NO_DIRECT_ALIGNED_IMAGE`; do not select a newer image silently.

## Prohibited actions

No `docker pull`, `docker run`, image build/commit, model launch, benchmark, package install/uninstall/upgrade, driver/CANN changes, model edits/deletes, full weight hashing, model imports, architecture/quantization probes, runtime changes, or long-running workload. Stage 0A may create only its task-owned Evidence files and must not modify/delete other Evidence.

## Evidence root and run ID

Use the fixed `EVIDENCE_ROOT` above. Record any read-only selection check and do not reuse another project's run. Generate a UTC run ID automatically at execution start in `YYYYMMDDTHHMMSSZ` form. Create `EVIDENCE_ROOT/VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY/YYYYMMDDTHHMMSSZ/` without overwriting an existing run. Do not ask User to replace a path or ID.

## Immutable Result

Write a manifest, verified Control SHA, exact commands, timestamps, outputs, exit codes, hardware/runtime/Docker inventories, image IDs/digests/tags, device and mount readiness, workspace capacity, aligned runtime gap, `ENV_READY` / `ENV_PREPARATION_REQUIRED` / `ENV_BLOCKED`, first blocker, last successful probe, prohibited actions not taken, and whether Stage 1 may be designed. Do not assign model compatibility verdicts. Publish one immutable environment Result to Control; do not rewrite it, use a supplement for corrections.
