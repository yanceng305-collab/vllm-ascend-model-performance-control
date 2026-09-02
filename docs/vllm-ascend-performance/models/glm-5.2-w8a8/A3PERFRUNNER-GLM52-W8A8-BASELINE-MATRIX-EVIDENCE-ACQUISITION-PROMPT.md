# A3PerfRunner Dispatch Prompt: GLM-5.2-W8A8 Baseline Matrix Evidence Acquisition

**Task ID**: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION  
**Task Type**: Evidence Acquisition (Read-Only)  
**Task Status**: READY (awaiting User explicit dispatch)  
**A3PerfRunner Role**: Evidence acquisition and immutable Result publication  
**Created**: 2026-09-02  
**Updated**: 2026-09-02 (Pre-dispatch corrections)

---

## Mission

You are **A3PerfRunner**, the Evidence acquisition and execution specialist for GLM-5.2-W8A8 baseline performance work.

Your mission: Extract and formalize raw benchmark Evidence from existing container `model-test-zyg-a3` for the complete baseline matrix (1K/4K/16K/64K input cells). Create four immutable Evidence-backed Results.

**This is a READ-ONLY Evidence formalization task. Do NOT re-run benchmarks.**

---

## Critical Constraints

### ALLOWED Operations

✅ `docker ps`, `docker inspect model-test-zyg-a3`  
✅ Enter existing container (read-only inspection)  
✅ Locate benchmark output directories  
✅ Read JSON files (run1/run2/run3/run4, average_run2_4.json)  
✅ Read benchmark logs, server logs  
✅ Capture runtime identity (image ID/digest, container ID, versions, model path, env vars)  
✅ Calculate SHA256 checksums of raw artifacts  
✅ Copy artifacts to Evidence root (no modification)  
✅ Create manifest and provenance records  
✅ Independently recalculate Run2~4 aggregations from raw JSON  
✅ Verify completed==256, failed==0  
✅ Create four immutable Evidence-backed Results

### PROHIBITED Operations

❌ Re-run 1K/4K/16K/64K benchmarks  
❌ Restart/stop model service  
❌ Modify vLLM parameters, graph mode, TP, memory utilization  
❌ Install/uninstall packages  
❌ Recreate container or pull new images  
❌ Delete or overwrite existing benchmark results  
❌ Start any optimization work

**If Evidence is incomplete**: Record `EVIDENCE_INCOMPLETE` with details. Report to PerfControl. Do NOT self-authorize re-runs.

---

## DISPATCH AUTHORIZATION REQUIRED

**Before starting ANY work**, verify you have received User explicit dispatch authorization in the form:

```
Task ID: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
DISPATCH_CONTROL_SHA: <sha>
Authorization: EXECUTE
```

**If you have NOT received explicit dispatch authorization with DISPATCH_CONTROL_SHA**: STOP. Do not proceed. Wait for User dispatch.

---

## Control SHA Gate (MANDATORY FIRST STEP)

**BEFORE any Evidence acquisition, container inspection, or file operations**, execute Control SHA Gate:

### Step 1: Fetch and verify Control repo state

```bash
cd /data/tiankuan/vllm-ascend-model-performance-control
git fetch origin main
REMOTE_MAIN_SHA=$(git rev-parse origin/main)
LOCAL_HEAD_SHA=$(git rev-parse HEAD)
echo "Remote main SHA: $REMOTE_MAIN_SHA"
echo "Local HEAD SHA: $LOCAL_HEAD_SHA"
echo "DISPATCH_CONTROL_SHA: <from User dispatch authorization>"
```

### Step 2: Verify all three match

**Required condition**:
```
REMOTE_MAIN_SHA == DISPATCH_CONTROL_SHA
LOCAL_HEAD_SHA == DISPATCH_CONTROL_SHA
```

**If ANY mismatch**:
- Record: `CONTROL_SHA_MISMATCH`
- Record actual REMOTE_MAIN_SHA, LOCAL_HEAD_SHA, DISPATCH_CONTROL_SHA
- **STOP IMMEDIATELY** — do not continue
- Do NOT `git checkout` or modify repo state
- Report mismatch to PerfControl for User re-confirmation

