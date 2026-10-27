---
name: ig-cut
description: "Rough cut as data: silence, fillers, false starts, retakes and the slate removed into cuts.json, every edge snapped to the voice, then replayed by the ffmpeg lane (and optionally Premiere). Use for: remove silence, cut the dead air, tighten this, jump cuts, rough cut, remove filler words, cut the ums, build the spine."
---

# ig-cut — node 03

Input `transcript/words.json` (WhisperX; digits are spelled out before alignment by `_wx_spell.py`, because the
aligner cannot time "30%" and shoves every later word early). Output `cuts.json`, the EDL, then `preview/spine.mp4`.

```bash
python workflows/rough-cut.py projects/<job> --review     # prints every removal with an id (and each rule inside a merge)
python workflows/validate-edl.py projects/<job>          # sane EDL + no cut point inside speech
python lanes/ffmpeg/assemble.py projects/<job> --stage spine
python workflows/verify-cut.py projects/<job>            # after transcribe --spine: every kept word heard once
```

## What the rules decide (words) and what the audio decides (edges)

The **words** decide what stays: dead air between words, fillers, immediate repeats, pickups (a phrase re-said
back to back — the sentence is kept whole, the re-said fragment goes), retakes (a take whose opening — or whose
first words re-worded — comes again within the window; the last take stays and a retake range never swallows the
survivor of another line), fragments (one or two words alone between pauses).

The **audio** decides where each clip starts and stops (`_audio.Envelope`): pauses the transcript hid are cut,
and every edge snaps to the measured onset − `lead_s` / offset + `tail_s`. Never trust a word timestamp for an
edge.

The **face** decides the slate: leading or trailing clips where the speaker is not on their mark (no face, or far
from where it sits for the rest of the video — walking to the chair) are dropped. `cut.mark` in `numbers.json`.

All numbers live in `presets/vertical/default/numbers.json` → `cut`.

## Review, don't re-cut

Read the `--review` table. A removal that kills a deliberate pause or a tic gets vetoed by id in
`projects/<job>/cuts.overrides.json` → `{"keep_ids": ["r004"]}`. A judgment no rule can make — an earlier draft
in other words, the speaker talking to the editor ("take the best one you got out of that") — goes in as
`{"remove": [{"in", "out", "why"}]}`. Place those ranges from the current `words.json`, never from memory of an
earlier transcript. Re-run and both are applied deterministically. Never edit `cuts.json` by hand.

## Gates

`validate-edl.py`: monotonic, in range, no slivers, stats exact, **no cut point inside speech**.
Zero silences ≥ 0.45 s in the spine (`run.sh`, `silencedetect`). **No whitespace anywhere**: `check-joins.py` measures
every pause on the spine's audio — a run `cut.pause_rel_db` under the speech level — and fails one at a join over
`cut.join_gap_max_s`, one inside a clip over `cut.pause_gate_s` (holds exempt). The creator's posted reels never drop
that far between words; 9278 failed his ear twice (0.25–0.39 s at every join, then 0.10–0.25 s after "Muse" and 16 more
breaths). The cutter removes them in step 7c: every pause over `cut.pause_max_s` is cut to `tail_s + lead_s` at a word
boundary (or anywhere when longer than `cut.closure_max_s`: shortening the silence of a long closure — "Grok|bot" on 9279 — is inaudible), and a breath or click quieter
than any word (`cut.breath_rel_db`) after the last word or before the first goes with its pause. A word-final "ch" or
"s" is quiet too but sits inside the word — never trim on level alone; `verify-cut.py` is the backstop. A short piece
that resumes the same take within `cut.tuck_max_s` is not a sliver. After a re-cut, `remap-plan.py` moves the graphics
plan (and rough-cut moves punches) by source time — never re-cue by hand. `verify-cut.py`: the spine's own transcript
against the kept words — no missing or doubled run of `cut.coverage_max_run` words. Voice grammar is never
corrected; only time is removed.

**Choosing takes by hand** (a scripted many-take raw): read the transcript as timed phrases, pick the last clean take
of every line, and write the choice as ranges — `{"keep": [{"in","out","why"}]}` and `{"remove": […]}` — never as
`keep_ids` (ids renumber when a word moves). Remove asides to the editor ("this part you're gonna show on screen") and
make them the graphic. A standing take that moves is not a slate: `{"mark": false}`. A take restarted mid-phrase whose
restart WhisperX missed: move the word's timing to the restart in `words.json` and remove the first attempt.

## Premiere

`node lanes/premiere/replay-edl.mjs projects/<job>` places every keep range as its own clip and reads
them back into `premiere/replay-verify.json`. That read-back is the gate, not the tool's flag.
