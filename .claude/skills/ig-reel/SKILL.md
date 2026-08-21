---
name: ig-reel
description: "The entry point and orchestrator for editing a short-form vertical video (Instagram Reel, TikTok, YouTube Short) end to end by driving Adobe Premiere Pro over MCP. Produces the timestamped, shot-by-shot EDIT BLUEPRINT the user approves, establishes the project and sequence, sets the track architecture, then dispatches each phase to the skill that owns it: ig-cut (silence and filler), ig-captions, ig-show (motion graphics), ig-sound (music and SFX), ig-pacing (pattern interrupts), ig-delivery (QA and export). Use this when the request is a whole video rather than one task — raw footage that needs turning into a finished reel, a long video that needs clipping into shorts, or an edit plan for a script. If the request is a single phase, go straight to that phase's skill instead. Triggers: edit my reel, edit this video, cut this footage, make this a reel, turn this into a short, finish this video, edit plan, blueprint this edit, EDL, polish this video, edit my talking head, clip this long video, plan the edit, premiere, premiere pro, where do I start."
---

# IG REEL — the orchestrator

Owns the **blueprint**, the **project setup**, and the **order of operations**. Owns no
craft of its own — every phase belongs to a specialist skill.

> North star: every second earns the next second. If a frame isn't holding attention, it
> gets cut, zoomed, or covered.

---

## Brand overrides — read these before anything else

This repo ships defaults. **Whoever cloned it may have replaced them.**

| Read | Holds |
|---|---|
| `brand/BRAND.md` | free-text house rules — voice, subject matter, banned visuals, CTA, sound |
| `brand/brand.json` | values — palette, fonts, canvas, fps, density, export |

**Precedence, lowest to highest:**
repo defaults (this file) → `brand/` → the project's own `tokens.css` / `MOTION-PLAN.md`
→ what the user says in this conversation.

Where `brand/` contradicts a default below, **`brand/` wins** — and say so out loud rather
than silently following the default. If neither file exists, use the defaults here.

Values in `brand.json` are already compiled into `brand/tokens.css`; regenerate with
`node scripts/brand.mjs build` after editing. Never hand-edit `brand/tokens.css`.

---

## The six steps, and who owns each

| # | Step | Skill | The one thing it does |
|---|---|---|---|
| 1 | Remove whitespace + filler | **`ig-cut`** | strips dead air into a tight spine, ~3s average clips |
| 2 | Captions | **`ig-captions`** | word-accurate, banded at **y 920–1130** on 1080×1920, never bottom-third |
| 3 | Background music | **`ig-sound`** | bed ducked ~-18dB, out under the hook |
| 4 | **Show** | **`ig-show`** | the motion graphics. **Plan every beat before building anything.** **Show the noun**: real app UI, real content with real metrics. **A graphic is on screen ≥85% of runtime** — usually one persistent object mutating, not many cards |
| 5 | Sound effects | **`ig-sound`** | one SFX per visual event, never per word |
| 6 | Pattern interrupts | **`ig-pacing`** | something changes every ~1.5s; nothing static past ~2s |
| — | QA + export | **`ig-delivery`** | 1080×1920, verified on disk |

Steps 3 and 5 share one skill because they are one mix on the same tracks.

**Step 4 is where the quality lives.** Steps 1, 2 and 6 are mechanical and largely
solvable; the SHOW layer is what separates a competent edit from a premium one. Its one
rule is **show the noun** — if the script names a thing, put that thing on screen; if it
names a number, draw the real measurement. A graphic that could be replaced by its own
caption fails the mute test and does not ship. Plan every beat before building anything.
See `ig-show/reference/TEARDOWN.md`.

---

## Default mode: Blueprint → Approve → Execute

1. **Ingest.** Load the footage, the script if there is one, and the goal.
   **Transcribe first** — `npx hyperframes transcribe <file>`, or a Whisper pass. Premiere's
   MCP has no transcription tool, and every later step needs word-level timestamps.

   Then check the transcript actually contains what the format needs: a tier list needs the
   *rankings*, a listicle needs the *items*, "3 reasons" needs the *three*. If the footage
   is raw takes without that structure — common — **get the missing pieces from the user
   before blueprinting** rather than inventing them.

