# GLM-5.2-W8A8 Status

**Status**: `BASELINE ESTABLISHED` (Evidence-backed baseline matrix formally accepted 2026-09-02, corrected 2026-09-02)

**Execution mode**: USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → **OPTIMIZATION** (current phase)

**Current baseline**: vLLM 0.24.0+empty / Image nightly-releases-v0.24.0rc-a3

**Stage 0 discovery**: Not required for GLM-5.2-W8A8 baseline performance work. Stage 0 capability is retained for new servers, new hardware, unknown runtimes, and unverified models.

## Completed by User

1. A3 container creation (`model-test-zyg-a3`)
2. vLLM 0.24 runtime verification
3. GLM-5.2-W8A8 TP16 successful launch with FULL_DECODE_ONLY graph mode
4. Graph compilation success
5. **Complete baseline matrix measurement** (1K/4K/16K/64K input + 1K output + C64)
6. A3 FP16 compute measurement: 6019.718 TFLOPS (via ascend-dmi)

## Current Performance

**Evidence-backed baseline matrix** (Evidence run: run-20260902-140958, corrected 2026-09-02):

| Cell | A3 Total Throughput (tok/s) | H100 Reference (tok/s) | 80% Target A3 (tok/s) | Achievement | Disposition | Status |
|---|---|---|---|---|---|---|
| 1K | **676.60** | 2688.71 | 817.76 | 66.19% | BELOW TARGET | Evidence-backed ACCEPTED (corrected) |
| 4K | 820.76 | 4063.45 | 1235.88 | 53.13% | BELOW TARGET | Evidence-backed ACCEPTED |
| 16K | **957.94** | 4379.60 | 1332.04 | 57.53% | BELOW TARGET | Evidence-backed ACCEPTED (corrected) |
| 64K | 927.59 | 5054.66 | 1537.35 | 48.27% | BELOW TARGET | Evidence-backed ACCEPTED |

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz` (SHA256: `8818e4ffa...01816d2`)  
**Evidence Location**: GitHub Release `evidence-test-glm52-run-20260902-140958` (Decision D-022)  
**DISPATCH_CONTROL_SHA**: `26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5`

**Runtime Identity** (corrected): Container `model-test-zyg-a3`, Image `nightly-releases-v0.24.0rc-a3`, vLLM `0.24.0+empty`

**Target**: ≥80% normalized throughput for each cell

**Performance Gap**: All four cells below 80% normalized target (active basis D-024, 6016). Baseline establishes formal reference for optimization tracking.

**Correction Note**: Original Results (commit 371f5f0) contained runtime identity transcription error and two calculation rounding errors. Correction Supplement created; original Results superseded but unchanged. Use corrected values: 1K=676.60 (was 676.59), 16K=957.94 (was 957.93).

**Hardware basis correction (2026-09-02, D-024)**: User corrected the A3/910C compute input; active basis is 752 TFLOPS/card × 8 = **6016 TFLOPS** (was 756 × 8 = 6048). H100 unchanged (989 × 16 = 15824). Measured 6019.718 TFLOPS remains evidence-only. All active achievements/80% targets above are machine-recomputed on 6016 (see [CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902](results/CORRECTION-SUPPLEMENT-HARDWARE-NORMALIZATION-20260902.md)). Immutable Results and the first correction supplement remain unchanged.

**64K historical baseline** (User-measured 2026-09-01):
- Total token throughput: 927.45 tok/s
- Normalized A3 throughput: 0.153348214285714 tok/s per TFLOPS
- Normalized H100 reference: 0.319429979777553 tok/s per TFLOPS
- Achievement: 48.01% (as recorded in the immutable historical Result; active D-024 basis value is 48.27% on 927.59)
- See [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](results/RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md) (immutable, unchanged)

**64K Evidence-backed** (2026-09-02): 927.59 tok/s (used in table above; difference from historical: +0.14 tok/s, within variance)

**OPT-01 Preflight (2026-09-02, read-only)**: outcome `RUNTIME_IDENTITY_MISMATCH` / Gate A `NO_PROCESS` → effective `max_num_batched_tokens` **UNVERIFIED** (no guess). The accepted GLM-5.2-W8A8 baseline runtime was NOT active at observation time; OPT-01 screening remains **BLOCKED**, candidate selection NOT AUTHORIZED. Evidence: GitHub Release `preflight-opt01-20260902-085628` (asset `GLM52-W8A8-OPT01-PREFLIGHT-run-20260902-085628.tar.gz`). `READ-ONLY PREFLIGHT EVIDENCE — NOT FORMAL BASELINE RESULT`. Re-observation requires User authorization to restore the accepted GLM baseline runtime.

**Manual runtime (2026-09-02)** — User manually restored GLM-5.2-W8A8 vLLM service (operational variant, NOT exact frozen baseline replay; see [MANUAL-RUNTIME-OBSERVATION-20260902.md](MANUAL-RUNTIME-OBSERVATION-20260902.md)). `max_num_batched_tokens` remains **UNVERIFIED**. Manual 16K exploratory microgate **COMPLETED (2026-09-02)**: Run2 total token throughput 960.45 tok/s vs accepted 957.94 → machine-computed delta **+0.262%** → **MANUAL EXPLORATORY MICROGATE: NO_MATERIAL_GAIN** (below +2%; not formal OPT-01 screening; not a regression; 256 success / 0 failed). Formal OPT-01 screening stays **BLOCKED / NOT YET AUTHORIZED**; future candidate families recorded as reference-only (scheduler 4096 / graph&scheduler alignment / official knobs / later families).

**Exploratory task (2026-09-02)**: `GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE` created - **READY / PENDING USER DISPATCH** (Task: [TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE.md](TASK-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE.md); Prompt: [A3PERFRUNNER-PROMPT-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE.md](A3PERFRUNNER-PROMPT-GLM52-W8A8-OFFICIAL-DERIVED-A3-64K-COMPAT-PROFILE-MICROGATE.md)). Validates the official-derived A3 profile (upstream GLM-5.2-W8A8 single-node recommendation) under the frozen `max-model-len=70000`: startup + 70K capacity gate, then 16K two-run microgate; no auto-64K; leave service running. Independent exploratory branch - NOT Formal OPT-01; NOT a baseline candidate.

## Frozen Artifacts

- **Container command**: See [BASELINE.md](BASELINE.md) and [scripts/start-container.sh](scripts/start-container.sh)
- **Server launch command**: See [BASELINE.md](BASELINE.md) and [scripts/start-server-baseline.sh](scripts/start-server-baseline.sh)
- **Benchmark scripts**: See [scripts/bench-glm52-matrix.sh](scripts/bench-glm52-matrix.sh) and [scripts/summarize-runs.py](scripts/summarize-runs.py)
- **Runbook**: See [RUNBOOK.md](RUNBOOK.md)

## Next Steps

1. **Baseline established**: Evidence-backed baseline matrix formally accepted (all four cells: 1K/4K/16K/64K)
2. **Optimization track begins**: Create OPT Tasks (HCCL tuning, memory tuning, KV cache tuning, scheduler tuning, etc.) with controlled parameter changes
3. **Target achievement**: ≥80% normalized throughput for all cells
4. **Cross-cell performance analysis**: Analyze performance trends across input lengths
5. **Root cause analysis**: Profiling to identify bottlenecks (observed symptoms: KV cache ~85%, scheduling constraints)

## Notes

- Baseline is frozen. Optimizations are tracked as separate OPT Tasks with independent Results.
- FlagOS-aligned 0.20.2 track remains as historical/migration reference but does not gate GLM-5.2-W8A8 native vLLM 0.24 performance work.
- Decision D-019: GLM-5.2-W8A8 User-verified baseline override
- Decision D-020: Hardware compute basis and normalization policy (historical; A3 compute-basis portion superseded by D-024)
- Decision D-021: PerfControl/A3PerfRunner separation (Runner produces Evidence; PerfControl produces formal Results)
- Decision D-022: GitHub Release Asset Evidence Transport
- Decision D-024: A3/910C hardware compute basis correction (active basis 752 × 8 = 6016)
