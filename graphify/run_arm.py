#!/usr/bin/env python3
"""One fresh headless Claude Code session per question, read-only tools, usage saved as JSON.
Usage: run_arm.py <repo dir> <arm: off|on> <prompts.jsonl> [--only ID] [--repeat N] [--model sonnet]
Results append to out/runs.jsonl. Tokens come from Claude Code's own result, not an estimate."""
import argparse, json, os, subprocess, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("repo"); ap.add_argument("arm", choices=["off", "on"]); ap.add_argument("prompts")
ap.add_argument("--only"); ap.add_argument("--repeat", type=int, default=1); ap.add_argument("--model", default="sonnet")
a = ap.parse_args()
env = dict(os.environ); env["PATH"] = f"{HERE/'work/venv/bin'}:{env['PATH']}"
tools = "Read,Grep,Glob" + (",Bash(graphify:*)" if a.arm == "on" else "")
for line in Path(a.prompts).read_text().splitlines():
    p = json.loads(line)
    if a.only and p["id"] != a.only: continue
    for n in range(a.repeat):
        t0 = time.time()
        r = subprocess.run(["claude", "-p", p["q"], "--model", a.model, "--output-format", "json", "--allowedTools", tools,
                            "--disallowedTools", "Edit,Write,NotebookEdit,WebFetch,WebSearch,Task"],
                           cwd=a.repo, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=420)
        try: d = json.loads(r.stdout)
        except ValueError: d = {"parse_error": r.stdout[-400:], "stderr": r.stderr[-400:]}
        u = d.get("usage", {})
        rec = {"ts": t0, "repo": Path(a.repo).name, "arm": a.arm, "id": p["id"], "n": n, "model": a.model, "secs": round(time.time()-t0, 1),
               "turns": d.get("num_turns"), "cost_usd": d.get("total_cost_usd"), "is_error": d.get("is_error"), "usage": u,
               "model_usage": d.get("modelUsage"), "answer": d.get("result"), "hit_key": [k for k in p["key"] if k.lower() in (d.get("result") or "").lower()],
               "raw_error": d.get("parse_error")}
        with open(HERE/"out/runs.jsonl", "a") as f: f.write(json.dumps(rec)+"\n")
        print(rec["repo"], rec["arm"], rec["id"], "turns", rec["turns"], "secs", rec["secs"], "cost", rec["cost_usd"], "in", u.get("input_tokens"), "cr", u.get("cache_read_input_tokens"), "cw", u.get("cache_creation_input_tokens"), "out", u.get("output_tokens"), "key", len(rec["hit_key"]), "/", len(p["key"]))
        if rec["is_error"] or rec["raw_error"]:
            print("STOP: a run failed (often the usage limit); fix it, then restart"); raise SystemExit(3)
