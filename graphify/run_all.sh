#!/usr/bin/env bash
# Full run: 10 questions x 2 repos x 2 arms x 2 passes = 80 fresh sessions. The arm order flips on pass 2.
# Start it only while no other Claude session is using the limit. It stops by itself if a run fails.
set -eu
cd "$(dirname "$0")"; W=$PWD/work
one() { python3 -I run_arm.py "$W/$1" "$2" "prompts/$3.jsonl" </dev/null; }
for repo in httpx django; do
  one "$repo" off "$repo"; one "${repo}_on" on "$repo"
  one "${repo}_on" on "$repo"; one "$repo" off "$repo"
done
echo done