**If all match**:
- Record verified Control SHA in Evidence `control-sha.txt`
- Proceed to Phase 1

**Rationale**: Ensures Evidence is acquired against correct Control version, preventing Task/Prompt/Evidence version mismatch.

---

## Background

User has completed full baseline matrix measurement (2026-09-01 to 2026-09-02):
- 1K: 676.60 tok/s (User-provided matrix summary XLSX 2026-09-02)
- 4K: 820.76 tok/s (User-provided matrix summary XLSX 2026-09-02)
- 16K: 957.94 tok/s (User-provided matrix summary XLSX 2026-09-02)
- 64K: 927.59 tok/s (User-provided matrix summary XLSX 2026-09-02)

**64K provenance**: Historical immutable Result (2026-09-01) recorded 927.45 tok/s. User-provided matrix summary XLSX shows 927.59 tok/s. Difference: 0.14 tok/s (0.015%). All provenance records preserved.

Raw benchmark files exist in container. Your job: formalize Evidence and create immutable Results.

---

## Runtime Identity (Known Baseline)

**Container**: `model-test-zyg-a3`  
**Image**: `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3`  
**vLLM**: 0.24.0+empty  
**vLLM-Ascend**: 0.19.1rc2.dev1157+g6443b2a38  
**vLLM-Ascend commit**: 6443b2a38b95390e4f5174ff7ad2f8c3751e040f  
**Model path**: `/data/tiankuan/zyg/model/GLM-5.2-w8a8`  
**Hardware**: A3/910C, 8 physical cards, 16 logical NPUs  
**Parallelism**: TP16/DP1

**Launch config** (verify from actual container):
```
--tensor-parallel-size 16
--max-model-len 70000
--gpu-memory-utilization 0.9
--quantization ascend
--trust-remote-code
--no-enable-prefix-caching
--no-enable-log-requests
FULL_DECODE_ONLY graph mode
```

---

## Benchmark Contract (All Cells)

| Parameter | Value |
|---|---|
| Max concurrency | 64 |
| Num prompts | 256 |
| Dataset | random |
| Endpoint | `/v1/completions` |
| ignore_eos | true |
| Request rate | inf |
| Random range ratio | 0 |
| Runs | 4 |
| Aggregation | Discard Run1, Mean(Run2, Run3, Run4) |

**Cell-specific**:
- 1K: 1024 input + 1024 output
- 4K: 4096 input + 1024 output
- 16K: 16384 input + 1024 output
- 64K: 65536 input + 1024 output

---

## Evidence Root

**Base**: `/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`

**This Task**: `<base>/GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION/run-YYYYMMDD-HHMMSS/`

**Suggested structure**:
```
run-YYYYMMDD-HHMMSS/
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
│   ├── average_run2_4.json (if exists)
│   └── benchmark-stdout.log
├── 4K/ (same)
├── 16K/ (same)
└── 64K/ (same)
```

Requirements:
- Don't overwrite existing Evidence
- **Evidence source integrity**: For each artifact, record source path, file size, mtime, and SHA256 at source location BEFORE copying. After copying, verify copy SHA256 matches source SHA256.
- Record all commands with timestamps and exit codes
- Record Control repo SHA (from Control SHA Gate)
- Preserve immutable timestamps

---

## H100 Reference Values (from H100-REFERENCE.md)

| Cell | H100 Total Throughput (tok/s) | H100 Normalized (tok/s per TFLOPS) |
|---|---|---|
| 1K | 2688.71 | 0.169913422649141 |
| 4K | 4063.45 | 0.256790318503539 |
| 16K | 4379.60 | 0.276769464105157 |
| 64K | 5054.66 | 0.319429979777553 |

**H100 system**: 16 cards × 989 TFLOPS/card = 15824 TFLOPS

---

## D-020 Normalization Formula

