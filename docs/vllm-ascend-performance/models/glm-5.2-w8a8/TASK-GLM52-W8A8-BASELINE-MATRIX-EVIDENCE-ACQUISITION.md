# TASK-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION

**Task ID**: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION  
**Task Type**: Evidence Acquisition (Read-Only)  
**Status**: CREATED  
**Created**: 2026-09-02  
**Assigned to**: A3PerfRunner  
**Priority**: HIGH

## Objective

Extract and formalize raw benchmark Evidence from existing A3 container for the complete GLM-5.2-W8A8 baseline matrix (1K/4K/16K/64K input cells). This is a **read-only Evidence formalization task**. Do NOT re-run benchmarks.

## Background

User has completed the full baseline matrix measurement:
- 1K input + 1K output, C64: 676.60 tok/s (User-provided matrix summary)
- 4K input + 1K output, C64: 820.76 tok/s (User-provided matrix summary)
- 16K input + 1K output, C64: 957.94 tok/s (User-provided matrix summary)
- 64K input + 1K output, C64: 927.45 tok/s (User-measured, recorded in RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md)

Raw benchmark output files (JSON, logs, stdout) exist in container `model-test-zyg-a3`. This Task formalizes Evidence to enable:
1. Independent verification of User-provided matrix summary values
2. Calculation of exact Run2/Run3/Run4 aggregations from raw JSON
3. Complete provenance chain (runtime identity, benchmark contract, checksums)
4. Immutable Evidence-backed Results for all four cells
5. PerfControl Formal Review and Acceptance

## Scope

### In Scope

**Read-only inspection and Evidence extraction**:
- Locate existing benchmark output directories for 1K/4K/16K/64K cells
- Read raw benchmark JSON files (run1/run2/run3/run4, average_run2_4.json if present)
- Read benchmark logs and server logs
- Capture runtime identity (image ID/digest, container ID, vLLM versions, model path)
- Calculate SHA256 checksums of all raw artifacts
- Copy raw artifacts to formal Evidence root with immutable timestamps
- Create manifest and provenance record
- Independently recalculate Run2/Run3/Run4 aggregations from raw JSON
- Verify completed==256, failed==0 for each run
- Compare calculated values with User-provided matrix summary
- Create four immutable Evidence-backed Results (one per cell)

**Verification**:
- Runtime identity matches known baseline configuration (vLLM 0.24.0, vLLM-Ascend 0.19.1rc2, TP16, etc.)
- Benchmark contract compliance (256 prompts, C64, correct input/output lengths, ignore_eos=true, etc.)
- Run quality (no failed requests, complete runs)

### Out of Scope

**Prohibited operations** (unless explicitly authorized by User after Evidence review confirms critical Evidence is missing):
- Re-running 1K benchmark
- Re-running 4K benchmark
- Re-running 16K benchmark
- Re-running 64K benchmark
- Restarting model service
- Stopping current service
- Modifying vLLM launch parameters
- Changing graph mode, TP, memory utilization, or any runtime configuration
- Installing/uninstalling packages
- Recreating container
- Pulling new images
- Deleting or overwriting existing benchmark results
- Any optimization work

**If Evidence is incomplete**: Record `EVIDENCE_INCOMPLETE` with details. Do NOT self-authorize re-runs. PerfControl will review and User will decide whether to authorize specific re-runs.

## Container and Runtime Identity

**Container**: `model-test-zyg-a3`  
**Known Image**: `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`  
**Known vLLM**: 0.24.0+empty  
**Known vLLM-Ascend**: 0.19.1rc2.dev1157+g6443b2a38  
**Known vLLM-Ascend commit**: 6443b2a38b95390e4f5174ff7ad2f8c3751e040f  
**Model path**: `/data/tiankuan/zyg/model/GLM-5.2-w8a8`  
**Hardware**: Ascend A3 / 910C, 8 physical cards, 16 logical NPUs  
**Parallelism**: TP16 / DP1

**Known launch configuration** (verify from actual container/logs):
- `--tensor-parallel-size 16`
- `--max-model-len 70000`
- `--gpu-memory-utilization 0.9`
- `--quantization ascend`
- `--trust-remote-code`
- `--no-enable-prefix-caching`
- `--no-enable-log-requests`
- Graph mode: `FULL_DECODE_ONLY`

## Benchmark Contract

All four cells must comply with:

| Parameter | Value |
|---|---|
| Max concurrency | 64 |
| Num prompts | 256 |
| Dataset | random |
| Endpoint | `/v1/completions` |
| ignore_eos | true |
| Request rate | inf |
| Random range ratio | 0 |
| Runs | 4 (Run1/Run2/Run3/Run4) |
| Aggregation | Discard Run1, Mean(Run2, Run3, Run4) |

**Cell-specific parameters**:

| Cell | Input Tokens | Output Tokens |
|---|---|---|
| 1K | 1024 | 1024 |
| 4K | 4096 | 1024 |
| 16K | 16384 | 1024 |
| 64K | 65536 | 1024 |

## Evidence Root

**Evidence root**: `/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`

**This Task Evidence directory**: `/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control/GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION/<RUN_ID>/`

where `<RUN_ID>` = `run-YYYYMMDD-HHMMSS` (e.g., `run-20260902-150000`)

**Directory structure** (suggested):
```
<Evidence root>/GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION/<RUN_ID>/
├── MANIFEST.txt
├── COMMANDS.txt
├── SHA256SUMS.txt
├── runtime-identity.txt
├── control-sha.txt
├── 1K/
│   ├── run1.json
│   ├── run2.json
│   ├── run3.json
│   ├── run4.json
│   ├── average_run2_4.json (if present)
│   ├── benchmark-stdout.log
│   └── (other relevant artifacts)
├── 4K/
│   └── (same structure)
├── 16K/
│   └── (same structure)
├── 64K/
│   └── (same structure)
└── (server logs, if accessible and relevant)
```

