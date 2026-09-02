# TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT

**Task ID**: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT  
**Task Type**: READ-ONLY Baseline Value Observation  
**Status**: READY  
**Created**: 2026-09-02  
**Assigned to**: A3PerfRunner  
**Priority**: HIGH

**READY status**: Task prepared, awaiting User explicit dispatch (Task ID + DISPATCH_CONTROL_SHA + Authorization: EXECUTE).

---

## Objective

Determine the current effective value of `max_num_batched_tokens` in the running A3 baseline environment through strictly read-only observation.

**This is NOT an optimization experiment.** No server restart, no parameter modification, no benchmark execution.

---

## Background

OPT-01 (max-batched-tokens screening) requires knowing the current baseline value before selecting a candidate. The frozen baseline documentation does not explicitly record max_num_batched_tokens, and the default value may vary by vLLM version, model type, or runtime configuration.

This preflight task establishes the actual effective value through direct runtime observation.

---

## Scope

### Read-Only Operations ONLY

**Permitted**:
- Read process command line
- Read server logs
- Read process working directory
- Read runtime configuration outputs
- Record runtime identity
- Capture Evidence

**ABSOLUTELY FORBIDDEN**:
- Stop server
- Restart server
- Modify launch arguments
- Modify container
- Run benchmark
- Execute optimization
- Change any server state
- Modify model
- Modify runtime

**Violation of read-only constraint = immediate task failure**

---

## Required Observations

### 1. Current vLLM Process Identity

Capture:
- **PID**: Exact process ID
- **Command line**: Read `/proc/<PID>/cmdline` (Linux) or equivalent
- **Working directory**: `/proc/<PID>/cwd` or `pwdx <PID>`
- **Start time**: Process start timestamp (if available via `ps -p <PID> -o lstart=`)
- **User**: Process owner

**Method**: Direct `/proc` filesystem read or equivalent system interface. Do not rely on `ps aux | grep` pattern matching alone.

### 2. Current Baseline Server Log

Locate and identify the actual server log file:
- Expected path from baseline: `glm52_w8a8.log` in working directory
- Verify via `/proc/<PID>/fd/` symlinks or working directory inspection

Search log for runtime scheduler configuration:
- Lines containing: `scheduler`, `max_num_batched_tokens`, `batched_tokens`, `batch`, `chunked_prefill`
- Configuration initialization output
- Scheduler policy statements
- Any explicit parameter logging

Capture relevant log excerpts (up to 100 lines around scheduler initialization).

### 3. Runtime Configuration Identity

Record complete runtime identity:
- Container name/ID (if running in container)
- Image name + digest/ID
- vLLM version (from `vllm --version` if accessible, or from process environment)
- vLLM-Ascend version
- Model path
- TP size
- max-model-len
- Current launch command (reconstructed from cmdline)

Verify this matches frozen baseline identity from `BASELINE.md`.

### 4. Effective max_num_batched_tokens Value

The runtime-identity gate (Step 8) decides among three outcomes: `VALUE_VERIFIED`, `BASELINE_VALUE_UNVERIFIED`, or `RUNTIME_IDENTITY_MISMATCH`.

#### Outcome A: VALUE_VERIFIED

If there is explicit runtime Evidence showing:
```
max_num_batched_tokens = X
```

Record:
- **Value**: X
- **Evidence source**: (cmdline / server log line number / config file)
- **Exact evidence**: Quote the specific line/output

Sources in priority order:
1. Explicit `--max-num-batched-tokens X` in process cmdline
2. Scheduler initialization log statement printing effective value
3. Runtime config dump or API query result

#### Outcome B: BASELINE_VALUE_UNVERIFIED

If:
- Cmdline does not include `--max-num-batched-tokens`
- Server log does not print effective scheduler value
- No other reliable runtime source exists

Then output:
```
BASELINE_VALUE_UNVERIFIED
Reason: [specific reason - e.g., "parameter not in cmdline, scheduler config not logged"]
```

