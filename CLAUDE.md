# CLAUDE.md — vibe-editor

One raw file in, one postable vertical reel out. **The scripts do the mechanical work; the agent is the editor.**
Which takes stay, what goes on screen, where, how it moves and where the camera punches in are decisions made by
reading and watching — against the reference reels in `samples/`, studied into `samples/STYLE.md` — not rules in a
file. When a choice is taste, the samples decide; when the samples don't cover it, make the call that keeps a viewer
watching, and say why.

`README.md` is the human setup doc.

---

## The pipeline

```
raw → 01 intake → 02 transcript → 03 rough cut → 04 captions → 05 graphics → 06 audio → 07 pacing → 08 export
        RUN.md     words.json      cuts.json      captions.json  graphics-plan.json  voice-gain.json  cuts.json(zoom)  outputs/<job>.final.mp4
                                   review/takes.md renders/captions  compositions/ → renders/  sfx-plan.json  (hand-placed)  review/final-sheet.png
```

| # | Node | Script(s) | The editor's part |
|---|---|---|---|
| 01 | intake | `workflows/new-job.py <src> --slug <job> [--brief …] [--lane] [--preset vertical/<look>]` | pick the look that matches the samples |
| 02 | transcript | `workflows/transcribe.py` (WhisperX) → `validate-transcript.py` | product names in `transcript-corrections.json` |
| 03 | rough cut | `rough-cut.py --review` → `assemble.py --stage spine` · gates: `validate-edl.py`, spine silences, `check-joins.py` | **choose the takes** from `review/takes.md` → `cuts.overrides.json`; listen to every join |
| 04 | captions | `transcribe.py --spine` → `plan-captions.py` → `build-captions.py` · `verify-cut.py` | accents (if any) in `captions.overrides.json` |
| 05 | graphics | `validate-plan.py` → `build-graphics.py` (renders `compositions/*.html` or a kept preset) | **decide and write the graphics** (`ig-show`) |
| 06 | audio | `voice-gain.py` → `sfx-plan.py` | SFX/music only where they help |
| 07 | pacing | `pacing-audit.py` (a report) | zoom punches by hand (`--zoom-at`), as the samples do |
| 08 | export | `finalize.sh` → `verify-final.py` | **watch the final** before handing it over |

`./run.sh <job>` runs the mechanical nodes. `--to rough_cut` stops for the take review, `--to captions` stops for the
graphics plan, `--from <node>` resumes. With no `graphics-plan.json` there are no graphics. `--lane premiere` replays
the EDL onto a Premiere sequence and falls back to ffmpeg when the bridge is down.

## Where things live

```
samples/                    reference reels (gitignored) + STYLE.md — the bar every decision is checked against;
                            BASELINE.md + baseline/ — the approved pipeline edit (9278 v5) every edit has to match
presets/vertical/default/   numbers.json (mechanical defaults: canvas, cut, caption look, audio, export), captions.md, sfx.json + sfx/, fonts/
presets/vertical/<look>/    a look: numbers.json `extends` default, overrides only what differs; `samples` = measured from samples/ (use it)
presets/graphics/           four reusable presets (app-mock, receipt, thumb-wall, comment) + _base.html, _icons.html
lanes/ffmpeg/               assemble.py (EDL replay + layers + mix), frame.py (the only way stills are made)
lanes/premiere/             bridge.mjs, replay-edl.mjs, import-edl.mjs, place-layers.mjs, export.mjs, lab-notes.md
workflows/                  the nodes and gates; argument-driven; no project data inside
docs/lab-notes-archive.md   the war stories behind the technical locks below
brand/                      brand.json + BRAND.md (the creator's own rules — they beat everything) → tokens.css
projects/<job>/             gitignored: RUN.md raw/ transcript/ cuts.json captions.json graphics-plan.json compositions/
                            renders/ assets/ audio/ preview/ outputs/ review/
LANES.md                    step × lane matrix
```

## Skills

`ig-study` learns the samples → `samples/STYLE.md` · `ig-reel` edits a whole video · `ig-cut` takes ·
`ig-captions` captions · `ig-show` graphics · `ig-sound` audio · `ig-pacing` zooms · `ig-delivery` export ·
`premiere-pro-mcp` bridge setup. HyperFrames skills (`hyperframes-core`, `hyperframes-animation`) for writing
compositions.

