---
name: ig-sound
description: "Measured voice level, SFX derived from the placed graphics, optional music bed. Use for: add music, sound effects, sfx, duck the music, mix the audio, audio levels, the audio feels flat."
---

# ig-sound — node 06

```bash
python workflows/voice-gain.py projects/<job>   # measure the spine → audio/voice-gain.json (gain to −16 LUFS, limiter at −1.5 dBTP)
python workflows/sfx-plan.py projects/<job>     # graphics-plan sfx → sfx-plan.json (density-capped)
python lanes/ffmpeg/assemble.py projects/<job> --stage audio
```

Numbers: `presets/vertical/default/numbers.json` → `audio`. Verb → file: `presets/vertical/default/sfx.json`;
the files are the creator's pack in `assets/sfx/`. `presets/vertical/default/sfx/` holds only a README
today, so `sfx-plan` resolves 0 hits and the reel ships silent under its graphics (9077, 2026-09-28).
Check `sfx-plan: N hits` in the run output; with 0 and a plan that asked for sound, tell the creator. Supplying or
generating the pack is theirs to approve. Use sound the way the samples do (`samples/STYLE.md` → sound).

## Rules that are files, not prose

- Voice wins: measured, never a fixed number. Re-run after any re-replay.
- SFX mark visual events, never words: a graphic's `sfx` (entrance) and `sfx_events` (one per `reveal_at`) in
  `graphics-plan.json`; the four kept presets have a default verb. A graphic moved later means re-running it.
- Music is opt-in: only when the brief names a track that exists in `projects/<job>/audio/`. Bed at
  −18 dB, −30 dB under the opening until the first graphic lands, 2 s tail. Never generated silently.

## Override

Per graphic, `"sfx": "ding"` (or `""` for none) in `graphics-plan.json` beats a preset's default verb.
