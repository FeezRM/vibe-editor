# BLOCK CATALOG — The Terminal, in motion

Thirteen named motion graphics. Every graphic Feez uses is one of these, or a
deliberate variant of one that gets added back to this file.

Naming things matters: it means he can say *"meter on the 12s beat, delta on the
payoff"* and get exactly that, and it means the AI stops inventing a new visual
language every time it's asked for a graphic.

Read [MOTION-LANGUAGE.md](MOTION-LANGUAGE.md) first — the palette, type, docks, and
easing referenced here are defined there.

---

## Quick reference

| # | Block | Dock | Life | Reveal | Use when the line is… |
|---|---|---|---|---|---|
| 01 | **HOOK SLAM** | FULL | 1.2–2.0s | SLAM | the hook. one line, first 3 seconds. |
| 02 | **THE METER** | BL | 2.0–3.0s | FILL | a quantity between two bounds |
| 03 | **THE COUNTER** | BL / FULL | 1.8–2.6s | COUNT | a single number worth staring at |
| 04 | **THE DELTA** | BL | 2.0–2.8s | COUNT + SLAM | before → after |
| 05 | **THE CURVE** | FULL | 2.4–3.5s | DRAW | retention, growth, a drop-off |
| 06 | **THE DIFF** | FULL | 2.6–3.5s | WIPE ×2 | their version vs his version |
| 07 | **THE STACK** | BL / FULL | 2.4–3.5s | WIPE stagger | a list, framework, or set of steps |
| 08 | **THE CHIP** | TL | 1.4–2.4s | SNAP | a fact worth pinning: a price, a count, a date |
| 09 | **THE RAIL** | BL | 1.6–2.4s | DRAW + WIPE | naming or defining a term |
| 10 | **THE REDACTION** | BL / FULL | 1.6–2.2s | PRINT + STRIKE | killing a claim the posers make |
| 11 | **THE TERMINAL** | FULL | 2.6–4.0s | PRINT | build-in-public, code, CS wedge |
| 12 | **THE PROOF PANEL** | R | 2.0–3.5s | SNAP + scale | showing a real screen: DM, dashboard, analytics |
| 13 | **THE END CARD** | FULL | 1.8–2.6s | WIPE | the comment-trigger CTA |

---

## 01 — HOOK SLAM

**What it proves:** nothing. This is the one block allowed to be pure assertion.
**Anatomy:** full frame, `PLATE` at 92%, one display line 150–190px, left-aligned at
`x=96`, vertically centred. Optional 22px caps label above at `INK-DIM`.
**Motion:** the whole block SLAMs in one frame (scale 1.06→1.00, opacity 0→1, 0.18s
`expo.out`). One word — the one he hits with his voice — is `ACCENT`. Nothing else moves.
Hold. Cut.
**Rules:** ≤7 words. Exactly one per reel, in the first 3 seconds. Never combine with a
counter, a meter, or a caption on the same frame.

> `posting is gambling.` — with *gambling* in accent.

---

## 02 — THE METER

The signature block. If Feez had one graphic, this is it — it's the literal picture of
"I measure, you guess."

**What it proves:** where a real value sits between two bounds.
**Anatomy:** a 760×14px track at `INK-GHOST`, 2px radius. Fill bar in `ACCENT`, hard
edge (no gradient). Caps label above (`+0.085em`, `INK-DIM`), bound labels at each end
(`0` / max), live value as a mono readout that counts while the bar fills.
**Motion:** FILL — `scaleX` 0→n, `transform-origin: left`, 0.7s `power2.out`. Value
counts in sync, `power2.out`, `tabular-nums`. A 1px accent tick drops at the final
position on arrival with a 0.12s SNAP. Ambient: fill breathes ±1.5% opacity, `sine.inOut`.
**Variants:** *segmented* (24 discrete cells that light in sequence, 40ms stagger) for
counts rather than continuums; *dual* (two stacked tracks, his vs theirs) — the losing
track stays `INK-GHOST`, never red.
**Rules:** always label the bounds. An unbounded bar measures nothing.

---

## 03 — THE COUNTER

**What it proves:** a single quantity, big enough to be the whole point of the beat.
**Anatomy:** mono readout 96–140px, `INK`, `tabular-nums`. Caps unit label directly
beneath at 26px `INK-DIM` (`VIEWS`, `MRR`, `DAYS`). Optional 1px accent underline that
WIPEs in after the count settles.
**Motion:** COUNT — 0.9s `power2.out`, easing *out* so it decelerates into the final
number instead of stopping dead. Digits do not individually animate; the value tweens
and the text rewrites each frame.
**Rules:** real numbers only, with real units. `4,000,000` not `4M+`. If the number is
a projection or an average, the label says so — the entire brand is built on the
difference between a measured number and a claimed one.

