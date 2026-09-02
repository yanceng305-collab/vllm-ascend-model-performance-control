# Historical 910B Multi-Node Optimization Reference

**REFERENCE ONLY — NOT A3 EVIDENCE — NOT DIRECTLY TRANSFERABLE**

**Source**: User-provided historical engineering records (2 Excel files)
- 汇总结果(1).xlsx
- 优化总结(1).xlsx

**Hardware**: Ascend 910B  
**Topology**: Multi-node  
**Context**: GLM-class model W8A8 quantization, long-context (65K input) performance tuning

**Warning**: This document contains historical observations from 910B multi-node environment. Parameters, optimal values, and architectural conclusions ARE NOT directly transferable to single-node A3/910C TP16 environment.

---

## Historical Optimization Stages

### Stage 1: 原始基线 (Original Baseline)
- **Concurrency range**: 3.9 - 15.5
- **Output throughput**: 33.6 - 55.7 tok/s
- **E2E throughput**: 2187.5 - 3619.8 tok/s
- **Configuration**: 
  - max-num-batched-tokens: 4096
  - max-num-seqs: 16
  - speculative tokens: 5
  - cudagraph_mode: FULL_DECODE_ONLY (no explicit capture sizes)
- **Observation**: Low baseline performance

### Stage 2: 池化 (Pooling)
- **Concurrency range**: 3.9 - 15.1
- **Output throughput**: 93.0 - 151.6 tok/s (2.77x - 2.72x improvement)
- **E2E throughput**: 6048.8 - 9857.0 tok/s
- **Configuration**:
  - max-num-batched-tokens: 4096 (unchanged)
  - max-num-seqs: 8 (changed from 16)
  - speculative tokens: 5 (unchanged)
  - Added: KV cache pooling infrastructure (Mooncake/AscendStore)
- **Signal**: MAJOR PERFORMANCE IMPROVEMENT
- **Note**: **CONFOUNDED** - "池化" refers to multi-node KV cache disaggregation (Mooncake), combined with max-num-seqs reduction. NOT directly transferable to A3 single-node.

### Stage 3: 参数优化1+池化 (Parameter Optimization 1 + Pooling)
- **Output throughput**: 100.3 - 170.5 tok/s
- **Improvement over Stage 2**: +7.9% - +12.5%
- **Configuration changes from Stage 2**:
  - max-num-batched-tokens: 4096 → **2048**
  - max-num-seqs: 8 (unchanged)
  - speculative tokens: 5 → **4**
  - cudagraph_capture_sizes: (none) → **[1,2,4,8,12,16]**
- **Signal**: Incremental gain from parameter tuning
- **Note**: **CONFOUNDED** - THREE parameters changed simultaneously (max-num-batched-tokens, speculative tokens, cudagraph sizes). Cannot attribute gain to any single change.

### Stage 4: 参数优化2+池化 (Parameter Optimization 2 + Pooling)
- **Output throughput**: 105.1 - 167.1 tok/s
- **Configuration changes from Stage 3**:
  - max-num-batched-tokens: 2048 (unchanged)
  - max-num-seqs: 8 (unchanged)
  - speculative tokens: 4 (unchanged)
  - **enable_fused_mc2**: (none) → **1** (NEW)
  - **enable_npugraph_ex**: (none) → **true** (NEW)
  - cudagraph_capture_sizes: [1,2,4,8,12,16] → **[1,2,4,8,12,16,24,32,48,64,80]** (expanded)
  - **max_cudagraph_capture_size**: (none) → **80** (NEW)
- **Observation**: Mixed results vs Stage 3 (some regression at high CC)
- **Note**: **CONFOUNDED** - FOUR changes simultaneously (fused_mc2, npugraph_ex, expanded cudagraph sizes, max capture size)

### Stage 5: 参数优化3+池化（本周最优） (Parameter Optimization 3 + Pooling - Best)
- **Output throughput**: 131.0 - 184.7 tok/s
- **E2E throughput**: 8514.8 - 12005.8 tok/s
- **Improvement over original**: 3.9x - 3.3x
- **Configuration changes from Stage 4**:
  - max-num-batched-tokens: 2048 (unchanged)
  - max-num-seqs: 8 (unchanged)
  - speculative tokens: 4 (unchanged)
  - **enable_flashcomm1**: (none) → **true** (NEW)
  - enable_fused_mc2: 1 (unchanged)
  - enable_npugraph_ex: true (unchanged)
  - cudagraph_capture_sizes: [1,2,4,8,12,16,24,32,48,64,80] → **[40,80]** (simplified)
  - max_cudagraph_capture_size: 80 (unchanged)
- **Observation**: Best historical result
- **Note**: **CONFOUNDED** - TWO changes simultaneously (added flashcomm1, simplified cudagraph capture sizes)

---

## Saturation / Overload Observations

### Concurrency Sweep (汇总结果.xlsx)

**第三次测试**:
- CC 21 → 27: throughput +58% (433 → 704 tok/s)
- CC 27 → 36: throughput +11% (704 → 785 tok/s)
- CC 36 → 40: throughput **-18%** (785 → 644 tok/s) **REGRESSION**
- CC 40 → 44: throughput +38% (644 → 889 tok/s) **RECOVERY**
- CC 44 → 57: throughput +8% (889 → 957 tok/s)
- CC 57 → 63: throughput +22% (957 → 1167 tok/s)
- CC 63 → 86: throughput +13% (1167 → 1324 tok/s)
- CC 86 → 113: throughput +20% (1324 → 1583 tok/s)