**Do NOT**:
- Assume default value from documentation
- Infer from vLLM version
- Use AI knowledge of defaults
- Guess from 910B configuration
- Derive from parameter name semantics

If the value cannot be observed from actual runtime Evidence, report UNVERIFIED.

---

## Execution Steps

### Step 1: Verify Dispatch Authorization

Confirm receipt of:
```
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```

### Step 2: Locate vLLM Process

```bash
# Find vLLM serve process
ps aux | grep "vllm serve" | grep -v grep

# Capture PID
VLLM_PID=<identified_pid>

# Verify it's the GLM-5.2-w8a8 baseline service
ps -p $VLLM_PID -f
```

Record PID and confirm model path matches `/data/tiankuan/zyg/model/GLM-5.2-w8a8`.

### Step 3: Read Process Command Line

```bash
# Linux: Read exact command line
cat /proc/$VLLM_PID/cmdline | tr '\0' ' '

# Alternative: Use ps
ps -p $VLLM_PID -o args=

# Capture to file
cat /proc/$VLLM_PID/cmdline | tr '\0' ' ' > process-cmdline.txt
```

Search cmdline for `--max-num-batched-tokens`.

### Step 4: Read Process Working Directory

```bash
# Get working directory
pwdx $VLLM_PID

# Or via /proc
ls -l /proc/$VLLM_PID/cwd
```

Record working directory.

### Step 5: Locate Server Log

```bash
# Expected location from baseline
WORK_DIR=$(pwdx $VLLM_PID | cut -d: -f2 | xargs)
LOG_FILE="$WORK_DIR/glm52_w8a8.log"

# Verify log exists
ls -lh $LOG_FILE

# Alternative: Check file descriptors
ls -l /proc/$VLLM_PID/fd/ | grep -E "\.log|stdout|stderr"
```

Confirm log file identity and location.

### Step 6: Search Server Log for Scheduler Config

```bash
# Search for scheduler-related initialization
grep -n -i -E "scheduler|max_num_batched|batch.*token|chunked.*prefill" $LOG_FILE | head -100

# Capture broader context around scheduler init (adjust line numbers as needed)
# Look for early initialization phase
head -500 $LOG_FILE | grep -A5 -B5 -i "scheduler"

# Save relevant excerpts
grep -n -i -E "scheduler|max_num_batched|batch.*token" $LOG_FILE > scheduler-config-evidence.txt
```

Look for explicit logging of effective `max_num_batched_tokens` value.

### Step 7: Record Runtime Identity

Capture:
```bash
# Container (if applicable)
docker ps --filter "name=model-test-zyg-a3" --format "{{.ID}} {{.Image}} {{.Status}}"

# vLLM version (if accessible without disturbing service)
# Only if safe and non-invasive

# Process start time
ps -p $VLLM_PID -o lstart=
```

Save to `runtime-identity.txt`.

### Step 8: Determine Outcome

**Decision logic**:

```python
if "--max-num-batched-tokens" in cmdline:
    VALUE_VERIFIED
    value = <extracted_from_cmdline>
    source = "process cmdline"
elif "max_num_batched_tokens" in server_log:
    VALUE_VERIFIED
    value = <extracted_from_log>
    source = "server log line <N>"
else:
    BASELINE_VALUE_UNVERIFIED
    reason = "parameter not in cmdline, not logged in server output"
```

### Step 9: Create Evidence Package

Directory structure:
```
GLM52-W8A8-OPT01-PREFLIGHT-run-<timestamp>/
├── runtime-identity.txt
├── process-cmdline.txt
├── process-cwd.txt
├── scheduler-config-evidence.txt
├── server-log-snippet.txt
├── effective-max-num-batched-tokens.txt
├── control-sha.txt
├── MANIFEST.txt
└── SHA256SUMS.txt
```

**effective-max-num-batched-tokens.txt** format:

If VALUE_VERIFIED:
```
STATUS: VALUE_VERIFIED
VALUE: <X>
SOURCE: <cmdline / server log line N / other>
EVIDENCE: <exact quoted line>
```

