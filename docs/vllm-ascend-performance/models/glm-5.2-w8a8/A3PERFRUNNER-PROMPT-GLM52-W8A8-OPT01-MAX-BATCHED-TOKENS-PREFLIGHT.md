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
**Constraint**: ABSOLUTELY READ-ONLY — no server restart, no modifications, no benchmark, no parameter change, no candidate selection  
**Outcome** (exactly one of three): `VALUE_VERIFIED` / `BASELINE_VALUE_UNVERIFIED` / `RUNTIME_IDENTITY_MISMATCH`

---

## Execution Checklist

### 1. Verify Dispatch Authorization

```
Task ID: GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT
DISPATCH_CONTROL_SHA: <from User>
Authorization: EXECUTE
```

Only proceed if all three present.

### 2. (GATE A) Locate vLLM Process — deterministic, single match required

Do **not** hand-write `VLLM_PID=<...>`. Auto-scan `/proc` and bind the PID only on exactly one unambiguous match.

```bash
# Auto-scan every PID whose cmdline contains "serve" AND the exact model path.
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
MATCH_PIDS=""
for d in /proc/[0-9]*/; do
  cmd_text=$(tr '\0' ' ' 2>/dev/null < "${d}cmdline" 2>/dev/null || true)
  case "$cmd_text" in
    *"serve"*"$MODEL_PATH"*) MATCH_PIDS="$MATCH_PIDS ${d%/}";;
  esac
done
MATCH_PIDS=$(echo $MATCH_PIDS | tr '\n' ' ')

MATCH_COUNT=$(set -- $MATCH_PIDS; echo $#)
echo "match-count: $MATCH_COUNT"
echo "match-pids: ${MATCH_PIDS:-<none>}"

VLLM_PID=""
if [ "$MATCH_COUNT" -eq 1 ]; then
  VLLM_PID=$(set -- $MATCH_PIDS; echo $1)
  echo "VLLM_PID=$VLLM_PID"
else
  echo "GATE A FAIL"
fi
```

Resolution rules:

- `0` matches → **STOP**. Outcome = `RUNTIME_IDENTITY_MISMATCH`, reason `NO_PROCESS`.
- `>1` matches → **STOP**. Outcome = `RUNTIME_IDENTITY_MISMATCH`, reason `AMBIGUOUS_PROCESS` (list the PIDs).
- exactly `1` → `VLLM_PID` bound automatically by the script. Confirm with:

```bash
ps -p "$VLLM_PID" -o pid=,user=,lstart=,args=
```

If `VLLM_PID` is empty after GATE A, stop further observation (no cmdline/log reads with an empty PID) and go to Evidence packaging for a `RUNTIME_IDENTITY_MISMATCH` failure.

### 3. Read Process Command Line

```bash
# Read exact cmdline (null-separated, convert to spaces)
cat /proc/$VLLM_PID/cmdline | tr '\0' ' ' | tee process-cmdline.txt

# Verify readable
cat process-cmdline.txt
```

Search output for `--max-num-batched-tokens`.

**If found**: Capture the raw value for Step 8 extraction.  
**If not found**: Continue to Step 4.

### 4. Read Process Working Directory

```bash
# Get working directory
WORK_DIR=$(readlink /proc/$VLLM_PID/cwd)
echo "Working directory: $WORK_DIR" | tee process-cwd.txt

# Or alternative
pwdx $VLLM_PID | tee -a process-cwd.txt
```

### 5. Locate Server Log (deterministic)

The frozen server is launched with `nohup ... > glm52_w8a8.log 2>&1`, so stdout/stderr resolve to the log file.

