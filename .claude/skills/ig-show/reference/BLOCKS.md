# BLOCK CATALOG — the viral skin

Every graphic is one of these. Derived by measurement from three reels that performed —
see [TEARDOWN.md](TEARDOWN.md) for the evidence behind each one.

Read [MOTION-LANGUAGE.md](MOTION-LANGUAGE.md) for palette, docks, easing and reveal verbs.
To choose a block from a line of script, use [DEVICES.md](DEVICES.md).

> **The gate every block must pass:** mute the video, hide the captions — does the frame
> still make the point? If not, it is decoration and it does not ship.

---

## Quick reference

| # | Block | Occupies | Life | Use when the line… |
|---|---|---|---|---|
| 01 | **APP SCREEN** | cutaway / beside | 2–4s | names a screen the viewer knows (profile, feed, story, DM, settings) |
| 02 | **PROGRESSIVE BUILD** | cutaway, continuous | whole reel | walks through the parts of one artefact, one at a time |
| 02b | **ELEMENT HIGHLIGHT** | on top of 01–08 | 0.8–1.5s | names one part of something already on screen |
| 03 | **CONTENT + METRIC** | beside / flank | 1.5–3s | points at a real piece of content and its number |
| 04 | **THE COMPARISON** | cutaway / flank | 2.5–4s | sets two things against each other — this vs that |
| 05 | **PHONE IN HAND** | cutaway | 2–4s | shows content *as an object* being held or scrolled |
| 06 | **THE WALL** | cutaway | 1.5–2.5s | says *everyone*, *all of them*, *a million times* |
| 07 | **TIER STACK** | cutaway | 1.5–2.5s ×N | names a rank, level, or percentile |
| 08 | **THE CHART** | stage | 2–3.5s | claims a shape over time — retention, growth, a drop |
| 09 | **THE READOUT** | stage / cutaway | 2–3s | names a deadline, a window, or a live count |
| 10 | **TYPE-IN** | cutaway | 2.5–4s | tells the viewer exactly what to write |
| 11 | **COLOUR WASH** | full frame | 0.8–2s | contrasts a bad phrasing against a good one |
| 12 | **ANNOTATION** | on top of 01–08 | 1–2s | singles out one part of something already on screen |
| 13 | **THE DOCUMENT** | cutaway | 2–3s | offers a resource — the lead magnet, the template |
| 14 | **THE INTERACTION** | cutaway | 1.8–2.6s | the CTA — a button pressed, a comment typed |
| 15 | **HOOK LOCKUP** | centred, huge | 2.5–4.5s | **the first graphic of the reel — always** |

Fifteen blocks, and **eleven of them show a real object.** That ratio is the point.

> **Block 15 is not optional and not interchangeable.** Every reel opens with it. It is the
> only block with its own reference file — [VISUAL-HOOK.md](VISUAL-HOOK.md) — because it
> follows different rules from everything else here: it holds still, it is centred and huge,
> and it silences the caption track.

> **Reach for 01 APP SCREEN first.** Rebuilt interface is ~60% of reference graphic time.
> A reel whose plan contains no recreated app UI is almost certainly wrong — the fallback
> of "cards on a dark plate" reads as a slide deck, not as this style. Verified by
> rebuilding a failing beat as a real Instagram profile grid, 2026-08.

---

## 01 — APP SCREEN

**Shows:** the actual interface being discussed, rebuilt in the app's real dark mode.
**Anatomy:** use the `.ig-*` component classes in `tokens.css` — they already encode
Instagram's metrics (132px avatar, 6px grid gutter, iOS greys, the story-ring gradient).
Chrome uses `--font-ui`, never the brand display face: a mockup that uses your headline
font stops reading as a real app instantly.
**Motion:** the screen WIPEs or scales in as one object (0.30s `power3.out`), then the
element being named lands separately 0.15s later.
**Rules:** get the details right — the gradient ring, the tabular numbers in the stat row,
the blue link. Accuracy is the entire effect. If you would not recognise it at a glance in
someone else's reel, rebuild it.

## 02 — PROGRESSIVE BUILD

**The highest-value pattern in the reference set, and the one that keeps getting missed.**
S1 is nothing but this block for 45 straight seconds. If you build one thing well, build
this.

