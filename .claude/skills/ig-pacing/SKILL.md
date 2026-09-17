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