```bash
if [ -z "$VLLM_PID" ]; then exit 0; fi
WORK_DIR=$(readlink /proc/$VLLM_PID/cwd 2>/dev/null || true)
echo "WORK_DIR=$WORK_DIR" > process-cwd.txt

LOG_FILE=""

# Priority 1: preferred log inside the working directory
if [ -r "$WORK_DIR/glm52_w8a8.log" ]; then
  LOG_FILE="$WORK_DIR/glm52_w8a8.log"
else
  # Priority 2: resolve real stdout/stderr target through process file descriptors
  fd1=$(readlink /proc/$VLLM_PID/fd/1 2>/dev/null || true)
  fd2=$(readlink /proc/$VLLM_PID/fd/2 2>/dev/null || true)
  echo "fd1=$fd1"; echo "fd2=$fd2"
  for cand in "$fd1" "$fd2"; do
    if [ -n "$cand" ] && [ -f "$cand" ] && [ -r "$cand" ]; then
      LOG_FILE="$cand"; break
    fi
  done
fi

if [ -z "$LOG_FILE" ]; then
  echo "LOG_SOURCE_UNAVAILABLE"
fi
echo "LOG_FILE=${LOG_FILE:-<unset>}"
```

- If `$WORK_DIR/glm52_w8a8.log` is readable, use it.
- Otherwise resolve `/proc/$VLLM_PID/fd/1` and `/proc/$VLLM_PID/fd/2` and use the first readable target.
- If neither yields a readable log → `LOG_SOURCE_UNAVAILABLE`. Do **not** keep grep non-existent paths. Still write `scheduler-config-evidence.txt` stating availability `unavailable`.

### 6. Search Server Log for Scheduler Configuration

```bash
if [ -n "$LOG_FILE" ] && [ -r "$LOG_FILE" ]; then
  # Search for scheduler initialization and config
  grep -n -i -E "scheduler|max_num_batched|batch.*token|chunked.*prefill" "$LOG_FILE" | head -100 > scheduler-config-evidence.txt

  # Capture initialization phase (first 500 lines usually contain config)
  head -500 "$LOG_FILE" > server-log-snippet.txt

  # Display findings
  cat scheduler-config-evidence.txt
else
  echo "LOG_SOURCE_UNAVAILABLE" > scheduler-config-evidence.txt
  echo "(server log unavailable)" > server-log-snippet.txt
fi
```

**Look for lines like**:
- `Scheduler config: ...`
- `max_num_batched_tokens = <value>`
- `Initializing scheduler with ...`
- Any explicit logging of batch-related parameters

**If found**: Capture the raw match line for Step 8 value extraction.  
**If not found**: Proceed to Step 8.

### 7. (GATE B) Record and Cross-check Runtime Identity

Capture and compare the observed runtime against the frozen baseline. Do **not** hard-code `Runtime verified: YES` — it is always a computed result.

