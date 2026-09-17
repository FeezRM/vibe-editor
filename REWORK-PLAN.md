# REWORK PLAN — from taste spec to one-shot editor

> **Status 2026-09-12 — implemented.** Phases 0–9 are built and gated on this Mac: `./run.sh <job>` runs the
> eight nodes unattended on the ffmpeg lane; `tests/regress.sh` covers the ten presets and the fixture's EDL
> and caption grouping; docs are on the one-home rule (`CLAUDE.md` ≈ 1,100 words, skills ≤ 600, 0 broken
> links). Open: the Premiere lane is written but unvalidated (bridge not started here); the fixture carries
> burnt-in captions (swap in a raw take); caption case is a `numbers.json` switch. Details: `LANES.md`,
> `docs/lab-notes-archive.md`.

**Audience:** the AI agent implementing this. Read it top to bottom once, then work the phases
in order. Every phase ends in a command that can fail. Do not skip to a later phase because an
earlier gate is inconvenient — the gates are the product.

**Goal:** `one prompt + raw footage → postable vertical reel`, unattended, at or above the
consistency of Jason Cooperson's one-shot editor (YouTube `7MaARoS9o2s`, artifact "Video Editor
Map"). "Postable" means: zero objective defects (no dead air, no drifting captions, no graphic
over a face, no invented number, no two text layers, voice at target loudness, export exists on
disk), a small locked visual vocabulary applied consistently, and a human review that is *taste
only*.

---

## 0. Ground truth — verified 2026-09-11, do not re-derive

### 0.1 What the reference actually is

Jason's system (from the video and the artifact, both read in full):

- **Thesis:** the model lacks taste and workflow knowledge, so *lock the style into presets*
  and give the model a pipeline of scripted nodes. Every zoom-in, pop-in, rise-in is a
  hand-tuned preset. The model chooses *which* preset and *when*; it never decides *how it moves*.
- **Eight linear nodes**, each with a declared input file, output file and owner:
  Intake → Rough cut (`WhisperX` once → `cuts.json` EDL + canonical transcript) → Audio polish
  (measured: `voice-gain.py` → −17 LUFS into a −6 dBFS limiter) → Grade (long-form only) →
  Graphics (`graphics-plan` → `graphics-build` → `graphics-qa.py` must be green → `edit-review`
  loop, defects → rebuild, **cap 3**) → SFX (`sfx-plan.py` derived from the *placed* graphics
  → `place-sfx.py`) → Music (opt-in, flat −18 dB bed, 2 s tail) → Review (human, taste only) →
  Export (`finalize.sh`).
- **WHAT vs HOW:** `presets/` holds looks and numbers, app-independent. `lanes/<app>/` holds
  mechanics (`premiere-bridge.mjs`, `audio-polish.py`, `grade-lut.py`, `place-graphics.py`,
  `place-sfx.py`, `place-music.py`). `LANES.md` is the step × app matrix (✅ scripted / ✋
  manual / ⚠️ unvalidated / ⛔ gap). Adding an app changes no preset.
- **State:** `projects/<job>/RUN.md` is the state file a session reads first.
- **Docs diet:** one-home rule (every rule lives in exactly one file, everything else points);
  CLAUDE.md 8,000 → 3,832 words; documents opened per job 45 → 17; war stories moved to
  `docs/lab-notes-archive.md`; `docs/check-links.py` keeps pointers honest.
- **Default tier is basic:** "blue cards plus the creative-moves vocabulary. Bigger looks are
  opt-in by name."
- **Observed output** (frames of the one-shot intro): ~six devices reused consistently — one
  phrase of white caption with an italic-serif accent word; a blue check-list card popping in
  top-right; a left-to-right flow diagram; a chat mockup; a wall of real thumbnails with a red
  strike-through; a REC-frame overlay; punch-ins. **Postable because consistent and clean, not
  because spectacular.** 2h42m runtime, horizontal talking-head only, **no vertical preset**.

### 0.2 What this repo is today

- ~50k words of prose across CLAUDE.md, README, HOOK-ENGINE.md, eight skills and ten reference
  docs. **Four scripts** in `analysis/`: `measure.py` (caption geometry), `motion-density.py`
  (tween counter), `build-captions.py` (words → caption HTML; carries a hard-coded per-project
  `ACCENT` dict), `validate-hook-packet.py`. Nothing cuts, places, mixes or exports.
- Every timeline operation is the agent driving 283 Premiere MCP tools one call at a time.
- The graphics doctrine (`ig-show`, 9.5k words) sets a ceiling — frame contracts, 1–3 scenes,
  persistent-object state machines, ≥25 tweens — and states that *every composition ever
  produced fails it*. There is no basic tier.
- `templates/base/` holds four blocks that "deliberately fail the motion floor." No preset
  library exists.
- Transcription = `npx hyperframes transcribe` = whisper.cpp `small.en`, token-level word
  timestamps (drift 100–300 ms on fast speech; merges fillers).
