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

## HyperFrames vs Remotion on Opus 5.5 (2026-11-20)

Lab for the video "Claude Code Animation: HyperFrames vs Remotion, Same Video, Measured". Same rules as above,
on Opus, one build per tool per brief, HyperFrames 0.9.72 and Remotion 4.0.545:

```sh
MODEL=opus HF_VERSION=0.9.72 ./run_build.sh hyperframes opus-b1-1
MODEL=opus REMOTION_VERSION=4.0.545 ./run_build.sh remotion opus-b1-1
MODEL=opus HF_VERSION=0.9.72 BRIEF=BRIEF_explainer.md ./run_build.sh hyperframes opus-b2-1
MODEL=opus REMOTION_VERSION=4.0.545 BRIEF=BRIEF_explainer.md ./run_build.sh remotion opus-b2-1
```

- `BRIEF.md` is brief 1 (the Day 5 Short, 9:16). `BRIEF_explainer.md` is brief 2: a 16:9, 45 s explainer that
  draws six models' scores and costs as bars from `assets_explainer/scores.csv`.
- `HF_VERSION` copies the agent skills shipped in that npm release, unpacked under `~/.cache/hf-skills/<version>`
  (`npm pack hyperframes@0.9.72` and untar it there).
- `run_edit.sh <tool> <run>`: the edit test. Resumes the finished build's session with one change request (bars blue,
  title 80 px higher), keeps the old render as `before.mp4`, and logs the edit to `out/edits.jsonl`. A resumed session
  reports build + edit cost together, so the script subtracts the build's cost.
- `time_split.py`: splits each run's time into model, render, install, check and other tool time, plus network
  stalls (an API request that hung), from Claude Code's own timestamped transcript.
- `render_speed.sh`: re-renders each finished video 3 times with the exact command its agent used, alternating
  the two tools, memory-capped.
- `results/opus-2026-11-20/`: what we got. `builds.jsonl`, `edits.jsonl`, `render_speed.jsonl`, and `quality.md`
  (frame checks, time split, edit and render tables).

Short version: Remotion was faster on the Short (5:31 vs 6:29) and cheaper on every build and edit; HyperFrames
passed every frame check (Remotion's "Why?" at 7.1 s runs off both edges, and its own frame check called it fine)
and rendered 1.4-1.6x faster. One run per tool per brief, so treat it as a strong hint, not a law.
