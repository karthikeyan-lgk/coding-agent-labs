#!/usr/bin/env bash
# One build of the brief with one tool, headless, traced.
#   ./run_build.sh <hyperframes|remotion|fframes|raea> <run number>
# Each run gets a fresh folder (runs/<tool>-<n>) holding only BRIEF.md, assets/ and that tool's official agent
# skills (.claude/skills). Claude Code starts with --setting-sources project + --strict-mcp-config, so no user
# plugins, CLAUDE.md or MCP servers leak in: every tool gets the same model, prompt and help.
# Telemetry: lab.tool / lab.run on every metric and event; the session transcript goes to session.jsonl.
set -euo pipefail
TOOL=${1:?tool}; RUN=${2:?run}
LAB=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$LAB/../../.." && pwd)
# From round 3 the run folders live outside the repo, so its .claude/skills can't be listed in a run
# (rounds 1-2 ran in $LAB/runs, where they were listed; no run used them).
DIR="${VB_RUNS:-$HOME/.cache/video-builds-runs}/$TOOL-$RUN"
[ -e "$DIR" ] && { echo "$DIR exists; pick a new run number" >&2; exit 1; }
"$LAB/check_assets.sh"
mkdir -p "$DIR/.claude/skills"
# BRIEF=BRIEF_creative.md picks another brief (copied in as BRIEF.md); the default is the round 1-3 brief.
cp "$LAB/${BRIEF:-BRIEF.md}" "$DIR/BRIEF.md"
cp -r "$LAB/assets" "$DIR/assets"
# Brief 2 adds its data file next to the shared fonts.
if [ "${BRIEF:-}" = "BRIEF_explainer.md" ]; then cp "$LAB/assets_explainer/"* "$DIR/assets/"; fi

