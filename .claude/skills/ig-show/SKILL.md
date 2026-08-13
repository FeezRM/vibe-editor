---
name: ig-show
description: "Designs and builds the SHOW layer of a short-form video — the motion graphics that visually represent what is being said — in a locked house style with two skins: ANALOG (vintage brass instrument: dials, needles, tick scales, engraved linework, bone and brass on near-black with contour texture) and DIGITAL (terminal readouts, meters, diffs). Twenty named blocks, nine reveal verbs, and a spoken-idea-to-visual-device lookup table, built as HyperFrames HTML compositions and rendered to alpha .mov / .mp4 for Premiere Pro. Works brief to questions to approved MOTION PLAN to build to render to Premiere import sheet. This is step 4 of the six-step editing SOP and the one that matters most. Use whenever the user wants to: make or design a motion graphic, visually show or represent what they are saying, add a graphic/overlay/lower-third/animated text to a reel, visualize a number or stat, build an animated counter, dial, gauge, chart, diff, terminal, comparison, or end card, style or restyle reel graphics, plan the graphics for a script, or ask what a graphic should look like or why their graphics look AI-generated. Triggers: motion graphic, motion graphics, show this visually, visualize this, animate this, animated overlay, reel graphic, lower third, kinetic text, animated number, counter animation, dial, gauge, stat graphic, chart for my reel, graphics for this script, hyperframes, premiere overlay, alpha overlay, b-roll graphic, icon pop up, make it look premium, looks ai generated, what should this graphic look like."
---

# IG SHOW — visually represent what is being said

**Step 4 of the editing SOP, and the one that separates a good edit from a premium one.**

> "You wanna visually show as much as you can in your video. The main thing we want to do
> with our editing is amplify the viewer experience."

This skill owns the **look** and the **build** of every designed element. The cut belongs
to `ig-cut`, captions to `ig-captions`, audio to `ig-sound`, pacing to `ig-pacing`. When a
request needs several, produce the edit blueprint in `ig-reel` and the MOTION PLAN here,
and cue everything off the same timecodes.

---

## Brand overrides — read these before anything else

This repo ships defaults. **Whoever cloned it may have replaced them.**

| Read | Holds |
|---|---|
| `brand/BRAND.md` | free-text house rules — voice, subject matter, banned visuals, CTA, sound |
| `brand/brand.json` | values — palette, fonts, canvas, fps, density, export |

**Precedence, lowest to highest:**
repo defaults (this file) → `brand/` → the project's own `tokens.css` / `MOTION-PLAN.md`
→ what the user says in this conversation.

Where `brand/` contradicts a default below, **`brand/` wins** — and say so out loud rather
than silently following the default. If neither file exists, use the defaults here.

Values in `brand.json` are already compiled into `brand/tokens.css`; regenerate with
`node scripts/brand.mjs build` after editing. Never hand-edit `brand/tokens.css`.

---

## The one rule everything else serves

> **Graphics are instrumentation, not decoration.**

Every graphic on screen looks like a readout from something that is *measuring*: a dial, a
counter, a delta, a curve, a scale, a ledger, a log line. Not a sticker, not a swoosh, not
a highlight blob.

**Before building anything, answer: what does this measure, prove, or compare?**
No answer → say so and recommend a cut, a push-in, or a caption hit instead. A graphic
that exists to fill a static shot is the problem, not the fix.

The corollary matters as much: **plain explanatory lines get no graphic at all.** Most
runtime is unadorned talking head. That scarcity is what makes each graphic land.

---

## Workflow — do not skip a step

### 1. Read the spec

| Read | When |
|---|---|
| `brand/BRAND.md` + `brand/brand.json` | **first, always.** the user's own house rules — they beat everything below |
| [reference/DEVICES.md](reference/DEVICES.md) | **always.** which graphic for which spoken line |
| [reference/MOTION-LANGUAGE.md](reference/MOTION-LANGUAGE.md) | **always.** palette, type, docks, timing, easing, banned list |
| [reference/BLOCKS.md](reference/BLOCKS.md) | **always.** the 20 named blocks. pick from these |
| [reference/TEXTURE.md](reference/TEXTURE.md) | **always.** the craft layer — why it reads premium and not generated |
| [reference/INTAKE.md](reference/INTAKE.md) | before asking questions or writing a plan |
| [reference/PIPELINE.md](reference/PIPELINE.md) | before scaffolding, rendering, or handing off |
| `reference/tokens-analog.css` · `tokens-digital.css` | copy one into the project as `tokens.css` |
| [reference/PIPELINE.md §1](reference/PIPELINE.md) | **fonts.** licensed faces must be installed on the machine; never write `@font-face` |

