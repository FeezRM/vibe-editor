---
name: ig-show
description: "The graphics layer as a plan file: choose a preset per beat, fill it with REAL content and a timeline cue, let the pipeline build, QA and loop. Use for: motion graphic, show this visually, overlay, mockup, chart, counter, stat graphic, graphics for this script, looks AI-generated, what should this graphic look like."
---

# ig-show — node 05

The graphics are a JSON plan, not compositions you write. **Presets own the motion; you choose the
preset, the real content, and the cue.**

```bash
python workflows/draft-plan.py projects/<job>       # heuristic first draft (numbers, lists, CTA, washes)
# edit projects/<job>/graphics-plan.json
./run.sh projects/<job> --from graphics             # validate → faces → build → qa → fix, ≤ 3 rounds
```

## The plan

One entry per graphic: `id, preset, cue, duration, placement (auto|beside-l|beside-r|inline|cutaway|wash),
reveal_at [seconds into the graphic, one per internal event], params (the preset's schema), provenance`.
`cue` is a **timeline** second taken from `captions.json`, never arithmetic on source time. `reveal_at`
lands each row/node/message on the word that names it.

## The ten presets (`presets/graphics/<name>/README.md` says when each is right)

| Speaker does… | Preset | Needs |
|---|---|---|
| says the claim / the payoff line | `phrase` (mutes captions) | the exact words |
| lists 2–6 things | `list-card` | the spoken items, in order |
| describes a process / before → after | `flow` | the nouns |
| says a number | `metric` | the real number + provenance |
| names an app, page, profile, DM | `app-mock` | a real screenshot (`workflows/capture-url.py`) |
| shows proof — a date, a result, a doc | `receipt` | the real still (`ffmpeg -ss … -frames:v 1`) |
| "everyone does this" / "these all…" | `thumb-wall` | 2–12 real images |
| gives a comment / DM CTA | `chat` | the literal CTA word, `creator.handle` |
| a bad → good turn, a win | `wash` | nothing (emotion, exempt from the mute test) |
| "I recorded this", the footage is the point | `rec-frame` | nothing |

## Real material — the acquisition ladder, in order

on disk (`assets/`, `samples/`) → extract from the footage → capture the real interface
(`workflows/capture-url.py <url> assets/x.png --mobile`) → look it up → generate a *texture* (never a
number) → ask the creator → build nothing. `validate-plan.py` refuses placeholders (`Hook 1`, `TBD`,
empty strings), missing files, metrics without provenance and any handle from `samples/`.

## The loop

`graphics-qa.py` checks composited pixels: caption band while a caption is live, face box, luma
(darkening), alpha, staleness. `fix-plan.py` applies deterministic remedies (flip side, move inline,
cutaway + mute, drop). After 3 rounds the node is `blocked` — that is your cue to re-plan the beat,
not to lower a threshold. Read `review/qa-round-N.png` every time.

## Scale check — before you call the layer done

Open two composited frames at 1080×1920 (not a sheet). A card should span ~85 % of the width at
chest height with ≥ 42 px text; a phrase should read at arm's length on a phone; nothing should be
a small dark rectangle in a corner. If it looks like "a box around text", the placement or preset
size is wrong — fix the preset (goldens will move; re-write them deliberately), not the one job.

## Taste rules that are yours to apply

Show the noun. If the footage already shows the object, do not add a graphic of it — punch in.
Vary the preset (three in a row is a warning, four fails). Mute captions only where the graphic
carries the words. One `wash` pair per video is plenty. Presence 60 % is the floor for basic tier;
the beat matters more than the percentage.

## Premium tier

`tier: premium` in `RUN.md` opens `docs/style/` (frame contracts, persistent-object scenes, the motion
floor `workflows/motion-density.py`). Same plan → build → QA loop; scene templates are presets too.
