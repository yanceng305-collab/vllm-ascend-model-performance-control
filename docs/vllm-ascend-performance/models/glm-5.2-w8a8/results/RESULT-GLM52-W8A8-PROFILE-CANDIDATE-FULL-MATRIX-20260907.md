# Result: GLM-5.2-W8A8 Profile Candidate Full-Matrix (Machine-Verified)

| field | value |
|---|---|
| Result ID | `RESULT-GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-20260907` |
| Model | `GLM-5.2-W8A8` |
| Result Type | `PROFILE_CANDIDATE_FULL_MATRIX` |
| Result State | `READY_FOR_FORMAL_REVIEW` |
| Formal note | `NOT_YET_FORMALLY_ACCEPTED` |
| Task | `GLM52-W8A8-PROFILE-CANDIDATE-FULL-MATRIX-VALIDATION` |
| Dispatch Control SHA | `2711b6ed366d84187a1102b60186d42c5ba198cd` |
| Evidence Review | `FULL_MATRIX_CANDIDATE_EVIDENCE_REVIEW_PASS` / `docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/EVIDENCE-REVIEW-PROFILE-CANDIDATE-FULL-MATRIX-20260907.md` |
| Review date | 2026-09-07 |
| Candidate classification | `FINAL_RECOMMENDED_PROFILE_CANDIDATE` |
| Formal OPT-01 | `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION` |

## 0. Factual issues

This document is machine-generated from `candidate-result-input.json`; all numbers below are values read from the reviewed Evidence (D-025 layout), not hand-typed.

## 1. Evidence provenance

| key | value |
|---|---|
| release id | 382481190 |
| tag | `glm52-od-profile-full-matrix-20260903` |
| tag object commit | `2711b6ed366d84187a1102b60186d42c5ba198cd` |
| published | 2026-09-04T04:41:56Z |
| asset id | 543798263 |
| asset | `fullmatrix-evidence.tar.gz` (53550 bytes) |
| asset digest | `sha256:01eb1b5f7163fe52956483fae2316851e4fcdaaa064c43301af3c69deb94ee03` |
| sidecar id | 543798262 |
| sidecar | `fullmatrix-evidence.tar.gz.sha256` (93 bytes) |
| sidecar digest | `sha256:bea018e159b2df844df896643e30e985b9b07d9eb9545543bc1341dbaaf644bc` |

| archive SHA256SUMS | True |
| MANIFEST present | True |
| control-sha match | True |
| pinned tooling | 4 files recorded |

### 2b. Runtime identity

| field | value |
|---|---|
| container | `model-test-zyg-a3` |
| image | `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3` |
| log | `/workspace/glm52_od_64k_candidate.log` |
| model_path | `/data/tiankuan/zyg/model/GLM-5.2-w8a8` |
| pid_host | `3164838` |
| port | `8000` |
| vllm | `0.24.0` |
| vllm_ascend_plugin | `ascend` |
| identical across cells | True |

### 2c. Runtime environment

| var | value |
|---|---|
| ASCEND_RT_VISIBLE_DEVICES | `0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15` |
| HCCL_BUFFSIZE | `200` |
| HCCL_OP_EXPANSION_MODE | `AIV` |
| OMP_NUM_THREADS | `1` |
| OMP_PROC_BIND | `false` |
| PYTORCH_NPU_ALLOC_CONF | `expandable_segments:True` |
| VLLM_ASCEND_BALANCE_SCHEDULING | `1` |
| VLLM_ASCEND_ENABLE_MLAPO | `1` |
| _unset | `ASCEND_LAUNCH_BLOCKING,LD_PRELOAD,VLLM_ASCEND_ENABLE_FLASHCOMM1,VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE,VLLM_VERSION` |

## 2d. Frozen profile (candidate)

| field | value |
|---|---|
| async_scheduling | `True` |
| cudagraph_mode | `FULL_DECODE_ONLY` |
| data_parallel_size | `2` |
| expert_parallel | `True` |
| gpu_memory_utilization | `0.95` |
| max_cudagraph_capture_size | `96` |
| max_model_len | `67000` |
| max_num_batched_tokens | `4096` |
| max_num_seqs | `48` |
| mtp | `OFF` |
| multistream_overlap_shared_expert | `True` |
| prefix_cache | `False` |
| tensor_parallel_size | `8` |

## 3. Matrix gate

| gate | value |
|---|---|
| matrix validation | `PASS` |
| measured runs | 12 |
| warmup discarded | 4 |
| profile identical | True |
| profile == Task expected | True |
| runtime identity identical | True |

## 4. Per-cell machine numbers

| cell | r2 | r3 | r4 | mean | min | max | stddev | CV%% | delta%% | ach%% | 80%% tgt | met |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 16K | 1935.41 | 1934.05 | 1937.61 | 1935.6900 | 1934.05 | 1937.61 | 1.466788 | 0.0758 | 102.0680 | 116.2545 | 1332.0361 | True |
| 1K | 1198.14 | 1194.81 | 1222.32 | 1205.0900 | 1194.81 | 1222.32 | 12.259062 | 1.0173 | 78.1097 | 117.8919 | 817.7593 | True |
| 4K | 1631.80 | 1629.85 | 1627.29 | 1629.6467 | 1627.29 | 1631.80 | 1.846805 | 0.1133 | 98.5534 | 105.4890 | 1235.8804 | True |
| 64K | 1772.28 | 1756.94 | 1769.89 | 1766.3700 | 1756.94 | 1772.28 | 6.739026 | 0.3815 | 90.4257 | 91.9175 | 1537.3526 | True |

per measured run success/failed counts (256/0):

- 16K: run2 256/0, run3 256/0, run4 256/0 (successful/failed)
- 1K: run2 256/0, run3 256/0, run4 256/0 (successful/failed)
- 4K: run2 256/0, run3 256/0, run4 256/0 (successful/failed)
- 64K: run2 256/0, run3 256/0, run4 256/0 (successful/failed)

## 5. Latencies / rates (run2, ms)

| cell | TTFT m/p99 | TPOT m/p99 | ITL m/p99 | req/s | out tok/s |
|---|---|---|---|---|---|
| 1K | 3754.81 / 9350.11 | 103.16 / 107.52 | 103.16 / 104.39 | 0.5900 | 599.07 |
| 4K | 74073.16 / 138934.62 | 112.03 / 186.03 | 112.03 / 1453.87 | 0.3200 | 326.36 |
| 16K | 432808.83 / 540634.43 | 78.09 / 80.09 | 78.09 / 1487.15 | 0.1100 | 113.85 |
| 64K | 2064983.47 / 2432340.60 | 46.29 / 47.43 | 46.29 / 46.22 | 0.0300 | 27.27 |

## 6. D-024 normalization basis

| term | value |
|---|---|
| A3 | 8 x 752 = 6016 |
| H100 | 16 x 989 = 15824 |
| target min | 0.8 |
| decision | `D-024` |

## 7. Candidate statement

- Classification: **FINAL_RECOMMENDED_PROFILE_CANDIDATE** (supported by the Evidence Review PASS)
- **NOT YET FORMALLY ACCEPTED** - this candidate is READY FOR FORMAL REVIEW only.
- Formal OPT-01 is independent and remains `BLOCKED_PENDING_BASELINE_VALUE_VERIFICATION`.
- No Acceptance performed by the generator.
