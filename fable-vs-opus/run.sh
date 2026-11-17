#!/usr/bin/env bash
# One run of one viral Opus 5.5 prompt, verbatim, headless.
#   ./run.sh <prompt id> <run number>
# Fresh empty folder outside the repo; Claude Code starts with --setting-sources project + --strict-mcp-config,
# so no user plugins, skills, CLAUDE.md or MCP servers leak in. Only addition to the creator's prompt: one
# delivery line so every run ends in the same place (index.html) and doesn't stop to ask questions.
set -euo pipefail
ID=${1:?prompt id}; RUN=${2:?run}
LAB=$(cd "$(dirname "$0")" && pwd)
PROMPT_FILE="$LAB/prompts/$ID.txt"; [ -f "$PROMPT_FILE" ] || { echo "no prompt $ID" >&2; exit 1; }
DIR="${VP_RUNS:-$HOME/.cache/viral-prompts-runs}/$ID-$RUN"
[ -e "$DIR" ] && { echo "$DIR exists; pick a new run number" >&2; exit 1; }
mkdir -p "$DIR"
MODEL=${VP_MODEL:-opus}
# VP_OPENROUTER=1: route Claude Code to an OpenRouter :free model (VP_MODEL=<id>:free). Every model slot points at
# it, so no call reaches a paid model; key from the repo's root .env, never printed.
if [ "${VP_OPENROUTER:-0}" = 1 ]; then
  case "$MODEL" in *:free) ;; *) echo "VP_OPENROUTER needs a :free model id" >&2; exit 1;; esac
  export ANTHROPIC_BASE_URL=https://openrouter.ai/api ANTHROPIC_API_KEY=
  ANTHROPIC_AUTH_TOKEN=$(grep '^OPENROUTER_API_KEY=' "$LAB/../../../.env" | cut -d= -f2-); export ANTHROPIC_AUTH_TOKEN
  export ANTHROPIC_DEFAULT_HAIKU_MODEL=$MODEL ANTHROPIC_DEFAULT_SONNET_MODEL=$MODEL ANTHROPIC_DEFAULT_OPUS_MODEL=$MODEL
  export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
fi
PROMPT="$(cat "$PROMPT_FILE")

Put the whole thing in index.html in this folder (it must play by itself when opened). Don't ask me questions; make sensible choices and finish."
printf '%s\n' "$PROMPT" > "$DIR/PROMPT.txt"
cd "$DIR"
START=$(date +%s)
set +e
timeout 60m claude -p "$PROMPT" --model "$MODEL" \
  --setting-sources project --strict-mcp-config \
  --permission-mode acceptEdits --allowedTools Bash Read Write Edit Glob Grep \
  --output-format stream-json --verbose > session.jsonl 2> stderr.log
CODE=$?
set -e
END=$(date +%s)
python3 - "$DIR" "$ID" "$RUN" "$((END-START))" "$CODE" <<'EOF' | tee -a "$LAB/out/runs.jsonl"
import json, os, sys
d, pid, run, secs, code = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
results = []
for line in open(f"{d}/session.jsonl"):
    try: m = json.loads(line)
    except ValueError: continue
    if m.get("type") == "result": results.append(m)
res = results[-1] if results else {}
mu, models = {}, list(res.get("modelUsage", {}))
for v in res.get("modelUsage", {}).values():
    for k, n in v.items():
        if isinstance(n, (int, float)): mu[k] = mu.get(k, 0) + n
html = f"{d}/index.html"
print(json.dumps({"prompt": pid, "run": run, "exit": code, "wall_s": secs, "turns": sum(r.get("num_turns") or 0 for r in results),
    "models": models, "cost_usd": res.get("total_cost_usd"), "input": mu.get("inputTokens"),
    "cache_read": mu.get("cacheReadInputTokens"), "cache_write": mu.get("cacheCreationInputTokens"), "output": mu.get("outputTokens"),
    "index_html": os.path.exists(html), "html_kb": round(os.path.getsize(html) / 1024, 1) if os.path.exists(html) else None,
    "files": sorted(f for f in os.listdir(d) if f not in ("session.jsonl", "stderr.log", "PROMPT.txt"))}))
EOF
