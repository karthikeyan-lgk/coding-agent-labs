# What burns your Claude limit

Companion for "Claude Code Usage Limits Explained". Recorded on 2026-10-30 with Claude Code 2.1.314 (Claude Pro
subscription login, no API key), otelcol-contrib 0.162.0, Prometheus 3.15.0 and Grafana 13.2.4.

## What it shows

- The same one-word prompt ("Reply with just the word ok.") carries about 42,500 tokens on Sonnet: 2 of them are
  the prompt, the rest is Claude Code's own setup (instructions, tools, CLAUDE.md, skills, plugins).
- Same task on Haiku, Sonnet and Opus: about 43k tokens each, but Opus costs about 2× Sonnet and about 40× Haiku
  at API prices.
- A 30-turn session grows the one-word request to about 68,800 tokens (1.6×). `/compact` brings it to about
  51,900; `/clear` takes it back to a fresh session (about 42,700, cache write included).
- Two MCP servers add about 2,000 tokens per request (+5%) on this setup.

Every number is in `recorded_runs.txt`. Costs are Claude Code's own estimate at API prices; Anthropic doesn't
publish how tokens map onto the 5-hour and weekly limits.

## The limit meter

The 5-hour and weekly percentages never leave Claude Code as telemetry. `limit_meter.py` is a status-line script
that prints them and sends them to the Collector as gauges after every reply, so Grafana can plot the limit next
to the token metrics. Wire it up in `.claude/settings.json`:

```json
{"statusLine": {"type": "command", "command": "python3 /path/to/limit_meter.py"}}
```

## Privacy

`collector.yaml` deletes `user.email`, `user.id`, `user.account_uuid`, `user.account_id`, `session.id` and
`organization.id` before anything reaches Prometheus.

## Run it

```sh
docker compose up -d                       # Collector :14317/:14318, Prometheus :19090, Grafana :13000
python3 make_repo.py /tmp/tinyledger       # the demo repo (generated code, status line pre-wired)
source env.sh                              # turn on Claude Code telemetry, pointed at the lab Collector
./run_all.sh /tmp/tinyledger               # every arm in order; stops if the 5-hour limit passes GUARD (60%)
open http://127.0.0.1:13000                # dashboard "Claude Code usage limits"
docker compose down
```

`run_all.sh` drives interactive sessions in tmux (`drive.py`), because only interactive sessions run the status
line. It uses your own plan's limit, so watch the meter. `record_clips.py` is how the video's Grafana clips were
recorded and needs the main video repo; you can skip it.