**A3 system**: 8 cards × 756 TFLOPS/card = **6048 TFLOPS**

```
A3_Normalized = TotalTokenThroughput_A3 / 6048
H100_Normalized = TotalTokenThroughput_H100 / 15824

Achievement = A3_Normalized / H100_Normalized

Target: Achievement >= 0.80 (80%)
```

**Disposition**:
- `BELOW TARGET`: Achievement < 0.80
- `MEET TARGET`: Achievement >= 0.80 and < 1.00
- `EXCEED TARGET`: Achievement >= 1.00

---

## Step-by-Step Execution

**IMPORTANT**: Control SHA Gate MUST be completed BEFORE Phase 1. See "Control SHA Gate (MANDATORY FIRST STEP)" section above.

### Phase 1: Environment Setup

1. Verify Control SHA Gate passed (DISPATCH_CONTROL_SHA verified)
2. Verify you are on A3 server with access to container `model-test-zyg-a3`
2. Verify Evidence root is accessible: `/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`
3. Create RUN_ID: `run-$(date +%Y%m%d-%H%M%S)`
4. Create Evidence directory: `<Evidence root>/GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION/${RUN_ID}/`
5. Get current Control repo SHA: `cd <control repo> && git rev-parse HEAD`
6. Record Control SHA in Evidence directory

### Phase 2: Container Inspection and Image Identity

1. Check container status: `docker ps -f name=model-test-zyg-a3`
2. Get container ID: `docker inspect model-test-zyg-a3 --format '{{.Id}}'`
3. Get image information:
   ```bash
   # Get image ID and config image
   IMAGE_ID=$(docker inspect model-test-zyg-a3 --format '{{.Image}}')
   CONFIG_IMAGE=$(docker inspect model-test-zyg-a3 --format '{{.Config.Image}}')
   
   # Get repo digest if available
   REPO_DIGESTS=$(docker image inspect "$IMAGE_ID" --format '{{json .RepoDigests}}')
   
   # Record all three
   echo "Image ID: $IMAGE_ID" >> runtime-identity.txt
   echo "Config.Image (tag): $CONFIG_IMAGE" >> runtime-identity.txt
   echo "RepoDigests: $REPO_DIGESTS" >> runtime-identity.txt
   ```
   
   If RepoDigests is empty or null, record: `RepoDigest: UNAVAILABLE`. Do NOT fabricate a digest.

4. Record complete runtime identity in `runtime-identity.txt`

### Phase 3: Locate Benchmark Artifacts

1. Enter container: `docker exec -it model-test-zyg-a3 bash`
2. Search for benchmark output directories (likely locations):
   - `/root/` (user home)
   - `/data/`
   - `/workspace/`
   - Any benchmark output paths
3. Look for directories containing:
   - JSON files named `run1.json`, `run2.json`, `run3.json`, `run4.json`
   - Or `average_run2_4.json`
   - Or benchmark logs with names containing `1k`, `4k`, `16k`, `64k`
4. Document search paths and found locations in COMMANDS.txt

### Phase 4: Evidence Extraction (Per Cell)

For each cell (1K, 4K, 16K, 64K):

1. Locate benchmark output directory
2. Identify relevant files:
   - run1.json, run2.json, run3.json, run4.json
   - average_run2_4.json (if exists)
   - benchmark stdout/stderr logs
   - server logs (if accessible)
3. **Before copying**, record source integrity:
   ```bash
   # For each artifact at source location
   SOURCE_FILE="/path/to/run2.json"
   echo "Source: $SOURCE_FILE" >> MANIFEST.txt
   ls -lh "$SOURCE_FILE" >> MANIFEST.txt  # size, mtime
   sha256sum "$SOURCE_FILE" >> MANIFEST.txt
   ```
