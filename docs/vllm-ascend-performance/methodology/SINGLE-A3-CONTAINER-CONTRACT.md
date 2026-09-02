# Single-A3 Container Contract

This is the User-approved standard for a future Stage 1 FlagOS-aligned runtime preparation Task. It is a methodology contract, not an execution authorization and not a Stage 1 Task.

## Target

One Ascend A3/910C server, 8 cards / 16 NPU chips. The exact approved image identity must be frozen by a later Task from official image evidence plus Stage 0 server inventory. Do not guess a tag or digest.

## Standard docker run structure

```bash
docker run -itd \
  --name=<MODEL_CONTAINER_NAME> \
  --privileged=true \
  --net=host \
  --shm-size=512g \
  --device /dev/davinci0 --device /dev/davinci1 --device /dev/davinci2 --device /dev/davinci3 \
  --device /dev/davinci4 --device /dev/davinci5 --device /dev/davinci6 --device /dev/davinci7 \
  --device /dev/davinci8 --device /dev/davinci9 --device /dev/davinci10 --device /dev/davinci11 \
  --device /dev/davinci12 --device /dev/davinci13 --device /dev/davinci14 --device /dev/davinci15 \
  --device /dev/davinci_manager \
  --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccn.conf:/etc/hccn.conf \
  -v /data/tiankuan:/data/tiankuan \
  -v /home:/home \
  <APPROVED_VLLM_ASCEND_IMAGE> \
  /bin/bash
```

The placeholders are allowed only in this methodology contract. A formal Stage 1 Task must resolve them to a deterministic container name and approved image tag/digest before dispatch; no User hand-editing or A3PerfRunner improvisation is allowed.

## Fixed mounts and prohibitions

The device mapping, privileged mode, host network, shared memory, driver/DCMI/HCCN mounts, `/data/tiankuan:/data/tiankuan`, and `/home:/home` are fixed. Do not add `/root/.cache:/root/.cache` or use the legacy `/data:/data` mount.

Normally only the container name and approved image identity vary per model. If an image/model requires another argument, A3PerfRunner records the reason and STOPs or proposes a Control revision; it cannot permanently change this contract without a new Decision and User authorization.

## Container names

| Model | Fixed name | Notes |
|---|---|---|
| GLM-5.2-W8A8 | `model-test-zyg-a3` | Current User-verified baseline (D-019). Historical: `vllm-ascend-glm5.2-zyg` |
| DeepSeek-V4-Flash-W8A8 | `vllm-ascend-deepseek-v4-flash-zyg` | FlagOS-aligned discovery track |
| MiniMax-M3 | `vllm-ascend-minimax-m3-zyg` | FlagOS-aligned discovery track |

Future models use `vllm-ascend-<normalized-model-name>-zyg`. Do not change a model's name across later Tasks unless a Task/Decision documents a naming conflict and User authorization.

**Note**: GLM-5.2-W8A8 container name is governed by Decision D-019 User-verified baseline, not this generic contract.
