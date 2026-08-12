# THE TERMINAL, IN MOTION — Feez's Reel Editing & Motion-Graphics Style

The technical spec. Everything in this file is a rule, not a suggestion. If a graphic
violates one of these, it's wrong even if it looks nice.

Companion files: [BLOCKS.md](BLOCKS.md) (the catalog), [PIPELINE.md](PIPELINE.md)
(how it gets built and delivered), [tokens.css](tokens.css) (the actual values).

---

## 0. The one-sentence thesis

> **His graphics are instrumentation, not decoration.**

The brand's enemy is The Pose — people who "can't measure, that's why they pose."
The thesis is *"posting is gambling. building a system isn't."*

So every graphic on screen must look like a **readout from a system that's measuring
something**: a meter, a counter, a delta, a curve, a diff, a log line. Not a sticker,
not a shape, not a swoosh, not a highlight blob.

This is why the style is called **The Terminal**. It's the same design system already
locked for his carousels (`carousel-designer` skill) — this file is that system with a
time axis added. A carousel slide and a reel frame should be recognisably the same
studio.

If you can't answer *"what is this graphic measuring or proving?"* — delete it.

---

## 1. Canvas and technical baseline

| | Value | Why |
|---|---|---|
| Composition size | **1080 × 1920** | 9:16, full IG Reel frame. Overlays render at full frame so they drop into Premiere at 100% scale — never at a smaller size that has to be positioned by hand. |
| FPS | **Match the Premiere sequence.** Default 30. | HyperFrames defaults to 30. His `4 million views` reel was cut at 24. Ask once, then lock it in the project for good. |
| Safe zone | **top 240px, bottom 420px, sides 90px** | IG's own UI (caption, profile, action rail, progress bar) covers this. Nothing load-bearing lives there. |
| Caption band | **y 1180 – 1500** | Where spoken-word captions live. Motion graphics must not fight this band. |
| Delivery | `.mov` (alpha) for overlays, `.mp4` for full-frame cards | See [PIPELINE.md](PIPELINE.md). |

---

## 2. Palette

Three roles. That's the whole system.

```
GROUND    #0F0F10   near-black. Never pure #000.
INK       #F0EEE8   warm off-white. Never pure #FFF.
ACCENT    declared per project. Default #E8A03C (amber).
```

**The accent is a per-project variable, not a fixed colour.** It is asked for at brief
time (see [INTAKE.md](INTAKE.md)) and written into the project's `tokens.css`. Every
block reads `var(--accent)`. Changing one line restyles the whole reel.

Supporting neutrals, derived — do not invent new greys:

```
INK-DIM   rgba(240,238,232,0.55)   labels, secondary readouts
INK-GHOST rgba(240,238,232,0.18)   rules, inactive states, grid
PLATE     rgba(15,15,16,0.86)      the dark panel behind graphics
STROKE    rgba(240,238,232,0.14)   1px panel borders
```

### Accent law

- **Maximum two accent elements on screen at once.** Same rule as the carousels.
- The accent marks **the one thing that matters in this beat** — the live value, the
  filled portion of the meter, the winning row. Never a border, never a background,
  never a whole word of body copy.
- Emphasis inside a sentence comes from **font weight**, not colour.
- A second signal colour (red for "broken", green for "up") is allowed **only inside a
  data block** where it carries actual meaning (a diff, a delta, a chart drop). Never
  as styling.

### The white-box ban

His `4 million views in 1 day` reel put a **solid white chart card** over dark Cave
footage. That single element is the loudest amateur tell in the whole video — it blows
the grade, it reads as a screenshot someone pasted in, and it flattens the depth of the
shot.

**No graphic ever uses a light background over footage.** Data lives on `PLATE` with a
`STROKE` border. If the source is genuinely a white screenshot, it goes inside a
**Proof Panel** (see BLOCKS.md) which crops it, rounds it, darkens it to ~72%
brightness and gives it a 1px stroke so it sits *in* the frame instead of on top of it.

---

## 3. Type

One family, two roles.

| Role | Family | Weight | Size | Tracking |
|---|---|---|---|---|
| **Display** — hook slams, big numbers, card headlines | Inter Tight (fallback: Inter, Helvetica Now Display, SF Pro Display) | 800–900 | 110 – 190px | **−0.028em** |
| **Label** — all-caps tags, units, chip text, axis labels | same family | 600–700 | 22 – 34px | **+0.085em**, uppercase |
| **Readout** — counters, code, terminal, diffs, timestamps | JetBrains Mono (fallback: SF Mono, Menlo) | 500–700 | 34 – 96px | 0 |
| **Caption** — spoken word burn-in | Inter Tight | 800 | 76 – 96px | −0.02em |

Rules:

- **Tracking is the craft tell.** −0.028em on display and +0.085em on caps are not
  approximate. Get them exact.
- Line-height **0.94** on display, **1.35** on body/labels.
- `font-variant-numeric: tabular-nums` on **every** number that changes over time,
  or the digits jitter as they count.
