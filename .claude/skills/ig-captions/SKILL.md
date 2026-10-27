---
name: ig-captions
description: "Captions from word timestamps on the cut's own audio: grouping, timing, the look (matched to the samples), accents the editor picks, muted where a graphic carries its own words. Use for: add captions, subtitles, caption timing, caption style, sync the captions, emphasise a word."
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

The default is in `presets/vertical/default/numbers.json` → `captions` (see `captions.md`); a look under
`presets/vertical/<name>/` overrides it. Match the samples (`samples/STYLE.md` → captions): if they differ from the
default, make or pick a look rather than living with the default.

## Emphasis

No word is accented by default. Emphasis goes in `captions.overrides.json` (it survives re-runs; hand edits to
`captions.json` are lost when anything upstream re-runs):

- `{"keywords": {"profile picture": "cyan"}}` — every caption group that says the phrase is set whole in the accent
  face (caps italic in the `samples` look) in that colour. This is how the samples emphasise: the hook words, the
  feature name, the CTA word. Classes: `ink`, `bad`, `good`, `hot`, `cyan`, `magenta`, `em`.
- `{"accents": {"not": "bad"}}` — one word inside an otherwise plain line ("does NOT").

Look options a look's `numbers.json` can set: `case: natural` (lowercase, names keep their capitals), `strip_punct`
(characters dropped from captions, e.g. `".,"`), `accent_case` (`uppercase` for the accent face).

## Verify

`workflows/measure.py <preview/captions.mp4> t1,t2,t3` reports cap height and width at 1080×1920;
`run.sh` prints it. Look at `review/` composites, not at the caption composition alone.
