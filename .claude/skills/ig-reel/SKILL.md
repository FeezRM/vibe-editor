---
name: ig-reel
description: "Entry point for editing a whole short-form vertical video end to end: creates the job, runs the pipeline (./run.sh), authors the graphics plan with real material, reviews the QA sheet, hands over the final file. Use for: edit my reel, edit this video, make this a reel, turn this into a short, finish this video, plan the edit, where do I start. Single-phase asks go straight to that node's skill."
---

# ig-reel — the orchestrator

You run a pipeline of files. You do not edit a timeline by hand and you do not describe an edit in
chat. Read `CLAUDE.md` (the map) and `presets/vertical/default/numbers.json` (every constant) once.

## The run

```bash
python workflows/new-job.py <source.mp4> --slug <job> --brief "<the user's prompt, verbatim>" [--music <file>]
./run.sh projects/<job> --to captions          # transcript → EDL → spine → captions
# author projects/<job>/graphics-plan.json    (see ig-show; draft-plan.py gives you a start)
./run.sh projects/<job> --from graphics        # graphics loop → audio → pacing → export
```

Then open `projects/<job>/review/final-sheet.png` and `review/qa-round-N.png`, and hand the user
`projects/<job>/outputs/<job>.final.mp4` (also copied to `~/Downloads`). Report what the gates said.

## What you decide

1. **Brief → job.** Copy the user's words into `--brief`. If they name a tier (`premium`), a lane
   (`premiere`), or a music file, pass it. Never guess a music track.
   **Pick the look:** a talking head carried by the creator's own b-roll → `--preset vertical/broll-story`
   (playbook `docs/style/BROLL-STORY.md`; graphics in the `pixel-arcade` style); graphics-led reels → `vertical/default`
   or `vertical/pixel-arcade` / `azure-void` for a look.
2. **The graphics plan** is the only creative document. It is written *after* captions exist so every
   cue is a real timeline time from `captions.json`. Rules in `ig-show`.
3. **Measure before you look.** The creator judges by ear and by framing, and twice called a reel that passed every
   gate wrong ("too much whitespace", "the zooming in is completely off"). Before handing anything over, read these
   numbers off the files, not the success lines, and fix what fails:
   - `check-joins.py` — every join's true silence ≤ `cut.join_gap_max_s` (whitespace at the cuts);
   - `verify-cut.py` — every kept word is heard in the spine (no clipped first/last syllable);
   - `check-framing.py` — face where the creator's framing puts it in every clip, every punch anchored on the face;
   - one frame of the final next to one frame of his last posted reel (`Desktop/Raw Vid/COMPLETED/Posted`), same
     size: is he as big in frame, is the frame as full? If his reel is tighter, raise `framing.scale` in his look;
   - the export's peak RAM stays in the low GB (the lane renders clips one at a time — if it climbs, the lane is
     holding 4K frames again; stop it, don't wait it out).
4. **Review** is taste only, and it is done at **full frame size**. First question at every frame:
   *is this a visual or a sentence?* Count the text-only graphics; if the layer reads as captions in
   boxes, re-plan with `ig-show` §"Show, don't caption" before anything else. Then: pull 4–6 frames from the final with
   `lanes/ffmpeg/frame.py <final> <t> out.png` (one per graphic) and look at them next to a frame from the
   reference reel in `samples/` or the user's own last video. A contact sheet hides bad type and small
   cards — the first output of this pipeline shipped with both because it was judged from one.
   Second question, per graphic: *does something happen on the word?* A still that slowly zooms or a
   screenshot that scrolls is a picture, not a motion graphic; the creator scored a layer of those 6/10
   and wanted every beat acted out (`ig-show` → act it out). Pull 2–3 frames *inside* each graphic, not
   one, so you see the action, not its end state. Objective
   defects are gone by construction (`graphics_qa: pass`); if the node is `blocked`, read
   `review/qa-round-3.json`, fix the plan, re-run `--from graphics`.

