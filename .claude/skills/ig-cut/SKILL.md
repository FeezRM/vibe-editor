---
name: ig-cut
description: "Builds the rough cut / spine of a short-form edit by removing whitespace (dead air) and filler words from raw footage on the Adobe Premiere Pro timeline over MCP — the first of six editing steps, owning silence removal and jump cuts only, before any captions, graphics, music, or SFX get added. Use when the user has raw talking-head footage that needs tightening into a fast-flowing spine before the rest of the edit happens. Triggers: remove silence, cut the dead air, silence removal, tighten this, jump cuts, rough cut, cut down raw footage, remove filler words, cut the ums, make this flow faster, build the spine."
---

# IG Cut — Step 1: Whitespace & Filler Removal

Raw footage in, tight spine out. This skill owns **the cut, nothing else** — no captions, no B-roll, no graphics, no music, no SFX. Those are later steps (`ig-captions`, `ig-show`, `ig-sound`, `ig-pacing`). If it's not "should this frame exist," it's not this skill's job.

> North star: raw footage is **~40% air**. Cut it. Short-form lives or dies on pace — the frame should never sit still longer than it has to.

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

**Cut ON the breath, not after it.** The inhale before a word is the tell that a new thought is starting — leaving it in reads as a beat of hesitation, cutting through it reads as intent. Find the breath in the waveform or the word-timestamp gap, and place the razor at its leading edge, not after the exhale finishes. This is the single detail that separates a jump cut that feels *snappy* from one that feels *choppy*.

---

## The Workflow: Transcribe → Mark → Cut → Verify

1. **Transcribe first.** Premiere's MCP has no transcription tool. Run `npx hyperframes transcribe <file>` or a Whisper pass to get **word-level timestamps** — this is what makes filler removal surgical instead of guesswork. Without timestamps you're razoring by ear and eyeballing waveforms; with them you know the exact in/out frame of every "um."
2. **Mark the cut list before touching the timeline.** Walk the transcript and flag every removal candidate:
   - Dead air: silence/pause gaps with no speech.
   - Filler words: um, uh, like, you know, so, basically, I mean.
   - False starts and repeated words ("I think— I think what we—").
   - Lip-smacks and audible breaths sitting directly before a line.
   List each as a timecode range. This is the cut list — cheap to edit here, expensive to edit on the timeline. Example rows:
   ```
   CUT LIST — <source file>
   00:03.2–00:04.6  dead air (pause between thoughts)
   00:11.0–00:11.4  filler "um"
   00:22.8–00:23.5  false start ("we should— we need to")
   00:37.1–00:37.6  breath before line
   ```
3. **Cut.** Execute the cut list on the live Premiere timeline (tools below), in timecode order, oldest-to-newest so downstream positions don't shift under you mid-pass. Work in small batches, verify as you go.
4. **Verify.** Play back / `export_frame` spot-checks to confirm the spine flows with no visible dead air and no audio drift.

For a short talking-head take (under ~2 min raw), it's fine to mark the full cut list up front and execute it in one pass. For a long raw dump (10+ min, multiple takes), work in ~1-minute source windows — mark, cut, verify each window — so a mid-pass mistake doesn't compound across the whole file.

---

## What Stays, What Goes

| Cut it | Keep it |
|---|---|
| Silence / dead air between thoughts | The speaker's actual phrasing |
| um, uh, like, you know, so, basically, I mean | Slang, double negatives, verbal tics that are *voice*, not filler |
| False starts, repeated words | Intentional repetition for emphasis |
| Breath/lip-smack directly before a line | Natural breath mid-sentence that doesn't break flow |

**Do not clean up the speaker's actual voice.** You are cutting dead air and filler, not editing them into a different person. If a phrase is grammatically rough but is genuinely what they said and how they'd say it, it stays. This skill removes silence — it does not rewrite anyone.

---

## Target Density (observed baseline)

