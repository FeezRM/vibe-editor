# PIPELINE — brief → HyperFrames → Premiere Pro

The technical half. [MOTION-LANGUAGE.md](MOTION-LANGUAGE.md) says what it looks like;
this says how it gets built and how it lands on the timeline.

---

## 0. Where this runs

HyperFrames renders by driving a headless Chrome. **It must run on Feez's Mac** — via
Claude Code in Terminal, or Open Design's studio. The Cowork Linux sandbox is ARM64 and
has no Chrome Headless Shell, so `render`, `preview`, `inspect`, `snapshot`, and
`validate` will fail there. `init`, `add`, `lint`, and all authoring work fine anywhere.

**Practical split:**

| Step | Where |
|---|---|
| Brief, questions, MOTION PLAN | anywhere (Cowork is fine) |
| Author the composition HTML | anywhere |
| `lint` | anywhere |
| `check` / `snapshot` / `render` | **Feez's Mac** |
| Premiere import | Feez's Mac |

If the session can't render, author the composition, lint it, and hand back the exact
render command to paste. Don't pretend a render happened.

---

## 1. Project layout

One folder per reel, under `motion-system/projects/`:

```
projects/<slug>/
├── hyperframes.json          created by `hyperframes init`
├── meta.json
├── tokens.css                copied from skill-src/reference/tokens.css, accent set
├── index.html                the composition (or a router for several)
├── compositions/
│   ├── 01-hook-slam.html
│   ├── 02-meter.html
│   └── ...                   one file per graphic
├── assets/                   screenshots, screen recordings for Proof Panels
├── MOTION-PLAN.md            the approved plan, kept next to the build
└── renders/                  output .mov / .mp4 — this is what goes to Premiere
```

Scaffold:

```bash
cd "motion-system/projects"
npx hyperframes init <slug> --example blank --non-interactive
cp ../skill-src/reference/tokens.css <slug>/tokens.css
```

Then edit `tokens.css` to set `--accent` for this project and nothing else.

---

## 2. Composition boilerplate

Each graphic is its own composition, rendered separately, so it can be re-cut,
re-timed, and re-rendered without touching the others. **One graphic per file.**

