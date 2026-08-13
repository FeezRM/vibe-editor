---
name: ig-sound
description: "Handles background music and sound effects — steps 3 and 5 of the 6-step editing SOP, merged into one skill because they are one mix sharing the same tracks and the same Premiere audio tools. Chooses and places a music bed, ducks it under voice, drops it out under the hook line, and adds SFX as auditory bullet points tied one-for-one to on-screen graphic events, then drives Adobe Premiere Pro over MCP to build the mix on the timeline. Use this skill whenever the user wants to: add music, score a reel, add sound effects, design the sound, fix a flat-sounding edit, or mix audio levels. Triggers: add music, background music, add sfx, sound effects, sound design, duck the music, mix the audio, audio levels, add a riser, whoosh, music bed, the audio feels flat."
---

# IG Sound — Music + SFX Mix

Build the audio mix for a short-form edit: a ducked music bed plus SFX that mark graphic events. Steps 3 and 5 of the 6-step SOP, one skill because they fight over the same faders and the same tracks — do them together or you'll re-duck the music every time a new SFX lands.

This does not touch A-roll cuts (`ig-cut`), captions (`ig-captions`), or build the graphics SFX are cued to (`ig-show`). It picks up after those layers exist and adds sound on top of them.

> The rule, in one line: **voice always wins the mix, and an SFX only fires when something happens on screen.**

---

## Brand overrides — read these before anything else

This repo ships defaults. **Whoever cloned it may have replaced them.**

| Read | Holds |
|---|---|
| `brand/BRAND.md` | free-text house rules — voice, subject matter, banned visuals, CTA, sound |
| `brand/brand.json` | values — palette, fonts, canvas, fps, density, export |

**Precedence, lowest to highest:**
repo defaults (this file) → `brand/` → the project's own `tokens.css` / `MOTION-PLAN.md`
→ what the user says in this conversation.

Where `brand/` contradicts a default below, **`brand/` wins** — and say so out loud rather
than silently following the default. If neither file exists, use the defaults here.

Values in `brand.json` are already compiled into `brand/tokens.css`; regenerate with
`node scripts/brand.mjs build` after editing. Never hand-edit `brand/tokens.css`.

---

## The One Rule

Everything below is downstream of two constraints:

1. **Voice wins.** Music sits under dialogue at all times. If the viewer has to strain to hear the voice, the music is too loud — full stop, no exception for a good drop.
2. **SFX mark visual events, not words.** An SFX plays because a graphic landed, a cut happened, or a reveal occurred. If nothing happened on screen at that timecode, nothing should happen in the ears. This is the difference between sound design and noise — spam SFX and the mix reads amateur no matter how good each individual sound is.

As the source SOP puts it: BG music "makes the video more entertaining... just make sure you don't make the music too loud to the point they can't hear you." SFX "make the video more engaging... the strat is not to just spam em around, you want to use them where they apply."

---

## Music: Choosing, Placing, Ducking

**Choosing.** One track for the whole edit unless there's a hard tonal break (e.g. a full-screen insert flips mood). Match the house energy — low, moody, cinematic/lo-fi — not a pop hook that competes with the voice for attention. Source a real file (licensed library, the `media-use` skill for generation) — Premiere does not generate music. Write it to `projects/<slug>/assets/` and `import_media` it onto **A5**.

**Placing.** Lay the music as one continuous clip (or a small number of pre-trimmed sections) under the full A-roll spine. Trim the head so the beat lands near the hook, not mid-phrase.

**Ducking.** Music sits ~**-18dB** under voice for the whole runtime by default — this is the baseline, not a special case. Use `add_audio_keyframes` on the music clip's volume to ride it: a keyframe just before dialogue starts, a lower-volume keyframe under it, and a keyframe back up whenever there's a dialogue-free beat (B-roll insert, pause with SFX doing the work). Confirm the shape by reading the clip's levels back — don't fire the keyframes and assume they landed.

**The hook dropout.** Under the hook line (0-3s), pull the music to silent or near-silent (**-30dB or lower**, not just "quieter") — then bring it back to the -18dB bed on the first beat *after* the hook lands. That silence-then-return is the single highest-leverage move in this whole skill: it's a contrast cut the ear registers as a lift, and it costs one pair of keyframes.

Note on this technique: ducking automation could not be confirmed by direct observation of a real project (the source project had a visible music file but no visible rubber-band automation in the captured frames). Treat the -18dB figure and the hook-dropout move as the correct technique to apply, not as something copied off an observed timeline — verify the actual mix by ear/meter on this project, not by matching a reference.

**Sequence, one music cue:**

1. `import_media` the chosen track onto A5.
2. `adjust_audio_levels` to set the baseline bed level (roughly -18dB relative to the voice clip's level — read the voice level first, don't guess).
3. `add_audio_keyframes`: keyframe to near-silent at the hook's start, hold, keyframe back up to the -18dB bed on the first beat after the hook.
4. `add_audio_keyframes` again at any other dialogue-free beat that deserves a lift (a B-roll insert, a pause with SFX carrying it).
5. `export_frame`/scrub playback to confirm by ear that voice is never buried.

