# PIPELINE — brief → HyperFrames → Premiere Pro

The technical half. [MOTION-LANGUAGE.md](MOTION-LANGUAGE.md) says what it looks like;
this says how it gets built and how it lands on the timeline.

---

## 0. Where this runs

HyperFrames renders by driving a headless Chrome, so rendering works on **macOS,
Windows, and x64 Linux** — anywhere three things are present:

| Requirement | Check | Fix |
|---|---|---|
| **Node 22+** | `node -v` | nodejs.org · `brew install node` · `winget install OpenJS.NodeJS.LTS` |
| **FFmpeg** on `PATH` | `ffmpeg -version` | `brew install ffmpeg` · `winget install Gyan.FFmpeg` · `apt install ffmpeg` |
| **Chrome Headless Shell** | `npx hyperframes doctor` | the doctor prints the install command for this platform |

**Run `npx hyperframes doctor` once per machine before the first render.** It is the
fastest way to tell "this environment can't render" from "this environment isn't set up
yet." It is almost always the second.

Premiere Pro must be on the **same machine** as the renders — the MCP bridge is local and
`import_media` takes a local path.

### When rendering genuinely isn't available

Two cases, and only two: **ARM64 Linux** (no Chrome Headless Shell build) and **a
restricted agent shell** that blocks the Chrome launch, where the render hangs at
"Capturing frame N" — re-run the same command in a plain terminal.

Authoring, `init`, `add`, and `lint` work everywhere. If you land in one of those two:
author, lint, write the plan and the import sheet, and hand back the exact commands.
**Never imply a render happened** — and never hand back commands the machine you're on
could have run itself.

---

## 1. Project layout

One folder per reel, under `projects/`:

```
projects/<slug>/
├── hyperframes.json          created by `hyperframes init`
├── meta.json
├── tokens.css                copied from brand/tokens.css (generated — see below)
├── textures/                 pre-baked contour / grain assets (see §3)
├── index.html
├── compositions/
│   ├── 01-hook-slam.html
│   ├── 02-dial.html
│   └── ...                   ONE FILE PER GRAPHIC
├── assets/                   screenshots, recordings for Proof Panels
├── MOTION-PLAN.md            the approved plan, kept next to the build
└── renders/                  output .mov / .mp4 — this is what goes to Premiere
```

### Scaffold

```bash
cd projects
npx hyperframes init <slug> --example blank --non-interactive
cp ../brand/tokens.css <slug>/tokens.css        # the brand build — see below
mkdir -p <slug>/textures
```

```powershell
cd projects
npx hyperframes init <slug> --example blank --non-interactive
Copy-Item ..\brand\tokens.css <slug>\tokens.css   # the brand build — see below
New-Item -ItemType Directory -Force <slug>\textures | Out-Null
```

### Where tokens.css comes from

**Do not copy a skin file directly, and never hand-edit `brand/tokens.css`.** It is
generated:

```
brand/brand.json  ──node scripts/brand.mjs build──▶  brand/tokens.css  ──copy──▶  projects/<slug>/tokens.css
        ▲
   edit this
```

The generator loads `.claude/skills/ig-show/reference/tokens-<skin>.css` and substitutes
the brand's values into its `:root` block, so every class definition lives in exactly one
place. Change the accent once in `brand.json`, rebuild, and every future project picks it
up.

A project may still override a variable *after* the import for a one-off — but if you find
yourself doing that twice, it belongs in `brand.json`.

Free-text house rules that aren't values — voice, banned visuals, CTA — live in
`brand/BRAND.md`, which every skill reads.

### Fonts — the step that silently breaks renders

