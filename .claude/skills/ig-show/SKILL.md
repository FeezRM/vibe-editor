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

## Show, don't caption — the first rule

The captions already carry the words. If the graphics layer is also words, the reel is a slideshow of
text over a talking head, and it reads as generated. **A graphic exists to SHOW the thing the speaker
names**: the real screen, the real profile, the real post, the real document, the footage itself punched
in, a wall of real thumbnails, a colour flood for a feeling. Look at `samples/` and
`docs/style/SAMPLES.md`: the references are a phone in a hand, a profile filling in, a feed scrolling,
a competitor's reel with one word boxed — almost never a sentence in a nicer font.

For every beat, in this order:

0. **What does the line MEAN?** Name the concept before you reach for a noun. A word can name a
   thing and mean something else: "the right AI *setup*" means *a system doing the work*, not a
   product's web page; "30 times *better*" means *quality*, not thirty copies; "*faster*" means
   time collapsing; "*boring*" means time dragging; "everyone" means a wall; "the one" means a hero.
   Show the meaning. The noun is only the material the meaning is built from.

   | The line means… | Show |
   |---|---|
   | a system / setup / "it does it for me" | `agent-run` — real steps typing and checking off, a real result |
   | more, N of them | `multiply` — one real thing becomes N |
   | better, N× the quality | `upgrade` — the same real thing sharpens and colours in as a dial fills |
   | the one that won | `scan` with `hero`, `thumb-wall` with `hero` |
   | everyone / all of them / dying | `scan` (dim), `thumb-wall` (strike) |
   | a real screen the viewer would recognise | `app-mock` (phone), `receipt` (still) — only when the *screen itself* is the subject |
   | the feeling turns | `wash` |

   If your visual could be captioned "a picture of the noun", it is the wrong visual.

   **Then act it out.** The creator scored a reel of real-but-static graphics (a receipt that slowly
   zooms, a phone that scrolls, a console of text lines) **6/10**: "some visuals contain text and don't
   stand out, some are just image stills slowly zooming in". The same beats redone as *actions* (the
   script is sliced into clips, the silence shatters off the waveform, the file is dragged into the app,
   the layers slam together, the phone plays the reel inside itself) scored "pretty good". So for every
   beat name the **verb** as well as the meaning, and make the object *do* it on the word:

   | The line's verb… | Show (demonstration preset) |
   |---|---|
   | wrote / scripted, then cut / edited | `script-cut`: the real script writes on, a blade slices it into the EDL's real clips, dead ones break away red |
   | X goes in, Y comes out ("run my idea through a skill") | `transform`: input fed into a labelled machine that works, output emerges |
   | drop / upload / send it into an app | `drag-drop`: a cursor drags the real file (frame + real filename) into a window named for the real app |
   | cut / remove / tighten silence, dead space | `dead-space`: the REAL waveform (`workflows/waveform.py`), silence goes red and shatters, counter raw → kept |
   | it makes A, B and everything | `layer-stack`: real footage / caption / graphic layers fan out in 3D, land on their words, slam into one |
   | review / approve / reject | `stamp`: a playhead runs through the real thing, a check or cross slams down |
   | "the video you're watching" | `phone-play`: a phone rises playing the finished reel at that moment (it contains itself) |
   | comment X and I'll send Y | `comment`: X types into a comment box, sends, the DM drops in carrying Y |
   | OVERPOWERED / broke / destroyed / dead | `shatter`: the thing strains, cracks, explodes into red shards (one per video) |

   A still that only zooms, and any card whose content is sentences, is the fallback, not the plan.

1. **What can I show?** Run the line through `docs/style/DEVICES.md` §0. A named THING → `app-mock`
   (real screenshot, `scroll_px` so it moves) · a result / date / doc → `receipt` (real still, slow `zoom`)
   · "everyone / these all / my videos" → `thumb-wall` (real tiles, `hero` or `strike`) · "look at this /
   I recorded" → `rec-frame` + a `zoom` punch in `cuts.json` · a bad→good turn → `wash`.
2. **Where do I get it?** The acquisition ladder below — and the creator's **own** logged-in Chrome
   (`claude-in-chrome`) is the strongest rung for their own profile, their own posts, their own tools:
   real, current, theirs. Capture at phone width, save into `assets/`, write the provenance.
3. **Only then** a text preset (`phrase`, `list-card`, `flow`, `metric`, `chat`), and only when the words
   *are* the point — the hook claim, the one number, the literal CTA word. Never to restate the caption.

The gate: text-only presets may carry at most `graphics.max_text_share` of graphic time
(`numbers.json`; `validate-plan.py` fails above it). Be creative *inside* that: a screen that scrolls,
a still that pushes in, a wall that gets struck through, one object that comes back later changed —
motion and callbacks, not more cards. When there is truly nothing real to show, build nothing and let
the caption and a zoom punch carry the beat — that beats a card.

## Play it, don't print it: the third rule