Non-negotiables (these are HyperFrames' own rules — breaking them breaks the render):

- Root div carries `data-composition-id`, `data-width="1080"`, `data-height="1920"`,
  `data-start="0"`, `data-duration="<seconds>"`.
- Standalone files put that div **directly in `<body>`** — no `<template>` wrapper.
  `<template>` is only for sub-compositions loaded via `data-composition-src`.
- Every timeline is `gsap.timeline({ paused: true })` and is registered:
  `window.__timelines["<composition-id>"] = tl`.
- Build timelines **synchronously** — never inside `async`, `setTimeout`, or a Promise.
- **Deterministic only.** No `Math.random()`, no `Date.now()`. Use a seeded mulberry32
  if you need jitter.
- **No `repeat: -1`.** Compute finite: `Math.ceil(duration / cycle) - 1`.
- Animate visual properties only — never `display`, `visibility`, or `.play()`.
- Layout the **hero frame in CSS first**, then `gsap.from()` into it. Never position
  elements at their animated start state.
- `.scene-content` fills the frame with `width:100%; height:100%; padding:…;
  box-sizing:border-box` — never `position:absolute; top:Npx`.

Two lint traps, both verified against `hyperframes lint` v0.7.103 — get these wrong and
the render 404s:

- **Asset paths are root-relative, always.** A file at `compositions/02-meter.html`
  links `href="tokens.css"`, **not** `href="../tokens.css"`. Compositions are served
  with the project root as their base URL. `../` is a hard lint error.
- **No Google Fonts `<link>` or `@import`.** The compiler embeds supported families
  automatically from the `font-family` declaration. A raw external font request is a
  lint warning and adds render latency.

Minimal skeleton (see `templates/base/` for four real, lint-clean ones):

```html
<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="tokens.css">
<style>/* hero-frame layout, static */</style>
</head><body>
<div id="root" data-composition-id="meter" data-width="1080" data-height="1920"
     data-start="0" data-duration="2.6" data-track-index="0" data-fps="30">
  <div class="scene-content"><!-- content --></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  /* entrances only — no exits */
  window.__timelines["meter"] = tl;
</script>
</body></html>
```

### Transparent background

For an **overlay**, the composition must have no background paint: `body` and the root
div stay `background: transparent`. The `PLATE` colour goes on the graphic's own panel,
not on the frame. For a **full-frame card**, the root gets `background: var(--ground)`.

### Templated blocks

Declare `data-composition-variables` on the root and read values via
`window.__hyperframes.getVariables()`. Then one composition renders many variants:

```bash
npx hyperframes render . -c compositions/02-meter.html \
  --variables '{"label":"REVENUE PER REEL","value":2997,"max":5000,"unit":"$"}' \
  -o renders/02-meter-revenue.mov --format mov
```

Use this for THE COUNTER, THE METER, THE CHIP, and THE DELTA — the four blocks he'll
reuse most.

---

## 3. Rendering

### Overlays — alpha

```bash
npx hyperframes render . -c compositions/02-meter.html \
  --format mov --resolution portrait --fps 30 --quality high \
  -o renders/02-meter.mov
```

`--format mov` and `--format webm` render **with transparency**. MOV is the one to use —
Premiere imports it natively with the alpha channel intact, no interpretation step.

For an After Effects / Fusion round-trip, or if a MOV ever misbehaves:

```bash
npx hyperframes render . -c compositions/02-meter.html \
  --format png-sequence -o renders/02-meter-frames/
```

RGBA PNGs, then import as an image sequence.

### Full-frame cards — no alpha needed

```bash
npx hyperframes render . -c compositions/01-hook-slam.html \
  --format mp4 --resolution portrait --fps 30 --quality high \
  -o renders/01-hook-slam.mp4
```

### The blend-mode shortcut

For any graphic that is **light-on-transparent with no dark plate** — a bare counter, a
caption, a hairline rail — you can skip alpha entirely: render `mp4` on a pure `#000000`
background and set the Premiere clip to **Screen**. Black goes fully transparent under
Screen. It encodes faster, files are smaller, and it's completely lossless for this
palette because nothing in the graphic is darker than the background.

Use alpha MOV whenever the graphic contains a `PLATE` panel, a stroke, or any dark
element that Screen would erase.

---

## 4. Quality gate — before it goes anywhere near Premiere

```bash
npx hyperframes lint .                                   # structure (runs anywhere)
npx hyperframes check .                                  # lint + runtime + layout (Mac)
npx hyperframes snapshot . -c compositions/02-meter.html \
  --at 0.2,0.5,1.2,2.4                                   # eyeball the hero frames
```

Then read the snapshots and check them against the MOTION-LANGUAGE §9 list. `check`
catches JS errors, missing assets, text overflow, and WCAG contrast. It does **not**
catch: wrong tracking, bounce easing, two accents on one frame, a graphic sitting in the
caption band. Those are on you.

`hyperframes compare` renders variants into one labelled sheet — use it when Feez is
choosing between two treatments rather than approving one.

---

## 5. Premiere Pro handoff

Every render lands in `projects/<slug>/renders/` with a filename that encodes its cue:

```
<order>-<block>-<slug>@<timecode>.mov
03-counter-4million@00-12.mov
```

The MOTION PLAN is the import sheet. Alongside the renders, write
`renders/IMPORT.md`:

| File | Cue (source TC) | Block | Track | Blend | Notes |
|---|---|---|---|---|---|
| `01-hook-slam.mp4` | 00:00:01:04 | HOOK SLAM | V2 | Normal | full frame, cut to it |
| `03-counter-4million.mov` | 00:00:12:18 | COUNTER | V3 | Normal | alpha, sits over A-roll |
| `05-rail-attribution.mov` | 00:00:19:02 | RAIL | V3 | Normal | alpha |
| `07-caption-band.mp4` | 00:00:00:00 | CAPTIONS | V4 | Screen | black bg, screen blend |

Track convention, bottom to top:

```
V1  A-roll
V2  B-roll / proof panels / full-frame cards
V3  motion-graphic overlays (alpha)
V4  captions
A1  voice   A2  music   A3  SFX
```

### In Premiere

1. Sequence: **1080×1920, 30fps** (or 24 — match what the compositions were rendered at;
   a mismatch is what makes graphics stutter).
2. Import the whole `renders/` folder. Alpha MOVs interpret automatically — if one
   doesn't, right-click → *Modify → Interpret Footage → Alpha Channel: Straight
   (Unmatted)*.
3. Drop each clip at the cue timecode from `IMPORT.md`. **Snap the head to the frame the
   keyword lands on**, not the start of the sentence.
4. Screen-blend clips: Effect Controls → Opacity → Blend Mode → **Screen**.
5. Do not scale, reposition, or add effects to a graphic. It was composed at full frame
   for a reason — if it's in the wrong place, fix the composition and re-render. Twenty
   seconds of re-render beats a graphic that's 8px off the shared left axis.
6. Export: H.264, 1080×1920, VBR 2-pass, target 12 Mbps, AAC 320kbps.

---

## 6. Common failures and what they actually mean

| Symptom | Cause | Fix |
|---|---|---|
| Black frame instead of the graphic | rendered `mp4` when the graphic needed alpha | re-render `--format mov` |
| Graphic invisible under Screen | it has a dark `PLATE` — Screen erased it | re-render as alpha MOV |
| Numbers jitter while counting | missing `tabular-nums` | add `font-variant-numeric: tabular-nums` |
| Banding across a dark gradient | full-screen linear gradient in H.264 | radial gradient, or solid + localised glow |
| Graphic stutters on the timeline | fps mismatch with the sequence | re-render at the sequence fps |
| Render hangs at "Capturing frame N" | Chrome sandboxed by the agent shell | run the render in a plain Terminal, not inside a sandboxed tool call |
| `window.__timelines` errors | timeline built async, or not registered | build synchronously, register by composition id |
| Text clipped in the render but fine in preview | fixed-size container | add `max-width` + wrap, or `window.__hyperframes.fitTextFontSize(...)` |
| Element appears fully formed | missing entrance tween | every element gets a `gsap.from()` |
| Composition ends on an empty frame | someone added exit animations | delete them — the cut is the exit |
| `invalid_parent_traversal_in_asset_path` | `../tokens.css` in a composition | use `tokens.css` — paths are root-relative |
| `google_fonts_import` warning | a Google Fonts `<link>` / `@import` | delete it, keep the `font-family` |
| Styles missing in the render but fine locally | same root-relative path issue | run `lint` before every render |
