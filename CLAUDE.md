# CLAUDE.md — vibe-editor

Agent-driven short-form video editing. **HyperFrames** (HTML → alpha video) draws the motion
graphics; **Adobe Premiere Pro over MCP** does everything else on the live timeline.

`README.md` is the human-facing setup and product doc. **This file is the operating manual:**
what is already decided, what this machine actually does, and what has burned previous runs.

---

## First: the skills own the craft — route, don't freestyle

Seven skills in `.claude/skills/` encode the house style, and they are the source of truth.
**Do not invent an editing approach, a graphic design, or a caption spec from scratch.** Find
the owner and follow it.

| Request | Skill |
|---|---|
| A whole video, an edit plan, "where do I start" | **`ig-reel`** — orchestrator, blueprint, sequence + track setup |
| Remove silence/filler, tighten the spine | **`ig-cut`** (step 1) |
| Captions: build, timing, styling, placement | **`ig-captions`** (step 2) |
| Music, ducking, SFX, the mix | **`ig-sound`** (steps 3 + 5) |
| **Motion graphics, overlays, mockups, charts** | **`ig-show`** (step 4) — the one that decides quality |
| Boring, drags, needs energy, zoom pulses | **`ig-pacing`** (step 6) |
| QA and export | **`ig-delivery`** |
| Premiere MCP setup / bridge troubleshooting | **`premiere-pro-mcp`** |

Single-phase request → go straight to that phase's skill. Whole-video request → `ig-reel`.

`ig-show/reference/` holds the deep spec. Read in this order:
`SAMPLES.md` (**the four reels torn down structurally** — persistent object, motif, beat map,
technique index; read before planning anything), `FRAME-CONTRACTS.md` (**the four spatial
architectures — declaring one is mandatory**), `TEARDOWN.md` (the style measurements behind
SAMPLES.md, and why the previous style failed), `VISUAL-HOOK.md`, `DEVICES.md` (spoken line →
object on screen), `BLOCKS.md` (15 blocks), `MOTION-LANGUAGE.md`, `TEXTURE.md`,
`PIPELINE.md` (build/render/handoff mechanics + failure table).

### Precedence, lowest to highest

```
repo defaults (skills) → brand/ → projects/<slug>/tokens.css + MOTION-PLAN.md → this conversation
```

Read `brand/BRAND.md` and `brand/brand.json` **before planning or building anything.** Where
`brand/` contradicts a skill default, `brand/` wins — and say so out loud rather than
silently following the default.

### Where the docs disagree, these win

The repo has been corrected in place several times and older prose survives in places. When
you hit a conflict, the later, measured figure is authoritative:

| Topic | Stale | Use |
|---|---|---|
| Pattern-interrupt interval | "3–5s" (README, old SOP) | **~1.5s average, never past ~2s static** (`ig-pacing`) |
| Caption band | "45–60%", "y 864–1152" | **y 920–1130** on 1080×1920 (`ig-captions`) |
| Graphics per 30s | "≤8" (README) | **`brand.json` `density.maxGraphicsPer30s: 12`** — brand/ outranks README |
| `@font-face` | "never write one, it kills the stylesheet" (`PIPELINE.md` §1) | On hyperframes ≥0.7.108 lint *demands* one for non-auto-resolving families. Prefer auto-resolving families; use `@font-face` at a local file only for a licensed face, and **verify with a rendered frame** (`ig-show` §4) |
| Composition granularity | "one HTML file per graphic" | **1–3 SCENES per video**, each one persistent object through a labelled state machine (`ig-show` §4). The old rule is why the output was a slideshow |
| Hook lockup type | 96/104px | **108/118px**, measured (`VISUAL-HOOK.md`) |
| Assets you don't have | "ask the creator, or build nothing" | **the acquisition ladder** — on disk → extract from footage → capture a real UI → look it up → generate → ask → build nothing (`ig-show` §2) |
| Density | "a graphic is on screen ≥85%" | "**one object** is on screen ≥85% and changes state every ~1.5s" — the first is satisfied by 12 unrelated cards |

---

## Known environment defects — verified, not theory

