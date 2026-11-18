#!/usr/bin/env python3
"""2 or 4 recordings in one 3840x2160 clip, each with a label line above it (free-models video).

    python grid.py <out.mp4> <seconds> "<run dir>[@start]|<label>|<colour>" ...   (2 or 4 tiles)

A run dir of "-" draws an empty tile with the label (e.g. "dots-3 · no page"). Recordings are 1920x1080 from
record.mjs and are only scaled down, never up.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = Path.home() / ".cache/viral-prompts-runs"
FONTS = HERE.parents[2] / "fframes/limit-short/media"
BOLD = FONTS / "Inter-Bold.ttf"
COLOURS = {"ernie": "0x3ec7d4", "flint": "0xe8743b", "north": "0xb48cf2", "dots": "0x7ee787", "dim": "0x8b98a5"}


def _esc(t: str) -> str:
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace(",", "\\,")


def build(out: Path, seconds: float, tiles: list[str]) -> None:
    if len(tiles) == 4:
        w, h = 1680, 945
        spots = [(160, 150), (2000, 150), (160, 1185), (2000, 1185)]
    elif len(tiles) == 2:
        w, h = 1860, 1046
        spots = [(40, 420), (1940, 420)]
    else:
        raise SystemExit("2 or 4 tiles")
    inputs, chains, texts = [], [f"color=c=0x0b0f14:s=3840x2160:r=30:d={seconds}[bg]"], []
    last = "bg"
    for i, (spec, (x, y)) in enumerate(zip(tiles, spots)):
        run, label, colour = (spec.split("|") + ["dim"])[:3]
        size = 64 if len(tiles) == 4 else 80
        texts.append(f"drawtext=fontfile={BOLD}:text='{_esc(label)}':x={x}:y={y - size - 24}:fontsize={size}:"
                     f"fontcolor={COLOURS.get(colour, colour)}:expansion=none")
        if run == "-":
            chains.append(f"[{last}]drawbox=x={x}:y={y}:w={w}:h={h}:color=0x1b222c:t=fill[e{i}]")
            last = f"e{i}"
            continue
        name, _, start = run.partition("@")
        inputs += ["-ss", start or "0", "-i", str(RUNS / name / "recording.mp4")]
        k = len(inputs) // 4 - 1
        chains += [f"[{k}:v]scale={w}:{h}[s{i}]", f"[{last}][s{i}]overlay={x}:{y}:eof_action=repeat[o{i}]"]
        last = f"o{i}"
    chains.append(f"[{last}]" + ",".join(texts) + "[v]")
    script = out.with_suffix(".filter.txt")
    script.write_text(";".join(chains))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex_script", str(script), "-map", "[v]",
                    "-t", str(seconds), "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", str(out)], check=True)
    script.unlink()
    print(out, seconds)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        raise SystemExit(2)
    build(Path(sys.argv[1]), float(sys.argv[2]), sys.argv[3:])
