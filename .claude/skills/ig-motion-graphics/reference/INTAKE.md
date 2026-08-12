# INTAKE — the questions, and the MOTION PLAN

The point of this file: turn a half-sentence request into a build spec, in **one round
of questions**, then produce a plan precise enough that building it is mechanical.

---

## The rule about asking

Ask **once**. Batch every question into a single message. Never trickle questions across
several turns — that's the thing that makes working with an agent feel slow.

**Skip any question the brief already answers.** If Feez says *"a meter for the $2,997
number, amber, over the 12-second beat"* — that's Q1, Q2, Q3 and Q5 answered. Ask only
what's genuinely missing.

**Never ask about anything already locked** in MOTION-LANGUAGE.md. Do not ask about
fonts, easing, layout, safe zones, or "what vibe are you going for". Those are decided.
Asking them again signals the system isn't real.

---

## The six questions

### Q1 — What is this graphic measuring or proving?
The gate question. If there isn't an answer, the graphic shouldn't exist and the right
response is to say so and suggest a cut or a b-roll instead.

### Q2 — What are the actual numbers / words?
Real values, in his voice. `4,000,000` not "a big number". `$2,997/mo` not "the price".
If a value is a projection or an average, that gets labelled as one.

### Q3 — Overlay or full-frame?
- **Overlay** — sits over the Cave A-roll. He keeps talking underneath it.
- **Full-frame card** — the edit cuts to it. He's not on screen.

Default: overlay. Cut to a card only for a HOOK SLAM, a DIFF, a CURVE, a TERMINAL, or
an END CARD.

### Q4 — Where in the reel, and how long is the beat?
A timecode or a quoted line from the script. This determines the composition's
`data-duration` and the Premiere cue. "Somewhere in the middle" isn't an answer.

### Q5 — Accent colour for this project?
The one genuinely open variable in the system. Default `#E8A03C` amber (matches the
locked carousel house style). Ask once per project, then write it into `tokens.css` and
never ask again for that reel.

### Q6 — Sequence fps?
30 unless his Premiere sequence is 24. Ask once per project. Getting this wrong makes
every graphic stutter, and it isn't fixable in Premiere.

**Conditional, only when relevant:**
- Proof Panel → *"where's the screenshot/recording, and is there anything to redact?"*
- Terminal block → *"paste the real command and output"* (fake terminal text is banned)
- More than 3 graphics in one reel → *"drop the script or the edit blueprint"* — then
  plan the whole set at once instead of one at a time.

---

## The MOTION PLAN

Produced **before any HTML is written**, saved to `projects/<slug>/MOTION-PLAN.md`, and
approved before the build starts. This is the cheap place to change your mind.

One `GRAPHIC` block per graphic. Every field is an executable instruction — if a field
says "nice transition here", the plan isn't finished.

```markdown
# MOTION PLAN — <reel title>
Project: projects/<slug>/    Accent: #E8A03C    FPS: 30    Sequence: 1080×1920
Script: <path or inline>     Graphics: <n>      Runtime: <reel length>

## GRAPHIC 01 — <BLOCK NAME>
Proves       : <one sentence — the Q1 answer>
Cue          : 00:00:01:04  ·  on the word "<word>"
Line         : "<the spoken line this sits under>"
Type         : overlay (alpha .mov)  |  full-frame card (.mp4)
Dock         : DOCK-BL
Duration     : 2.4s   (enter 0.34 · hold 1.6 · cut)
Accent on    : <the one element that gets --accent>

Anatomy
  · <element> — <role/class> — <exact copy or value> — <size/weight>
  · <element> — ...
  (max 2 accent elements; nothing light-on-dark; clear of caption band)

Beat sheet
  0.00  hold empty
  0.12  label WIPEs in            0.28s  power4.out
  0.20  track WIPEs in            0.30s  power3.out       (stagger 80ms)
  0.34  fill FILLs to 60%         0.70s  power2.out
  0.34  value COUNTs 0 → 2,997    0.90s  power2.out       tabular-nums
  1.10  accent tick SNAPs         0.12s  expo.out
  1.20  ambient: fill breathes ±1.5% opacity, sine.inOut, 3 repeats
  2.40  END — no exit animation. the cut is the exit.

SFX          : low click on the tick @1.10
Premiere     : V3 · Normal · renders/01-meter-2997.mov
Render       : npx hyperframes render . -c compositions/01-meter.html \
                 --format mov --resolution portrait --fps 30 --quality high \
                 -o renders/01-meter-2997.mov

## GRAPHIC 02 — ...
```

### Plan-level checks before showing it to Feez

- [ ] Every graphic has a Q1 answer that isn't "it looks good there"
- [ ] ≤ 8 graphics in a 30s reel; gaps of 3–5s between them
- [ ] Exactly one graphic in the first 3 seconds
- [ ] No two graphics overlap in time
- [ ] Every duration ≥ enter + 0.8s hold
- [ ] No exit animations anywhere except the final element
- [ ] ≥ 3 distinct eases across the set; no bounce/elastic/back
- [ ] Every cue is a timecode + a specific word
- [ ] Blocks come from BLOCKS.md — flag any new one explicitly and justify it
- [ ] Nothing sits in the caption band or the IG safe zones

---

## After approval

1. Scaffold the project (PIPELINE.md §1) and set the accent in `tokens.css`.
2. Build **one composition per graphic**. Layout the hero frame in CSS first, then
   animate into it.
3. `npx hyperframes lint .` after each one.
4. `npx hyperframes check .` and `snapshot` the hero frames — read them, don't assume.
5. Render, following the exact commands in the plan.
6. Write `renders/IMPORT.md` (PIPELINE.md §5) and hand it over.

If Feez changes something after the build, **change the MOTION PLAN first**, then
re-render only the affected graphic. Never rebuild the set for a one-graphic note.
