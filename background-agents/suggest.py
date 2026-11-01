#!/usr/bin/env python3
"""Does "promptSuggestionEnabled": false stop the prompt_suggestion requests? Four short turns per arm.

Usage: python3 suggest.py <tinyledger repo> [model]

Arm suggest-on uses default settings; arm suggest-off passes --settings '{"promptSuggestionEnabled": false}'.
analyze.py then shows whether any prompt_suggestion requests appear in each arm.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

SESSION = "suggest-lab"
TURNS = ["What does tinyledger/invoices.py do? One sentence.", "Which function in tinyledger/payments.py is longest? One line.",
         "Name one missing test for tinyledger/refunds.py. One line.", "Reply with just the word ok."]


def tmux(*args: str) -> str:
    return subprocess.run(["tmux", *args], capture_output=True, text=True).stdout


def session(repo: str, model: str, arm: str, settings: dict | None) -> None:
    env = ("CLAUDE_CODE_ENABLE_TELEMETRY=1 OTEL_METRICS_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp "
           "OTEL_EXPORTER_OTLP_PROTOCOL=grpc OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:14317 "
           "OTEL_LOGS_EXPORT_INTERVAL=2000 "
           f"OTEL_RESOURCE_ATTRIBUTES=lab=background_agents,lab.arm={arm},lab.run=2")
    extra = f" --settings '{json.dumps(settings)}'" if settings else ""
    tmux("kill-session", "-t", SESSION)
    tmux("new-session", "-d", "-s", SESSION, "-x", "160", "-y", "48",
         f"cd {repo} && env {env} claude --model {model} --strict-mcp-config{extra}")
    time.sleep(8)
    for turn in TURNS:
        tmux("send-keys", "-t", SESSION, "-l", turn); time.sleep(1.5)
        tmux("send-keys", "-t", SESSION, "Enter"); time.sleep(30)
    tmux("send-keys", "-t", SESSION, "/exit", "Enter"); time.sleep(12)
    tmux("kill-session", "-t", SESSION)
    print(f"{arm}: done")


if __name__ == "__main__":
    repo, model = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "haiku"
    session(repo, model, "suggest-on", None)
    session(repo, model, "suggest-off", {"promptSuggestionEnabled": False})