- `projects/` is empty on this machine. `this summer.mp4` / `this summer... v2.mp4` in the root
  are **Faiz's own hand edit** (700 views; `IMG_8967.png` shows 50 % of viewers gone by ~3 s).
  They are the creator's baseline, not agent output. The "mediocre" agent runs were on Windows.
- Known Premiere defects (CLAUDE.md, verified on Windows 11 / Premiere 26): `export_frame`
  returns success and writes nothing; `encodeSequence` can throw; re-rendering a `.mov`
  Premiere has open fails at ~90 % and leaves the old file.
- Machine: macOS, Node 24, ffmpeg 8, Python 3.13 default, **`/opt/homebrew/bin/python3.11`
  and `uv` present**. Premiere MCP server built at
  `vendor/adobe-premiere-pro-mcp/dist/index.js` (v1.2.0, ships `@modelcontextprotocol/sdk`);
  `.mcp.json` sets `PREMIERE_TEMP_DIR=/tmp/premiere-mcp-bridge`.
- Brand: `brand/brand.json` (handle `feezkera`, 1080×1920 @30, caption band y 920–1130, accent
  `#FFC531`, red `#EB0408`, green `#00E800`, fonts Anton / Inter / JetBrains Mono),
  `brand/BRAND.md` (voice, banned/required on screen), `brand/tokens.css` generated by
  `node scripts/brand.mjs build` and already defining `.ig-*`, `.reel`, `.chart`, `.wash`,
  `.hook`, `.phone`, `.tile-wall`, `.skel-*`, `.beside`, `.cutaway`, `.stage` etc.

### 0.3 The five principles the rework enforces

1. **Nodes exchange files, not chat.** Every step reads a file and writes a file. If a step's
   output is not on disk, the step did not happen.
2. **WHAT lives in `presets/`, HOW lives in `lanes/`.** A skill names a preset and a cue; a
   preset owns its motion; a lane owns its app. No skill contains a timing constant or a tool
   call sequence.
3. **A gate that cannot fail is not a gate.** Every gate is a script with a non-zero exit,
   run by the pipeline, not a checklist the agent remembers. Verify with pixels and file
   timestamps, never a tool's return code.
4. **Basic tier by default.** ≤10 presets, applied consistently, zero defects. The existing
   premium doctrine (scenes, frame contracts, persistent objects) stays, opt-in by name.
5. **One home per rule.** Prose that says "this used to say X, that was wrong" goes to the
   archive. Skills become ≤1,200-word maps that point at scripts, presets and schemas.

---

## 1. Target layout

```
vibe-editor/
  CLAUDE.md                 ≤3,500 words: the pipeline, the format table, skills index, folder map, locks
  LANES.md                  step × lane matrix (✅ ✋ ⚠️ ⛔), the WHAT/HOW law, universal audio target
  run.sh                    the one-shot entry: run.sh <job-dir> [--lane ffmpeg|premiere] [--tier basic|premium]
  finalize.sh               promote the lane's render to outputs/<job>.final.mp4 (+ copy to ~/Downloads)
  brand/                    unchanged contract (brand.json, BRAND.md, tokens.css generated)
  presets/
    vertical/default/       THE house preset for 9:16 (this repo's differentiator — Jason has none)
      README.md             step index: which node reads which file here
      numbers.json          every number a lane needs: caption band, sizes, entrance ms, hold s, LUFS, dB, zoom %
      captions.md           the caption look (points at numbers.json; no numbers in prose)
      creative-moves.md     the basic-tier vocabulary: when each preset is the right answer
      sfx.json              graphic verb → sound file (relative to assets/sfx/)
    graphics/               one folder per preset (see §4.3)
      <name>/template.html  HyperFrames composition with {{param}} slots
      <name>/params.schema.json
      <name>/README.md      what it shows, what REAL content it needs, when not to use it
      <name>/example.json   a params file that renders
      <name>/golden.png     rendered reference frame for regression
  lanes/
    ffmpeg/                 assemble.py (EDL + overlays + audio → mp4), frame.py (composite stills)
    premiere/               bridge.mjs, replay-edl.mjs, place-graphics.mjs, place-audio.mjs, export.mjs, lab-notes.md
  workflows/                universal, argument-driven, no project data inside
    transcribe.py           WhisperX → transcript/words.json (+ segments.json)
    rough-cut.py            words.json → cuts.json
    validate-edl.py         cuts.json sanity (monotonic, no <8-frame slivers, source in range)
    build-captions.py       moved from analysis/, project data removed, reads presets numbers
    validate-plan.py        graphics-plan.json against schemas + asset existence + no placeholders
    build-graphics.py       graphics-plan.json + presets → compositions → renders (hyperframes)
    graphics-qa.py          composited pixels: band, face, luma, alpha, timestamps
    face-frame.py           face / chin bbox per cue from the A-roll (opencv haar, ships with cv2)
    voice-gain.py           ebur128 measure → gain to target
    sfx-plan.py             placed graphics → sfx-plan.json
    pacing-audit.py         event log from EDL + plan + captions → gaps > threshold
    check-links.py          every relative link in docs resolves
  analysis/                 gitignored scratch ONLY (measure.py and motion-density.py move to workflows/)
  docs/
    style/                  the current ig-show/reference/*.md, as the PREMIUM tier reference
    lab-notes-archive.md    every "this used to say" paragraph, one anchor each
  .claude/skills/           one skill per node, each a map (≤1,200 words) pointing at the above
  projects/<job>/           gitignored
    RUN.md                  state file, read first, updated by every node
    raw/                    copied source, never moved
    transcript/words.json  segments.json  corrections-applied.json
    cuts.json               the EDL
    graphics-plan.json      sfx-plan.json  captions.json
    compositions/  renders/  assets/  audio/
    preview/                ffmpeg-lane renders per stage (spine.mp4, spine+captions.mp4, …)
    outputs/<job>.final.mp4
    review/                 composite stills + qa reports per round
```

