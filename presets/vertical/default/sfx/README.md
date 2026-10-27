# default SFX pack
Synthesised, tactile, short. They exist so a one-shot run has one real sound per visual event.
Replace any file with your own (same name) — the verb → file map is `../sfx.json`.

`*.wav` is gitignored, so the pack is rebuilt by `./synth.sh` (ffmpeg synthesis, never overwrites a file that
exists — your own `pop.wav` stays). Without it `sfx-plan.py` finds no files and places 0 hits.
