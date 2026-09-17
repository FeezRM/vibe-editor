# FRAME CONTRACTS — the spatial architecture of the whole video

`SKILL.md` §3b has always said *"the video should have a shape — commit to one spatial
contract and break it exactly once, at the payoff."* It has never said what a spatial
contract **is**, so nothing ever committed to one, and every reel this repo has built is
eight unrelated rectangles that each appear, do a thing, and cut away.

This file is that vocabulary. **Declaring a contract is mandatory before any composition is
built.** It goes in the MOTION PLAN header and on the `CONTRACT:` line of the EDIT BLUEPRINT.

All four contracts below are measured off `samples/`. See [SAMPLES.md](SAMPLES.md) for the
per-reel teardown each one is derived from.

---

## Why this is the first decision, not a late one

A contract is a promise about **where the viewer looks**. Once made, every later choice
follows from it: what the A-roll is doing, whether captions exist at all, how a graphic
enters, what "breaking it" means at the payoff.

Choose it before the first composition, because it determines the *shape of the scene files
themselves* — a SPLIT-STAGE reel is one 45-second composition; a TWO-WORLDS reel is two
alternating ones. Get it wrong and you are rebuilding, not adjusting.

The contract is also the answer to "why does this feel like a slideshow." A slideshow is
what you get when there is no contract: each beat re-answers the question *where should this
go* from scratch, and the honest answer each time is "middle, same size as last time."

---

## 1. SPLIT-STAGE

> **S1.** Hard horizontal division. The graphic world owns the top; the talker owns the
> bottom. The line between them never moves.

```
┌──────────────────────────┐  y 0
│                          │
│      GRAPHIC WORLD       │   one persistent object lives here
│      (opaque ground)     │   for the entire runtime
│                          │
├──────────────────────────┤  y ~960   <- this line never moves
│                          │
│       A-ROLL             │   plain background, speaker gestures UP
│                          │   at the graphic
└──────────────────────────┘  y 1920
```

| | |
|---|---|
| **A-roll** | Lower half, unmodified. The speaker looks and gestures **up into** the graphic — this is a directing note, not a post decision. Tell the creator before the shoot. |
| **Captions** | **None.** S1 runs 45 seconds with zero burnt-in captions. The graphic *is* the caption. If you find yourself wanting one, the graphic is not carrying enough. |
| **Graphic ground** | Opaque, near-black, full-bleed across the top half. Not a floating card. |
| **Focus mechanism** | **Brightness, not motion.** The active element glows; everything else dims to ~0.3. Nothing moves to attract attention. |
| **Break it once** | At the payoff, the object crosses the line — S1's pyramid finally rises over the divider and sits *in front of* the speaker's head. That crossing is the climax. |

**Use when** the subject is one recognisable artefact that can be built up over time: a
profile, a document, a dashboard, a settings screen, a form.

**This is the highest-value contract in the set** and the one this repo is furthest from.
It requires exactly one composition for the whole video.

---

## 2. NESTED-SCALE

> **S2.** Content inside app inside device. Zoom is a narrative verb, not a transition.

```
   ┌─────────────────┐        ┌───────────────┐        ┌──────────┐
   │  a story frame  │  --->  │  the IG app   │  --->  │  a phone │
   │   (full bleed)  │  zoom  │  around it    │  zoom  │  in a    │
   └─────────────────┘  out   └───────────────┘  out   │  hand    │
                                                        └──────────┘
```

| | |
|---|---|
| **A-roll** | **Lives inside the mockup** on at least one beat — the talking head plays as a post in the rebuilt feed. This is the signature move of the contract. |
| **Captions** | Present on the outermost scale only. Muted whenever the frame is inside the app. |
| **Motion** | Scale changes are **slow and continuous** (0.8–1.4s), never cuts. Directional motion blur on the fastest ones. |
| **Break it once** | The push all the way *in* — past the app, into a single message bubble. |

**Use when** the script walks through a workflow with steps that live at different levels:
"post this → they reply → you DM them → they book."