Keep `HOOK-ENGINE.md`, `templates/`, `samples/` until Phase 8 decides their fate; do not delete
anything before its replacement passes its gate.

---

## 2. Job folder contract and `RUN.md`

`RUN.md` is machine-readable front matter plus human notes. Every node reads it first, appends
its result, and never rewrites another node's block.

```markdown
---
job: <slug>
source: raw/<file>            # copied by intake, checksum recorded
format: vertical              # from aspect: vertical | horizontal
fps: 30                       # from brand.json canvas.fps
lane: ffmpeg                  # ffmpeg | premiere
tier: basic                   # basic | premium
preset: vertical/default
nodes:
  intake:      {status: done, at: 2026-09-11T19:00Z, out: raw/…}
  transcript:  {status: done, at: …, out: transcript/words.json, engine: whisperx-large-v3-int8}
  rough_cut:   {status: done, at: …, out: cuts.json, kept_s: 41.2, cut_s: 18.6}
  captions:    {status: pending}
  graphics:    {status: pending, rounds: 0}
  audio:       {status: pending}
  pacing:      {status: pending}
  export:      {status: pending}
gates:
  validate_edl: pass
  graphics_qa:  n/a
---
## Notes
- <node>: <one line of what was decided and why>
```

Rules:
- `run.sh` refuses to run a node whose predecessor is not `done`.
- A node re-run invalidates every node after it (statuses flip to `stale`); the `ffmpeg` lane
  re-renders cheaply, the `premiere` lane re-replays.
- The user's prompt is stored verbatim in `RUN.md` under `## Brief`, and any instruction in it
  that names a preset or tier overrides `presets/` for that job only.

---

## 3. Phases

Each phase: **Build** (files), **Spec** (behaviour), **Gate** (a command that fails). Phases 1–3
make a verifiable spine with no Premiere at all. Phases 4–6 add the layers. Phase 7 is the
one-shot run. Phase 8 is the docs diet. Phase 9 is the vertical preset and the feedback loop.
Do not reorder 1 → 2 → 3; everything keys off the transcript.

### Phase 0 — Harness and fixtures

**Build**
- `run.sh` skeleton: parses job dir, reads `RUN.md`, dispatches nodes in order, stops at the
  first failing gate, prints the gate's output verbatim.
- `workflows/new-job.py <source-file> --slug <slug>`: creates the job folder, copies the source
  into `raw/` (never move), records checksum + duration + aspect, writes initial `RUN.md`.
- A fixture: copy `this summer.mp4` into `projects/fixture-summer/raw/` and treat the *raw*
  source of that reel (ask Faiz for the unedited take if available; otherwise the reel itself
  is the fixture) as the regression input for every later gate.
- `lanes/ffmpeg/frame.py <video> <t> [--overlay mov] → png`: the composite still tool every QA
  script calls. Pull this out of the CLAUDE.md fallback command; it becomes the only way stills
  are made.

**Gate**
```bash
./run.sh projects/fixture-summer --to intake && test -f projects/fixture-summer/RUN.md
```

### Phase 1 — Transcript: WhisperX, once

**Build**
- Environment: `uv venv --python 3.11 .venv-whisperx && uv pip install --python .venv-whisperx whisperx`
  (Python 3.13 will not take torch cleanly; 3.11 is on this machine). Record the exact
  versions in `LANES.md`.
