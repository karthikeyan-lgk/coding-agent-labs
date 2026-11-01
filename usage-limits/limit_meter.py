#!/usr/bin/env python3
"""Claude Code status line that also exports your usage-limit meter.

Claude Code pipes session JSON to the status line on every new assistant message. Pro/Max
subscribers get `rate_limits.five_hour` / `rate_limits.seven_day` in it: the same percentage
/usage shows. This script prints a one-line status, appends the reading to
out/limit_meter.jsonl, and sends it as OTLP gauges to the lab Collector so Grafana can plot the
limit next to Claude Code's own token metrics.

Wire it up in .claude/settings.json:
  {"statusLine": {"type": "command", "command": "python3 /path/to/limit_meter.py"}}

Stdlib only. Never fails the status line: export errors are swallowed.
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ENDPOINT = os.environ.get("LIMIT_METER_OTLP", "http://127.0.0.1:14318/v1/metrics")
LOG = Path(os.environ.get("LIMIT_METER_LOG", Path(__file__).parent / "out" / "limit_meter.jsonl"))
ARM = os.environ.get("LAB_ARM", "manual")


def reading(data: dict) -> dict:
    limits = data.get("rate_limits") or {}
    ctx = data.get("context_window") or {}
    usage = ctx.get("current_usage") or {}
    return {
        "ts": time.time(),
        "arm": ARM,
        "model": (data.get("model") or {}).get("id"),
        "five_hour_pct": (limits.get("five_hour") or {}).get("used_percentage"),
        "five_hour_resets_at": (limits.get("five_hour") or {}).get("resets_at"),
        "seven_day_pct": (limits.get("seven_day") or {}).get("used_percentage"),
        "context_pct": ctx.get("used_percentage"),
        "last_request_input": sum(usage.get(k) or 0 for k in
                                  ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "session_cost_usd": (data.get("cost") or {}).get("total_cost_usd"),
    }


def export(r: dict) -> None:
    now = str(time.time_ns())
    attrs = [{"key": "lab.arm", "value": {"stringValue": r["arm"]}},
             {"key": "model", "value": {"stringValue": r["model"] or "unknown"}}]
    gauges = [("claude_limit_five_hour_used_percent", r["five_hour_pct"]),
              ("claude_limit_seven_day_used_percent", r["seven_day_pct"]),
              ("claude_context_used_percent", r["context_pct"]),
              ("claude_last_request_input_tokens", r["last_request_input"])]
    metrics = [{"name": name, "gauge": {"dataPoints": [{"asDouble": float(v), "timeUnixNano": now, "attributes": attrs}]}}
               for name, v in gauges if v is not None]
    if not metrics:
        return
    body = {"resourceMetrics": [{
        "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "claude-limit-meter"}},
                                    {"key": "lab", "value": {"stringValue": "usage_limits"}}]},
        "scopeMetrics": [{"scope": {"name": "limit_meter"}, "metrics": metrics}]}]}
    req = urllib.request.Request(ENDPOINT, json.dumps(body).encode(), {"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=1).read()


def main() -> None:
    data = json.load(sys.stdin)
    r = reading(data)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as f:
            f.write(json.dumps(r) + "\n")
        export(r)
    except Exception:
        pass
    five = "-" if r["five_hour_pct"] is None else f"{r['five_hour_pct']:.1f}%"
    week = "-" if r["seven_day_pct"] is None else f"{r['seven_day_pct']:.1f}%"
    ctx = "-" if r["context_pct"] is None else f"{r['context_pct']:.0f}%"
    print(f"5h limit {five} · week {week} · context {ctx} · {r['arm']}")


if __name__ == "__main__":
    main()
