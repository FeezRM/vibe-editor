# BLOCK CATALOG

Every graphic is one of these, or a deliberate variant that gets added back to this file.

Naming them is the point: it means you can say *"dial on the 12s beat, versus on the
payoff"* and get exactly that, and it means the agent stops inventing a new visual
language every time it's asked for a graphic.

Read [MOTION-LANGUAGE.md](MOTION-LANGUAGE.md) first — palette, type, docks, easing and
the reveal verbs used here are defined there. To choose a block from a line of script,
use [DEVICES.md](DEVICES.md).

**S** = works in both skins · **A** = analog only · **D** = digital only

---

## Quick reference

| # | Block | Skin | Dock | Life | Reveal | Use when the line is… |
|---|---|---|---|---|---|---|
| 01 | **HOOK SLAM** | S | FULL | 1.2–2.0s | SLAM | the hook. one line, first 3 seconds |
| 02 | **THE DIAL** | A | C / BL | 2.2–3.2s | SWEEP | a quantity between bounds, or 1-of-N |
| 03 | **THE METER** | D | BL | 2.0–3.0s | FILL | same, in the digital register |
| 04 | **THE COUNTER** | S | BL / FULL | 1.8–2.6s | COUNT | a single number worth staring at |
| 05 | **THE DELTA** | S | BL | 2.0–2.8s | COUNT + STAMP | before → after |
| 06 | **THE VERSUS** | S | FULL | 2.4–3.4s | STAMP ×2 | theirs vs. ours, with receipts |
| 07 | **THE CURVE** | S | FULL | 2.4–3.5s | DRAW | shape over time — growth, a cliff |
| 08 | **THE SCALE** | A | BL | 1.8–2.6s | DRAW + STAMP | where something sits on a range |
| 09 | **THE STACK** | S | BL / FULL | 2.4–3.5s | WIPE stagger | a list, framework, set of steps |
| 10 | **THE CHIP** | S | TL | 1.4–2.4s | STAMP | one fact, pinned quietly |
| 11 | **THE RAIL** | S | BL | 1.6–2.4s | DRAW + WIPE | naming or defining a term |
| 12 | **THE ANNOTATION** | A | any | 1.2–2.0s | DRAW | correcting or circling something |
| 13 | **THE REDACTION** | S | BL / FULL | 1.6–2.2s | PRINT + STRIKE | killing a claim |
| 14 | **THE DIFF** | D | FULL | 2.6–3.5s | WIPE ×2 | their version vs. this version, in code |
| 15 | **THE TERMINAL** | D | FULL | 2.6–4.0s | PRINT | real commands, real output |
| 16 | **THE MOCK UI** | S | FULL | 2.0–3.0s | WIPE | overwhelm, scale, "everyone is doing this" |
| 17 | **THE IMPACT** | S | FULL | 1.6–2.4s | DRAW + SLAM | a collapse, a break, a hit |
| 18 | **THE PROOF PANEL** | S | R | 2.0–3.5s | STAMP + scale | a real screen: DM, dashboard, analytics |
| 19 | **THE LEDGER** | A | FULL | 2.4–3.4s | WIPE stagger | itemised figures, a receipt, a breakdown |
| 20 | **THE END CARD** | S | FULL | 1.8–2.6s | WIPE | the CTA |

---

## 01 — HOOK SLAM · S

**Proves:** nothing. The one block allowed to be pure assertion.
**Anatomy:** full frame. Ground with contour + vignette. One display line 150–190px,
left-aligned at `x=96`, optically centred. Optional engraved caps label above.
**Motion:** the whole block SLAMs in one frame (scale 1.06→1.00, opacity 0→1, 0.18s
`expo.out`). One word — the one hit hardest in the audio — is accent. Nothing else moves.
Hold. Cut.
**Rules:** ≤7 words. Exactly one per reel, in the first 3s. Never combined with a counter,
dial, or caption on the same frame.

> `most of your reels die in the first second.` — *first second* in accent.

---

## 02 — THE DIAL · A

The signature analog block, and the direct descendant of the compass reference. If the
system had one graphic, this is it.

**Proves:** where a real value sits between bounds — or which one of N things is being
discussed.
**Anatomy:** concentric rings on `DOCK-C`. Outer bezel hairline (`--stroke`). A tick ring:
minor ticks every 5°, major every 45°, majors 2px and full-ink, minors 1px at
`--ink-ghost`. Radial numerals in `Cinzel` at 64px, each placed as its own `<text>` with
`transform="rotate(a) translate(0,-r) rotate(-a)"`, angle computed `360/N * i`. A centre
needle in accent with a darker cap. Engraved caps label beneath at `+0.180em`. Optional
live readout in mono.
**Motion:** SWEEP — needle throws past target by 3° over 0.60s `power3.out`, settles back
over 0.35s `power1.inOut`. The tick ring rotates continuously at `linear`, very slowly
(≥8s per revolution) as ambient. Numerals stagger in 80ms apart ahead of the sweep.
Mechanical motion stepped to `--stutter-fps`.
**Variants:** *segmented* — ring divided into exactly N wedges, one lit by a radial wipe,
N taken from the number actually spoken. *dual* — two concentric arcs, ours vs. theirs;
the losing arc stays `--ink-ghost`, never red.
**Rules:** always label the bounds — an unbounded dial measures nothing. Overshoot ≤5°.
Segment count is computed, never eyeballed.

