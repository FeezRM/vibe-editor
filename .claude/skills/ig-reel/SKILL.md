---
name: ig-reel
description: "Entry point for editing a whole short-form vertical video end to end: creates the job, runs the mechanical pipeline (./run.sh), makes the editing decisions (takes, graphics, zooms) against the reference reels in samples/, watches the result, hands over the final file. Use for: edit my reel, edit this video, make this a reel, turn this into a short, finish this video, plan the edit, where do I start. Single-phase asks go straight to that node's skill."
---

# ig-reel — the editor

The scripts do the mechanical work. **You are the editor**: you decide which takes stay, what goes on screen, where,
how it moves, and when the camera punches in. The bar is the reference reels in `samples/` — studied into
`samples/STYLE.md` — not a rulebook. Nobody will describe the visuals to you; read the video, understand what it is
saying, and edit it the way the samples would.

## 0. Know what good looks like

Read `samples/STYLE.md`. If it is missing, empty, or older than any file in `samples/`, run `ig-study` first. Read
`brand/BRAND.md` for the creator's own rules — they beat everything here.

## 1. Intake → cut

```bash
python workflows/new-job.py <source.mp4> --slug <job> --brief "<the user's words, verbatim>" [--music <file>]
./run.sh projects/<job> --to rough_cut
```

## 2. Choose the takes — never skip

Read `projects/<job>/review/takes.md` top to bottom, the way a viewer will hear it (`ig-cut` → choosing takes). The
rules only remove what looks alike on paper. Mistakes that survive them are the most common reason an edit feels
amateur: a fumbled line said once, a sentence abandoned and re-said in other words, a wrong word corrected later, a
false start the transcript smoothed over, an aside to someone off camera. Write every decision into
`cuts.overrides.json`, re-run `./run.sh projects/<job> --from rough_cut --to rough_cut`, and **listen to the spine**
(`/watch projects/<job>/preview/spine.mp4`) — every join, start to end. Repeat until nothing you hear is a mistake.

## 3. Captions

```bash
./run.sh projects/<job> --from captions --to captions
```

## 4. Plan the edit

Now decide what this video needs (`ig-show`). Start from what it is *saying* and where a viewer would lose interest,
not from a list of devices. Some beats want a graphic, some a punch-in, most want nothing but the face and the words.
Do what the samples do — and when this video's content would be more engaging done differently (a recurring visual,
a cold open, a held beat, a reveal), do that, and say why in the plan's `notes`. Write `graphics-plan.json` and the
compositions it points at, then:

```bash
./run.sh projects/<job> --from graphics
```

## 5. Watch it

Watch the final (`/watch projects/<job>/outputs/<job>.final.mp4`) and pull full-size frames
(`lanes/ffmpeg/frame.py <final> <t> out.png`) at the start, middle and end of every graphic and every punch. Put
one next to a frame from a sample. For each one ask: would this be in the sample reel? Is anything covering the face
or the captions, too small to read on a phone, off-brand, generic, or there for its own sake? Fix the plan or the
composition and re-run from the node that reads it. Iterate until the answer is yes, then hand the user
`projects/<job>/outputs/<job>.final.mp4` (also copied to `~/Downloads`) with a short list of what you decided and why.

## Iteration

Change the file, re-run from the node that reads it: transcript corrections → `--from transcript`; takes
(`cuts.overrides.json`) → `--from rough_cut`; caption grouping/accents (`captions.overrides.json`) → `--from
captions`; graphics → `--from graphics` (only `dirty` graphics re-render); a zoom (`pacing-audit.py --zoom-at`) →
`--from pacing`.

## Never

- Trust a tool's success flag — read `RUN.md` gates and the files on disk.
- Ship without having watched the final.
- Put the plan in chat instead of the file.

## Premiere

**When the creator prefers their own cut, adopt it** — don't recompute it:

```bash
node lanes/premiere/import-edl.mjs projects/<job> --sequence "<their sequence>"   # V1 → cuts.json, rough_cut done
./run.sh projects/<job> --from captions --to captions
./run.sh projects/<job> --from graphics
node lanes/premiere/place-layers.mjs projects/<job> --sequence "<their sequence>__GFX" --no-gain
```

`duplicate_sequence` (clearContents:false) makes `<their sequence>__GFX` first, so their grade, framing and audio
chain stay untouched; `--no-gain` leaves A1 alone. When they want graphics on THEIR sequence, place the renders by
hand on a V track whose A lane is empty (`add_to_timeline` overwrites the same-index A track, even with
`linkAudio:false`), diff the audio tracks after, and check each graphic on the program monitor (PrintWindow) — their
V1 may punch in. They edit between turns; re-list the tracks before every change.

- **The lav offset** comes from the sequence: `get_clip_properties` on a paired V1/A1 clip gives both in-points;
  video in − audio in = the delay. Mux: `ffmpeg -i cam.mp4 -i lav.wav -filter_complex "[1:a]adelay=<ms>,apad,aresample=48000[a]" -map 0:v -map "[a]" -c:v copy -shortest`.
- **A 4K sequence** shows 1080×1920 renders at half size; `place-layers.mjs` scales overlays to seqW/1080.
  `replace_clip` does not carry the scale over.
- On Windows run the Python nodes with `PYTHONUTF8=1`.

`--lane premiere` replays the EDL as trimmable clips on `<job>__CUT`; if the bridge is down, `run.sh` continues on
the ffmpeg lane and says so in `RUN.md`. `LANES.md` lists what is scripted on each lane.
