---
name: ig-sound
description: "Measured voice level, SFX derived from the placed graphics, optional music bed. Use for: add music, sound effects, sfx, duck the music, mix the audio, audio levels, the audio feels flat."
---

# ig-sound — node 06

```bash
python workflows/voice-gain.py projects/<job>   # measure the spine → audio/voice-gain.json (gain to −16 LUFS, limiter at −1.5 dBTP)
python workflows/sfx-plan.py projects/<job>     # placed graphics → sfx-plan.json (one hit per visual event, density-capped)
python lanes/ffmpeg/assemble.py projects/<job> --stage audio
```

Numbers: `presets/vertical/default/numbers.json` → `audio`. Verb → file: `presets/vertical/default/sfx.json`;
the files are the creator's pack in `assets/sfx/` (the preset ships a synthesised default pack).

## Rules that are files, not prose

- Voice wins: measured, never a fixed number. Re-run after any re-replay.
- SFX mark visual events, never words: `sfx-plan.py` reads the graphics as placed; a graphic moved
  later means re-running it (the pipeline invalidates downstream nodes for you).
- Music is opt-in: only when the brief names a track that exists in `projects/<job>/audio/`. Bed at
  −18 dB, −30 dB under the opening until the first graphic lands, 2 s tail. Never generated silently.

## Override

Per graphic, `"sfx": "ding"` (or `""` for none) in `graphics-plan.json` beats the preset's verb.
