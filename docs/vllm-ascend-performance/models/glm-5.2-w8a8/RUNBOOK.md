# GLM-5.2-W8A8 Runbook

This runbook provides frozen, User-verified commands and scripts for GLM-5.2-W8A8 baseline performance testing on A3.

## Prerequisites

- A3 server with 8 physical A3/910C cards (16 logical NPU devices)
- Model downloaded to `/data/tiankuan/zyg/model/GLM-5.2-w8a8`
- Image: `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`
- No other workloads occupying NPU devices

## Fast Preflight Checklist

Before running baseline benchmarks, perform bounded fast preflight (<5 minutes):

1. **NPU availability**: `npu-smi info` shows 16 devices healthy
2. **Device health**: No errors in npu-smi
3. **Container/image exists**: `docker images | grep nightly-releases-v0.24.0rc-a3`
4. **Model path exists**: `ls -d /data/tiankuan/zyg/model/GLM-5.2-w8a8`
5. **No competing workloads**: Check if NPU devices are free
6. **Evidence root writable**: `/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`

Do not re-discover environment, re-research images, re-design TP, re-design Graph mode, or re-design benchmark. These are frozen in the baseline.

## Container Creation

Use the frozen User-verified container creation command:

```bash
cd /data/tiankuan/vllm-ascend-model-performance-control/docs/vllm-ascend-performance/models/glm-5.2-w8a8/scripts
./start-container.sh
```

Or manually:

```bash
docker run -itd \
  --name=model-test-zyg-a3 \
  --privileged=true \
  --net=host \
  --shm-size=512g \
  --device /dev/davinci0 \
  --device /dev/davinci1 \
  --device /dev/davinci2 \
  --device /dev/davinci3 \
  --device /dev/davinci4 \
  --device /dev/davinci5 \
  --device /dev/davinci6 \
  --device /dev/davinci7 \
  --device /dev/davinci8 \
  --device /dev/davinci9 \
  --device /dev/davinci10 \
  --device /dev/davinci11 \
  --device /dev/davinci12 \
  --device /dev/davinci13 \
  --device /dev/davinci14 \
  --device /dev/davinci15 \
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
  quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3 \
  /bin/bash
```

Container name: `model-test-zyg-a3`

## Server Launch (Baseline)

Inside the container, use the frozen User-verified launch command:

```bash
cd /data/tiankuan/vllm-ascend-model-performance-control/docs/vllm-ascend-performance/models/glm-5.2-w8a8/scripts
./start-server-baseline.sh
```

Or manually:

```bash
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15

MODEL="/data/tiankuan/zyg/model/GLM-5.2-w8a8"

nohup vllm serve "$MODEL" \
  --tensor-parallel-size 16 \
  --max-model-len 70000 \
  --gpu-memory-utilization 0.9 \
  --quantization ascend \
  --trust-remote-code \
  --no-enable-prefix-caching \
  --no-enable-log-requests \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  > glm52_w8a8.log 2>&1 &
```

**Wait for graph compilation to complete** (check `glm52_w8a8.log`). This may take significant time on first launch.

**Verify server readiness**:

```bash
curl http://127.0.0.1:8000/v1/models
```

Expected: JSON response listing the model.

## Benchmark Execution

Run the frozen benchmark matrix (1K/4K/16K/64K inputs, 1024 output, C64, 256 prompts, 4 runs):

```bash
cd /data/tiankuan/vllm-ascend-model-performance-control/docs/vllm-ascend-performance/models/glm-5.2-w8a8/scripts
./bench-glm52-matrix.sh all
```

Or run individual cells:

```bash
./bench-glm52-matrix.sh 1024    # 1K input only
./bench-glm52-matrix.sh 4096    # 4K input only
./bench-glm52-matrix.sh 16384   # 16K input only
./bench-glm52-matrix.sh 65536   # 64K input only
```

Results are saved to `$RESULT_ROOT` (default: `/workspace/glm52_w8a8_bench`).

Each cell produces:
- `run1.json` / `run1.log`
- `run2.json` / `run2.log`
- `run3.json` / `run3.log`
- `run4.json` / `run4.log`
- `average_run2_4.json` (aggregation: mean of run2/run3/run4; run1 discarded)
- `average_run2_4.txt` (human-readable summary)

## Server Stop

Use the controlled stop script:

```bash
cd /data/tiankuan/vllm-ascend-model-performance-control/docs/vllm-ascend-performance/models/glm-5.2-w8a8/scripts
./stop-server.sh
```

Do not use `pkill -9 python` or other methods that may affect unrelated processes.

## Benchmark Workload Semantics (Frozen)

- **Inputs**: 1024, 4096, 16384, 65536 tokens
- **Output**: 1024 tokens
- **Max concurrency**: 64
- **Num prompts**: 256
- **Dataset**: random
- **Endpoint**: `/v1/completions`
- **ignore_eos**: true
- **Request rate**: inf
- **Random range ratio**: 0
- **Runs per cell**: 4 (run1 warmup/discard, mean of run2/run3/run4)

A3PerfRunner must not modify these parameters for baseline runs. Any workload changes require a new Task with separate Result.

## Result Collection

After benchmark completion:

1. Copy raw results from `$RESULT_ROOT` to Evidence root
2. Preserve all run1-run4 JSON and logs (do not delete raw data)
3. Include `average_run2_4.json` and `average_run2_4.txt`
4. Record server log snippet (graph compilation, any errors)
5. Record benchmark stdout/stderr
6. Capture runtime identity if not already recorded (vLLM version, vLLM-Ascend version, image digest, CANN/torch/torch_npu versions)

## Optimization Workflow

Optimizations (HCCL tuning, memory tuning, graph tuning, KV cache tuning, scheduler tuning, etc.) must:

1. Be tracked as separate OPT-xxx Tasks
2. Produce independent OPT Results
3. Compare against this frozen baseline
4. Not overwrite baseline commands or Results

See Decision D-019 for baseline vs optimization separation policy.

## Notes

- This runbook is for **baseline performance measurement** only.
- Graph compilation happens on first launch and may take considerable time.
- 64K input benchmark may take several hours to complete.
- If any run has `failed != 0`, investigate before accepting that cell's average.
- Never modify benchmark raw JSON files manually.
