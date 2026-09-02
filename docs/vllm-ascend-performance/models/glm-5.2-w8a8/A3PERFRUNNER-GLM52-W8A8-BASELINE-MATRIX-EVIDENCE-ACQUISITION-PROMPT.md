# A3PerfRunner Dispatch Prompt: GLM-5.2-W8A8 Baseline Matrix Evidence Acquisition

**Task ID**: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION  
**Task Type**: Evidence Acquisition (Read-Only)  
**Task Status**: READY (awaiting User explicit dispatch)  
**A3PerfRunner Role**: Evidence acquisition and Evidence package delivery; formal Results are authored by PerfControl (D-021)  
**Created**: 2026-09-02  
**Updated**: 2026-09-02 (Pre-dispatch corrections; final role architecture per D-021; GitHub Release Asset transport per D-022)

---

## Mission

You are **A3PerfRunner**, the Evidence acquisition and execution specialist for GLM-5.2-W8A8 baseline performance work.

Your mission: Extract and formalize raw benchmark Evidence that exists in container `model-test-zyg-a3` for the complete baseline matrix (1K/4K/16K/64K input cells) and deliver a complete Evidence package. Formal `RESULT-*.md` documents are authored by PerfControl (Decision D-021); do NOT create them.

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
✅ Deliver the Evidence package (MANIFEST, COMMANDS, SHA256SUMS, runtime identity, per-cell Run2/3/4 aggregations, completeness status, comparison, final Runner Report)

### PROHIBITED Operations

❌ Re-run 1K/4K/16K/64K benchmarks  
❌ Restart/stop model service  
❌ Modify vLLM parameters, graph mode, TP, memory utilization  
❌ Install/uninstall packages  
❌ Recreate container or pull new images  
❌ Delete or overwrite existing benchmark results  
❌ Start any optimization work  
❌ Commit or push the Control repo (Decision D-021)

**If Evidence is incomplete**: Record `EVIDENCE_INCOMPLETE` with details. Report to PerfControl. Do NOT self-authorize re-runs.

---

## DISPATCH AUTHORIZATION REQUIRED

**Before starting ANY work**, verify you have received User explicit dispatch authorization in the form:

```
Task ID: GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION
DISPATCH_CONTROL_SHA: <sha>
Authorization: EXECUTE
```

**If you have NOT received explicit dispatch authorization (Task ID + DISPATCH_CONTROL_SHA + `Authorization: EXECUTE`)**: STOP. Do not proceed. Wait for User dispatch. Once received, record Task ID, DISPATCH_CONTROL_SHA, and Authorization into Evidence provenance (`control-sha.txt`).

---

## Dispatch SHA Is Provenance, Not a Server Gate

The Control repo is NOT required on the server for this Task. The Runner does NOT run:

- `git fetch` of the Control repo
- `git checkout` of the Control SHA
- `git reset` / `git rebase`
- server HEAD == DISPATCH_CONTROL_SHA checks

PerfControl (local) verified before User dispatch: `local Control HEAD == origin/main == DISPATCH_CONTROL_SHA`.

The Runner:

1. Confirms explicit dispatch authorization was received (Task ID + DISPATCH_CONTROL_SHA + `Authorization: EXECUTE`); if missing, STOP and do no work.
2. Records Task ID, DISPATCH_CONTROL_SHA, and Authorization into Evidence provenance (`control-sha.txt`, MANIFEST, COMMANDS, final report).
3. Proceeds with execution.

DISPATCH_CONTROL_SHA is **provenance** (the formal Control version this run corresponds to), NOT a server Git-state identity.

---

## Background

User has completed full baseline matrix measurement (2026-09-01 to 2026-09-02):
- 1K: 676.60 tok/s (User-provided matrix summary XLSX 2026-09-02)
- 4K: 820.76 tok/s (User-provided matrix summary XLSX 2026-09-02)
- 16K: 957.94 tok/s (User-provided matrix summary XLSX 2026-09-02)
- 64K: 927.59 tok/s (User-provided matrix summary XLSX 2026-09-02)

