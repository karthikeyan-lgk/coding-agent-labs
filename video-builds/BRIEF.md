# Brief: "Your first Claude Code message costs 9x the rest" (vertical Short)

The same brief for every tool. Build it with the tool named in your prompt, in this folder.

## Output
- `out.mp4`: 1320 x 2868 (portrait, iPhone 17 Pro Max), 30 fps, H.264 + AAC, 25.8 s.
- Audio: `assets/vo.wav` (voiceover, 0 to 22.22 s) plus the sound effects listed below. Voice must stay clear.

## Look
- Background `#0b0f14`, a faint grid of 78 px squares in `#223040`.
- Text: Inter (assets/Inter-*.ttf) for words and numbers, JetBrains Mono (assets/JetBrainsMono-SemiBold.ttf) for labels.
- Colours: ink `#e6edf3`, muted `#8b98a8`, panel `#11171f`, orange `#e8743b`, cyan `#3ec7d4`, green `#3fb950`, red `#f85149`.
- Everything important sits between y = 300 and y = 1890 (phone app bars cover the rest). Captions sit at y 1990 to 2240.
- A small orange pill "DAY 5" at the top centre (y about 300) until 22.4 s.
- Must be sharp: no upscaled images, text crisp at full size.

## Captions
Karaoke captions from `assets/transcript.json` (word timings: `[{"text","start","end"}]`), Inter 84 px bold, centred
in the caption band. The word being spoken is orange, spoken words white, upcoming words grey. Group the words into these cues
(seconds): 0.16-2.56, 2.56-4.16, 4.16-6.88, 6.88-7.68, 7.68-10.64, 10.64-12.48, 12.48-14.32, 14.32-16.8, 16.8-18.48,
18.48-20.56, 20.56-22.1. No captions after 22.22 s.

## Beats (times in seconds, from the voiceover)
1. 0 - 6.88, hook: "Your first message" (white, ~120 px) at the top; at 2.56 a huge orange "9x" (~400 px) pops in with a
   slight overshoot; at 3.06 "the price of the rest" (muted). At 4.16 a bar row slides in: label "message 1", value "$0.066",
   a full-width orange bar that grows in. At 5.68 a second row: "message 2+", "$0.007", a cyan bar about 1/9 of the width.
2. 6.88 - 7.68: a huge "Why?" (white) pops in, alone on screen.
3. 7.68 - 12.48, the cache: heading "Message 1 writes / the setup to the cache". A big rounded box labelled "cache" fills
   from the bottom with orange starting at 9.04 over about 1.4 s while a number inside counts 0 -> 15,894 ("tokens written"
   under it). At 10.8 two outlined cyan chips appear under the box: "system prompt" and "tool list".
4. 12.48 - 16.8, the joining fee: a panel "message 1 ... $0.066"; at 13.2 a red-orange outlined stamp "JOINING FEE" slams
   onto it, rotated about -7 degrees. Then three rows slide in at 14.72, 15.12, 15.52: "message 2 / 3 / 4", "reads cache",
   "$0.007" each, cyan outline.
5. 16.8 - 20.56, the tip: heading "Pay the fee once". At 17.6 a red card with a cross: "New session for every tiny question",
   "fee every time". At 18.9 a green card with a tick: "One session per task", "fee once". At 19.6 a small muted line
   "(/clear pays it again too)".
6. 20.56 - 22.4: "How many do / you open / a day?" big and centred ("a day?" in orange).
7. 22.4 - 25.8, send card: "Send this to the friend / who opens a new chat / for every question", and a box "Comment" /
   "TRACE" (orange) / "free OpenTelemetry course" (small, muted).

Scenes fade between each other in about 0.2 s. The background may move gently but must not distract.

## Sound effects (assets/)
pop.mp3 at 4.16 and 5.68, whoosh-short.mp3 at 6.78 and 22.3, impact-bass-1.mp3 at 13.2, click-soft.mp3 at 18.9.
All well under the voice.

## Done means
1. `out.mp4` exists with the size, frame rate and length above, with sound.
2. You extracted frames at 3.6, 5.9, 7.1, 10.9, 13.9, 16.0, 19.9, 21.4 and 24.0 s and looked at them: every beat is there,
   nothing overlaps, nothing is cut off, text is sharp, captions match the voice.
3. You fixed what was wrong and re-rendered.
