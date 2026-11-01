"""Grafana clips for "Claude Code Usage Limits Explained".

    uv run --no-project --with playwright==1.64.0 python -I \
        companions/coding_agent_telemetry/usage_limits/record_clips.py en/output [clip names]

Run while the lab stack still holds the 2026-10-30 runs (Prometheus keeps them in its container volume).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "otel_course_recording"))
from browser import Page, record  # noqa: E402

GRAFANA = "http://127.0.0.1:13000/d/claude-usage-limits"
# 14:08 to 14:28 IST on 2026-10-30: every arm of run_all.sh
WINDOW = "from=1793349480000&to=1793350680000"


def panel(n: int | None) -> str:
    view = f"&viewPanel=panel-{n}" if n else ""
    return f"{GRAFANA}?orgId=1&{WINDOW}&kiosk{view}"


async def hold(page: Page, seconds: float = 10) -> None:
    await page.wait_for_timeout(seconds * 1000)


async def trace_line(page: Page) -> None:
    """Hover along the long-session line so the tooltip reads out each turn."""
    await page.wait_for_timeout(2500)
    box = await page.locator("canvas").first.bounding_box()
    if box:
        y = box["y"] + box["height"] * 0.5
        for i in range(60):
            await page.mouse.move(box["x"] + box["width"] * (0.28 + i * 0.005), y)
            await page.wait_for_timeout(120)
    await page.wait_for_timeout(3000)


async def main(out_root: Path) -> None:
    screen = out_root / "claude_usage_limits" / "screen"
    clips = {
        "one_word": (panel(1), hold),
        "long_session": (panel(2), trace_line),
        "token_split": (panel(3), hold),
        "three_models": (panel(4), hold),
        "limit_meter": (panel(5), hold),
        "dashboard_tour": (panel(None), lambda p: hold(p, 12)),
    }
    only = set(sys.argv[2:])
    for name, (url, actions) in clips.items():
        if only and name not in only:
            continue
        print(await record(screen / f"{name}.mp4", url, actions))


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1])))
