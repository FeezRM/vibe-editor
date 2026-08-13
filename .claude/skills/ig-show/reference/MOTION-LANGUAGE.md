# MOTION LANGUAGE — the spec

Everything here is a rule, not a suggestion. If a graphic violates one, it is wrong even
if it looks nice.

Companions: [DEVICES.md](DEVICES.md) (which graphic for which line) ·
[BLOCKS.md](BLOCKS.md) (the catalogue) · [TEXTURE.md](TEXTURE.md) (the craft layer) ·
[PIPELINE.md](PIPELINE.md) (build and deliver) · `tokens-analog.css` / `tokens-digital.css`.

---

## 0. The thesis

> **Graphics are instrumentation, not decoration.**

Every graphic on screen must look like a readout from something that is *measuring*: a
dial, a counter, a delta, a curve, a scale, a ledger, a log line. Not a sticker, not a
swoosh, not a highlight blob.

If you cannot answer *"what is this measuring or proving?"* — delete it. The gate is in
[DEVICES.md §0](DEVICES.md).

---

## 1. Two skins

One system, two registers. Same variable names, same class names, same block logic — a
composition built against one renders correctly under the other.

| | **ANALOG** *(default)* | **DIGITAL** |
|---|---|---|
| Register | vintage brass instrument | terminal / readout |
| Ground | `#0B0C0A` + contour texture | `#0F0F10`, flat |
| Ink | `#EDE6D6` bone | `#F0EEE8` off-white |
| Accent | `#C9A24B` brass, 5-stop metal ramp | `#E8A03C` amber, flat |
| Signature block | `THE DIAL` — needle sweeping a tick arc | `THE METER` — hard-edged fill bar |
| Linework | tapered, round caps, engraved | even-weight, butt caps |
| Type | Tactic display · Cinzel engraved · Europa caption | Tactic display · JetBrains Mono · Europa caption |
| Texture | grain 12%, contour, 15fps stutter | grain 7%, no contour, no stutter |
| Use for | most content — story, proof, money, systems | tooling, code, build-in-public, data |

**ANALOG is the default.** Reach for DIGITAL only when the subject is literally
computational. Declare the skin once per project by copying the matching tokens file to
`tokens.css`; never mix the two in one reel.

---

## 2. Canvas

| | Value | Why |
|---|---|---|
| Composition | **1080 × 1920** | Overlays render full-frame so they land in Premiere at 100% scale — never at a size that needs hand-positioning |
| FPS | **match the sequence.** Default 30 | A mismatch is what makes overlays stutter, and it is not fixable in Premiere |
| Safe zone | top **240px**, bottom **420px**, sides **90px** | Platform chrome covers this. Nothing load-bearing lives there |
| Caption band | **y 864 – 1152** (45–60% of height) | See §6 — this is deliberately higher than a bottom-third band |
| Delivery | `.mov` alpha for overlays · `.mp4` for cutaways | [PIPELINE.md](PIPELINE.md) |

---

## 3. Colour

Three roles. That is the whole system.

```
GROUND   near-black.  never pure #000 — pure black reads flat and digital
INK      bone/off-white.  never pure #FFF
ACCENT   declared per project.  brass (analog) / amber (digital) are defaults
```

Derived neutrals are in the tokens files. **Do not invent new greys.**

### Accent law

- **Maximum two accent elements on screen at once.**
- The accent marks *the one thing that matters in this beat* — the live value, the lit
  segment, the winning row. Never a border, never a background, never a whole word of
  body copy.
- A second signal colour (oxblood `--sig-down`, forest `--sig-up`) is allowed **only where
  it carries meaning**: inside a diff, a delta, a crash, or semantic caption emphasis
  (see §6). Never as styling.
- Gold must be a **5-stop ramp with an off-centre specular**, never a flat hue plus a
  bevel. [TEXTURE.md §6](TEXTURE.md).

### The white-box ban

**No graphic ever uses a light background over footage.** A solid white card over a dark
grade blows the grade, reads as a pasted screenshot, and flattens the depth of the shot —
one element undoing the whole look. Data lives on `--plate` with a 1px `--stroke`. A
genuinely white screenshot goes inside a `THE PROOF PANEL` at ~72% brightness.

---

## 4. Type

Four faces, one job each. **Never mix two inside a single element.**

| Role | Face | Size | Tracking |
|---|---|---|---|
| **Display** — hook slams, headlines | `TacticSans-UltIt` | 110–190px | `-0.020em` |
| **Caption** — burnt-in spoken word | `Europa Grotesk SH` | 76–92px | `-0.015em` |
| **Engrave** — instrument micro-labels, radial numerals | `Cinzel` (analog) / `JetBrains Mono` (digital) | 22–34px label, 64px numeral | **`+0.180em`** |
| **Readout** — counters, coordinates, timecode | `JetBrains Mono` | 34–96px | `0` |

Rules:

- **Tracking is the craft tell.** `+0.180em` on engraved micro-labels is what makes them
  read as stamped into metal rather than typed into a browser. It is not approximate.
- Line-height `0.94` display, `1.35` body.
- `font-variant-numeric: tabular-nums` on **every** number that changes over time.
- **Never `<br>` inside body copy** — set `max-width` and let it wrap. `<br>` is for
  deliberate one-word-per-line display type only.
- Display and caption faces are **ALL CAPS**. The engraved face is always caps.
- Copy is the creator's voice: lowercase in the script, blunt, slang intact. Do not
  grammar-correct. Caps is a *rendering* choice, not a rewrite.

### Word budget

| | Max words |
|---|---|
| Hook slam | 7 |
| Full-frame card | 14 |
| Overlay label / chip | 5 |
| Caption line | 4 |

If the copy doesn't fit, **cut the idea — don't shrink the type.**

⚠️ The licensed faces must be **installed on the render machine**. Do NOT write
`@font-face` rules — HyperFrames injects its own and a hand-authored one silently kills
the entire stylesheet. See [PIPELINE.md §1](PIPELINE.md).

---

## 5. Motion

### Timing law

| | Value |
|---|---|
| Entrance | **0.28 – 0.42s.** Never slower |
| Hold (nothing moving, fully readable) | **≥ 0.8s** — the viewer has to *read* it |
| Exit | **there isn't one.** The cut is the exit |
| Overlay life | 1.4 – 3.0s |
| Cutaway life | 1.8 – 3.5s |

**Exits are banned** except on the final element of a composition. This is also a hard
HyperFrames rule — outgoing content must be fully visible when the transition fires.
Fading a graphic out before cutting away wastes 0.4s of a 30-second video and reads as
hesitation.

### Easing

```
ENTER    power3.out      fast arrival, long settle — the "lands" feeling
NUMBER   power2.out      counters, dials, anything counting
SNAP     expo.out        chips, stamps, single-frame lands
DRAW     power2.inOut    engraved stroke-dashoffset reveals
SETTLE   power1.inOut    the needle coming back off its overshoot
AMBIENT  sine.inOut      breathing, drift
MACHINE  none (linear)   continuous ring rotation ONLY
```

**Never** `bounce`, `elastic`, or `back` on anything a viewer reads. Bounce is the single
fastest way to make premium content look like a 2021 template. `linear` is banned
everywhere except a persistently rotating ring, where it correctly reads as *machine*.

### Choreography

- Offset the first tween **0.10–0.20s** in. Nothing starts at t=0.
- **At most 1–2 elements moving at any moment.** Everything-at-once is the loudest
  generated-content tell there is.
- **Stagger 60–120ms** between siblings. Not 300ms+ (reads broken), not 0 (reads
  templated).
- Elements enter on **one axis only** — `y` OR `x` OR `scale`. Combined transforms read
  as template.
- **Hold 300–800ms between beats.** Cheap work never holds; it just keeps moving.
- Ambient motion on anything living >1.5s — a 2% breath, a 1px rule pulse, a slow ring
  rotation. Static graphics look dead against moving A-roll.
- No `repeat: -1`. Compute finite: `Math.ceil(duration / cycle) - 1`.

### Mechanical motion — the analog signature

Real instruments have mass. Two moves encode it:

**Needle sweep** — throw past the target, then settle back.

```js
tl.to(needle, { rotation: target + 3, duration: 0.60, ease: "power3.out" })
  .to(needle, { rotation: target,     duration: 0.35, ease: "power1.inOut" });
```

A plain ease-out decelerates to a dead stop, which reads weightless. The 3° overshoot is
the difference between a graphic and an instrument. Overshoot stays ≤5° — beyond that it
becomes bounce, which is banned.

**Mechanical counter** — discrete integer stops, never a smooth tween through fractions.
Use `steps()` or GSAP `roundProps`.

### The stutter

Animate smoothly, then step mechanical motion down to **~15fps** (`--stutter-fps`) so it
judders very slightly against the 30fps render. Motion that is *too* smooth is the
loudest generated tell; nothing physical moves that cleanly. Full recipe and the list of
what to exclude: [TEXTURE.md §5](TEXTURE.md).

### The reveal vocabulary

Nine verbs. If a graphic needs a tenth, it is probably two graphics.

| Verb | Motion | Use for |
|---|---|---|
| **SLAM** | scale 1.06→1.00 + opacity, 0.18s `expo.out` | hook lines, verdicts |
| **WIPE** | `clip-path` inset 100%→0%, L→R, 0.34s `power3.out` | headlines, rows, log lines |
| **COUNT** | value tween, `tabular-nums`, 0.9s `power2.out` | any real quantity |
| **FILL** | `scaleX` 0→n from left, 0.7s `power2.out` | meters, bars |
| **SWEEP** | needle rotation + overshoot + settle | dials, gauges, compasses |
| **DRAW** | `stroke-dashoffset`→0, 1.2s `power2.inOut` | engraved linework, curves, rails |
| **PRINT** | per-character, 28ms/char, deterministic | terminal logs, typed claims |
| **STRIKE** | rule sweeps L→R across text, 0.22s `expo.out` | killing a claim |
| **STAMP** | scale 1.10→1.00 + opacity, 0.14s `expo.out`, no drift | chips, badges, annotations |

