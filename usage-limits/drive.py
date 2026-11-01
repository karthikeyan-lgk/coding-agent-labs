#!/usr/bin/env python3
"""Drive one interactive Claude Code session in tmux and label everything it exports.

Usage:
  python3 drive.py --arm long --model sonnet --repo <tinyledger> --prompts prompts/long.txt [--mcp]

Interactive mode on purpose: only interactive sessions run the status line, and the status line is
the only place Claude Code reports the 5-hour / weekly limit (see limit_meter.py). Each line of the
prompts file is typed as one turn; lines starting with "/" are slash commands (/compact, /clear).
A turn is done when the status line has fired and the pane has stopped changing for QUIET seconds.

Telemetry: OTEL_RESOURCE_ATTRIBUTES carries lab.arm, so every token metric and api_request event
from this session can be split by arm. Without --mcp the session starts with --strict-mcp-config
and no servers, so the baseline doesn't depend on whatever MCP servers this machine has.
"""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent
METER_LOG = LAB / "out" / "limit_meter.jsonl"
SESSION = "usage-lab"
QUIET = 8
TURN_TIMEOUT = 420


def tmux(*args: str) -> str:
    return subprocess.run(["tmux", *args], capture_output=True, text=True).stdout


def pane() -> str:
    return tmux("capture-pane", "-p", "-t", SESSION)


def meter_lines() -> int:
    return sum(1 for _ in METER_LOG.open()) if METER_LOG.exists() else 0


def wait_done(before: int, need_meter: bool = True) -> bool:
    """Wait for a new status-line reading, then for the pane to go still."""
    start = time.time()
    last, still_since = None, time.time()
    while time.time() - start < TURN_TIMEOUT:
        time.sleep(1)
        now = pane()
        if now != last:
            last, still_since = now, time.time()
        fired = meter_lines() > before or not need_meter
        if fired and time.time() - still_since >= QUIET:
            return True
    return False


def send(text: str) -> None:
    tmux("send-keys", "-t", SESSION, "-l", text)
    time.sleep(0.5)
    tmux("send-keys", "-t", SESSION, "Enter")


def last_reading() -> dict:
    if not METER_LOG.exists():
        return {}
    lines = METER_LOG.read_text().splitlines()
    return json.loads(lines[-1]) if lines else {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--mcp", action="store_true", help="keep this machine's MCP servers (default: none)")
    a = ap.parse_args()

    env_file = (LAB / "env.sh").read_text()
    exports = [l.removeprefix("export ").strip() for l in env_file.splitlines() if l.startswith("export ")]
    env = " ".join(exports).replace("OTEL_RESOURCE_ATTRIBUTES=\"lab=usage_limits\"",
                                    f"OTEL_RESOURCE_ATTRIBUTES=lab=usage_limits,lab.arm={a.arm}")
    flags = "" if a.mcp else "--strict-mcp-config"
    cmd = f"cd {a.repo} && env {env} LAB_ARM={a.arm} claude --model {a.model} {flags}"

    tmux("kill-session", "-t", SESSION)
    tmux("new-session", "-d", "-s", SESSION, "-x", "160", "-y", "48", cmd)
    time.sleep(6)
    if "trust this folder" in pane().lower():  # our own generated repo; the default option is "No, exit"
        tmux("send-keys", "-t", SESSION, "Down")
        time.sleep(0.5)
        tmux("send-keys", "-t", SESSION, "Enter")
        time.sleep(6)

    log = LAB / "out" / "turns.jsonl"
    prompts = [l for l in Path(a.prompts).read_text().splitlines() if l.strip() and not l.startswith("#")]
    for i, p in enumerate(prompts, 1):
        before = meter_lines()
        t0 = time.time()
        send(p)
        ok = wait_done(before, need_meter=not p.startswith("/clear"))
        r = last_reading()
        rec = {"arm": a.arm, "model": a.model, "turn": i, "prompt": p, "ok": ok, "t0": t0, "t1": time.time(),
               "five_hour_pct": r.get("five_hour_pct"), "context_pct": r.get("context_pct"),
               "last_request_input": r.get("last_request_input")}
        with log.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[{a.arm}] turn {i:>2} ok={ok} 5h={rec['five_hour_pct']} ctx={rec['context_pct']} "
              f"in={rec['last_request_input']} :: {p[:60]}", flush=True)
        if not ok:
            break
    send("/exit")
    time.sleep(5)
    tmux("kill-session", "-t", SESSION)


if __name__ == "__main__":
    main()
