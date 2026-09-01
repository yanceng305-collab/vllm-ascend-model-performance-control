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
5. 64K input + 1K output + C64 benchmark completion
6. Baseline performance measurement: 927.45 tok/s total throughput
7. A3 FP16 compute measurement: 6019.718 TFLOPS (via ascend-dmi)

## Current Performance

**64K baseline** (User-measured):
- Total token throughput: 927.45 tok/s
- Normalized A3 throughput: 0.153373 tok/s per TFLOPS
- Normalized H100 reference: 0.319431 tok/s per TFLOPS
- Achievement: 48.01%
- Target: ≥80%
- **Disposition**: BELOW TARGET

See [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](results/RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md)

## Frozen Artifacts

- **Container command**: See [BASELINE.md](BASELINE.md) and [scripts/start-container.sh](scripts/start-container.sh)
- **Server launch command**: See [BASELINE.md](BASELINE.md) and [scripts/start-server-baseline.sh](scripts/start-server-baseline.sh)
- **Benchmark scripts**: See [scripts/bench-glm52-matrix.sh](scripts/bench-glm52-matrix.sh) and [scripts/summarize-runs.py](scripts/summarize-runs.py)
- **Runbook**: See [RUNBOOK.md](RUNBOOK.md)

## Next Steps

1. **Complete baseline matrix**: A3PerfRunner executes 1K/4K/16K/64K cells using frozen scripts
2. **Evidence collection**: Formal Evidence-backed Results to supplement User-measured baseline
3. **Root cause analysis**: Profiling to identify bottlenecks (observed symptoms: KV cache ~85%, scheduling constraints)
4. **Optimization track**: Separate OPT Tasks (HCCL tuning, memory tuning, KV cache tuning, scheduler tuning, etc.) with controlled parameter changes
5. **Target achievement**: ≥80% normalized throughput

## Notes

- Baseline is frozen. Optimizations are tracked as separate OPT Tasks with independent Results.
- FlagOS-aligned 0.20.2 track remains as historical/migration reference but does not gate GLM-5.2-W8A8 native 0.24 performance work.
- Decision D-019: GLM-5.2-W8A8 User-verified baseline override
- Decision D-020: Hardware compute basis and normalization policy
