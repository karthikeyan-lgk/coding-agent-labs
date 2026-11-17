#!/usr/bin/env python3
"""Opus and Fable recordings of one prompt, side by side at 3840x2160, with each run's numbers under it.

    python sidebyside.py <prompt> <out.mp4>        (prompts: token-bucket business-explainer ai-datacentre recursion qr-codes)

Numbers come from out/runs.jsonl; scores are the 4-check scores from the outline
(outlines/tech_en/fable_vs_opus_claude_code.txt). Recordings are 1920x1080 from record.mjs and are only
scaled down (to 1860 wide), never up. Spans listed in BLUR are blurred on the Opus side (recursion: the
pixel-art scene that looks like a famous platformer).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = Path.home() / ".cache/viral-prompts-runs"
FONTS = HERE.parents[2] / "fframes/limit-short/media"
BOLD, MONO = FONTS / "Inter-Bold.ttf", FONTS / "JetBrainsMono-SemiBold.ttf"
ORANGE, CYAN, TEXT, DIM = "0xe8743b", "0x3ec7d4", "0xe6edf3", "0x8b98a5"

PROMPTS = {
    # prompt: (opus run, fable run, credit, opus score, fable score)
    "token-bucket": ("1", "fable1", "@ParkerRex", 4, 4),
    "business-explainer": ("1", "fable1", "@alex_prompter", 3, 4),
    "ai-datacentre": ("1", "fable2", "@mdaman010", 4, 3),
    "recursion": ("2", "fable2", "@emollick", 3, 4),
    "qr-codes": ("1", "fable2", "@eyadnour", 4, 4),
}
BLUR = {"recursion": [(12, 18.5), (44, 49.5)]}


def _runs() -> dict:
    rows = {}
    for line in (HERE / "out/runs.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows[(r["prompt"], r["run"])] = r
    return rows


def _minutes(s: float) -> str:
    m, s = divmod(round(s), 60)
    return f"{m} min {s:02d} s" if m else f"{s} s"


def _esc(t: str) -> str:
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%").replace(",", "\\,")


def _text(t: str, x: str, y: int, size: int, color: str, font: Path = BOLD) -> str:
    return f"drawtext=fontfile={font}:text='{_esc(t)}':x={x}:y={y}:fontsize={size}:fontcolor={color}"


def build(prompt: str, out: Path) -> None:
    o_run, f_run, credit, o_score, f_score = PROMPTS[prompt]
    rows = _runs()
    o, f = rows[(prompt, o_run)], rows[(prompt, f_run)]
    o_mp4, f_mp4 = RUNS / f"{prompt}-{o_run}/recording.mp4", RUNS / f"{prompt}-{f_run}/recording.mp4"
    length = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(o_mp4)]))
    blur = "+".join(f"between(t,{a},{b})" for a, b in BLUR.get(prompt, []))
    o_chain = "[0:v]scale=1860:-2" + (f",boxblur=40:enable='{blur}'" if blur else "") + "[o]"
    texts = [
        _text(f"{prompt.replace('-', ' ')}  ·  prompt by {credit}, copied word for word", "80", 110, 76, DIM),
        _text("Opus 5.5", "40", 225, 80, ORANGE),
        _text("Fable 5.2", "1940", 225, 80, CYAN),
    ]
    for x, r, score, color in (("40", o, o_score, ORANGE), ("1940", f, f_score, CYAN)):
        texts += [
            _text(f"{_minutes(r['wall_s'])}  ·  {r['turns']} turns  ·  ${r['cost_usd']:.2f}", x, 1440, 84, TEXT),
            _text(f"read {r['cache_read']:,} tokens  ·  wrote {r['output']:,}", x, 1560, 64, DIM, MONO),
            _text(f"{score}/4 checks", x, 1680, 96, color),
        ]
    graph = ";".join([
        f"color=c=0x0b0f14:s=3840x2160:r=30:d={length}[bg]",
        o_chain,
        "[1:v]scale=1860:-2[f]",
        "[bg][o]overlay=40:340[t1]",
        "[t1][f]overlay=1940:340[t2]",
        "[t2]" + ",".join(texts) + "[v]",
    ])
    script = out.with_suffix(".filter.txt")
    script.write_text(graph)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(o_mp4), "-i", str(f_mp4), "-filter_complex_script", str(script),
         "-map", "[v]", "-t", str(length), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(out)],
        check=True,
    )
    script.unlink()
    print(out, length)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in PROMPTS:
        print(__doc__)
        raise SystemExit(2)
    build(sys.argv[1], Path(sys.argv[2]))