**Shows:** that a thing has parts, by assembling it across the whole video.
**Anatomy:** an `APP SCREEN` that starts as grey `.skel` bars and gains one real element
per beat — avatar, then name, then bio line 1, then bio line 2, then link, then each
highlight, then the grid. **The object never leaves the frame between beats.**
**Motion:** only the newly-added element animates. Everything already present is static and
fully rendered.

### The three sub-rules that make it work

1. **The pre-reveal white flash — do not skip this.**
   Before real content lands, its placeholder turns **pure white and blank** for a beat,
   *then* the real content resolves into it.
   ```
   grey .skel bar  →  white blank bar (FLASH)  →  real text
   ```
   It is the visual equivalent of "and here's the thing": it puts the eye on the exact spot
   *before* there is anything to read there, so the content arrives somewhere the viewer is
   already looking. It appears on **every single reveal** in S1. A progressive build without
   it is technically correct and feels flat.

2. **One mover at a time. Never two.** That is what makes the moving element read as the
   answer to the sentence being spoken.

3. **State persists, and each appearance ADDS.** Beat 4 shows everything from beats 1–3
   still in place. Never reset to skeleton, never re-animate an element that already
   landed, and never show the same state twice — if a graphic appears twice looking the
   same, one of those appearances is wasted.

**Rules:** build one composition per state rather than one long timeline, so each can be
re-cut independently — but cue them back to back so the object is continuously on screen.
The gap between two states of a progressive build should be zero, not a return to bare
footage.

## 02b — ELEMENT HIGHLIGHT

The atomic operation `PROGRESSIVE BUILD` is made of, usable on its own against any object
already on screen.

**Shows:** which single part of the thing on screen the current sentence is about.
**Anatomy:** one element of an existing graphic changes state — grey → white → accent, or
dim → lit, or placeholder → real. Everything else on the object holds perfectly still and
stays fully rendered.
**Motion:** `LIGHT` (see MOTION-LANGUAGE §5). No layout shift — the element must not move
or resize, or the whole object appears to reflow.
**Rules:** this is the cheapest way to hit the ≥85% graphic-presence target without
building anything new, and it is what the references actually spend most of their graphic
time doing. When a line has no obvious new object, ask what part of the *current* object it
refers to and light that instead.

## 03 — CONTENT + METRIC

**Shows:** a real piece of content with its real number attached.

**Anatomy — re-measured 2026-08-15 off S3, and the old numbers were wrong:**

| Part | Spec |
|---|---|
| Card | `.reel` — **3:4**, **34px radius** |
| Image | **`brightness(1.30) contrast(1.10) saturate(1.08)`** — reference covers are bright |
| Scrim | `.reel__scrim`, bottom-up black gradient |
| Its own caption | `.reel__cap` — **~26px, low, LEFT-aligned**, `--font-ui`, accent word in green |
| Badge | `.metric` — **light frosted pill, dark digits**, bottom-left, inset 20px |
| Winner | `.reel--win` 5px gold outline + `.metric--win` |
| Loser | `.reel--lose` — **`grayscale(1) brightness(.74)`** |
| Minimum width | **~380px.** Below that a cover cannot carry legible copy *and* a badge |

**Motion:** card STAMPs in (scale 0.94→1.00, 0.22s `expo.out`); the metric pill lands 0.12s
later and COUNTs if the number is the point.

**Rules:** the number must be real. This block is worthless with an invented figure —
its whole authority is that the viewer believes the screenshot. If there is no real number,
use a different block.

⚠️ **This card carries its own words, so the burnt-in caption mutes while it is on screen.**
Add the window to the MOTION PLAN's `CAPTION MUTE WINDOWS` block. Two headlines on one frame
is the most common way a structurally-correct build still looks cheap.

⚠️ **Four corrections that each cost an iteration:**
- A **dark** metric pill (`rgba(0,0,0,.66)`, the old token) sinks into a dark thumbnail. The
  badge is meant to pop *off* the artefact.
- **20px radius** reads as a web thumbnail. 34px reads as a phone.
- Copy **centred across the middle** of the cover is a stock-photo caption. Real covers put
  it low and left, over a scrim.
- The loser **desaturates**; it does not fade. 55% opacity read as a rendering fault.

## 04 — THE COMPARISON