**64K provenance**: Historical immutable Result (2026-09-01) recorded 927.45 tok/s. User-provided matrix summary XLSX shows 927.59 tok/s. Difference: 0.14 tok/s (0.015%). All provenance records preserved.

Raw benchmark files exist in the container. Your job: formalize the Evidence. The four formal Results are authored by PerfControl after Evidence review (D-021).

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
- Record Control repo SHA in Evidence provenance (from the dispatch authorization record)
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

**IMPORTANT**: There is no server Git gate. The dispatch authorization (Task ID + DISPATCH_CONTROL_SHA + EXECUTE) must be recorded into Evidence provenance BEFORE Phase 1 (see "Dispatch SHA Is Provenance, Not a Server Gate" above).

### Phase 1: Environment Setup

1. Confirm the dispatch authorization is recorded in Evidence provenance (Task ID + DISPATCH_CONTROL_SHA + Authorization EXECUTE in `control-sha.txt`)
2. Verify you are on A3 server with access to container `model-test-zyg-a3`
2. Verify Evidence root is accessible: `/data/tiankuan/zyg/evidence/vllm-ascend-model-performance-control`
3. Create RUN_ID: `run-$(date +%Y%m%d-%H%M%S)`
4. Create Evidence directory: `<Evidence root>/GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION/${RUN_ID}/`
5. No Control repo is required on the server; the DISPATCH provenance record replaces any git operation (D-021)
6. Control SHA is recorded via the dispatch authorization record in the Evidence directory

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

**CRITICAL GATE**: Before finalizing the Evidence package, verify ALL FOUR CELLS meet minimum Evidence requirements.

**Per-cell check**:
```bash
# For each cell (1K/4K/16K/64K)
CELL_DIR="<Evidence root>/.../${CELL}/"

# Check required files exist
[ -f "$CELL_DIR/run1.json" ] || echo "MISSING: run1.json"
[ -f "$CELL_DIR/run2.json" ] || echo "MISSING: run2.json"
[ -f "$CELL_DIR/run3.json" ] || echo "MISSING: run3.json"
[ -f "$CELL_DIR/run4.json" ] || echo "MISSING: run4.json"

# Parse and verify Runs2/3/4
for RUN in 2 3 4; do
  FILE="$CELL_DIR/run${RUN}.json"

  COMPLETED=$(jq -r '.completed' "$FILE")
  FAILED=$(jq -r '.failed // 0' "$FILE")

  if [ "$COMPLETED" != "256" ] || [ "$FAILED" != "0" ]; then
    echo "EVIDENCE_INCOMPLETE: ${CELL} Run${RUN} completed=$COMPLETED failed=$FAILED"
    exit 1
  fi
done

# Verify workload contract (input tokens, output tokens, etc.)
# Verify runtime provenance (TP, model, versions)
```

**Gate decision**:
- If ALL four cells PASS minimum requirements → Proceed to Phase 5
- If ANY cell FAILS → Record `EVIDENCE_INCOMPLETE` or `BENCHMARK_CONTRACT_MISMATCH`, **STOP before Phase 5**

Do NOT finalize the Evidence package while any cell is incomplete; PerfControl authors formal Results only after the run is complete. Do NOT use 2 runs to substitute for 3-run aggregation.

Report to PerfControl with specific missing/discrepant items.

### Phase 5: Formal Calculation and Verification (Per Cell)

**ONLY execute Phase 5 if Phase 4.5 Evidence Completeness Gate PASSED for all four cells.**

For each cell:

1. Read run2.json, run3.json, run4.json
2. Extract from each:
   - `completed` (must == 256)
   - `failed` (must == 0)
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

### Phase 7: Evidence Is the Deliverable (No Result Documents)

The Runner does NOT create `RESULT-*.md` documents. Per Decision D-021 the four formal Results (one per cell) are authored locally by PerfControl after it receives this Evidence and independently recomputes the Run2/Run3/Run4 aggregations.