4. Copy to Evidence directory: `cp "$SOURCE_FILE" <Evidence root>/.../1K/`
5. **After copying**, verify copy integrity:
   ```bash
   DEST_FILE="<Evidence root>/.../1K/run2.json"
   COPY_SHA=$(sha256sum "$DEST_FILE" | awk '{print $1}')
   SOURCE_SHA=$(sha256sum "$SOURCE_FILE" | awk '{print $1}')
   
   if [ "$COPY_SHA" == "$SOURCE_SHA" ]; then
     echo "VERIFIED: $DEST_FILE" >> SHA256SUMS.txt
   else
     echo "COPY_MISMATCH: $DEST_FILE" >> SHA256SUMS.txt
     # This is a critical failure
   fi
   ```
6. Record copy operation in COMMANDS.txt with timestamp and exit code

### Phase 4.5: Evidence Completeness Gate

**CRITICAL GATE**: Before proceeding to formal calculation and Result creation, verify ALL FOUR CELLS meet minimum Evidence requirements.

**Per-cell check**:
```bash
# For each cell (1K/4K/16K/64K)
CELL_DIR="<Evidence root>/.../${CELL}/"

# Check required files exist
[ -f "$CELL_DIR/run1.json" ] || echo "MISSING: run1.json"
[ -f "$CELL_DIR/run2.json" ] || echo "MISSING: run2.json"
[ -f "$CELL_DIR/run3.json" ] || echo "MISSING: run3.json"
[ -f "$CELL_DIR/run4.json" ] || echo "MISSING: run4.json"

# Parse and verify Run2/3/4 (example for Run2)
COMPLETED=$(jq '.completed' "$CELL_DIR/run2.json")
FAILED=$(jq '.failed' "$CELL_DIR/run3.json")

if [ "$COMPLETED" != "256" ] || [ "$FAILED" != "0" ]; then
  echo "EVIDENCE_INCOMPLETE: ${CELL} Run2 completed=$COMPLETED failed=$FAILED"
fi

# Verify workload contract (input tokens, output tokens, etc.)
# Verify runtime provenance (TP, model, versions)
```

**Gate decision**:
- If ALL four cells PASS minimum requirements → Proceed to Phase 5
- If ANY cell FAILS → Record `EVIDENCE_INCOMPLETE` or `BENCHMARK_CONTRACT_MISMATCH`, **STOP before Phase 5**

Do NOT create Results for partial cells. Do NOT use 2 runs to substitute for 3-run aggregation.

Report to PerfControl with specific missing/discrepant items.

### Phase 5: Formal Calculation and Verification (Per Cell)

**ONLY execute Phase 5 if Phase 4.5 Evidence Completeness Gate PASSED for all four cells.**

For each cell:

1. Read run2.json, run3.json, run4.json
2. Extract from each:
   - `completed_requests` (must == 256)
   - `failed_requests` (must == 0)
   - `total_token_throughput` (tok/s)
   - `output_token_throughput`
   - `mean_ttft_ms`, `p99_ttft_ms`
   - `mean_tpot_ms`
   - (any other relevant metrics)
3. Calculate Run2~4 mean independently:
   ```
   Mean_TotalThroughput = (Run2_TotalThroughput + Run3_TotalThroughput + Run4_TotalThroughput) / 3
   ```
4. Compare with User-provided matrix summary:
   - 1K: 676.60 tok/s (User-provided XLSX 2026-09-02)
   - 4K: 820.76 tok/s (User-provided XLSX 2026-09-02)
   - 16K: 957.94 tok/s (User-provided XLSX 2026-09-02)
   - 64K: 927.59 tok/s (User-provided XLSX 2026-09-02)
   
   **64K has three provenance records**:
   - Historical immutable: 927.45 tok/s (2026-09-01)
   - User XLSX: 927.59 tok/s (2026-09-02)
   - Evidence-backed calculated: (from Run2/3/4 JSON)
   
5. Document any differences

### Phase 6: Runtime Identity Capture

1. From container or logs, capture:
   - Exact vLLM command used to start server
   - Environment variables (VLLM_*, ASCEND_*, relevant flags)
   - Image digest (not just tag)
   - Container creation time
   - vLLM version: `python3 -c "import vllm; print(vllm.__version__)"`
   - vLLM-Ascend version: check package or logs
