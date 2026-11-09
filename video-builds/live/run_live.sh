#!/usr/bin/env bash
# The run from the video: one interactive Claude Code session, one line typed in (live/PROMPT.txt).
#   ./live/run_live.sh <run name>     then paste the line from live/PROMPT.txt
# Same isolation as run_build.sh: a fresh folder outside this repo with only BRIEF.md and assets/,
# --setting-sources project + --strict-mcp-config, so no user plugins, CLAUDE.md or MCP servers leak in.
# Needs raea 0.1.0-canary.3 (or newer) unpacked by hand; set RAEA_HOME if it isn't under ~/.cache/raea-trial.
set -euo pipefail
NAME=${1:?run name}
LAB=$(cd "$(dirname "$0")/.." && pwd)
DIR="${VB_RUNS:-$HOME/.cache/video-builds-runs}/$NAME"
[ -e "$DIR" ] && { echo "$DIR exists; pick a new name" >&2; exit 1; }
"$LAB/check_assets.sh"
mkdir -p "$DIR"
cp "$LAB/${BRIEF:-BRIEF.md}" "$DIR/BRIEF.md"
cp -r "$LAB/assets" "$DIR/assets"
RAEA="${RAEA_HOME:-$HOME/.cache/raea-trial/pkg/raea}"
export PATH="$RAEA/bin:$PATH" RAEA_OFFLINE=1 RAEA_AUDIO_AUTOSETUP=0 RAEA_TOOLS_CACHE="${RAEA_TOOLS_CACHE:-$HOME/.cache/raea-trial/tools}"
cd "$DIR"
echo "Paste this line into Claude Code:"; echo; cat "$LAB/live/PROMPT.txt"; echo
exec claude --model sonnet --setting-sources project --strict-mcp-config \
  --permission-mode acceptEdits --allowedTools Bash Read Write Edit Glob Grep
