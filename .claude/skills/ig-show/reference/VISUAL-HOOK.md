# VISUAL HOOK — the first graphic is not a graphic

The opening graphic is a **different object** from every other graphic in the reel, with its
own rules. Building it like a normal beat is why hooks come out weak.

Every other graphic answers a sentence. **The visual hook answers "why should I stay?"** —
before the viewer has heard a full sentence, and while their thumb is still moving.

> Measured from S3 (`samples/…dbw.mp4`, the "STOP USING HOOKS" reel), which is the
> best-performing hook in the reference set. Numbers below are pixel measurements off
> 720×1280 frames, converted to 1080×1920 by ×1.5.

---

## 1. SPG — what the hook must contain

A graphic visual hook visually represents the **verbal** hook. It has three parts and all
three are required.

### S — Summarize

The whole video, compressed to **3–7 words**. Not the first sentence of the script; the
*claim*. If you cannot say it in 7 words, you do not yet know what the video is about.

S3: `STOP USING HOOKS` — three words for a 51-second video.

### P — Power word

**At least one** word that provokes an emotional or psychological response, and it takes the
accent colour. A power word is dramatic, not descriptive.

| Power | Not power |
|---|---|
| STOP · NEVER · KILLING · STEAL · BROKE · WASTED · GUESSING · SECRET · BANNED · DEAD | learn · improve · tips · guide · better · how to · understand |

S3's is `STOP`, in red, on its own line above the noun.

**The power word gets its own line where possible**, so the eye lands on it first and the
noun resolves it. `STOP USING` / `HOOKS` is two beats, not one sentence.

### G — Graphic

**One** graphic, doing exactly one of these three jobs:

| Job | What it shows | Use when |
|---|---|---|
| **Preview of the value** | what the viewer will learn or get | the video teaches a method |
| **Borrow interest** | something more famous than you — a known brand, a huge number, a recognisable app | you have no proof of your own |
| **Before → after** | the transformation, both states visible at once | the video promises a change |

S3 uses *preview of the value*: a retention curve falling off a cliff — "here is the problem
this video fixes", stated as a shape with units.

**One graphic. Not three.** The hook is the one place where adding a second object always
costs more than it gains.

---

## 2. The lockup — measured

The hook is a **type lockup with one proof card underneath it**, and it is big.

```
                    ┌─────────────────────────┐
   y 637–802        │   POWER WORD (accent)   │   line 1, accent colour
   y 780–945        │   THE NOUN (white)      │   line 2, white, LARGER
                    └─────────────────────────┘
   y 980–1250       ┌─────────────────────────┐
                    │   ONE wide, short       │   the proof card
                    │   proof card            │
                    └─────────────────────────┘
```

| Property | Value @1080×1920 | Measured from S3 |
|---|---|---|
| Line 1 font-size | **108px** | — |
| Line 2 font-size | **118px** | — |
| Line 2 is larger than line 1 | **always** | the noun is the payload |
| Block width | **~74% of frame for line 1**, ~50% for line 2 | matched-scale side-by-side |
| Alignment | **centred as a block**, lines centred on each other | — |
| Line 1 fill | vertical **gradient**, light→deep, in `--sig-down` red (bad/stop) or `--sig-up` green (good/do) | red |
| Line 2 fill | vertical gradient, white → light grey | white |
| Case | ALL CAPS, both lines | — |
| Face | **the caption face**, at hook scale — see below | — |
| Tracking | tight, ~-0.01em | — |
| Bloom | **required** — coloured glow matching each line's own colour | red glow on line 1 |
| Dark halo | **required** — so the type holds over any footage | — |
| Proof card | **wide and short** — ~72% frame width, ~9–14% frame height | x100–620, y540–660 @720 |
| Gap, text → card | ~40px | — |

> ⚠️ **The sizes above were corrected on 2026-08-15.** They were first recorded as 96/104px
> and "≤72% block width" from a *zoomed crop*, which understated them. A matched-scale
> side-by-side against the reference frame showed the reference power line spanning **74%**
> of frame width against our 65%. **Measure a hook by compositing it beside the reference
> frame at the same pixel width** — a crop will lie to you about scale.

### Use the caption face, not `--font-display`

The reference's hook type and its body captions are visibly **one family**. That is the
correct relationship, because the lockup *replaces* the caption for those seconds — it
should read as the same voice, just louder.

