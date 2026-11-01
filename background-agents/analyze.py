#!/usr/bin/env python3
"""Split Claude Code's api_request events by arm and query_source: requests, tokens and cost.

Usage: python3 analyze.py [out/telemetry.json]

Tokens are everything the request read (input + cache read + cache creation). Cost is Claude Code's own
estimate at API prices (cost_usd on the event).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "out" / "telemetry.json")


def attrs(items):
    out = {}
    for a in items or []:
        v = a.get("value", {})
        out[a["key"]] = next(iter(v.values()), None) if v else None
    return out


rows = defaultdict(lambda: [0, 0, 0.0])
runs = defaultdict(set)
for line in path.read_text().splitlines():
    data = json.loads(line)
    for rl in data.get("resourceLogs", []):
        res = attrs(rl.get("resource", {}).get("attributes"))
        arm = res.get("lab.arm")
        if not arm:
            continue
        for sl in rl.get("scopeLogs", []):
            for rec in sl.get("logRecords", []):
                a = attrs(rec.get("attributes"))
                if a.get("event.name") not in ("api_request", "claude_code.api_request"):
                    continue
                tokens = sum(int(a.get(k) or 0) for k in ("input_tokens", "cache_read_tokens", "cache_creation_tokens"))
                key = (arm, a.get("query_source") or "?", a.get("model") or "?")
                rows[key][0] += 1
                rows[key][1] += tokens
                rows[key][2] += float(a.get("cost_usd") or 0)
                runs[arm].add(res.get("lab.run"))

for arm in sorted({k[0] for k in rows}):
    total_t = sum(v[1] for k, v in rows.items() if k[0] == arm)
    total_c = sum(v[2] for k, v in rows.items() if k[0] == arm)
    print(f"== {arm} ({len(runs[arm])} runs): {total_t:,} tokens, ${total_c:.4f}")
    for (a, src, model), (n, t, c) in sorted(rows.items(), key=lambda kv: -kv[1][2]):
        if a == arm:
            print(f"   {src:<28} {model:<26} {n:>4} req  {t:>10,} tok ({t / total_t:5.1%})  ${c:.4f} ({c / total_c:5.1%})")