- `workflows/transcribe.py <job>`:
  1. `ffmpeg -vn -ac 1 -ar 16000` → `transcript/audio.wav`.
  2. `whisperx transcript/audio.wav --model large-v3 --compute_type int8 --device cpu
     --language en --vad_method silero --output_format json --highlight_words True`.
     `silero` avoids the Hugging Face token; `int8` is the only CPU-viable compute type.
     Fall back to `medium.en` if a 60 s source takes > 6 min.
  3. Normalise to `transcript/words.json`: `[{ "w": "imma", "s": 0.42, "e": 0.61,
     "score": 0.91, "seg": 0, "end_punct": "" }]` — this is the shape
     `build-captions.py` already expects (`w`, `s`, `e`, `end_punct`), so keep it.
  4. **Unaligned tokens** (WhisperX gives no timing to tokens without dictionary characters:
     `$10k`, `2014.`, emoji) → interpolate linearly between the neighbours' boundaries and mark
     `"interp": true`. Never drop a word.
  5. Apply `presets/vertical/default/transcript-corrections.json` (`{"content spy": "ContentSpy",
     "fees": "Feez"}`), case-insensitive, whole-word; log every hit to
     `transcript/corrections-applied.json`. This is the *only* place the transcript is edited;
     grammar is never corrected (BRAND.md: preserve exact grammar and slang).
  6. Write `transcript/segments.json` (sentence-level from WhisperX) for the rough-cut reader.
- Keep `npx hyperframes transcribe` as `--engine hyperframes` fallback; record which engine ran
  in `RUN.md`.

**Gate**
```bash
python workflows/transcribe.py projects/fixture-summer && python workflows/validate-transcript.py projects/fixture-summer
```
`validate-transcript.py` fails on: non-monotonic times, a word > 2.5 s long, a gap inside a
segment > 1.5 s with no `interp` flag, fewer than 1.5 words/s over the whole file, any word
with `score < 0.3` that is not flagged.

**Why this first:** every later node (cuts, captions, cue times, SFX, pacing) keys off word
onsets. whisper.cpp small.en drift is why "cut on the breath" was never achievable.

### Phase 2 — Rough cut as data, and two lanes to replay it

