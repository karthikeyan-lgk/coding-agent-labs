#!/usr/bin/env python3
"""Summarise out/sessions.jsonl: per long session and per arm. total_cost_usd is per session
on --resume if it rises at every position, so cost here is checked before it is summed."""
import json, statistics as st, collections
from pathlib import Path
keys = {}
for f in ("httpx", "django"):
    for l in Path(f"prompts/{f}.jsonl").read_text().splitlines():
        p = json.loads(l); keys[p["id"]] = p
R = [json.loads(l) for l in open("out/sessions.jsonl")]
tok = lambda r: sum(r["usage"].get(k, 0) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
S = collections.defaultdict(list)
for r in R: S[(r["repo"], r["arm"], r["run"])].append(r)
print("calls", len(R), "errors", sum(bool(r["is_error"] or r["raw_error"]) for r in R), "same session everywhere", all(r["same_session"] for r in R))
print("session                 calls  tokens  sum_cost last_cost secs turns keyfull ids")
agg = collections.defaultdict(list)
for k, rs in sorted(S.items()):
    rs.sort(key=lambda r: r["pos"]); t = sum(map(tok, rs)); c = sum(r["cost_usd"] for r in rs)
    full = sum(len(r["hit_key"]) == len(keys[r["id"]]["key"]) for r in rs)
    print(f"{k[0]:10}{k[1]:4}{k[2]:2}  {len(rs):6} {t:8} {c:8.3f} {rs[-1]['cost_usd']:8.3f} {sum(r['secs'] for r in rs):5.0f} {sum(r['turns'] for r in rs):4} {full:4}  {len({r['session'] for r in rs})}")
    agg[(k[0].replace('_on',''), k[1])].append((t, rs[-1]["cost_usd"], c, sum(r["secs"] for r in rs), [tok(r) for r in rs], [r["cost_usd"] for r in rs]))
for repo in ("httpx", "django"):
    o, n = agg[(repo, "off")], agg[(repo, "on")]
    a, b = st.mean(x[0] for x in o), st.mean(x[0] for x in n)
    print(repo, "tokens/session", round(a), round(b), f"{b/a-1:+.1%}", "secs", round(st.mean(x[3] for x in o)), round(st.mean(x[3] for x in n)), "spread off", [x[0] for x in o], "on", [x[0] for x in n])
    print("  per-position tokens off", [round(st.mean(x[4][i] for x in o)) for i in range(10)])
    print("  per-position tokens on ", [round(st.mean(x[4][i] for x in n)) for i in range(10)])
    print("  cost by pos off", [round(c, 3) for c in o[0][5]])
    print("  cost by pos on ", [round(c, 3) for c in n[0][5]])
