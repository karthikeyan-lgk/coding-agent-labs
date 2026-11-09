# Claude Code makes a Short from one text file (raea, HyperFrames, Remotion, fframes)

Lab for the video "Claude Code Video Editing: I Made a 3D Short From One Text File".

## The run from the video (start here)

- `BRIEF.md`: the one text file. It describes the Day 5 Short "first message costs 9x the rest" (1320x2868, 25.8 s):
  look, captions, beat timings, sound effects, and what "done" means (pull out frames and look at them).
- `live/PROMPT.txt`: the one line typed into Claude Code. The `DONE-42` ending only tells a recording script
  when the session has finished.
- `live/run_live.sh <name>`: makes a fresh folder outside the repo with only the brief and `assets/`, then opens
  an interactive Claude Code session (Sonnet, `--setting-sources project --strict-mcp-config`, edits auto-accepted).
  Paste the line in. On camera it took 3 min 57 s on a Pro plan: one crash on the token counter, then three
  layout faults it found itself by looking at frames (stamp over the price, a cross icon drawn as a sliver,
  a wrapped question), all fixed.
- `BRIEF_creative.md`: the same story in 3D with physics (scales, cache jar, stamp, turnstiles). Use it with
  `BRIEF=BRIEF_creative.md ./run_build.sh raea <n>` (or the same variable for `live/run_live.sh`). Our 3D build
  took about 57 min and about 13x the cost of the flat build, including two review passes (`creative/FIXES*.md`).

Before the first run: `./check_assets.sh`. The four sound effects are Pixabay files and are not in this repo;
the script says where to get them. Fonts are Inter and JetBrains Mono (SIL OFL, licences in `assets/`).
raea is canary software; we used the 0.1.0-canary.3 Linux release unpacked by hand under
`~/.cache/raea-trial` (`RAEA_HOME` to change it).

## The four-tool comparison (rounds 1-3)

- `assets/`: fonts, `transcript.json` (word timings) and `vo.wav` (the voiceover); add the SFX first (see above).
- `run_build.sh <tool> <n>`: fresh folder `~/.cache/video-builds-runs/<tool>-<n>` (`VB_RUNS` to change it), the tool's official agent skills only, headless
  `claude -p` on Sonnet with `--setting-sources project --strict-mcp-config` (no user plugins, CLAUDE.md or MCP),
  telemetry tagged `lab.tool` / `lab.run`. One summary line per build goes to `out/builds.jsonl`
  (wall time, turns, tokens by type, API-rate cost, the MP4's size/fps/length).
- Collector -> Prometheus -> Grafana on 24317 / 29090 / 23000 (`docker compose up -d`); dashboard
  "Claude Code: same Short, three tools". Identity fields are deleted in the Collector.

Setup check: `chmod 777 out` before the first `docker compose up` (the Collector container writes out/telemetry.json as uid 10001).

Fairness rules: same brief, model, prompt and isolation for every tool; two runs per tool, both reported.
fframes setup facts (local 1.4.1 path deps, FFmpeg built once into the shared target dir) are given up front,
like having Node installed for the other two; its one-time ~20 min FFmpeg build is stated, not timed.
Uses the Claude Pro login (no API key). Stop the stack when done: `docker compose down`.

Round 3 (2026-11-07): `raea` added, the 0.1.0-canary.3 Linux release unpacked by hand under
`~/.cache/raea-trial` (not the `curl | sh` installer, which writes skills into `~/.claude/skills`), run with
`RAEA_OFFLINE=1`. From this round run folders live outside the repo (`~/.cache/video-builds-runs`, or `VB_RUNS`),
because in rounds 1-2 the repo's own `.claude/skills` were listed in every run (none used them). The HyperFrames
arm now copies the skills from the 0.9.15 plugin. raea-1: 809 s, 27 turns, $0.42; every beat present, sharp,
-14.1 LUFS; OpenH264 baseline video, audio re-encoded to AAC by the agent. One run so far.

The Remotion and fframes arms copy skills and a warm build directory from our working repo (`$REPO/.agents/skills`,
`$REPO/fframes/target`); point those two lines at your own copies of the Remotion agent skills and an fframes checkout.
