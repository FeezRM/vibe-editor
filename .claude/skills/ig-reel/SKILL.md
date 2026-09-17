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
2. **The graphics plan** is the only creative document. It is written *after* captions exist so every
   cue is a real timeline time from `captions.json`. Rules in `ig-show`.
3. **Review** is taste only, and it is done at **full frame size**: pull 4–6 frames from the final with
   `lanes/ffmpeg/frame.py <final> <t> out.png` (one per graphic) and look at them next to a frame from the
   reference reel in `samples/` or the user's own last video. A contact sheet hides bad type and small
   cards — the first output of this pipeline shipped with both because it was judged from one. Objective
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

`--lane premiere` replays the EDL as trimmable clips on `<job>__CUT` for the user's hand refinement,
then imports renders. The bridge must be started in Premiere first (`premiere-pro-mcp`); if it is
down, `run.sh` continues on the ffmpeg lane and says so in `RUN.md`. See `LANES.md` for what is
scripted on each lane.
