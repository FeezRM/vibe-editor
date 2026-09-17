# LANES.md — step × lane

The preset says WHAT, the lane says HOW. Adding an app changes no preset. Every cell points at the
script that does the step; a ⛔ cell is not a blocked step — do it by hand from the preset's numbers
and say so in `RUN.md`.

✅ scripted and verified on this Mac · ✋ manual · ⚠️ scripted, unvalidated here · ⛔ gap

| Step | ffmpeg (default, verification lane) | premiere (refinement lane) |
|---|---|---|
| 02 transcript | ✅ `workflows/transcribe.py` (lane-independent) | ✅ same |
| 03 rough cut | ✅ `lanes/ffmpeg/assemble.py --stage spine` | ⚠️ `lanes/premiere/replay-edl.mjs` — `add_to_timeline_batch` with source in/out, read back with `get_clip_properties`; bridge was down on this Mac (Premiere 2022, no CEP panel started) |
| 04 captions | ✅ `renders/captions*.mov` overlaid | ✋ import the same `.mov` on the caption track (`import_media` + `add_to_timeline`, `linkAudio:false`) |
| 05 graphics | ✅ every `renders/g*.mov` overlaid at its cue | ✋ import each render on V3 at `graphics-plan.json` cue; never scale or reposition in Premiere |
| 06 audio | ✅ gain + limiter + sfx `adelay` + optional music bed | ⚠️ `adjust_audio_levels` + `add_audio_keyframes` from `audio/voice-gain.json` and `sfx-plan.json` (script not written yet) |
| 07 pacing | ✅ zoom punches from `cuts.json` (`scale` eval=frame + `crop`) | ⚠️ `add_keyframe` on Scale, read back with `get_keyframes` (script not written yet) |
| 08 export | ✅ `lanes/ffmpeg/assemble.py --stage final` | ⚠️ `lanes/premiere/export.mjs` → `export_sequence`; `finalize.sh` proves the file and falls back |
| stills / QA | ✅ `lanes/ffmpeg/frame.py` only | ⛔ `export_frame` lies (returns success, writes nothing) — use the ffmpeg lane |

## Universal targets (from `presets/vertical/default/numbers.json`)

- voice −16 LUFS integrated, true peak −1.5 dBFS, ±1 LU tolerance
- caption band y 920–1130, one line, ≤ 4 words, ≤ 78 % width
- graphic entrance 0.28–0.42 s, hold ≥ 0.8 s, no exits
- nothing static > 2.0 s; zoom punch 3 % over 1.2 s

## Environment (verified 2026-09-12)

macOS · Node 26 · ffmpeg 8.0.1 · Python 3.13 (nodes) + `.venv-whisperx` (Python 3.11, whisperx, torch 2.8 CPU) ·
hyperframes 0.8.36 via `npx` · headless Chrome from the puppeteer cache · OpenCV 4.13 (Haar face box) ·
Premiere Pro 2022 installed; MCP server v1.2.0 built in `vendor/adobe-premiere-pro-mcp/dist`.

Timing on a 42 s vertical source (M2 Pro): transcript 49 s · captions render 28 s · 11 graphics 159 s ·
final encode 25 s · whole `./run.sh` ≈ 6 min.