---

## 03 — THE METER · D

**Proves:** the same thing as `THE DIAL`, in the digital register.
**Anatomy:** 760×14px track at `--ink-ghost`, 2px radius. Fill bar in accent, **hard edge,
no gradient**. Caps label above, bound labels at each end, live mono readout that counts
while the bar fills.
**Motion:** FILL — `scaleX` 0→n from `transform-origin: left`, 0.7s `power2.out`. Value
COUNTs in sync. A 1px accent tick STAMPs at the landing position. Ambient: fill breathes
±1.5% opacity.
**Rules:** always label the bounds. No gradient on the fill — that's the digital skin's
whole discipline.

---

## 04 — THE COUNTER · S

**Proves:** a single quantity, big enough to be the point of the beat.
**Anatomy:** mono readout 96–140px with `tabular-nums`. Engraved caps unit label directly
beneath (`VIEWS`, `MRR`, `DAYS`). Optional 1px accent underline that WIPEs in after the
count settles. In analog, optionally on a `.plate--engraved` with dashed axis rules behind.
**Motion:** COUNT — 0.9s `power2.out`, decelerating into the final number rather than
stopping dead. Digits do not animate individually; the value tweens and the text rewrites.
**Rules:** real numbers with real units. `4,000,000`, not `4M+`. If it's a projection or
average, the label says so — the whole system rests on the difference between a measured
number and a claimed one.

---

## 05 — THE DELTA · S

**Proves:** change. The before/after most proof content comes down to.
**Anatomy:** two mono values side by side. Left = before, `--ink-dim`, 1px strike through
it. A 40px `→` in `--ink-ghost`. Right = after, full ink, one size larger. Engraved caps
label under the pair. Optional `+n%` chip in accent.
**Motion:** before WIPEs in (0.3s). Beat. Arrow DRAWs L→R (0.2s). After COUNTs **from the
before value**, 0.9s `power2.out`. The `+n%` chip STAMPs last.
**Rules:** counts from the old number, never from zero — counting from zero throws away
the comparison. Two values only; three stages is a `STACK`. The arrow never bounces.

---

## 06 — THE VERSUS · S

**Proves:** that one thing beat another, with the receipts on screen.
**Anatomy:** full frame. Two rounded panels side by side, each holding a label line and a
figure, each with a small badge (an eye glyph + count, or a unit tag). The winner sits
~12% larger and carries the accent; the loser stays `--ink-ghost` at ~80% scale.
**Motion:** loser STAMPs in first (0.16s `expo.out`). Beat 0.25s. Winner STAMPs in and
scales up to full over 0.30s `power3.out`. Figures COUNT. Optional 1px accent underline
DRAWs under the winning figure at the moment it's named.
**Rules:** the loser is never red or ugly — it is *quiet*. Making the losing side neutral
is the confident move. Both figures must be real and comparable (same metric, same window).

---

## 07 — THE CURVE · S

**Proves:** shape over time — retention, growth, a cliff.
**Anatomy:** full frame on a plate. Hairline axes with engraved caps labels. The line is
3px accent, round caps, **no fill beneath, no gradient**. One marked point: 6px accent dot
+ 1px vertical drop line + a mono annotation.
**Motion:** DRAW — `stroke-dashoffset`→0 over 1.0–1.2s `power2.inOut`. Axes WIPE in first,
staggered 60ms. The marker STAMPs at the moment the draw passes it, not after. Ambient:
the marker dot pulses 1→0.6 opacity, finite repeats.
**Rules:** one line. A second series is allowed only as `--ink-ghost` and never as a second
accent. No area fill — fills band badly in H.264 and read as stock chart.

---

## 08 — THE SCALE · A

**Proves:** where a value sits on a labelled range, when a dial would be too ceremonial.
**Anatomy:** a horizontal engraved rule with a tick scale — majors every 5th at 2px full
ink, minors 1px at `--ink-ghost`, consistent unit logic. A marker (small accent triangle
or needle) that slides to position. Bound labels at each end in engraved caps, live value
in mono above the marker.
**Motion:** the rule DRAWs L→R (0.5s `power2.inOut`), ticks WIPE in staggered 40ms, then
the marker slides to position with a 2% overshoot and settle. Value COUNTs in sync.
**Rules:** tick logic must be consistent — that consistency is what makes it read as a
real instrument scale rather than decorative dashes.

