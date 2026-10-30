# Claude Code in a CI pipeline

Companion for "Claude Code in CI: Trace Every Headless Run with OpenTelemetry". Recorded on 2026-10-29 with
Claude Code 2.1.312 (subscription login, no API key, Haiku), otelcol-contrib 0.162.0 and Jaeger 2.22.0.

## What it shows

- A "release-prep" job runs `claude -p` three times (review, changelog, lint). Run on their own, the steps are
  three unrelated traces (`parent.source: none`).
- The job opens one span plus one span per step and hands each step `TRACEPARENT`. The whole run is then one
  trace, and every Claude Code run says `parent.source: env`. Only `claude -p` and the Agent SDK read
  inbound `TRACEPARENT`; interactive sessions ignore it.
- `OTEL_RESOURCE_ATTRIBUTES` adds `cicd.pipeline.name` and `cicd.pipeline.run.id` (OpenTelemetry CI/CD
  conventions, release candidate), so a run can be found by its id.
- Allow rules match how a command starts. With `Bash(git diff:*)`, the model's `git -C <repo> diff --cached`
  and chained `git diff … && …` were refused (`claude_code.tool.blocked_on_user` `decision: reject`,
  `source: config`), and every refusal cost another model call. The numbers are in `recorded_runs.txt`.

## Privacy

`collector.yaml` deletes `user.email`, `user.id`, `user.account_uuid`, `user.account_id` and `organization.id`,
and rewrites the laptop path in `full_command` / `file_path` to `/work/repo`, before anything reaches Jaeger.

## Run it

```sh
docker compose up -d
./make_repo.sh && uv run --no-project --with opentelemetry-sdk --with opentelemetry-exporter-otlp-proto-http \
    python -I pipeline.py split
./make_repo.sh && uv run ... python -I pipeline.py joined     # repeat for a few "nights"
python3 inspect_traces.py release-prep 30                      # spans, timing, tokens, refusals per run
cd ../../.. && uv run --no-project --with playwright==1.64.0 python -I \
    companions/coding_agent_telemetry/ci_pipeline/record_clips.py en/output <bad trace id> <its run id> <split trace id>
docker compose down
```

Jaeger keeps traces in memory, so the ids change after a restart. Runs vary night to night: which commands get
refused depends on how the model words them.
