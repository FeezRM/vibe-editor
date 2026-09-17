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
| 02 | transcript | `workflows/transcribe.py` (WhisperX large-v3, int8, silero VAD) | `validate-transcript.py` |
| 03 | rough cut | `workflows/rough-cut.py --review` → `lanes/ffmpeg/assemble.py --stage spine` | `validate-edl.py`; zero silences ≥ 0.45 s in the spine |
| 04 | captions | `plan-captions.py` → `build-captions.py` | timing within 1 frame; `measure.py` on the composite |
| 05 | graphics | `draft-plan.py` (or an agent-authored plan) → `validate-plan.py` → `face-frame.py` → `build-graphics.py` → `graphics-qa.py` → `fix-plan.py`, **≤ 3 rounds** | `graphics_qa` = zero objective defects |
| 06 | audio | `voice-gain.py` (measured LUFS) → `sfx-plan.py` (from the placed graphics) | loudness within ±1 LU |
| 07 | pacing | `pacing-audit.py --fix` (zoom punches into `cuts.json`) | zero gaps > 2.0 s |
| 08 | export | `finalize.sh` → `verify-final.py` | file exists, newer than the run, duration = EDL, 0 silences |

**`./run.sh <job>` runs all of it.** `--to captions` stops before graphics so an agent can author the
plan; `--from graphics` resumes. `--lane premiere` replays the EDL onto a Premiere sequence and falls
back to ffmpeg when the bridge is down. `tests/regress.sh` must pass before any change to
`presets/` or `workflows/` is called done.

## Where things live

```
presets/vertical/default/   WHAT — numbers.json (every constant), captions.md, creative-moves.md, sfx.json, fonts/, sfx/
presets/graphics/<name>/    the ten basic-tier presets: template.html · params.schema.json · example.json · golden.png · README.md
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

**basic** (default): the ten presets in `presets/graphics/`, placement computed, captions from the
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
- Caption entrances (slide/fade) were rejected twice → captions hard-cut only. archive#caption-motion
- Two text layers never share a frame → presets with `x-mute-captions` add a mute window; captions are dropped, not hidden. archive#mute-windows
- Never invent a metric, a screenshot, or a comparison from duplicate assets → `validate-plan.py` refuses placeholders; metrics need provenance. archive#no-fabrication
- Handles from `samples/` never appear in a mockup → `creator.handle` only; `validate-plan.py` greps for them. archive#sample-handles
- A graphic must not darken the frame → `graphics-qa.py` luma check (darkening > 25 % fails). archive#no-scrim
- The footage is sometimes the receipt (he is holding the phone up) → don't add a receipt of the same object; punch in instead. archive#footage-is-receipt

## What the agent does, and does not

Does: create the job, run `./run.sh --to captions`, author `graphics-plan.json` from `captions.json`
with **real material** (acquisition ladder: on disk → extract from footage → `workflows/capture-url.py`
→ look it up → generate a texture → ask → build nothing), run `./run.sh --from graphics`, read
`review/final-sheet.png`, hand the user the file.
Does not: put a timing constant in a skill, author a composition by hand for a job, lower a gate,
trust a tool's success flag, re-render onto an open file, put the plan in chat instead of the file.