---

## 04 — THE DELTA

**What it proves:** change. The before/after that most of his proof content is.
**Anatomy:** two mono values side by side. Left = before, `INK-DIM`, with a 1px
`INK-GHOST` strike through it. A 40px `→` in `INK-GHOST`. Right = after, `INK`, one size
larger. A caps label sits under the pair. Optional small `+n%` chip in `ACCENT`.
**Motion:** before value WIPEs in (0.3s). Beat. Arrow draws L→R (0.2s). After value
COUNTs from the before value to the after value (0.9s `power2.out`) — it counts *from*
the old number, not from zero. The `+n%` chip SNAPs last.
**Rules:** the arrow never bounces or loops. Two values only — a three-stage delta is a
Stack.

---

## 05 — THE CURVE

**What it proves:** shape over time — retention, growth, a cliff.
**Anatomy:** full-frame, `PLATE`. Hairline `INK-GHOST` axes with caps labels. The line
is 3px `ACCENT`, round caps, no fill under it, no gradient. A single marked point:
6px accent dot + 1px vertical drop line + a mono annotation.
**Motion:** DRAW — `stroke-dashoffset` → 0 over 1.0s `power2.inOut`. Axes WIPE in first
(0.25s, staggered 60ms). The marker SNAPs at the moment the draw passes it, not after.
Ambient: the marker dot pulses opacity 1 → 0.6, `sine.inOut`, finite repeats.
**Rules:** one line. A second series is allowed only as `INK-GHOST` (the comparison he's
beating) and never as a second accent. No area fill — fills band badly in H.264 and
read as stock chart.

---

## 06 — THE DIFF

The CS wedge made visual. Directly borrowed from code review, which is the point.

**What it proves:** that his version is structurally different, not just better-sounding.
**Anatomy:** full frame, `PLATE`. Mono 34–44px lines. Removed lines prefixed `−`,
`INK-DIM`, on a 6% red wash. Added lines prefixed `+`, `INK`, on a 6% accent wash, with
the `+` glyph itself in `ACCENT`. A caps filename-style header at the top
(`SCRIPT.HOOK`, `BIO.TXT`, `DM.OPENER`).
**Motion:** header WIPEs. Removed lines WIPE in as a stagger (70ms). Beat of 0.4s.
Added lines WIPE in as a stagger (70ms). The eye reads the deletion, then the fix.
**Rules:** ≤3 removed and ≤3 added lines. This is the one block where red is allowed,
because in a diff red *means* something. Never use red anywhere else.

---

## 07 — THE STACK

**What it proves:** that the thing is a system with parts, not a vibe.
**Anatomy:** 3–5 rows. Each row: a mono index (`01`), a 1px `INK-GHOST` rule, and a
label in `INK` at 44–56px. The active row's index goes `ACCENT` and its rule goes
`INK`; inactive rows sit at `INK-DIM`.
**Motion:** rows WIPE in with a 80ms stagger, `power4.out`. Then the "active" state
walks down the stack, one row per spoken beat — driven by the script's timing, not on a
loop. Ambient: the active row's rule pulses 1px→1.5px, `sine.inOut`.
**Rules:** ≤5 rows, ≤4 words per row. If it needs six, it's a carousel not a reel.

---

## 08 — THE CHIP

The smallest, most reusable block. Steal-from-devinjatho: proof as a quiet corner tag.

**What it proves:** one hard fact, tucked away, not shouted.
**Anatomy:** `DOCK-TL`. 40px-tall pill, `PLATE` at 86%, 1px `STROKE`, 20px radius.
Inside: an optional 12px accent dot, then mono text at 26px. Max 5 words.
**Motion:** SNAP in (scale 0.94→1.00, 0.16s `expo.out`), tiny 4px `y` settle. If the
chip carries a live number it COUNTs. Ambient: if there's a dot, it breathes
`sine.inOut` — a status LED.
**Variants:** *status* (`● RECORDING`, `● LIVE`), *proof* (`4,912,004 VIEWS`), *source*
(`SRC: IG INSIGHTS · JUL 2026`), *price* (`$2,997/MO`).
**Rules:** one chip at a time. A chip may co-exist with captions but not with another
overlay.

---

## 09 — THE RAIL

Direct port of the carousel system's off-frame connector rail — the visual link between
the carousels and the reels.

