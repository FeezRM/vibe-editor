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
                         words.json       (the EDL)       alpha .mov     compositions   from graphics  hand-placed   + contact sheet
```

The scripts do the mechanical work — transcription, silence and edge cutting, caption timing, loudness, rendering,
export — and every one reads a file and writes a file. The **editing decisions** are the agent's: which takes stay,
what (if anything) goes on screen, where, how it moves, where a zoom lands. It makes them against a set of reference
reels you choose (`samples/`), studied into `samples/STYLE.md`, and checks its work by watching the result.

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

Run alone, `./run.sh` gives a clean cut with captions and no graphics. With the agent (the `ig-reel` skill) it
stops after the rough cut to choose the takes from `review/takes.md`, and after captions to plan and write the
graphics for this video, then finishes the run.

Timing on a 42 s vertical source (M2 Pro, models cached): about six minutes end to end.

## What you get

- **A rough cut as data.** `cuts.json` lists every kept range and every removal with a reason; `review/takes.md`
  shows the whole raw with every cut word bracketed, so the takes are chosen by reading, not by a rule.
- **Word-accurate captions** from WhisperX forced alignment on the cut's own audio: hard cuts, one line.
- **Graphics written for each video.** HyperFrames compositions the agent authors per beat, rendered to alpha
  `.mov`. Four neutral presets (`app-mock`, `receipt`, `thumb-wall`, `comment`) are there to reuse when they fit.
- **Measured audio.** Voice to −16 LUFS by measurement, SFX where the plan asks for them, music only when you
  name a track.
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
- `samples/` — the reels the edit should look like; `samples/STYLE.md` is what the agent learned from them.
- `presets/vertical/default/numbers.json` — caption geometry, cut thresholds, loudness, export.
- `presets/vertical/default/transcript-corrections.json` — your product names and how they are spelled.
- `presets/vertical/default/sfx/` — drop in your own pack (same file names).
`tests/regress.sh` re-renders the kept presets against their goldens and re-derives a fixture's EDL and caption
grouping.

## Layout

```
run.sh · finalize.sh          the one-shot entry and the export
workflows/                    the nodes and gates (Python, argument-driven)
lanes/ffmpeg/  lanes/premiere/ how each app replays the same files
presets/vertical/default/     numbers.json, captions.md, sfx, fonts
presets/graphics/<name>/      four reusable presets
samples/                      your reference reels + STYLE.md (what good looks like)
.claude/skills/               one short skill per node — maps that point at the scripts above
docs/lab-notes-archive.md     the technical war stories behind the locks
projects/<job>/               gitignored: RUN.md + every intermediate file of a job
```

`CLAUDE.md` is the agent's map.

## Requirements

macOS (tested) or Windows · Node 22+ · Python 3.11 (for WhisperX) and 3.13 (nodes) with `opencv-python`,
`numpy`, `jinja2` · ffmpeg 6+ · `uv` · `jq` · Adobe Premiere Pro 2020+ (optional).

## Built on

[WhisperX](https://github.com/m-bain/whisperX) · [HyperFrames](https://github.com/heygen-com/hyperframes) ·
[Adobe Premiere Pro MCP](https://github.com/hetpatel-11/adobe_premiere_pro_mcp) · [Claude Video](https://github.com/bradautomates/claude-video) · GSAP · ffmpeg · OpenCV
