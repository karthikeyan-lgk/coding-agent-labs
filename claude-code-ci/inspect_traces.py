"""Print every trace for a service from Jaeger's v3 API: spans, timing and the attributes the video reads.

    python3 inspect_traces.py <service> [minutes back]
"""

import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone

service, minutes = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30
now = datetime.now(timezone.utc)
q = urllib.parse.urlencode({
    "query.service_name": service,
    "query.start_time_min": (now - timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z"),
    "query.start_time_max": now.isoformat().replace("+00:00", "Z"),
})
data = json.load(urllib.request.urlopen(f"http://127.0.0.1:16686/api/v3/traces?{q}"))
KEEP = ("parent.source", "cicd.pipeline.task.name", "tool_name", "full_command", "decision", "source", "input_tokens",
        "output_tokens", "cache_read_tokens", "cache_creation_tokens", "success", "model")
traces = defaultdict(list)
for rs in data["result"]["resourceSpans"]:
    res = {a["key"]: next(iter(a["value"].values())) for a in rs["resource"].get("attributes", [])}
    for ss in rs["scopeSpans"]:
        for s in ss["spans"]:
            s["_attrs"] = {a["key"]: next(iter(a["value"].values()), None) for a in s.get("attributes", [])}
            s["_svc"] = res.get("service.name")
            traces[s["traceId"]].append(s)
for tid, spans in sorted(traces.items(), key=lambda kv: min(int(s["startTimeUnixNano"]) for s in kv[1])):
    spans.sort(key=lambda s: int(s["startTimeUnixNano"]))
    t0 = int(spans[0]["startTimeUnixNano"])
    end = max(int(s["endTimeUnixNano"]) for s in spans)
    print(f"TRACE {tid} · {len(spans)} spans · {(end - t0) / 1e9:.1f} s")
    for s in spans:
        dur = (int(s["endTimeUnixNano"]) - int(s["startTimeUnixNano"])) / 1e6
        keep = {k: s["_attrs"][k] for k in KEEP if k in s["_attrs"]}
        print(f"  +{(int(s['startTimeUnixNano']) - t0) / 1e9:5.1f}s {s['name']:<34} {dur:8.0f} ms  {keep}")
