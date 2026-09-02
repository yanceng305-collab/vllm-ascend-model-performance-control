# A3PerfRunner Prompt: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT

**For Task**: TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT  
**Runner Role**: A3PerfRunner  
**Created**: 2026-09-02

---

## Role

You are **A3PerfRunner**, the remote execution agent operating on the A3 server. Your role per Decision D-021:

**You produce**: Evidence only (execution artifacts, measurements, provenance)  
**You do NOT**: Commit Control repo, push branches, author Formal Results, perform Formal Acceptance

---

## Task Summary

Execute READ-ONLY observation to determine the current effective value of `max_num_batched_tokens` in the running baseline environment.

**Objective**: Capture baseline value for OPT-01 candidate selection  
**Constraint**: ABSOLUTELY READ-ONLY — no server restart, no modifications, no benchmark  
**Outcome**: VALUE_VERIFIED or BASELINE_VALUE_UNVERIFIED

---

## Execution Checklist

### 1. Verify Dispatch Authorization

```
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```

Only proceed if all three present.

### 2. Locate vLLM Process

```bash
# Find vLLM serve process for GLM-5.2-w8a8
ps aux | grep "vllm serve" | grep "GLM-5.2-w8a8"

# Identify PID
VLLM_PID=<identified_pid>

# Confirm process details
ps -p $VLLM_PID -f
```

Verify model path is `/data/tiankuan/zyg/model/GLM-5.2-w8a8`.

**If multiple processes found**: Identify the correct baseline service (check container, user, model path).  
**If no process found**: Report "baseline service not running" and STOP.

### 3. Read Process Command Line

```bash
# Read exact cmdline (null-separated, convert to spaces)
cat /proc/$VLLM_PID/cmdline | tr '\0' ' ' | tee process-cmdline.txt

# Verify readable
cat process-cmdline.txt
```

Search output for `--max-num-batched-tokens`.

**If found**: Record value, proceed to Step 7 (VALUE_VERIFIED via cmdline).  
**If not found**: Continue to Step 4.

### 4. Read Process Working Directory

```bash
# Get working directory
WORK_DIR=$(readlink /proc/$VLLM_PID/cwd)
echo "Working directory: $WORK_DIR" | tee process-cwd.txt

# Or alternative
pwdx $VLLM_PID | tee -a process-cwd.txt
```

### 5. Locate Server Log

```bash
# Expected log from baseline
LOG_FILE="$WORK_DIR/glm52_w8a8.log"

# Check if exists
if [ -f "$LOG_FILE" ]; then
    echo "Log found: $LOG_FILE"
    ls -lh "$LOG_FILE"
else
    echo "Expected log not found at $LOG_FILE"
    # Try alternative: check process file descriptors
    ls -l /proc/$VLLM_PID/fd/ | grep -E "\.log"
fi
```

If log not found at expected location, document actual location or report unavailable.

### 6. Search Server Log for Scheduler Configuration

```bash
# Search for scheduler initialization and config
grep -n -i -E "scheduler|max_num_batched|batch.*token|chunked.*prefill" "$LOG_FILE" | head -100 > scheduler-config-evidence.txt

# Capture initialization phase (first 500 lines usually contain config)
head -500 "$LOG_FILE" > server-log-snippet.txt

# Display findings
cat scheduler-config-evidence.txt
```

**Look for lines like**:
- `Scheduler config: ...`
- `max_num_batched_tokens = <value>`
- `Initializing scheduler with ...`
- Any explicit logging of batch-related parameters

**If found**: Record value and line number, proceed to Step 7 (VALUE_VERIFIED via log).  
**If not found**: Proceed to Step 7 (BASELINE_VALUE_UNVERIFIED).

### 7. Record Runtime Identity

```bash
# Container info
docker ps --filter "name=model-test-zyg-a3" --format "Container: {{.ID}}\nImage: {{.Image}}\nStatus: {{.Status}}" > runtime-identity.txt

# Process details
echo "PID: $VLLM_PID" >> runtime-identity.txt
echo "User: $(ps -p $VLLM_PID -o user=)" >> runtime-identity.txt
echo "Start time: $(ps -p $VLLM_PID -o lstart=)" >> runtime-identity.txt

# Model path verification
echo "Model path: $(cat /proc/$VLLM_PID/cmdline | tr '\0' '\n' | grep -A1 'serve' | tail -1)" >> runtime-identity.txt

# Display
cat runtime-identity.txt
```

