#!/usr/bin/env bash
# Free-models long: the same 5 prompts on 4 OpenRouter :free models, one run at a time, cheapest prompt first.
# Records the OpenRouter key's usage before/after each run in out/free_usage.jsonl (should stay at $0).
set -uo pipefail
LAB=$(cd "$(dirname "$0")" && pwd)
KEY=$(grep '^OPENROUTER_API_KEY=' "$LAB/../../../.env" | cut -d= -f2-)
usage() { curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $KEY" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['usage'])"; }
for P in ${PROMPTS:-token-bucket business-explainer recursion ai-datacentre qr-codes}; do
  for M in ${MODELS:-dots-studio/dots-3-note-preview:free cohere/north-mini-code:free baidu/ernie-5.5-flash-preview:free recursive/flint-v1.0:free}; do
    tag=free-$(echo "${M%%:*}" | sed 's|.*/||')
    B=$(usage)
    VP_OPENROUTER=1 VP_MODEL=$M "$LAB/run.sh" "$P" "$tag" >/dev/null
    A=$(usage)
    echo "{\"prompt\":\"$P\",\"run\":\"$tag\",\"model\":\"$M\",\"usage_before\":$B,\"usage_after\":$A}" >> "$LAB/out/free_usage.jsonl"
    python3 -c "import sys; sys.exit(0 if float('$A')-float('$B') < 0.01 else 1)" || { echo "SPEND on $M $P, stopping" >&2; exit 3; }
  done
done