Reproduced on Windows 11 with Premiere 26.x, and each one has silently produced a false
"verified" in a past run. **Check them on your machine before you trust a green result**;
they may or may not reproduce on yours, and that is exactly the point — none of them
announces itself.

1. **`export_frame` returns `{"success": true}` and writes nothing.** Two failure modes:
   backslash paths get read as escapes and mangled (`\v`, `\f`), *and* the host exporter is
   broken even with a clean path. Always pass **forward slashes**, then:
   ```bash
   test -f "<path>" || echo "export_frame LIED"
   ```
   Fallback that works — composite the overlay over a real A-roll frame with ffmpeg:
   ```bash
   ffmpeg -y -ss <t> -i <a-roll> -ss <t> -i <overlay.mov> \
     -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];\
     [1:v]format=rgba[ov];[bg][ov]overlay=0:0" -frames:v 1 out.png
   python analysis/measure.py out.png 0
   ```
2. **`encodeSequence` can throw — Premiere then cannot export the sequence at all.** The
   workaround is to rebuild the spine outside Premiere: read every V1 clip's source in-point,
   scale and position back over MCP with `get_clip_properties`, then reassemble with ffmpeg.
   That script is per-project (it hardcodes your source path and clip table) — write it into
   `analysis/`, which is gitignored for exactly this reason. If a real export is required,
   hand the user *File → Export → Media*; never report an export that didn't happen.
3. **Re-rendering a `.mov` that Premiere has open fails at ~90%** with
   `EPERM: … rename … .hf-transaction-XXXX/x.mov -> x.mov`. The **old file survives**, so
   anything you check afterwards is the previous render and the log tail looks normal.
   Render to a new filename (`07-hook-v2.mov`) and swap the clip, or take the item offline
   first. After any re-render, check the output's **timestamp** before trusting a frame from it.

**The rule behind all three: a verification step that cannot fail is not a verification
step.** Verify with pixels and file timestamps, never with a tool's return code.

---

## Premiere MCP — non-negotiables

- **`verify_premiere_connection` before anything else.** Read-only; reports build, open
  project, active sequence. If it fails the bridge is down: Premiere open → project open →
  *Window → Extensions → MCP Bridge (CEP)* → Temp Directory matches `PREMIERE_TEMP_DIR` in
  `.mcp.json` → *Start Bridge*. Don't edit around a dead bridge.
- Attach `premiere://config/get_instructions` before project-modifying work; it overrides
  guesses made anywhere else.
- **It edits the live project. No dry run, no agent-controlled undo** — your calls share one
  history with the user's Ctrl-Z. Before a destructive pass, state what you're about to do
  and how many operations it is, and have the user save.
- **Timecodes are timeline frames, not source frames.** Read positions back with
  `get_clip_properties` / `get_clip_at_position` instead of computing them.
- **Never assume a track index exists** — `add_track`, then confirm with
  `list_sequence_tracks`. Two clips can't share a start frame on one track.
- **Premiere generates nothing** — no transcription, no images, no music. Transcribe with
  `npx hyperframes transcribe`; generate assets via the `media-use` skill into
  `projects/<slug>/assets/`, then `import_media`.
- **Never scale, reposition, or add effects to a rendered graphic in Premiere.** It was
  composed at full frame. Fix the composition and re-render.
- Don't reach for After Effects round-trips — `import_ae_comps` is unadvertised and `.aep`
  imports can wedge the bridge.
- When a call fails twice the same way, run the CEP panel's **Run Diagnostics** and report
  what it says instead of retrying a third time.

**Track architecture** (each recurring graphic type gets its own track — this is deliberate):

```
V1 A-roll · V2 B-roll/cutaways · V3 primary graphics (alpha) · V4 secondary · V5+ more
CAP native captions (separate from graphics)
A1 voice · A2 voice alt · A3 SFX · A4 SFX · A5 music · A6 spare
```

---

## Commands

Toolchain present and verified here: Node 24.12, ffmpeg 8.1.1, Python 3.14. `hyperframes` is
**not** installed globally — `npx hyperframes` resolves the registry package (npx-cached);
`vendor/hyperframes` is an upstream monorepo clone, not the CLI you invoke.

