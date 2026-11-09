# Fix pass 2 (only these things; leave every other scene, timing, caption and sound exactly as it is)

`edit.tsx` renders the Short in BRIEF.md (v2 kept as out_v2.mp4 / edit_v2.tsx). A reviewer found:

Blocker
1. Question scene (20.56 - 22.4 s): a turnstile post with its red knob from the split scene stands right behind
   "How many do / you open", and a diagonal red/green floor cuts across the frame. Remove or fully fade the split
   scene's gates, cubes, coins and lane floors before 20.6 s; behind the question keep only the dark world and grid.

Should fix
2. Cache scene (11.0 - 12.4 s): the "system prompt" tag is half buried in the cubes and "tool list" is not visible.
   Both tags must be fully readable from 10.8 s to the end of the beat: let them rest on top of the pile in front of
   the glass (or float just above the jar mouth), side by side, never covered by cubes.
3. Joining-fee ticket (13.3 s): the small "message 1" label overlaps the top of "$0.066". Move it up or shrink the
   number so there is a clear gap.
4. Split scene (19.9 s): the orange coin pile still overlaps the session cubes at the left gate. Pile the coins
   beside the gate on the floor, away from the cubes' path.

Polish
5. 10.2 - 11.0 s: cubes bounce out past the right frame edge; keep them inside the frame.
6. 15.3 s: the turnstile posts are cut off at both frame edges and the "message 3" ticket covers the right post;
   bring the gate fully into frame.
7. 19.6 s+: the lane divider line runs through "pays" in "(/clear pays it again too)"; move the line or the text.
8. "fee every time" / "fee once" are about 28 px; make them at least 40 px.

Keep the audio as it is (music is mixed in afterwards). Render to out.mp4, then look at frames 10.4, 10.9, 11.5, 12.2,
13.3, 15.3, 18.4, 19.2, 19.9, 20.4, 20.8, 21.4 and 22.2 s at full size: every fix holds and nothing new overlaps or is
cut off. Spot-check 3.6, 7.1 and 24.0 s are unchanged.