If BASELINE_VALUE_UNVERIFIED:
```
STATUS: BASELINE_VALUE_UNVERIFIED
REASON: <specific reason>
CMDLINE_CHECKED: YES
SERVER_LOG_CHECKED: YES
ALTERNATIVE_SOURCES_CHECKED: <list>
```

**MANIFEST.txt**: List all files with timestamps and sizes

**SHA256SUMS.txt**: SHA256 hash of each file

### Step 10: Upload Evidence

Per D-022:
1. Create tarball: `GLM52-W8A8-OPT01-PREFLIGHT-run-<timestamp>.tar.gz`
2. Calculate archive SHA256
3. Create GitHub Release: `preflight-opt01-<timestamp>`
4. Upload as Release Asset

**Upload regardless of outcome** (VALUE_VERIFIED or UNVERIFIED). PerfControl needs Evidence for review.

**Evidence Type**: `READ-ONLY OPTIMIZATION PREFLIGHT EVIDENCE`

### Step 11: Runner Report

```markdown
# A3PerfRunner Report: OPT01 Preflight

**Task**: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT
**Status**: COMPLETE
**Outcome**: <VALUE_VERIFIED / BASELINE_VALUE_UNVERIFIED / RUNTIME_IDENTITY_MISMATCH>

**Process PID**: <pid>
**Model path**: /data/tiankuan/zyg/model/GLM-5.2-w8a8
**Container**: model-test-zyg-a3
**Runtime identity**: <OK / MISMATCH> (computed gate; never hard-coded YES)

**max_num_batched_tokens**:
<if VALUE_VERIFIED>
  Value: <X>
  Source: <source>
  Evidence: <quoted line>
</if>
<if UNVERIFIED>
  Status: BASELINE_VALUE_UNVERIFIED
  Reason: <reason>
  Cmdline: <does not contain parameter>
  Server log: <does not print effective value>
</if>

**Evidence**: <GitHub Release URL>
**Archive SHA256**: <hash>

**Server state**: UNCHANGED (read-only observation)
```

---

## Success Criteria

1. ✅ Preflight completes without modifying server state
2. ✅ Runtime identity captured and verified against frozen baseline
3. ✅ Process cmdline read
4. ✅ Server log searched for scheduler config
5. ✅ Outcome determined (VALUE_VERIFIED or UNVERIFIED)
6. ✅ Evidence package created
7. ✅ Evidence uploaded to GitHub Release
8. ✅ Runner Report delivered to PerfControl

---

## Constraints

- **ABSOLUTELY READ-ONLY**: No server restart, no parameter changes, no benchmark
- Do NOT stop/restart service
- Do NOT run benchmark
- Do NOT modify any server state
- Do NOT guess values if not observable
- Do NOT commit Control repo
- Do NOT author Formal Results
- Evidence upload required regardless of outcome

---

## What Happens After Preflight

### If VALUE_VERIFIED:
1. PerfControl reviews Evidence
2. PerfControl designs candidate based on verified baseline value
3. PerfControl updates OPT-01 Task with candidate
4. OPT-01 becomes READY for execution

### If BASELINE_VALUE_UNVERIFIED:
1. PerfControl reviews Evidence
2. PerfControl designs alternative strategy (e.g., minimal test launch with explicit logging, or vLLM source code inspection)
3. New preflight or investigation task may be created
4. OPT-01 remains BLOCKED until baseline value established

---

## Rollback Triggers

This is a read-only task. There is no rollback because there are no changes.

If the task inadvertently modifies server state:
- **Immediate STOP**
- Report violation to PerfControl
- Document what was changed
- Do NOT attempt to "fix" without PerfControl authorization

---

## References

- Blocked Task: `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING.md`
- Baseline: `BASELINE.md`
- D-021: PerfControl/A3PerfRunner separation
- D-022: GitHub Release Asset Evidence Transport