```bash
# brand — the only place the look is configured
node scripts/brand.mjs init|scaffold|build|show|check   # build: brand.json -> brand/tokens.css

# graphics
npx hyperframes lint  projects/<slug>          # structure, no Chrome needed
npx hyperframes check projects/<slug>          # + runtime/layout, needs Chrome
npx hyperframes snapshot projects/<slug> --at 0.2,0.6,1.4   # NO -c on 0.8.4; snapshots index.html
python analysis/motion-density.py projects/<slug>/compositions/*.html   # the motion floor
npx hyperframes render projects/<slug> -c compositions/NN-block.html \
  --format mov --fps 30 -o projects/<slug>/renders/NN-block.mov
npx hyperframes transcribe <file>              # word-level timestamps; Premiere has none

# measurement (don't eyeball anything with a number in its spec)
python analysis/measure.py <frame-or-video> <t1,t2,...>   # caption cap height + line width
python analysis/build-captions.py <words.json> <out.html> [--duration S]

# diagnostics
npx hyperframes doctor
npm --prefix vendor/adobe-premiere-pro-mcp run setup:doctor:win
```

`--format mov` / `webm` carry alpha; `mp4` does not. `--resolution` is **rejected** for alpha
output — author at 1080×1920 and omit it. **Render at the sequence fps** — a mismatch shows as
overlay stutter and is not fixable at export.

`analysis/` ships exactly three tools — `measure.py`, `motion-density.py`,
`build-captions.py` — and they are generic, argument-driven, and tracked. Everything else in
that folder is **gitignored scratch**: single-frame compositors, preview builders, audit
stills. Those carry a hardcoded source path and clip table for one project, so write a fresh
one per project rather than trusting the numbers in an old one.

---

## Layout and where things go

```
brand/            brand.json + BRAND.md → the ONLY place to change the look.
                  tokens.css is GENERATED — never hand-edit it.
.claude/skills/   the house style. Change brand/, not these, to restyle.
templates/base/   lint-clean HyperFrames starter, 4 working blocks (see its README --
                  they show the contract, and deliberately fail the motion floor)
projects/<slug>/  one folder per video — gitignored, yours
  hyperframes.json meta.json tokens.css index.html
  compositions/   ONE FILE PER SCENE (1-3 per video), not one per graphic
  assets/  textures/  renders/  (+ renders/IMPORT.md cue sheet)
  MOTION-PLAN.md  MIX.md  DELIVERY.md  RESULT.md
analysis/         scratch frame checks + measurement scripts (gitignored)
exports/          finished masters out of Premiere
samples/          reference reels — REAL people's accounts. Copy layout, never identity.
vendor/           cloned engines, gitignored, managed by scripts/setup-*.
```

Scaffold a project: `npx hyperframes init <slug> --example blank --non-interactive` from
inside `projects/`, then copy `brand/tokens.css` → `<slug>/tokens.css` and `mkdir textures`.

**Git hygiene:** this repo is the *tool*, not the footage. `.prproj`, all media, `projects/*`,
`analysis/`, `renders/*`, `exports/*`, `vendor/`, `.mcp.json`, and font binaries are
gitignored on purpose. Don't add them, and don't commit unless asked.

---

## Composition rules that break the render if ignored