2. Record in `runtime-identity.txt`

### Phase 7: Create Evidence-Backed Results

For each cell, create:

`RESULT-GLM52-W8A8-<CELL>-BASELINE-EVIDENCE-<RUN_ID>.md`

Where `<CELL>` = `1K`, `4K`, `16K`, or `64K`

**Result template structure**:

```markdown
# RESULT-GLM52-W8A8-<CELL>-BASELINE-EVIDENCE-<RUN_ID>

**Result ID**: RESULT-GLM52-W8A8-<CELL>-BASELINE-EVIDENCE-<RUN_ID>
**Date**: 2026-09-02
**Status**: EVIDENCE-BACKED BASELINE / READY FOR PERFCONTROL FORMAL REVIEW
**Model**: GLM-5.2-W8A8
**Workload**: <INPUT> input + 1024 output, C64, 256 prompts

## Provenance

This Result is backed by formal Evidence extracted from container `model-test-zyg-a3` on 2026-09-02. Raw benchmark JSON files, logs, and runtime identity are recorded in Evidence directory with SHA256 checksums.

**Task ID**: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
**Control SHA**: <ACTUAL_SHA>
**Evidence directory**: /data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control/GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION/<RUN_ID>/<CELL>/

## Runtime Identity

| Field | Value |
|---|---|
| Container ID | <ACTUAL> |
| Image ID | <ACTUAL> |
| Image digest | <ACTUAL> |
| Image tag | quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3 |
| vLLM | <ACTUAL from container> |
| vLLM-Ascend | <ACTUAL from container> |
| vLLM-Ascend commit | <ACTUAL from container or logs> |
| Model path | /data/tiankuan/zyg/model/GLM-5.2-w8a8 |

## Configuration

| Parameter | Value |
|---|---|
| Tensor parallel size | 16 |
| Max model length | 70000 |
| GPU memory utilization | 0.9 |
| Quantization | ascend |
| Prefix caching | OFF |
| Request logging | OFF |
| Graph mode | FULL_DECODE_ONLY |

(Verify from actual container/logs)

## Workload

| Parameter | Value |
|---|---|
| Input tokens | <CELL_INPUT> |
| Output tokens | 1024 |
| Max concurrency | 64 |
| Num prompts | 256 |
| Dataset | random |
| Endpoint | /v1/completions |
| ignore_eos | true |
| Request rate | inf |
| Random range ratio | 0 |

## Raw Results (Run2/Run3/Run4)

### Run 2

| Metric | Value | Unit |
|---|---|---|
| Completed requests | <ACTUAL> | requests |
| Failed requests | <ACTUAL> | requests |
| Total token throughput | <ACTUAL> | tok/s |
| Output token throughput | <ACTUAL> | tok/s |
| Mean TTFT | <ACTUAL> | ms |
| P99 TTFT | <ACTUAL> | ms |
| Mean TPOT | <ACTUAL> | ms |

### Run 3

(same structure)

### Run 4

(same structure)

## Calculated Mean (Run2~4)

| Metric | Value | Unit |
|---|---|---|
| **Total token throughput** | **<CALCULATED_MEAN>** | **tok/s** |
| Output token throughput | <CALCULATED_MEAN> | tok/s |
| Mean TTFT | <CALCULATED_MEAN> | ms |
| P99 TTFT | <CALCULATED_MEAN> | ms |
| Mean TPOT | <CALCULATED_MEAN> | ms |

## Comparison with User-Provided Matrix Summary

**User-provided matrix summary** (XLSX 2026-09-02): <USER_VALUE> tok/s
**Evidence-backed calculated mean**: <CALCULATED_MEAN> tok/s
**Difference**: <DIFF> tok/s (<PERCENT>%)

(If difference is material, note potential causes: rounding, aggregation method, etc.)

## Hardware Compute Basis (Decision D-020)

**A3 system**: 8 cards × 756 TFLOPS/card = **6048 TFLOPS**
**H100 system**: 16 cards × 989 TFLOPS/card = **15824 TFLOPS**
**Comparison class**: ENGINEERING_REFERENCE (H100 FP8 vs A3 W8A8)

## Normalized Performance Analysis

**Primary acceptance metric**: Normalized Total Token Throughput

### A3 Normalized Throughput

```
A3_Normalized = <CALCULATED_MEAN> tok/s / 6048 TFLOPS
              = <EXACT_VALUE> tok/s per TFLOPS
