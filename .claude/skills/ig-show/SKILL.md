---
name: ig-show
description: >-
  Designs and builds the SHOW layer of a short-form video — the motion graphics that
  visually depict what is being said, in the VIRAL house style: rebuilt app UI (Instagram
  profile, story, feed, DM), real content carrying real metrics, side-by-side comparisons,
  tier stacks, charts with labelled axes, countdowns, and semantic colour washes. Fifteen
  named blocks, four frame contracts and a spoken-idea-to-object lookup, built as HyperFrames
  HTML compositions
  and rendered to alpha .mov / .mp4 for Premiere Pro. Works brief to questions to approved
  MOTION PLAN to build to render to Premiere import sheet. This is step 4 of the six-step
  editing SOP and the one that matters most. Use whenever the user wants to: make or design
  a motion graphic, visually show or represent what they are saying, add a graphic/overlay/
  lower-third/animated text to a reel, visualize a number or stat, build a mockup, counter,
  chart, comparison, or end card, style or restyle reel graphics, plan the graphics for a
  script, or ask what a graphic should look like or why their graphics look AI-generated.
  Triggers: motion graphic, motion graphics, show this visually, visualize this, animate
  this, animated overlay, reel graphic, lower third, kinetic text, animated number, counter
  animation, stat graphic, chart for my reel, mockup, graphics for this script,
  hyperframes, premiere overlay, alpha overlay, b-roll graphic, make it look premium, looks
  ai generated, what should this graphic look like.
---

# IG SHOW — put the thing on screen

**Step 4 of the editing SOP, and the one that separates a good edit from a premium one.**

> "You wanna visually show as much as you can in your video."

This skill owns the **look** and the **build** of every designed element. The cut belongs to
`ig-cut`, captions to `ig-captions`, audio to `ig-sound`, pacing to `ig-pacing`.

`ig-hook` owns the first 0–8 seconds. When it routes a beat to HyperFrames, this skill
builds that designed object; it does not choose the opening mode or replace the Hook Packet.

---

## The one rule

> # SHOW THE NOUN.

If the script names a thing the viewer could recognise — a profile, a story, a DM, a reel, a
document, a button — put **that thing** on screen, rebuilt faithfully enough to be
recognised in half a second. If the script names a number, a rank, or a change, draw the
**actual measurement**, with real axes and real units.

**The disqualifier, and it is not optional:**

> Mute the video and hide the captions. Does the frame still make the point?
> If not, it is decoration. Delete it and build nothing.

A graphic that could be replaced by its own caption is not a graphic — it is the caption in
a second typeface, and it costs you the beat it occupies. The caption layer already says the
words, larger and better. **The graphic's job is to show what the words cannot.**

> **The one carve-out: an emotional beat may carry feeling instead of fact.**
>
> S2 puts a gold `Congratulations` over fireworks for two seconds. S4 floods the whole frame
> red on "SUPER" and green on "DISGUSTINGLY EASY". Neither carries a single unit of
> information, both are load-bearing, and the mute test as stated above would delete them.
>
> The test disqualifies *informational* decoration — a card that restates the audio. It does
> not disqualify a beat whose job is the feeling. **One per video**, it must be nameable as
> a specific emotion (relief, dread, triumph), and it must land on a beat where the script
> actually turns. If you cannot name the emotion in one word, it is decoration after all.

This skill previously said "graphics are instrumentation, not decoration" and that produced
dark plates with engraved headings — abstract dials measuring nothing, ledgers with empty
rows, a claim in quotes with a line through it. Every one of those restated the audio.
[TEARDOWN.md](reference/TEARDOWN.md) documents the failure and the three reels that
replace it. **Read it before you plan anything.**

---

## Brand overrides — read these before anything else

| Read | Holds |
|---|---|
| `brand/BRAND.md` | free-text house rules — voice, subject matter, banned visuals, CTA, sound |
| `brand/brand.json` | values — palette, fonts, canvas, fps, density, export |

**Precedence, lowest to highest:** repo defaults (this file) → `brand/` → the project's own
`tokens.css` / `MOTION-PLAN.md` → what the user says in this conversation.

Where `brand/` contradicts a default here, **`brand/` wins** — say so out loud rather than
silently following the default.

---

## Workflow

### 1. Read the spec

| Read | When |
|---|---|
| `brand/BRAND.md` + `brand/brand.json` | **first, always** |
| [reference/SAMPLES.md](reference/SAMPLES.md) | **always, before you plan.** the four reels torn down structurally — the persistent object, the motif, the beat map, the technique index |
| [reference/FRAME-CONTRACTS.md](reference/FRAME-CONTRACTS.md) | **always, before beat 2.** the four spatial architectures. Declaring one is mandatory |
| [reference/TEARDOWN.md](reference/TEARDOWN.md) | **always.** what actually performs, and why the old style failed — the *style* measurements behind SAMPLES.md |
| `../ig-hook/SKILL.md` + its references | whenever the first 0–8 seconds are not already locked |
| [reference/VISUAL-HOOK.md](reference/VISUAL-HOOK.md) | only when `ig-hook` selects **LOCKUP-FIRST** — SPG and the measured lockup spec |
| [reference/DEVICES.md](reference/DEVICES.md) | **always.** spoken line → what goes on screen |
| [reference/BLOCKS.md](reference/BLOCKS.md) | **always.** the 15 blocks |
| [reference/MOTION-LANGUAGE.md](reference/MOTION-LANGUAGE.md) | palette, docks, timing, easing, banned list |
| [reference/INTAKE.md](reference/INTAKE.md) | after the acquisition ladder — how to ask for the residue, and the MOTION PLAN template |
| [reference/PIPELINE.md](reference/PIPELINE.md) | before scaffolding, rendering, or handing off |
| `reference/tokens-viral.css` | the skin — copy via `node scripts/brand.mjs build` |

### 2. Gather the specifics — the step that decides the ceiling

The blocks that carry this style need **real material**: real screenshots, real view counts,
the actual five hooks, the actual document. **Ask for them.** One batched question:

> "For the strongest version of this I need: the two hook screenshots with their view
> counts, and whether you want your real profile on screen or a stand-in."

Getting two real screenshots is a two-minute favour and it is the difference between a reel
that proves something and one that asserts it. **Never invent a metric**, and never render a
container with placeholder contents — an empty numbered list shows the viewer less than a
plain talking-head frame, because it promises information and withholds it.

#### Go and get them — the acquisition ladder

