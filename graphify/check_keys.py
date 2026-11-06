#!/usr/bin/env python3
"""Confirm every answer key is really in the pinned code. Usage: check_keys.py <repo> <prompts.jsonl>"""
import json, sys
from pathlib import Path
repo = Path(sys.argv[1]); bad = 0
for line in Path(sys.argv[2]).read_text().splitlines():
    p = json.loads(line)
    for f, s in p["check"]:
        ok = s in (repo/f).read_text(errors="ignore")
        if not ok: bad += 1; print("MISSING", p["id"], f, s)
print("checked", repo.name, "bad", bad)