Do not improvise a visual language. Every graphic is one of the 20 blocks or a deliberate,
justified variant.

### 2. Ask — once, batched

Seven questions in [INTAKE.md](reference/INTAKE.md). Skip any the brief answers. **Never
ask about anything already locked** — fonts, easing, layout, safe zones, "what vibe."

The two that can't be defaulted safely: **accent colour** and **sequence fps**.

### 3. Write the MOTION PLAN — and get it approved

Template in [INTAKE.md](reference/INTAKE.md). Per graphic: what it proves, cue timecode
**and trigger word**, block, dock, duration, anatomy, texture line, and a **beat sheet with
timings and eases to two decimals**. Save to `projects/<slug>/MOTION-PLAN.md`.

**Do not write HTML before it's approved.** A plan costs a minute to change; a built
composition costs twenty.

*Fast mode:* "just do it" → collapse to one line per graphic and go. The quality bar
doesn't move; only the approval step shrinks.

### 4. Build

Scaffold per [PIPELINE.md §1](reference/PIPELINE.md), then **one composition file per
graphic** so any single graphic can be re-cut without touching the others.

Load-bearing rules — breaking these breaks the render:

- Root div: `data-composition-id`, `data-width="1080"`, `data-height="1920"`,
  `data-start`, `data-duration`, `data-fps`. Standalone files put it directly in `<body>`
  — **no `<template>` wrapper**.
- `gsap.timeline({ paused: true })`, registered as `window.__timelines["<id>"]`, built
  **synchronously**.
- **Deterministic.** No `Math.random()`, no `Date.now()`, no `repeat: -1`, fixed `seed` on
  every `feTurbulence`.
- **Layout the hero frame in CSS first**, then `gsap.from()` into it.
- Asset paths are **root-relative** — `href="tokens.css"`, never `../tokens.css`.
- **No exit animations.** The cut is the exit. Only the final element may fade.
- Overlays keep `background: transparent`; cutaways add `class="card"`.
- **Never write `@font-face`.** HyperFrames injects its own; a hand-authored rule kills the
  whole stylesheet (symptom: everything renders black serif). The licensed faces must be
  installed on the render machine and are matched by family name.

### 5. Check before rendering

```bash
npx hyperframes lint .          # structure — no Chrome needed
npx hyperframes check .         # lint + runtime + layout + contrast (needs Chrome)
npx hyperframes snapshot . -c compositions/NN-block.html --at 0.2,0.6,1.4,2.4
```

**Read the snapshots.** Then run the checklist in [MOTION-LANGUAGE §9](reference/MOTION-LANGUAGE.md).
`check` catches JS errors and overflow. It will happily pass a graphic with a fallback
font, bounce easing, two accent elements, or a white box over the footage.

### 6. Render and hand off

```bash
# overlay — alpha
npx hyperframes render . -c compositions/02-dial.html \
  --format mov --resolution portrait --fps 30 --quality high -o renders/02-dial.mov

# cutaway
npx hyperframes render . -c compositions/01-hook-slam.html \
  --format mp4 --resolution portrait --fps 30 --quality high -o renders/01-hook-slam.mp4
```

Render **at the sequence fps**, not the composition default. Then write
`renders/IMPORT.md` — file, cue, block, track, blend ([PIPELINE.md §6](reference/PIPELINE.md)).

**Rendering works on macOS, Windows, and x64 Linux.** Run `npx hyperframes doctor` once
per machine. Only ARM64 Linux and restricted agent shells genuinely can't render; in the
second case re-run in a plain terminal. If you truly can't: author, lint, write the plan
and import sheet, hand back exact commands. **Never imply a render happened** — and never
hand back commands the machine you're on could have run.