For a long time this step ended at *"ask the creator, or build nothing."* That capped the
ceiling at whatever the user happened to volunteer, and three separate builds paid for it:
one shipped **five empty grey bars** standing in for hook copy the script never named;
another was abandoned half-built because a single screenshot never arrived; a third simply
**invented its two central numbers**, which is the worst outcome of the three.

**Work down this ladder. Ask the creator only for what genuinely only they have.**

| | Source | Use it for |
|---|---|---|
| 1 | **Already on disk** — `samples/`, `projects/*/assets/`, previous `renders/` | anything you have built or been given before |
| 2 | **Extract from footage** — `ffmpeg -ss <t> -i <file> -frames:v 1 out.png`, then crop. Or `/watch <url-or-path>` to pull frames from a competitor reel or the creator's own back catalogue | real thumbnails, real covers, real on-screen text, a still of the A-roll for a mockup slot. **This is how S3 and S4 got their third-party evidence** |
| 3 | **Capture a real interface** — Chrome automation (`mcp__claude-in-chrome__*`): open the real page, screenshot it | a real profile, a real dashboard, a real app screen. Far better than rebuilding one from memory, and it cannot look AI-generated |
| 4 | **Look it up** — `WebSearch` / `WebFetch` | real public figures: a real follower count, a real published statistic, a real product price |
| 5 | **Generate** — the `media-use` skill, or Higgsfield | textures, plates, a hand holding a phone, an icon, a background. **Never a metric** |
| 6 | **Ask the creator** — batched into one message, per `INTAKE.md` | only what is genuinely private: their own analytics, their own DMs, their own unpublished drafts |
| 7 | **Build nothing** | still the right answer sometimes — but now genuinely last |

Steps 2–5 are all installed and working on this machine and were, until now, mentioned in no
skill at all. That omission is most of the gap between the reference reels and this repo's
output.

**What does not change:** *never invent a metric.* Generating a texture is resourceful;
generating a number is fraud. And never render a container with placeholder contents — an
empty numbered list shows the viewer less than a plain talking-head frame, because it
promises information and withholds it.

If after the ladder the specifics still aren't available, pick a block that doesn't need them
(colour wash, tier stack, a chart whose *shape* is the claim) or build nothing.

### 3. PLAN THE WHOLE VIDEO FIRST — every beat, before you build anything

**Do not build a single composition until the entire video is planned beat by beat.**
Building as you go is how an edit ends up with six interchangeable cards: each one is a
locally reasonable answer to one sentence, and together they have no shape.

**Declare the frame contract first.** Before any beat table, one line naming which of the
four architectures in [FRAME-CONTRACTS.md](reference/FRAME-CONTRACTS.md) this video uses —
SPLIT-STAGE, NESTED-SCALE, TWO-WORLDS or OBJECT-OVER-GROUND — what owns the frame, what the
A-roll does, whether captions exist at all, and how you break it once at the payoff. The
contract determines how many scene files you write, so it cannot be decided later.

**A plan with no declared contract does not get built.**

Write `projects/<slug>/MOTION-PLAN.md` with **one row per spoken beat — not per graphic.**
Beats with no new graphic still get a row, saying what is on screen and why it is still the
right thing. That is what forces the ≥85% presence target to be met by *design* rather than
discovered as a gap afterwards.

| Column | What goes in it |
|---|---|
| Cue | timecode + the exact trigger word |
| He says | the line, verbatim |
| On screen | the **real object or measurement**, named specifically |
| Change | what is *different* from the previous beat — new object, element lit, number ticked, wash |
| Placement | `.cutaway` / `.beside--l/r` / background / inline — and **why that side** |
| Life | duration, and whether it persists dimmed afterwards |

Then read the **Change column top to bottom on its own.** That column is the video. If it
reads "card in, card out, card in, card out", the plan is a slideshow — go back and find
the object that should have persisted and mutated instead. If two rows describe the same
change, one of them is wasted.

Every row must survive the mute test. A row that reads "a panel showing THE ADVICE" fails.

*Fast mode:* "just do it" → still plan every beat, just in one line each. The quality bar
does not move; only the prose does.

### 3a. Plan the HOOK on its own, before the beat sheet

**The opening is not row 1 of the beat sheet. It is the `ig-hook` deliverable and must be
locked first.** Read `projects/<slug>/HOOK-PACKET.json` and build only the beats assigned to
HyperFrames. The packet defines frame zero, evidence IDs, changes through second eight,
caption mute windows, and the selected mode.

If the selected mode is **LOCKUP-FIRST**, read
[VISUAL-HOOK.md](reference/VISUAL-HOOK.md) and apply SPG, the 108/118px lockup, one proof
object, and the ≥2.5s readable hold. Other modes may use receipts, comparisons,
demonstrations, role-play, interface action, or a pattern break; do not force them into a
lockup.

### 3b. BE CREATIVE — the catalogue is a floor, not a ceiling

The 14 blocks describe what the references *happened* to build. They are a vocabulary, not
a menu to cycle through. **Decide what this specific idea deserves**, then find the block
that gets you there — and if none does, build the thing anyway and add it to the catalogue.

Creativity here is not decoration. It is choosing the object that makes the argument in one
glance:

- "my hook sucked" → not a sad-face icon. A **retention curve falling off a cliff**, real axes.
- "I tested 5 hooks" → not a numbered list. **Five real hooks in a real notes app**, then
  two struck through, then three surviving — the same object, three states.
- "one of them went viral" → not a rocket. **Three real thumbnails with real view counts**,
  one taking a gold outline.
- "everyone says this" → not a crowd icon. **A wall of a dozen near-identical reels.**

**Vary the device.** Three consecutive beats using the same block reads as a template even
when each one is individually correct. Alternate: object → measurement → environment →
object. Change the placement between adjacent graphics; two `.beside--r` cards in a row
make the second look like the first one failed to leave.

> **Carve-out: deliberate identical repetition is an argument, not a template.**
>
> S3 runs the same worksheet layout **three times**, pixel-identical, with three different
> niches — and that sameness *is* the proof that the structure generalises. Varying it would
> destroy the argument.
>
> The rule above bans *accidental* sameness: three beats that look alike because you reached
> for the same block three times. It does not ban repetition where the content varies, the
> repetition is announced (`EXAMPLE #2`, `EXAMPLE #3`), and the point being made is
> *"this works every time."* If you use it, say so in the MOTION PLAN — an unannounced
> repeat is still a template.

**The video should have a shape.** This is the frame contract, declared in step 3 and
specified in [FRAME-CONTRACTS.md](reference/FRAME-CONTRACTS.md). Commit to it and break it
exactly once, at the payoff. A reel where every beat is the same size and in the same place
has no climax.

### 3c. The AI-generated tell — what it actually looks like