2. **Blueprint.** The deliverable below. This is where the craft decisions get made, while
   they are still cheap.

3. **Approve.** Show it, take notes. Cheap to change here, expensive on the timeline.

4. **Execute.** Dispatch phase by phase, in order, verifying between passes.

5. **QA + export.** `ig-delivery`.

*Fast mode:* "just do it" / "don't overthink it" → collapse to one line per beat and go
straight to execute. The quality bar doesn't move; the approval step shrinks.

---

## Before touching the timeline

1. **`verify_premiere_connection`.** Read-only. Returns the build, the open project, and the
   active sequence. If it fails the bridge isn't running: Premiere open → project open →
   *Window → Extensions → MCP Bridge (CEP)* → Temp Directory matches `PREMIERE_TEMP_DIR` →
   *Start Bridge*. Don't edit around a dead bridge; fix it or hand over the blueprint.
2. **Attach `premiere://config/get_instructions`** before any project-modifying work. It
   carries the server's own operating guidance and overrides guesses made here.
3. **List the live tool set.** ~283 tools ship and the catalog moves. Use the names the
   connected server actually exposes.
4. **Confirm the sequence.** `get_active_sequence` / `get_sequence_settings` for fps and
   frame size. `create_sequence` at 1080×1920 if there isn't a vertical one.
   **Every graphic must be rendered at the sequence fps** — a mismatch is what makes
   overlays stutter, and it is not fixable afterwards.
5. **Build the track architecture** (below) before placing anything.

---

## Track architecture

From an observed real project. It differs from the naive layout in one important way:
**each recurring graphic type gets its own track** rather than sharing one graphics track.
Two clips cannot share a start frame on one track, so this removes a whole class of
placement collision before it happens.

```
V1   A-roll
V2   B-roll / full-frame cutaways
V3   primary graphic overlays (alpha)
V4   secondary graphics — annotations, chips (alpha)
V5+  additional simultaneous graphic types
CAP  native captions track — separate from graphics
A1   voice      A2  voice / alt
A3   SFX        A4  SFX
A5   music      A6  spare
```

Create with `add_track`, confirm with `list_sequence_tracks`. **Never assume an index
exists.**

---

## The deliverable: EDIT BLUEPRINT

Every row is an executable instruction. Produce this before touching the timeline.

```
EDIT BLUEPRINT — [title]
Source: [file] · in [Xs] → target out [Ys] · Ratio 9:16 · Sequence [fps]
Goal: [views / leads / sales]      Graphics skin: VIRAL (default)
CONTRACT: [SPLIT-STAGE | NESTED-SCALE | TWO-WORLDS | OBJECT-OVER-GROUND]
  owns the frame: [..]  ·  A-roll does: [..]  ·  captions: [yes / none / muted in world 2]
  broken once at: [TC + what changes]
SCENES: [1-3] — [name each, and the one persistent object it carries]

HOOK (0–3s)
- A-roll: [source TC] | Scale: [wide/med/CU]
- Caption: "[exact words — the creator's voice]" | Emphasis: [word] [.pop/.pop--bad/.pop--good]
- Graphic: [block + cue TC + trigger word] | SFX: [riser/none] | Music: [out under hook]

[BEAT 2 — 3–7s] — label what this beat does (build-up / mind-read / authority)
- A-roll: [TC] | Scale: [..] | Caption: "[..]" | Motion: [zoom pulse / cut]
- Graphic: [..] | SFX: [..]

[BEAT 3 — value] ...
  (one row per beat; a beat is 1–4s — something changes every beat)

[PAYOFF] — resolve the hook, held as long as possible
[CTA]    — [comment trigger / DM word], clean end card

GLOBAL
- Captions : Europa Grotesk SH 88px, ONE line, 2–4 words, block centre y ~50%, hard cut
- Music    : [track] ducked -18dB, out under the hook
- Grade    : deep contrast, cool shadows, controlled highlights
- Graphics : [one line per SCENE + the beats it spans]  → ig-show writes the MOTION PLAN
             NOT one line per graphic — a video is 1-3 scenes, each one persistent
             object through a labelled state machine. See ig-show/reference/
             FRAME-CONTRACTS.md and SAMPLES.md.
- B-roll   : [screen recordings to capture / assets to generate]
```