---

## 09 — THE STACK · S

**Proves:** that the thing is a system with parts, not a vibe.
**Anatomy:** 3–5 rows. Each row: a mono index (`01`), a 1px `--ink-ghost` rule, and a label
44–56px. The active row's index goes accent and its rule goes full ink; inactive rows sit
at `--ink-dim`.
**Motion:** rows WIPE in with 80ms stagger, `power3.out`. Then the active state walks down
one row per spoken beat — driven by the script's timing, never on a loop. Ambient: the
active rule pulses 1px→1.5px.
**Rules:** ≤5 rows, ≤4 words per row. If it needs six, it's a carousel, not a reel.

---

## 10 — THE CHIP · S

The smallest, most reusable block. Proof as a quiet corner tag.

**Proves:** one hard fact, tucked away, not shouted.
**Anatomy:** `DOCK-TL`. 44px pill on `--plate`, 1px `--stroke`, 20px radius. Optional 12px
accent dot, then mono text at 26px. Max 5 words.
**Motion:** STAMP (scale 1.10→1.00, 0.14s `expo.out`) with a 4px `y` settle. If it carries a
live number it COUNTs. Ambient: the dot breathes like a status LED.
**Variants:** *status* (`● RECORDING`), *proof* (`4,912,004 VIEWS`), *source*
(`SRC: IG INSIGHTS · JUL 2026`), *price* (`$2,997/MO`).
**Rules:** one chip at a time. May co-exist with captions but not with another overlay.

---

## 11 — THE RAIL · S

**Proves:** that a term just spoken is a defined thing in the system.
**Anatomy:** a 1px accent line entering from off-frame left, running horizontally, turning
90°, terminating at an engraved caps label and a short definition line.
**Motion:** DRAW the rail (0.4s `power3.out`), WIPE the label (0.28s), then the definition
(0.24s, 70ms later). The rail never re-draws or loops.
**Rules:** 1px always. Definition ≤8 words. One per reel — it's a signature move and stops
being one if it's on every beat.

---

## 12 — THE ANNOTATION · A

The hand on the page. The most human-feeling block in the set.

**Proves:** nothing on its own — it *marks* something else, the way a red pen does.
**Anatomy:** a single hand-drawn-looking stroke over existing content: a squiggle
underline, a circle around a figure, an arrow, a strike. Tapered stroke, round caps, drawn
from a pre-baked SVG path with deliberate wobble. Accent or oxblood.
**Motion:** DRAW only — `stroke-dashoffset`→0 over 0.5–0.8s `power2.inOut`, timed to land
exactly as the word is spoken. Nothing else moves.
**Rules:** the wobble must be **baked into the path data**, never generated at runtime. One
annotation per frame. It always sits *over* something — an annotation with nothing to
annotate is a doodle, which is banned.

---

## 13 — THE REDACTION · S

The myth-punching block. Use it when the script attacks a bad practice — never a person.

**Proves:** that a widely-held claim is false, by showing it then killing it.
**Anatomy:** the claim in `--ink-dim`, 60–76px, in quotes. A rule sweeps through it and the
text drops to `--ink-ghost`. The replacement lands underneath in full ink with one accent
word.
**Motion:** PRINT the claim (28ms/char — it types out like someone else wrote it), hold
0.5s, STRIKE (rule sweeps L→R, 0.22s `expo.out`, text dims on the same tween), then the
replacement SLAMs 0.15s later.
**Rules:** the strike rule is `--ink`, not red. Killing a claim quietly is more confident.
**Never redact a named person.**

---

## 14 — THE DIFF · D

Borrowed from code review, which is the point.

**Proves:** that this version is structurally different, not just better-sounding.
**Anatomy:** full frame on a plate. Mono 34–44px lines. Removed lines prefixed `−`,
`--ink-dim`, on a 6% oxblood wash. Added lines prefixed `+`, full ink, on a 6% accent wash,
the `+` glyph itself in accent. Engraved filename-style header (`SCRIPT.HOOK`, `BIO.TXT`).
**Motion:** header WIPEs. Removed lines WIPE in staggered 70ms. Beat of 0.4s. Added lines
WIPE in staggered 70ms. The eye reads the deletion, then the fix.
**Rules:** ≤3 removed, ≤3 added. This is the one block where red carries meaning. Never use
red anywhere else.

---

## 15 — THE TERMINAL · D

