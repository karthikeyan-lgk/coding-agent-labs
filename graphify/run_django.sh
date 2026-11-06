#!/usr/bin/env bash
# Django half of run_all.sh, run on its own after the 11-05 run hit the 5-hour limit: 40 fresh sessions.
set -eu
cd "$(dirname "$0")"; W=$PWD/work
one() { python3 -I run_arm.py "$W/$1" "$2" "prompts/$3.jsonl" </dev/null; }
one django off django; one django_on on django
one django_on on django; one django off django
echo done