case "$TOOL" in
  hyperframes)
    # HF_VERSION pins the CLI and copies the skills shipped in that npm release (unpacked under ~/.cache/hf-skills/<v>);
    # unset = rounds 1-3 (0.9.15 plugin skills, unpinned npx).
    if [ -n "${HF_VERSION:-}" ]; then
      cp -r "$HOME/.cache/hf-skills/$HF_VERSION/package/dist/skills/"* "$DIR/.claude/skills/"
      NOTES="HyperFrames (HTML + GSAP compositions rendered by the hyperframes CLI: npx hyperframes@$HF_VERSION). Node and npm are installed."
    else
      cp -r "$HOME"/.claude/plugins/cache/hyperframes/hyperframes/0.9.15/skills/* "$DIR/.claude/skills/"
      NOTES="HyperFrames (HTML + GSAP compositions rendered by the hyperframes CLI: npx hyperframes). Node and npm are installed."
    fi ;;
  remotion)
    cp -r "$REPO"/.agents/skills/remotion-* "$DIR/.claude/skills/"
    NOTES="Remotion (React; start a project with npx create-video@${REMOTION_VERSION:-latest} or add remotion${REMOTION_VERSION:+@$REMOTION_VERSION} to a new package). Node and npm are installed." ;;
  fframes)
    cp -r "$HOME/src/fframes/skills/fframes-video" "$DIR/.claude/skills/"
    # Setup facts every fframes user hits once (done off camera, same as installing Node for the others):
    # crates.io fframes 1.4.0 lacks captions/3d, so depend on the local 1.4.1 clone; the prebuilt FFmpeg
    # links the wrong x264 ABI, so build it from source once into a shared target dir (already warm).
    NOTES="fframes (Rust). Depend on the local release by path: fframes = { path = \"$HOME/src/fframes/fframes\", features = [\"compile-time-svgtree\", \"cli\", \"captions\", \"3d\", \"wgpu\", \"h264\", \"libav-agree-gpl\"] }, fframes_skia_renderer = { path = \"$HOME/src/fframes/fframes-skia-renderer\", features = [\"vulkan\", \"wgpu\"] }, fframes_native_player = { path = \"$HOME/src/fframes/fframes-native-player\", default-features = false, features = [\"vulkan\", \"audio\"] }. Cargo is at ~/.cargo/bin. The environment already sets CARGO_TARGET_DIR (warm FFmpeg build) and FFMPEG_FORCE_BUILD=1; keep them."
    export CARGO_TARGET_DIR="$REPO/fframes/target" FFMPEG_FORCE_BUILD=1
    # Pin crate versions to a lockfile whose FFmpeg is already built in the shared target dir; otherwise a
    # fresh resolve can change ffmpeg-sys's build hash and the run spends ~25 min compiling FFmpeg
    # (what happened in fframes-1). Same idea as having the toolchain installed.
    [ -f "$LAB/fframes.Cargo.lock" ] && cp "$LAB/fframes.Cargo.lock" "$DIR/Cargo.lock" ;;
  raea)
    # raea 0.1.0-canary.3 Linux release, unpacked by hand (not the curl | sh installer, which writes to ~/.claude/skills).
    RAEA="${RAEA_HOME:-$HOME/.cache/raea-trial/pkg/raea}"
    cp -r "$RAEA"/share/raea/skills/* "$DIR/.claude/skills/"
    export PATH="$RAEA/bin:$PATH" RAEA_OFFLINE=1 RAEA_AUDIO_AUTOSETUP=0 RAEA_TOOLS_CACHE="$HOME/.cache/raea-trial/tools"
    NOTES="raea (React + TypeScript compositions rendered on the GPU by the raea CLI, already on PATH as raea; offline, so no downloads)." ;;
  *) echo "unknown tool $TOOL" >&2; exit 1 ;;
esac

export PATH="$HOME/.cargo/bin:$PATH"
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:24317
export OTEL_METRIC_EXPORT_INTERVAL=5000 OTEL_LOGS_EXPORT_INTERVAL=2000
export OTEL_RESOURCE_ATTRIBUTES="lab=video_builds,lab.tool=$TOOL,lab.run=$RUN,lab.model=${MODEL:-sonnet},lab.brief=${BRIEF:-BRIEF.md}"

# Brief 1 keeps the round 1-3 wording word for word; brief 2 is a 16:9 video, so it says "video".
WHAT="vertical Short"; if [ "${BRIEF:-}" = "BRIEF_explainer.md" ]; then WHAT="video"; fi
PROMPT="Build the $WHAT described in BRIEF.md with $NOTES Work only in this folder; the assets are in assets/. Render it to out.mp4, then check it the way BRIEF.md's 'Done means' says (extract the frames and look at them), fix anything wrong and re-render. Don't ask me questions; make sensible choices and finish."

cd "$DIR"
START=$(date +%s)
set +e
timeout 75m claude -p "$PROMPT" --model "${MODEL:-sonnet}" \
  --setting-sources project --strict-mcp-config \
  --permission-mode acceptEdits --allowedTools Bash Read Write Edit Glob Grep \
  --output-format stream-json --verbose > session.jsonl 2> stderr.log
CODE=$?
set -e
END=$(date +%s)
python3 - "$DIR" "$TOOL" "$RUN" "$((END-START))" "$CODE" <<'EOF' | tee -a "$LAB/out/builds.jsonl"
import json, os, subprocess, sys
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
# A session can end in several "result" messages (one per wake-up from a background task). Their usage and
# num_turns cover only that segment; modelUsage and total_cost_usd on the last one are the session totals.
results = []
for line in open(f"{d}/session.jsonl"):
    try: m = json.loads(line)
    except ValueError: continue
    if m.get("type") == "result": results.append(m)
res = results[-1] if results else {}
mu = {}
for v in res.get("modelUsage", {}).values():
    for k, n in v.items():
        if isinstance(n, (int, float)): mu[k] = mu.get(k, 0) + n
mp4 = f"{d}/out.mp4"
probe = ""
if os.path.exists(mp4):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,r_frame_rate:format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip()
print(json.dumps({"tool": tool, "run": run, "model": os.environ.get("MODEL", "sonnet"), "brief": os.environ.get("BRIEF", "BRIEF.md"), "exit": code, "wall_s": secs, "turns": sum(r.get("num_turns") or 0 for r in results),
    "results": len(results), "cost_usd": res.get("total_cost_usd"), "input": mu.get("inputTokens"),
    "cache_read": mu.get("cacheReadInputTokens"), "cache_write": mu.get("cacheCreationInputTokens"), "output": mu.get("outputTokens"),
    "out_mp4": os.path.exists(mp4), "probe": probe, **limit_use(f"{d}/session.jsonl")}))
EOF
