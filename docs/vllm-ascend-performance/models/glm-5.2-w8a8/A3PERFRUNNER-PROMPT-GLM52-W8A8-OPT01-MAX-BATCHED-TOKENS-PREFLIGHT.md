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
# IMPORTANT: MATCH_PIDS holds the NUMERIC PID only (e.g. 12345), never "/proc/12345".
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
MATCH_PIDS=""
for d in /proc/[0-9]*/; do
  pid="${d#/proc/}"
  pid="${pid%/}"
  case "$pid" in
    ''|*[!0-9]*) continue ;;          # keep pure numeric PIDs only
  esac
  cmd_text=$(tr '\0' ' ' 2>/dev/null < "/proc/$pid/cmdline" 2>/dev/null || true)
  case "$cmd_text" in
    *"serve"*"$MODEL_PATH"*) MATCH_PIDS="$MATCH_PIDS $pid" ;;
  esac
done
MATCH_PIDS=$(echo $MATCH_PIDS)

MATCH_COUNT=$(set -- $MATCH_PIDS; echo $#)
echo "match-count: $MATCH_COUNT"
echo "match-pids: ${MATCH_PIDS:-<none>}"

VLLM_PID=""
GATE_A="PASS"
GATE_A_REASON=""
if [ "$MATCH_COUNT" -eq 0 ]; then
  GATE_A="FAIL"; GATE_A_REASON="NO_PROCESS"
elif [ "$MATCH_COUNT" -gt 1 ]; then
  GATE_A="FAIL"; GATE_A_REASON="AMBIGUOUS_PROCESS"
else
  VLLM_PID=$(set -- $MATCH_PIDS; echo $1)
  case "$VLLM_PID" in
    ''|*[!0-9]*) VLLM_PID=""; GATE_A="FAIL"; GATE_A_REASON="NON_NUMERIC_PID" ;;
  esac
fi
echo "GATE_A=$GATE_A reason=${GATE_A_REASON:-n/a}"
echo "VLLM_PID=${VLLM_PID:-<unset>}"
```

Resolution rules:

- `0` matches → `GATE_A=FAIL`, reason `NO_PROCESS` → **do not proceed to inference**.
- `>1` matches → `GATE_A=FAIL`, reason `AMBIGUOUS_PROCESS` (list the PIDs) → **do not proceed to inference**.
- exactly `1` → `VLLM_PID` bound automatically and re-checked as a pure integer `^[0-9]+$`.
- A `VLLM_PID` that fails the integer check also flips `GATE_A=FAIL (NON_NUMERIC_PID)`.

Confirm (only when `GATE_A=PASS`):

```bash
ps -p "$VLLM_PID" -o pid=,user=,lstart=,args=
```

If `GATE_A=FAIL`, do **not** read cmdline/log with an empty or non-numeric PID. Skip PID-dependent steps and proceed to the Evidence packaging path (Step 9 onwards) for `RUNTIME_IDENTITY_MISMATCH` — never `exit` before Evidence is packaged.

### 3. Read Process Command Line

Only executes when `GATE_A=PASS`; otherwise writes a placeholder (no missing files).

```bash
if [ "$GATE_A" = "PASS" ]; then
  # Read exact cmdline (null-separated, convert to spaces)
  tr '\0' ' ' < /proc/$VLLM_PID/cmdline > process-cmdline.txt

  # Verify readable
  cat process-cmdline.txt
else
  echo "UNAVAILABLE (GATE_A_FAIL: ${GATE_A_REASON:-unknown})" > process-cmdline.txt
fi
```

Search output for `--max-num-batched-tokens`.

**If found**: Capture the raw value for Step 8 extraction.  
**If not found**: Continue to Step 4.

### 4. Read Process Working Directory

Only executes when `GATE_A=PASS`; otherwise writes a placeholder.

```bash
if [ "$GATE_A" = "PASS" ]; then
  WORK_DIR=$(readlink /proc/$VLLM_PID/cwd 2>/dev/null || true)
  echo "Working directory: $WORK_DIR" > process-cwd.txt
  cat process-cwd.txt
