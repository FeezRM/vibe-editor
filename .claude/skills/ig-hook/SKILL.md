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
| act-out | the claim's verbs performed on a real object, landing on the words | `script-cut`, `shatter`, `transform` (see `ig-show` → act it out) |
| game | a pixel stand-in of the creator playing the hook's number out, from frame zero, beside his face | `pixel-quest` (money), `pixel-crowd` (audience) — `ig-show` → play it |

On 9030 ("Is it possible to get to 10K a month while working a job and in uni?") the stock `metric` counter was
rejected as uncreative and a keyed cash explosion as tacky. What landed: cue 0.0, a pixel version of the creator
spawns, sprints, punches a $ block on "to" and the counter rolls white → green across "ten thousand", then a
**condition montage** takes over: one real 0.4–0.5 s shot per condition ("working a job" → office, "in uni" →
campus; `broll_story.hook_montage_*`). The question stays on the face; the conditions go to b-roll.

On 9077 ("This video is scripted and edited by AI") an `agent-run` console that typed the job's
real steps was honest but read as text in a box. `script-cut` performed the two verbs instead, cue
0.0, `top` placement: the real script wrote itself on "scripted", a blade cut it into the EDL's real
clips (real frames) on "edited", and the dead takes broke away red. The creator's verdict went from
6/10 to "pretty good". A hook that *does* the claim beats one that *proves* it with text.
Frame zero must already show the object (cue 0.0, content drawing from the first frame), not an
entrance that is still fading in.

## Rules

- Frame zero is never a topic label over a talking head (`BRAND.md`), and a `phrase` alone is the
  last resort, not the default — the references open on an object (a phone, a chart, a wall of
  reels). Prefer a real screen or still the viewer recognises; if the only honest option is the
  speaker's line, use `phrase` with the strongest word accented **and** put a real object in by 2 s.
- Something must change by second 5 — a second graphic, a reveal, a punch. The pacing audit sees
  the first 8 s like any other stretch.
- Captions are muted under a `phrase` (the preset declares it); everything else keeps captions.
- No fabricated proof. The acquisition ladder in `ig-show` applies with extra force here.

## Trial variants

`--hook-lab` is not implemented in `run.sh`; to test A/B/C openings, copy the job folder per variant,
change only the first plan entries, and run each. The premium reference (`docs/style/HOOK-ENGINE.md`,
`docs/style/VISUAL-HOOK.md`) describes the fuller storyboard workflow if a client wants it.
