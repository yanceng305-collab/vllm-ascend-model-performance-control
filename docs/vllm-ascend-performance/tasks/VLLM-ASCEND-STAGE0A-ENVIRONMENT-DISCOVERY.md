# Task: VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY

**Status:** `READY / AWAITING EXPLICIT USER DISPATCH`

**Track:** environment discovery only; no model compatibility verdict, performance result, or FlagOS acceptance.

**Hardware target:** one Ascend A3/910C server, single node, 8 cards / 16 NPU chips.

## Control binding

- Control repo: `yanceng305-collab/vllm-ascend-model-performance-control`
- Task path: `docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY.md`
- Formal dispatch prompt path: `docs/vllm-ascend-performance/tasks/CODEX2-VLLM-ASCEND-STAGE0A-DISPATCH-PROMPT.md`
- Control lineage anchor: `e354d443dc44bac3f4d71cc13b6f02c9f3ecaa0c`
- Codex2 must live query/fetch Control, verify the current prompt and Task, record `CONTROL_SHA_VERIFIED`, and stop on scope drift.

## Authorization boundary

Codex2 may execute only after explicit User dispatch of the committed Stage 0A prompt. This Task is read-only/non-destructive. Its only permitted writes are task-owned Evidence directory/files and the immutable discovery Result.

## Frozen workspace roots

```text
WORK_ROOT=/data/tiankuan/zyg
MODEL_ROOT=/data/tiankuan/zyg/model
EVIDENCE_ROOT=/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control
TASK_WORK_ROOT=/data/tiankuan/zyg/work/vllm-ascend-model-performance-control
```

Use `EVIDENCE_ROOT` for this run. Do not use `/tmp`, reuse another project's run, or search the whole server. Stage 0A may only lightly inspect `MODEL_ROOT` existence, disk usage, top-level directory names, and obvious download activity; it must not inspect model contents deeply or hash weights.

## Scope

Acquire environment facts required to decide whether Stage 1 FlagOS-aligned runtime preparation is eligible. Do not make model-specific compatibility decisions.

### Hardware

Read-only query exact Ascend SKU, physical card count, logical NPU count, existence of `/dev/davinci0` through `/dev/davinci15`, `npu-smi`, HBM, topology, firmware, and driver.

### Host

Read-only query OS/distribution, kernel, architecture, safe hostname, and disk layout/free capacity relevant to `WORK_ROOT`, `MODEL_ROOT`, and `EVIDENCE_ROOT`.

### Runtime

Read-only query Python, CANN, torch, torch_npu, vLLM, vLLM-Ascend, Triton Ascend, HCCL, Mooncake, and relevant package versions.

### Docker and images

Read-only query Docker version and safe `docker info` fields, `docker images --no-trunc`, `docker ps -a`, relevant local vLLM-Ascend image IDs/tags/digests, and fixed-name container conflicts:

```text
vllm-ascend-glm5.2-zyg
vllm-ascend-deepseek-v4-flash-zyg
vllm-ascend-minimax-m3-zyg
```

Do not pull images, create containers, or inspect/modify model containers beyond safe metadata queries.

### Container prerequisites

Verify existence/readability of `/dev/davinci0`–`/dev/davinci15`, `/dev/davinci_manager`, `/dev/devmm_svm`, `/dev/hisi_hdc`, `/usr/local/dcmi`, `/usr/local/Ascend/driver/tools/hccn_tool`, `/usr/local/bin/npu-smi`, `/usr/local/Ascend/driver/lib64/`, `/usr/local/Ascend/driver/version.info`, `/etc/ascend_install.info`, `/etc/hccn.conf`, `/data/tiankuan`, and `/home`.

### FlagOS-aligned gap

Assess the frozen target `flagos-ai/vllm-plugin-FL@release/0.2`, vLLM `0.20.2`, vLLM-Ascend `0.20.2rc1`, and its compatibility tuple. Record `ENV_READY`, `ENV_PREPARATION_REQUIRED`, or `ENV_BLOCKED`. If no direct aligned A3 image is locally available, record `NO_DIRECT_ALIGNED_IMAGE`; do not choose a newer tag.

## Explicit Stage 0A exclusions

Do not compute full model/weight hashes, traverse all large weight files, read model `config.json`, import model/tokenizer code, perform architecture/quantization probes, launch models, benchmark, install packages, pull images, create containers, or change runtime. Model download state must not become an environment blocker.

## Evidence and Result

Generate the UTC run identifier as `YYYYMMDDTHHMMSSZ`. Create `EVIDENCE_ROOT/VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY/YYYYMMDDTHHMMSSZ/`, replacing the final component with that generated timestamp, without overwriting an existing run; record root selection, exact commands, timestamps, outputs, exit codes, manifests, and checksums. Publish one immutable environment Result containing `CONTROL_SHA_VERIFIED`, environment disposition, last successful probe, first blocker, aligned runtime gap, image inventory, mount/device readiness, and whether Stage 1 may be designed. Do not publish model compatibility verdicts. Never rewrite the Result; use a supplement.