From a real 40s short's A-roll track: **~3 second average clip length**, roughly **4–5 segments per 15 seconds**. Use this as the pace floor, not a hard formula — a beat that genuinely needs 5s to land shouldn't be hacked shorter, but if most clips are running 6–8s+, the cut isn't tight enough yet. Nothing sits still.

---

## Blueprint row → Premiere tool

| Step | Tools |
|---|---|
| Confirm bridge is alive | `verify_premiere_connection` (always first) |
| Find natural cut points in a long take | `detect_scene_edits` |
| Talking head + separate mic (unlinked A/V) | `link_audio_video` **before** any cutting |
| Place the razor | `razor_timeline_at_time`, `split_clip` |
| Remove the dead segment | `remove_from_timeline` |
| Frame-accurate trim | `trim_clip`, `set_clip_properties` |
| Close gaps / reflow downstream clips | `move_clip` |
| Read back where a clip actually landed | `get_clip_properties`, `get_clip_at_position` |

---

## Common Mistakes

- **Cutting after the breath instead of on it.** Leaves a micro-beat of dead air at the top of every clip — feels like hundreds of tiny stumbles even though each one is under a second.
- **Trusting the waveform alone.** A quiet "um" or a soft filler word doesn't always show as a visible dip. The transcript's word timestamps catch what the eye misses on the waveform.
- **Over-cutting rhythm out of the delivery.** A short natural pause for emphasis is not the same as dead air — don't strip every gap mechanically. Read the transcript for intent, not just silence.
- **Losing sync on unlinked A/V.** Skipping `link_audio_video` (or the matched-delta workaround) is the single most common way this step silently breaks a video — it won't show until playback or export, by which point many cuts have compounded the drift.
- **Polishing while cutting.** Reaching for a caption, a zoom, or a color tweak mid-pass here means re-timing it later when the spine shifts underneath it. Resist — that's the next skill's job.

## Hard Limits & Gotchas

- **Link audio/video before cutting.** If camera audio and a separate mic are unlinked, `link_audio_video` first so one razor moves both. If they truly can't be linked, razor **both** at the *same* timeline frames and shift both by the *same* delta — otherwise the audio drifts and it's invisible until export.
- **Timecodes are timeline frames, not source frames.** They diverge whenever source fps ≠ sequence fps. Don't compute positions by hand — read them back with `get_clip_properties` after every cut.
- **This edits the live project. There is no dry run and no agent-controlled undo.** Before a destructive pass, state what you're about to do and how many operations it is, and have the user save first — your calls and their Cmd/Ctrl-Z share one history.
- **`verify_premiere_connection` before anything else.** If it fails, the bridge isn't running: Premiere open → project open → *Window → Extensions → MCP Bridge (CEP)* → *Start Bridge*. Don't cut around a dead bridge.
- **Two clips can't share a start frame on one track.** If a removal leaves a gap, close it with `move_clip` rather than leaving a hole or overlapping the next segment.
- **Nothing gets polished before the story flows end to end.** No captions, no color, no B-roll, no zoom pulses here — those all assume a locked spine and will need re-timing if the cut changes underneath them.

---

## QA Checklist (before handoff)

- [ ] Every silence/dead-air gap removed — no beat where nobody's talking?
- [ ] Every filler word (um, uh, like, you know, so, basically, I mean) cut?
- [ ] False starts and repeated words removed?
- [ ] Cuts land ON the breath, not after it?
- [ ] Average clip length in the ballpark of ~3s, no clip dragging past ~6-8s without reason?
- [ ] Speaker's actual phrasing, slang, and voice left untouched — nothing "corrected"?
- [ ] Audio in sync throughout (no drift from unlinked A/V cuts) — spot-check with `get_clip_properties` / playback?
- [ ] Story/argument flows end-to-end with the spine alone, no graphics or captions needed to follow it?

---

## Handoff

Once the spine is locked — silence gone, filler gone, story flows end-to-end — **hand off to `ig-captions`** (step 2). Do not add captions, graphics, music, or SFX in this skill; those own their own steps downstream.