There is also a practical reason: `--font-display` (Anton) did not resolve in a real
composition and silently fell back to a mid-weight grotesque, which killed the whole effect.
The caption face is loaded from a local `@font-face` and is guaranteed. **Verify the face in
a rendered frame** — a fallback is invisible in the markup and obvious in the pixels.

**The proportions are the whole trick.** Line 2 bigger than line 1, and a proof card that is
*wide and short* rather than square. A tall card under the type reads as two competing
objects; a wide short one reads as a base the type sits on.

### Gradient fill + bloom, and neither is optional

Reference hook type is **not flat colour**. It carries a vertical gradient — light at the
top, deep at the bottom — plus a coloured bloom and a dark halo. Flat type over footage
reads as a subtitle, not a title, and the gradient is most of the difference between "a red
word" and "a title".

`text-shadow` **cannot** be combined with a clipped gradient: the shadow renders through the
transparent fill and reads as a blob behind the glyphs. Use `filter: drop-shadow()`, which
respects glyph alpha.

```css
.hook__line--power {
  background: linear-gradient(180deg, #FF7A7A 0%, #EB0408 52%, #A80206 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; color: transparent;
  filter: drop-shadow(0 0 30px rgba(235, 4, 8, .72))   /* colour bloom */
          drop-shadow(0 0 12px rgba(235, 4, 8, .55))
          drop-shadow(0 5px 16px rgba(0, 0, 0, .92));  /* dark halo */
}
```

Both are in `tokens-viral.css` as `.hook__line--power` / `--power-up` / `--noun`; compose
from those rather than re-deriving the shadow stack per project.

---

## 3. It holds still

**The hook lockup does not move after it lands.** S3's holds, unchanged, for its entire
life. There is no drift, no scroll, no loop, no ambient motion.

| | |
|---|---|
| Entrance | one STAMP, **≤0.30s**, `expo.out`, both lines together or 60ms apart |
| Then | **nothing.** It holds. |
| Life | **≥2.5s** — long enough to be read twice |
| Exit | none. The cut is the exit. |

The proof card may have **exactly one** internal event (a line drawing in, a number
resolving) inside the first second, then it holds too.

This is the one place where the "something changes every 1.5s" rule is deliberately
suspended. The hook's job is to be *read*, and a moving target cannot be read by a thumb
that has not stopped yet. **Motion in the hook is a bug.**

---

## 4. The hook lockup replaces the caption

While the hook lockup is on screen, **the caption track is silent.** The lockup *is* the
caption for those seconds — bigger, better set, and carrying the accent.

Two competing text layers in the first three seconds is the single fastest way to look
amateur. See the arbitration rule in `SKILL.md` — it applies for the whole reel, but it is
absolute here.

---

## 5. Banned in a hook

- **A scrolling, drifting, or looping object.** Nothing that moves after 0.3s.
- **More than one graphic.**
- Small type. Anything under ~64px cap height is a caption, not a hook.
- A graphic tucked into a corner or a side column — the hook is centred and it is big.
- Flat type with no bloom and no dark halo.
- A container with placeholder contents (see `DEVICES.md §4`) — doubly banned here.
- The power word in white while something else takes the accent.
- Line 2 smaller than line 1.
- A tall or square proof card.
- **Starting on bare footage.** The lockup is on screen by frame 3 at the latest.

---

## 6. Worked example — this repo's own reel

Verbal hook: *"Most people will tell you to just write a good hook, but how do you know if
your hook's actually good?"*

**A first attempt failed** and is worth recording. It rendered a column of nine small reel
cards in the left third, drifting upward, each carrying a phrasing of the same advice, with
`?` badges stamping on at 2.20s. It satisfied "show the noun", it satisfied the density
rule, `check` passed, and it was **wrong**:

- the type was 23px — a hundredth of the reference's presence
- it *moved continuously*, so there was nothing to read
- it had no summarize, no power word, and no single graphic
- it lived in a side column instead of the centre
- the caption ran underneath it the whole time, competing

**The fix, by SPG:**

| | |
|---|---|
| **S** | `STOP GUESSING YOUR HOOKS` — 4 words |
| **P** | `STOP` — and `GUESSING`, both on line 1, in red |
| **G** | *before → after*: `👁 ?` → `👁 52.9K`, one wide short card |

```
STOP GUESSING          <- red, 96px, bloom
YOUR HOOKS             <- white, 104px, bloom

┌───────────────────────────────┐
│   👁 ?      →     👁 52.9K    │   <- one wide short card
└───────────────────────────────┘
```

Lands as one STAMP at 0.10s, holds to 4.50, no motion in between, captions silent
throughout.
