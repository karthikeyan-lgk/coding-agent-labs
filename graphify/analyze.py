#!/usr/bin/env python3
"""Summarise out/runs.jsonl: tokens, cost, time and key hits by repo, arm and question kind."""
import json, statistics as st, collections
from pathlib import Path
kinds = {}; keys = {}
for f in ("httpx", "django"):
    for l in Path(f"prompts/{f}.jsonl").read_text().splitlines():
        p = json.loads(l); kinds[p["id"]] = p["kind"]; keys[p["id"]] = len(p["key"])
R = [json.loads(l) for l in open("out/runs.jsonl")]
def tok(r):
    u = r["usage"]; return sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
print("runs", len(R), "errors", sum(1 for r in R if r["is_error"] or r["raw_error"]), "total cost", round(sum(r["cost_usd"] or 0 for r in R), 2), "hours", round((R[-1]["ts"]-R[0]["ts"])/3600, 2))
def line(name, rs):
    if not rs: return
    print(f"{name:26} n={len(rs):3} tok_mean={st.mean(map(tok, rs)):9.0f} tok_med={st.median(map(tok, rs)):9.0f} cost={sum(r['cost_usd'] for r in rs):6.2f} secs_med={st.median(r['secs'] for r in rs):6.1f} turns_med={st.median(r['turns'] for r in rs):4.1f} keyfull={sum(len(r['hit_key'])==keys[r['id']] for r in rs)}")
for repo, on in (("httpx", "httpx_on"), ("django", "django_on")):
    for arm, name in (("off", repo), ("on", on)):
        line(f"{repo} {arm}", [r for r in R if r["repo"] == name and r["arm"] == arm])
    for k in ("find", "structure", "explain", "impact"):
        for arm, name in (("off", repo), ("on", on)):
            line(f"  {k} {arm}", [r for r in R if r["repo"] == name and r["arm"] == arm and kinds[r["id"]] == k])
print("per question: mean tokens off, on, on/off, key hits off/on")
wins = 0; ids = list(kinds)
for i in ids:
    o = [r for r in R if r["id"] == i and r["arm"] == "off"]; n = [r for r in R if r["id"] == i and r["arm"] == "on"]
    a, b = st.mean(map(tok, o)), st.mean(map(tok, n)); wins += b < a
    print(f"{i:4} {kinds[i]:9} {a:9.0f} {b:9.0f} {b/a:5.2f}  {[len(r['hit_key']) for r in o]} {[len(r['hit_key']) for r in n]} /{keys[i]}  spread off {min(map(tok,o))}-{max(map(tok,o))} on {min(map(tok,n))}-{max(map(tok,n))}")
print("questions where Graphify used fewer tokens:", wins, "of", len(ids))
