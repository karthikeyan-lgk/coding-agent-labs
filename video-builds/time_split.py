#!/usr/bin/env python3
"""Where did a build's wall time go? Reads Claude Code's own timestamped transcript for a run.

usage: time_split.py <run folder name, e.g. hyperframes-opus-b2-1> [...]
Model time = from the last tool result (or the prompt) to the next assistant message.
Tool time = from a tool_use to its tool_result, bucketed by what the Bash command did.
"""
import glob, json, os, re, sys
from datetime import datetime

BUCKETS = [  # first match wins
    ("install", r"\bnpm (i|install|ci)\b|create-video|npx -y create|pip install|cargo (add|fetch)"),
    ("render", r"\brender\b|remotion render|hyperframes(@[\d.]+)? render|cargo run.*render"),
    ("lint/check", r"hyperframes(@[\d.]+)? (check|lint|validate)|tsc\b|eslint|npx remotion (compositions|still)"),
    ("look at frames", r"ffmpeg|ffprobe|\.png"),
]

def ts(m): return datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00"))

def split(run):
    runs = os.environ.get("VB_RUNS", os.path.expanduser("~/.cache/video-builds-runs"))
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.path.join(runs, run))  # Claude Code's project folder name
    files = sorted(glob.glob(os.path.expanduser(f"~/.claude/projects/{slug}/*.jsonl")), key=os.path.getmtime)
    if not files: return None
    msgs = []
    for f in files:
        for line in open(f):
            try: m = json.loads(line)
            except ValueError: continue
            if "timestamp" in m and m.get("type") in ("user", "assistant", "queue-operation", "system"): msgs.append(m)
    msgs.sort(key=ts)
    # run_edit.sh resumes the same session, so the edit lands in the same transcript: stop at the second typed prompt.
    prompts = [i for i, m in enumerate(msgs) if m["type"] == "user" and not m.get("isMeta") and not any(
        isinstance(c, dict) and c.get("type") == "tool_result" for c in (m.get("message") or {}).get("content") or [])]
    if len(prompts) > 1: msgs = msgs[:prompts[1]]
    out = {"network stall": 0.0, "model": 0.0, "install": 0.0, "render": 0.0, "lint/check": 0.0, "look at frames": 0.0, "other tools": 0.0}
    pending = {}     # tool_use_id -> (start, bucket)
    last_done = ts(msgs[0])
    for m in msgs:
        t = ts(m)
        content = (m.get("message") or {}).get("content")
        if m["type"] == "system":
            if m.get("subtype") == "api_error":   # the wait ended in a dropped connection: not model time
                out["network stall"] += max(0.0, (t - last_done).total_seconds()); last_done = t
            continue
        if m["type"] == "assistant":
            if not pending: out["model"] += max(0.0, (t - last_done).total_seconds())
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_use":
                    cmd = c.get("input", {}).get("command") or json.dumps(c.get("input", {}))
                    b = next((name for name, rx in BUCKETS if c["name"] == "Bash" and re.search(rx, cmd)), "other tools")
                    pending[c["id"]] = (t, b)
            last_done = t
        elif m["type"] == "user" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in pending:
                    start, b = pending.pop(c["tool_use_id"])
                    out[b] += (t - start).total_seconds()
                    last_done = t
    return {k: round(v) for k, v in out.items()}

if __name__ == "__main__":
    for run in sys.argv[1:]:
        r = split(run)
        print(run, json.dumps(r) if r else "no transcript")