**Shows:** that one thing beat another, with both artefacts visible at once.
**Anatomy:** **two** `CONTENT + METRIC` cards in a `.vs` row, or flanking the head via
`.flank--l` / `.flank--r`. Same size, same treatment, differing only in the metric and the
win/lose state.
**Motion:** loser lands first (0.18s), beat of 0.25s, then winner lands and takes the gold
outline. Optionally the loser desaturates further when the winner is named.

⚠️ **Two cards, not three.** S3 shows each cover **big and alone** first, then brings both
together flanking the head. Three cards abreast puts each under ~300px, where the copy and
the badge both stop being legible, and the beat reads as a grid of thumbnails instead of a
comparison. If the script genuinely names three, show them **sequentially** at full size, or
show two and let the third arrive — never three at once.
**Rules:** both must be genuinely comparable — same metric, same window. The loser is never
made ugly; it is just quieter. Making the losing side neutral is the confident move.

⚠️ **Never build this from duplicate assets.** Two copies of the same thumbnail with
different numbers on them is worse than no graphic — the device's entire authority is that
the viewer believes two *different* artefacts are being compared, and identical images void
it instantly. A previous build shipped three copies of the same shot labelled `HOOK 1/2/3`
with different view counts; it read as fake. If only one real asset exists, use
`CONTENT + METRIC` on its own, or build nothing.

## 05 — PHONE IN HAND

**Shows:** content as a physical object rather than as a graphic.
**Anatomy:** `.phone` frame (470px wide, 9:19.5, 54px radius, 10px bezel) with `.phone__notch`,
containing a full app screen. Composite over footage of a hand where available.
**Motion:** a slow drift and slight rotation so it reads as held, not pasted. Content inside
may scroll.
**Rules:** the screen content must be a real screen, not a placeholder. If the phone is not
in an actual hand, keep the drift subtle or it reads as floating clip-art.

## 06 — THE WALL

**Shows:** volume and sameness — *everyone is doing this.*
**Anatomy:** a grid of 9–15 `.reel` cards, all carrying near-identical content, drifting
slowly upward. Monochrome or lightly desaturated so no single cell wins attention.
**Motion:** cells WIPE in row-major on a 40ms stagger, then the whole grid drifts `linear`
(the one place `linear` is correct — it implies endless scroll).
**Rules:** the sameness must be visible in one glance. If the cells look varied, the block
is saying the opposite of what it means.

## 07 — TIER STACK

**Shows:** rank. A pyramid that gains a layer every time a new level is named.
**Anatomy:** `.pyramid` + `.tier--1..6`, bottom (worst) to top (best), colour ramping
`#EB0408 → #FF7A00 → #FFC531 → #9BE300 → #00E800 → #7B5CFF`. Each tier carries its label.
Widths taper toward the apex.
**Motion:** the new layer drops in from above and seats (0.28s `power3.out`); existing
layers do not move. The apex gets a star and a glow only on the final tier.
**Rules:** one layer per named rank, computed from the script — never eyeballed. Like
`PROGRESSIVE BUILD`, **state persists**: the fourth appearance shows all four layers.

## 08 — THE CHART

**Shows:** a shape over time.
**Anatomy:** `.chart` on a `.card`. Hairline grid, **y-axis labelled with real units**
(`100% / 50% / 0%`), **x-axis labelled with real time** (`00:00 → 01:10`). One line, 6px,
round caps, `.chart__line--bad` red or `--good` green with a matching drop-shadow glow.
**Motion:** axes WIPE first, then the line DRAWs (`stroke-dashoffset`→0, 1.0s
`power2.inOut`). A marker STAMPs at the moment the draw passes the point that matters.
**Rules:** **label the axes or do not draw the chart.** An unlabelled curve is a squiggle.
If the underlying numbers are not known, say what the axis measures and let the *shape* be
the claim — but never print a fabricated figure.

## 09 — THE READOUT

**Shows:** a deadline, a window, or a live quantity.
**Anatomy:** `.readout` in tabular mono at ~108px, with `.readout__units` beneath
(`HOURS MINUTES SECONDS`).
**Motion:** COUNT, decelerating, or a live tick for a countdown. Digits never animate
individually — the value tweens and the text rewrites.
**Rules:** real units, real precision. `72:00:00` counting to `71:59:59` sells a 72-hour
window in one second of screen time.

## 10 — TYPE-IN