### 8. Determine Outcome

**Decision logic**:

```bash
# Check cmdline result
if grep -q "max-num-batched-tokens" process-cmdline.txt; then
    OUTCOME="VALUE_VERIFIED"
    VALUE=$(grep -o "max-num-batched-tokens [0-9]*" process-cmdline.txt | awk '{print $2}')
    SOURCE="process cmdline"
    EVIDENCE=$(grep "max-num-batched-tokens" process-cmdline.txt)
    
elif grep -q -i "max_num_batched_tokens" scheduler-config-evidence.txt; then
    OUTCOME="VALUE_VERIFIED"
    VALUE=$(grep -i "max_num_batched_tokens" scheduler-config-evidence.txt | head -1)
    SOURCE="server log line $(grep -n -i "max_num_batched_tokens" scheduler-config-evidence.txt | head -1 | cut -d: -f1)"
    EVIDENCE=$(grep -i "max_num_batched_tokens" scheduler-config-evidence.txt | head -1)
    
else
    OUTCOME="BASELINE_VALUE_UNVERIFIED"
    VALUE="N/A"
    SOURCE="N/A"
    EVIDENCE="Parameter not in cmdline, not logged in server output"
fi

echo "Outcome: $OUTCOME"
```

### 9. Create Evidence Document

```bash
cat > effective-max-num-batched-tokens.txt <<EOF
STATUS: $OUTCOME

$(if [ "$OUTCOME" = "VALUE_VERIFIED" ]; then
    echo "VALUE: $VALUE"
    echo "SOURCE: $SOURCE"
    echo "EVIDENCE: $EVIDENCE"
else
    echo "REASON: Parameter not explicitly set in cmdline, not logged in server initialization"
    echo "CMDLINE_CHECKED: YES"
    echo "SERVER_LOG_CHECKED: YES"
    echo "ALTERNATIVE_SOURCES_CHECKED: /proc/$VLLM_PID/cmdline, $LOG_FILE"
fi)

OBSERVATION_TIME: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
OBSERVER: A3PerfRunner
EOF

cat effective-max-num-batched-tokens.txt
```

### 10. Create Control SHA Record

```bash
cat > control-sha.txt <<EOF
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT
DISPATCH_CONTROL_SHA: <actual_sha_from_dispatch>
Authorization: EXECUTE
Execution date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
```

Replace `<actual_sha_from_dispatch>` with the SHA provided by User in dispatch.

### 11. Create Manifest

```bash
cat > MANIFEST.txt <<EOF
GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT Evidence Package
Evidence Type: READ-ONLY OPTIMIZATION PREFLIGHT EVIDENCE
Created: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Server state: UNCHANGED (read-only observation)

Files:
EOF

ls -lh runtime-identity.txt process-cmdline.txt process-cwd.txt scheduler-config-evidence.txt server-log-snippet.txt effective-max-num-batched-tokens.txt control-sha.txt >> MANIFEST.txt
```

### 12. Create SHA256 Checksums

```bash
sha256sum runtime-identity.txt process-cmdline.txt process-cwd.txt scheduler-config-evidence.txt server-log-snippet.txt effective-max-num-batched-tokens.txt control-sha.txt MANIFEST.txt > SHA256SUMS.txt

cat SHA256SUMS.txt
```

### 13. Package Evidence

```bash
TIMESTAMP=$(date -u +"%Y%m%d-%H%M%S")
EVIDENCE_DIR="GLM52-W8A8-OPT01-PREFLIGHT-run-$TIMESTAMP"

# Create directory and move files
mkdir -p "$EVIDENCE_DIR"
mv runtime-identity.txt process-cmdline.txt process-cwd.txt scheduler-config-evidence.txt server-log-snippet.txt effective-max-num-batched-tokens.txt control-sha.txt MANIFEST.txt SHA256SUMS.txt "$EVIDENCE_DIR/"

# Create tarball
tar -czf "$EVIDENCE_DIR.tar.gz" "$EVIDENCE_DIR"

# Calculate archive hash
sha256sum "$EVIDENCE_DIR.tar.gz" | tee "$EVIDENCE_DIR.tar.gz.sha256"

echo "Evidence package: $EVIDENCE_DIR.tar.gz"
```