---

## The 20 blocks

Full anatomy in [BLOCKS.md](reference/BLOCKS.md). **S** both skins · **A** analog · **D** digital.

`HOOK SLAM`ˢ · `THE DIAL`ᴬ · `THE METER`ᴰ · `THE COUNTER`ˢ · `THE DELTA`ˢ ·
`THE VERSUS`ˢ · `THE CURVE`ˢ · `THE SCALE`ᴬ · `THE STACK`ˢ · `THE CHIP`ˢ ·
`THE RAIL`ˢ · `THE ANNOTATION`ᴬ · `THE REDACTION`ˢ · `THE DIFF`ᴰ · `THE TERMINAL`ᴰ ·
`THE MOCK UI`ˢ · `THE IMPACT`ˢ · `THE PROOF PANEL`ˢ · `THE LEDGER`ᴬ · `THE END CARD`ˢ

Nine reveal verbs, and nothing else:
**SLAM · WIPE · COUNT · FILL · SWEEP · DRAW · PRINT · STRIKE · STAMP**

---

## Two skins

**ANALOG is the default** — vintage brass instrument on near-black with contour texture.
**DIGITAL** is for literally computational subjects. One skin per project, declared once in
`tokens.css`, never mixed. Both expose identical variable and class names, so a
composition built against one renders under the other.

---

## Hard limits — check these every single time

- **Palette:** ground / ink / accent. Max **2 accent elements per frame**. Never pure black
  or pure white. Gold is a 5-stop ramp with off-centre specular — never a flat hue + bevel.
- **No light backgrounds over footage.** No white cards. Screenshots go in a Proof Panel at
  ~72% brightness with a 1px stroke.
- **Type:** `TacticSans-UltIt` display · `Europa Grotesk SH` caption · `Cinzel`
  engraved at **+0.180em** · `JetBrains Mono` readouts with `tabular-nums`.
  Word budget: 7 (slam) / 14 (card) / 5 (chip) / 4 (caption line).
- **Layout:** left axis `x=96`. One of five docks. **Never two overlays at once.** Clear of
  the caption band (**864–1152**) and the safe zones (top 240 / bottom 420 / sides 90).
  **Never park a graphic over the face.**
- **Motion:** entrance 0.28–0.42s, hold ≥0.8s, **no exits**. ≥3 distinct eases, 60–120ms
  staggers, 1–2 movers at a time, ambient motion on anything living >1.5s. Needles
  overshoot ≤5° then settle. **Never bounce, elastic, or back.**
- **Texture is mandatory, not optional.** Grain ≤15% static, felt-not-seen vignette,
  feathered mask edges, contour ground on analog cutaways, mechanical motion stepped to
  `--stutter-fps`. Zero texture is what makes a render look generated.
- **Density:** ≤8 graphics per 30s reel, one every 3–5s, exactly one in the first 3s.
- **Zero UI chrome.** No slide counters, no `@handle` watermark, no progress bars, no
  "FOLLOW FOR MORE" banner, no logo.
- **Copy is the creator's voice:** blunt, spoken, slang intact. Do not grammar-correct.
- **Banned:** emoji, flying icons, arrow doodles, gradient text, neon/cyan/purple,
  `box-shadow` on panels, emissive blowout, gym/car/hotel/watch/lifestyle visuals.

---

## When the request isn't a graphic

| Ask | Owner |
|---|---|
| cut footage, remove silence or filler | `ig-cut` |
| burn in captions, caption styling or timing | `ig-captions` |
| music, SFX, ducking, the mix | `ig-sound` |
| it feels boring, pacing, zoom pulses, shot scale | `ig-pacing` |
| export, QA, is it ready | `ig-delivery` |
| plan a whole edit end to end | `ig-reel` |

Hand it over. But hold these two lines regardless of which skill is driving:

1. **Land graphics on the word, not the sentence.** One frame late reads as lag.
2. **A pattern interrupt doesn't need a cut.** A near-static talking-head take reads fast
   if the graphics layer changes every 1–3s. Spend the interrupt budget here.
