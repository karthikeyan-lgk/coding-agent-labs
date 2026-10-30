"""Jaeger clips for "Claude Code in CI: Trace Every Headless Run with OpenTelemetry".

    uv run --no-project --with playwright==1.64.0 python -I \
        companions/coding_agent_telemetry/ci_pipeline/record_clips.py en/output <bad night trace id> <bad night run id> <split trace id> [clip names]

Run after `pipeline.py split` and a few `pipeline.py joined` runs. Jaeger keeps traces in memory, so the ids
change on every lab restart.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "otel_course_recording"))
from browser import Page, record  # noqa: E402
from record_browser_ch0_3 import collapse_header, widen_names  # noqa: E402

JAEGER = "http://localhost:16686"
TOOL_ROW = re.compile(r"claude_code\.tool$")
DECISION_ROW = re.compile(r"claude_code\.tool\.blocked_on_user$")


def search(service: str, tags: dict[str, str] | None = None, operation: str | None = None) -> str:
    q = {"service": service, "limit": "20", "lookback": "1h"}
    if tags:
        q["tags"] = json.dumps(tags)
    if operation:
        q["operation"] = operation
    return f"{JAEGER}/search?{urllib.parse.urlencode(q)}"


async def show_results(page: Page) -> None:
    await page.wait_for_timeout(2500)
    await page.mouse.move(700, 450)
    for _ in range(8):
        await page.mouse.wheel(0, 30)
        await page.wait_for_timeout(60)
    await page.wait_for_timeout(5000)


async def whole_trace(page: Page) -> None:
    await page.wait_for_timeout(800)
    await collapse_header(page)
    await widen_names(page)
    await page.wait_for_timeout(1500)
    await page.mouse.move(700, 600)
    for _ in range(20):
        await page.mouse.wheel(0, 40)
        await page.wait_for_timeout(120)
    await page.wait_for_timeout(3000)


async def hold_trace(page: Page) -> None:
    await page.wait_for_timeout(800)
    await collapse_header(page)
    await widen_names(page)
    await page.wait_for_timeout(12000)


async def open_row(page: Page, pattern: re.Pattern[str], nth: int, scroll: int = 300) -> None:
    await page.wait_for_timeout(800)
    await collapse_header(page)
    await widen_names(page)
    await page.wait_for_timeout(800)
    await page.locator(".span-name-wrapper").filter(has_text=pattern).nth(nth).locator(".span-name").click()
    await page.wait_for_timeout(900)
    # Jaeger opens GenAI spans on its GenAI tab; the raw attributes live under Details.
    details = page.get_by_text("Details", exact=True)
    if await details.count():
        await details.first.click()
        await page.wait_for_timeout(500)
    await page.get_by_text("Attributes:", exact=True).first.click()
    await page.wait_for_timeout(600)
    await page.mouse.move(700, 380)
    for _ in range(6):
        await page.mouse.wheel(0, scroll / 6)
        await page.wait_for_timeout(60)
    await page.wait_for_timeout(5000)


async def interaction_attrs(page: Page) -> None:
    await open_row(page, re.compile(r"claude_code\.interaction$"), 1, scroll=200)


async def main(out_root: Path, bad: str, run_id: str, split: str) -> None:
    screen = out_root / "claude_code_ci_tracing" / "screen"
    clips = {
        "split_strangers": (search("claude-code", {"parent.source": "none"}, "claude_code.interaction"), show_results),
        "split_one_run": (f"{JAEGER}/trace/{split}", whole_trace),
        "split_parent_none": (f"{JAEGER}/trace/{split}", lambda p: open_row(p, re.compile(r"claude_code\.interaction$"), 0, scroll=200)),
        "release_nights": (search("release-prep"), show_results),
        "bad_night_trace": (f"{JAEGER}/trace/{bad}", whole_trace),
        "bad_night_still": (f"{JAEGER}/trace/{bad}", hold_trace),
        "refused_command": (f"{JAEGER}/trace/{bad}", lambda p: open_row(p, TOOL_ROW, 2, scroll=170)),
        "refused_decision": (f"{JAEGER}/trace/{bad}", lambda p: open_row(p, DECISION_ROW, 2, scroll=200)),
        "parent_source_env": (f"{JAEGER}/trace/{bad}", interaction_attrs),
        "find_by_run_id": (search("release-prep", {"cicd.pipeline.run.id": run_id}), show_results),
    }
    only = set(sys.argv[5:])
    for name, (url, actions) in clips.items():
        if only and name not in only:
            continue
        print(await record(screen / f"{name}.mp4", url, actions))


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1]), *sys.argv[2:5]))