Keep beats short. If a row covers more than ~4 seconds of static A-roll, split it — the
frame should change.

**The Change column is the test.** Read every beat's change in isolation, ignoring the copy.
If the sequence reads "card in, card out, card in, card out", the blueprint is a slideshow
and no amount of craft in `ig-show` will rescue it. It should read like one object being
worked on: "skeleton", "avatar fills", "name fills", "bio line 1", "…", "grid populates",
"winner takes gold, losers desaturate".

---

## Execution order

Build in this order. **Do not polish before the spine is right.**

**Pass 1 — the spine.** `ig-cut`. Import, pick takes, strip silence and filler, lock the
hook. Story flows end to end with zero dead air. Nothing pretty yet.

**Pass 2 — the words.** `ig-captions`. The video has to work on mute before it gets
decorated.

**Pass 3 — the show.** `ig-show`. MOTION PLAN → build → render → import → place on V3/V4 at
the cue timecodes. This is the expensive pass; the blueprint should have already decided
what gets built.

**Pass 4 — the mix.** `ig-sound`. Music bed, ducking, hook dropout, SFX cued off the same
timecodes as the graphics.

**Pass 5 — the pass that finds the holes.** `ig-pacing`. Audit for gaps >3s, fill with the
cheapest interrupt that works. Zoom pulses and shot-scale alternation land here.

**Pass 6 — ship.** `ig-delivery`.

---

## Premiere MCP — read before executing

- **It edits the live project. There is no dry run and no agent-controlled undo.** Before a
  destructive pass, say what you're about to do and how many operations it is. If the user
  has unsaved manual work, have them save first — your calls and their Ctrl-Z share one
  history.
- **Timecodes are timeline frames, not source frames.** They diverge whenever source fps ≠
  sequence fps. Read positions back with `get_clip_properties` / `get_clip_at_position`
  rather than computing them.
- **Verify with pixels, not faith.** `export_frame` at the hook, at every graphic cue, and
  at the end card. A tool returning success is not proof — and here that is literal:
  `export_frame` returns `success: true` and writes **nothing** on this machine, and
  mangles any `outputPath` containing backslashes. Pass forward slashes, `test -f` the
  result, and fall back to an ffmpeg composite. See `ig-show/SKILL.md`.
- **Measure, don't eyeball, anything with a number in its spec.** Caption geometry via
  `python analysis/measure.py`. The last build passed a visual check with captions 35%
  oversized.
- **Premiere generates nothing.** No transcription, no image/video/music generation.
  Transcribe with `hyperframes transcribe`; generate assets via the `media-use` skill;
  write to `projects/<slug>/assets/`, then `import_media`.
- **`import_ae_comps` is not advertised** and `.aep` imports can wedge the bridge. Don't
  reach for After Effects round-trips.
- **When something fails twice the same way**, run the CEP panel's *Run Diagnostics* rather
  than retrying a third time, and report what it says instead of guessing.

---

## Iteration

Most common asks, in order: re-cut the hook · tighten pacing · swap a graphic · restyle
captions · adjust the music. **Change the blueprint first**, then re-execute only the
affected beats. Never rebuild the whole timeline for a one-beat note.

For a long source clipped into several shorts: one blueprint per short, one project folder
per short, shared assets.

---

## Aliases

Requests that used to route to `ig-video-editor` (the cut) or `ig-motion-graphics` (the
look) belong here now — this skill dispatches them to the right specialist. If the request
is clearly a single phase, skip this skill and go straight to that phase's skill.
