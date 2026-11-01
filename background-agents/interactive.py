#!/usr/bin/env python3
"""Run one interactive Claude Code session with two background agents, in tmux, with telemetry on.

Usage: python3 interactive.py <tinyledger repo> [model] [arm] [prompt file] [run]

Interactive sessions summarize each running background agent by default, so this is the setting the
viral report measured. The session is tagged lab.arm=<arm> (default "interactive"); analyze.py splits
its api_request events by query_source. The run ends when the pane has been still for QUIET seconds
after the agents started, or after LIMIT seconds, then /exit.
"""
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent
SESSION = "bg-agents-lab"
QUIET, LIMIT = 90, 900


def tmux(*args: str) -> str:
    return subprocess.run(["tmux", *args], capture_output=True, text=True).stdout


def pane() -> str:
    return tmux("capture-pane", "-p", "-t", SESSION)


def main() -> None:
    repo, model = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "sonnet"
    arm = sys.argv[3] if len(sys.argv) > 3 else "interactive"
    prompt = Path(sys.argv[4]) if len(sys.argv) > 4 else LAB / "prompts" / "interactive.txt"
    run = sys.argv[5] if len(sys.argv) > 5 else "1"
    env = ("CLAUDE_CODE_ENABLE_TELEMETRY=1 OTEL_METRICS_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp "
           "OTEL_EXPORTER_OTLP_PROTOCOL=grpc OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:14317 "
           "OTEL_METRIC_EXPORT_INTERVAL=5000 OTEL_LOGS_EXPORT_INTERVAL=2000 "
           f"OTEL_RESOURCE_ATTRIBUTES=lab=background_agents,lab.arm={arm},lab.run={run}")
    cmd = (f"cd {repo} && env {env} claude --model {model} --strict-mcp-config "
           f"--allowedTools Read,Grep,Glob,Agent,Task")
    tmux("kill-session", "-t", SESSION)
    tmux("new-session", "-d", "-s", SESSION, "-x", "160", "-y", "48", cmd)
    time.sleep(6)
    if "trust this folder" in pane().lower():  # our own generated repo; the default option is "No, exit"
        tmux("send-keys", "-t", SESSION, "Down"); time.sleep(0.5)
        tmux("send-keys", "-t", SESSION, "Enter"); time.sleep(6)
    tmux("send-keys", "-t", SESSION, "-l", prompt.read_text().strip())
    time.sleep(1.5)
    tmux("send-keys", "-t", SESSION, "Enter")
    time.sleep(3)
    if "background agent" not in pane() and "Agent" not in pane():  # the first Enter can land before the box is ready
        tmux("send-keys", "-t", SESSION, "Enter")
    t0, last, still = time.time(), "", time.time()
    while time.time() - t0 < LIMIT:
        time.sleep(10)
        now = pane()
        if now != last:
            last, still = now, time.time()
        elif time.time() - t0 > 180 and time.time() - still >= QUIET:
            break
    (LAB / "out" / f"{arm}-pane.txt").write_text(last)
    print(f"{arm}: {time.time() - t0:.0f} s")
    tmux("send-keys", "-t", SESSION, "/exit", "Enter")
    time.sleep(15)
    tmux("kill-session", "-t", SESSION)


if __name__ == "__main__":
    main()
