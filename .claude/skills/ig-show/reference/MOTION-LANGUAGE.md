# MOTION LANGUAGE — the spec

Everything here is a rule, not a suggestion. If a graphic violates one it is wrong even if
it looks nice.

Companions: [TEARDOWN.md](TEARDOWN.md) (the evidence) · [DEVICES.md](DEVICES.md) (which
graphic for which line) · [BLOCKS.md](BLOCKS.md) (the catalogue) ·
[TEXTURE.md](TEXTURE.md) (craft layer) · [PIPELINE.md](PIPELINE.md) (build and deliver) ·
`tokens-viral.css`.

---

## 0. The thesis

> **Show the noun.** The graphic depicts the thing being talked about, or it measures
> something with real units. It never restates the caption.

The gate: **mute the video, hide the captions — does the frame still make the point?**
No → delete it.

---

## 1. The skin

**VIRAL is the default**, derived by measurement from reels that performed. `analog` and
`digital` remain in `reference/` for projects already built against them, but they are not
the house style any more and should not be chosen for new creator content.

| | **VIRAL** *(default)* |
|---|---|
| Register | real app UI, real screenshots, real numbers |
| Ground | `#0A0A0B` near-black |
| Ink | `#FFFFFF` **pure white — correct here** |
| Semantic | `#EB0408` bad · `#00E800` good · `#FFC531` metric/winner |
| Signature block | `APP SCREEN` — a rebuilt Instagram interface |
| Type | Anton display · Europa Grotesk SH caption · **Inter for app chrome** |
| Texture | grain 6%, heavy vignette, no stutter, no contour |

---

## 2. Canvas

| | Value |
|---|---|
| Composition | **1080 × 1920** — overlays render full-frame so they land at 100% scale |
| FPS | **match the sequence.** Default 30. A mismatch causes stutter and is not fixable later |
| Safe zone | top **240px**, bottom **420px**, sides **72px** |
| Caption band | block centre **y ~50%**; band y 920 – 1130 |
| Graphic stage | `.beside` y 200 (default) · `.stage` y 1180 – 1560 (**rare**) |
| Delivery | `.mov` alpha for overlays · `.mp4` for full-frame cutaways |

---

## 3. Colour

```
GROUND   #0A0A0B    near-black
INK      #FFFFFF    pure white
BAD      #EB0408    the old way, the myth, the loser, the drop
GOOD     #00E800    the fix, the new way, the winner
METRIC   #FFC531    view counts, the winning card, the highlight ring
LINK     #3B9DFF    inside app mockups only
```

### The colour law

- **Colour carries meaning, never styling.** Red because it is the wrong way; green because
  it is the right way; gold because it is the number that matters.
- **More than one may share a frame — but only when each carries a different meaning.** A
  comparison frame legitimately shows a red loser, a green winner and a gold metric at once.
  Three colours doing three jobs is correct; three colours doing decoration is not.
- Bad/good only ever appear as a **pair with an adjacent counterpart** in the script.
- Inside an app mockup, use the app's real colours. Authenticity beats palette discipline
  there — that is the whole point of the block.

### Backgrounds

Full-frame cutaways use a subtle radial lift (`.cutaway`). **Never a hue gradient as the
ground.** No white cards over footage; a real light-mode screenshot goes inside a device
frame at reduced brightness.

---

## 4. Type

| Role | Face | Size | Tracking |
|---|---|---|---|
| **Caption** | `Europa Grotesk SH` | **88px** body / **140px** hook · **one line, max 78% of frame** | `-0.015em` |
| **Display** — headlines inside cutaways | `Anton` | 90–150px | `-0.010em` |
| **App chrome** — inside any mockup | `Inter` | 22–34px | normal |
| **Readout** — counters, countdowns | `JetBrains Mono` | 34–110px | `0` |

Rules:

- **No serif anywhere in this skin.** The old engraved `Cinzel` micro-label at `+0.180em` is
  gone; it read as a museum placard on content that needed to read as a phone screen.
