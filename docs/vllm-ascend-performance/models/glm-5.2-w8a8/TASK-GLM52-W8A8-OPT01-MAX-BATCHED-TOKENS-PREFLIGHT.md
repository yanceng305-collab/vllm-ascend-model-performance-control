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

### Step 2: Locate vLLM Process (normative contract — implementation in Runner Prompt Section 2)

- PID discovery is deterministic: scan `/proc`, match cmdline that contains `serve` AND model path `/data/tiankuan/zyg/model/GLM-5.2-w8a8`, keep **numeric PID only** (`^[0-9]+$`).
- `0` matches → `NO_PROCESS` → STOP inference; Evidence still produced (outcome `RUNTIME_IDENTITY_MISMATCH`).
- exactly `1` match → bind `VLLM_PID` (pure integer).
- `>1` matches → `AMBIGUOUS_PROCESS` → STOP inference; Evidence still produced.
- Manual selection (`VLLM_PID=<identified_pid>`) is FORBIDDEN — no hand-picked PID.
- `NO_EXIT_BEFORE_EVIDENCE`: a failed PID resolution never skips Evidence packaging.

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

### Step 5: Locate Server Log (normative contract — implementation in Runner Prompt Section 5)

- Preferred log: `$WORK_DIR/glm52_w8a8.log` (resolved from `/proc/<PID>/cwd`).
- If not readable, resolve the real stdout/stderr target through `/proc/<PID>/fd/1` and `/proc/<PID>/fd/2` and use the first readable target.
- If none is readable → `LOG_SOURCE_UNAVAILABLE`; do NOT grep non-existent paths; the Evidence files still record `unavailable`.
- `NO_EXIT_BEFORE_EVIDENCE`: a missing log never aborts before Evidence packaging.

### Step 6: Search Server Log for Scheduler Config

Run only when the log is readable (see Runner Prompt Section 6); otherwise write placeholder Evidence files mentioning the log was unavailable. Example:

```bash
if [ -n "$LOG_FILE" ] && [ -r "$LOG_FILE" ]; then
  grep -n -i -E "scheduler|max_num_batched|batch.*token|chunked.*prefill" "$LOG_FILE" | head -100
  head -500 "$LOG_FILE" > server-log-snippet.txt
  grep -n -i -E "scheduler|max_num_batched|batch.*token" "$LOG_FILE" > scheduler-config-evidence.txt
else
  echo "LOG_SOURCE_UNAVAILABLE" > scheduler-config-evidence.txt
fi
```

Look for explicit logging of effective `max_num_batched_tokens` value.

### Step 7: Record and Cross-check Runtime Identity (normative contract — implementation in Runner Prompt Section 7)

- Actually compare, field by field, against the frozen baseline: container name, image name, image ID (captured separately), vLLM version, vLLM-Ascend version, model path, TP=16, max-model-len=70000, cmdline readable.
- Each field recorded as `EXPECTED / OBSERVED / STATUS=MATCH|MISMATCH|UNAVAILABLE` in `runtime-identity.txt`.
- `runtime_verified=YES` only when EVERY required field is `MATCH` — never hard-coded.
- Any `MISMATCH` or `UNAVAILABLE` in a required field → `RID=MISMATCH` → outcome `RUNTIME_IDENTITY_MISMATCH`; optimization inference STOPPED; Evidence still uploaded.

### Step 8: Determine Outcome (normative contract — implementation in Runner Prompt Section 8)

Three and only three possible outcomes:

1. `VALUE_VERIFIED` — pure integer `^[0-9]+$` observed (cmdline space/equal form, or log key=value / `:` / space form, including a value embedded in a larger config line); full raw line saved as `EVIDENCE_LINE`.
2. `BASELINE_VALUE_UNVERIFIED` — key found but no reliable integer; or no key. Never guess.
3. `RUNTIME_IDENTITY_MISMATCH` — GATE A failed (NO_PROCESS / AMBIGUOUS_PROCESS) or GATE B failed; optimization inference STOPPED; Evidence still uploaded.

Order of precedence: GATE A first, then GATE B, then value.

`NO_EXIT_BEFORE_EVIDENCE`: every outcome (including failures) continues into packaging and the D-022 upload.

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

Common fields (all outcomes):
```
STATUS: <VALUE_VERIFIED | BASELINE_VALUE_UNVERIFIED | RUNTIME_IDENTITY_MISMATCH>
GATE_A: <PASS | FAIL>
GATE_A_REASON: <NO_PROCESS | AMBIGUOUS_PROCESS | NON_NUMERIC_PID | n/a>
RUNTIME_GATE: <OK | MISMATCH | n/a>
VLLM_PID: <pid | N/A>
LOG_FILE: <path | LOG_SOURCE_UNAVAILABLE>
OBSERVATION_TIME: <UTC>
```

If VALUE_VERIFIED:
```
VALUE: <X>
SOURCE: <cmdline / server log line N / other>
EVIDENCE_LINE: <full raw line>
```

If BASELINE_VALUE_UNVERIFIED:
```
REASON: <specific reason>
CMDLINE_CHECKED: YES
SERVER_LOG_CHECKED: YES / LOG_SOURCE_UNAVAILABLE
VALUE: N/A
```

If RUNTIME_IDENTITY_MISMATCH:
```
REASON: <gate + specific fields>
VALUE: N/A
```

**MANIFEST.txt**: List all files with timestamps and sizes (all required files exist on every branch — placeholders when unavailable)

**SHA256SUMS.txt**: SHA256 hash of each file

### Step 10: Upload Evidence

Per D-022:
1. Create tarball: `GLM52-W8A8-OPT01-PREFLIGHT-run-<timestamp>.tar.gz`
2. Calculate archive SHA256
3. Create GitHub Release: `preflight-opt01-<timestamp>`
4. Upload as Release Asset

**Upload regardless of outcome** (`VALUE_VERIFIED` / `BASELINE_VALUE_UNVERIFIED` / `RUNTIME_IDENTITY_MISMATCH`). PerfControl needs Evidence for review.

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
2. ✅ Runtime identity actually cross-checked against frozen baseline (container, image, image ID, vLLM, vLLM-Ascend, model path, TP=16, max-model-len=70000, cmdline); no hard-coded "Runtime verified: YES"
3. ✅ PID resolution deterministic, numeric-only `^[0-9]+$`; 0 matches => NO_PROCESS STOP, >1 => AMBIGUOUS_PROCESS STOP, exactly 1 => bind; never a hand-written PID
4. ✅ No exit before Evidence packaging (NO_PROCESS / AMBIGUOUS_PROCESS / missing log / failed version command all reach packaging)
5. ✅ Process cmdline read (or placeholder on GATE A fail)
6. ✅ Server log searched for scheduler config (or placeholder `LOG_SOURCE_UNAVAILABLE`)
7. ✅ Outcome determined — one of `VALUE_VERIFIED` / `BASELINE_VALUE_UNVERIFIED` / `RUNTIME_IDENTITY_MISMATCH`; VALUE is a pure integer or UNVERIFIED
8. ✅ Evidence package created (all required files exist on every branch, placeholders allowed)
9. ✅ Evidence uploaded to GitHub Release (all three outcomes)
10. ✅ Runner Report delivered to PerfControl

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