- **Never `<br>` inside body copy** — set a `max-width` and let it wrap. `<br>` is
  allowed only on deliberate one-word-per-line display type.
- Sentence case for display copy, in his voice: **lowercase, spoken, blunt.** Do not
  capitalise or grammar-correct him. ALL-CAPS is for labels and units only.

### Word budget

| Block type | Max words on screen |
|---|---|
| Hook slam | 7 |
| Full-frame card | 14 |
| Overlay label / chip | 5 |
| Caption line | 4 |

If the copy doesn't fit, **cut the idea — don't shrink the type.**

---

## 4. Layout

- **Left-aligned on one axis.** Every graphic in a reel shares the same left margin
  (default `x = 96px`). Centre alignment is reserved for a single full-frame end card
  and nothing else.
- Overlays occupy **one of four docks**, declared explicitly. Never free-floating:

```
DOCK-TL   x 96,  y 300      chips, source tags, timers, "REC"-style status
DOCK-BL   x 96,  y 980      the workhorse. meters, counters, deltas, stacks.
DOCK-R    x 620, y 640      proof panels, inset screens, phone mockups
DOCK-FULL full frame        cards, hook slams, end cards
```

- A graphic in `DOCK-BL` must clear the caption band. If it can't, it becomes a
  `DOCK-FULL` card and you cut to it.
- **Never two overlays on screen at once.** One graphic, one idea, one beat.
- Scrim rule, inherited from the carousels: if a graphic needs the footage darkened
  behind it, **scrim only its own bounding box, feathered 40px** — never the whole
  frame. A full-frame scrim kills the Cave lighting, which is the shot's entire value.

---

## 5. Motion

This is where most "AI motion graphics" fail. The defaults below exist to stop the
generic ease-in-fade-up-everything look.

### Timing law

| | Value |
|---|---|
| Entrance | **0.28 – 0.42s**. Never slower. |
| Hold (fully readable, nothing moving) | **≥ 0.8s** — the viewer has to *read* it |
| Exit | **there isn't one.** The cut is the exit. |
| Total overlay life | 1.4 – 3.0s |
| Full-frame card life | 1.8 – 3.5s |

**Exits are banned** except on the last element of a composition. This is also a hard
HyperFrames rule — the outgoing content must be fully visible when the transition
fires. Fading a graphic out before cutting away wastes 0.4s of a 30-second video and
reads as hesitation.

### Easing — the signature

```
ENTER   power4.out        fast arrival, long settle. the "lands" feeling.
NUMBER  power2.out        counters, meters, anything counting up
SNAP    expo.out          single-frame slams, chips, redactions
AMBIENT sine.inOut        breathing glows, cursor blinks, idle drift
```

**Never** `bounce`, `elastic`, `back`, or `linear` on anything a viewer reads.
Bounce is the single fastest way to make premium content look like a 2021 template.

### Choreography

- Offset the first tween **0.10 – 0.20s** into the block. Nothing starts at t=0.
- **Vary the ease** — at least three different eases per multi-element block.
- **Stagger 60–90ms** between siblings (rows in a stack, digits in a counter).
- Elements enter on **one axis only**: `y` OR `x` OR `scale`, never all three. Combined
  transforms read as "template".
- **Ambient motion is mandatory on anything that lives longer than 1.5s** — a 2% glow
  breath, a 1px rule pulse, a blinking cursor. Static graphics look dead against moving
  A-roll.
- No `repeat: -1`. Compute finite repeats: `Math.ceil(duration / cycle) - 1`.

### The reveal vocabulary — pick one per block

| Name | Motion | Use for |
|---|---|---|
| **SLAM** | scale 1.06 → 1.00, opacity 0 → 1, 0.18s `expo.out` | hook lines, single numbers, verdicts |
| **WIPE** | `clip-path` inset 100% → 0%, left to right, 0.34s `power4.out` | headlines, rows, terminal lines |
| **COUNT** | value tween with `tabular-nums`, 0.9s `power2.out` | any number that represents a real quantity |
| **FILL** | `scaleX` 0 → n with `transform-origin: left`, 0.7s `power2.out` | meters, bars, progress |
| **DRAW** | `stroke-dashoffset` → 0, 1.0s `power2.inOut` | curves, charts, connector rails |
| **PRINT** | per-character reveal, 28ms/char, deterministic | terminal logs, code, the CS wedge |
| **STRIKE** | rule sweeps L→R across text, 0.22s `expo.out`, text drops to INK-DIM | killing the enemy's claim |

Seven verbs. If a graphic needs an eighth, it's probably two graphics.

---

## 6. The edit around the graphics

Motion graphics don't rescue a slack cut. These are the A-roll rules the graphics
assume are already true. (Full edit workflow lives in the `ig-video-editor` skill —
this section is the handshake between the two.)

