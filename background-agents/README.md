# What Claude Code spends while you're not typing

Companion for the "Claude Code Read 52,000 Tokens to Write 4 Words" Short and the long video on Claude Code's hidden
requests. Recorded on 2026-11-01 with Claude Code 2.1.316 (Claude Pro subscription login, no API key),
otelcol-contrib 0.162.0, Prometheus 3.15.0, Loki 3.6.18 and Grafana 13.2.4.

## What it shows

Every model request Claude Code makes is an `api_request` event with a `query_source`. Besides your own conversation
(`repl_main_thread`) and your agents, an interactive session makes requests you never asked for:

- `agent_summary`: the 3-5 word status label next to each running background agent. Each one sends the agent's whole
  transcript back to the model: 52k-71k tokens read for 12-109 written. In a 5-minute session with two background
  agents, across four sessions, the labels were 13-21% of all tokens and 10-14% of the cost. There is no setting to
  turn it off in 2.1.316.
- `prompt_suggestion`: the greyed-out "next prompt" suggestion after each reply. In 4 short turns it was 34% of the
  tokens; `"promptSuggestionEnabled": false` in settings removed every one of them (twice: -34% and -37% tokens).
- `generate_session_title`: one small Haiku request per session.

Every number is in `recorded_runs.txt`. Costs are Claude Code's own `cost_usd` estimate at API prices.

## Why Loki

Claude Code's metrics carry `query_source` too, but only as `main`, `subagent` or `auxiliary`. The detail
(`agent_summary`, `prompt_suggestion`, ...) lives in the `api_request` events, so the Collector sends events to Loki
and the Grafana panels sum `cost_usd` and tokens from them, split by `query_source`.

## Privacy

`collector.yaml` deletes `user.email`, `user.id`, `user.account_uuid`, `user.account_id`, `session.id` and
`organization.id` before anything is stored.

## Run it

```sh
mkdir -p out && chmod 777 out              # the Collector container writes out/telemetry.json
docker compose up -d                       # Collector :14317/:14318, Prometheus :19090, Loki :13100, Grafana :13000
python3 make_repo.py /tmp/tinyledger       # the demo repo (generated code)
python3 interactive.py /tmp/tinyledger sonnet          # one interactive session with two background agents (tmux)
python3 suggest.py /tmp/tinyledger haiku               # prompt suggestions on vs off, 4 turns each
python3 run.py /tmp/tinyledger 2 sonnet                # headless claude -p with CLAUDE_CODE_AGENT_PROGRESS_SUMMARIES on/off
python3 analyze.py                         # requests, tokens and cost per arm and query_source
open http://127.0.0.1:13000                # dashboard "Claude Code: requests you didn't type"
docker compose down
```

The sessions use your own plan's limit: the two interactive runs above took about 8% of a Pro 5-hour window on Sonnet.
In our headless runs no `agent_summary` requests appeared with the flag on or off (the agents finished in under a
minute), so the interactive run is the one that shows them.
