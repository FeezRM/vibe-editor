---
name: ig-motion-graphics
description: "Designs and builds Instagram Reel motion graphics in Feez's (@feezkera) locked house style — 'The Terminal, in motion': 1080×1920, near-black + off-white + one declared accent, instrumentation-not-decoration graphics (meters, counters, deltas, curves, diffs, terminal logs, proof panels), built as HyperFrames HTML compositions and rendered to alpha .mov / .mp4 for Premiere Pro. Works brief → questions → approved MOTION PLAN → build → render → Premiere import sheet. Use whenever the user wants to: make or design a motion graphic, add a graphic/overlay/lower-third/animated text to a reel, visualize a number or stat in a video, build an animated counter, meter, chart, diff, terminal, or end card, style or restyle reel graphics, plan the graphics for a script, ask about the reel editing style, caption style, or how graphics get into Premiere. Triggers: motion graphic, motion graphics, animate this, animated overlay, reel graphic, lower third, kinetic text, animated number, counter animation, stat graphic, chart for my reel, graphics for this script, hyperframes, premiere overlay, alpha overlay, editing style, caption style, what should this graphic look like."
---

# IG Motion Graphics — The Terminal, in motion

Feez's locked motion-graphics system for Instagram Reels. This skill owns the **look**
and the **build**. The `ig-video-editor` skill owns the cut (silence removal, shot
scale, b-roll, pacing) — when a request needs both, produce the edit blueprint there and
the MOTION PLAN here, and cue them off the same timecodes.

Same design system as the `carousel-designer` skill, with a time axis added. A carousel
slide and a reel frame must read as the same studio.

---

## The one rule everything else serves

> **The graphics are instrumentation, not decoration.**

The brand's enemy is The Pose — people who *can't measure, that's why they pose*. The
thesis is *"posting is gambling. building a system isn't."* So every graphic on screen
looks like a readout from a system that is measuring something: a meter, a counter, a
delta, a curve, a diff, a log line, a receipt.

**Before building anything, answer: what does this graphic measure or prove?**
If there's no answer, say so and recommend a cut or b-roll instead. A graphic that
exists to fill a static shot is the problem, not the fix.

---

## Workflow — do not skip a step

### 1. Read the spec

| Read | When |
|---|---|
| [reference/MOTION-LANGUAGE.md](reference/MOTION-LANGUAGE.md) | **always.** palette, type, docks, timing, easing, banned list |
| [reference/BLOCKS.md](reference/BLOCKS.md) | **always.** the 13 named blocks. pick from these. |
| [reference/INTAKE.md](reference/INTAKE.md) | before asking questions or writing a plan |
| [reference/PIPELINE.md](reference/PIPELINE.md) | before scaffolding, rendering, or handing off |
| [reference/tokens.css](reference/tokens.css) | copy into every project; set `--accent` |

Do not improvise a visual language. Every graphic is one of the 13 blocks or a
deliberate, justified variant.

### 2. Ask — once, batched

Six questions in [INTAKE.md](reference/INTAKE.md). **Skip any the brief already
answers. Never ask about anything already locked** — fonts, easing, layout, safe zones,
"what vibe". Those are decided; re-asking them signals the system isn't real.

The two that always need asking on a new project, because they can't be defaulted
safely: **accent colour** and **sequence fps**.

### 3. Write the MOTION PLAN — and get it approved

Template in [INTAKE.md](reference/INTAKE.md). Per graphic: what it proves, the cue
timecode and trigger word, block, dock, duration, anatomy, and a **beat sheet with
timings and eases to two decimal places**. Save to `projects/<slug>/MOTION-PLAN.md`.

Show it. Take notes. **Do not write HTML before it's approved** — a plan costs a minute
to change, a built composition costs twenty.

*Fast mode:* if he says "just do it", collapse the plan to one line per graphic and go.
The quality bar doesn't move; only the approval step shrinks.

### 4. Build

Scaffold per [PIPELINE.md](reference/PIPELINE.md) §1, then **one composition file per
graphic** so any single graphic can be re-cut without touching the others.

Load-bearing HyperFrames rules — breaking these breaks the render:

- Root div: `data-composition-id`, `data-width="1080"`, `data-height="1920"`,
  `data-start`, `data-duration`, `data-track-index`. Standalone files put it directly in
  `<body>` — **no `<template>` wrapper**.
- `gsap.timeline({ paused: true })`, registered as
  `window.__timelines["<composition-id>"]`, built **synchronously**.
- **Deterministic.** No `Math.random()`, no `Date.now()`, no `repeat: -1`.
- **Layout the hero frame in CSS first**, then `gsap.from()` into it.
- `.scene-content` fills the frame with padding — never `position:absolute; top:Npx`.
- **No exit animations.** The cut is the exit. Only the final element of the final
  composition may fade.