**What it proves:** that a term he just said is a defined thing in his system.
**Anatomy:** a 1px `ACCENT` line that enters from off-frame left, runs horizontally,
turns 90°, and terminates at a caps label + a short definition line in `INK`.
**Motion:** DRAW the rail (0.4s `power4.out`), then WIPE the label (0.28s), then the
definition (0.24s, 70ms later). The rail never re-draws or loops.
**Rules:** rail is 1px, always. Definition ≤8 words. One per reel — it's a signature
move and it stops being one if it's on every beat.

---

## 10 — THE REDACTION

The enemy-punching block. Use it when the script attacks The Pose.

**What it proves:** that a widely-held claim is false — by showing it, then killing it.
**Anatomy:** the claim in `INK-DIM`, 60–76px, in quotes. Then a rule sweeps through it
and the text drops to `INK-GHOST`. The replacement lands underneath in `INK` with one
`ACCENT` word.
**Motion:** PRINT the claim (28ms/char — it types out like someone else wrote it), hold
0.5s, STRIKE (rule sweeps L→R, 0.22s `expo.out`, text dims on the same tween), then the
replacement SLAMs in 0.15s later.
**Rules:** the strike rule is `INK`, not red. Killing it quietly is more confident than
killing it loudly. Never redact a named person.

---

## 11 — THE TERMINAL

The block the whole system is named after. Reserved for build-in-public, ContentSpy,
AI-workflow, and CS-wedge content — it loses its meaning if it's decorating a mindset reel.

**What it proves:** that there is an actual machine behind the claims.
**Anatomy:** full-frame `PLATE`, 1px `STROKE`, 20px radius, with a 44px header bar
carrying three 10px `INK-GHOST` dots and a mono path label. Body: mono 34–40px lines.
Prompt lines prefixed `$` in `ACCENT`; output lines in `INK-DIM`; the one result line in
`INK`. A 3px block cursor at the end.
**Motion:** PRINT, deterministic — 28ms/char for prompts, whole-line WIPEs for output
(machines don't type). Cursor blinks 0.5s on / 0.5s off, `steps(1)`, finite repeats.
**Rules:** the content must be **real** — a real command, a real log line, real output.
Fake terminal text is the exact "posing as technical" thing the brand attacks. If
there's no real output to show, use a Stack instead.

---

## 12 — THE PROOF PANEL

How a screenshot enters the frame without wrecking it. This is the fix for the white-box
problem.

**What it proves:** the receipt — a DM, a dashboard, an analytics screen, a payment.
**Anatomy:** `DOCK-R`. Source image or screen recording, 24px radius, 1px `STROKE`,
brightness pulled to **~72%** and contrast +6% so it sits in the Cave grade. Four 20px
`INK-GHOST` corner brackets outside the panel (the devinjatho viewfinder move). A caps
source label beneath at `INK-DIM`. Optional accent underline on the one row that matters.
**Motion:** SNAP in (scale 0.96→1.00 + 12px `y`, 0.22s `expo.out`), brackets WIPE in
40ms later from opposite corners. Then a slow 2% push-in over the panel's whole life
(`sine.inOut`) so it never sits dead. If one value matters, an accent underline WIPEs
under it at the moment he says it.
**Rules:** never at 100% brightness. Never with a drop shadow. Redact real names,
handles, and dollar figures that aren't his to show — a 6px blur bar in `INK-GHOST`,
never a black box (a black box looks like hiding, a blur looks like discretion).

---

## 13 — THE END CARD

**What it proves:** nothing. It asks.
**Anatomy:** full frame `PLATE`. One line of instruction in `INK` at 88px, with the
comment trigger word in `ACCENT` inside quotes. That's it — **no handle, no logo, no
follow banner, no arrows.** Zero UI chrome is a house rule.
**Motion:** WIPE the line (0.34s `power4.out`), then the trigger word SNAPs 0.12s later
so it lands separately. The trigger word gets a single 1.5% scale breath,
`sine.inOut`, and nothing else.
**Rules:** one CTA. Comment trigger or DM word — never both, never "link in bio" as
well. Sits on screen ≥1.8s so it's actually readable at scroll speed.

---

## Adding a block

New blocks are allowed, but they get added here before they get used twice. A block
qualifies if it:

1. answers "what does this measure or prove?"
2. uses only the seven reveal verbs in MOTION-LANGUAGE.md §5
3. needs no colour outside `GROUND / INK / ACCENT` + the derived neutrals
4. fits one dock
5. can be described in one sentence Feez would actually say out loud

If it fails any of those, it's a one-off — build it for that reel and don't canonise it.