1. **Silence removal first.** Cut *on* the breath, not after it. Raw footage is ~40% air.
2. **Shot-scale alternation.** His `4 million views` reel holds the identical medium
   shot for 36 seconds — that's the real retention problem, not the graphics. Adjacent
   beats must differ in scale: `MED → CU → MED-WIDE → CU`. Push-ins are **2–4%
   over 1.2s**, never a visible zoom.
3. **A graphic is a pattern interrupt.** Budget **one every 3–5s**, max **6–8 per
   30-second reel**. More than that and they stop interrupting anything.
4. **Never place a graphic on a static shot you could have cut instead.** The graphic
   earns its place by adding information, not by covering boredom.
5. **The hook (0–3s) gets exactly one graphic** — a slam or a card. Never both, never a
   meter. Nothing competes with the first line.
6. **Land graphics on the word, not the sentence.** The block's entrance frame is the
   frame the spoken keyword hits. One frame late reads as lag.

### Captions

Captions are part of the motion system, not a separate thing.

- Word-by-word or 2–4 word phrase pops, synced to speech.
- Inter Tight 800, `INK`, 76–96px, centred in the caption band.
- Legibility: **4px blur / 40% black drop shadow.** No stroke, no box.
- **One accent word per line, maximum.** That word is the one he'd hit with his voice.
- His exact words, lowercase. If the transcriber "corrects" his grammar or drops
  "mans", change it back.
- Caption rhythm follows cut rhythm. When he speeds up, they speed up.

### Sound

- Music bed ducked **−18dB** under voice, **out entirely under the hook line**, back in
  on the first beat after.
- SFX are auditory bullet points: a soft low click on a `SLAM` or a chip, a short
  filtered whoosh on a `WIPE`, a rising tick-bed under a `COUNT`. **One SFX per
  graphic, never per word.**
- No airhorns, no cartoon pops, no risers stacked three deep.

---

## 7. Banned list

Visual, from the brand bible — these break positioning instantly:

- Gym mirrors, gym equipment in frame, cars, hotels, watches, branded fits, beach/pool,
  "coffee shop founder" b-roll. *(His `4 million views` reel has gym equipment visible
  behind him. Reframe or relight.)*

Motion-graphic, specific to this system:

- Solid light/white cards over footage
- Emoji, emoji-adjacent glyphs, flying icons, arrow doodles, hand-drawn scribbles
- Neon green / cyan-on-dark / purple-to-blue gradient text — the AI-design tells
- `background-clip: text` gradients
- Drop shadows on panels (use a 1px `STROKE` instead)
- Glow so bright it clips — emissive blowout reads as clip-art. Same failure that
  killed the first two carousel attempts.
- Bounce / elastic / back easing
- More than one overlay on screen at once
- Slide counters, `@handle` watermarks, "FOLLOW FOR MORE" banners, progress bars —
  **zero UI chrome**, same as the carousels
- Any graphic that doesn't measure or prove something

---

## 8. What "good" looks like — the reference read

**@devinjatho** is the closest benchmark in the niche. What actually makes his edits
read premium, from the archived footage in `Research/devinjatho/`:

1. **His overlays are diegetic.** The `● REC` chip, the corner viewfinder brackets, the
   battery icon — they pretend to belong to the camera looking at him. They read as
   *world*, not sticker. Feez's equivalent is instrumentation: his overlays pretend to
   belong to a system that's measuring the content.
2. **Practical colour does the chapter work.** He gels the room red for one reel, green
   for another. The lighting carries the identity so the graphics can stay minimal.
   Feez's Cave equivalent: the single-source laptop glow already does this — protect it,
   don't scrim over it.
3. **Monochrome + one signal colour at a time.** Never a palette.
4. **Proof is a chip, not a paragraph.** A view-count with an eye icon, tucked in a
   corner. Small, quiet, devastating.
5. **In his carousels: bracket tokens.** `[do action]`, `[desirable outcome]` in a
   signal colour inside otherwise plain text — the reader instantly sees the template's
   variables. Worth stealing directly for framework content.

What **not** to take from him: the light `#111`-on-white carousel body copy density
(too much text for Feez's ~19-word budget), and the emoji CTA (`Comment "HOOKS" 👇`).

---

## 9. Self-check before anything renders

- [ ] Every graphic answers "what is this measuring or proving?"
- [ ] Accent used ≤ 2× per frame, and it marks the live value
- [ ] Nothing light-on-dark-footage; no white boxes
- [ ] Display tracking −0.028em, caps +0.085em, `tabular-nums` on live numbers
- [ ] One dock per graphic, never two overlays at once
- [ ] Entrances 0.28–0.42s, ≥0.8s hold, **no exit animations**
- [ ] ≥3 different eases, 60–90ms staggers, no bounce/elastic
- [ ] Ambient motion on anything living >1.5s
- [ ] Clear of the safe zone and the caption band
- [ ] ≤ 8 graphics in a 30s reel, one every 3–5s
- [ ] Zero UI chrome — no counters, watermarks, follow banners
- [ ] Copy is his voice: lowercase, spoken, blunt, "mans" intact