---

## 6. Captions

Captions are part of the motion system, not a separate thing. `ig-captions` owns building
them; this section owns how they look.

### Placement — a deliberate correction

**Caption band: y 864–1152 (45–60% of frame height).**

This is **higher** than a conventional bottom-third band, and the change is intentional.
With eyes on the upper third, this band sits *under the chin*. Captions parked in the
bottom third force the viewer to choose between watching the face and reading the words —
the eye cannot do both at that separation. Two independent sources agree on the higher
placement.

Also: keep clear of the right-side action rail (avoid centreX > ~0.85) and never let a
graphic and the caption band occupy the same space.

### Style

- `Europa Grotesk SH`, 76–92px, ALL CAPS, centred in the band.
- Legibility: 4px blur / 42% black drop shadow. **No stroke, no box.**
- 2–4 words per group, or word-by-word, synced to speech.
- Rhythm follows cut rhythm — when speech speeds up, captions speed up.

### Emphasis — colour and scale, not weight

The caption face ships in **one weight**, so weight-based emphasis is unavailable. This
turns out to be an improvement: colour can carry meaning where weight cannot.

| Class | Colour | Means |
|---|---|---|
| `.pop` | accent | the live value / the thing that matters |
| `.pop--bad` | oxblood | the wrong way, the old way, the myth |
| `.pop--good` | forest | the right way, the fix |

**One emphasised word per line, maximum.** That word is the one hit hardest in the audio.
Emphasis also scales `1.14em` so it survives at scroll speed.

Full technique: [DEVICES.md §2](DEVICES.md).

---

## 7. Layout

- **Left-aligned on one axis** — every graphic shares `--margin-x` (96px). Centring is
  reserved for full-frame cards, end cards, and centred instruments.
- Overlays occupy **one of five docks**, declared explicitly, never free-floating:

```
DOCK-TL   x 96,  y 300     chips, source tags, status
DOCK-BL   x 96,  y 1260    the workhorse — counters, deltas, stacks (BELOW the caption band)
DOCK-R    x 620, y 620     proof panels, inset screens
DOCK-C    centred, y 760   dials, compasses, centred instruments
DOCK-FULL full frame       cards, hook slams, mock UI, end cards
```

- **Never two overlays on screen at once.** One graphic, one idea, one beat.
- Scrim only the graphic's **own bounding box, feathered 40px** — never the frame. A
  full-frame scrim kills the practical lighting, which is the shot's whole value.
- **Never park a graphic over the face.**

---

## 8. Banned

- Light or white cards over footage
- Emoji, flying icons, arrow doodles, generic icon-pack glyphs
- Neon / cyan-on-dark / purple-to-blue gradient text — the generated-design tells
- `background-clip: text` *hue* gradients (the metal ramp is the one exception)
- `box-shadow` on panels — use the 1px stroke, or a print-registration offset
- Glow so bright it clips
- `bounce` / `elastic` / `back` easing; `linear` outside a rotating ring
- More than one overlay at a time; more than two accent elements per frame
- Exit animations on anything but the final element
- Slide counters, `@handle` watermarks, "FOLLOW FOR MORE" banners, progress bars —
  **zero UI chrome**
- `Math.random()`, `Date.now()`, `repeat: -1`, unseeded `feTurbulence`
- Any graphic that doesn't measure, prove, or compare something

---

## 9. Self-check — before anything renders

- [ ] Every graphic answers "what does this measure or prove?"
- [ ] One skin, declared in `tokens.css`, not mixed
- [ ] Accent ≤2 per frame, marking the live value
- [ ] Nothing light over footage; no white boxes
- [ ] Engraved tracking `+0.180em`; `tabular-nums` on live numbers
- [ ] One dock per graphic; never two overlays at once; nothing over the face
- [ ] Captions in the **864–1152** band, ≤1 emphasised word per line
- [ ] Entrances 0.28–0.42s, hold ≥0.8s, **no exits**
- [ ] ≥3 distinct eases, 60–120ms staggers, no bounce/elastic/back
- [ ] Needles overshoot ≤5° and settle; mechanical motion stepped to `--stutter-fps`
- [ ] Ambient motion on anything living >1.5s
- [ ] Texture stack present ([TEXTURE.md §11](TEXTURE.md)); grain ≤15%, static
- [ ] Clear of safe zones and the caption band
- [ ] ≤8 graphics per 30s, one every 3–5s, exactly one in the first 3s
- [ ] Zero UI chrome
- [ ] Deterministic: no random, no clock, no infinite repeat, seeds fixed