> ⚠️ **SUPERSEDED on hyperframes >= 0.7.108.** The absolute ban below was correct on older
> builds and is no longer. `lint` now actively *demands* an `@font-face` for any family it
> cannot auto-resolve, and a composition using one to point at a locally-installed OTF
> renders correctly with all custom properties intact (verified by render, 2026-08).
>
> **The current rule:** prefer auto-resolving families (`Anton`, `Inter`, `JetBrains Mono`)
> and write no `@font-face` at all. Write one *only* to guarantee a licensed face from a
> local file — and then **verify it in a rendered frame**, because a fallback is invisible in
> the markup and obvious in the pixels. `SKILL.md` §4 is the authority on this.
>
> The historical warning is kept below because the failure it describes is real and
> spectacular when it happens.

**Historically: never write `@font-face`.** This was the single most expensive mistake available here.
HyperFrames injects its own deterministic `@font-face` block at compile time, and a
hand-authored one collides with it and **silently kills the entire stylesheet** — every
custom property stops resolving, so the render comes out as black serif text on a
transparent ground with no linework at all. `lint` and `check` both pass clean while this
is happening. Verified by render, not by theory.

The licensed faces are matched by **system font resolution instead**, so they must be
**installed on the machine doing the render**. Nothing goes in the project.

**Exact family strings — these are not guessable and one of them is a trap:**

| Role | Family string | Notes |
|---|---|---|
| Display | `TacticSans-UltIt` | matches the installed name directly |
| Caption | `Europa Grotesk SH` | **not** `Europa Grotesk SH Bol` |

`Europa Grotesk SH Bol` is what Windows' `InstalledFontCollection` reports — it is the
truncated GDI name, and Chrome will not match it. The typographic family is
`Europa Grotesk SH`. The GDI name falls back to a serif in total silence.

Cinzel and JetBrains Mono are Google/OFL and embed automatically from the `font-family`
declaration. No install needed for those.

**Free fallbacks are already declared in every stack** (`Anton`, `Archivo Black`), so a
machine without the licensed faces renders a degraded look rather than breaking.

**Verify before a batch render:** snapshot one frame and look at it. A fallback face is
obvious at a glance and completely invisible to the linter. If the frame comes back black
serif with no strokes, something re-introduced an `@font-face`.

⚠️ Both licensed faces are commercial. Because nothing is copied into the project there is
nothing to leak, but `.gitignore` still excludes font binaries as a backstop.

---

## 2. Composition boilerplate

One graphic per file, rendered separately, so any single graphic can be re-cut and
re-rendered without touching the others.

Non-negotiables — these are HyperFrames' own rules, and breaking them breaks the render:

- Root div carries `data-composition-id`, `data-width="1080"`, `data-height="1920"`,
  `data-start="0"`, `data-duration="<seconds>"`, `data-fps`.
- Standalone files put that div **directly in `<body>`** — no `<template>` wrapper.
  `<template>` is only for sub-compositions loaded via `data-composition-src`.
- Every timeline is `gsap.timeline({ paused: true })`, registered as
  `window.__timelines["<composition-id>"] = tl`, and built **synchronously** — never
  inside `async`, `setTimeout`, or a Promise.
- **Deterministic only.** No `Math.random()`, no `Date.now()`. Seeded mulberry32 if you
  need jitter. No `repeat: -1` — compute `Math.ceil(duration / cycle) - 1`.
- Animate visual properties only — never `display`, `visibility`, or `.play()`.
- **Layout the hero frame in CSS first**, then `gsap.from()` into it. Never position
  elements at their animated start state.
- `.scene-content` fills the frame with padding — never `position:absolute; top:Npx`.

Two lint traps that 404 the render:

- **Asset paths are root-relative, always.** A file at `compositions/02-dial.html` links
  `href="tokens.css"`, **not** `href="../tokens.css"`. Compositions are served with the
  project root as their base URL. `../` is a hard lint error.
- **No Google Fonts `<link>` or `@import`.** Name the family; the compiler embeds it.

### Skeleton

```html
<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="tokens.css">   <!-- ONE stylesheet. no fonts.css -->
<style>/* hero-frame layout, static */</style>
</head><body>
<div id="root" data-composition-id="dial" data-width="1080" data-height="1920"
     data-start="0" data-duration="2.8" data-track-index="0" data-fps="30">
  <div class="scene-content"><!-- content --></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  /* entrances only — no exits */
  window.__timelines["dial"] = tl;
</script>
</body></html>
```