"It looks AI-generated" is the most common complaint about this layer, and it is not vague.
It is a specific, enumerable set of tells. Check the plan against every one:

| Tell | What it looks like | The fix |
|---|---|---|
| **One layout for everything** | every graphic is a dark rounded rectangle, same width, same y | vary placement per beat; `.stage` is rare |
| **Generic container, generic contents** | a card headed `THE STRATEGY` with three bullet points | show the artefact, not a summary of it |
| **Placeholder content** | `Hook 1 / Hook 2 / Hook 3`, `Lorem`, `[Name]`, empty rows | get the real strings, or use a block that needs none |
| **Duplicate assets** | three "different" videos that are the same thumbnail | refuse to build it — see Banned |
| **Invented numbers** | `+247% growth`, a chart with no units | real figures from the creator, or the shape only |
| **Icon soup** | flying rocket / lightbulb / target glyphs | the object itself, never a metaphor for it |
| **Even, symmetrical, centred everything** | every element centred, equal margins, nothing overlapping | real UI is asymmetric; screenshots overlap and sit at angles |
| **Uniform motion** | everything fades in over 0.3s | ≥3 distinct eases; different verbs for different objects |
| **No state** | each graphic appears and disappears unchanged | persistent object + element highlight + cumulative build |
| **Smooth, clean, weightless** | no grain, no vignette, perfect edges | the references are grainy, heavily vignetted, and glow |

The single strongest antidote: **build from real material.** A real screenshot with a real
number on it cannot look AI-generated, because it isn't. Ask for the assets (step 2) — that
request is the highest-leverage thing in this entire skill.

### 3d. Follow the house style — do not invent a new one

The look is already decided: `reference/TEARDOWN.md` is the evidence, `MOTION-LANGUAGE.md`
is the spec, `tokens-viral.css` is the implementation. Compose from the existing classes.

A graphic that is beautiful and off-style is a defect. If a beat genuinely needs something
the style does not have, say so out loud and propose the addition — do not quietly ship a
different visual language in the middle of a reel.

### 4. Build — SCENES, not graphics

> **This repo used to say "one composition file per graphic." That rule is why the output
> was a slideshow, and it is gone.**
>
> Every reference reel is **one persistent object that mutates for the whole runtime**. S1 is
> a single Instagram profile that fills in from a grey skeleton across 45 seconds — roughly
> 13 pattern interrupts out of **one** composition. Building one file per beat structurally
> forbids that: each file can only appear, do its thing, and cut away.

**A video is 1–3 SCENES.** A scene is a single composition spanning many spoken beats,
carrying one persistent object through a **state machine**. Only when the frame contract
genuinely changes worlds (TWO-WORLDS) or the payoff needs a different object do you start a
second scene.

**How to build a scene**

- **Lay out the finished object first**, in CSS, with every field present. Then set the
  initial state to *skeleton* and reveal into it. The wireframe is not a loading state — it
  is the "before" half of every reveal, and it tells the viewer what is coming so each fill
  lands as a payoff.
- **Mark every beat with `tl.addLabel('<beat-name>', t)`** before the tweens at that cue. The
  labels are the state machine, they make a 45-second timeline navigable, and
  `analysis/motion-density.py` reports them.
- **The object accumulates. It never resets.** A field that has been filled stays filled. A
  row that has been struck stays struck. Recede it to ~0.3 opacity when another element owns
  the beat, and bring it back — never rebuild it.
- **Focus by brightness, not motion.** In a 45-second single composition, motion can never
  stop, so it cannot be the attention mechanism. The active element glows and everything
  else dims. This is how S1 holds a single frame for its entire runtime.
- **Use sub-compositions.** `hyperframes.json` supports nesting and **nothing in this repo
  has ever used it.** Scene = parent composition; each device inside it (the pyramid, the
  chart, the phone) = a sub-comp with its own timeline. This is what makes a 40-second single
  composition tractable instead of one 900-line file.
- **Guard the scrub.** A long accumulating timeline must survive backward seeking. Anything
  a `tl.call()` mutates — `textContent`, `src`, a class — is *not* rewound by GSAP, so a
  backward seek leaves the object in a state it was never in. Every callback that changes
  state needs a matching restore, keyed off `tl.time()`:

  ```js
  /* the forward mutation */
  tl.call(function () {
    document.getElementById('cap2').textContent = 'after';
    document.getElementById('tile2').classList.add('tile--sel');
  }, null, 5.14);

  /* the restore — without this, scrubbing back keeps the "after" state */
  tl.eventCallback("onUpdate", function () {
    if (tl.time() < 5.14) {
      document.getElementById('cap2').textContent = 'before';
      document.getElementById('tile2').classList.remove('tile--sel');
    }
  });
  ```

  One `onUpdate` handler per composition, holding one `if` block per callback beat, each
  restoring every property that beat touched. Renders are deterministic, but `snapshot`,
  `check` and the preview player all seek — an unguarded swap shows up as a graphic that is
  right in the render and wrong in every still you take of it.

**The reference implementation to beat** — the best composition this repo has produced —
is a single object with **8 cumulative states and 36 tweens**: a skeleton placeholder →
five sequential content reveals → the whole block recedes → pulses → two rows get struck
through → three rows resolve green. One file, one object, no exits, no second card. It was
an accident. Make it the default.

**Load-bearing rules** — breaking these breaks the render:

- Root div: `data-composition-id`, `data-width="1080"`, `data-height="1920"`, `data-start`,
  `data-duration`, `data-fps`. Standalone files put it directly in `<body>` — no `<template>`.
- `gsap.timeline({ paused: true })`, registered as `window.__timelines["<id>"]`, built
  **synchronously**.
- **Deterministic.** No `Math.random()`, no `Date.now()`, no `repeat: -1`, fixed `seed` on
  every `feTurbulence`.
- Asset paths are **root-relative** — `href="tokens.css"`, never `../tokens.css`.
- Lay the hero frame out in CSS first, then `gsap.from()` into it.
- **No exits *between* scenes** — the cut is the exit, and only a scene's final element may
  fade. **Inside** a scene the rule is different and stricter: elements persist, dim,
  desaturate, or are displaced. They do not disappear and reappear. An element that leaves
  and comes back is two graphics wearing one name.
- Overlays keep `background: transparent`; full-frame cutaways use `.cutaway`.
- Compose from the `.ig-*`, `.reel`, `.metric`, `.pyramid`, `.chart`, `.wash`, `.skel-*`,
  `.glow-*`, `.keep-*`, `.brace`, `.annot-*` classes in `tokens.css` — they already encode
  the correct metrics. Do not reinvent them per project. Most of that file is currently
  **unused**; read it before you write a line of CSS.

