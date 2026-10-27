# LANES.md — step × lane

The preset says WHAT, the lane says HOW. Adding an app changes no preset. Every cell points at the
script that does the step; a ⛔ cell is not a blocked step — do it by hand from the preset's numbers
and say so in `RUN.md`.

✅ scripted and verified on this Mac · ✋ manual · ⚠️ scripted, unvalidated here · ⛔ gap

| Step | ffmpeg (default, verification lane) | premiere (refinement lane) |
|---|---|---|
| 02 transcript | ✅ `workflows/transcribe.py` (lane-independent) | ✅ same |
| 03 rough cut | ✅ `lanes/ffmpeg/assemble.py --stage spine` · or adopt the creator's own cut: `lanes/premiere/import-edl.mjs <job> --sequence "<name>"` writes cuts.json from V1 | ✅ `lanes/premiere/replay-edl.mjs` — sequence set to the preset canvas, clips placed one at a time at Premiere's own reported end (a computed 574/30 lands a frame late), A-roll scaled canvas/source, read back with `get_clip_properties` (verified Windows / Premiere 25.3, 2026-09-20) |
| 04 captions | ✅ `renders/captions*.mov` overlaid | ✅ `lanes/premiere/place-layers.mjs` — the caption `.mov` on V2 at 0, `linkAudio:false`, read back |
| 05 graphics | ✅ every `renders/g*.mov` (a composition written for the video, or a kept preset) overlaid at its cue | ✅ `place-layers.mjs [--sequence <name>] [--no-gain]` — each render on V3 at its cue (V4 while V3 is busy); onto `<job>__CUT` or a `duplicate_sequence` of the creator's cut; tracks added and their output forced on; scaled to the sequence (200 % on a 4K sequence), never repositioned |
| 06 audio | ✅ gain + limiter + sfx `adelay` + optional music bed | ⚠️ `place-layers.mjs` applies `audio/voice-gain.json` with `adjust_audio_levels` on every A1 clip (no limiter, no SFX/music placement yet) |
| 07 pacing | ✅ hand-placed zoom punches from `cuts.json` (`zoompan` on the face, one fixed camera) | ⚠️ `add_keyframe` on Scale, read back with `get_keyframes` (script not written yet) |
| 08 export | ✅ `lanes/ffmpeg/assemble.py --stage final` | ⚠️ `lanes/premiere/export.mjs` → `export_sequence`; `finalize.sh` proves the file and falls back |
| stills / QA | ✅ `lanes/ffmpeg/frame.py` only | ⛔ `export_frame` lies (returns success, writes nothing) — use the ffmpeg lane; on Windows, `PrintWindow` of the program monitor is the only pixel check of the sequence itself |

## Universal targets (from `presets/vertical/default/numbers.json`)

- voice −16 LUFS integrated, true peak −1.5 dBFS, ±1 LU tolerance
- caption band y 920–1130, one line, ≤ 78 % width (defaults — a look can change them)

## Environment (verified 2026-09-12)

macOS · Node 26 · ffmpeg 8.0.1 · Python 3.13 (nodes) + `.venv-whisperx` (Python 3.11, whisperx, torch 2.8 CPU) ·
hyperframes 0.8.36 via `npx` · headless Chrome from the puppeteer cache · OpenCV 4.13 (Haar face box) ·
Premiere Pro 2022 installed; MCP server v1.2.0 built in `vendor/adobe-premiere-pro-mcp/dist`.

Timing on a 42 s vertical source (M2 Pro): transcript 49 s · captions render 28 s · 11 graphics 159 s ·
final encode 25 s · whole `./run.sh` ≈ 6 min.
