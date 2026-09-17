---
name: ig-hook
description: "The first 0–8 seconds, decided inside the graphics plan: pick an opening mode from real evidence, put proof at frame zero, advance by second five. Use for: visual hook, opening recut, first 8 seconds, hook variants, Trial Reel openings."
---

# ig-hook — the opening, inside the plan

The hook is the graphics plan's first entries plus the EDL's first clips. There is no separate
document: write `"hook": {"mode": …, "evidence": […], "frame_zero": "g01"}` at the top of
`graphics-plan.json` and make `g01`'s cue ≤ 0.5 s.

## Modes (pick from evidence you actually have)

| Mode | Frame zero shows | Preset |
|---|---|---|
| receipt | the literal result / date / number | `receipt`, `metric` |
| comparison | both outcomes | `thumb-wall` (hero), two `receipt`s |
| demonstration | the mistake happening in the footage | `rec-frame` + a zoom punch |
| interface | a real UI in motion | `app-mock` |
| pattern-break | a wall of sameness, then the break | `thumb-wall` + strike |
| phrase | the claim, hook-sized, one proof object beside it | `phrase` + one of the above |

## Rules

- Frame zero is never a topic label over a talking head (`BRAND.md`). If the only honest option is
  the speaker's line, use `phrase` with the strongest word accented, and put a proof object in by 2 s.
- Something must change by second 5 — a second graphic, a reveal, a punch. The pacing audit sees
  the first 8 s like any other stretch.
- Captions are muted under a `phrase` (the preset declares it); everything else keeps captions.
- No fabricated proof. The acquisition ladder in `ig-show` applies with extra force here.

## Trial variants

`--hook-lab` is not implemented in `run.sh`; to test A/B/C openings, copy the job folder per variant,
change only the first plan entries, and run each. The premium reference (`docs/style/HOOK-ENGINE.md`,
`docs/style/VISUAL-HOOK.md`) describes the fuller storyboard workflow if a client wants it.