**Fonts.** Use `--font-ui` (Inter) inside any app mockup — the brand display face inside a
mockup breaks the illusion instantly. `Anton`, `Inter`, and `JetBrains Mono` auto-resolve
from the family name. A licensed face (`Europa Grotesk SH`, `TacticSans-UltIt`) must be
installed on the render machine and is matched by system font resolution.

> On `@font-face`: `PIPELINE.md` says never to write one, on the grounds that it kills the
> stylesheet. On hyperframes 0.7.108 that is **no longer true** — `lint` actively demands
> one for any family it cannot auto-resolve, and a composition using `@font-face` for a
> locally-installed OTF renders correctly with all custom properties intact (verified by
> render, 2026-08). Prefer auto-resolving families; use `@font-face` pointing at a local
> file only when a licensed face must be guaranteed, and **verify with a rendered frame.**

### 5. Check before rendering

```bash
npx hyperframes lint  projects/<slug>
npx hyperframes check projects/<slug>
python analysis/motion-density.py projects/<slug>/compositions/*.html   # the motion floor
npx hyperframes render projects/<slug> -c compositions/NN-block.html --format mov --fps 30 \
  -o projects/<slug>/renders/NN-block.mov
```

`--resolution` is rejected for alpha output; author at 1080×1920 and omit it.

> ### The motion floor — `analysis/motion-density.py`
>
> `lint` and `check` verify a composition is **correct**. Nothing verified it was **alive**,
> and the consequence was measured across everything this repo has shipped: **58% of every
> animated property was `opacity`**, zero rotation, zero depth, zero masks, a median of 9
> tweens per composition, and four compositions that were literally a card that fades in.
> Every one of them passed `lint` and `check`.
>
> The gate fails a composition on any of five hard metrics:
>
> | Metric | Floor |
> |---|---|
> | tweens (loop-expanded) | ≥ 25 per scene |
> | distinct timeline cues | ≥ 5 |
> | distinct animated properties | ≥ 6 |
> | fade share of all animated properties | ≤ 50% |
> | elements with depth (shadow / blur / mask / rotate / clip) | ≥ 1 |
>
> **Calibration, and it is worth knowing:** run against the existing corpus, **every single
> composition fails, including the best one.** `01-note-v2.html` clears tweens, cues and
> depth but its entire vocabulary is `opacity, scale, scaleX, color` — four verbs, 55% fades.
> The thresholds describe the target tier, not the current one. Do not lower them to make old
> work pass; that is the whole reason the old work looks the way it does.
>
> Widen the vocabulary with things that already exist in `tokens.css` and cost nothing:
> `filter` (blur, saturate, brightness, drop-shadow), `clipPath` and mask position for a real
> unmask, `rotation` on an object with weight, `backgroundColor`, `boxShadow`,
> `xPercent`/`yPercent`, `strokeDashoffset` and `strokeWidth` on drawn annotation, `attr`
> on an SVG `d` to morph one shape into another, and a proxy object driving `textContent`
> for counters.
>
> ⚠️ **Do not animate `letterSpacing`, `width`, `height`, `left`, `top`, `padding`, `margin`
> or `fontSize`** to pad the count. They reflow layout and snap to integer device pixels, so
> they stutter under the seek-by-frame capture engine — `hyperframes lint` fails them as
> `gsap_non_transform_motion`. Transforms and filters interpolate sub-pixel. If you want a
> letter-spacing effect, split to per-character elements and animate each glyph's `x`.
>
> **What it cannot see:** it reads the source, not the pixels. It cannot tell you the motion
> is *good*. It is a floor, not a ceiling, and it does not replace the next two steps.

> ### ⚠️ Re-rendering over a file Premiere has open fails at 90%
>
> Once a `.mov` is placed on the timeline, Premiere holds a lock on it. Re-rendering to the
> same path gets to *"Assembling final video"* and then dies:
>
> ```
> EPERM: operation not permitted, rename
>   '…/renders/.07-hook.hf-transaction-XXXX/07-hook.mov' -> '…/renders/07-hook.mov'
> ```
>
> **The old file is left intact on disk**, so anything you verify afterwards is the
> *previous* render, and the failure is easy to miss because the progress bar reaches 90%
> and the tail of the log looks normal. This is the same class of trap as `export_frame`
> reporting success and writing nothing.
>
> **Render to a new filename** (`07-hook-v2.mov`) and swap the clip in Premiere, or take the
> item offline first. And after any re-render, `ls -la` the output and check the
> **timestamp** before trusting a frame pulled from it.

**Then look at the pixels.** `check` will happily pass a graphic that is entirely wrong:
right structure, no meaning. Composite the render over a real A-roll frame with ffmpeg and
read it. The two defects that shipped last time — captions double-exposing, three graphics
absent — were both invisible to lint and obvious in a frame.

> ### ⚠️ `export_frame` can report success and write nothing
>
> Verified 2026-08 on this machine: `mcp__premiere-pro__export_frame` returns
> `{"success": true}` with a clean `outputPath` and **no file appears on disk**. Two
> separate failure modes:
>
> 1. **Backslash paths get mangled.** `C:\Users\you\vibe-editor\analysis\x.png` came back as
>    `C:Users\youvibe-editor\u000banalysis…` — the `\v` in `\vibe-editor` (and a `\f` in any
>    `\fonts` segment) were read as C escapes rather than path separators.
>    **Always pass forward slashes:** `C:/Users/you/vibe-editor/analysis/x.png`.
> 2. **Even with a clean path it may still write nothing** — the host's exporter is broken
>    here (the same fault that makes `encodeSequence` throw).
>
> **Never treat an `export_frame` success as verification.** After every call:
>
> ```bash
> test -f "<path>" || echo "export_frame LIED — fall back to ffmpeg composite"
> ```
>
> This matters more than it sounds: the previous build's QA checklist said "verified with
> pixels" for a step that was silently producing no pixels at all. **A verification step
> that cannot fail is not a verification step.**
>
> **Fallback that works:** composite the rendered overlay over a real A-roll frame with
> ffmpeg and measure that instead —
> ```bash
> ffmpeg -y -ss <t> -i <a-roll> -ss <t> -i <overlay.mov> \
>   -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];\
>   [1:v]format=rgba[ov];[bg][ov]overlay=0:0" -frames:v 1 out.png
> python analysis/measure.py out.png 0
> ```

### 5b. Compare against the corpus — the only check that asks if it is any *good*

