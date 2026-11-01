#!/usr/bin/env python3
"""Run the same subagent task headless, with Claude Code's agent progress summaries on and off.

Usage: python3 run.py <tinyledger repo> [runs per arm] [model]

Interactive sessions summarize every running background agent by default (query_source agent_summary).
Headless `claude -p` only does it with CLAUDE_CODE_AGENT_PROGRESS_SUMMARIES=1, which makes a clean
on/off comparison: same prompt, same repo, same model, one environment variable. Each run is tagged
with lab.arm and lab.run in OTEL_RESOURCE_ATTRIBUTES; analyze.py splits the api_request events by them.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent
PROMPT = (LAB / "prompts" / "task.txt").read_text().strip()


def run(repo: Path, arm: str, n: int, model: str) -> None:
    env = dict(os.environ)
    env.update({
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_METRICS_EXPORTER": "otlp", "OTEL_LOGS_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc", "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:14317",
        "OTEL_METRIC_EXPORT_INTERVAL": "5000", "OTEL_LOGS_EXPORT_INTERVAL": "2000",
        "OTEL_RESOURCE_ATTRIBUTES": f"lab=background_agents,lab.arm={arm},lab.run={n}",
    })
    env.pop("CLAUDE_CODE_AGENT_PROGRESS_SUMMARIES", None)
    if arm == "summaries-on":
        env["CLAUDE_CODE_AGENT_PROGRESS_SUMMARIES"] = "1"
    started = time.time()
    out = subprocess.run(
        ["claude", "-p", "--model", model, "--allowedTools", "Read,Grep,Glob,Agent,Task"],
        input=PROMPT, cwd=repo, env=env, capture_output=True, text=True, timeout=1800,
    )
    print(f"{arm} run {n}: exit {out.returncode}, {time.time() - started:.0f} s")
    (LAB / "out" / f"{arm}-{n}.txt").write_text(out.stdout + "\n--- stderr ---\n" + out.stderr)
    time.sleep(10)  # let the last log batch export


def main() -> None:
    repo = Path(sys.argv[1]).resolve()
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    model = sys.argv[3] if len(sys.argv) > 3 else "sonnet"
    for n in range(1, runs + 1):
        for arm in ("summaries-off", "summaries-on"):
            run(repo, arm, n, model)


if __name__ == "__main__":
    main()