else
  echo "UNAVAILABLE (GATE_A_FAIL: ${GATE_A_REASON:-unknown})" > process-cwd.txt
fi
```

`WORK_DIR` is also resolved again inside Step 5 for the log search.

### 5. Locate Server Log (deterministic)

The frozen server is launched with `nohup ... > glm52_w8a8.log 2>&1`, so stdout/stderr resolve to the log file.

```bash
LOG_FILE=""
if [ "$GATE_A" = "PASS" ]; then
  WORK_DIR=$(readlink /proc/$VLLM_PID/cwd 2>/dev/null || true)
  echo "WORK_DIR=$WORK_DIR" > process-cwd.txt

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
else
  echo "SKIPPED_DUE_TO_GATE_A_FAIL" >> process-cwd.txt
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

`runtime_verified` is always a computed result; it is never a hard-coded `YES`.

```bash
# ---------------- helpers (no state change) ----------------
chk_field() {   # $1 label  $2 expected  $3 observed  (exact match)
  local label="$1" exp="$2" obs="$3" st
  if [ -z "$obs" ] || [ "$obs" = "UNAVAILABLE" ]; then
    st="UNAVAILABLE"
  elif [ "$obs" = "$exp" ]; then
    st="MATCH"
  else
    st="MISMATCH"
  fi
  echo "$label: EXPECTED=$exp OBSERVED=$obs STATUS=$st"
  [ "$st" != "MATCH" ] && RID="MISMATCH"
}

chk_contains() {  # $1 label  $2 expected  $3 observed  (observed contains expected)
  local label="$1" exp="$2" obs="$3" st
  if [ -z "$obs" ] || [ "$obs" = "UNAVAILABLE" ]; then
    st="UNAVAILABLE"
  elif case "$obs" in *"$exp"*) true;; *) false;; esac; then
    st="MATCH"
  else
    st="MISMATCH"
  fi
  echo "$label: EXPECTED=$exp OBSERVED=$obs STATUS=$st"
  [ "$st" != "MATCH" ] && RID="MISMATCH"
}

RID="OK"
{
  echo "GATE_A: ${GATE_A:-unknown} reason=${GATE_A_REASON:-n/a}"
  echo "VLLM_PID: ${VLLM_PID:-<unset>}"
} > runtime-identity.txt

if [ "$GATE_A" = "PASS" ]; then
  # ----- read-only capture -----
  CN=$(docker inspect --format '{{.Name}}' model-test-zyg-a3 2>/dev/null)
  CN=${CN#/}
  IMG_NAME=$(docker inspect --format '{{.Config.Image}}' model-test-zyg-a3 2>/dev/null)
  IMG_ID=$(docker inspect --format '{{.Image}}' model-test-zyg-a3 2>/dev/null)
  VLLM_VER=$(docker exec model-test-zyg-a3 sh -c 'vllm --version 2>/dev/null' 2>/dev/null)
  ASCEND_VER=$(docker exec model-test-zyg-a3 sh -c 'python -c "import vllm_ascend; print(vllm_ascend.__version__)"' 2>/dev/null)

  MODEL_PRESENT=$(grep -c 'GLM-5.2-w8a8' process-cmdline.txt)
  TP_OBS=$(grep -oE -- '--tensor-parallel-size[ =][0-9]+' process-cmdline.txt | grep -oE '[0-9]+' | tail -1)
  MML_OBS=$(grep -oE -- '--max-model-len[ =][0-9]+' process-cmdline.txt | grep -oE '[0-9]+' | tail -1)

  {
    chk_field "container" "model-test-zyg-a3" "$CN"
    echo "image_id: OBSERVED=$IMG_ID STATUS=CAPTURED (frozen baseline has no recorded ID)"
    chk_field "image" "quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3" "$IMG_NAME"
    chk_contains "vllm_version" "0.24.0+empty" "$VLLM_VER"
    chk_contains "vllm_ascend_version" "0.19.1rc2.dev1157+g6443b2a38" "$ASCEND_VER"
    chk_field "model_path" "present" "$( [ "${MODEL_PRESENT:-0}" -ge 1 ] && echo present || echo absent )"
    chk_field "tensor_parallel_size" "16" "$TP_OBS"
    chk_field "max_model_len" "70000" "$MML_OBS"
    chk_field "cmdline_readable" "yes" "$( [ -s process-cmdline.txt ] && echo yes || echo no )"
  } >> runtime-identity.txt
else
  {
    echo "SKIPPED_DUE_TO_GATE_A_FAIL: no process identity observable"
    echo "container: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "image_id: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "image: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "vllm_version: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "vllm_ascend_version: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "model_path: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "tensor_parallel_size: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "max_model_len: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "cmdline_readable: OBSERVED=UNAVAILABLE STATUS=UNAVAILABLE"
    echo "runtime_verified=NO (cannot identify instance)"
  } >> runtime-identity.txt
  RID="MISMATCH"
fi

echo "RUNTIME_GATE=$RID" >> runtime-identity.txt
if [ "$RID" = "OK" ]; then
  echo "runtime_verified=YES (all required fields MATCH)" >> runtime-identity.txt
else
  echo "runtime_verified=NO (not all required identity fields matched)" >> runtime-identity.txt
fi
cat runtime-identity.txt
```

