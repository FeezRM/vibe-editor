---
name: ig-cut
description: "Rough cut: the scripts remove dead air, fillers and obvious repeats and snap every edge to the voice; the editor reads review/takes.md and decides which takes stay, so no mistake survives. Use for: remove silence, cut the dead air, tighten this, jump cuts, rough cut, remove filler words, cut the ums, my mistakes are still in, bad takes, build the spine."
---

# ig-cut — node 03

Input `transcript/words.json` (WhisperX). Output `cuts.json` (the EDL), `review/takes.md`, then `preview/spine.mp4`.

```bash
python workflows/rough-cut.py projects/<job> --review     # every removal with an id and its reason
python workflows/validate-edl.py projects/<job>          # sane EDL + no cut point inside speech
python lanes/ffmpeg/assemble.py projects/<job> --stage spine
```

## What the script does (mechanical)

Dead air between words, fillers, immediate repeats, pickups (a phrase re-said back to back), retakes that open with
the same words (the last take stays), one-or-two-word fragments between pauses, and the walk-on/walk-off slate (face
off its mark). Every edge snaps to the measured voice onset/offset, never to a word timestamp. Numbers:
`numbers.json` → `cut`.

## Choosing the takes (the editor — never skip)

The script cannot tell a mistake from a line. `review/takes.md` is the whole raw, line by line, every cut word in
[brackets]. Read all of it as the viewer will hear it and ask of every kept line:

- Is this the best complete take? Was the same idea said again later, better or in other words? Keep one.
- Did the speaker stumble, mispronounce, trail off, restart mid-sentence, or correct a word? Cut back to the clean
  attempt.
- Is it talking to someone off camera, a slate, a "wait let me redo that"? Cut it.
- Does every sentence still make sense with its neighbours after the cut?

Write the decisions in `projects/<job>/cuts.overrides.json` — ranges from the current `words.json`, never from memory:

```json
{"remove": [{"in": 41.20, "out": 47.85, "why": "first try at the hook, re-said at 52 s"}],
 "keep":   [{"in": 12.10, "out": 14.02, "why": "deliberate pause before the reveal"}],
 "holds":  [{"at": 30.5, "s": 0.6, "why": "beat before the punchline"}],
 "mark": false}
```

(`keep` protects a range from every rule; `holds` freeze a keep's last frame; `"mark": false` when the speaker moves
on purpose.) Re-run, then **listen** to `preview/spine.mp4` (`/watch`) at every join. A word clipped at an edge,
a breath left in, a sentence that no longer follows — fix it and re-run. Never edit `cuts.json` by hand; it is
regenerated.

## Gates

`validate-edl.py` (monotonic, in range, no cut inside speech) · zero silences ≥ `audio.silence_max_s` in the spine
(`run.sh`) · `check-joins.py` (no pause over `cut.join_gap_max_s` at a join, `cut.pause_gate_s` inside a clip) ·
`verify-cut.py` after the spine transcript (every kept word heard once). These catch mechanical slips; they cannot
tell you the takes are right — only reading and listening can.

## Premiere

`node lanes/premiere/replay-edl.mjs projects/<job>` places every keep range as its own clip and reads them back into
`premiere/replay-verify.json`. That read-back is the gate, not the tool's flag.