**Cost warning.** The A-roll-inside-the-mockup beat is not yet supported by this pipeline —
it needs a matte hole in the alpha render plus a Premiere transform of V1, or an ffmpeg
pre-composite. Until that exists, build the mockup with a still frame of the A-roll in the
slot and say so in the MOTION PLAN. Do not fake it with a stock photo.

---

## 3. TWO-WORLDS

> **S3.** The A-roll world and a full-frame analysis world, alternating. Each world has its
> own palette, its own type, its own rules.

```
   A-ROLL WORLD                    WORKSHEET WORLD
   ┌──────────────┐                ┌──────────────┐
   │ speaker      │                │ SOLID ACCENT │
   │ + small      │  <--- cut --->  │ evidence     │
   │   overlays   │                │ + annotation │
   │ dark         │                │ building     │
   └──────────────┘                └──────────────┘
        chapter marker                the proof
```

| | |
|---|---|
| **A-roll** | Owns world 1 entirely. Absent from world 2. |
| **Captions** | World 1 only. World 2 has a **hard caption mute window** — write it into the MOTION PLAN. |
| **World 2** | Full-frame **solid accent colour** (S3 uses a neon green, not black). Real third-party evidence playing in a small window, annotation filling in line by line beside it *as the source plays*. |
| **Repetition** | World 2 repeats **identically**, 3+ times, with different content. The sameness is the argument — see the carve-out in `SKILL.md` §3b. |
| **Break it once** | The final return to world 1 brings world 2's structure with it — S3's opening three-thumbnail brace comes back **resolved**, now labelled with the formula. |

**Use when** the claim is a pattern that must be proved by cases: "this same structure works
in three different niches."

**This is the WORKSHEET mode** referenced in `MOTION-LANGUAGE.md`'s word budgets. World 2 is
exempt from the ≤7-word limits precisely because nothing competes with it.

---

## 4. OBJECT-OVER-GROUND

> **S4.** The A-roll is permanent ground. Graphics are physical objects in front of it. The
> ground itself changes colour on emotional beats.

| | |
|---|---|
| **A-roll** | Full-frame, always. Never cut away from, never covered more than ~40%. |
| **Captions** | **Two-tone lockup**, mid-frame, y 920–1130. White line + accent line. This is the most recognisable single feature of the reference corpus. |
| **Graphics** | Enter as **objects with weight** — rounded cards with real shadows, held at an angle, greyscaled with one colour kept. They **park** in a corner rather than exiting. |
| **The ground recolours** | Full-frame red backlight on "SUPER", green on "DISGUSTINGLY EASY". Practical lighting where possible, `.wash` where not. This is an emotional beat, not an informational one — see the mute-test carve-out. |
| **Break it once** | The object **tiles** — S4's single phone mockup becomes a 3×3 wall of variants with the live A-roll as the centre cell. |

**Use when** the script is a rapid list of tactics with third-party evidence for each, and
the speaker's energy is the spine.

**Lowest build cost of the four**, and the safest default when the footage is a single
unbroken take with high energy.

---

## Choosing

| The script is… | Contract |
|---|---|
| about **one artefact** that gets built up, audited, or fixed | **SPLIT-STAGE** |
| a **workflow** whose steps live at different zoom levels | **NESTED-SCALE** |
| a **pattern proved by repeated cases** | **TWO-WORLDS** |
| a **list of tactics** with evidence, carried by energy | **OBJECT-OVER-GROUND** |

If two fit, take the one with fewer compositions. If none fits, say so and describe the
contract you are proposing instead — in the same terms as the four above: what owns the
frame, what the A-roll does, where captions live, and how you break it once.

**A reel with no declared contract does not get built.**

---

## What a contract does NOT license

- It is not a licence to invent a new skin. `SKILL.md` §3d still holds: compose from
  `tokens.css`. The contract governs **layout and continuity**, not palette or type.
- It does not override the hook. Beat 1 is `VISUAL-HOOK.md`'s SPG lockup under every
  contract; the contract begins at beat 2.
- It does not exempt you from the motion floor
  (`python workflows/motion-density.py`) or from compositing over a real A-roll frame and
  looking at it.
