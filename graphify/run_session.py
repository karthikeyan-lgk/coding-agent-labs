#!/usr/bin/env python3
"""All questions of a repo in ONE Claude Code session: the first starts it, the rest use --resume.
Usage: run_session.py <repo dir> <off|on> <prompts.jsonl> <pass> [--limit N] [--out FILE] [--model sonnet]
One line per question goes to out/sessions.jsonl. A pass that already finished is skipped; a pass
that failed part way is dropped by analyze_sessions.py and run again from question 1."""
import argparse, json, os, subprocess, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("repo"); ap.add_argument("arm", choices=["off", "on"]); ap.add_argument("prompts"); ap.add_argument("run", type=int)
ap.add_argument("--limit", type=int); ap.add_argument("--out", default="out/sessions.jsonl"); ap.add_argument("--model", default="sonnet")
a = ap.parse_args()
out = HERE/a.out; name = Path(a.repo).name
qs = [json.loads(l) for l in Path(a.prompts).read_text().splitlines()][:a.limit]
if out.exists():
    done = [json.loads(l) for l in out.read_text().splitlines()]
    if sum(r["repo"] == name and r["run"] == a.run and not r["is_error"] and not r["raw_error"] for r in done) >= len(qs):
        print("skip", name, a.arm, a.run); raise SystemExit(0)
env = dict(os.environ); env["PATH"] = f"{HERE/'work/venv/bin'}:{env['PATH']}"
tools = "Read,Grep,Glob" + (",Bash(graphify:*)" if a.arm == "on" else "")
sid = None
for i, p in enumerate(qs):
    t0 = time.time()
    cmd = ["claude", "-p", p["q"], "--model", a.model, "--output-format", "json", "--allowedTools", tools,
           "--disallowedTools", "Edit,Write,NotebookEdit,WebFetch,WebSearch,Task"] + (["--resume", sid] if sid else [])
    r = subprocess.run(cmd, cwd=a.repo, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=420)
    try: d = json.loads(r.stdout)
    except ValueError: d = {"parse_error": r.stdout[-400:] + r.stderr[-400:]}
    new = d.get("session_id"); same = sid is None or new == sid; sid = new or sid
    u = d.get("usage", {})
    rec = {"ts": t0, "repo": name, "arm": a.arm, "run": a.run, "pos": i+1, "id": p["id"], "session": sid, "same_session": same, "model": a.model,
           "secs": round(time.time()-t0, 1), "turns": d.get("num_turns"), "cost_usd": d.get("total_cost_usd"), "is_error": d.get("is_error"), "usage": u,
           "answer": d.get("result"), "hit_key": [k for k in p["key"] if k.lower() in (d.get("result") or "").lower()], "raw_error": d.get("parse_error")}
    with open(out, "a") as f: f.write(json.dumps(rec)+"\n")
    print(name, a.arm, "run", a.run, "q", i+1, p["id"], "same", same, "turns", rec["turns"], "secs", rec["secs"], "cost", rec["cost_usd"], "cr", u.get("cache_read_input_tokens"), "cw", u.get("cache_creation_input_tokens"), "key", len(rec["hit_key"]), "/", len(p["key"]), flush=True)
    if rec["is_error"] or rec["raw_error"]:
        print("STOP: a run failed (often the usage limit); fix it, then restart"); raise SystemExit(3)
