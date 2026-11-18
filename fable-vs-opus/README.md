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


## Free models on OpenRouter (second video)

Video: [How to Use Claude Code for Free: I Tested 4 Free Models (Real Numbers)](https://youtu.be/9CluUS52Fdg).
The same 5 prompts and the same 4 checks, run with `run_free.sh` on four `:free` OpenRouter models, all three
`ANTHROPIC_DEFAULT_*_MODEL` slots set to the same model. Every run cost $0.00: the OpenRouter key's usage before
and after each run didn't change. Claude Code's own `total_cost_usd` prices these models as if they were paid, so
it's left out here. `exit 1` with a page means the run stopped after the page was written (usually a text-only
model being sent a screenshot: `400 No endpoints found that support image input`).

| prompt | model | time | turns | exit | page | checks |
|---|---|---|---|---|---|---|
| token-bucket | Flint v1.0 | 3 min 30 s | 10 | 1 | [free-flint.html](results/token-bucket/free-flint.html) | 3/4 |
| token-bucket | ERNIE 5.5 Flash | 4 min 51 s | 18 | 1 | [free-ernie.html](results/token-bucket/free-ernie.html) | 4/4 |
| token-bucket | north-mini-code | 1 min 32 s | 21 | 0 | [free-north.html](results/token-bucket/free-north.html) | 1/4 |
| token-bucket | dots-3 | 7 min 35 s | 5 | 0 | [free-dots-3.html](results/token-bucket/free-dots-3.html) | 3/4 |
| business-explainer | Flint v1.0 | 3 min 33 s | 8 | 0 | [free-flint.html](results/business-explainer/free-flint.html) | 3/4 |
| business-explainer | ERNIE 5.5 Flash | 2 min 58 s | 9 | 1 | [free-ernie.html](results/business-explainer/free-ernie.html) | 3/4 |
| business-explainer | north-mini-code | 1 min 03 s | 6 | 0 | [free-north.html](results/business-explainer/free-north.html) | 2/4 |
| business-explainer | dots-3 | 20 min 41 s | 45 | 0 | [free-dots-3.html](results/business-explainer/free-dots-3.html) | 1/4 |
| ai-datacentre | Flint v1.0 | 14 min 25 s | 33 | 1 | [free-flint.html](results/ai-datacentre/free-flint.html) | 3/4 |
| ai-datacentre | ERNIE 5.5 Flash | 7 min 19 s | 20 | 1 | [free-ernie.html](results/ai-datacentre/free-ernie.html) | 3/4 |
| ai-datacentre | north-mini-code | 0 min 53 s | 7 | 0 | [free-north.html](results/ai-datacentre/free-north.html) | 2/4 |
| ai-datacentre | dots-3 | 5 min 22 s | 17 | 1 | none | 0/4 |
| recursion | Flint v1.0 | 3 min 13 s | 7 | 1 | [free-flint.html](results/recursion/free-flint.html) | 2/4 |
| recursion | ERNIE 5.5 Flash | 0 min 15 s | 7 | 1 | none | 0/4 |
| recursion | north-mini-code | 1 min 26 s | 9 | 0 | [free-north.html](results/recursion/free-north.html) | 1/4 |
| recursion | dots-3 | 6 min 25 s | 2 | 1 | none | 0/4 |
| qr-codes | Flint v1.0 | 2 h 00 min | 65 | 1 | [free-flint.html](results/qr-codes/free-flint.html) | 3/4 |
| qr-codes | ERNIE 5.5 Flash | 9 min 28 s | 26 | 1 | not included (crashes the tab) | 0/4 |
| qr-codes | north-mini-code | 2 min 38 s | 11 | 0 | [free-north.html](results/qr-codes/free-north.html) | 1/4 |
| qr-codes | dots-3 | 25 min 45 s | 13 | 1 | none | 0/4 |
| **total** | **Flint v1.0** | **2 h 25 min** | **123** | | | **14/20** |
| **total** | **ERNIE 5.5 Flash** | **24 min 51 s** | **80** | | | **10/20** |
| **total** | **north-mini-code** | **7 min 32 s** | **54** | | | **7/20** |
| **total** | **dots-3** | **1 h 05 min** | **82** | | | **4/20** |

Models: `recursive/flint-v1.0:free`, `baidu/ernie-5.5-flash-preview:free`, `cohere/north-mini-code:free`,
`dots-studio/dots-3-note-preview:free`. Free endpoints may store or train on prompts: don't send keys, passwords or
private code to them.

## What's here

- `prompts/` the five prompts, verbatim, and their credits.
- `results/<prompt>/opus.html`, `fable.html`, `free-<model>.html` the pages each model wrote, unedited. Open them in Chrome. Opus's
  recursion page isn't included: one of its scenes looks like a famous game, so it's blurred in the video too.
- `out/runs.jsonl` every run, including retries and later runs of the same prompts on free OpenRouter models
  (`run` = `free-*`, see `run_free.sh` and the free-models section below).
- `run.sh <prompt> <run>` one run. `VP_MODEL=fable` for Fable; `VP_OPENROUTER=1 VP_MODEL=<id>:free` for a free model.
- `record.mjs`, `still.mjs`, `clock.mjs` record a page to MP4 / stills on a virtual clock, so a busy machine can't drop frames.
- `sidebyside.py` the side-by-side clips used in the video.

The screen recordings aren't in the repo (about 230 MB); everything in them can be re-made with `record.mjs`.
