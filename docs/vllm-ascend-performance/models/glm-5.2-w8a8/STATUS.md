# GLM-5.2-W8A8 Status

**Status**: `USER-VERIFIED KNOWN-GOOD BASELINE` (effective 2026-09-01, per Decision D-019)

**Execution mode**: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION

**Current baseline**: vLLM 0.24.0+empty / vLLM-Ascend 0.19.1rc2.dev1157+g6443b2a38

**Stage 0 discovery**: Not required for GLM-5.2-W8A8 baseline performance work. Stage 0 capability is retained for new servers, new hardware, unknown runtimes, and unverified models.

## Completed by User

1. A3 container creation (`model-test-zyg-a3`)
2. vLLM 0.24 runtime verification
3. GLM-5.2-W8A8 TP16 successful launch with FULL_DECODE_ONLY graph mode
4. Graph compilation success
5. **Complete baseline matrix measurement** (1K/4K/16K/64K input + 1K output + C64)
6. A3 FP16 compute measurement: 6019.718 TFLOPS (via ascend-dmi)

## Current Performance

**Baseline matrix** (User-measured and User-provided matrix summary):

| Cell | A3 Total Throughput (tok/s) | H100 Reference (tok/s) | Achievement | Disposition | Status |
|---|---|---|---|---|---|
| 1K | 676.60 | 2688.71 | 65.84% | BELOW TARGET | User-provided matrix summary, Evidence pending |
| 4K | 820.76 | 4063.45 | 52.85% | BELOW TARGET | User-provided matrix summary, Evidence pending |
| 16K | 957.94 | 4379.60 | 57.23% | BELOW TARGET | User-provided matrix summary, Evidence pending |
| 64K | 927.59 | 5054.66 | 48.01% | BELOW TARGET | User-provided matrix summary, Evidence pending |

**Target**: ≥80% normalized throughput for each cell

**64K historical baseline** (User-measured 2026-09-01):
- Total token throughput: 927.45 tok/s
- Normalized A3 throughput: 0.153348214285714 tok/s per TFLOPS
- Normalized H100 reference: 0.319429979777553 tok/s per TFLOPS
- Achievement: 48.01%
- See [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](results/RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md)

**64K matrix summary** (User-provided XLSX 2026-09-02): 927.59 tok/s (used in table above, difference: 0.14 tok/s)

## Frozen Artifacts

- **Container command**: See [BASELINE.md](BASELINE.md) and [scripts/start-container.sh](scripts/start-container.sh)
- **Server launch command**: See [BASELINE.md](BASELINE.md) and [scripts/start-server-baseline.sh](scripts/start-server-baseline.sh)
- **Benchmark scripts**: See [scripts/bench-glm52-matrix.sh](scripts/bench-glm52-matrix.sh) and [scripts/summarize-runs.py](scripts/summarize-runs.py)
- **Runbook**: See [RUNBOOK.md](RUNBOOK.md)

## Next Steps

1. **Evidence formalization**: A3PerfRunner executes Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION) after User dispatch (Task ID + DISPATCH_CONTROL_SHA + Authorization: EXECUTE) to extract and formalize raw benchmark Evidence from the existing container without re-running benchmarks. Runner output is Evidence only (raw artifacts, MANIFEST, COMMANDS, SHA256SUMS, runtime identity, Run2/3/4 calculations, comparison summary, final Runner Report)
2. **Evidence review**: PerfControl receives the Evidence, independently reproduces the Run2/Run3/Run4 recalculation, and authors four formal Evidence-backed `RESULT-*.md` documents (one per cell: 1K/4K/16K/64K) with complete provenance
3. **Baseline matrix review**: PerfControl performs Formal Review and Formal Acceptance per cell
4. **Cross-cell performance analysis**: Analyze performance trends across input lengths (1K→4K→16K→64K)
5. **Root cause analysis**: Profiling to identify bottlenecks (observed symptoms: KV cache ~85%, scheduling constraints)
6. **Optimization track**: Separate OPT Tasks (HCCL tuning, memory tuning, KV cache tuning, scheduler tuning, etc.) with controlled parameter changes
7. **Target achievement**: ≥80% normalized throughput for all cells

## Notes

- Baseline is frozen. Optimizations are tracked as separate OPT Tasks with independent Results.
- FlagOS-aligned 0.20.2 track remains as historical/migration reference but does not gate GLM-5.2-W8A8 native 0.24 performance work.
- Decision D-019: GLM-5.2-W8A8 User-verified baseline override
- Decision D-020: Hardware compute basis and normalization policy
