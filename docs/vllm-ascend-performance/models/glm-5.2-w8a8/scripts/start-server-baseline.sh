#!/usr/bin/env bash
#
# GLM-5.2-W8A8 Server Launch (User-verified baseline)
# Do not modify these parameters without creating a new Decision and updating BASELINE.md
# This is the BASELINE configuration. Optimizations must be tracked as separate OPT Tasks.
#

set -euo pipefail

export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15

MODEL="/data/tiankuan/zyg/model/GLM-5.2-w8a8"
LOG_FILE="${LOG_FILE:-glm52_w8a8.log}"

if [ ! -d "$MODEL" ]; then
  echo "ERROR: Model directory not found: $MODEL"
  exit 1
fi

if pgrep -f "vllm serve.*GLM-5.2-w8a8" > /dev/null; then
  echo "WARNING: vLLM server for GLM-5.2-w8a8 may already be running"
  echo "Check with: ps aux | grep 'vllm serve'"
  echo "If you want to proceed anyway, manually kill the existing process first"
  exit 1
fi

echo "Starting vLLM server for GLM-5.2-W8A8"
echo "Model: $MODEL"
echo "Log file: $LOG_FILE"
echo "This will run in background. Graph compilation may take significant time."
echo ""

nohup vllm serve "$MODEL" \
  --tensor-parallel-size 16 \
  --max-model-len 70000 \
  --gpu-memory-utilization 0.9 \
  --quantization ascend \
  --trust-remote-code \
  --no-enable-prefix-caching \
  --no-enable-log-requests \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  > "$LOG_FILE" 2>&1 &

SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Log file: $LOG_FILE"
echo ""
echo "To monitor: tail -f $LOG_FILE"
echo "To check readiness: curl http://127.0.0.1:8000/v1/models"
echo "To stop: kill $SERVER_PID  (or use stop-server.sh)"
echo ""
echo "Wait for graph compilation to complete before running benchmarks."