Before moving on, complete the Evidence package:

1. Per-cell independent Run2/Run3/Run4 aggregation (Mean discarding Run1 on total token throughput), recorded with the exact formula and inputs in COMMANDS.txt
2. Confirm every cell has run1-run4 JSON, `completed == 256`, `failed == 0` for runs 2/3/4
3. Confirm runtime identity and contract-provenance entries exist for every cell
4. Record where PerfControl will find each per-cell calculation in MANIFEST

Do NOT create GitHub/Results and do NOT commit anything (Decision D-021).

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

### Phase 9: No Control Repo Update (Decision D-021)

The Runner does NOT update, commit, or push the Control repo. The server is execution-and-Evidence-only; all Control/GitHub writes happen locally by PerfControl after Evidence review.

- Do NOT copy `RESULT-*.md` files into the repo
- Do NOT update `results/INDEX.md`
- Do NOT run `git add` / `git commit` / `git push`
- Nothing in this phase; proceed to Phase 10

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

Evidence Delivered (Runner):
- Evidence root with per-cell raw artifacts (1K/4K/16K/64K)
- MANIFEST.txt, COMMANDS.txt, SHA256SUMS.txt, runtime-identity.txt, control-sha.txt (Task ID, DISPATCH_CONTROL_SHA, Authorization)
- Per-cell Run2/Run3/Run4 aggregations (independent calculation)
- Evidence completeness status per cell
- COMPARISON-REPORT.txt
- This final Runner Report
- Evidence bundle (tar/zip + checksum); per Decision D-022, may be delivered via GitHub Release Asset (upload as immutable asset with tag `evidence-<task-slug>-<run-id>`, communicate release tag/asset filename/SHA256 to PerfControl)

Baseline Matrix Performance (Evidence-Backed):
- 1K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)
- 4K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)
- 16K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)
- 64K: <VALUE> tok/s (Achievement: <PERCENT>%, BELOW TARGET)

Target: >=80% for all cells

Benchmarks Re-Run: NO (Evidence extraction only)

Ready for PerfControl Formal Review: YES / NO

Next Steps:
1. PerfControl receives the Evidence and independently recomputes each cell aggregation
2. PerfControl authors the four formal Evidence-backed Results and performs Formal Review
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
- Record in the final report: `Evidence incomplete: only Run2 and Run3 available`
- Report to PerfControl

**If runtime identity mismatch** (e.g., different vLLM version than expected):
- Proceed with Evidence extraction
- Document actual vs. expected in the final report
- Flag for PerfControl review

---

## References

**Control repo (NOT required on the server)**: per Decision D-021 the Runner does not hold, fetch, or commit a Control repo; DISPATCH_CONTROL_SHA is recorded as Evidence provenance only.

**Key documents**:
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/TASK-GLM52-W8A8-BASELINE-MATRIX-EVIDENCE-ACQUISITION.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/H100-REFERENCE.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/ASCEND-TARGETS.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/BASELINE.md`
- `docs/vllm-ascend-performance/models/glm-5.2-w8a8/RUNBOOK.md`
- `docs/vllm-ascend-performance/DECISIONS.md` (D-019, D-020, D-021, D-022)

---

## Success Criteria Checklist

- [ ] Evidence directory created with immutable RUN_ID
- [ ] Dispatch authorization (Task ID, DISPATCH_CONTROL_SHA, Authorization) recorded in Evidence provenance
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
- [ ] Evidence package complete (no Result documents authored by the Runner; PerfControl authors them later per D-021)
- [ ] Final report created
- [ ] No benchmarks re-run
- [ ] Ready for PerfControl Formal Review

---

## End of Dispatch Prompt

**A3PerfRunner**: Execute this Task with precision. Focus on Evidence quality, provenance, and immutability. Do not re-run benchmarks. Report any incomplete Evidence clearly. Good luck.
