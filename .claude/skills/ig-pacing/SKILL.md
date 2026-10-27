---
name: ig-pacing
description: "Pacing as an audit over data: every cut, caption, graphic event and SFX is an event; gaps over 2 s get the cheapest interrupt (a zoom punch in the EDL). Use for: pacing, pattern interrupt, this feels boring, add zoom, push in, it drags, retention, energy."
---

# ig-pacing — node 07

```bash
python workflows/pacing-audit.py projects/<job>              # report
python workflows/pacing-audit.py projects/<job> --fix         # zoom punch on every gap > pacing.max_static_s
python workflows/pacing-audit.py projects/<job> --zoom-at 4.85   # a deliberate punch (a held-up prop, a landing line)
```

Punches are written into `cuts.json` on the clip that spans them (`zoom: {at, pct, dur}`) and applied
by both lanes; the spine is re-assembled by `run.sh`. Numbers: `numbers.json` → `pacing`.

The interrupt budget is spent on the graphics and caption layers first — a caption changes every
~0.8 s, so a talking head with a live graphics layer rarely needs a punch. If the audit reports many
gaps, the graphics plan is thin: go back to `ig-show`, don't paper over it with zooms.

## Cuts match on the face

His own reels are hard jump cuts with a camera that never moves: only the pose changes. Framing that re-centres each
clip, or a punch that is still in when the cut hits, makes every cut jump ("it looks snappy instead of smooth" — 9278,
where the face jumped 0.15 of the width at one cut). So the lane matches every cut on the face: rough-cut measures the
face on each clip's first and last frames (`face_in` / `face_out`, three frames averaged), the window glides between
them so the face sits in the same place on both sides of the join, the base scale follows the face's width so it is
the same size (within `framing.size_match`), and a punch eases back out (`pacing.zoom_hold_s`, `zoom_out_s`) before the
cut. `check-framing.py` fails any cut whose face moves more than `framing.cut_jump_tol` or changes size more than
`framing.cut_size_tol`. Never add a dissolve to hide a jump: his cuts are hard.

## What a punch is

A punch **snaps** (`pacing.zoom_dur_s`, ~0.12 s) to `pacing.zoom_pct` on a stressed word and holds to the end of the
clip; the next jump cut resets it. It is anchored on the clip's face (`cuts.json` keep.face, written by rough-cut), so
the face grows in place — never a slow creep, never a zoom from the frame centre or corner (9278: "the zooming in is
completely off" — a 1.2 s creep that slid the face 6 %). One punch per clip, on a word that carries the line
("I'm **not** even joking", "it's actually **insane**"), not on a timer.

The base shot is the creator's framing (`framing.scale`, `framing.face_y`): his posted reels are tight on the face, so
his look (`vertical/tiktok-sans`) punches the whole cut in 1.45× around the face. `check-framing.py` (run by
`run.sh` after the pacing spine) fails a clip whose face is off `framing.face_y` or under `framing.min_face_w`, and a
punch that moves the face more than `framing.anchor_tol`. Never call a punch done without that gate's numbers.