**第四次测试**:
- CC 22 → 28: throughput **-2%** (525 → 517 tok/s) **STAGNATION**
- CC 28 → 35: throughput +43% (517 → 742 tok/s)
- CC 35 → 42: throughput +21% (742 → 900 tok/s)
- CC 42 → 45: throughput **-23%** (900 → 690 tok/s) **REGRESSION**
- CC 45 → 57: throughput +35% (690 → 933 tok/s) **RECOVERY**
- CC 57 → 64: throughput +14% (933 → 1065 tok/s)
- CC 64 → 85: throughput +25% (1065 → 1328 tok/s)
- CC 85 → 115: throughput **-26%** (1328 → 980 tok/s) **OVERLOAD CLIFF**

**Historical Signal**: 
- Throughput does NOT monotonically increase with concurrency
- Multiple regression/recovery cycles observed
- Possible overload cliff around CC 100-115
- **NON-TRANSFERABLE**: Optimal CC for 910B multi-node ≠ optimal CC for A3 single-node TP16

---

## Key Historical Signals

### 1. **"池化" (Pooling) Had Major Impact**
- **Signal**: 2.7x-2.9x throughput improvement (Stage 1 → Stage 2)
- **Actual change**: max-num-seqs 16→8 + multi-node KV cache disaggregation (Mooncake/AscendStore)
- **Hypothesis for A3**: Memory/resource pooling, KV cache management, or batching策略 may be important
- **NOT TRANSFERABLE**: 910B multi-node pooling architecture (Mooncake) ≠ A3 single-node architecture
- **CONFOUNDED**: Cannot separate max-num-seqs effect from pooling infrastructure effect

### 2. **Parameter Tuning Shows Incremental Gains**
- **Signal**: 7-12% improvements in Stages 3-5 over pooling baseline
- **Actual changes documented**: See stage-by-stage configuration diffs above
- **Hypothesis for A3**: Scheduler, batching, graph, or communication parameters deserve systematic exploration
- **CONFOUNDED**: Every historical optimization stage changed MULTIPLE parameters simultaneously
- **Critical limitation**: Cannot determine which specific parameter(s) drove observed gains
- **A3 strategy**: Requires isolated single-variable validation to establish causal relationships

### 3. **Concurrency Saturation is Non-Monotonic**
- **Signal**: Performance regression at certain CC ranges
- **Hypothesis for A3**: Need to find optimal concurrency/batching balance for A3 hardware
- **NOT TRANSFERABLE**: 910B optimal CC values not applicable to A3

### 4. **High Variance Across Runs**
- **Signal**: Same CC shows different throughput in 第三次 vs 第四次 测试
- **Hypothesis for A3**: Need stable, repeatable measurements (already addressed by D-023 multi-run protocol)

---

## Non-Transferable 910B-Specific Items

The following factors observed or implied in historical data are **910B MULTI-NODE SPECIFIC** and **NOT directly applicable** to A3 single-node TP16:

1. **Multi-node topology**: Inter-node communication, RDMA, HCCL multi-node optimization
2. **池化 (Pooling)**: If referring to multi-node resource pooling, KV disaggregation, or distributed memory
3. **Specific concurrency values**: Optimal CC for 910B multi-node ≠ A3 single-node
4. **AscendStore / Mooncake**: Multi-node storage disaggregation (not present in A3 single-node)
5. **Multi-node HCCL buffer sizes**: Inter-node communication tuning
6. **DP topology**: Data parallelism placement across nodes

---

## Transferable Hypotheses for A3 Optimization

Based on historical signals, the following directions deserve **isolated, single-variable validation** on A3:

### High Priority:
1. **Scheduler / Batching Parameters**
   - `max-num-batched-tokens`
   - `max-num-seqs`
   - Batching policy
   - **Rationale**: Historical "参数优化" stages showed incremental gains; scheduler/batching likely candidates

2. **Concurrency Tuning**
   - Find A3-specific optimal concurrency range
   - **Rationale**: Historical data shows non-monotonic saturation; A3 needs independent sweep

### Medium Priority:
3. **Communication-Compute Overlap** (if applicable to TP16 intra-node)
   - FlashComm capabilities
   - HCCL optimization
   - **Rationale**: May improve TP16 intra-node communication

4. **Graph Execution**
   - NPUGraph optimization
   - Graph capture configurations
   - **Rationale**: Common optimization direction for inference workloads

### Lower Priority (Require Capability Verification):
5. **MTP / Speculative Decoding**
   - If supported by current runtime
   - **Rationale**: Could improve output phase efficiency

---

## Recommendations for A3 OPT-01

1. **Start with scheduler/batching**: Most likely to transfer from 910B experience
2. **Use single-variable experiments**: Avoid confounding factors that plagued historical stages
3. **Establish A3-specific baselines**: Do not assume 910B optimal values
4. **Use FAST MICROGATE (16K)**: Efficient screening before full matrix validation
5. **Watch for non-monotonic behavior**: Historical data shows performance can regress with "improvements"

---

## Decision Reference

- D-019: GLM-5.2-W8A8 User-verified baseline override
- D-020: Hardware compute basis and normalization
- D-021: PerfControl/A3PerfRunner separation
- D-022: GitHub Release Asset Evidence Transport
- D-023: Machine-Verified Formal Result Gate

---

**Last Updated**: 2026-09-02  
**Status**: HISTORICAL REFERENCE ONLY