- Root div carries `data-composition-id`, `data-width="1080"`, `data-height="1920"`,
  `data-start`, `data-duration`, `data-fps`, directly in `<body>` (no `<template>` wrapper —
  that's only for sub-compositions).
- `gsap.timeline({ paused: true })`, registered as `window.__timelines["<id>"]`, built
  **synchronously** — never in `async`, `setTimeout`, or a Promise.
- **Deterministic only.** No `Math.random()`, no `Date.now()`, no `repeat: -1` (compute
  `Math.ceil(duration / cycle) - 1`), fixed `seed` on every `feTurbulence`.
- **Asset paths are root-relative** — `href="tokens.css"`, never `../tokens.css` (hard lint
  error). No Google Fonts `<link>` or `@import`.
- Lay the hero frame out in CSS, then `gsap.from()` into it. Animate visual properties only —
  never `left`/`top`/`width`, `display`, `visibility`, or `.play()`.
- **No exits *between* scenes — the cut is the exit**, and only a scene's final element may
  fade. **Inside** a scene, elements persist, dim, desaturate, or are displaced; they never
  disappear and reappear.
- **Mark every beat with `tl.addLabel()`.** The labels are the scene's state machine.
- **Sub-compositions are supported and were never used.** A scene is the parent; each device
  inside it is a sub-comp with its own timeline. That is what makes a 40s composition
  tractable.
- Overlays stay `background: transparent`; full-frame cutaways use `.cutaway`. Grain over
  transparency fringes in Premiere — put it on the graphic's own plate or drop it.
- Compose from the `tokens.css` classes (`.ig-*`, `.reel`, `.metric`, `.pyramid`, `.chart`,
  `.wash`, `.skel-*`, `.glow-*`, `.keep-*`, `.brace`, `.annot-*`, `.hook2`, `.tile-wall`) —
  they already encode the correct metrics. **Most of that file is unused; read it before
  writing CSS.**

**Font family strings** (not guessable, one is a trap): `Europa Grotesk SH` — **not**
`Europa Grotesk SH Bol`, which is the truncated Windows GDI name Chrome won't match and which
falls back to a serif in total silence. Display: `TacticSans-UltIt`. `Anton`, `Inter`, and
`JetBrains Mono` auto-resolve. Licensed faces must be installed on the render machine. Use
`--font-ui` (Inter) inside app mockups — the brand display face inside a mockup breaks the
illusion instantly.

---

## The quality bar, in one screen

- **SHOW THE NOUN.** If the script names a thing, put that thing on screen, rebuilt faithfully.
  If it names a number, draw the real measurement with real axes and units.
- **The mute test disqualifies** *informational* decoration. Hide audio and captions — if the
  frame still makes the point, keep it. If not, it's decoration: build nothing. **One
  carve-out per video:** an emotional beat may carry feeling instead of fact (S2's fireworks,
  S4's colour washes) if you can name the emotion in one word.
- **Never invent a metric**, never ship a placeholder container (`Hook 1 / Hook 2`, empty
  rows), never build a comparison from duplicate assets. **Work the acquisition ladder before
  you ask or omit** — extract frames from footage with ffmpeg or `/watch`, screenshot a real
  interface with Chrome, look up a real public figure, generate a texture. Ask the creator
  only for what is genuinely private.
- **Declare a frame contract before you plan beats** — SPLIT-STAGE, NESTED-SCALE, TWO-WORLDS
  or OBJECT-OVER-GROUND. A plan with no contract doesn't get built.
- **Plan the entire video beat by beat before building one composition.** `MOTION-PLAN.md`,
  one row per spoken beat, with a Change column. Read the Change column alone: if it reads
  "card in, card out", it's a slideshow.
- **ONE OBJECT is on screen ≥85% of runtime**, mutating. Not "a graphic" — one object.
- **The motion floor is enforced, not advised:** `python analysis/motion-density.py` —
  ≥25 tweens, ≥6 distinct animated properties, ≤50% fades, ≥1 element with depth, per scene.
  The whole existing corpus fails it, including the best composition in it. That is the point.
- One accent per meaning: red = bad, green = good, gold = the metric/winner. Surfaces are
  **opaque hex — no `rgba()`**. No graphic may darken the frame.
- Entrances 0.28–0.42s, hold ≥0.8s, no exits, never bounce/elastic/back.
- Captions: the speaker's **exact words**, uncorrected. ONE line, 2–4 words, 88px
  (`Europa Grotesk SH`), ≤78% frame width, y 920–1130, hard cut — never slide or fade.
- Only one text layer at a time — a content card carrying its own copy gets a **caption mute
  window** written into the MOTION PLAN.
- Zero UI chrome. No watermark, follow banner, progress bar, or slide counter.
- Every mockup account uses `creator.handle` from `brand/brand.json`. If it is blank, ask —
  never invent one, and never lift one from `samples/`: a past build shipped a real person's
  handle that way. Grep the compositions for it before you render.
- Texture is mandatory. Perfectly smooth, perfectly flat output is what reads AI-generated;
  `ig-show/reference/TEXTURE.md` and §3c of `ig-show` enumerate the tells.

Blueprint-first, always: plan in text where changes are cheap, then touch the timeline where
they are expensive. Fast mode ("just do it") shortens the approval step, not the quality bar.
