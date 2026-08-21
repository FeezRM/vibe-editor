# INTAKE — the questions, and the MOTION PLAN

Turn a half-sentence request into a build spec in **one round of questions**, then produce
a plan precise enough that building it is mechanical.

> ⚠️ **Read `SKILL.md` §2 first.** This file used to be the *first* stop for anything the
> brief did not answer, and that made asking the default. It is not: the **acquisition
> ladder** in `SKILL.md` §2 is. Extract the frames, screenshot the real interface, look up
> the real figure, generate the texture — *then* bring whatever is genuinely private here.
>
> Everything below applies to that residue only. The questions are good; they were just
> being asked too early and about too much.

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

Default overlay. Under TWO-WORLDS the cutaway is a whole world, not a beat — see
[FRAME-CONTRACTS.md](FRAME-CONTRACTS.md) §3. Current block names and their occupancy are in
[BLOCKS.md](BLOCKS.md); the names once listed here (`HOOK SLAM`, `DIFF`, `CURVE`, `TERMINAL`,
`LEDGER`, `IMPACT`, `END CARD`) are from the retired analog catalogue and no longer exist.

### Q4 — Where in the reel, and how long is the beat?
A timecode **and** the specific word it lands on. This sets `data-duration` and the
Premiere cue. "Somewhere in the middle" isn't an answer.

### Q5 — Which frame contract?
Replaces the old "which skin?" question — ANALOG and DIGITAL are retired and **VIRAL is the
only skin.** What is genuinely open is the *spatial* architecture: SPLIT-STAGE,
NESTED-SCALE, TWO-WORLDS or OBJECT-OVER-GROUND. See
[FRAME-CONTRACTS.md](FRAME-CONTRACTS.md), which has a chooser at the bottom.

Usually you should propose one rather than ask — the script implies it. Declare it in the
MOTION PLAN either way; it determines how many scene files get written, so it cannot be
decided later.

### Q6 — Accent colour for this project?
The one genuinely open *visual* variable. Comes from `brand/brand.json` `palette.accent`
(currently `#FFC531` gold). Ask only if this video needs to depart from the brand, and if it
does, say so out loud rather than silently overriding.

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

- [ ] **A frame contract is declared**, with the one break named
- [ ] **The plan is 1–3 SCENES**, each naming its one persistent object — not a list of
      graphics. If it reads as a list, it is a slideshow
- [ ] **The Change column, read alone**, describes one object being worked on — not
      "card in, card out"
- [ ] **ONE OBJECT on screen ≥85% of runtime**, changing state every ~1.5s, nothing static
      past ~2s *(supersedes the old "≤8 graphics per 30s, gaps of 3–5s", which was invented,
      contradicted `TEARDOWN.md §5`, and produced the reel the user called "the visuals are
      barely there")*
- [ ] Every state change has a Q1 answer that isn't "it looks good there"
- [ ] Every duration ≥ enter + 0.8s hold
- [ ] No exits between scenes except the final element; **no exits at all inside a scene** —
      elements persist, dim or desaturate
- [ ] ≥3 distinct eases across the set; no bounce/elastic/back
- [ ] Every cue is a timecode **and** a specific word
- [ ] Blocks come from [BLOCKS.md](BLOCKS.md) — flag and justify any new one
- [ ] Nothing sits in the caption band (**y 920–1130**) or the safe zones
- [ ] ≤2 accent elements per graphic
- [ ] **Caption mute windows written in** for the hook, for every content card carrying its
      own copy, and for all of TWO-WORLDS' world 2
- [ ] **Nothing on screen is a placeholder** — the acquisition ladder was worked first

*Fast mode:* if the brief says "just do it," collapse to one line per graphic and go. The
quality bar doesn't move; only the approval step shrinks.

---

## After approval

1. Scaffold ([PIPELINE.md §1](PIPELINE.md)); set the accent; **copy the font files in**.
2. Build **one composition per SCENE** (1-3 per video), not one per graphic. Lay the
   finished object out in CSS first, set it to skeleton, then reveal into it. `SKILL.md` §4.
3. `npx hyperframes lint .` after each one.
4. `check` and `snapshot` the hero frames — **read them.** A fallback font is invisible to
   the linter and obvious in a snapshot.
5. Render with the exact commands from the plan.
6. Write `renders/IMPORT.md` ([PIPELINE.md §6](PIPELINE.md)) and hand off.

If something changes after the build, **change the MOTION PLAN first**, then re-render
only the affected graphic. Never rebuild the set for a one-graphic note.