---

## SFX: The Verb → Sound Map

One SFX per graphic event. Never one per word, never stacked (no double-riser, no riser + whoosh on the same beat unless two distinct things are actually happening). Pull from a real, specific library — not generic stock "whoosh_01.wav" — the same way a real edit does: named sounds chosen for what they mean, not filler.

| Graphic verb (from `ig-show`) | SFX |
|---|---|
| Riser building into the hook | Sci-fi Riser |
| Chip / stamp / stat card landing | low click or pop |
| Wipe or transition between beats | soft filtered whoosh |
| Proof panel / screenshot reveal | Clean Shutter |
| Counter or ticking value under a number | Fast Clock Ticking (as a bed, not a one-shot) |
| Redaction / censored word or blur | Censor |
| A myth or claim getting killed on screen | Wrong Answer |
| A "good"/confirm beat (checkmark, positive stat) | Bell Ding or Big Bell |
| A weighty stat or number dropping into place | Metal Weight Slide |

If a graphic event doesn't map cleanly to one of these, don't force a sound onto it — silence is a valid choice and keeps the ones that do land meaningful.

**Sequence, one SFX cue:**

1. Get the graphic's landing timecode from `ig-show`'s cue list (see Handoff below) — don't eyeball it off the preview.
2. `set_playhead_position` at that exact frame to confirm what's actually on screen at that moment.
3. `import_media` the chosen SFX file onto A3 or A4 (whichever track is free at that frame — check with `list_sequence_tracks`).
4. `adjust_audio_levels` so the SFX reads clearly over the ducked music bed but doesn't spike over voice.
5. `add_marker` at the cue point so the mix stays auditable later without re-deriving every timecode.

**Density check:** count SFX per 10 seconds before calling the pass done. If it's firing more than once every 2-3 seconds outside of a dense graphic-heavy beat, something is being marked that isn't a real visual event — cut it back.

---

## Track Convention (this skill's tracks)

Matches the observed 6-audio-track project: two dialogue lanes, two SFX lanes, two sparse/music lanes. Create with `add_track`, confirm with `list_sequence_tracks` — never assume an index exists before placing a clip on it.

| Track | Content |
|---|---|
| A1 | Voice (primary) |
| A2 | Voice (alt take / second mic) |
| A3 | SFX — dense, timed to beats |
| A4 | SFX — dense, timed to beats |
| A5 | Music bed |
| A6 | Ambience / spare SFX (sparse) |

Two SFX firing at the same timeline frame each need their own track (A3 vs A4) — a shared track means the second placement overwrites the first.

---

## Task → Premiere Tool

| Task | Tool |
|---|---|
| Confirm bridge is alive before touching anything | `verify_premiere_connection` |
| Bring in a music file or SFX asset | `import_media` |
| Create A5/A6/A3/A4 if missing | `add_track` |
| Confirm track layout before placing | `list_sequence_tracks` |
| Set base music/SFX level | `adjust_audio_levels` |
| Compression, EQ, or filtering on voice/SFX | `apply_audio_effect` |
| Duck music under voice, hook dropout, fade back in | `add_audio_keyframes` |
| Mark the exact cue timecode for an SFX-to-graphic sync | `add_marker`, `set_playhead_position` |

---

## Banned

- Airhorns, cartoon boings, any joke SFX out of tone with the house look.
- Three stacked risers on one hook — pick one.
- An SFX on every word, or on words at all — SFX track visual events only.
- Music loud enough that the voice needs straining for, at any point.
- Copy-pasting the same SFX for every graphic regardless of what the graphic is doing (see the verb map above).

---

## QA Checklist

- [ ] Music sits ~-18dB under voice everywhere it plays — checked by ear, not assumed from the keyframe count.
- [ ] Music drops to near-silent under the hook line and returns on the first beat after.
- [ ] Every SFX corresponds to a real, currently-visible graphic event — none placed on bare dialogue.
- [ ] No two SFX stacked on the same beat unless two distinct things happened on screen.
- [ ] SFX pulled from the named palette (or a deliberate equivalent), not generic stock filler.
- [ ] A3-A6 tracks confirmed with `list_sequence_tracks` before placing, not assumed.
- [ ] Voice is audible and clear at every timecode in the edit, no exceptions.

---

## Handoff

SFX cue timecodes come from the **same** timecodes `ig-show` uses to place its graphics — a Bell Ding lands on the exact frame the chip appears, a Clean Shutter on the exact frame the proof panel reveals. Pull the cue list from `ig-show`'s output rather than re-deriving timecodes independently; drift between the graphic's landing frame and its SFX is audible even at a few frames off.
