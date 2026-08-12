# motion-system — The Terminal, in motion

Feez's (@feezkera) locked motion-graphics and editing system for Instagram Reels.
Same design language as the carousel house style, with a time axis added.

**Start here:** open `reference-board/index.html` in a browser. It's the visual guide —
annotated frames, the palette and type rendered live, all 13 blocks animating to spec.

---

## What's in here

```
motion-system/
├── README.md                      ← you are here
├── reference-board/
│   ├── index.html                 ← THE VISUAL GUIDE. open this first.
│   └── frames/                    ← reference stills (devinjatho + his own reel)
├── skill-src/                     ← the installable skill
│   ├── SKILL.md                   ← what the AI reads
│   └── reference/
│       ├── MOTION-LANGUAGE.md     ← the style spec. the rules.
│       ├── BLOCKS.md              ← the 13 named graphics
│       ├── PIPELINE.md            ← HyperFrames → Premiere, technical
│       ├── INTAKE.md              ← the 6 questions + the MOTION PLAN template
│       └── tokens.css             ← the design tokens
├── templates/base/                ← lint-clean HyperFrames starter, 4 working blocks
├── projects/                      ← one folder per reel (created as you go)
└── exports/
```

---

## The system in six lines

1. **The graphics are instrumentation, not decoration.** Every graphic answers *what
   does this measure or prove?* Meters, counters, deltas, curves, diffs, terminal logs,
   receipts. Never swooshes, highlight blobs, arrows, or emoji.
2. **1080×1920.** Near-black `#0F0F10`, off-white `#F0EEE8`, and **one accent declared
   per project** (amber `#E8A03C` is only the default). Max two accent elements per frame.
3. **13 named blocks, 7 reveal verbs.** Pick from the catalog. Don't invent a new visual
   language per reel.
4. **Entrances 0.28–0.42s. Hold ≥0.8s. No exits — the cut is the exit.**
   Never bounce, elastic, back, or linear.
5. **≤8 graphics per 30s reel**, one every 3–5s, exactly one in the first 3 seconds.
6. **Zero UI chrome.** No counters, no watermark, no follow banner.

---

## How to use it

Say something like:

> *"make a meter for the $2,997 number, it lands on the 12-second beat"*
> *"counter for 4 million views, over the hook"*
> *"plan the graphics for this script"* + paste the script

The AI will ask up to six questions in **one** message, write a **MOTION PLAN** for you
to approve, then build and render. It won't touch HTML before the plan is signed off.

Two questions always get asked on a new reel because they can't be defaulted safely:
**accent colour** and **sequence fps**.

Say *"just do it"* to collapse the plan to one line per graphic and skip straight to
the build. The quality bar doesn't move.

---

## Installing the skill

`skill-src/` is packaged as `ig-motion-graphics.skill` in this folder — install it once
and the AI picks it up automatically whenever you mention motion graphics, overlays,
reel graphics, or the editing style.

Related skills that hand off to it:

- **`ig-video-editor`** — owns the cut (silence removal, shot scale, b-roll, pacing).
  When a job needs both, that skill writes the edit blueprint and this one writes the
  MOTION PLAN, cued off the same timecodes.
- **`carousel-designer`** — the same design system, static, at 1080×1350.

---

## Rendering

HyperFrames drives a headless Chrome, so **renders only run on the Mac** — Terminal or
Open Design. Authoring and `hyperframes lint` work anywhere, including Cowork.

```bash
cd motion-system/projects/<slug>

npx hyperframes lint .                          # always, before rendering
npx hyperframes check .                         # Mac only

# overlay — alpha channel
npx hyperframes render . -c compositions/02-meter.html \
  --format mov --resolution portrait --fps 30 --quality high \
  -o renders/02-meter.mov

# full-frame card
npx hyperframes render . -c compositions/01-hook-slam.html \
  --format mp4 --resolution portrait --fps 30 --quality high \
  -o renders/01-hook-slam.mp4
```

`--format mov` and `--format webm` render with transparency. MOV imports straight into
Premiere with the alpha intact.

Every render comes with `renders/IMPORT.md` — a cue sheet listing each file, its
timecode, track, and blend mode.

---

## Two things the reference board is blunt about

Both from tearing down `4 million views in 1 day 0 dollars.MP4`:

1. **The white chart card over dark footage** is the loudest amateur tell in the video.
   Data goes on a dark plate with a 1px stroke; screenshots go inside a Proof Panel at
   ~72% brightness.
2. **One shot scale held for 36 seconds** is the real retention problem, and no graphic
   fixes it. Alternate scale beat to beat.