- `font-variant-numeric: tabular-nums` on **every** number that changes over time.
- Never `<br>` inside body copy — set `max-width` and let it wrap.
- Captions are ALL CAPS. Caps is a *rendering* choice, never a rewrite.
- **Never use the brand display face inside an app mockup.** Instagram does not set its bio
  in Anton, and the moment yours does, the mockup stops reading as real.

### Word budget

| | Max words |
|---|---|
| Caption | **4**, on one line — never two lines |
| Headline in a cutaway | 7 |
| Annotation label | 6 |
| Metric badge | 2 (`1.2M`, `28.8M VIEWS`) |

If the copy does not fit, **cut the idea — do not shrink the type.**

---

## 5. Motion

### Timing law

| | Value |
|---|---|
| Entrance | **0.28 – 0.42s** |
| Hold (nothing moving, fully readable) | **≥ 0.8s** |
| Exit | **there isn't one.** The cut is the exit |
| Overlay life | 1.5 – 3.0s |
| Cutaway life | 2.0 – 4.0s |

### Easing

```
ENTER    power3.out      fast arrival, long settle
NUMBER   power2.out      counters, charts, anything counting
SNAP     expo.out        badges, stamps, single-frame lands
DRAW     power2.inOut    stroke-dashoffset reveals
SETTLE   power1.inOut    between beats
AMBIENT  sine.inOut      breathing, drift
MACHINE  linear          a continuously scrolling wall, and nothing else
```

**Never** `bounce`, `elastic`, or `back`. Bounce is the fastest way to make premium content
look like a 2021 template.

### Choreography

- Offset the first tween **0.10–0.20s** in. Nothing starts at t=0.
- **At most 1–2 elements moving at any moment.**
- **Stagger 60–120ms** between siblings.
- Elements enter on **one axis only** — `y` OR `x` OR `scale`.
- **Hold 300–800ms between beats.**
- Ambient motion on anything living >1.5s — a slow drift on a phone, a pulsing marker.
- No `repeat: -1`. Compute finite cycles.

### The reveal vocabulary

| Verb | Motion | Use for |
|---|---|---|
| **STAMP** | scale 1.06→1.00 + opacity, 0.16s `expo.out` | cards, badges, metrics |
| **WIPE** | `clip-path` inset 100%→0%, 0.34s `power3.out` | rows, screens, headlines |
| **COUNT** | value tween, `tabular-nums`, 0.9s `power2.out` | any real quantity |
| **FILL** | `scaleX` 0→n from left, 0.7s `power2.out` | bars, meters |
| **DRAW** | `stroke-dashoffset`→0, 1.0s `power2.inOut` | chart lines, annotation boxes |
| **PRINT** | per-character, 28ms/char, deterministic | typing into a real field |
| **SEAT** | drop from above + settle, 0.28s `power3.out` | tier layers, plates landing |
| **PRESS** | scale 0.96 over 0.10s then release | buttons in THE INTERACTION |
| **FLOOD** | radial wash rises over 0.25s, holds | COLOUR WASH |
| **FLASH** | placeholder goes pure white + blank, 0.10s `expo.out`, holds 0.12s, then the real content resolves into it over 0.18s | **every reveal on a persistent object** — see `BLOCKS.md 02` |
| **LIGHT** | one element of an object already on screen changes state (grey→white→accent) while everything else holds still | element-level highlight |

---

## 6. Captions

`ig-captions` owns building them; this section owns how they look.

- Block centre **y 49–57%** of height. Deliberately higher than a bottom third so the eye
  is not forced to choose between the face and the words.
- `Europa Grotesk SH`, **88px** body (cap ~59px) / **140px** for the hook block only, ALL CAPS, centred, **one line**.
- **HOUSE RULE: one line, 2–4 words. Never two lines.** A deliberate deviation from the
  references, which use two-line blocks.
- **Max line width 78% of the frame** — the constraint that governs the look. If a group
  overflows, split it into two captions; never shrink the type.
