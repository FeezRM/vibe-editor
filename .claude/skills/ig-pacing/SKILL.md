---
name: ig-pacing
description: "Pacing: a report of where nothing changes on screen, and zoom punches placed by hand on the words they serve. Use for: pacing, this feels boring, add zoom, push in, punch in, it drags, retention, energy."
---

# ig-pacing — node 07

```bash
python workflows/pacing-audit.py projects/<job>                    # report: stretches with nothing changing
python workflows/pacing-audit.py projects/<job> --zoom-at 4.85,20.1  # a punch on the clip spanning each time
python workflows/pacing-audit.py projects/<job> --zoom-out-open 35   # open 35 % punched in, ease out on the first word
python workflows/pacing-audit.py projects/<job> --clear-zooms        # remove every punch
./run.sh projects/<job> --from pacing
```

Nothing is added automatically. The report is information: a long static stretch is a question for the edit (is the
line dragging? would a cut, a graphic, or a punch help?), not a quota to fill.

## Zooms

Use them the way `samples/STYLE.md` says the samples do — how often, how much, how fast. If the samples barely punch
in, neither do you. A punch lands on a word that carries the line, snaps in around the face (`pacing.zoom_pct` over
`pacing.zoom_dur_s`), and holds until the next cut. Watch each one in the final; if it reads as a camera lurch rather
than emphasis, remove it.

The base camera is fixed for the whole video (`framing.scale`, `framing.face_y` in the look's `numbers.json`): one
crop on the median face, so jump cuts change only the pose.
