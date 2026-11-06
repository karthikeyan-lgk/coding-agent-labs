# Graphify lab

Does Graphify save Claude Code tokens against normal use, not against reading every file?
Every number from the video is in `recorded_runs.txt`.

## Set it up

You need Claude Code signed in, Python 3.12 and git. Nothing is installed in `~/.claude`.

```bash
mkdir work && cd work
python3 -m venv venv && venv/bin/pip install graphifyy==0.9.102
git clone https://github.com/encode/httpx && git -C httpx checkout b5addb64f016
git clone https://github.com/django/django && git -C django checkout ca3f31b255de
cp -r httpx httpx_on && cp -r django django_on
export PATH="$PWD/venv/bin:$PATH"
(cd httpx_on && graphify update . && graphify install --project --platform claude)
(cd django_on && graphify update . && graphify install --project --platform claude)
cd .. && mkdir -p out
```

## Run it

- `check_keys.py <repo> <prompts>` confirms each answer key is in the pinned code.
- `run_all.sh`: 80 fresh sessions, one question each. `analyze.py` summarises them.
- `run_sessions.sh`: 8 sessions of 10 questions each. `analyze_sessions.py` summarises them.
- `run_django.sh`: the Django half of `run_all.sh`, for a restart after a usage-limit stop.

Run these while no other Claude session is using your limit. Tools are read-only.
Change `prompts/` to your own questions and repo: that's the test that matters for you.
