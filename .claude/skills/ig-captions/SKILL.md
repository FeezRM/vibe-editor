---
name: ig-captions
description: "Captions from word timestamps: one line, 2–4 words, hard cuts, band y 920–1130, accent on the payload word, muted where a graphic carries its own words. Use for: add captions, subtitles, caption timing, caption style, sync the captions, emphasise a word."
---

# ig-captions — node 04

```bash
python workflows/transcribe.py projects/<job> --spine   # preview/spine.mp4 → transcript/spine-words.json (timeline time)
python workflows/plan-captions.py projects/<job>         # spine words → captions.json (raw words.json + EDL remap only as fallback)
python workflows/build-captions.py projects/<job>        # → compositions/captions.html → renders/captions*.mov
```

`run.sh` runs all three. **Captions come from the cut's own audio, not the raw's.** On a multi-take raw,
WhisperX aligns words to the wrong take, and the remap through the EDL drops or shifts every word near
a cut. On 9077 that dropped "This video" and "and the final result is", so the next caption ran 1 s
early. The creator saw it as "not in sync, some missing". The spine transcript is re-made whenever the
spine is newer. To check sync, transcribe the spine and diff its words against `captions.json`; never
judge sync from the raw transcript.

Groups never overlap (a caption ends where the next begins: hard cuts), and a sentence's last word
stays with its own sentence (no "skill. Then I record").

`captions.json` is the document you edit: `groups[].text / words / accent / hook`. The builder reads
it, applies `caption_mute_windows` from `graphics-plan.json` by **dropping** groups (never opacity —
the glow would draw), and fails if a group does not start within one frame of its first word.

## The look

Everything is in `presets/vertical/default/numbers.json` → `captions` and explained in
`presets/vertical/default/captions.md`: Inter 800 lowercase (local OFL), 78 px, band 920–1130, ≤ 78 %
width, ≤ 5 words, soft glow not stroke, hard cut on/off, accent ≤ 50 % of groups in the italic serif:
white `em` on the payload word, green/gold for a number, red for the bad thing.

## Emphasis

`plan-captions.py` gives a lenient default (numbers → gold, a small bad/good lexicon). You may
improve it in `captions.json` before building: accent the payload word the speaker hits hardest,
leave connective groups white, never three accented groups in a row.

## Verify

`workflows/measure.py <preview/captions.mp4> t1,t2,t3` reports cap height and width at 1080×1920;
`run.sh` prints it. Look at `review/` composites, not at the caption composition alone.

## Never

Slide, fade or scale a caption (rejected twice) · a second line · a stroke or box · the bottom third ·
grammar-correcting the speaker · a caption over a graphic that carries its own words.

## Accents you choose survive re-runs

Put the words in `captions.overrides.json` → `{"accents": {"Muse": "hot", "insane": "hot"}}`; `plan-captions.py`
applies them on every run (never two accented groups in a row). Editing `captions.json` by hand is lost the next time
anything upstream re-runs (9278 lost its accents twice that way).

