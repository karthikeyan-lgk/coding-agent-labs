# Opus 5.5 round (2026-11-20): quality checks

Frames at the brief's "Done means" times; first pass by Command Code (google/gemini-3.8-flash),
every FAIL then checked by eye at full size.

| build | checks | notes |
|---|---|---|
| hyperframes opus-b1-1 | 9/9 | Gemini flagged 21.4 s ("a day?" missing): false, the line is revealed with the voice and is there at 22.1 s |
| remotion opus-b1-1 | 8/9 | 7.1 s: "Why?" is cut off at both edges (confirmed). Same 21.4 s false flag as above |
| remotion opus-b2-1 | 7/7 | spot-checked 10 s + 32 s by eye: values, order, colours, green box all right |
| hyperframes opus-b2-1 | 7/7 | same; also adds a subtitle under each chart heading |

## Where the time went (time_split.py, from Claude Code's own timestamped transcripts)

| build | wall | model | render | install | other | network stall |
|---|---|---|---|---|---|---|
| hyperframes b1 (9:16) | 389 s | 251 | 100 | 0 | 36 | 0 |
| remotion b1 (9:16) | 331 s | 149 | 151 | 25 | 6 | 0 |
| remotion b2 (16:9) | 229 s | 123 | 79 | 23 | 3 | 0 |
| hyperframes b2 (16:9) | 2011 s | 184 | 55 | 0 | 24 | **1749** (one API request hung, then ECONNRESET) |

Excluding the stall, HyperFrames b2 took ~262 s, so on charts the two tools are close; HyperFrames renders faster
(55 vs 79 s, 100 vs 151 s), Remotion needs fewer model turns. Report the stall honestly; don't count it as tool time.

## Edit test (resume the build session with one change request), checked by eye before/after

| build | edit time | turns | edit cost* | result |
|---|---|---|---|---|
| hyperframes b1 | 73 s | 8 | $0.82 | both bars blue, heading ~80 px higher, nothing else changed |
| remotion b1 | 77 s | 5 | $0.42 | same |
| remotion b2 | 47 s | 8 | $0.52 | all bars blue in both charts, title ~80 px higher |
| hyperframes b2 | 44 s | 5 | $0.68 | same |

*resumed session reports build + edit together; edit = total - build. All 4 edits correct first time.

## Render speed alone (render_speed.sh, 3 interleaved renders each, the agent's own command, this laptop)

| video | HyperFrames (s) | Remotion (s) | median |
|---|---|---|---|
| 9:16 Short (25.8 s) | 41.3, 45.0, 44.2 | 70.4, 65.9, 68.8 | 44.2 vs 68.8 (1.56x) |
| 16:9 chart (45 s) | 23.1, 20.3, 22.9 | 32.3, 32.7, 31.5 | 22.9 vs 32.3 (1.41x) |
HyperFrames used `render -q delivery`, Remotion its default h264 render, as each agent chose.
