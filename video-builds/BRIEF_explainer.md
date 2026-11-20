# Brief 2: "6 models, 5 prompts: who actually finished?" (16:9 data explainer)

The same brief for every tool. Build it with the tool named in your prompt, in this folder.
The data is real (our Fable vs Opus vs free-models lab); don't change any number.

## Output
- `out.mp4`: 1920 x 1080, 30 fps, H.264, exactly 45.0 s. Silent (no audio track needed).

## Data
`assets/scores.csv`: one row per model: `model, score_of_20, cost_usd, minutes`.

## Look
- Background `#0b0f14`. Fonts by element: Inter (assets/Inter-*.ttf) for titles, captions and the value written at
  each bar's end; JetBrains Mono (assets/JetBrainsMono-SemiBold.ttf) for model names and axis ticks.
- Colours: ink `#e6edf3`, muted `#8b98a8`, panel `#11171f`, orange `#e8743b` (paid models), cyan `#3ec7d4` (free models),
  green `#3fb950`.
- Keep everything inside a 96 px safe margin. Must be sharp: text crisp at full size.

## Beats (seconds)
1. 0 - 4: title "6 models, 5 prompts" (white, about 110 px) and under it "who actually finished?" (orange, about 70 px).
2. 4 - 20: a horizontal bar chart of `score_of_20`, one bar per model, sorted high to low, model names on the left.
   The axis runs 0 to 20 with ticks every 5. Bars grow from 0 with staggered starts: bar 1 starts at 4.5 s and each next bar 0.6 s later; each takes 0.8 s to grow (so they overlap slightly).
   Paid models orange, free models cyan. The score is written at the end of each bar once it has grown.
   Caption 1 at the bottom from 6 s: "Score out of 20, four checks per prompt".
3. 20 - 21: one transition of your choice (wipe, slide or crossfade) to the next scene, about 0.6 s long.
4. 21 - 38: the same models, now showing `cost_usd` as bars (axis $0 to $16, ticks every $4), same order as scene 2.
   Free models show "$0" with no bar. Caption 2 from 23 s: "Cost for all 5 prompts".
   At 30 s a green outlined box appears around the Opus and Flint rows with the label "18/20 for $10.93 vs 14/20 for $0".
5. 38 - 45: closing card: "Free got to 14/20." (white) and "Paid got to 19/20." (orange), and caption 3:
   "Full test on the channel". Hold to the end.

## Done means
1. `out.mp4` exists at 1920 x 1080, 30 fps, 45.0 s.
2. You extracted frames at 2, 10, 19, 20.5, 26, 32 and 42 s and looked at them: every bar and number matches the CSV,
   nothing overlaps or is cut off, text is sharp.
3. If anything was wrong, you fixed it and re-rendered; if nothing was, you finished.
