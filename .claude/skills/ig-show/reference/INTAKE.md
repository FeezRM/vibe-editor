# INTAKE — the questions, and the MOTION PLAN

Turn a half-sentence request into a build spec in **one round of questions**, then produce
a plan precise enough that building it is mechanical.

---

## The rule about asking

Ask **once.** Batch every question into a single message. Trickling questions across
several turns is the thing that makes working with an agent feel slow.

**Skip any question the brief already answers.** *"a dial for the $2,997 number, brass,
over the 12-second beat"* answers Q2, Q3, Q4 and Q6 — ask only what's genuinely missing.

**Never ask about anything already locked** in [MOTION-LANGUAGE.md](MOTION-LANGUAGE.md).
Do not ask about fonts, easing, layout, safe zones, or "what vibe are you going for."
Those are decided. Re-asking signals the system isn't real.

---

## The seven questions

### Q1 — What does this graphic measure, prove, or compare?
The gate. No answer → the graphic shouldn't exist. Say so and recommend a cut, a push-in,
or a caption emphasis instead. See [DEVICES.md §0](DEVICES.md).

### Q2 — What are the actual numbers / words?
Real values, in the creator's voice. `4,000,000`, not "a big number". `$2,997/mo`, not
"the price". A projection or average gets labelled as one.

### Q3 — Overlay or cutaway?
- **Overlay** — sits over the A-roll. The speaker keeps talking underneath.
- **Cutaway** — the edit cuts to it. The speaker is off screen.

Default overlay. Cut away only for `HOOK SLAM`, `DIFF`, `CURVE`, `TERMINAL`, `MOCK UI`,
`LEDGER`, `IMPACT`, or `END CARD`. Table in [DEVICES.md §4](DEVICES.md).

### Q4 — Where in the reel, and how long is the beat?
A timecode **and** the specific word it lands on. This sets `data-duration` and the
Premiere cue. "Somewhere in the middle" isn't an answer.

### Q5 — Which skin?
**ANALOG** unless the subject is literally computational (code, tooling, build-in-public,
telemetry) — then **DIGITAL**. One skin per project, declared once, never mixed. Ask only
if genuinely ambiguous; default to analog silently.

### Q6 — Accent colour for this project?
The one genuinely open variable. Default `#C9A24B` brass (analog) / `#E8A03C` amber
(digital). Ask once per project, write it into `tokens.css`, never ask again.

### Q7 — Sequence fps?
30 unless the Premiere sequence is 24. Ask once per project. Getting this wrong makes
every graphic stutter and it isn't fixable in Premiere.

**Conditional, only when relevant:**
- Proof Panel → *"where's the screenshot, and is there anything to redact?"*
- Terminal → *"paste the real command and output"* (fake terminal text is banned)
- Versus / Delta → *"both figures, same metric, same window?"*
- More than 3 graphics → *"drop the script or the edit blueprint"*, then plan the whole
  set at once instead of one at a time.

---

## The MOTION PLAN

Produced **before any HTML is written**, saved to `projects/<slug>/MOTION-PLAN.md`, and
approved before the build starts. This is the cheap place to change your mind — a plan
costs a minute to change, a built composition costs twenty.

Every field is an executable instruction. If a field says "nice transition here," the plan
isn't finished.

```markdown
# MOTION PLAN — <reel title>
Project: projects/<slug>/   Skin: ANALOG   Accent: #C9A24B   FPS: 30   1080×1920
Script: <path or inline>    Graphics: <n>  Runtime: <reel length>

## GRAPHIC 01 — THE DIAL
Proves       : <one sentence — the Q1 answer>
Cue          : 00:00:12:18  ·  on the word "million"
Line         : "<the spoken line this sits under>"
Type         : overlay (alpha .mov)  |  cutaway (.mp4)
Dock         : DOCK-C
Duration     : 2.8s   (enter 0.34 · hold 1.9 · cut)
Accent on    : the needle + the live readout        (≤2 accent elements)

Anatomy
  · bezel        — .bezel            — r=300                  — 1px --stroke
  · tick ring    — .tick/.tick--major— minor 5°, major 45°     — 1/2px
  · numerals     — .numeral          — 1..8 radial, Cinzel     — 64px
  · needle       — .needle           — target 47°              — 3px accent
  · label        — .engrave          — "REVENUE PER REEL"      — 24px, +0.180em

Beat sheet
  0.00  hold empty
  0.12  bezel DRAWs                    0.50s  power2.inOut
  0.20  ticks WIPE in                  0.30s  power3.out      stagger 40ms
  0.34  numerals STAMP in              0.16s  expo.out        stagger 80ms
  0.70  needle SWEEPs to 50°           0.60s  power3.out      overshoot +3°
  1.30  needle SETTLEs to 47°          0.35s  power1.inOut    steps(5) stutter
  1.30  readout COUNTs 0 → 2,997       0.90s  power2.out      tabular-nums
  2.20  ambient: tick ring rotates, linear, finite
  2.80  END — no exit animation. the cut is the exit.

Texture      : contour ground · grain 0.12 · vignette 0.10 · stutter 15fps
SFX          : Metal Weight Slide on the sweep @0.70 · low click on settle @1.30
Premiere     : V3 · Normal · renders/01-dial-2997.mov
Render       : npx hyperframes render . -c compositions/01-dial.html \
                 --format mov --resolution portrait --fps 30 --quality high \
                 -o renders/01-dial-2997.mov

## GRAPHIC 02 — ...
```

### Plan-level checks before showing it

- [ ] Every graphic has a Q1 answer that isn't "it looks good there"
- [ ] ≤8 graphics per 30s; gaps of 3–5s; exactly one in the first 3s
- [ ] No two graphics overlap in time
- [ ] Every duration ≥ enter + 0.8s hold
- [ ] No exit animations except the final element
- [ ] ≥3 distinct eases across the set; no bounce/elastic/back
- [ ] Every cue is a timecode **and** a specific word
- [ ] Blocks come from [BLOCKS.md](BLOCKS.md) — flag and justify any new one
- [ ] Nothing sits in the caption band (864–1152) or the safe zones
- [ ] ≤2 accent elements per graphic
- [ ] Texture line present on every cutaway

*Fast mode:* if the brief says "just do it," collapse to one line per graphic and go. The
quality bar doesn't move; only the approval step shrinks.

---

## After approval

1. Scaffold ([PIPELINE.md §1](PIPELINE.md)); set the accent; **copy the font files in**.
2. Build one composition per graphic. Hero frame in CSS first, then animate into it.
3. `npx hyperframes lint .` after each one.
4. `check` and `snapshot` the hero frames — **read them.** A fallback font is invisible to
   the linter and obvious in a snapshot.
5. Render with the exact commands from the plan.
6. Write `renders/IMPORT.md` ([PIPELINE.md §6](PIPELINE.md)) and hand off.

If something changes after the build, **change the MOTION PLAN first**, then re-render
only the affected graphic. Never rebuild the set for a one-graphic note.