```bash
# --- 0) capture raw identity ---
{
  echo "container=$(docker ps --filter name=model-test-zyg-a3 --format '{{.Names}}' | head -1)"
  echo "image=$(docker inspect --format '{{.Image}}' model-test-zyg-a3 2>/dev/null)"
  echo "vllm_version=$(docker exec model-test-zyg-a3 sh -c 'vllm --version 2>/dev/null' 2>/dev/null)"
  echo "vllm_ascend_version=$(docker exec model-test-zyg-a3 sh -c 'python -c "import vllm_ascend as v;print(getattr(v,\"__version__\",\"n/a\"))" 2>/dev/null' 2>/dev/null)"
  echo "model_path_present=$(grep -c '/data/tiankuan/zyg/model/GLM-5.2-w8a8' process-cmdline.txt)"
  echo "tensor_parallel_size=$(grep -oE -- '--tensor-parallel-size[ =][0-9]+' process-cmdline.txt | grep -oE '[0-9]+' | tail -1)"
  echo "max_model_len=$(grep -oE -- '--max-model-len[ =][0-9]+' process-cmdline.txt | grep -oE '[0-9]+' | tail -1)"
  echo "cmdline_present=$([ -s process-cmdline.txt ] && echo yes || echo no)"
} > runtime-identity.txt
cat runtime-identity.txt

# --- expected values from frozen baseline ---
# required (must match exactly):
#   model path present, tensor_parallel_size=16, max_model_len=70000, cmdline present
# optional (compared only if observed; if missing record UNMEASURED, do not fail):
#   container=model-test-zyg-a3, image=quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3
#   vllm=0.24.0+empty, vllm_ascend=0.19.1rc2.dev1157+g6443b2a38

RID="OK"
[ "$(grep -c 'model/GLM-5.2-w8a8' process-cmdline.txt)" -ge 1 ] || { echo "MISMATCH: model path"; RID="MISMATCH"; }
TP_NUM=$(grep -oE -- '--tensor-parallel-size[ =][0-9]+' process-cmdline.txt | grep -oE '[0-9]+' | tail -1)
[ "$TP_NUM" = "16" ] || { echo "MISMATCH: TP=$TP_NUM expected 16"; RID="MISMATCH"; }
MML=$(grep -oE -- '--max-model-len[ =][0-9]+' process-cmdline.txt | grep -oE '[0-9]+' | tail -1)
[ "$MML" = "70000" ] || { echo "MISMATCH: max_model_len=$MML expected 70000"; RID="MISMATCH"; }
[ -s process-cmdline.txt ] || { echo "MISMATCH: cmdline missing"; RID="MISMATCH"; }

echo "RUNTIME_GATE=$RID"
echo "runtime_verified=NO (computed gate)" >> runtime-identity.txt
echo "runtime_identity_gate=$RID" >> runtime-identity.txt
```

Verify at minimum: container, image (and image ID/digest if available), vLLM version, vLLM-Ascend version, model path, TP=16, max-model-len=70000, process cmdline. Which and where possible these are already reflected above.

**If `RID=MISMATCH`**: STOP optimization inference. Still package and upload Evidence (as `RUNTIME_IDENTITY_MISMATCH`).

### 8. Determine Outcome (integer-guaranteed value; GATE A + GATE B enforced)

**Decision logic** — three and only three possible outcomes:

```bash
# ---- extract the value as a PURE integer ----
VALUE=""
EVIDENCE_LINE=""
SOURCE=""

# cmdline: supports "--max-num-batched-tokens 8192" and "--max-num-batched-tokens=8192"
RAW=$(grep -oE -- '--max-num-batched-tokens[[:space:]=]+[0-9]+' process-cmdline.txt | head -1)
if [ -n "$RAW" ]; then
  VALUE=$(printf '%s' "$RAW" | grep -oE '[0-9]+$')
  EVIDENCE_LINE="$RAW"
  SOURCE="process cmdline"
fi

# server log form: max_num_batched_tokens=8192  (only if log resolvable)
if [ -z "$VALUE" ] && [ -n "$LOG_FILE" ] && [ -r "$LOG_FILE" ]; then
  RAW=$(grep -n -i 'max_num_batched_tokens' "$LOG_FILE" | head -1)
  if [ -n "$RAW" ]; then
    VALUE=$(printf '%s' "$RAW" | grep -oE '[0-9]+$')
    [ -n "$VALUE" ] && { SOURCE="" ; EVIDENCE_LINE="$RAW" ; SOURCE="server log line ${RAW%%:*}" ; }
  fi
fi

# integer purity: VALUE must match ^[0-9]+$ ; otherwise clear it -> UNVERIFIED
if [ -n "$VALUE" ] && ! printf '%s' "$VALUE" | grep -qE '^[0-9]+$'; then
  VALUE=""
fi

echo "VALUE=${VALUE:-<none>}"
echo "EVIDENCE_LINE=${EVIDENCE_LINE:-<none>}"

# ---- final three-way outcome ----
if [ -z "${VLLM_PID:-}" ]; then
  OUTCOME="RUNTIME_IDENTITY_MISMATCH"                    # GATE A FAIL: NO_PROCESS / AMBIGUOUS_PROCESS
elif [ "${RID:-}" = "MISMATCH" ]; then
  OUTCOME="RUNTIME_IDENTITY_MISMATCH"                   # GATE B FAIL: frozen identity not matched
elif [ -n "$VALUE" ]; then
  OUTCOME="VALUE_VERIFIED"
else
  OUTCOME="BASELINE_VALUE_UNVERIFIED"
fi

echo "Outcome: $OUTCOME"
```

