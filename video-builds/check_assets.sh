#!/usr/bin/env bash
# The brief's sound effects are Pixabay files (Pixabay Content License), which can't be shared as loose files,
# so they aren't in this repo. Put these four in assets/ first: get them free from pixabay.com/sound-effects,
# or copy them from the HyperFrames plugin (skills/media-use/audio/assets/sfx/), which bundles the same files.
missing=0
for f in pop.mp3 whoosh-short.mp3 impact-bass-1.mp3 click-soft.mp3; do
  [ -f "$(dirname "$0")/assets/$f" ] || { echo "missing assets/$f" >&2; missing=1; }
done
[ "$missing" = 0 ] || { sed -n '2,4p' "$0" >&2; exit 1; }
