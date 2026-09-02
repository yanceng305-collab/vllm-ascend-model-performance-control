# GLM-5.2-W8A8 Baseline

Status: `USER-VERIFIED KNOWN-GOOD BASELINE` (effective 2026-09-01, supersedes prior PENDING_CODEX2_DISCOVERY state via Decision D-019).

## Identity

| Field | Value |
|---|---|
| Model | GLM-5.2-W8A8 |
| Model path | `/data/tiankuan/zyg/model/GLM-5.2-w8a8` |
| Quantization | W8A8 (Ascend quantization) |
| Image | `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3` |
| vLLM | 0.24.0+empty |
| vLLM-Ascend | 0.19.1rc2.dev1157+g6443b2a38 |
| vLLM-Ascend commit | 6443b2a38b95390e4f5174ff7ad2f8c3751e040f |
| Image identity detail | TO_CAPTURE_ON_NEXT_FAST_PREFLIGHT (digest/ID not yet recorded) |
| CANN / torch / torch_npu | TO_CAPTURE_ON_NEXT_FAST_PREFLIGHT |
| Ascend hardware | 8 physical A3/910C cards, 16 logical NPU devices |
| TP | 16 |
| DP | 1 |
| EP | N/A |

## Container baseline (frozen, User-verified)

Container name: `model-test-zyg-a3`

Complete creation command:

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

This supersedes any prior container name or command (e.g., `vllm-ascend-glm5.2-zyg`). See Decision D-019.

## Server launch baseline (frozen, User-verified)

Complete launch command:

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

Baseline semantics:
- TP: 16 logical NPU devices
- max-model-len: 70000
- gpu-memory-utilization: 0.9
- quantization: ascend
- Prefix cache: OFF
- Request logging: OFF
- Graph: ON (FULL_DECODE_ONLY mode)
- API port: vLLM default 8000
- Server log: glm52_w8a8.log

## Benchmark workload baseline (frozen)

Input lengths: 1024, 4096, 16384, 65536 tokens  
Output length: 1024 tokens  
Max concurrency: 64  
Num prompts: 256  
Dataset: random  
Endpoint: `/v1/completions`  
ignore_eos: true  
Request rate: inf  
Random range ratio: 0  
Runs per cell: 4 (run1 discarded, mean of run2/run3/run4)

See `RUNBOOK.md` and `scripts/bench-glm52-matrix.sh` for executable implementation.

## Hardware compute basis (Decision D-020; A3 basis corrected by D-024)

> **D-024 (2026-09-02)**: the A3/910C compute input `756 TFLOPS/card` was corrected by User as erroneous. Active A3/910C basis is **752 TFLOPS/card × 8 = 6016 TFLOPS** (see Decision D-024 and `hardware-normalization-config.yaml`). The `756 / 6048` values below are the superseded D-020/User-input historical record and must not be used for active normalization. H100 basis and measured value below are unchanged.

**A3/910C**: 756 TFLOPS per physical card @ FP16 (historical, superseded by D-024 → 752)  
**A3 system**: 8 cards × 756 = **6048 TFLOPS** (historical; active = 6016 per D-024)

**Measured A3 compute** (via ascend-dmi -f -t fp16 -q --all): **6019.718 TFLOPS** (evidence only; never the normalization denominator)

**H100**: 989 TFLOPS per physical card @ FP8  
**H100 system**: 16 cards × 989 = **15824 TFLOPS** (unchanged)

**Comparison class**: `ENGINEERING_REFERENCE` (precision differs: H100 FP8 vs A3 W8A8)

## Acceptance metric

**Primary acceptance metric**: Normalized Total Token Throughput

**Formula**:  
```
NormalizedThroughput = TotalTokenThroughput / PhysicalCardCount / UnifiedHardwareComputePerCard
```

**Pass condition**:  
```
(A3_Normalized / H100_Normalized) >= 0.80
```

See Decision D-020.

## Execution mode

GLM-5.2-W8A8 uses **USER-VERIFIED KNOWN-GOOD BASELINE** execution mode:

1. Fast Preflight (bounded, <5 minutes): verify NPU health, devices, container/image, model path, runtime version, server readiness
2. Run frozen baseline commands/scripts (no discovery, no improvisation)
3. Collect Evidence
4. Report Result
5. Optimization (separate OPT Tasks with independent Results)

Stage 0 discovery is not required for GLM-5.2-W8A8 baseline performance work. Stage 0 capability is retained for new servers, new hardware, unknown runtimes, and unverified models (DeepSeek, MiniMax).

## Baseline vs Optimization separation

This baseline is frozen. Any parameter changes (HCCL tuning, OMP tuning, memory allocator tuning, cudagraph_capture_sizes, KV cache tuning, max_num_seqs, scheduler tuning, batching tuning, kernel optimization, communication optimization) must be tracked as separate OPT-xxx Tasks with independent Results compared against this baseline.

Do not overwrite this baseline with optimization parameters.

## Version note

The FlagOS-aligned vLLM 0.20.2 / vLLM-Ascend 0.20.2rc1 track remains as historical/migration reference. GLM-5.2-W8A8 native performance baseline is vLLM 0.24 as User-verified. See Decision D-019.
