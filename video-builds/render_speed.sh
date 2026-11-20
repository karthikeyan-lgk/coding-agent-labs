#!/usr/bin/env bash
# Render speed on its own: re-render each finished build 3 times with the exact command its agent used
# (to bench.mp4, so out.mp4 is untouched), one at a time, memory-capped. One line per render to out/render_speed.jsonl.
set -uo pipefail
LAB=$(cd "$(dirname "$0")" && pwd); R="${VB_RUNS:-$HOME/.cache/video-builds-runs}"
export PATH="$HOME/.cargo/bin:$PATH"
for i in 1 2 3; do   # tries outer, tools inner: every tool sees the same background load
for run in hyperframes-opus-b1-1 remotion-opus-b1-1 hyperframes-opus-b2-1 remotion-opus-b2-1; do
  case $run in
    hyperframes-*) CMD="npx -y hyperframes@0.9.72 render -o bench.mp4 -q delivery --quiet" ;;
    remotion-opus-b1-1) CMD="npx remotion render src/index.ts Short bench.mp4 --log=error" ;;
    remotion-opus-b2-1) CMD="npx remotion render src/index.ts Main bench.mp4 --codec h264 --muted --log=error" ;;
  esac
    cd "$R/$run"; rm -f bench.mp4; S=$(date +%s.%N)
    systemd-run --user --scope -q -p MemoryMax=6G nice -n 10 bash -c "$CMD" > "bench_$i.log" 2>&1; CODE=$?
    E=$(date +%s.%N)
    P=$(ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 bench.mp4 2>/dev/null | tr '\n' ' ')
    printf '{"run":"%s","try":%d,"exit":%d,"render_s":%.1f,"probe":"%s"}\n' "$run" "$i" "$CODE" "$(echo "$E - $S" | bc)" "$P" | tee -a "$LAB/out/render_speed.jsonl"
    rm -f bench.mp4
done
done