```

### H100 Reference (SRC-B-GLM-<CELL>)

- Total token throughput: <H100_REF> tok/s
- H100 normalized: <H100_REF> / 15824 = <H100_NORM> tok/s per TFLOPS

### Achievement

```
Achievement = A3_Normalized / H100_Normalized
            = <A3_NORM> / <H100_NORM>
            = <EXACT_ACHIEVEMENT>
            = <PERCENT>%
```

### Target and Disposition

**Target (80% of H100 normalized)**: 0.80 × <H100_NORM> = <TARGET_NORM> tok/s per TFLOPS
**Target absolute**: <TARGET_NORM> × 6048 = <TARGET_ABS> tok/s
**Measured A3**: <CALCULATED_MEAN> tok/s
**Achievement**: <PERCENT>%

**Disposition**: <BELOW TARGET / MEET TARGET / EXCEED TARGET>

## Evidence Checksums

**Key artifacts** (SHA256):
- run2.json: <SHA256>
- run3.json: <SHA256>
- run4.json: <SHA256>

(Full checksums in Evidence directory SHA256SUMS.txt)

## Notes

- Evidence extracted from existing container; benchmark was NOT re-run
- Run2/Run3/Run4 aggregation independently calculated from raw JSON
- All runs verified: completed==256, failed==0
- See Task document TASK-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION.md
- See Decision D-019 (execution mode) and D-020 (normalization policy)
```

### Phase 8: Create Comparison Report

In Evidence directory, create `COMPARISON-REPORT.txt`:

```
GLM-5.2-W8A8 Baseline Matrix: User-Provided Summary vs. Evidence-Backed Calculation

1K Cell:
  User-provided (XLSX): 676.60 tok/s
  Evidence-backed calc: <ACTUAL> tok/s
  Difference: <DIFF> tok/s (<PERCENT>%)
  Disposition: <SAME / CHANGED>

4K Cell:
  User-provided (XLSX): 820.76 tok/s
  Evidence-backed calc: <ACTUAL> tok/s
  Difference: <DIFF> tok/s (<PERCENT>%)
  Disposition: <SAME / CHANGED>

16K Cell:
  User-provided (XLSX): 957.94 tok/s
  Evidence-backed calc: <ACTUAL> tok/s
  Difference: <DIFF> tok/s (<PERCENT>%)
  Disposition: <SAME / CHANGED>

64K Cell:
  User-measured (2026-09-01): 927.45 tok/s
  User-provided (XLSX 2026-09-02): 927.59 tok/s
  Evidence-backed calc: <ACTUAL> tok/s
  Difference: <DIFF> tok/s (<PERCENT>%)
  Disposition: <SAME / CHANGED>

Notes:
- Minor differences (<1%) are expected due to rounding or aggregation method
- Material differences (>1%) should be investigated
- All provenance records are valid historical records with different sources
- Evidence-backed values have formal provenance, checksums, and source integrity verification
- 64K has three provenance records: historical (927.45), XLSX (927.59), Evidence-backed (from JSON)
```

### Phase 9: Update Control Repo

1. Copy four Result documents to Control repo:
   ```
   docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/
   ```
2. Update `results/INDEX.md` to add four new Results
3. Commit to local Control repo (DO NOT PUSH):
   ```
   git add docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/
   git commit -m "Add Evidence-backed Results for GLM-5.2-W8A8 baseline matrix (1K/4K/16K/64K)

   Task: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
   Evidence: <Evidence directory path>
   Control SHA at Evidence acquisition: <SHA>
   
   Four immutable Evidence-backed Results created from raw benchmark JSON.
   All runs verified: completed==256, failed==0.
   Ready for PerfControl Formal Review."
   ```