## What you never do

- Put a constant in a skill; edit `presets/vertical/default/numbers.json` instead.
- Author a composition by hand for one job — add a preset (`presets/graphics/<name>/` with schema,
  example and golden) and use it.
- Trust `success: true` from any tool. Read `RUN.md` gates and the files on disk.
- Run graphics before captions, or audio before graphics — `run.sh` refuses, and so should you.

## Iteration

Change the file, re-run from the node that reads it: transcript corrections → `--from transcript`;
a vetoed cut (`cuts.overrides.json`) → `--from rough_cut`; caption grouping/accents → `--from captions`;
a graphic → `--from graphics` (only dirty graphics re-render). Nothing downstream is rebuilt by hand.

## Premiere

**The creator prefers their own cut.** Don't recompute it — adopt it. Make a job from the same footage
(the raw the sequence uses; mux the lav first if they synced one), then:

```bash
node lanes/premiere/import-edl.mjs projects/<job> --sequence "<their sequence>"   # V1 → cuts.json, rough_cut done
./run.sh projects/<job> --from captions --to captions                              # captions on THEIR timeline
# reuse an existing plan: remap every cue/reveal old-timeline → source → new-timeline (Timeline.to_source/to_timeline)
./run.sh projects/<job> --from graphics
node lanes/premiere/place-layers.mjs projects/<job> --sequence "<their sequence>__GFX" --no-gain
```

`duplicate_sequence` (clearContents:false) makes `<their sequence>__GFX` first, so their grade, framing
and audio chain stay untouched; `--no-gain` leaves A1 alone.

**When they want it on THEIR sequence** (b-roll added to the cut they're still touching): don't run
`place-layers.mjs` there — it lifts V2–V4 and adds the pipeline's captions over theirs. Build and QA the graphics
with the pipeline, then place the renders by hand on a V track whose A lane is empty (`add_to_timeline` overwrites
the same-index A track, even with `linkAudio:false`), diff the audio tracks after, and check each graphic on the
program monitor: their V1 may punch in, so the face is not where the spine's face box says. They edit between
turns; re-list the tracks before every change. The full procedure is `docs/style/BROLL-STORY.md` §7.
`verify-cut` fails on a multi-take raw under an adopted cut (transcription disagreement, not a cut defect):
report the gate, run `plan-captions.py` + `build-captions.py` so the graphics have cue words. Face boxes come from the job's spine, not
their punched-in frame — check the program monitor (PrintWindow) after placing.

- **The lav offset** comes from the sequence itself: `get_clip_properties` on a paired V1/A1 clip gives
  both in-points; video in − audio in = the delay (9.767 s on 9077, constant across all clips — check the
  first and last pair). Mux: `ffmpeg -i cam.mp4 -i lav.wav -filter_complex "[1:a]adelay=<ms>,apad,aresample=48000[a]" -map 0:v -map "[a]" -c:v copy -shortest`.
- **A 4K sequence** (2160×3840) shows 1080×1920 renders at half size. `place-layers.mjs` now scales every
  overlay to seqW/1080 (200 %) and reports it; `replace_clip` does not carry the scale over, so after
  swapping one render set `scale` again, then PrintWindow to confirm.
- **Re-placing after a rebuild**: run `place-layers.mjs` again. It lifts V2–V4 first; no need to delete the
  sequence. Save the project with `save_project` and check the `.prproj` mtime.
- On Windows run the Python nodes with `PYTHONUTF8=1`: without it `new-job.py` dies printing `→`, and a
  file read in cp1252 turns `·` into `Â·` inside a render.


`--lane premiere` replays the EDL as trimmable clips on `<job>__CUT` for the user's hand refinement,
then imports renders. The bridge must be started in Premiere first (`premiere-pro-mcp`); if it is
down, `run.sh` continues on the ffmpeg lane and says so in `RUN.md`. See `LANES.md` for what is
scripted on each lane.