Rules:

- Value extraction tolerates the space form, the `=` form, and the log form; `VALUE` must always end up `^[0-9]+$` (a pure integer).
- If you can only find the token but not a reliably parse integer → `BASELINE_VALUE_UNVERIFIED` (never invent a number).
- The raw evidence capture stays in `EVIDENCE_LINE` regardless of outcome.
- `RUNTIME_IDENTITY_MISMATCH` means optimization inference is STOPPED (no candidate selection).

### 9. Create Evidence Document

```bash
{
  echo "STATUS: $OUTCOME"
  echo "VALUE: ${VALUE:-N/A}"
  echo "SOURCE: ${SOURCE:-N/A}"
  echo "EVIDENCE_LINE: ${EVIDENCE_LINE:-N/A}"
  echo "RUNTIME_GATE: ${RID:-N/A}"
  echo "VLLM_PID: ${VLLM_PID:-N/A}"
  echo "LOG_FILE: ${LOG_FILE:-LOG_SOURCE_UNAVAILABLE}"
  echo "OBSERVATION_TIME: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  echo "OBSERVER: A3PerfRunner"
} > effective-max-num-batched-tokens.txt

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

**Process PID**: ${VLLM_PID:-<none>}
**Model path**: /data/tiankuan/zyg/model/GLM-5.2-w8a8
**Runtime identity gate**: ${RID:-N/A}
**Runtime verified**: NO (computed gate; never hard-coded)

**max_num_batched_tokens**:
  Value: ${VALUE:-N/A}
  Source: ${SOURCE:-N/A}
  Evidence line: ${EVIDENCE_LINE:-N/A}

**Evidence**: https://github.com/yanceng305-collab/vllm-ascend-model-performance-control/releases/tag/preflight-opt01-$TIMESTAMP
**Archive SHA256**: $(cut -d' ' -f1 "$EVIDENCE_DIR.tar.gz.sha256")

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
- Do NOT change any launch parameter
- Do NOT select an optimization candidate
- Do NOT commit Control repo
- Do NOT author Formal Results
- Evidence upload required regardless of outcome (`VALUE_VERIFIED`, `BASELINE_VALUE_UNVERIFIED`, or `RUNTIME_IDENTITY_MISMATCH`)

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

1. ✅ Deterministic PID resolution (0 / >1 / exactly 1 all handled; never a hand-written PID)
2. ✅ Deterministic log resolution or explicit `LOG_SOURCE_UNAVAILABLE`
3. ✅ Runtime identity actually cross-checked (no hard-coded "Runtime verified: YES")
4. ✅ Outcome determined — one of `VALUE_VERIFIED` / `BASELINE_VALUE_UNVERIFIED` / `RUNTIME_IDENTITY_MISMATCH`
5. ✅ Evidence captured (with integer-guarded VALUE, else UNVERIFIED)
6. ✅ Evidence uploaded to GitHub Release (all three outcomes)
7. ✅ Runner Report generated
8. ✅ Server state unchanged (verified)

---

## What to Report

Send Runner Report to PerfControl immediately after upload completes.

If `VALUE_VERIFIED`: PerfControl will design an OPT-01 candidate based on the observed (integer) value.

If `BASELINE_VALUE_UNVERIFIED`: PerfControl will design an alternative investigation strategy.

If `RUNTIME_IDENTITY_MISMATCH`: PerfControl will review runtime identity; optimization inference is STOPPED.

---

## References

- Task: `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT.md`
- Blocked OPT Task: `TASK-GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-SCREENING.md`
- Baseline: `BASELINE.md`
- D-021: Runner produces Evidence only
- D-022: GitHub Release Asset Evidence Transport