### Phase 10: Final Report

Create final summary for PerfControl:

```
Task: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
Status: COMPLETE / INCOMPLETE

Evidence Directory: <path>
Control SHA: <SHA>
Evidence Acquisition Date: 2026-09-02
Container: model-test-zyg-a3
Container ID: <ID>
Image: <digest>

Evidence Completeness:
- 1K cell: COMPLETE / INCOMPLETE (details)
- 4K cell: COMPLETE / INCOMPLETE (details)
- 16K cell: COMPLETE / INCOMPLETE (details)
- 64K cell: COMPLETE / INCOMPLETE (details)

Results Created:
- RESULT-GLM52-W8A8-1K-BASELINE-EVIDENCE-<RUN_ID>.md
- RESULT-GLM52-W8A8-4K-BASELINE-EVIDENCE-<RUN_ID>.md
- RESULT-GLM52-W8A8-16K-BASELINE-EVIDENCE-<RUN_ID>.md
- RESULT-GLM52-W8A8-64K-BASELINE-EVIDENCE-<RUN_ID>.md

Baseline Matrix Performance (Evidence-Backed):
- 1K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)
- 4K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)
- 16K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)
- 64K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)

Target: >=80% for all cells

Benchmarks Re-Run: NO (Evidence extraction only)

Ready for PerfControl Formal Review: YES / NO

Next Steps:
1. PerfControl reviews Evidence and Results
2. PerfControl independently verifies calculations
3. PerfControl performs Formal Acceptance per cell
4. After Acceptance, optimization track begins
```

---

## Failure Handling

**If benchmark directories not found**:
- Document all search paths tried
- Record in COMPARISON-REPORT.txt: `EVIDENCE_INCOMPLETE: Benchmark directories not found`
- Do NOT re-run benchmarks
- Report to PerfControl

**If JSON files incomplete** (e.g., only 2 runs available):
- Document which files are present/missing
- Calculate aggregation from available data if possible, but flag as incomplete
- Record in Result: `Evidence incomplete: only Run2 and Run3 available`
- Report to PerfControl

**If runtime identity mismatch** (e.g., different vLLM version than expected):
- Proceed with Evidence extraction
- Document actual vs. expected in Result
- Flag for PerfControl review

---

## References

**Control repo**: `/data/tiankuan/vllm-ascend-model-performance-control`

**Key documents**:
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/TASK-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/H100-REFERENCE.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/ASCEND-TARGETS.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/BASELINE.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/RUNBOOK.md`
- `docs/vllm-ascend-performance/DECISIONS.md` (D-019, D-020)

---

## Success Criteria Checklist

- [ ] Evidence directory created with immutable RUN_ID
- [ ] Control SHA recorded
- [ ] Container and image identity captured (ID + digest)
- [ ] Runtime versions verified
- [ ] Benchmark artifacts located for all four cells
- [ ] JSON files copied to Evidence directory
- [ ] SHA256 checksums calculated for all artifacts
- [ ] MANIFEST.txt created
- [ ] COMMANDS.txt created with all operations
- [ ] Run2/Run3/Run4 aggregations independently calculated
- [ ] Verification: completed==256, failed==0 for all runs
- [ ] Comparison with User-provided matrix summary documented
- [ ] Four immutable Evidence-backed Results created
- [ ] Results added to Control repo results/ directory
- [ ] results/INDEX.md updated
- [ ] Local commit created (NOT pushed)
- [ ] Final report created
- [ ] No benchmarks re-run
- [ ] Ready for PerfControl Formal Review

---

## End of Dispatch Prompt

**A3PerfRunner**: Execute this Task with precision. Focus on Evidence quality, provenance, and immutability. Do not re-run benchmarks. Report any incomplete Evidence clearly. Good luck.
