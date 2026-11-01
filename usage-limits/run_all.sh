#!/usr/bin/env bash
# Run every experiment arm in order, stopping before any arm if the 5-hour limit is at or above GUARD %.
# Usage: ./run_all.sh <tinyledger repo> [start-after-epoch]
set -u
cd "$(dirname "$0")"
REPO=$1; START=${2:-0}; GUARD=${GUARD:-60}
while [ "$(date +%s)" -lt "$START" ]; do sleep 20; done

# Last status-line reading; a reading from a window that has since reset counts as 0.
pct() { tail -1 out/limit_meter.jsonl 2>/dev/null | python3 -c '
import json, sys, time
r = json.loads(sys.stdin.read() or "{}")
print(0 if (r.get("five_hour_resets_at") or 0) < time.time() else int(r.get("five_hour_pct") or 0))'; }
arm() {  # arm <name> <model> <prompts> [--mcp]
  local p; p=$(pct)
  if [ "$p" -ge "$GUARD" ]; then echo "STOP before $1: 5-hour limit at $p% (guard $GUARD%)"; exit 3; fi
  echo "=== $1 ($2) at $(date +%T), 5h=$p%"
  python3 drive.py --arm "$1" --model "$2" --repo "$REPO" --prompts "prompts/$3" ${4:-}
}

arm fresh-1      sonnet probe.txt
arm long         sonnet long.txt
arm mcp-1        sonnet probe.txt --mcp
arm fresh-2      sonnet probe.txt
arm mcp-2        sonnet probe.txt --mcp
arm model-haiku  haiku  model_task.txt
arm model-sonnet sonnet model_task.txt
arm model-opus   opus   model_task.txt
echo "=== done at $(date +%T), 5h=$(pct)%"