**Requirements**:
- Do not overwrite existing Evidence directories
- Record all commands executed with timestamps and exit codes
- SHA256 checksum all copied artifacts
- Record Control repo SHA at time of Evidence acquisition
- Preserve immutable timestamps

## Expected Deliverables

### 1. Evidence Directory

Complete Evidence directory at Evidence root with all raw artifacts, checksums, manifest, and provenance records.

### 2. Four Immutable Evidence-Backed Results

Create one Result document for each cell:

- `RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-<RUN_ID>.md`
- `RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-<RUN_ID>.md`
- `RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-<RUN_ID>.md`
- `RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-<RUN_ID>.md`

**Each Result must include**:
- Exact Control repo SHA
- Task ID (GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION)
- Evidence root path
- Model identity (path, quantization)
- Container ID and image identity (ID, digest, tag)
- Runtime versions (vLLM, vLLM-Ascend, commit SHA)
- Hardware (A3/910C, 8 cards, 16 NPUs)
- Parallelism (TP16/DP1)
- Complete launch command (verified from container or logs)
- Benchmark contract (input/output tokens, C64, 256 prompts, etc.)
- Run2 raw metrics (from JSON)
- Run3 raw metrics (from JSON)
- Run4 raw metrics (from JSON)
- Calculated Run2~4 mean (independently computed)
- Completed/failed request counts
- H100 reference value (from H100-REFERENCE.md)
- A3 raw Total Token Throughput
- A3 normalized throughput (exact calculation per D-020)
- H100 normalized throughput (exact calculation per D-020)
- 80% target (exact calculation)
- Achievement (exact calculation)
- Disposition (BELOW TARGET / MEET TARGET / EXCEED TARGET)
- Evidence directory path
- SHA256 checksums of key artifacts

**Important**: Do not mix cells into a single Result. Each cell must have an independent Result that can be reviewed and Accepted individually.

### 3. Comparison Report

Brief comparison between:
- User-provided matrix summary values (from XLSX)
- Evidence-backed calculated values (from raw JSON Run2/Run3/Run4 aggregation)

If values differ, document:
- Absolute difference
- Percentage difference
- Whether difference affects disposition
- Potential causes (rounding, different aggregation method, etc.)

Do NOT silently overwrite User-provided values. Both values are valid historical records with different provenance.

### 4. Completeness Assessment

For each cell, report:
- Evidence completeness (COMPLETE / INCOMPLETE / MISSING)
- If incomplete: which specific artifacts are missing
- If complete: verification that all required artifacts are present and valid

## Success Criteria

1. All four cells have complete Evidence directories with checksums and manifest
2. All four cells have immutable Evidence-backed Result documents
3. Runtime identity verified and matches known baseline configuration
4. Benchmark contract verified for all cells (256 prompts, C64, correct input/output, etc.)
5. Run quality verified (completed==256, failed==0 for all runs)
6. Independent Run2~4 aggregation calculated and documented
7. Comparison with User-provided matrix summary documented
8. No benchmarks re-run (unless specific missing Evidence confirmed and User-authorized)
9. Control repo updated with four new Results
10. Ready for PerfControl Formal Review

## Failure Modes and Recovery

**If Evidence directory not found**:
- Document search paths tried
- Record EVIDENCE_INCOMPLETE
- Do NOT self-authorize re-run
- Report to PerfControl for User decision

**If JSON files incomplete** (e.g., only 3 runs instead of 4):
- Document which files are present/missing
- Calculate aggregation from available runs if possible, but flag incomplete
- Record EVIDENCE_INCOMPLETE with details
- Report to PerfControl for User decision

**If runtime identity does not match known baseline**:
- Document actual vs. expected values
- Flag discrepancy in Result
- Proceed with Evidence acquisition but mark Result with identity mismatch note
- PerfControl will review whether to Accept or request clarification

**If benchmark contract violation detected** (e.g., num_prompts != 256):
- Document violation in Result
- Proceed with Evidence acquisition
- Mark Result with contract violation note
- PerfControl will review and decide disposition

## Notes

- This is a read-only, Evidence formalization Task. The benchmarks have already been run.
- The goal is to create immutable, checksummed, provenance-tracked Evidence that PerfControl can Formally Review and Accept.
- Evidence-backed Results may have slightly different values than User-provided matrix summary due to exact JSON aggregation vs. spreadsheet summary. Both are valid historical records.
- The 64K cell already has RESULT-GLM52-W8A8-64K-BASELINE-USER-MEASURED.md. The new Evidence-backed 64K Result supplements (not replaces) it.
- After this Task, PerfControl will perform Formal Review, independent recalculation verification, and Acceptance per cell.
- Optimization work begins AFTER baseline is formally Accepted, not before.

## References

- Decision D-019: GLM-5.2-W8A8 User-verified baseline execution mode
- Decision D-020: Hardware compute basis and normalization policy
- BASELINE.md: Frozen baseline configuration
- RUNBOOK.md: Benchmark execution procedures
- scripts/: Frozen benchmark scripts
- H100-REFERENCE.md: H100 reference values for all four cells
- ASCEND-TARGETS.md: Calculated targets and provisional achievements
- STATUS.md: Current model status
- results/INDEX.md: Results index

## Dispatch

See companion document: `A3PERFRUNNER-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION-PROMPT.md` for complete A3PerfRunner execution prompt.
