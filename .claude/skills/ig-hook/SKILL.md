---
name: ig-hook
description: >-
  Directs and validates the first 0–8 seconds of a short-form video across source footage,
  HyperFrames, and Adobe Premiere Pro. Use for visual hooks, hook variants, opening recuts,
  Trial Reel openings, frame-zero concepts, or any whole-video edit whose opening has not
  been locked. Produces three complete opening sequences, selects a visual mode from real
  evidence, writes HOOK-PACKET.json, storyboards the candidates, builds only approved
  variants in sandbox Premiere sequences, and verifies the composited pixels. Does not own
  the rest of the reel, body pacing, captions after the opening, or general motion graphics.
---

# IG HOOK — direct the first eight seconds

The hook is not a sentence or a title card. It is the **0–8 second sequence** that makes a
specific promise, proves it visually, creates tension, and advances to a mechanism.

This skill is the interface between the editing agent, HyperFrames, and Premiere. It owns
the opening decision; `ig-show` builds designed objects, Premiere edits the footage, and
`ig-pacing` audits the body after second eight.

## Read first

1. `brand/BRAND.md` and `brand/brand.json`.
2. [reference/MODES.md](reference/MODES.md) to select candidate modes.
3. [reference/HOOK-PACKET.md](reference/HOOK-PACKET.md) before writing the plan.
4. [reference/QA.md](reference/QA.md) before touching Premiere or approving a render.

If the opening uses a HyperFrames composition, also use `ig-show`; its build rules still
apply. A Lockup candidate additionally uses `ig-show/reference/VISUAL-HOOK.md`.

## The contract

Every candidate must execute four jobs:

| Time | Job | Question it answers |
|---|---|---|
| 0–2s | **Trigger** | What specific fact, behavior, or consequence stops the thumb? |
| 0–3s | **Receipt** | What visible object proves that this is real? |
| 2–5s | **Tension** | What contradiction, objection, or risk keeps the question open? |
| 5–8s | **Mechanism** | What new model, demonstration, or next step is now coming? |

These jobs may overlap. A demonstration can trigger and prove in the same frame. What may
not happen is a strong first line followed by generic bridge copy.

## Workflow

### 1. Build a source map before ideating

- Transcribe the source with word timestamps.
- Pull frames at the candidate opening lines and note where the face and hands sit.
- Inventory usable proof: analytics, app screens, settings, objects, source clips, DMs,
  calendars, documents, before/after states.
- Record provenance. Never invent a metric or render an unverified number.

Work the `ig-show` acquisition ladder before asking the creator. Private analytics and DMs
are the residue that genuinely require user input.

### 2. Generate three different sequences

Generate **three complete 0–8 second candidates**, not three rewrites of the first sentence.
Each candidate must use a different dominant mode from `MODES.md` unless the source makes
that impossible.

For every candidate specify:

- exact spoken words by beat;
- frame-zero visual and evidence IDs;
- what changes at 2–5 seconds;
- the mechanism revealed by second eight;
- owner for every beat: Premiere, HyperFrames, or both;
- caption mute windows;
- feasibility and risk.

### 3. Write and gate `HOOK-PACKET.json`

Write it to `projects/<slug>/HOOK-PACKET.json`. This is the single source of truth for the
opening. Validate it before storyboarding:

```bash
python analysis/validate-hook-packet.py projects/<slug>/HOOK-PACKET.json
```

Score each candidate 0–2 on six dimensions: specificity, proof, tension, second beat, mute
test, and feasibility. The selected candidate needs **9/12 or better**, with no zero in
proof, second beat, or mute test. A high score cannot override missing or fabricated proof.

### 4. Storyboard before editing

For each candidate, composite five stills over real A-roll at approximately:

`0.15s · 1.25s · 3.25s · 5.25s · 7.25s`

Use HyperFrames snapshots for designed elements and ffmpeg for the real A-roll composite.
Review the three strips side by side. The storyboard must reveal the claim on mute and must
show a meaningful state change after frame zero.

Default mode is **design**: storyboard all three, build the selected candidate.  
**Trial mode:** build A/B/C against the same body for real Trial Reel testing.  
**Fast mode:** score three on paper and build the top candidate without an approval pause.

### 5. Build through explicit ownership

| Owner | It does |
|---|---|
| **Premiere** | source selection, hard cuts, role-play, split-screen footage, punch-ins, timing, sound, and the live sequence |
| **HyperFrames** | evidence cards, app UI, charts, labels, masks, comparisons, lockups, and deterministic state changes |
| **Both** | a real object or clip whose state is annotated or reframed by HyperFrames |

Do not recreate an edit in HyperFrames that Premiere can make from real footage. Do not ask
Premiere to improvise typography, charts, or proof UI that HyperFrames can render exactly.

### 6. Use a hook lab, not the live sequence

Before any Premiere modification, run `verify_premiere_connection`, read the server
instructions, and have the user save. Create or duplicate sandbox sequences named:

`HOOK-LAB__<slug>__A`, `HOOK-LAB__<slug>__B`, `HOOK-LAB__<slug>__C`

Use the same body after second eight in Trial mode. Never mutate the main edit until the
selected opening has passed QA. Premiere has no agent-controlled undo.

### 7. Verify pixels, then promote

Run the complete gate in `reference/QA.md`. A tool return is not visual proof. Check that
every requested frame exists on disk; use the ffmpeg composite fallback when Premiere's
`export_frame` reports success without writing a file.

After approval, promote the selected opening to the main sequence and hand the body back to
`ig-reel`.

## Hard failures

- generic talking head plus a topic label;
- a receipt mentioned but absent from frame zero;
- “trust me,” “this simple concept,” or similar bridge copy instead of a second beat;
- three candidates that differ only in wording;
- a fake metric, placeholder screenshot, or unlabeled chart;
- two text layers competing in the same frame;
- ambient motion that changes nothing about the argument;
- editing the live Premiere sequence before the storyboard gate;
- judging a hook from raw views alone or from one low-reach upload.

## Handoff

The completed handoff is:

- `HOOK-PACKET.json` — machine-readable decision and cue contract;
- `HOOK-PREVIEW.md` — links to the three storyboard strips and the selection rationale;
- rendered hook assets plus `renders/IMPORT.md`;
- sandbox sequence name(s);
- QA result and any unresolved evidence risk.