## Technical locks — one line each; the story is in the archive

- `export_frame` on Premiere returns success and writes nothing → stills come only from `lanes/ffmpeg/frame.py`. archive#export-frame
- Re-rendering a `.mov` Premiere holds open fails at 90 % and leaves the old file → `_hf.render` always writes a new filename and checks mtime. archive#rerender-eperm
- `encodeSequence` can throw → `finalize.sh` falls back to the ffmpeg lane; never report an export that is not on disk. archive#encode-throws
- whisper.cpp word timing drifts 100–300 ms → WhisperX is the transcript engine. archive#whisper-drift
- `hyperframes render` needs ~10 GB temp without `--low-memory-mode` → always passed. archive#low-memory
- `crop` w/h are evaluated at init and `scale`+`crop` punches slid the face → framing and punches are one `zoompan` anchored on the face. archive#crop-expr archive#zoom-anchor
- A Jinja expression outside `{{ }}` in a preset's script block throws before the timeline registers → silently empty render; `build-graphics --golden` catches it. archive#jinja-leak
- `tokens.css` class names (`.metric`) restyle a composition's own elements → prefix every class. archive#tokens-collision
- A `class="stage"` wrapper renders a silently empty composition (HyperFrames reserves it) → a blank render with a clean lint is a name collision first. archive#stage-class
- GSAP `keyframes` arrays mis-seek in renders, and a visible-start `fromTo` paints from frame 0 → consecutive `tl.to`; `immediateRender: false`. archive#gsap-seek
- Captions under a graphic that carries words are dropped, not hidden (the glow still draws) → `mute_captions` makes a mute window. archive#mute-windows
- Never invent a metric, a screenshot, or a comparison → `validate-plan.py` refuses placeholders; numbers need provenance. An acted-out UI (no numbers, provenance says illustration) is allowed: samples/BASELINE.md. archive#no-fabrication
- Handles from `samples/` never appear in an edit → `creator.handle` only; `validate-plan.py` greps for them. archive#sample-handles
- Captions from the raw's transcript lose and shift words at every cut on a multi-take raw → captions read `transcript/spine-words.json`. archive#spine-captions
- Renders are 1080×1920; a creator's 4K sequence shows them at half size → `place-layers.mjs` scales overlays to the sequence. archive#overlay-scale
- `add_to_timeline` (even `linkAudio:false`) overwrites the same-index A track → video on a V track with an empty A lane; diff audio after. archive#timeline-eats-audio
- A creator's punched-in V1 moves the face → check graphics on their program monitor (PrintWindow). archive#punch-in-face
- Pauses at joins and breaths inside clips read as dead air → `check-joins.py` gates them (`cut.join_gap_max_s`, `cut.pause_gate_s`). archive#join-whitespace archive#breath-pauses
- Removal ids are positional and renumber → keep or remove a take by range in `cuts.overrides.json`. archive#range-keeps
- A one-word piece between two pauses was dropped as a sliver → only word-less pieces are dropped. archive#range-keeps
- `trim=duration` left a partial frame per clip and drifted the spine off the EDL → clips snap to whole frames. archive#frame-drift
- `remap-plan.py` maps cue + t, then subtracts the new cue (graphic-local times are not timeline times). archive#frame-drift
- Hand edits to `captions.json` vanish on any upstream re-run → accents live in `captions.overrides.json`. archive#caption-rerun
- One filter graph replaying N clips from a 4K raw ran out of memory → the lane renders each clip alone and joins them. archive#assemble-ram

## The agent does, and does not

Does: study the samples when they change; read every line of `review/takes.md` and listen to the spine before moving
on; decide what each video needs on screen and write it for that video with real material (on disk → the footage →
capture the real page → look it up → ask → build nothing); watch the final at full size next to a sample and next to `samples/baseline/9278-muse-v5.mp4`; hand the
user the file with what it decided and why.
Does not: ship an edit it has not watched, invent material, trust a tool's success flag, re-render onto an open file,
put the plan in chat instead of the file.
