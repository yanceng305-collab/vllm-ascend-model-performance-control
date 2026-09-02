# GLM-5.2-W8A8 Results

## Baseline Matrix Status

**Complete Evidence-backed baseline matrix established** (Evidence run: run-20260902-140958, corrected 2026-09-02):
- 1K input + 1K output, C64: **676.60 tok/s** (Achievement: 65.84%, BELOW TARGET)
- 4K input + 1K output, C64: **820.76 tok/s** (Achievement: 52.85%, BELOW TARGET)
- 16K input + 1K output, C64: **957.94 tok/s** (Achievement: 57.23%, BELOW TARGET)
- 64K input + 1K output, C64: **927.59 tok/s** (Achievement: 48.01%, BELOW TARGET)

**Evidence Archive**: `GLM52-W8A8-BASELINE-EVIDENCE-run-20260902-140958.tar.gz`  
**Archive SHA256**: `8818e4ffaf88a23989c36f0a17376843f8078adc522a32bddf682aed401816d2`  
**Evidence Location**: GitHub Release Asset `evidence-test-glm52-run-20260902-140958`  
**DISPATCH_CONTROL_SHA**: `26eb575430bc1494f7d8d964a7ba4e16a4e0a2c5`

**Runtime Identity** (corrected): Container `model-test-zyg-a3`, Image `nightly-releases-v0.24.0rc-a3`, vLLM `0.24.0+empty`

**Target**: ≥80% normalized throughput (per Decision D-020). All four cells **BELOW TARGET**; formal baseline established for optimization tracking.

## Baseline Results

| Result ID | Date | Status | Workload | Throughput | Achievement | Disposition |
|---|---|---|---|---|---|---|
| [CORRECTION-SUPPLEMENT-BASELINE-EVIDENCE-run-20260902-140958](CORRECTION-SUPPLEMENT-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | **AUTHORITATIVE** | All cells correction | See below | See below | **USE THIS** |
| [RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | SUPERSEDED | 1K input + 1K output, C64 | ~~676.59~~ → **676.60** tok/s | 65.84% | Superseded by correction (runtime ID + calculation) |
| [RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | SUPERSEDED | 4K input + 1K output, C64 | 820.76 tok/s | 52.85% | Superseded by correction (runtime ID only; value correct) |
| [RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | SUPERSEDED | 16K input + 1K output, C64 | ~~957.93~~ → **957.94** tok/s | 57.23% | Superseded by correction (runtime ID + calculation) |
| [RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-run-20260902-140958](RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-run-20260902-140958.md) | 2026-09-02 | SUPERSEDED | 64K input + 1K output, C64 | 927.59 tok/s | 48.01% | Superseded by correction (runtime ID only; value correct) |
| [RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED](RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md) | 2026-09-01 | HISTORICAL | 64K input + 1K output, C64 | 927.45 tok/s | 48.01% | Historical baseline |

## Notes

- **Correction Supplement (2026-09-02)**: Original four Results contained runtime identity transcription error (incorrectly recorded as vLLM 0.6.4.post1; actual: vLLM 0.24.0+empty) and two calculation rounding errors (1K: 676.59→676.60; 16K: 957.93→957.94). Original Result files remain unchanged per immutability rules. **Use corrected values from Supplement for all baseline tracking.**
- **Evidence-backed baseline matrix**: All four cells (1K/4K/16K/64K) formally established with Evidence-backed Results from A3PerfRunner Evidence Acquisition Task (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION, run-20260902-140958).
- **PerfControl Formal Review and Acceptance**: Completed 2026-09-02 (correction review). Evidence completeness, workload contract, runtime identity, calculation integrity all verified. Runtime identity matches frozen baseline (Decision D-019). All four cells formally ACCEPTED.
- **Historical 64K Result**: `RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md` (927.45 tok/s, 2026-09-01) remains valid historical provenance, unchanged and immutable.
- **Performance Assessment**: All cells below 80% normalized target (Decision D-020), establishing performance gap for optimization work.
- **Runtime**: Container `model-test-zyg-a3`, Image `nightly-releases-v0.24.0rc-a3`, vLLM 0.24.0+empty (matches frozen baseline per D-019)
- **Evidence Transport**: Per Decision D-022 (GitHub Release Asset Evidence Transport)

## Next Steps

- Baseline formally accepted (corrected); optimization track may begin
- Optimization Tasks will produce separate OPT Results compared against these immutable corrected baseline Results
- Per Decision D-019: Baseline execution mode complete (USER-VERIFIED KNOWN-GOOD BASELINE → FAST PREFLIGHT → RUN FROZEN COMMANDS → EVIDENCE → RESULT → OPTIMIZATION)

## Read-Only Preflight Observations (Non-Formal)

`READ-ONLY PREFLIGHT EVIDENCE — NOT FORMAL BASELINE RESULT` (this section is NOT a formal Result; the baseline Results above remain authoritative and immutable).

| Record | Date | Outcome | Gate A | Effective value | Evidence (D-022) |
|---|---|---|---|---|---|
| OPT-01 Preflight (see `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT.md`) | 2026-09-02 | `RUNTIME_IDENTITY_MISMATCH` | `NO_PROCESS` | `max_num_batched_tokens`: **UNVERIFIED** | Release `preflight-opt01-20260902-085628` — asset `GLM52-W8A8-OPT01-PREFLIGHT-run-20260902-085628.tar.gz` (size 3019; SHA256 `245470fd6b61d47f8cf2163a9d3647fd51626d921abbb42127e07ce5d158ed03`) |

Notes:

- Interpretation: fail-closed preflight correctly found `ACCEPTED GLM-5.2-W8A8 BASELINE RUNTIME NOT CURRENTLY ACTIVE` at observation time (container `model-test-zyg-a3` serving another workload). NOT a benchmark failure; accepted historical baseline remains valid.
- Integrity (verified 2026-09-02 via live GitHub API + local download): GitHub asset digest == downloaded archive sha256 == `.sha256` sidecar recorded digest. The `.sha256` file's own digest differs from the recorded digest (file-digest vs recorded tar digest kept distinct).
- Runner's original natural-language report transcribed the archive SHA incorrectly; integrity reconciliation confirmed `LOCAL_ARCHIVE == LOCAL_SIDECAR_VALUE == GITHUB_TARBALL_ASSET`, recorded as `REPORT_TRANSCRIPTION_ERROR` — NOT `EVIDENCE_ARCHIVE_MISMATCH`.
- No other runner-narrative SHA values are adopted into this Control record.
- `OPT-01 remains BLOCKED until the accepted GLM baseline runtime is restored (User-authorized) and effective max_num_batched_tokens is re-observed.`
