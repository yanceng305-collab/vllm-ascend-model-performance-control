#!/usr/bin/env bash
#
# GLM-5.2-W8A8 Server Stop
# Safely stops the vLLM server without affecting other processes
#

set -euo pipefail

echo "Looking for vLLM server processes for GLM-5.2-w8a8..."

PIDS=$(pgrep -f "vllm serve.*GLM-5.2-w8a8" || true)

if [ -z "$PIDS" ]; then
  echo "No vLLM server process found for GLM-5.2-w8a8"
  exit 0
fi

echo "Found vLLM server process(es):"
ps aux | grep "vllm serve.*GLM-5.2-w8a8" | grep -v grep || true
echo ""

echo "PIDs to stop: $PIDS"
echo "Sending SIGTERM..."

for PID in $PIDS; do
  kill "$PID" || true
done

echo "Waiting for graceful shutdown (max 30 seconds)..."
WAITED=0
while [ $WAITED -lt 30 ]; do
  REMAINING=$(pgrep -f "vllm serve.*GLM-5.2-w8a8" || true)
  if [ -z "$REMAINING" ]; then
    echo "Server stopped successfully"
    exit 0
  fi
  sleep 1
  WAITED=$((WAITED + 1))
done

echo "Graceful shutdown timed out. Checking if processes are still running..."
REMAINING=$(pgrep -f "vllm serve.*GLM-5.2-w8a8" || true)

if [ -n "$REMAINING" ]; then
  echo "WARNING: Processes still running: $REMAINING"
  echo "You may need to manually kill with: kill -9 $REMAINING"
  exit 1
else
  echo "Server stopped"
  exit 0
fi