### Transparent background

**Overlay:** `body` and the root div stay `background: transparent`. The plate colour goes
on the graphic's own panel, not on the frame. **Cutaway:** add `class="card"` to the root.

Overlays skip the ground/contour texture layers — the footage underneath is the ground.
Carry grain **only** if the graphic has its own plate to carry it on; grain over
transparency produces a dirty alpha that fringes badly in Premiere.

### Templated blocks

Declare `data-composition-variables` on the root, read via
`window.__hyperframes.getVariables()`. One composition, many variants:

```bash
npx hyperframes render . -c compositions/02-dial.html \
  --variables '{"label":"REVENUE PER REEL","value":2997,"max":5000,"prefix":"$"}' \
  -o renders/02-dial-revenue.mov --format mov
```

Use it for `THE DIAL`, `THE COUNTER`, `THE CHIP`, and `THE DELTA` — the four blocks that
get reused most.

---

## 3. Pre-baked texture assets

Contour fields, guilloche bands, crack paths, and annotation wobble are **generated
offline and pasted in as static SVG `<path>` data**. Never at runtime — even seeded noise
is a liability across Chrome versions, and there's no reason to pay for it every frame.

Store generated assets in `<slug>/textures/`. Grain stays a live `feTurbulence` with a
**fixed `seed`**, or gets baked to a PNG if the project must be bit-identical across
machines. Full recipes: [TEXTURE.md](TEXTURE.md).

---

## 4. Rendering

### Overlays — alpha

```bash
npx hyperframes render . -c compositions/02-dial.html \
  --format mov --resolution portrait --fps 30 --quality high \
  -o renders/02-dial.mov
```

`--format mov` and `--format webm` render **with transparency**. MOV is the one to use —
Premiere imports it with the alpha intact, no interpretation step.

For an After Effects / Fusion round-trip, or if a MOV misbehaves:
`--format png-sequence -o renders/02-dial-frames/` gives RGBA PNGs.

### Cutaways — no alpha needed

```bash
npx hyperframes render . -c compositions/01-hook-slam.html \
  --format mp4 --resolution portrait --fps 30 --quality high \
  -o renders/01-hook-slam.mp4
```

### The blend-mode shortcut

A graphic that is **light-on-transparent with no dark plate** — a bare counter, a hairline
rail, an annotation — can skip alpha: render `mp4` on pure `#000000` and set the Premiere
clip to **Screen**. Black goes fully transparent under Screen. Faster, smaller, and
lossless for this palette because nothing in the graphic is darker than the background.

Use alpha MOV whenever the graphic contains a plate, a stroke, or any dark element that
Screen would erase.

**Render at the sequence fps.** Not at whatever the composition defaulted to.

---

## 5. Quality gate

```bash
npx hyperframes lint .                       # structure — no Chrome needed
npx hyperframes check .                      # lint + runtime + layout — needs Chrome
npx hyperframes snapshot . -c compositions/02-dial.html --at 0.2,0.6,1.4,2.4
```

**Read the snapshots.** `check` catches JS errors, missing assets, text overflow, and
contrast. It does **not** catch: a fallback font, wrong tracking, bounce easing, two
accents on one frame, a graphic sitting in the caption band, or a missing texture stack.
Those are on you — run [MOTION-LANGUAGE §9](MOTION-LANGUAGE.md).

`hyperframes compare` renders variants into one labelled sheet — use it when choosing
between two treatments rather than approving one.

---

## 6. Premiere handoff

Filenames encode the cue:

```
<order>-<block>-<slug>@<timecode>.mov
03-counter-4million@00-12.mov
```

Write `renders/IMPORT.md` alongside them:

| File | Cue (TC) | Block | Track | Blend | Notes |
|---|---|---|---|---|---|
| `01-hook-slam.mp4` | 00:00:01:04 | HOOK SLAM | V2 | Normal | full frame, cut to it |
| `03-counter-4million.mov` | 00:00:12:18 | COUNTER | V3 | Normal | alpha, over A-roll |
| `05-annotation.mov` | 00:00:19:02 | ANNOTATION | V4 | Normal | alpha, lands on "wrong" |

### Track convention

Derived from an observed real project, and it differs from the naive layout: **each
recurring graphic type gets its own track** rather than sharing one graphics track. Two
graphics that overlap in time cannot share a track, so this removes an entire class of
placement collision before it happens.

```
V1  A-roll
V2  B-roll / full-frame cutaways
V3  primary graphic overlays (alpha)
V4  secondary graphics — annotations, chips (alpha)
V5+ additional simultaneous graphic types
CAP native Premiere captions track — kept separate from graphics
A1  voice   A2  voice/alt   A3  SFX   A4  SFX   A5  music   A6  spare
```

Create tracks with `add_track`; confirm with `list_sequence_tracks`. **Never assume an
index exists.**

### In Premiere — over MCP

1. `verify_premiere_connection`, then `get_sequence_settings` — render at the sequence fps.
2. `import_media` each file in `renders/` (or `import_folder`).
3. `add_track` / `list_sequence_tracks`, then place each clip at its `IMPORT.md` cue.
4. **`export_frame` at every cue.** The only honest check — a tool returning success is
   not one.

Screen-blend clips need the blend mode set by hand in Effect Controls; there is no
blend-mode tool. Prefer alpha MOV when that matters.

**Never scale, reposition, or add effects to a rendered graphic in Premiere.** It was
composed at full frame for a reason. Fix the composition and re-render — twenty seconds
of render beats a graphic eight pixels off the shared axis.

---

## 7. Common failures

| Symptom | Cause | Fix |
|---|---|---|
| Everything renders black serif, no strokes, no colours | an `@font-face` rule collided with HyperFrames' injected block and killed the stylesheet | on <0.7.108: delete every `@font-face`. On >=0.7.108 this collision no longer occurs and `lint` may require one — check the version before deleting. Symptom in the log: `Fonts: 0 loaded` |
| Type looks *almost* right | licensed face fell back | not installed on this machine, or the family string is wrong — `Europa Grotesk SH`, never `...SH Bol` |
| Black rectangle instead of the graphic | rendered `mp4` when it needed alpha | re-render `--format mov` |
| Graphic invisible under Screen | it has a dark plate — Screen erased it | re-render as alpha MOV |
| Alpha MOV imports opaque | interpretation | right-click → Modify → Interpret Footage → Alpha: Straight (Unmatted) |
| Dirty/fringed alpha edges | grain applied over transparency | move grain onto the graphic's plate, or drop it from the overlay |
| Numbers jitter while counting | missing `tabular-nums` | add `font-variant-numeric: tabular-nums` |
| Ledger column wobbles | same | right-aligned figures need it most |
| Banding across a dark gradient | full-screen linear gradient in H.264 | radial gradient, or solid + localised lift |
| Graphic stutters on the timeline | fps mismatch with the sequence | re-render at the sequence fps |
| Motion looks *too* smooth / synthetic | no stutter pass | step mechanical motion to `--stutter-fps` ([TEXTURE.md §5](TEXTURE.md)) |
| Render hangs at "Capturing frame N" | Chrome blocked by a sandboxed shell | run it in a plain terminal |
| `Could not find Chrome` | headless shell not installed | `npx hyperframes doctor` |
| `window.__timelines` errors | timeline built async, or not registered | build synchronously, register by composition id |
| Text clipped in render, fine in preview | fixed-size container | add `max-width` + wrap, or `fitTextFontSize(...)` |
| Element appears fully formed | missing entrance tween | every element gets a `gsap.from()` |
| Composition ends on an empty frame | someone added exit animations | delete them — the cut is the exit |
| `invalid_parent_traversal_in_asset_path` | `../tokens.css` | paths are root-relative |
| Styles missing in render, fine locally | same root-relative path issue | run `lint` before every render |
