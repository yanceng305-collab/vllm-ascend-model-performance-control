#!/usr/bin/env bash
#
# GLM-5.2-W8A8 Benchmark Matrix (User-verified baseline workload)
# Do not modify workload parameters without creating a new Task and separate Result
#

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-/data/tiankuan/zyg/model/GLM-5.2-w8a8}"
RESULT_ROOT="${RESULT_ROOT:-/workspace/glm52_w8a8_bench}"

OUTPUT_LEN=1024
CONCURRENCY=64
NUM_PROMPTS=256
RUNS=4

MODE="${1:-all}"

case "$MODE" in
  all)
    INPUTS=(1024 4096 16384 65536)
    ;;
  1024|4096|16384|65536)
    INPUTS=("$MODE")
    ;;
  *)
    echo "Usage: $0 {all|1024|4096|16384|65536}"
    exit 2
    ;;
esac

echo "Checking vLLM endpoint: ${BASE_URL}/v1/models"
if ! curl -fsS "${BASE_URL}/v1/models" >/dev/null; then
  echo "ERROR: vLLM server not reachable at ${BASE_URL}"
  echo "Start the server with start-server-baseline.sh first"
  exit 1
fi

mkdir -p "$RESULT_ROOT"

for INPUT_LEN in "${INPUTS[@]}"; do
  CELL="i${INPUT_LEN}_o${OUTPUT_LEN}_c${CONCURRENCY}"
  CELL_DIR="${RESULT_ROOT}/${CELL}"

  mkdir -p "$CELL_DIR"

  echo "=================================================="
  echo "Cell: $CELL"
  echo "Input: $INPUT_LEN"
  echo "Output: $OUTPUT_LEN"
  echo "Concurrency: $CONCURRENCY"
  echo "Prompts: $NUM_PROMPTS"
  echo "Runs: $RUNS"
  echo "=================================================="

  for RUN in 1 2 3 4; do
    echo
    echo "===== ${CELL} Run ${RUN}/${RUNS} ====="

    vllm bench serve \
      --backend vllm \
      --base-url "$BASE_URL" \
      --endpoint /v1/completions \
      --model "$MODEL" \
      --tokenizer "$MODEL" \
      --trust-remote-code \
      --dataset-name random \
      --random-input-len "$INPUT_LEN" \
      --random-output-len "$OUTPUT_LEN" \
      --random-range-ratio 0 \
      --request-rate inf \
      --max-concurrency "$CONCURRENCY" \
      --num-prompts "$NUM_PROMPTS" \
      --ignore-eos \
      --save-result \
      --result-dir "$CELL_DIR" \
      --result-filename "run${RUN}.json" \
      2>&1 | tee "${CELL_DIR}/run${RUN}.log"

    if [ ! -s "${CELL_DIR}/run${RUN}.json" ]; then
      echo "ERROR: run${RUN}.json not created or is empty"
      exit 1
    fi
  done

  echo
  echo "Aggregating runs for $CELL (mean of run2/run3/run4; run1 discarded)..."

  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  if [ -f "$SCRIPT_DIR/summarize-runs.py" ]; then
    python3 "$SCRIPT_DIR/summarize-runs.py" "$CELL_DIR"
  else
    echo "WARNING: summarize-runs.py not found in $SCRIPT_DIR"
    echo "Skipping aggregation. Run manually: python3 summarize-runs.py $CELL_DIR"
  fi

  echo
  echo "Finished $CELL"
  if [ -f "${CELL_DIR}/average_run2_4.txt" ]; then
    echo "Summary: ${CELL_DIR}/average_run2_4.txt"
    echo "--- Summary Preview ---"
    head -20 "${CELL_DIR}/average_run2_4.txt"
  fi
  echo
done

echo "=================================================="
echo "Benchmark matrix complete"
echo "Results saved to: $RESULT_ROOT"
echo "=================================================="