Real and acted-out is the floor, not the bar. On the 9030 reel the creator rejected, in order: a keyed
green-screen cash explosion ("tacky"), a hand-made profile card ("out of place"), the stock `metric` counter
("lacks creativity in every single aspect") and a real profile screenshot that slowly zoomed ("an image zooming
in… there's nothing of substance"). What he asked for instead was **a pixel-art video game where a character that
looks like him plays the line out**, and then he asked for that to become a style (`vertical/pixel-arcade`).
Before you pick a preset, ask:

1. **Could this beat be a scene instead of an object?** A number is a score in a game, an audience is a crowd
   running in, a goal is a block you punch. Give the scene a **stand-in of the creator** (`look` sampled from the
   footage: hair, skin, glasses, beard, shirt and logo colour, pants, shoes) and keep that look identical in every
   graphic of the reel, so it's one character returning, not a mascot per beat.
2. **Does the real proof live inside the scene?** His real avatar pixelated into the HUD, the real count as the
   score, the spoken number as the target. Playful never means invented: provenance still applies.
3. **Does the second appearance change state?** The hero and ledge come back with a crowd; the empty block is
   now grey and cashed in. That's a callback, not a repeat.
4. **Would a stock asset do this?** Then it's wrong. No green-screen packs, no generic counters, no card that a
   template site sells. If the beat can't be played, leave the face and the caption alone.

| The line… | Play it with |
|---|---|
| a money goal / price / monthly figure | `pixel-quest`: the hero sprints, punches a $ block on the number, coins spin into an arcade counter that rolls white → green |
| an audience number (followers, subs, members) | `pixel-crowd`: the same hero; pixel followers pour in from both edges while the count climbs to the real value; the crowd jumps, hearts float |
| anything else, in a reel that uses the game world | any preset under the `pixel-arcade` skin (PixelQuest type, brick panels, hard outlines, 12 fps steps) so the whole layer is one world |

For a b-roll-driven talking head, graphics live **only where the face is on screen**; the b-roll carries
everything else (`docs/style/BROLL-STORY.md`). Place against the creator's real framing: a punched-in Premiere
sequence puts the head where the spine's `top` slot is.

## Never the same thing twice — the second rule

A viewer who has seen a row of tiles does not want a row of tiles four seconds later, even with new
tiles in it. Boredom is *sameness of kind*. Every preset belongs to a **visual family**
(`numbers.json` → `graphics.families`): `wall` (scan, thumb-wall) · `tiles` (multiply) · `gauge` (upgrade) ·
`console` (agent-run) · `screen` (receipt) · `device` (app-mock) · `number` (metric) · `words` (phrase,
list-card, flow) · `thread` (chat) · `flood` (wash) · `footage` (rec-frame). `validate-plan.py` fails the plan when:

- two graphics in a row are the same family (floods and footage don't count);
- a family appears more than twice, or returns with fewer than two other graphics between — a
  family may come back **once**, as a callback, and the object must be in a changed state (the
  tiles that died now get scanned; the number that was 1 is now 30);
- one asset file appears in more than two graphics — get more real material, don't recycle;
- a reel with four or more graphics shows fewer than four families.

So plan the sequence as a run of *different kinds of things*: a wall, then a screen, then a burst,
then a device, then the wall again changed, then a thread. Write the family next to each beat
before choosing the preset; if two neighbours match, change one of them, not the rule.

## The plan

One entry per graphic: `id, preset, cue, duration, placement (auto|beside-l|beside-r|inline|cutaway|wash),
reveal_at [seconds into the graphic, one per internal event], params (the preset's schema), provenance`.
`cue` is a **timeline** second taken from `captions.json`, never arithmetic on source time. `reveal_at`
lands each row/node/message on the word that names it.

## The presets (`presets/graphics/<name>/README.md` says when each is right)

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
| "your content / these die / the machine reads them all" | `scan` (dim → the threat; scan + hero → the payoff) | 2–8 of the creator's real tiles |
| "30 times MORE", "10× the output" — a spoken quantity | `multiply` (one real tile → N tiles + counter) | the tile + the spoken number with `source` |
| "30 times BETTER", "twice as sharp" — a spoken quality | `upgrade` (one real tile sharpens as a dial fills to N×) | the tile + the number + the quality word |
| "my AI setup / the system / the agent runs it" | `agent-run` (real steps type, spin, check; real result) | the real session name, its real steps, its real output |
| scripted + edited / cut into clips | `script-cut` (top) | the real script lines, the EDL's clip count, one real frame per clip (`thumbs`) |
| X → a tool → Y | `transform` | two icons from `_icons.html` (or real images) + the speaker's noun for the machine |
| drops / uploads a file into an app | `drag-drop` (top) | a real frame of the file, its real filename, the real app name |
| cuts silence / dead space | `dead-space` | `assets/waveform.json` from `workflows/waveform.py <job>` (an `x-json` param) |
| makes captions, graphics, everything | `layer-stack` (top) | a real footage frame, the real caption words, a real still of one of the reel's graphics |
| reviews / approves / rejects | `stamp` | a real frame (of the final, on a second pass) |
| "the video you're watching" | `phone-play` (inline) | the finished reel cut to this graphic's window (second pass) |
| comment-to-DM CTA | `comment` (cutaway) | the literal word, the promised reply, the promised things' real names |
| something violently wins / breaks | `shatter` (top) | an icon, a real still, or one short word |
| says a money goal / price / monthly figure | `pixel-quest` (top or inline) | the spoken number + `source`, the creator's `look` |
| says an audience number | `pixel-crowd` (inline or top) | the real count + `source` (a real profile), the avatar pixelated 16×16, the same `look` |

## Where it goes: alternate the slots

The face sits centre (about y 650–990 with its pad) and the captions own y 920–1130, which leaves two big
slots: **`top`** (y 210–640, 920 wide, above the head; `graphics.top_top` / `top_h`) and **`inline`** (y 1180+,
below the captions). Alternate them beat to beat; a layer docked entirely under the captions reads as one
box that keeps changing. `cutaway` presets that lay out the whole frame (`comment`) keep their own content
off the face and the band; QA checks both.

## Real data and the second pass

- `workflows/waveform.py <job>` → `assets/waveform.json` (RMS of the raw and of the cut + the keeps). Presets
  read files like it through an `x-json` param, loaded at build time. Never paste numbers into the plan.
- Frames per clip: the middle of each `cuts.json` keep (`ffmpeg -ss … -frames:v 1 -vf scale=240:-2`); dropped
  takes: the middle of the longest `removed` ranges.
- **Recursive material needs a second pass.** Build once, then take a frame of `outputs/<job>.final.mp4` (for
  `stamp`), an alpha still of another render (`ffmpeg -ss t -i renders/gNN.mov -pix_fmt rgba`, cropped; for
  `layer-stack`) and the final cut to a graphic's window (for `phone-play`), mark those graphics `dirty` and
  run `--from graphics` again. The phone then plays a reel that contains the phone.

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

Show the noun (the first rule, above), play it (the third rule). If the footage already shows the object, do not add a graphic of it — punch in.
Never a stock overlay (keyed effects packs, generic counters), never a still whose only motion is a zoom.
Look at every graphic on the creator's *framed* output (Premiere program monitor) — a punch-in moves the face.
Vary the preset (three in a row is a warning, four fails). Mute captions only where the graphic
carries the words. One `wash` pair per video is plenty. Presence 60 % is the floor for basic tier;
the beat matters more than the percentage.

## Authoring a preset: what broke while building the demonstration set

Add a preset (never a hand-made composition): `template.html` extending `_base.html`, `params.schema.json`,
`example.json` with **neutral** example assets (the repo is public: no creator footage), `README.md`, a golden
from `build-graphics.py --preset presets/graphics/<name> --write-golden`, its family in `numbers.json →
graphics.families`, and its verbs in `sfx-plan.py`. Shared pieces: `_icons.html` (drawn SVG objects:
`{% import "_icons.html" as ic %}` then `{{ ic.icon("bulb", 200) }}`) and `prng(seed)` in `_base.html` for debris.

- **Look at the motion, not the golden.** The golden is one frame at t=1.0; composite 4–6 moments of the
  render over a real A-roll frame (`ffmpeg -ss t -i renders/….mov -pix_fmt rgba`, alpha-composite) and look.
  Every defect below was invisible in the golden.
- GSAP `keyframes: [...]` arrays did not seek correctly in the render (the drag stalled, then jumped): write
  consecutive `tl.to` calls instead.
- A `fromTo` whose *from* state is visible (a ring at opacity 1) paints at build time and shows from frame 0:
  pass `immediateRender: false`.
- Clipped copies (`clip-path` slices of one element) position their children relative to the WHOLE element:
  a thumbnail at `left: 4px` shows only in slice 0. Place per-slice content at `i × sliceW`.
- Use `<img>`, not CSS `background-image`, for real assets.
- Class names from `tokens.css` restyle your elements (`.cap` rendered upper-case): prefix every class.
- `sepia()` on a light colour lands on gold, not red; `brightness(.55) sepia(1) hue-rotate(-38deg) saturate(9)` reads red.
- Debris, glows and flying objects stay out of the face box and the band (fling up or sideways, glows
  ≤ 340 px), or `graphics-qa` drops the graphic.
- Size for a phone: objects ≥ 200 px, labels ≥ 30 px, light surfaces (white glass, azure rim); a dark
  machine disappears against a black shirt.
- `rgba(` in a `background` fails `graphics-qa`; use 8-digit hex (`#1F84ED33`) or a gradient.

## Premium tier

`tier: premium` in `RUN.md` opens `docs/style/` (frame contracts, persistent-object scenes, the motion
floor `workflows/motion-density.py`). Same plan → build → QA loop; scene templates are presets too.