- Legibility is a **glow**, not a stroke and not a box: a dark halo plus a soft coloured
  bloom matching the text colour.
- **Accent the payload WORD, inline** — `How To **MELT** Fat Off Your Body`, `WRITE **5**
  DIFFERENT`. A whole line may take the colour only when the line *is* a complete payload
  phrase (`STOP USING` / `HOOKS`, `DISGUSTINGLY` / `EASY`).
  ⚠️ Do not accent a line just because it contains a keyword: a rule of "colour the line
  containing the accent word" turned `to waste so` entirely red in a build — an arbitrary
  slice of a sentence, which means nothing. Verified and fixed by render, 2026-08.
- **Accent ~40% of blocks; leave ~60% plain white.**
- Rhythm follows cut rhythm.

---

## 7. Layout

- Graphics are **big**, and the default is `.cutaway` (full frame) or `.beside--l/r`
  (one object at head height, `top: 200px`, `width: 432px`, in the empty half of frame).
- **`.stage` — the full-width bottom band — is RARE.** One instance across all three
  references. Do not make it the default; an edit where every graphic is a dark rounded
  rectangle across the bottom is this system's most recognisable failure mode.
- `.flank--l` + `.flank--r` together only for a two-artefact comparison.
- **Graphics render opaque.** A graphic that is on screen but is no longer the subject
  takes `.dim` (30%) and stays crisp. Nothing renders as a translucent haze.
- **Never two graphics on screen at once**, unless they are the two halves of one
  comparison, or one of them is `.dim` and persisting from an earlier beat.
- **Never park a graphic over the face.** Pull A-roll frames and check where the face and
  hands actually are before placing anything — `.beside` goes on the side he is *not* on.
- Keep clear of the caption band and the safe zones.

---

## 8. Banned

- Panels whose content is a headline and a rule — that is a caption
- Restating the caption in a second typeface
- Empty numbered slots, placeholder contents, invented metrics, unlabelled charts
- Serif type, engraved tracking, "instrument" styling, brass
- Emoji as decoration, flying icons, arrow doodles, icon-pack glyphs
- Light or white cards over footage (real dark-mode app UI is fine)
- Neon/cyan-on-dark/purple-to-blue gradient text
- `box-shadow` on panels; glow so bright it clips
- `bounce` / `elastic` / `back`; `linear` outside a scrolling wall
- Exit animations on anything but the final element
- Watermarks, follow banners, progress bars — zero UI chrome
- `Math.random()`, `Date.now()`, `repeat: -1`, unseeded `feTurbulence`
- **Any graphic that fails the mute test**

## 9. Self-check — before anything renders

- [ ] Every graphic survives the mute test
- [ ] Every graphic shows a real object or a real measurement
- [ ] No invented numbers; charts have labelled axes with real units
- [ ] App mockups use Inter, not the brand display face
- [ ] Colour is carrying meaning; each colour on frame does a different job
- [ ] Placement is mixed and mostly cutaway / beside — not everything docked to `.stage`
- [ ] Every graphic opaque; only a non-subject graphic dimmed, to 30%
- [ ] Captions **88px (cap 58–65px), ONE line, ≤78% of frame**, centred in the band, glow not stroke
- [ ] Caption geometry **measured** with `analysis/measure.py`, not eyeballed
- [ ] Entrances 0.28–0.42s, hold ≥0.8s, no exits, no bounce
- [ ] ≥3 distinct eases, 60–120ms staggers, 1–2 movers at a time
- [ ] Progressive builds persist state across cutaways
- [ ] Clear of safe zones, caption band, and the face
- [ ] **A graphic on screen ≥85% of runtime; no graphic-free stretch over ~2s; one in the first 3s**
- [ ] The persistent object mutates element by element, one mover at a time
- [ ] Reveals use the pre-reveal white flash; recurring graphics add state, never repeat it
- [ ] Deterministic: no random, no clock, no infinite repeat, seeds fixed
- [ ] **Composited over a real A-roll frame and actually looked at**
