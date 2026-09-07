#!/bin/bash
# Full-matrix cell driver (one cell = 4 runs; run1 warmup/discard, run2-4 measured)
# Usage: bash cell-driver.sh <CELL> <INPUT_LEN> <CELL_DIR_ABS_IN_CONTAINER>
CELL="$1"; INPUT_LEN="$2"; CELL_DIR="$3"
BASE_URL="http://127.0.0.1:8000"
SERVED_MODEL="glm52-w8a8"
MODEL_PATH="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
mkdir -p "$CELL_DIR"

for RUN in 1 2 3 4; do
  BENCH_ARGS=(vllm bench serve --backend vllm --base-url "$BASE_URL" --endpoint /v1/completions \
    --model "$SERVED_MODEL" --tokenizer "$MODEL_PATH" --trust-remote-code \
    --dataset-name random --random-input-len "$INPUT_LEN" --random-output-len 1024 \
    --random-range-ratio 0 --request-rate inf --max-concurrency 64 --num-prompts 256 \
    --ignore-eos --save-result --result-dir "$CELL_DIR" --result-filename "run${RUN}.json")

  # 1) canonical command artifact FIRST
  python3 -c '
import json, sys
p = sys.argv[1]
argv = sys.argv[2:]
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(argv, f, indent=2)
    f.write("\n")
got = json.load(open(p, encoding="utf-8"))
assert got == argv and got and got[0] == "vllm", "command artifact corruption"
' "$CELL_DIR/run${RUN}.command.txt" "${BENCH_ARGS[@]}" || exit 1

  # 2) execute with exact argv; log via tee
  echo "=== cell=$CELL run=$RUN start $(date -u +%FT%TZ) ==="
  "${BENCH_ARGS[@]}" 2>&1 | tee "$CELL_DIR/run${RUN}.log"
  echo "run${RUN} exit=$?"
done

# run1 role artifact
echo "WARMUP_DISCARD" > "$CELL_DIR/run1.role.txt"
echo "CELL=${CELL}_DONE"