**Build**
- `workflows/rough-cut.py <job>` → `cuts.json`:
  ```json
  { "source": "raw/x.mp4", "fps": 30, "keep": [
      { "in": 0.38, "out": 4.92, "reason": "speech", "lead_s": 0.08 },
      { "in": 6.10, "out": 9.77, "reason": "speech", "lead_s": 0.06 } ],
    "removed": [ { "in": 4.92, "out": 6.10, "reason": "silence" },
                 { "in": 11.02, "out": 11.31, "reason": "filler:um" } ],
    "stats": { "kept_s": 41.2, "removed_s": 18.6, "clips": 14, "mean_clip_s": 2.9 } }
  ```
  Rules (all from `presets/vertical/default/numbers.json`, not hard-coded):
  - remove gaps between words ≥ `cut.min_gap_s` (default 0.35) leaving `cut.lead_s` before the
    next word onset (the "cut on the breath" rule, now a number);
  - remove filler tokens from `cut.fillers` (um, uh, hmm) and standalone repeats ("I think— I
    think"); **never** remove words in `cut.keep_tics` (like, you know, basically) — those are
    voice per BRAND.md;
  - never produce a kept clip shorter than `cut.min_clip_s` (0.6) — merge with its neighbour
    instead;
  - a `--review` flag prints a table of every removal with its words so the agent (or a
    sub-agent loop) can veto entries by id; vetoes are written to `cuts.overrides.json` and
    re-applied deterministically. This is the "recursive loop" Jason runs on the rough cut —
    implemented as a file, not as chat.
- `workflows/validate-edl.py`: monotonic, inside source duration, no sliver < 8 frames, no
  overlap, stats recomputed and matching.
- `lanes/ffmpeg/assemble.py <job> --stage spine`: concat the `keep` ranges with
  `-ss/-to` + `concat` (re-encode, `-r 30`, `-pix_fmt yuv420p`), output
  `preview/spine.mp4`. Same script later takes `--stage captions|graphics|audio|final` and
  overlays the alpha renders at their cue times (`overlay=enable='between(t,a,b)'`) and mixes
  the audio stems. **This lane is the verification lane on every machine and the delivery
  lane where Premiere is absent or broken.**
- `lanes/premiere/bridge.mjs`: an MCP *client* that spawns
  `vendor/adobe-premiere-pro-mcp/dist/index.js` over stdio (`@modelcontextprotocol/sdk`
  `Client` + `StdioClientTransport`, env from `.mcp.json`) and exposes
  `call(toolName, args)`; every other lane script imports it. First call is always
  `verify_premiere_connection`; if it fails, the script exits 2 with the CLAUDE.md bridge
  checklist printed, and `run.sh` falls back to `--lane ffmpeg` and records that in `RUN.md`.
- `lanes/premiere/replay-edl.mjs <job>`: creates the 1080×1920 sequence and the track
  architecture (`add_track` then `list_sequence_tracks`, never assume an index), imports the
  raw, places every `keep` range as its own trimmable clip on V1/A1 in order, then **reads
  every clip back** with `get_clip_properties` and writes `premiere/replay-verify.json`.
  Never a flat render onto the timeline — the human refines this later.

**Gate**
```bash
python workflows/rough-cut.py projects/fixture-summer && python workflows/validate-edl.py projects/fixture-summer \
 && python lanes/ffmpeg/assemble.py projects/fixture-summer --stage spine \
 && ffmpeg -i projects/fixture-summer/preview/spine.mp4 -af silencedetect=n=-35dB:d=0.45 -f null - 2>&1 | grep -c silence_start   # must print 0
```
Premiere lane gate (only when Premiere is open): `replay-verify.json` clip count equals
`cuts.keep` length and every in/out matches within 1 frame.

### Phase 3 — Captions from words, no eyeballing

**Build**
- Move `analysis/build-captions.py` → `workflows/build-captions.py`; delete the hard-coded
  `ACCENT` dict; read sizes, band, max words, width ceiling and glow from
  `presets/vertical/default/numbers.json`; read emphasis from `captions.json` (below).
- `workflows/plan-captions.py <job>` → `captions.json`: groups words per the existing rules
  (one line, 2–4 words, ≤ width ceiling, never end on a function word, hard cuts), remaps
  times through `cuts.json` (source time → timeline time), and assigns emphasis:
  `{"idx": 12, "text": "no progress", "s": 8.21, "e": 9.02, "accent": {"word": "no", "cls": "bad"}}`.
  Emphasis is chosen by the agent in a **review pass over this file** (≤ 40 % of groups, one
  colour per line, payload word only), not by a global dictionary. Mute windows come from
  `graphics-plan.json` and are applied here at build time by *dropping* groups, not by opacity.
- Render once per job to `renders/captions.mov` (alpha) at the sequence fps.
- Move `analysis/measure.py` → `workflows/measure.py` unchanged.

**Gate**
```bash
python workflows/plan-captions.py projects/fixture-summer && python workflows/build-captions.py projects/fixture-summer \
 && python lanes/ffmpeg/assemble.py projects/fixture-summer --stage captions \
 && python workflows/measure.py projects/fixture-summer/preview/spine+captions.mp4 3.0,9.5,17.2,30.1   # cap 58–65px, width ≤78%, one line
```
Plus a timing check inside `build-captions.py`: every group's `s` equals its first word's
timeline onset within 1 frame, or the build fails.

### Phase 4 — The preset library and the graphics loop (the phase that decides quality)

This replaces "author a bespoke GSAP composition per video" with "choose a preset, fill it with
real content, render, QA, loop."

**4.1 Preset contract** — every folder under `presets/graphics/<name>/`:
- `template.html`: a complete, lint-clean HyperFrames composition at 1080×1920 with the root
  `data-*` attributes, `gsap.timeline({paused:true})` registered synchronously, deterministic
  (no random/clock/`repeat:-1`), `background: transparent`, composed from `tokens.css`
  classes, with `{{param}}` slots (`{{title}}`, `{{rows}}`, `{{image_1}}`, `{{duration}}`).
  Entrances 0.28–0.42 s, hold ≥ 0.8 s, **no exit** (the cut is the exit), never
  bounce/elastic/back. Motion vocabulary per preset is fixed and tuned once, by hand, by
  looking at a render.
- `params.schema.json`: JSON Schema; every string param that carries content is marked
  `"x-real": true`, which `validate-plan.py` uses to refuse placeholders (`Hook 1`, `Lorem`,
  `[`, `TBD`, `?`, empty, or any handle found in `samples/`).
- `README.md`: one paragraph — what it shows, the real material it needs, when it is wrong.
- `example.json` + `golden.png`: the example renders, and `graphics-qa.py --golden` compares
  the rendered frame at `t=1.0` against `golden.png` (SSIM ≥ 0.97) so a preset edit that
  changes the look is a deliberate, visible diff.

**4.2 Placement is a parameter, not a decision.** `placement` ∈ `beside-l | beside-r |
cutaway | wash | inline`. `face-frame.py` computes the face bbox at each cue from the A-roll;
`build-graphics.py` picks `beside-l/-r` automatically as the side the face is *not* on and
refuses `cutaway` for any cue where a caption group is not muted. The band y 920–1130 is a
no-content zone for every preset except `wash`.

**4.3 The basic tier — build these ten, in this order, each to its golden frame before the next**

| # | Preset | Shows | Real content required | Jason equivalent |
|---|---|---|---|---|
| 1 | `phrase` | one 2–5 word line, one accent word, `.hook` classes at 108/118 px | the exact spoken words | italic-serif accent line |
| 2 | `list-card` | titled card, N rows with ✓ / ✗ appearing on cue | row strings from the transcript | the blue check-list card |
| 3 | `flow` | 2–4 nodes left→right with arrows, appearing on cue | node labels from the transcript | Raw Footage → Entire Edit → Postable |
| 4 | `thumb-wall` | grid of real images, optional red strike / gold outline on one | image files with provenance | the YouTube thumbnail wall |
| 5 | `app-mock` | `.phone` frame with a real screenshot, optional `.annot-*` box | the screenshot file | — (vertical-native) |
| 6 | `chat` | DM/chat mockup, messages appearing in order | message strings, `creator.handle` | the chat mockup |
| 7 | `metric` | one big `.readout` number + unit, counts up | the real number and its source | — |
| 8 | `wash` | bad/good edge flood pair (`.wash--bad` then `.wash--good`), face core clear | none | — |
| 9 | `receipt` | a real screenshot/still shown at an angle with `.lift` shadow, one label | the file | — |
| 10 | `rec-frame` / `zoom-punch` | REC corners overlay; the zoom is a lane preset (2–4 % over 1.2 s) | none | REC overlay + punch-ins |

Nothing else exists in the basic tier. Three consecutive uses of the same preset is a
`validate-plan.py` warning; four is a failure.

**4.4 The plan file** — `graphics-plan.json`, written by the agent from `words.json` +
`cuts.json` + BRAND.md + `presets/vertical/default/creative-moves.md`:
```json
{ "tier": "basic", "graphics": [
  { "id": "g01", "preset": "list-card", "cue": 12.40, "trigger": "lacks", "duration": 4.2,
    "placement": "auto", "mute_captions": false, "sfx": "pop",
    "params": { "title": "CLAUDE BY ITSELF LACKS", "rows": ["Creativity", "Taste", "Workflow instructions"] },
    "assets": [], "provenance": "rows are the spoken list at 12.4–15.9" } ],
  "caption_mute_windows": [[0.0, 2.6]] }
```
`cue`/`duration` are **timeline** seconds; the agent gets them from `captions.json`, never by
arithmetic on source time. The plan is written for the *whole* video before anything renders.

**4.5 Scripts**
- `workflows/validate-plan.py`: schema per preset, `x-real` placeholder refusal, asset files
  exist, no overlap on the same placement, presence ≥ `numbers.graphics.min_presence` (0.6 for
  basic tier — Jason's output is well under 85 %; the 85 % rule moves to the premium tier),
  no gap without a graphic or caption change > `numbers.pacing.max_static_s` (2.0), repeats
  rule, every `cutaway` has a mute window.
- `workflows/build-graphics.py`: fills templates → `compositions/NN-<preset>-<id>.html`, runs
  `npx hyperframes lint` and `check`, renders each to `renders/<id>.mov` (`--format mov`,
  sequence fps, no `--resolution`), **always to a new filename when re-rendering**
  (`<id>-r2.mov`) and records the file mtime in the plan.
- `workflows/graphics-qa.py`: for every graphic, composite frames at `cue+0.3`, `cue+1.0`,
  `cue+duration-0.2` over the spine with `lanes/ffmpeg/frame.py`; fail on: render older than
  plan; alpha channel missing; content bbox intersects the caption band while a caption is
  live; content bbox intersects the face bbox; mean luma of the frame differs > 25 % from the
  neighbouring bare frames; any `rgba(` background in the composition that is not a scrim,
  hairline, glow or wash; any string from `samples/` handles. Writes
  `review/qa-round-N.json` and a contact sheet `review/qa-round-N.png`.
- The **review loop**: `run.sh` runs plan → build → qa; on failure it hands the qa report to
  the agent (or a sub-agent) with the instruction "fix the plan or the params, never the
  preset", re-runs, **max 3 rounds**, then stops and marks the node `blocked` in `RUN.md` with
  the remaining defects listed. Zero objective defects is the exit condition; taste is not.

**Gate**
```bash
for p in presets/graphics/*/; do python workflows/build-graphics.py --preset "$p" --params "$p/example.json" --golden; done \
 && python workflows/validate-plan.py projects/fixture-summer && python workflows/build-graphics.py projects/fixture-summer \
 && python workflows/graphics-qa.py projects/fixture-summer && python lanes/ffmpeg/assemble.py projects/fixture-summer --stage graphics
```

**4.6 Premium tier** — the existing `ig-show` doctrine (frame contracts, 1–3 scenes, persistent
object, motion floor via `motion-density.py`) is preserved as `tier: premium`, selected only by
name in the brief. It reuses the same plan/qa/loop; its "presets" are scene templates added
later. Do not spend Phase 4 on it.

### Phase 5 — Audio: measured, then derived

**Build**
- `workflows/voice-gain.py <job>`: `ffmpeg -af ebur128` on the spine → integrated LUFS and
  true peak; compute gain to `numbers.audio.voice_lufs` (−16 for vertical; Jason uses −17 for
  YouTube) with a limiter ceiling `numbers.audio.peak_dbfs` (−1.5); write `audio/voice-gain.json`.
  The ffmpeg lane applies it with `loudnorm`/`alimiter`; the Premiere lane applies it via
  `adjust_audio_levels` + a limiter effect through `bridge.mjs`.
- `workflows/sfx-plan.py <job>`: reads the *placed* `graphics-plan.json` (post-QA), maps each
  graphic's `sfx` verb through `presets/vertical/default/sfx.json` to a file in `assets/sfx/`,
  one sound per graphic event, none per word, density cap `numbers.audio.max_sfx_per_10s`
  (4). Writes `sfx-plan.json`. Re-run automatically when the graphics plan changes (the
  pipeline invalidation from §2 handles this).
- Music: opt-in only, per BRAND.md ("drops out or stays minimal under the opening claim"). If
  the brief names a track: place from onset, bed at `numbers.audio.music_db` (−18) with the
  hook dropout to −30 for `[0, first_graphic_cue]`, 2 s tail. `assets/sfx/` and the music file
  are the creator's; the pipeline never generates audio silently.
- `lanes/ffmpeg/assemble.py --stage audio`: mixes voice (gained), sfx (at cue), music (ducked
  with `sidechaincompress` against voice).
- `lanes/premiere/place-audio.mjs`: same placements on A3/A4/A5 with `add_audio_keyframes`,
  read back.

**Gate**
```bash
python workflows/voice-gain.py projects/fixture-summer && python workflows/sfx-plan.py projects/fixture-summer \
 && python lanes/ffmpeg/assemble.py projects/fixture-summer --stage audio \
 && ffmpeg -i projects/fixture-summer/preview/spine+graphics+audio.mp4 -af ebur128 -f null - 2>&1 | grep "I:"   # within ±1 LU of target
```

### Phase 6 — Pacing as an audit over data

**Build**
- `workflows/pacing-audit.py <job>`: builds the event log from `cuts.json` (cuts),
  `captions.json` (group changes), `graphics-plan.json` (in/out and row reveals — presets
  declare their internal event times in `params.schema.json` `x-events`), `sfx-plan.json`;
  reports every gap > `numbers.pacing.max_static_s` with the cheapest fix from a fixed menu
  (caption accent → sfx → zoom-punch → graphic). Zoom punches are written into `cuts.json`
  as `{"zoom": {"at": t, "pct": 3, "dur": 1.2}}` on the clip and applied by both lanes
  (ffmpeg `zoompan`/`scale` keyframes; Premiere `add_keyframe` read back with `get_keyframes`).
- Seconds 0–8 are exempt from automatic zoom insertion if the plan marks a `hold` there.

**Gate**
```bash
python workflows/pacing-audit.py projects/fixture-summer --fix && python workflows/pacing-audit.py projects/fixture-summer   # second run reports 0 gaps
```

### Phase 7 — The one-shot run and the regression set

**Build**
- `run.sh <job>` runs Phases 1–6 end to end with no prompts, then `finalize.sh` which:
  ffmpeg lane → `outputs/<job>.final.mp4` (`libx264`, 20 Mbps, `-pix_fmt yuv420p`, AAC 320k,
  1080×1920 @ sequence fps) and a copy in `~/Downloads`; Premiere lane → `export_sequence`
  via `bridge.mjs`, **then `test -f` the output and check its mtime is newer than the run
  start**; on failure, fall back to the ffmpeg render and say so in `RUN.md`. Never report an
  export that is not on disk.
- `workflows/verify-final.py`: duration equals `cuts.stats.kept_s` ± 0.2 s; loudness in
  range; zero silences ≥ 0.45 s; 12 evenly spaced frames extracted to `review/final-sheet.png`
  for the human; `measure.py` on 4 caption hits.
- Regression: `tests/regress.sh` re-runs the fixture and diffs `cuts.json`, `captions.json`,
  `graphics-plan.json` (structure, not cue-by-cue if the agent authored the plan) and every
  preset golden. Run it before any change to `presets/` or `workflows/` is called done.
- Timing budget recorded in `RUN.md`: target < 45 min wall-clock for a 60 s vertical on this
  Mac, of which WhisperX ≤ 6 min and renders ≤ 15 min.

**Gate — this is the definition of done for the rework**
```bash
./run.sh projects/fixture-summer --lane ffmpeg --tier basic && python workflows/verify-final.py projects/fixture-summer && tests/regress.sh
```
and a human review of `review/final-sheet.png` + the mp4 that finds **only taste notes** —
no defect from the objective list in §0 (Goal).

### Phase 8 — The docs diet (do this after Phase 7 passes, not before)

- Rewrite `CLAUDE.md` to ≤ 3,500 words: the eight nodes and their files, the format table,
  a one-line index of skills, the folder map, and the **locks** (one line each, dated,
  pointing at the owning file and an archive anchor). Delete the "stale vs use" table by
  fixing every stale sentence at its home.
- Every `.claude/skills/*/SKILL.md` becomes ≤ 1,200 words: what the node does, which files it
  reads and writes, which script to run, the gate, the three most common failures. All timing
  constants move to `presets/vertical/default/numbers.json`; all "this used to say" prose
  moves to `docs/lab-notes-archive.md` with an anchor; skills link to the anchor, never repeat
  the story.
- Move `ig-show/reference/*.md` to `docs/style/` as the premium-tier reference; `ig-show`
  points at `presets/graphics/` for basic and `docs/style/` for premium.
- Fold `ig-hook` into the graphics plan: the hook is `graphics[0..n]` with `cue < 8` plus a
  `hook` block in `graphics-plan.json` (`{"mode": "receipt|comparison|demonstration|roleplay|
  interface|pattern|phrase", "evidence": [...], "frame_zero": "g01"}`) validated by
  `validate-plan.py`. Keep the mode list and the "no topic label at frame zero" rule; drop the
  12-point score, three storyboard strips and sandbox sequences from the default path (they
  stay available as `--hook-lab` for Trial Reels). Retire `HOOK-ENGINE.md` into
  `docs/style/hooks.md`.
- Write `LANES.md` as the step × lane matrix with the real status of every cell after Phase 7
  (`ffmpeg` should be all ✅; `premiere` cells are ✅ only where the read-back verify passed on
  this Mac, ⚠️ elsewhere; `export_frame` cells are ⛔ with the fallback named).
- `workflows/check-links.py` over every `.md`; zero broken links is a gate.
- A fresh session for a job must open ≤ 15 documents (CLAUDE.md, LANES.md, the preset README
  + numbers, the node's skill, RUN.md, and the schemas). Count it.

**Gate**
```bash
python workflows/check-links.py && wc -w CLAUDE.md .claude/skills/*/SKILL.md   # CLAUDE ≤3500, each skill ≤1200
```

### Phase 9 — The vertical preset and the feedback loop (the differentiator)

- `presets/vertical/default/` is where this repo beats the reference: Jason has no 9:16
  preset. Tune it against Faiz's own reels and BRAND.md: caption band 920–1130, hook as
  receipt/action at frame zero, music minimal under the opening claim, one tactile SFX per
  visual event, `feezkera` in every mockup.
- Decide and record in `captions.md` the open question: the spec says ALL CAPS Europa/Anton;
  Faiz's own reel used lowercase IG-native captions. One or the other, then `build-captions.py`
  obeys `numbers.captions.case`.
- `workflows/ledger.py <job> --add-result views=… reach=… retention_3s=…`: appends the
  published result to `docs/ledger.jsonl` with the hook mode, frame-zero preset and first
  spoken line, so the next brief can read what held past 3 s. Below ~300 reached accounts
  record `insufficient-signal`.

---

## 4. Anti-patterns — the implementing agent must not

- Add a timing constant, an easing, or a tool-call sequence to a skill or CLAUDE.md. Numbers
  go in `numbers.json`; motion goes in a preset; calls go in a lane script.
- Author a new composition by hand for a job. If no preset fits, add a preset (with schema,
  example, golden) and *then* use it.
- Lower a gate threshold to make a run pass. Fix the plan, the params, or the preset.
- Trust `success: true` from any Premiere tool. Read back (`get_clip_properties`,
  `get_keyframes`, `list_sequence_tracks`), `test -f`, check mtimes.
- Re-render to a filename Premiere has open. New filename every time.
- Put the plan in chat. Plans are files in the job folder; chat is for the review notes that
  then edit the files.
- Copy a handle, name or avatar from `samples/`. `creator.handle` only.
- Invent a metric, a screenshot, or a comparison from duplicate assets. Work the acquisition
  ladder (on disk → footage → real UI capture → lookup → generate texture → ask) and, if the
  real thing is not obtainable, choose a preset that needs none.
- Reintroduce caption entrance animation, two-line captions, strokes/boxes, or captions in the
  bottom third — all previously rejected by the owner.
- Delete an old document before the new home passes `check-links.py`.

## 5. Open decisions for Faiz (do not block on these; use the default and flag it)

| Decision | Default until answered |
|---|---|
| Caption case | ALL CAPS per current spec; Faiz's reel used lowercase |
| Default delivery lane on this Mac | `ffmpeg` (verifiable); Premiere as replay-for-refinement |
| Music source | none unless the brief names a file; never generated silently |
| Voice target | −16 LUFS integrated, −1.5 dBTP for vertical |
| Raw fixture | the unedited take behind `this summer.mp4` if it exists; otherwise the reel itself |
| WhisperX model | `large-v3` int8 on CPU; `medium.en` if > 6 min for a 60 s source |

## 6. Order of work, one line

Harness → WhisperX → EDL + ffmpeg lane → captions → ten presets + plan/qa/loop → audio →
pacing → one-shot run + regression → docs diet → vertical preset + ledger. Every arrow is a
command that can fail.
