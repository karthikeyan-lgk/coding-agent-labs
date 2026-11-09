# Fix pass (only these three things; leave every other scene, timing, caption and sound exactly as it is)

`edit.tsx` already renders the Short in BRIEF.md (v1 kept as out_v1.mp4 / edit_v1.tsx). Fix:

1. Cache scene (about 9.0 - 12.4 s): token cubes fly over the heading "Message 1 writes / the setup to the cache".
   Nothing may pass over or behind the heading text: spawn the cubes below the heading (just above the jar mouth),
   or keep them in a narrower column, so the heading stays fully clear in every frame.
2. Split scene (17.6 - 20.5 s): the left lane's labels ("New session for every tiny question" / "fee every time") sit
   at the left edge, and the coin pile overlaps the session cubes. Keep all labels at least 80 px inside the frame
   and inside the y 300-1890 band; let the coins pile beside or below the gate, never covering a cube or a label.
3. Question scene (20.56 - 22.4): coins from the split scene fly across "How many do / you open / a day?". Clear them
   (fade them out, or move the pile low and out of the text area, dimmed) so nothing crosses the question text.

Then render to out.mp4 and look at frames 9.6, 10.2, 10.9, 11.8, 17.8, 18.4, 19.2, 19.9, 20.8, 21.4 and 22.2 s at full
size: the three fixes hold, nothing new is cut off or overlapping. Spot-check 3.6, 13.9 and 24.0 s are unchanged.
