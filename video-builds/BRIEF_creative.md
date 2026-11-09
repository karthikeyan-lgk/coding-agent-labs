# Brief (creative): "Your first Claude Code message costs 9x the rest" (vertical Short, 3D)

The same story, voiceover, captions and timings as the flat brief, told in a 3D world with physics and camera moves
instead of flat cards. Build it with the tool named in your prompt, in this folder. Use its 3D, physics and camera
features; flat 2D cards are allowed only for the captions, the "DAY 5" pill and the final send card.

## Output
- `out.mp4`: 1320 x 2868 (portrait, iPhone 17 Pro Max), 30 fps, H.264 + AAC, 25.8 s.
- Audio: `assets/vo.wav` (voiceover, 0 to 22.22 s) plus the sound effects listed below. Voice must stay clear.
- Must be sharp: text crisp at full size, no soft or upscaled frames, no jagged 3D edges (use anti-aliasing).

## Look
- World and background dark `#0b0f14`; a faint floor grid of `#223040` lines is welcome.
- Text: Inter (assets/Inter-*.ttf) for words and numbers, JetBrains Mono (assets/JetBrainsMono-SemiBold.ttf) for labels.
- Colours: ink `#e6edf3`, muted `#8b98a8`, panel `#11171f`, orange `#e8743b`, cyan `#3ec7d4`, green `#3fb950`, red `#f85149`.
  Orange = message 1 / the fee, cyan = later messages / cache reads.
- Everything important sits between y = 300 and y = 1890 (phone app bars cover the rest). Captions sit at y 1990 to 2240.
- A small orange pill "DAY 5" at the top centre (y about 300) until 22.4 s.
- Simple, clean shapes with soft lighting; readable on a phone at a glance. The camera moves with purpose, never wobbles.

## Captions
Karaoke captions from `assets/transcript.json` (word timings: `[{"text","start","end"}]`), Inter 84 px bold, centred
in the caption band, drawn flat on top of the 3D. The word being spoken is orange, spoken words white, upcoming words
grey. Cues (seconds): 0.16-2.56, 2.56-4.16, 4.16-6.88, 6.88-7.68, 7.68-10.64, 10.64-12.48, 12.48-14.32, 14.32-16.8,
16.8-18.48, 18.48-20.56, 20.56-22.1. No captions after 22.22 s.

## Beats (times in seconds, from the voiceover)
1. 0 - 6.88, the scales: a 3D balance scale. "Your first message" (white, ~120 px) at the top. At 0.4 one heavy orange
   block labelled "message 1" drops onto the left pan and slams it down. From 2.56 small cyan coins drop onto the right
   pan one by one (physics, a little bounce); the beam levels when the 9th lands at about 4.0, and a huge orange "9x"
   (~400 px) pops in above with a slight overshoot, "the price of the rest" (muted) under it. At 4.16 a label
   "$0.066" appears by the block; at 5.68 "$0.007" by one coin.
2. 6.88 - 7.68: the camera pulls back fast; the scale drops away out of frame and a huge "Why?" (white) is alone.
3. 7.68 - 12.48, the cache: heading "Message 1 writes / the setup to the cache". A glass jar labelled "cache"; from 9.04
   for about 1.4 s orange token cubes pour in and pile up (physics) while a number counts 0 -> 15,894 ("tokens written"
   under it). At 10.8 two cyan tags "system prompt" and "tool list" drop in and settle on the pile.
4. 12.48 - 16.8, the joining fee: a ticket "message 1  $0.066" lies on the floor; at 13.2 a red-orange "JOINING FEE"
   stamp slams onto it (rotated about -7 degrees), with a short camera shake. Then at 14.72, 15.12 and 15.52 three cyan
   tickets "message 2 / 3 / 4  reads cache  $0.007" slide through a turnstile that stays open (no charge).
5. 16.8 - 20.56, the tip: heading "Pay the fee once". Split view. At 17.6 left side, red: many small session cubes
   each stop at a turnstile and drop an orange coin, the coins pile up; label "New session for every tiny question" /
   "fee every time". At 18.9 right side, green: one session cube passes through once; label "One session per task" /
   "fee once". At 19.6 a small muted line "(/clear pays it again too)".
6. 20.56 - 22.4: "How many do / you open / a day?" big and centred ("a day?" in orange), the coin pile from beat 5
   still visible, dimmed, behind it.
7. 22.4 - 25.8, send card (flat is fine): "Send this to the friend / who opens a new chat / for every question", and a
   box "Comment" / "TRACE" (orange) / "free OpenTelemetry course" (small, muted).

Beats flow into each other with camera moves or 0.2 s fades; no hard cuts mid-sentence.

## Sound effects (assets/)
pop.mp3 at 4.16 and 5.68, whoosh-short.mp3 at 6.78 and 22.3, impact-bass-1.mp3 at 13.2, click-soft.mp3 at 18.9.
All well under the voice.

## Done means
1. `out.mp4` exists with the size, frame rate and length above, with sound.
2. You extracted frames at 1.0, 3.6, 4.2, 7.1, 10.2, 10.9, 13.3, 15.3, 18.0, 19.9, 21.4 and 24.0 s and looked at them:
   every beat is there and reads as 3D, nothing overlaps, nothing is cut off, text is sharp, captions match the voice.
3. You fixed what was wrong and re-rendered.