Identity contract (frozen baseline from BASELINE.md):

| Field | Expected | Compare |
|---|---|---|
| container | `model-test-zyg-a3` | exact (`{{.Name}}` minus leading `/`) |
| image name | `quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3` | exact (`{{.Config.Image}}`) |
| image ID | none recorded | captured as `{{.Image}}`, CAPTURED only |
| vLLM | `0.24.0+empty` | observed contains it |
| vLLM-Ascend | `0.19.1rc2.dev1157+g6443b2a38` | observed contains it |
| model path | present in cmdline | required |
| tensor_parallel_size | `16` | exact |
| max_model_len | `70000` | exact |
| cmdline readable | yes | required |

Guarantees:

- Any `MISMATCH` or `UNAVAILABLE` in a required field -> `RID=MISMATCH`.
- `runtime_verified=NO` when version/container capture is UNAVAILABLE (fail-closed).
- `runtime_verified=YES` only when EVERY required field is `MATCH` - computed, never hard-coded.
- GATE A failure => all fields UNAVAILABLE, `RID=MISMATCH`, outcome `RUNTIME_IDENTITY_MISMATCH`.

**If `RID=MISMATCH`** (including GATE A fail): STOP optimization inference. Still package and upload Evidence (outcome `RUNTIME_IDENTITY_MISMATCH`).

### 8. Determine Outcome (integer-guaranteed value; GATE A + GATE B enforced)

Do not let any of these commands abort the run before Evidence is packaged. No `exit` is allowed in this block.

**Decision logic** — three and only three possible outcomes:

```bash
# ---- extract the value as a PURE integer ----
VALUE=""
EVIDENCE_LINE=""
SOURCE=""

# 1) process cmdline: "--max-num-batched-tokens 8192" or "--max-num-batched-tokens=8192"
if [ -n "$VLLM_PID" ] && [ -s process-cmdline.txt ]; then
  RAW=$(grep -oE -- '--max-num-batched-tokens[[:space:]=]+[0-9]+' process-cmdline.txt | head -1)
  if [ -n "$RAW" ]; then
    VALUE=$(printf '%s' "$RAW" | grep -oE '[0-9]+' | tail -1)
    EVIDENCE_LINE="$RAW"
    SOURCE="process cmdline"
  fi
fi

# 2) server log: extract the key/value PAIR from the raw line
#    (supports values embedded inside a larger config line)
if [ -z "$VALUE" ] && [ -n "$LOG_FILE" ] && [ -r "$LOG_FILE" ]; then
  RAW=$(grep -n -i 'max_num_batched_tokens' "$LOG_FILE" | head -1)
  if [ -n "$RAW" ]; then
    PAIR=$(printf '%s' "$RAW" | grep -oE 'max_num_batched_tokens[[:space:]]*[:=][[:space:]]*[0-9]+' | head -1)
    if [ -n "$PAIR" ]; then
      VALUE=$(printf '%s' "$PAIR" | grep -oE '[0-9]+' | tail -1)
      EVIDENCE_LINE="$RAW"
      SOURCE="server log: ${RAW%%:*}"
    fi
  fi
fi

# 3) integer purity: VALUE must match ^[0-9]+$ ; otherwise -> UNVERIFIED
if [ -n "$VALUE" ] && ! printf '%s' "$VALUE" | grep -qE '^[0-9]+$'; then
  VALUE=""
fi

echo "VALUE=${VALUE:-<none>}"
echo "EVIDENCE_LINE=${EVIDENCE_LINE:-<none>}"
echo "SOURCE=${SOURCE:-<none>}"

# ---- final three-way outcome ----
if [ "${GATE_A:-FAIL}" != "PASS" ]; then
  OUTCOME="RUNTIME_IDENTITY_MISMATCH"          # NO_PROCESS / AMBIGUOUS_PROCESS / NON_NUMERIC_PID
elif [ "${RID:-MISMATCH}" = "MISMATCH" ]; then
  OUTCOME="RUNTIME_IDENTITY_MISMATCH"          # GATE B FAIL
elif [ -n "$VALUE" ]; then
  OUTCOME="VALUE_VERIFIED"
else
  OUTCOME="BASELINE_VALUE_UNVERIFIED"
fi
echo "Outcome: $OUTCOME"
```

Rules:

- Command line accepts `--max-num-batched-tokens 8192` (space) and `--max-num-batched-tokens=8192` (equal).
- Log accepts `max_num_batched_tokens=8192`, `max_num_batched_tokens = 8192`, `max_num_batched_tokens: 8192`, and a value embedded in a larger line such as `SchedulerConfig(... max_num_batched_tokens=8192, max_num_seqs=128)`.
- `VALUE` must finally match `^[0-9]+$` (pure integer); anything else clears it -> `BASELINE_VALUE_UNVERIFIED` (never guess a number).
- `EVIDENCE_LINE` always keeps the full raw line where the key was found.
- If the key appears but no integer can be parsed reliably -> `BASELINE_VALUE_UNVERIFIED`.
- Every outcome continues into Evidence packaging (Steps 9-14) and the D-022 upload. There is no exit before packaging on any branch.

### 9. Create Evidence Document

Always created — on every outcome, including `RUNTIME_IDENTITY_MISMATCH` with a GATE A failure.

```bash
{
  echo "STATUS: $OUTCOME"
  echo "GATE_A: ${GATE_A:-n/a}"
  echo "GATE_A_REASON: ${GATE_A_REASON:-n/a}"
  echo "RUNTIME_GATE: ${RID:-n/a}"
  echo "VALUE: ${VALUE:-N/A}"
  echo "SOURCE: ${SOURCE:-N/A}"
  echo "EVIDENCE_LINE: ${EVIDENCE_LINE:-N/A}"
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
{
  echo "GLM52-W8A8-OPT01-MAX-BATCHED-TOKENS-PREFLIGHT Evidence Package"
  echo "Evidence Type: READ-ONLY OPTIMIZATION PREFLIGHT EVIDENCE"
  echo "Created: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  echo "Server state: UNCHANGED (read-only observation)"
  echo "Outcome: $OUTCOME"
  echo ""
  echo "Files:"
} > MANIFEST.txt
for f in runtime-identity.txt process-cmdline.txt process-cwd.txt scheduler-config-evidence.txt server-log-snippet.txt effective-max-num-batched-tokens.txt control-sha.txt; do
  if [ -f "$f" ]; then
    ls -lh "$f"
  else
    echo "MISSING: $f"
  fi
done >> MANIFEST.txt
cat MANIFEST.txt
```