**Proves:** that there is an actual machine behind the claims.
**Anatomy:** full-frame plate, 1px stroke, 44px header bar with three 10px ghost dots and a
mono path label. Body: mono 34–40px. Prompt lines prefixed `$` in accent; output in
`--ink-dim`; the one result line in full ink. 3px block cursor.
**Motion:** PRINT, deterministic — 28ms/char for prompts, whole-line WIPEs for output
(machines don't type). Cursor blinks 0.5s on/off with `steps(1)`, finite repeats.
**Rules:** the content must be **real** — a real command, real output. Fake terminal text is
exactly the "posing as technical" failure this system exists to avoid. No real output to
show → use a `STACK`.

---

## 16 — THE MOCK UI · S

**Proves:** scale and sameness — that there is too much of something.
**Anatomy:** full frame. A recreated interface: a feed grid of near-identical cards, or a
search field with autocomplete rows. **Monochrome only** — ground, bone text, ghost chrome.
Optionally one cell lit in accent while the rest sit at `--ink-ghost`.
**Motion:** the grid WIPEs in as a stagger (40ms, row-major), or the search text PRINTs and
the suggestion rows WIPE in beneath it. Optional very slow drift upward to imply endless
scroll — `linear`, finite.
**Rules:** monochrome except real thumbnail art. A full-colour UI recreation reads as a
screenshot you forgot to grade. Never reproduce a real brand's exact logo or wordmark.

---

## 17 — THE IMPACT · S

**Proves:** that something broke — a collapse, a crash, a hit.
**Anatomy:** a target object (a ring, a plate, a figure) and a drawn line that travels into
it. At contact the object splits along 2–3 pre-baked crack paths; fragments displace 4–12px
along fixed vectors. One frame of accent-to-oxblood flash at ≤20% opacity.
**Motion:** the line DRAWs in (0.5s `power2.inOut`), contact SLAMs (0.10s), fragments
displace with `power3.out` and hold. A 2px frame shake over 0.12s, decaying, and nothing
else moves. No exit — the cut is the exit.
**Rules:** fragments travel **away from the point of contact** — an impact that breaks in the
wrong direction reads as broken. All crack paths and vectors are pre-baked; no runtime
randomness. One per reel; it's a loud block.

---

## 18 — THE PROOF PANEL · S

How a screenshot enters the frame without wrecking it. The fix for the white-box problem.

**Proves:** the receipt — a DM, a dashboard, an analytics screen, a payment.
**Anatomy:** `DOCK-R`. Source image or screen recording, 16px radius, 1px stroke,
brightness pulled to **~72%** and contrast +6% so it sits in the grade. Four 20px
`--ink-ghost` corner brackets outside the panel. Engraved caps source label beneath.
Optional accent underline on the one row that matters.
**Motion:** STAMP in (scale 0.96→1.00 + 12px `y`, 0.22s `expo.out`), brackets WIPE in 40ms
later from opposite corners. Then a slow 2% push-in across the panel's whole life so it
never sits dead.
**Rules:** never at 100% brightness. Never a drop shadow. Redact names, handles, and
figures that aren't yours to show with a 6px blur bar — never a black box. A black box
looks like hiding; a blur looks like discretion.

---

## 19 — THE LEDGER · A

**Proves:** that the number breaks down into real parts.
**Anatomy:** full frame. An engraved plate with a header rule, then 3–5 itemised rows —
engraved caps label on the left axis, mono figure right-aligned on a shared column. A
double rule above the total. The total in accent.
**Motion:** header WIPEs, rows WIPE in staggered 90ms, the double rule DRAWs L→R, then the
total COUNTs. Right-aligned figures need `tabular-nums` or the column visibly wobbles.
**Rules:** figures right-align on one column, always. ≤5 rows. The total must actually be
the sum of the rows — a ledger that doesn't add up is the single fastest way to lose the
audience that this style is built for.

---

## 20 — THE END CARD · S

**Proves:** nothing. It asks.
**Anatomy:** full frame. One instruction line at 88px with the trigger word in accent
inside quotes. That's it — **no handle, no logo, no follow banner, no arrows.**
**Motion:** WIPE the line (0.34s `power3.out`), then the trigger word STAMPs 0.12s later so
it lands separately. The trigger word gets a single 1.5% scale breath and nothing else.
**Rules:** one CTA — comment trigger *or* DM word, never both, never "link in bio" as well.
On screen ≥1.8s so it's readable at scroll speed.

---

## Adding a block

New blocks are allowed, but they get added here before they get used twice. A block
qualifies if it:

1. answers "what does this measure, prove, or compare?"
2. uses only the nine reveal verbs in [MOTION-LANGUAGE §5](MOTION-LANGUAGE.md)
3. needs no colour outside `GROUND / INK / ACCENT` + the derived neutrals
4. fits one dock
5. can be described in one sentence the creator would say out loud

Fails any of those → it's a one-off. Build it for that reel and don't canonise it.
