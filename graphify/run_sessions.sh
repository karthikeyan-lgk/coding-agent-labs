#!/usr/bin/env bash
# Long-session test: 10 questions in one session x 2 repos x 2 arms x 2 passes = 8 sessions, 80 calls.
# Arm order flips on pass 2. Finished passes are skipped, so it can be restarted after a limit stop.
set -eu
cd "$(dirname "$0")"; W=$PWD/work
one() { python3 -I run_session.py "$W/$1" "$2" "prompts/$3.jsonl" "$4" </dev/null; }
for repo in httpx django; do
  one "$repo" off "$repo" 1; one "${repo}_on" on "$repo" 1
  one "${repo}_on" on "$repo" 2; one "$repo" off "$repo" 2
done
echo done
