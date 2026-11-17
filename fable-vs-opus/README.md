# Fable 5.2 vs Opus 5.5 in Claude Code: same 5 prompts, measured

Lab for the video [Fable 5.2 vs Opus 5.5 in Claude Code: Same 5 Prompts, Measured](https://youtu.be/CeH4KlnmQtY).

Five viral prompts, copied word for word from their creators (see [prompts/CREDITS.md](prompts/CREDITS.md)), each run
headless in a fresh empty folder. Claude Code starts with `--setting-sources project --strict-mcp-config`, so no
plugins, skills, CLAUDE.md or MCP servers leak in. The only line added to each prompt asks for one `index.html` and
no questions. Only the model changes.

## Results

Scores are 4 checks written before any Fable result: plays by itself, matches the prompt, text readable at 1080p,
no broken scene. Cost is the API-rate estimate from Claude Code's own usage report (`total_cost_usd`); on a
subscription it shows up as your usage limit instead.

| prompt | model | time | turns | tokens read (cache) | tokens written | cost | checks |
|---|---|---|---|---|---|---|---|
| token-bucket | Opus 5.5 | 2 min 30 s | 8 | 120,339 | 14,702 | $0.52 | 4/4 |
| token-bucket | Fable 5.2 | 7 min 02 s | 16 | 210,718 | 37,834 | $2.48 | 4/4 |
| business-explainer | Opus 5.5 | 4 min 12 s | 24 | 515,351 | 17,606 | $0.94 | 3/4 |
| business-explainer | Fable 5.2 | 4 min 09 s | 16 | 182,716 | 21,434 | $1.84 | 4/4 |
| ai-datacentre | Opus 5.5 | 12 min 30 s | 22 | 1,035,828 | 73,725 | $2.53 | 4/4 |
| ai-datacentre | Fable 5.2 | 11 min 35 s | 18 | 360,047 | 59,190 | $3.81 | 3/4 |
| recursion | Opus 5.5 | 15 min 26 s | 23 | 1,118,273 | 84,632 | $2.99 | 3/4 |
| recursion | Fable 5.2 | 9 min 40 s | 16 | 395,493 | 51,501 | $3.29 | 4/4 |
| qr-codes | Opus 5.5 | 26 min 41 s | 38 | 3,223,918 | 108,370 | $3.96 | 4/4 |
| qr-codes | Fable 5.2 | 18 min 28 s | 6 | 47,628 | 74,815 | $4.11 | 4/4 |
| **total** | **Opus 5.5** | **61 min** | **115** | **6,013,709** | **299,035** | **$10.93** | **18/20** |
| **total** | **Fable 5.2** | **51 min** | **72** | **1,196,602** | **244,774** | **$15.53** | **19/20** |

Claude Code 2.1.322 (Opus) / 2.1.323 (Fable), models `claude-opus-5-5` and `claude-fable-5-2`.

## What's here

- `prompts/` the five prompts, verbatim, and their credits.
- `results/<prompt>/opus.html`, `fable.html` the pages each model wrote, unedited. Open them in Chrome. Opus's
  recursion page isn't included: one of its scenes looks like a famous game, so it's blurred in the video too.
- `out/runs.jsonl` every run, including retries and later runs of the same prompts on free OpenRouter models
  (`run` = `free-*`, see `run_free.sh`; those are for a separate video).
- `run.sh <prompt> <run>` one run. `VP_MODEL=fable` for Fable; `VP_OPENROUTER=1 VP_MODEL=<id>:free` for a free model.
- `record.mjs`, `still.mjs`, `clock.mjs` record a page to MP4 / stills on a virtual clock, so a busy machine can't drop frames.
- `sidebyside.py` the side-by-side clips used in the video.

The screen recordings aren't in the repo (about 230 MB); everything in them can be re-made with `record.mjs`.
