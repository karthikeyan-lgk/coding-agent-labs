#!/usr/bin/env bash
# The edit test: resume a finished build's session with one change request, headless, traced.
#   ./run_edit.sh <tool> <run>        (the build must exist in $VB_RUNS/<tool>-<run>)
# Same model, flags and isolation as run_build.sh. The finished out.mp4 is kept as before.mp4 so the two can be
# compared frame by frame. One summary line per edit goes to out/edits.jsonl.
set -euo pipefail
TOOL=${1:?tool}; RUN=${2:?run}
LAB=$(cd "$(dirname "$0")" && pwd)
DIR="${VB_RUNS:-$HOME/.cache/video-builds-runs}/$TOOL-$RUN"
[ -f "$DIR/session.jsonl" ] || { echo "no build at $DIR" >&2; exit 1; }
[ -e "$DIR/edit.jsonl" ] && { echo "$DIR already has an edit" >&2; exit 1; }
SID=$(python3 -c "
import json,sys
sid=None
for l in open(sys.argv[1]):
    try: m=json.loads(l)
    except ValueError: continue
    sid=m.get('session_id') or sid
print(sid)" "$DIR/session.jsonl")
[ "$SID" != "None" ] || { echo "no session id" >&2; exit 1; }
cp -p "$DIR/out.mp4" "$DIR/before.mp4"

if grep -q "16:9 data explainer" "$DIR/BRIEF.md"; then
  REQ="Change request: make every bar in both charts blue (#3b82f6) instead of orange/cyan, and move the opening title 80 px higher. Keep everything else the same. Re-render out.mp4, extract frames at 2, 10 and 26 s and look at them, fix anything that broke, and finish."
else
  REQ="Change request: make both cost bars in the hook (message 1 and message 2+) blue (#3b82f6), and move the 'Your first message' heading 80 px higher. Keep everything else the same. Re-render out.mp4, extract frames at 3.6 and 5.9 s and look at them, fix anything that broke, and finish."
fi

export PATH="$HOME/.cargo/bin:$PATH"
export CLAUDE_CODE_ENABLE_TELEMETRY=1 OTEL_METRICS_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:24317
export OTEL_METRIC_EXPORT_INTERVAL=5000 OTEL_LOGS_EXPORT_INTERVAL=2000
export OTEL_RESOURCE_ATTRIBUTES="lab=video_builds,lab.tool=$TOOL,lab.run=$RUN-edit,lab.model=${MODEL:-sonnet}"

cd "$DIR"
START=$(date +%s)
set +e
timeout 40m claude -p "$REQ" --resume "$SID" --model "${MODEL:-sonnet}" \
  --setting-sources project --strict-mcp-config \
  --permission-mode acceptEdits --allowedTools Bash Read Write Edit Glob Grep \
  --output-format stream-json --verbose > edit.jsonl 2> edit.stderr.log
CODE=$?
set -e
END=$(date +%s)
python3 - "$DIR" "$TOOL" "$RUN" "$((END-START))" "$CODE" <<'EOF' | tee -a "$LAB/out/edits.jsonl"
import hashlib, json, os, sys
def limit_use(path):
    """First and last five-hour / seven-day utilisation the session saw (Pro plan meter, 0-1)."""
    first = last = None
    try:
        for line in open(path):
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") == "rate_limit_event":
                w = m.get("rate_limit_info", {}).get("unifiedWindows", {})
                u = (w.get("five_hour", {}).get("utilization"), w.get("seven_day", {}).get("utilization"))
                first = first or u; last = u
    except OSError: pass
    return {"five_hour_start": first and first[0], "five_hour_end": last and last[0],
            "seven_day_start": first and first[1], "seven_day_end": last and last[1]}
d, tool, run, secs, code = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
def results(path):
    out = []
    if not os.path.exists(path): return out
    for line in open(path):
        try: m = json.loads(line)
        except ValueError: continue
        if m.get("type") == "result": out.append(m)
    return out
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
er, br = results(f"{d}/edit.jsonl"), results(f"{d}/session.jsonl")
res = er[-1] if er else {}
mu = {}
for v in res.get("modelUsage", {}).values():
    for k, n in v.items():
        if isinstance(n, (int, float)): mu[k] = mu.get(k, 0) + n
# On --resume, total_cost_usd/modelUsage may be cumulative (build + edit): keep the raw value and the build's own
# total side by side and decide from the numbers, not from an assumption.
print(json.dumps({"tool": tool, "run": run, "model": os.environ.get("MODEL", "sonnet"), "exit": code, "wall_s": secs,
    "turns": sum(r.get("num_turns") or 0 for r in er), "cost_raw": res.get("total_cost_usd"),
    "build_cost": (br[-1].get("total_cost_usd") if br else None), "output_raw": mu.get("outputTokens"),
    "cache_read_raw": mu.get("cacheReadInputTokens"), "changed": sha(f"{d}/out.mp4") != sha(f"{d}/before.mp4"), **limit_use(f"{d}/edit.jsonl")}))
EOF