Every other gate asks whether the work is correct. This one asks whether it is good, and it
is the cheapest honest signal available.

Composite the render over a real A-roll frame (the ffmpeg fallback above — `export_frame`
returns success and writes nothing on this machine), then **open a still from the matching
sample in `samples/` beside it** and answer three questions in `RESULT.md`:

1. **Does one object own the frame?** Or is this a card that arrived and will leave?
2. **Has it changed state since the last check?** Name the change. "It is still on screen"
   is not a change.
3. **Would a viewer read these two frames as the same tier?** If no, say which is missing —
   depth, real content, glow, density, or continuity.

Pull the sample still with `ffmpeg -ss <t> -i samples/<file> -frames:v 1 ref.png`, or
`/watch samples/<file>` for a spread. [SAMPLES.md](reference/SAMPLES.md) has a technique
index telling you which reel to compare against for which device.

Answering "yes, yes, yes" without having looked at both images is the failure mode this step
exists to prevent. **A verification step that cannot fail is not a verification step.**

### 6. Render and hand off

Render **at the sequence fps**. Write `renders/IMPORT.md` — file, cue, block, track, blend.

---

## Occupying the frame

Graphics in this style are **big**, and they are almost never a bar across the bottom.

| Mode | Share of graphic time | Class | Geometry |
|---|---|---|---|
| **Full-frame takeover** | **~40%** | `.cutaway` | `inset: 0` — the graphic *is* the shot; footage gone, or embedded inside the graphic |
| **Beside the head** | **~30%** | `.beside--l` / `--r` | `top: 200px`, `width: 432px` (40% of frame), inset 56px on its side |
| **Background replacement** | **~15%** | `.wash`, `.wall` | full frame, *behind* the subject |
| **Chest-height inline object** | **~10%** | in the caption slot | a DM bar, a `👁 496` counter — small, centred, at caption height |
| **Full-width bottom band** | **~5%** | `.stage` | y 1180–1560. **Rare.** |

Two corrections that matter more than anything else in this file:

**`.stage` is not the default.** In the references a full-width bottom band appears *once* —
S3's retention card, in the hook, for two seconds. An edit where every graphic is a dark
rounded rectangle pinned across the bottom is the single most recognisable failure mode of
this system, and it is what happens when `.stage` is the only mode with coordinates. Reach
for `.cutaway` or `.beside` first and justify `.stage` when you use it.

**Pick the side before you build.** `.beside` goes in whichever half of the frame the
subject is *not* occupying. Pull the A-roll frame at the cue timecode and look at it — a
`.beside--r` on a shot where he leans right is a graphic on his face.

### Opacity is load-bearing

Reference graphics are **opaque**, with a visible edge and a coloured bloom. A graphic
rendered semi-transparent over footage reads as a rendering fault, not as a design choice.

- On-screen and the current subject → **full opacity**.
- On-screen but no longer the subject → `.dim` (30%). It stays crisp; it just recedes.
- There is no third state. Nothing renders at 40–60% "so the footage shows through."

> # Every SURFACE is 100% opaque. No exceptions.
>
> A surface is anything the viewer reads content off: a card, a panel, a plate, a pill, a
> badge, a sheet, a mockup screen, a button. **Write surfaces as hex, never `rgba()`.**
>
> `rgba(22,22,26,.96)` looks opaque in a browser against a dark page and is visibly
> see-through over a lit face. 96% is not "basically solid" — you can read an arm through
> it. This shipped on a follow card and was spotted instantly.
>
> **Alpha is legal in exactly four places, and none of them is a surface:**
>
> | Legal | Example |
> |---|---|
> | A scrim or gradient over an image **inside** the graphic | `.reel__scrim`, a cover's bottom fade |
> | Hairline strokes and rules | `border: 1px solid rgba(255,255,255,.10)` |
> | Glow, bloom, shadow | `drop-shadow`, `text-shadow` |
> | The semantic colour washes | `.wash--bad` / `.wash--good` |
>
> Element-level `opacity` for entrance tweens and the `.dim` state is fine — that is
> animation, not fill.
>
> **Audit before you render:**
> ```bash
> grep -nE "background[^;]*rgba\(" compositions/*.html tokens.css | grep -v gradient
> ```
> Every hit must be one of the four legal cases. Anything else is a defect.

### A graphic must not restyle the footage it sits on

> **No full-frame scrim behind a bounded graphic.** If the graphic needs ground to sit on,
> the ground belongs *inside the graphic's own bounds* — not spread across the whole frame.

A recurring temptation is to darken the whole frame so a cutaway "reads as its own space".
It does the opposite: the viewer sees **the video** get darker, not a graphic arrive. It is
the same failure as the colour wash tinting the subject's face — a graphic behaving like a
colour grade.

Measured on a real build: a `radial-gradient(… rgba(0,0,0,.90) 100%)` behind a profile grid
dropped mean frame brightness from **62 to 14** and held it there for 9.9s — a third of the
reel. The fix was to delete the wash and give the mockup an opaque bounded panel, which is
what a real app screen is anyway: **a panel, not a filter.** Brightness went to 54–60
against neighbours at 61–64, and the graphic read better, not worse.

**Check it, don't eyeball it.** Sample mean luma across the reel; a graphic beat should sit
within roughly ±25% of the surrounding footage:

```bash
ffmpeg -v error -ss <t> -i <preview.mp4> -frames:v 1 \
  -vf "scale=1:1,format=gray" -f rawvideo - | xxd -p | head -c2
```

The legitimate exceptions are the **semantic colour washes** (`--sig-down` / `--sig-up`),
which are meaning, are brief, and are shaped with a large clear core so the subject stays
neutrally lit. A neutral black scrim is never meaning — it is always styling.

---

## Caption arbitration — only one text layer at a time

> **A graphic that carries its own words and the burnt-in caption never occupy the frame
> at the same time. One of them yields.**

This is the single most common reason a technically-correct build still looks cheap, and it
is invisible to every automated check — both layers are individually perfect, and together
they are clutter.

