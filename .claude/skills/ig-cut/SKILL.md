---
name: ig-cut
description: "Rough cut as data: silence, fillers and false starts removed from the transcript into cuts.json, replayed by the ffmpeg lane (and optionally Premiere). Use for: remove silence, cut the dead air, tighten this, jump cuts, rough cut, remove filler words, cut the ums, build the spine."
---

# ig-cut — node 03

Input `transcript/words.json` (WhisperX, word onsets accurate to tens of ms). Output `cuts.json`, the
EDL, then `preview/spine.mp4`.

```bash
python workflows/rough-cut.py projects/<job> --review     # prints every removal with an id
python workflows/validate-edl.py projects/<job>
python lanes/ffmpeg/assemble.py projects/<job> --stage spine
```

The numbers live in `presets/vertical/default/numbers.json` → `cut`: `min_gap_s` (dead air ≥ this is
removed), `lead_s` (the breath left before the next word — "cut on the breath" as a number),
`fillers` (removed whole), `keep_tics` (never removed — they are the speaker's voice), `min_clip_s`.

## Review, don't re-cut

Read the `--review` table. A removal that kills a deliberate pause or a tic gets vetoed by id in
`projects/<job>/cuts.overrides.json` → `{"keep_ids": ["r004"]}`; re-run and the veto is applied
deterministically. Never edit `cuts.json` by hand — it is regenerated.

## Gate

`validate-edl.py` (monotonic, in range, no slivers, stats exact) and zero silences ≥ 0.45 s in the
spine (`run.sh` checks with `silencedetect`). Voice grammar is never corrected; only time is removed.

## Premiere

`node lanes/premiere/replay-edl.mjs projects/<job>` places every keep range as its own clip and reads
them back into `premiere/replay-verify.json`. That read-back is the gate, not the tool's flag.
