# CLAUDE.md — vibe-editor

One raw file in, one postable vertical reel out. **Eight nodes run in order on every job; each reads
a file and writes a file.** The preset says WHAT (looks and numbers), the lane says HOW (the app).
Every rule has one home; this file points at it and repeats nothing.

`README.md` is the human setup doc. `REWORK-PLAN.md` is why the repo looks like this.

---

## The pipeline

```
raw → 01 intake → 02 transcript → 03 rough cut → 04 captions → 05 graphics → 06 audio → 07 pacing → 08 export
        RUN.md     words.json      cuts.json      captions.json  graphics-plan.json  voice-gain.json  cuts.json(zoom)  outputs/<job>.final.mp4
                   segments.json   preview/spine  renders/captions  renders/g*.mov   sfx-plan.json    preview/*        review/final-sheet.png
```

| # | Node | Script(s) | Gate |
|---|---|---|---|
| 01 | intake | `workflows/new-job.py <src> --slug <job> [--brief …] [--lane] [--tier]` | job folder + `RUN.md` |
| 02 | transcript | `workflows/transcribe.py` (WhisperX large-v3, int8, silero VAD; overlong words clamped to silence, dropped takes re-transcribed) | `validate-transcript.py` |
| 03 | rough cut | `workflows/rough-cut.py --review` (silence, fillers, false starts, **retakes — the last take stays**) → `lanes/ffmpeg/assemble.py --stage spine` | `validate-edl.py`; zero silences ≥ 0.45 s in the spine; `check-joins.py` (no pause over 0.1 s anywhere) · `remap-plan.py` keeps the plan on its words |
| 04 | captions | `transcribe.py --spine` → `plan-captions.py` → `build-captions.py` (words from the cut's own audio) | timing within 1 frame; no overlap; `measure.py` on the composite |
| 05 | graphics | `draft-plan.py` (or an agent-authored plan) → `validate-plan.py` → `face-frame.py` → `build-graphics.py` → `graphics-qa.py` → `fix-plan.py`, **≤ 3 rounds** | `validate-plan` (text share ≤ `max_text_share`, visual variety per `graphics.variety`) · `graphics_qa` = zero objective defects |
| 06 | audio | `voice-gain.py` (measured LUFS) → `sfx-plan.py` (from the placed graphics) | loudness within ±1 LU |
| 07 | pacing | `pacing-audit.py --fix` (zoom punches into `cuts.json`) | zero gaps > 2.0 s; `check-framing.py` (face framed, punches anchored) |
| 08 | export | `finalize.sh` → `verify-final.py` | file exists, newer than the run, duration = EDL, 0 silences |

**`./run.sh <job>` runs all of it.** `--to captions` stops before graphics so an agent can author the
plan; `--from graphics` resumes. `--lane premiere` replays the EDL onto a Premiere sequence and falls
back to ffmpeg when the bridge is down. `tests/regress.sh` must pass before any change to
`presets/` or `workflows/` is called done.

## Where things live

```
presets/vertical/default/   WHAT — numbers.json (every constant), captions.md, creative-moves.md, sfx.json, fonts/, sfx/
presets/vertical/azure-void/  a look: numbers.json `extends` default, overrides only colours + graphics.skin (fonts/sfx inherited)
presets/graphics/<name>/    the basic-tier presets: template.html · params.schema.json · example.json · golden.png · README.md
                            incl. the demonstration set that ACTS the line out: script-cut, transform, drag-drop, dead-space,
                            layer-stack, stamp, phone-play, comment, shatter · shared: _base.html, _icons.html, _skins/
presets/graphics/_skins/    <skin>.css recolours every preset; picked by numbers.json → graphics.skin; goldens are the default look
presets/vertical/pixel-arcade/  a graphics STYLE: pixel-arcade skin + PixelQuest font + 12 fps stepped motion (graphics.motion_fps)
presets/vertical/broll-story/   an EDIT style: own b-roll cut on the nouns, game graphics only on the face; playbook docs/style/BROLL-STORY.md
presets/graphics/_pixel.html    the pixel engine (sprites, the creator's stand-in, 5x7 font) for pixel-quest / pixel-crowd;
                                scripts/pixel-font.py turns its font table into presets/vertical/default/fonts/PixelQuest.ttf
lanes/ffmpeg/               assemble.py (EDL replay + layers + mix), frame.py (the only way stills are made)
lanes/premiere/             bridge.mjs (MCP client), replay-edl.mjs, export.mjs, lab-notes.md
workflows/                  the nodes and gates above; argument-driven; no project data inside
docs/style/                 the PREMIUM tier: SAMPLES, FRAME-CONTRACTS, TEARDOWN, DEVICES, BLOCKS, MOTION-LANGUAGE, TEXTURE, PIPELINE, HOOK-ENGINE
docs/lab-notes-archive.md   every war story behind every lock, one anchor each
brand/                      brand.json + BRAND.md → tokens.css (generated: node scripts/brand.mjs build)
projects/<job>/             gitignored: RUN.md raw/ transcript/ cuts.json captions.json graphics-plan.json sfx-plan.json
                            compositions/ renders/ assets/ audio/ preview/ outputs/ review/
LANES.md                    step × lane matrix (✅ scripted · ✋ manual · ⚠️ unvalidated · ⛔ gap)
```

## Format table

| Format | Preset | Lane default | Notes |
|---|---|---|---|
| vertical (h > w) | `vertical/default` | ffmpeg | the only tuned preset; captions at y 920–1130, 1080×1920 |
| horizontal | `vertical/default` numbers, no vertical placement rules | ffmpeg | works but untuned — see LANES.md |

## Skills index (one line each — the SKILL.md is the home of the procedure)

`ig-reel` orchestrates a whole video · `ig-hook` the first 8 s (mode + evidence, inside the plan) ·
`ig-cut` rough cut · `ig-captions` captions · `ig-show` graphics (basic presets; premium by name) ·
`ig-sound` audio · `ig-pacing` pacing · `ig-delivery` export/QA · `premiere-pro-mcp` bridge setup.

## Tiers

**basic** (default): the presets in `presets/graphics/`, placement computed (`top` above the head / `inline` below the captions), captions from the
transcript, one SFX per visual event. Consistent and defect-free is the bar.
**premium** (opt-in by name in the brief): `docs/style/` — frame contracts, 1–3 persistent-object
scenes, the motion floor (`workflows/motion-density.py`). Same plan → build → QA loop.

## Locks — one line each; the story is in the archive

- `export_frame` on Premiere returns success and writes nothing → stills come only from `lanes/ffmpeg/frame.py`. archive#export-frame
- Re-rendering a `.mov` Premiere holds open fails at 90 % and leaves the old file → `_hf.render` always writes a new filename and checks mtime. archive#rerender-eperm
- `encodeSequence` can throw → `finalize.sh` falls back to the ffmpeg lane; never report an export that is not on disk. archive#encode-throws
- whisper.cpp word timing drifts 100–300 ms → WhisperX is the transcript engine; hyperframes transcribe is the fallback. archive#whisper-drift
- The caption/graphics type is Inter 800 lowercase + Playfair Display Italic accents, both local OFL files in `presets/vertical/default/fonts/` (Anton caps was rejected on sight; italics don't auto-resolve). archive#caption-font
- `hyperframes render` needs ~10 GB temp without `--low-memory-mode` → always passed. archive#low-memory
- `crop` w/h are evaluated at init (no `t`) → zoom punches scale then crop to fixed source dims. archive#crop-expr
- A Jinja expression outside `{{ }}` in a preset's script block throws before the timeline registers → the render is silently empty; `build-graphics --golden` catches it. archive#jinja-leak
- `.metric` exists in `tokens.css` (a light pill) → presets never reuse tokens class names for their own containers. archive#tokens-collision
- A `class="stage"` wrapper renders a silently empty composition (HyperFrames reserves the name; Chrome shows it fine) → presets prefix their container classes (`.mstage`); a blank render with a clean lint is a name collision first. archive#stage-class
- Caption entrances (slide/fade) were rejected twice → captions hard-cut only. archive#caption-motion
- Two text layers never share a frame → presets with `x-mute-captions` add a mute window; captions are dropped, not hidden. archive#mute-windows
- Never invent a metric, a screenshot, or a comparison from duplicate assets → `validate-plan.py` refuses placeholders; metrics need provenance. archive#no-fabrication
- Handles from `samples/` never appear in a mockup → `creator.handle` only; `validate-plan.py` greps for them. archive#sample-handles
- A graphic must not darken the frame → `graphics-qa.py` luma check (darkening > 25 % fails). archive#no-scrim
- The footage is sometimes the receipt (he is holding the phone up) → don't add a receipt of the same object; punch in instead. archive#footage-is-receipt
- Captions from the raw's transcript lose and shift words at every cut on a multi-take raw → captions read `transcript/spine-words.json` (the cut's own audio). archive#spine-captions
- A layer of real stills that zoom and cards of text scored 6/10 → every beat acts its line out (ig-show → act it out). archive#act-it-out
- GSAP `keyframes` arrays mis-seek in renders, and a visible-start `fromTo` paints from frame 0 → consecutive `tl.to`; `immediateRender: false`. archive#gsap-seek
- Renders are 1080×1920; a creator's 4K sequence shows them at half size → `place-layers.mjs` scales overlays to the sequence. archive#overlay-scale
- `add_to_timeline` (even `linkAudio:false`) overwrites the same-index A track before dropping its audio → video goes on a V track with an empty A lane; diff audio after. archive#timeline-eats-audio
- A creator's punched-in V1 moves the face away from the spine's face box → check graphics on their program monitor (PrintWindow) before calling them placed. archive#punch-in-face
- A 0.25 s gap at every join passed the 0.45 s silence gate and still read as "too much whitespace" → `check-joins.py` gates true silence per join (`cut.join_gap_max_s`). archive#join-whitespace
- A −50 dB floor passed 0.1–0.25 s breaths at joins and inside clips ("still too much pause … muse") → every pause relative to speech is cut (rough-cut 7c) and gated (`cut.pause_gate_s`). archive#breath-pauses
- Removal ids are positional — moving one word renumbered them and `keep_ids` vetoes hit the wrong takes (9287) → keep a take by range: `cuts.overrides.json` `{"keep": [{"in","out","why"}]}`. archive#range-keeps
- A one-word piece between two pauses ("This … is my other account") was dropped as a sliver and the next clip started mid-word → `drop_slivers` only drops word-less pieces; short word pieces are padded to `min_sliver_frames`. archive#range-keeps
- `trim=duration` left a partial frame per clip; 34 clips drifted the spine 0.17 s off the EDL and every offset-based check read the wrong frames → rough-cut snaps clips to whole frames, the lane cuts by frame count. archive#frame-drift
- `remap-plan.py` first moved graphic-local times (`reveal_at`, params `*_at`) as timeline times and broke every beat of a graphic not cued at 0 → cue + t is mapped, the new cue subtracted. archive#frame-drift
- The matte model keeps a wall picture touching the hair (9280: a figure on his head) → `bg-plate.py` keeps only a skull ellipse above the face box. archive#matte-head
- `scale` (eval=frame) + `crop` x/y grew punches from the corner and slid the face → framing and punches are one face-anchored `zoompan`; `check-framing.py` measures it. archive#zoom-anchor
- Re-centring each clip and punches still in at the cut made every jump cut snap → framing matches the face's position and size across each join, punches ease out before it; `check-framing.py` gates the jump. archive#cut-match
- Hand edits to `captions.json` vanish on any upstream re-run, and a pacing spine rebuild made `plan-captions` fall back to the raw transcript → accents live in `captions.overrides.json`; spine words are keyed to the cut (`spine-words.key`). archive#caption-rerun
- One filter graph replaying N clips from a 4K raw queued every decoded frame ahead of `concat` (23 GB, out of memory) → the lane renders each clip alone into `preview/clips/` and joins them with the concat demuxer. archive#assemble-ram
- Stock overlays, stills that only zoom and generic counters were rejected → graphics play the line as a scene with the creator's stand-in (ig-show → play it). archive#creativity-floor

## What the agent does, and does not

Does: create the job, run `./run.sh --to captions`, author `graphics-plan.json` from `captions.json`
with **real material** (acquisition ladder: on disk → extract from footage → `workflows/capture-url.py`
→ look it up → generate a texture → ask → build nothing), run `./run.sh --from graphics`, read
`review/final-sheet.png`, hand the user the file.
Does not: put a timing constant in a skill, author a composition by hand for a job, lower a gate,
trust a tool's success flag, re-render onto an open file, put the plan in chat instead of the file.