Measured across the reference reels: whenever a content card with its own baked-in text is
on screen (S3's two reel covers at 0:20–0:30, its annotated mockup, its hook lockup), **the
caption track is empty.** The card's own text carries the beat. When the caption is running
big and centred, there is no competing text on screen. They alternate. They never stack.

### Who yields

| On screen | Yields |
|---|---|
| **Hook lockup** | caption, always — the lockup *is* the caption |
| **Content card with its own caption** (a reel cover, a screenshot, a DM) | caption |
| **App UI whose text is chrome** (tab bar, stat row, nav, buttons) | nobody — captions over chrome are in-style |
| **A chart, a counter, a wash** | nobody — no competing words |
| Bare footage | nothing to arbitrate |

The distinction is **content vs chrome**, not graphic vs no-graphic. A caption over
Instagram's tab bar is fine and the references do it. A caption over a reel cover's own
headline is two headlines.

### How to make it yield

The caption composition owns this, not the graphic — hand `ig-captions` the windows:

```
CAPTION MUTE WINDOWS
  0.00 – 4.50   hook lockup
  20.27 – 30.17 trial reel covers carry their own copy
```

Write these into the MOTION PLAN as their own block, because the caption pass runs before
the graphics pass and cannot discover them on its own.

**Do not solve this by shrinking the caption or moving it.** A small caption tucked beside a
card is still two text layers; it just looks timid as well as cluttered. It goes away.

---

## Content cards — the anatomy that reads as real

A "content card" is a rebuilt piece of real content: a reel cover, a post, a screenshot.
It is the highest-leverage device in the whole style (`TEARDOWN.md §2.2`) and it is easy to
build a version that is structurally right and still looks like a slide.

Measured off S3's two comparison covers:

| Property | Value | Why |
|---|---|---|
| Corner radius | **~34px** @1080 | 20px reads as a web thumbnail, not a phone |
| Aspect | **3:4** | what a cropped cover actually is |
| Image brightness | **`brightness(1.30) contrast(1.10)`** | reference covers are bright; a dim room reads as placeholder art |
| Its own caption | **small (~26px), low, LEFT-aligned**, in `--font-ui` | it belongs to the artefact, not to your reel |
| Caption scrim | bottom-up black gradient | what a real cover uses |
| View badge | **light frosted pill, dark digits**, bottom-left, inset 20px | a dark badge sinks into a dark thumbnail |
| Loser treatment | **`grayscale(1) brightness(.74)`** | desaturate, don't fade |
| Winner | 5px `--accent` outline | — |

**Two failures to avoid, both seen in this repo's own build:**

- **Copy centred across the middle of the cover.** Real covers put their text low and left,
  over a scrim. Centred text across the middle of a thumbnail is a stock-photo caption.
- **Three cards crammed abreast.** Under ~300px wide, a cover cannot carry legible copy
  *and* a badge. Show **two** cards at ~380–420px, or show one at a time and let the third
  arrive. Fewer, bigger, brighter beats more, smaller, dimmer every time.

### The one exception: a rebuilt profile grid

**A recreated Instagram profile grid is app UI, not a set of content cards**, and 3-across
is correct there — it is what the app actually looks like, and the viewer recognises it
because of the 3-across layout, not despite it. The ~380px minimum does not apply.

What *does* apply, and is what makes a 325px tile work:

- The cover copy goes on a **solid plate with a hard edge** — a filled rectangle hugging the
  text, anchored top-left, in heavy caps. S1 does this in red as its own cover branding.
  Use a neutral near-black plate unless red is free in your palette, because red is
  load-bearing (`= bad`) in this system.
- **Floating text over a soft gradient is what fails at this size.** The plate is the whole
  difference between crisp and mushy — not the font size.
- The badge still needs to be the light frosted pill; a dark badge on a 325px dark tile is
  invisible.

So: **standalone comparison cards ≥380px and no more than two; a profile grid may be
3-across at ~325px if every cover label sits on a plate.**

---

## Density — the graphic layer is the default state of the frame

This file previously said *"~40% of runtime should have no graphic at all."* **That number
was invented.** It was never measured off the references, it contradicted this repo's own
`TEARDOWN.md §5` and `ig-pacing`, and a build that hit it faithfully produced the reel the
user described as "the visuals are barely there". See `analysis/DEEP-ANALYSIS.md §7.2`.

**Measured across the three references:**

| | S1 | S2 | S3 |
|---|---|---|---|
| Runtime with **no** graphic on screen | **~0%** | ~10% | ~15% |
| Distinct visual events | 32 | 31 | 34 |
| Mean interval between events | 1.4s | 1.5s | 1.5s |
| Longest beat with nothing changing | ~2.0s | ~2.0s | ~2.0s |

S1 never shows a bare talking head — its profile stage is present in **every frame of the
reel.**

> **The working rule: ONE OBJECT is on screen for ≥85% of runtime, it changes state at
> least every ~1.5s, and nothing holds unchanged longer than ~2s. Bare footage is the
> exception you spend for emphasis, not the resting state.**

The emphasis on *one object* is the whole point and it was missing. "A graphic is on screen
≥85%" is satisfiable by twelve unrelated cards in a row, which is exactly what this repo
built. **≥85% presence of a persistent, mutating object** is a completely different
instruction and is what the references actually do.

This is cheaper than it sounds, because **most of those events are state changes on one
object that is already on screen**, not new graphics. One persistent object mutating 20
times costs one composition. Do not read "≥85%" as "build 12 separate cards" — read it as
"build one or two objects and keep them alive."

---

## The three mechanisms that do most of the work

These are the devices carrying the reference reels, and none of them appeared anywhere in
the last build. They are not optional flourishes — they are the style.

### 1. Element-level highlight on a persistent object

A graphic is **placed once and then mutated, one element at a time, in sync with the exact
word being spoken.** Everything not currently being discussed holds perfectly still and
stays fully rendered.

S1's entire 45 seconds is one object — a rebuilt Instagram profile — cycling this 20+
times: avatar lands, ring turns green, name resolves, bio line 1, bio line 2, link,
highlight 1, highlight 2, highlight 3, scroll down, post 1, post 2, post 3.

**Only one element moves at a time. Never two.** That is what makes the moving one read as
the answer to the sentence.

### 2. The pre-reveal white flash

Before real content lands, its placeholder turns **pure white and blank for a beat**, then
the real content resolves into it.

```
grey skeleton bar  →  white blank bar (flash)  →  real text
```

This is the visual equivalent of "and here's the thing": it puts the viewer's eye on the
exact spot *before* there is anything to read there, so the content arrives somewhere they
are already looking. It appears on **every single reveal** in S1. Skipping it is why a
progressive build can be technically correct and still feel flat.

### 3. The cumulative build

A recurring graphic **adds** on each appearance and never resets. S1's tier pyramid is
visited six times and gains exactly one tier per visit, keeping all previous tiers. The
profile at 00:33 still contains everything added at 00:02.

If a graphic appears twice showing the same state, one of the two appearances is wasted.

---

## Worked example — the same script, wrong and right

Script: *"Most people will tell you to just write a good hook. But how do you know if your
hook's actually good? I used to waste so much time on a video people didn't even watch,
cuz the hook sucked. So write 5 different hooks, eliminate 2, and record each as the trial
reel."* (32s, one locked-off medium shot, no B-roll.)

**What the last build did** — six independent cards, all `.stage`, 41% of runtime bare:

| Cue | Graphic | Why it failed |
|---|---|---|
| 1.97 | a reel card with `?` for the view count | bottom band, 26% width, translucent, unreadable |
| 5.70 | retention chart | bottom band again |
| 11.37 | notes app with 5 hooks | bottom band again |
| 13.90 | comment sheet | bottom band again |
| 21.00 | three "hook" cards | **three copies of the same shot of him** |
| — | 0–2s, 8.8–11.4s, 18–21s, 28–32s | nothing on screen at all |

**What it should be** — one persistent object, mutating, plus two takeovers:

| Cue | Placement | What happens |
|---|---|---|
| 0.0 | `.beside--r` | the **hook-drafts note** appears as a real Notes-app card, five grey `.skel` rows. It is on screen from frame one and does not leave until 21s. |
| 2.3 | ELEMENT HIGHLIGHT | on *"how do you know"* — row 1 FLASHes white, then resolves to a real hook string |
| 4.2 | `.cutaway` | on *"waste so much time"* — full-frame retention curve, labelled axes, red cliff. Takes the whole shot for 2s, then back. |
| 6.5 | `.beside--r`, `.dim` | the note returns dimmed while he talks about the past |
| 11.4 | ELEMENT HIGHLIGHT ×5 | *"write 5 different hooks"* — rows 2–5 FLASH and resolve one per beat, ~0.7s apart. Four events, one composition. |
| 17.5 | ELEMENT HIGHLIGHT | *"eliminate 2"* — two rows strike through red **in place**; the other three stay lit |
| 21.0 | `.cutaway` | *"record each as the trial reel"* — the three surviving hooks become three real reel cards. Needs three **different** thumbnails; if only one exists, use CONTENT + METRIC on one instead |
| 28.0 | `.beside--l` | end card: the follow button pressed, swapping to Following |

Same script, same footage, **~92% graphic presence, ~14 visual events, two compositions
instead of six.** The difference is not more work — it is one object kept alive instead of
six cards fading in and out of the same bottom band.

---

## Tuned by render — things only a composited frame will tell you

Every item below passed `check` and was wrong. They are listed because each one
cost an iteration, and none is discoverable without compositing the overlay over
a real A-roll frame and looking at it.

### The colour wash must leave the subject clear

In the references the wall floods **behind** the presenter and his face stays
neutrally lit. A 2D alpha overlay cannot get behind him, so a full-frame flood
tints his skin and reads as a **colour filter**, not as lighting — the single
most obvious tell that a wash was added in post.

Shape it as a wide edge-flood with a large untouched core:

```css
/* subject stays clear to ~54%, colour only builds at the edges */
radial-gradient(ellipse 96% 62% at 50% 44%,
  rgba(235,4,8,0) 54%, rgba(235,4,8,.30) 82%, rgba(120,0,0,.62) 100%)
```

A first attempt at `ellipse 76% 50% … .46 at 76%` turned his whole face red.

**And the wash is always a PAIR.** A red flood on "the hook sucked" with no green
counterpart is just a coloured light. The good half must land within a few
seconds — in the test reel, red at 8.00 ("sucked") and green at 10.23 ("farming
views").

### Rebuilt app UI is the workhorse — if the plan has none, the plan is wrong

~60% of reference graphic time is a recreated interface. The first build of the
test reel had none: three cards on a dark plate, which read as a slide. Replacing
it with the **actual Instagram profile grid** — header, stat row, tab bar, 3:4
tiles, view badges — changed nothing structurally and everything perceptually,
because the viewer recognises it in half a second.

### A graphic sharing the frame with captions must clear the band with its CONTENT

Chrome may sit under the caption; content may not. The grid was authored with its
tiles at y934 and the caption band (920–1130) landed on the thumbnails. Moving the
screen down so the **tab bar** takes the caption and the tiles start at y1008
fixed it. Captions over app chrome is in-style — S2 burns captions straight over
the IG feed.

### No header chrome — and that has nothing to do with opacity

The reference chart has **no header chrome**, sits at chest height overlapping the
body, and puts nearly all its weight in the line's bloom. An opaque card with an
`AUDIENCE RETENTION` heading reads as a dashboard widget.

> ⚠️ **This section used to say "~74% keeps it glassy and legible." That was wrong and it
> has been removed.** What made the card read as a widget was the *header chrome and the
> placement*, not the fill. Translucency was the wrong lever pulled for the right problem,
> and it propagated: cards, plates, badges and the CTA panel all ended up at 82–96% alpha,
> and the footage showing through them is exactly what makes a graphic look cheap. Fix the
> chrome and the placement. **The fill stays solid.**

### Brighten dim source material

Reference reel covers are bright and high-contrast, and that is most of why they
read as real content rather than as placeholder art. Footage shot in a dim room
needs `filter: brightness(1.36) contrast(1.12) saturate(1.10)` on the thumbnail to
sit in the same world.

### The loser dims, it does not disappear

A comparison's losing side goes to **~40–55%**. At 18% it read as a bug. The
confident move is to make the loser quiet, never ugly and never invisible.

### Counters trickle before they spike

Three badges sitting on `0` for 2.5s was the longest static beat in the reel.
Views arriving as a trickle (`9 / 24 / 13`) and then surging is both more truthful
and fills the beat. Counters that all land at the same instant read as a chart;
staggered arrival reads as results coming in.

---

## Hard limits

- **Palette:** ground / white / one meaning per colour. `--sig-down` red = bad, `--sig-up`
  green = good, `--accent` gold = the metric or the winner. More than one may share a frame
  **only when each carries a different meaning**.
- **Type:** `--font-ui` inside mockups, `--font-display` for headlines, `--font-mono` with
  `tabular-nums` for every number that changes. **No serif anywhere in this skin.**
- **Motion:** entrance 0.28–0.42s, hold ≥0.8s, no exits. ≥3 distinct eases, 60–120ms
  staggers, 1–2 movers at a time. Never bounce, elastic, or back. `linear` only for a
  continuously scrolling wall.
- **Motion floor:** ≥25 tweens, ≥6 distinct animated properties, ≤50% fades, ≥1 element with
  depth, per scene. Enforced by `python analysis/motion-density.py` — not by eye.
- **Structure:** 1–3 SCENES per video, not one file per graphic. One persistent object per
  scene, carried through a labelled state machine.
- **Contract:** one of the four in `FRAME-CONTRACTS.md`, declared before any build.
- **Density:** see below. **ONE OBJECT is on screen ≥85% of runtime.**
- **State persists** across a progressive build. Never reset to skeleton.
- **Zero UI chrome:** no watermark, no follow banner, no progress bar, no slide counter.
- **Copy is the creator's voice.** Do not grammar-correct.

## Banned

- Panels whose content is a headline and a rule — that is a caption
- Restating the caption in a second typeface
- Numbered empty slots standing in for content that was never named
- Invented metrics, fake screenshots, fabricated axis values
- **A comparison built from duplicate assets while pretending they are different.** The one
  carve-out is verified sameness as evidence, declared with
  `comparison.samenessIsClaim: true` and provenance in `HOOK-PACKET.json`.
- **A full-frame scrim, vignette, or dark wash behind a bounded graphic** — the ground goes inside the graphic's own bounds. The viewer must never see the video get darker (see *A graphic must not restyle the footage it sits on*)
- **`rgba()` on any surface** — cards, panels, plates, pills, badges, sheets, mockup screens, buttons. Surfaces are hex. `.96` is not "basically solid"; you can read an arm through it (see *Opacity is load-bearing*)
- **A handle, display name, or avatar copied from a reference reel in `samples/`** — those are real people's accounts. Every mockup carries `creator.handle` from `brand/brand.json`. Copy the *layout* from the references, never the identity.
- **A burnt-in caption over a content card that carries its own words** — see *Caption arbitration*
- **Ambient hook motion that advances nothing.** Hook motion must reveal, compare,
  demonstrate, annotate, or reframe; Lockup mode still holds still after its stamp.
- **A Lockup-mode hook with no power word**, or with the power word set in white
- **Three-plus content cards abreast**, or copy centred across the middle of a cover
- **Every graphic docked to the same bottom band**
- Unlabelled charts
- Serif micro-labels, engraved tracking, "instrument" styling
- Emoji as decoration, flying icons, arrow doodles
- Light/white cards over footage (real app UI in dark mode is fine)
- **`box-shadow` as generic elevation on a flat panel** — a dark rounded rectangle with a
  soft drop shadow under it is a Bootstrap card, and it reads as one. Depth is *required*
  elsewhere: an object meant to read as physical (a card held at an angle, a device, an
  artefact lifted off the ground, a screenshot overlapping another) should carry a real
  shadow. The distinction is whether the shadow is describing a thing with weight or
  decorating a container. The motion floor requires at least one element with depth per
  scene — spend it on an object, not a panel.
- Glow so bright it clips
- `Math.random()`, `Date.now()`, `repeat: -1`, unseeded `feTurbulence`
- Any graphic that fails the mute test

## Self-check — before anything renders

- [ ] **A frame contract is declared** and named in the MOTION PLAN — one of the four in `FRAME-CONTRACTS.md`, with the one break identified
- [ ] **The video is 1–3 scenes, not N graphics** — each scene one persistent object through a labelled state machine
- [ ] **`python analysis/motion-density.py` passes on every composition** — ≥25 tweens, ≥6 properties, ≤50% fades, ≥1 depth element
- [ ] **Real material was pursued down the acquisition ladder** before anything was asked for or omitted — nothing on screen is a placeholder
- [ ] **`HOOK-PACKET.json` validates** and the selected 0–8 second candidate passed its storyboard gate
- [ ] **Frame zero shows verified proof, consequence, or action** — not a topic label
- [ ] **The second beat advances by second five** — not generic bridge copy
- [ ] **If mode is LOCKUP-FIRST:** SPG, centred ~108/118px, line 2 larger, bloom + halo, one stamp then ≥2.5s hold
- [ ] **Only one text layer at a time** — caption mute windows written into the MOTION PLAN for the hook and for every content card carrying its own copy
- [ ] **Every surface is opaque hex, zero `rgba()` fills** — verified with the grep in *Opacity is load-bearing*, not by eye
- [ ] **No graphic darkens the frame** — mean luma sampled across the reel; every graphic beat sits within ~±25% of the surrounding footage
- [ ] **Every account shown in a mockup uses `creator.handle` from `brand/brand.json`** — grep the compositions for any handle appearing in `samples/`
- [ ] **Content cards: radius ~34px, brightened, own caption low-left over a scrim, light frosted badge, loser desaturated not faded**
- [ ] **No more than two content cards abreast** — fewer, bigger, brighter
- [ ] **The WHOLE video was planned beat by beat before anything was built**
- [ ] **The Change column reads as a build, not as card-in/card-out**
- [ ] **Checked against every row of the AI-generated tell table (§3c)**
- [ ] **The device varies — no three consecutive beats using the same block**
- [ ] Every graphic survives the mute test
- [ ] Every graphic shows a real object or a real measurement
- [ ] No invented numbers; every metric is one the creator supplied
- [ ] Charts have labelled axes with real units
- [ ] App mockups use `--font-ui`, not the brand display face
- [ ] Colour is carrying meaning, not styling
- [ ] **A graphic is on screen ≥85% of runtime; no graphic-free stretch over ~2s**
- [ ] **Placement is mixed — not every graphic docked to `.stage`**
- [ ] **`.beside` is on the side of frame the subject is not occupying** (A-roll frame pulled and checked)
- [ ] **Every graphic renders opaque; only a non-subject graphic is dimmed, to 30%**
- [ ] **The persistent object mutates element by element; one mover at a time**
- [ ] **Reveals use the pre-reveal white flash**
- [ ] **No comparison fakes difference with duplicate assets** — verified sameness-as-proof is declared in the Hook Packet
- [ ] **At least one rebuilt app UI** — if the plan has none, it is wrong
- [ ] **Every wash is a bad/good PAIR and leaves the subject's face untinted**
- [ ] **Graphic CONTENT clears the caption band** (chrome under it is fine)
- [ ] **The losing side of a comparison sits at 40–55%, not invisible**
- [ ] Nothing over the face; clear of the caption band and safe zones
- [ ] Progressive builds persist state and each appearance adds something new
- [ ] Entrances 0.28–0.42s, holds ≥0.8s, no exits, no bounce
- [ ] Deterministic: no random, no clock, no infinite repeat
- [ ] **Composited over a real A-roll frame and looked at**

## When the request isn't a graphic

| Ask | Owner |
|---|---|
| cut footage, remove silence | `ig-cut` |
| captions, styling or timing | `ig-captions` |
| music, SFX, ducking | `ig-sound` |
| pacing, zoom pulses, shot scale | `ig-pacing` |
| export, QA | `ig-delivery` |
| plan a whole edit | `ig-reel` |
