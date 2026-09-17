<div align="center">

# Vibe Editor

**One prompt, one raw file, one postable vertical reel.**

An agent-driven short-form editor that runs as a pipeline of files, not a conversation with a
timeline. [WhisperX](https://github.com/m-bain/whisperX) cuts, [HyperFrames](https://github.com/heygen-com/hyperframes)
draws, ffmpeg assembles and verifies, and [Adobe Premiere Pro over MCP](https://github.com/hetpatel-11/adobe_premiere_pro_mcp)
gets the same edit as trimmable clips when you want to refine by hand.

![Node](https://img.shields.io/badge/node-22%2B-339933?style=flat-square&logo=node.js&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-tested-000000?style=flat-square&logo=apple&logoColor=white)
![Premiere Pro](https://img.shields.io/badge/Premiere%20Pro-optional-9999FF?style=flat-square&logo=adobepremierepro&logoColor=white)
![License](https://img.shields.io/badge/license-GPL--3.0-blue?style=flat-square)

</div>

---

## How it works

```
raw.mp4 ─▶ 01 intake ─▶ 02 transcript ─▶ 03 rough cut ─▶ 04 captions ─▶ 05 graphics ─▶ 06 audio ─▶ 07 pacing ─▶ 08 export
             RUN.md      WhisperX         cuts.json       captions.json  graphics-plan   LUFS + SFX   zoom punches  final.mp4
                         words.json       (the EDL)       alpha .mov     presets→.mov   from graphics  in the EDL    + contact sheet
```

Every node reads a file and writes a file. Every gate is a script that can fail. The **preset** says
what the edit looks like (`presets/vertical/default/numbers.json` holds every constant); the **lane**
says how an app does it (`lanes/ffmpeg/`, `lanes/premiere/`). The agent's creative work is one JSON
document — the graphics plan — filled with real material and checked in composited pixels before
anything ships.

## Quick start

```bash
git clone https://github.com/FeezRM/vibe-editor.git && cd vibe-editor
./scripts/setup-macos.sh                                   # engines into vendor/, brand scaffold, doctor
uv venv --python 3.11 .venv-whisperx && uv pip install --python .venv-whisperx/bin/python whisperx
node scripts/brand.mjs init                                # your handle, colours, fonts → brand/
```

Then one video:

```bash
python workflows/new-job.py ~/Downloads/take.mp4 --slug my-reel --brief "Edit this end to end. Keep my exact words."
./run.sh projects/my-reel
open projects/my-reel/review/final-sheet.png              # 12 frames of the result
open projects/my-reel/outputs/my-reel.final.mp4           # also copied to ~/Downloads
```

`./run.sh` is unattended: a heuristic drafter writes the graphics plan and a deterministic fixer
converges the QA loop. With an agent in the loop it is better: `./run.sh --to captions`, the agent
authors `graphics-plan.json` from the caption timings and real assets (a captured page, a frame from
the footage, a real number with provenance), then `./run.sh --from graphics`.

Timing on a 42 s vertical source (M2 Pro, models cached): about six minutes end to end.

## What you get

- **A rough cut as data.** `cuts.json` lists every kept range and every removal with a reason. Veto a
  removal by id; the EDL regenerates deterministically. Replayed as separate trimmable clips.
- **Word-accurate captions** from WhisperX forced alignment: one line, 2–4 words, hard cuts, band under
  the chin, accent on the payload word, dropped where a graphic carries its own words.
- **Ten tuned graphic presets** (`presets/graphics/`): phrase, list-card, flow, metric, app-mock,
  receipt, thumb-wall, chat, wash, rec-frame. Each is a HyperFrames composition with a params schema,
  an example, a golden frame, and a README saying when it is right. The plan picks the preset and the
  content; the preset owns the motion.
- **Pixel QA.** Every graphic is composited over the real frame and checked: caption band, face box
  (OpenCV), luma, alpha, staleness. Placeholders, missing assets, metrics without provenance and
  borrowed handles are refused before a render starts.
- **Measured audio.** Voice to −16 LUFS by measurement, one SFX per visual event derived from the
  placed graphics, music only when you name a track.
- **A verified export.** Duration equals the EDL, zero dead air, loudness in range, file on disk and
  newer than the run, or it is not called done.

## Premiere Pro

`./run.sh projects/my-reel --lane premiere` additionally replays the EDL onto a `<job>__CUT` sequence
as trimmable clips and reads every clip back. Start the bridge first: open a project → *Window →
Extensions → MCP Bridge (CEP)* → Temp Directory as printed by the installer → *Start Bridge*. If the
bridge is down the run continues on the ffmpeg lane and says so. `LANES.md` is the honest step × lane
matrix of what is scripted, manual, unvalidated, or a gap.

## Make it yours

- `brand/brand.json` + `brand/BRAND.md` → `node scripts/brand.mjs build` (colours, fonts, handle, voice).
- `presets/vertical/default/numbers.json` — caption geometry, cut thresholds, timing, loudness, export.
- `presets/vertical/default/transcript-corrections.json` — your product names and how they are spelled.
- `presets/vertical/default/sfx/` — drop in your own pack (same file names).
- Add a preset: copy a folder in `presets/graphics/`, write the template + schema + example, render a
  golden with `python workflows/build-graphics.py --preset presets/graphics/<name> --write-golden`.

`tests/regress.sh` re-renders every preset against its golden and re-derives the fixture's EDL and
caption grouping. Run it before calling any change done.

## Layout

```
run.sh · finalize.sh          the one-shot entry and the export
workflows/                    the nodes and gates (Python, argument-driven)
lanes/ffmpeg/  lanes/premiere/ how each app replays the same files
presets/vertical/default/     WHAT: numbers.json, captions.md, creative-moves.md, sfx, fonts
presets/graphics/<name>/      the ten presets
.claude/skills/               one short skill per node — maps that point at the scripts above
docs/style/                   the premium tier: frame contracts, persistent-object scenes, the motion floor
docs/lab-notes-archive.md     every war story behind every lock
projects/<job>/               gitignored: RUN.md + every intermediate file of a job
```

`CLAUDE.md` is the agent's map. `REWORK-PLAN.md` explains why the repo is shaped like this.

## Requirements

macOS (tested) or Windows · Node 22+ · Python 3.11 (for WhisperX) and 3.13 (nodes) with `opencv-python`,
`numpy`, `jinja2` · ffmpeg 6+ · `uv` · `jq` · Adobe Premiere Pro 2020+ (optional).

## Built on

[WhisperX](https://github.com/m-bain/whisperX) · [HyperFrames](https://github.com/heygen-com/hyperframes) ·
[Adobe Premiere Pro MCP](https://github.com/hetpatel-11/adobe_premiere_pro_mcp) · [Claude Video](https://github.com/bradautomates/claude-video) · GSAP · ffmpeg · OpenCV