### 12. Create SHA256 Checksums

```bash
for f in runtime-identity.txt process-cmdline.txt process-cwd.txt scheduler-config-evidence.txt server-log-snippet.txt effective-max-num-batched-tokens.txt control-sha.txt MANIFEST.txt; do
  if [ -f "$f" ]; then
    sha256sum "$f"
  else
    echo "MISSING_FILE_FOR_HASH: $f"
  fi
done > SHA256SUMS.txt

cat SHA256SUMS.txt
```

### 13. Package Evidence (immutable)

```bash
TIMESTAMP=$(date -u +"%Y%m%d-%H%M%S")
EVIDENCE_DIR="GLM52-W8A8-OPT01-PREFLIGHT-run-$TIMESTAMP"

# Create directory and move files (never abort on a missing file)
mkdir -p "$EVIDENCE_DIR"
for f in runtime-identity.txt process-cmdline.txt process-cwd.txt scheduler-config-evidence.txt server-log-snippet.txt effective-max-num-batched-tokens.txt control-sha.txt MANIFEST.txt SHA256SUMS.txt; do
  [ -f "$f" ] && mv "$f" "$EVIDENCE_DIR/"
done

# Create tarball
tar -czf "$EVIDENCE_DIR.tar.gz" "$EVIDENCE_DIR"

# Calculate archive hash
sha256sum "$EVIDENCE_DIR.tar.gz" | tee "$EVIDENCE_DIR.tar.gz.sha256"

echo "Evidence package: $EVIDENCE_DIR.tar.gz"
```

Note: the required Evidence files are produced on every branch (placeholders when data is UNAVAILABLE / SKIPPED_DUE_TO_GATE_FAILURE), so the guards above are belt-and-suspenders.

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

1. ✅ PID resolution produces a pure numeric PID (`^[0-9]+$`); 0 matches => NO_PROCESS STOP, >1 => AMBIGUOUS_PROCESS STOP, exactly 1 => bind; never a hand-written `VLLM_PID`.
2. ✅ No pre-packaging `exit` on `NO_PROCESS` / `AMBIGUOUS_PROCESS` / missing log / failed version command; every branch reaches Evidence packaging.
3. ✅ Deterministic log resolution or explicit `LOG_SOURCE_UNAVAILABLE` (no grep on non-existent paths).
4. ✅ Runtime identity actually compared field-by-field (container, image name, image ID captured, vLLM, vLLM-Ascend, model path, TP=16, max-model-len=70000, cmdline); no hard-coded `Runtime verified: YES`.
5. ✅ Outcome is one of `VALUE_VERIFIED` / `BASELINE_VALUE_UNVERIFIED` / `RUNTIME_IDENTITY_MISMATCH`; the three-way gate (GATE A first, then GATE B) is enforced.
6. ✅ `VALUE` is a pure integer `^[0-9]+$`; `EVIDENCE_LINE` keeps the full raw line; unparseable -> UNVERIFIED.
7. ✅ All three outcomes produce the required Evidence files (with placeholders when unavailable), MANIFEST, SHA256SUMS, tar.gz, archive SHA256).
8. ✅ Evidence uploaded to GitHub Release (D-022) for all three outcomes.
9. ✅ Runner Report generated.
10. ✅ Server state unchanged; strictly read-only (no benchmark, no stop/restart, no parameter change, no candidate selection).
11. ✅ Shell snippets pass a static `bash -n` syntax check on the consolidated implementation (local review only, not an A3 execution).

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
