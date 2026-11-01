"""Grafana clips for "Claude Code Is Spending Tokens While You're Not Typing".

    uv run --no-project --with playwright==1.64.0 python -I \
        companions/coding_agent_telemetry/background_agents/record_clips.py en/output [clip names]

Run while Loki still holds the 2026-11-01 re-runs (lab.run=2). Needs the main video repo's browser recorder.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "otel_course_recording"))
from browser import Page, record  # noqa: E402

GRAFANA = "http://127.0.0.1:13000/d/claude-hidden-requests"
# Each arm's events on 2026-11-01 (IST): a little before the first, a little after the last.
WINDOWS = {
    "interactive": "from=1793518080000&to=1793518290000",       # 12:58-13:01
    "interactive-long": "from=1793518290000&to=1793518535000",  # 13:01-13:05
    "suggest-on": "from=1793518540000&to=1793518685000",        # 13:05-13:08
    "suggest-off": "from=1793518685000&to=1793518830000",       # 13:08-13:10
}


def panel(arm: str, n: int | None) -> str:
    view = f"&viewPanel=panel-{n}" if n else ""
    return f"{GRAFANA}?orgId=1&{WINDOWS[arm]}&var-arm={arm}&kiosk{view}"


async def hold(page: Page, seconds: float = 10) -> None:
    await page.wait_for_timeout(seconds * 1000)


async def main(out_root: Path) -> None:
    screen = out_root / "claude_hidden_requests" / "screen"
    clips = {
        "tour": (panel("interactive-long", None), lambda p: hold(p, 12)),
        "spend": (panel("interactive-long", 1), hold),
        "tokens": (panel("interactive-long", 2), hold),
        "timeline": (panel("interactive-long", 3), hold),
        "labels": (panel("interactive-long", 4), hold),
        "suggest_on": (panel("suggest-on", 2), hold),
        "suggest_off": (panel("suggest-off", 2), hold),
    }
    only = set(sys.argv[2:])
    for name, (url, actions) in clips.items():
        if only and name not in only:
            continue
        print(await record(screen / f"{name}.mp4", url, actions))


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1])))