**Shows:** exactly what to write, typed into the real interface it belongs in.
**Anatomy:** an `APP SCREEN` (story, DM, caption box) with a text field. Characters appear
progressively; variables like `[Name]` are highlighted in `--link` blue.
**Motion:** PRINT at ~28ms/char, built as one span per character on a stagger so it stays
seek-safe. A caret may blink with `steps(1)`, finite.
**Rules:** the copy is the deliverable — it must be the exact wording the creator said.

## 11 — COLOUR WASH

Nearly free, reads instantly, and the strongest per-second device in the whole set.

**Shows:** which of two phrasings is endorsed.
**Anatomy:** `.wash--bad` or `.wash--good` — a full-frame radial flood behind the subject —
plus `.vignette`. The caption keyword takes the matching colour on the same frame.
**Motion:** the wash rises over 0.25s and holds; it does not pulse.
**Rules:** only ever in a bad/good pair, and the pair must be adjacent in the script. A wash
with nothing to contrast against is just a coloured light.

## 12 — ANNOTATION

**Shows:** which part of the thing already on screen matters.
**Anatomy:** `.annot-box` (4px, green for good / red for bad) drawn around a real element,
plus an `.annot-label` beside it.
**Motion:** the box DRAWs, the label WIPEs 0.1s later.
**Rules:** it must sit on top of something real. An annotation with nothing beneath it is a
doodle, which is banned.

## 13 — THE DOCUMENT

**Shows:** the resource being offered, so the CTA is for something visible.
**Anatomy:** a document card in slight 3D perspective (`rotateY` 8–14°), with a real title
and 3–5 real rows. Rows may carry thumbnails.
**Motion:** floats in with a slow parallax drift; rows stagger 70ms.
**Rules:** the contents must reflect what the viewer will actually receive.

## 14 — THE INTERACTION

**Shows:** the CTA as an action rather than an instruction.
**Anatomy:** a real profile card with `.ig-btn` (Follow), or a comment field. The button is
pressed — it depresses, then swaps to `.ig-btn--done` (Following).
**Motion:** press = scale 0.96 over 0.10s, release and swap over 0.14s.
**Rules:** one CTA. No handle, no logo, no banner. On screen ≥1.8s.

## 15 — HOOK LOCKUP

**Full spec: [VISUAL-HOOK.md](VISUAL-HOOK.md). Read it before building.** Summary only here.

**Shows:** why the viewer should stay, before they have heard a full sentence.
**Use when:** always, as the first graphic of every reel. There is no alternative block for
this position.

**Anatomy:** a centred two-line type lockup with **one** wide, short proof card beneath.

```
STOP GUESSING     .hook__line--power   96px, accent colour, bloom + dark halo
YOUR HOOKS        .hook__line--noun   104px, white, LARGER than line 1

┌──────────────────────────────┐
│  ONE wide, short proof card  │  .hook__proof — ~72% frame width, 9–14% height
└──────────────────────────────┘
```

**SPG — all three required:**
- **S**ummarize the whole video in 3–7 words
- **P**ower word, at least one, in the accent colour (`STOP` · `NEVER` · `KILLING` ·
  `WASTED` · `GUESSING` · `BROKE` · `STEAL`)
- **G**raphic, exactly one, doing *preview of the value* / *borrow interest* /
  *before → after*

**Motion:** one STAMP, ≤0.30s, `expo.out`. **Then nothing.** Holds ≥2.5s. No exit.
The proof card may have exactly one internal event inside its first second.

**Rules:**
- **It holds still.** The every-1.5s change rule is suspended here — a thumb that has not
  stopped moving cannot read a moving target. Motion in a hook is a bug.
- **The caption track is silent for its whole life.** The lockup is the caption.
- Line 2 is always larger than line 1.
- Bloom and dark halo are both required. Flat type over footage reads as a subtitle.
- On screen by frame 3 at the latest — never open on bare footage.

⚠️ **The failure this block exists to prevent:** a small object in a side column that
scrolls or drifts. It can satisfy "show the noun", hit the density target, pass `check`, and
still be a non-hook — because it has no summarize, no power word, no single graphic, it is
too small to read, and it never stops moving. See `VISUAL-HOOK.md §6`.

---

## Adding a block

A new block qualifies only if it **shows a real object or a real measurement**. If it is a
panel with words on it, it is a caption — use the caption layer, which already exists and is
better at it.