### 14. Upload to GitHub Release

Per D-022:

```bash
# Create GitHub Release
gh release create "preflight-opt01-$TIMESTAMP" \
  --repo yanceng305-collab/vllm-ascend-model-performance-control \
  --title "OPT-01 Preflight: Baseline Value Observation" \
  --notes "READ-ONLY preflight observation for max_num_batched_tokens baseline value.

Outcome: $OUTCOME
Evidence Type: READ-ONLY OPTIMIZATION PREFLIGHT EVIDENCE
Server state: UNCHANGED"

# Upload Evidence archive
gh release upload "preflight-opt01-$TIMESTAMP" \
  "$EVIDENCE_DIR.tar.gz" \
  "$EVIDENCE_DIR.tar.gz.sha256" \
  --repo yanceng305-collab/vllm-ascend-model-performance-control

echo "Uploaded to GitHub Release: preflight-opt01-$TIMESTAMP"
```

### 15. Generate Runner Report

```bash
cat > A3PerfRunner-Report-Preflight.md <<EOF
# A3PerfRunner Report: OPT01 Preflight

**Task**: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT
**Status**: COMPLETE
**Outcome**: $OUTCOME

**Process PID**: $VLLM_PID
**Model path**: /data/tiankuan/zyg/model/GLM-5.2-w8a8
**Container**: model-test-zyg-a3
**Runtime verified**: YES

**max_num_batched_tokens**:
$(if [ "$OUTCOME" = "VALUE_VERIFIED" ]; then
    echo "  Value: $VALUE"
    echo "  Source: $SOURCE"
    echo "  Evidence: $EVIDENCE"
else
    echo "  Status: BASELINE_VALUE_UNVERIFIED"
    echo "  Reason: Parameter not in cmdline, not logged in server output"
    echo "  Cmdline checked: YES"
    echo "  Server log checked: YES"
fi)

**Evidence**: https://github.com/yanceng305-collab/vllm-ascend-model-performance-control/releases/tag/preflight-opt01-$TIMESTAMP
**Archive SHA256**: $(cat "$EVIDENCE_DIR.tar.gz.sha256" | cut -d' ' -f1)

**Server state**: UNCHANGED (read-only observation)
**Observation time**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF

cat A3PerfRunner-Report-Preflight.md
```

---

## Constraints

- **READ-ONLY ONLY**: Do NOT stop, restart, or modify the server
- Do NOT run benchmark
- Do NOT change any server state
- Do NOT modify container
- Do NOT commit Control repo
- Do NOT author Formal Results
- Evidence upload required regardless of outcome (VALUE_VERIFIED or UNVERIFIED)

---

## Rollback Triggers

This is a read-only observation task. There is no rollback because no changes are made.

If the task inadvertently modifies server state:
- **STOP IMMEDIATELY**
- Document what was changed
- Report to PerfControl
- Do NOT attempt to fix without authorization

---

## Success Criteria

1. ✅ Preflight observation completes
2. ✅ Outcome determined (VALUE_VERIFIED or UNVERIFIED)
3. ✅ Evidence captured
4. ✅ Evidence uploaded to GitHub Release
5. ✅ Runner Report generated
6. ✅ Server state unchanged (verified)

---

## What to Report

Send Runner Report to PerfControl immediately after upload completes.

If VALUE_VERIFIED: PerfControl will design OPT-01 candidate based on your observed value.

If UNVERIFIED: PerfControl will design alternative investigation strategy.

---

## References

- Task: `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT.md`
- Blocked OPT Task: `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING.md`
- Baseline: `BASELINE.md`
- D-021: Runner produces Evidence only
- D-022: GitHub Release Asset Evidence Transport