- Overlays keep `background: transparent` on body and root; cards paint `--ground`.

### 5. Check before rendering

```bash
npx hyperframes lint .          # anywhere
npx hyperframes check .         # Mac — lint + runtime + layout + contrast
npx hyperframes snapshot . -c compositions/NN-block.html --at 0.2,0.6,1.4,2.4
```

**Read the snapshots.** Then run the checklist in MOTION-LANGUAGE §9 — `check` catches
JS errors and overflow, but it will happily pass a graphic with bounce easing, two
accent elements, or a white box over the footage.

### 6. Render and hand off

```bash
# overlay — alpha
npx hyperframes render . -c compositions/02-meter.html \
  --format mov --resolution portrait --fps 30 --quality high -o renders/02-meter.mov

# full-frame card
npx hyperframes render . -c compositions/01-hook-slam.html \
  --format mp4 --resolution portrait --fps 30 --quality high -o renders/01-hook-slam.mp4
```

Then write `renders/IMPORT.md` — the Premiere cue sheet (file, timecode, block, track,
blend mode). Format in [PIPELINE.md](reference/PIPELINE.md) §5.

**Rendering needs Chrome and only works on Feez's Mac.** In the Cowork sandbox
(Linux ARM64) authoring and `lint` work, `render` does not. If you can't render:
author, lint, write the plan and the import sheet, and hand back the exact commands to
paste. Never imply a render happened.

---

## The 13 blocks

Full anatomy and motion in [BLOCKS.md](reference/BLOCKS.md).

`HOOK SLAM` · `THE METER` · `THE COUNTER` · `THE DELTA` · `THE CURVE` · `THE DIFF` ·
`THE STACK` · `THE CHIP` · `THE RAIL` · `THE REDACTION` · `THE TERMINAL` ·
`THE PROOF PANEL` · `THE END CARD`

Seven reveal verbs, and nothing else: **SLAM · WIPE · COUNT · FILL · DRAW · PRINT ·
STRIKE**.

---

## Hard limits — check these every single time

- **Palette:** `--ground #0F0F10` / `--ink #F0EEE8` / `--accent` (declared per project).
  Max **2 accent elements per frame**. Emphasis inside a sentence is **weight**, not
  colour. Never pure black or pure white.
- **No light backgrounds over footage.** No white cards. Screenshots go inside a
  Proof Panel at ~72% brightness with a 1px stroke.
- **Type:** Inter Tight display at **−0.028em**, caps labels at **+0.085em**, JetBrains
  Mono readouts, `tabular-nums` on every live number. Word budget: 7 (slam) / 14 (card)
  / 5 (chip) / 4 (caption line).
- **Layout:** left-aligned on one axis (`x=96`). One of four docks. **Never two
  overlays at once.** Clear of the caption band (y 1180–1500) and the IG safe zones
  (top 240 / bottom 420 / sides 90).
- **Motion:** entrance 0.28–0.42s, hold ≥0.8s, **no exits**. ≥3 distinct eases,
  60–90ms staggers, ambient motion on anything living >1.5s. Eases: `power4.out` /
  `power2.out` / `expo.out` / `sine.inOut`. **Never bounce, elastic, back, or linear.**
- **Density:** ≤8 graphics per 30s reel, one every 3–5s, exactly one in the first 3s.
- **Zero UI chrome.** No slide counters, no `@handle` watermark, no progress bars, no
  "FOLLOW FOR MORE" banner, no logo.
- **Copy is his voice:** lowercase, spoken, blunt, "mans" intact. Do not grammar-correct
  him. ALL-CAPS is for labels and units only.
- **Banned:** emoji, flying icons, arrow doodles, gradient text, neon/cyan/purple, drop
  shadows on panels, emissive blowout, gym/car/hotel/watch/lifestyle visuals.

---

## When the request is about the edit, not a graphic

If he asks to cut footage, remove silence, add b-roll, or fix pacing, that's
`ig-video-editor`. Hand it over. But hold these two lines regardless of which skill is
driving, because they're the two biggest problems in his current reels:

1. **Shot-scale alternation.** His `4 million views` reel holds one medium shot for 36
   seconds. Adjacent beats must differ in scale; push-ins are 2–4% over 1.2s.
2. **Land graphics on the word, not the sentence.** One frame late reads as lag.

---

## Reference board

`motion-system/reference-board/index.html` — the visual guide: annotated frames from
@devinjatho's archived carousels, a teardown of Feez's own reel with what's working and
what isn't, the palette and type specs rendered live, and all 13 blocks drawn to spec.
Open it when a written rule needs a picture.
