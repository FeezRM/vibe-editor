---
name: ig-delivery
description: "Runs the final QA-and-export pass on a Premiere Pro sequence built by the ig-cut/ig-captions/ig-show/ig-sound/ig-pacing chain — validates the project, checklists retention/caption/safe-zone/audio correctness, verifies every graphic cue with a pixel-level frame check, then exports the finished 9:16 file to exports/ and confirms it actually landed on disk. Use this when a cut is otherwise finished and needs to be checked and shipped, not when it's still being built. Triggers: export, render it out, export the reel, ship it, final check, QA, is this ready, validate the sequence, export settings, 9:16 export, deliver."
---

# IG Delivery — QA and Export

The last step in the chain. It does not cut, caption, build graphics, or mix — it verifies what those steps produced and ships it. If this skill finds a problem, the fix belongs to the skill that owns that layer (see the table at the bottom), not here.

> **The one rule: never report an export that didn't happen.** A tool call returning without an error is not proof of a finished file. Only call it exported once `export_sequence` returns successfully **and** the file exists on disk at the expected path. If it fails, say so plainly and hand the user *File → Export → Media* — don't paper over a failed render.

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

## Before anything: `verify_premiere_connection`

Read-only, confirms the bridge is alive and reports the open project + active sequence. This operates on the **live project** — there is no dry run and no undo the agent controls. If it fails, the bridge isn't running; don't try to QA around a dead connection.

Then `get_sequence_settings` to confirm frame size and fps before touching the checklist below.

---

## QA Checklist (the centrepiece — run every item before export)

- [ ] **Hook** — does the first frame + first line stop the scroll? Biggest text, hardest cut, zero dead air?
- [ ] **Silence** — every breath, pause, and filler word gone? No dead air anywhere in the spine?
- [ ] **Pacing** — something changes every **1–2s, measured** off the actual timeline (not the SOP's stated 3–5s — that figure is looser than what holds attention in practice)?
- [ ] **Shot scale** — do adjacent A-roll shots differ in scale (zoom pulse actually alternating, not two same-size cuts back to back)?
- [ ] **Captions** — word-by-word, sitting in the **45–60% vertical band** of the frame (NOT the bottom third — too close to the IG UI), and the speaker's **exact words, uncorrected** (no grammar cleanup, no "fixed" slang)?
- [ ] **Graphics** — does every graphic prove something (a number, a comparison, a result)? None decorative?
- [ ] **Safe zones** — nothing sits in the IG UI zones at 1080×1920: top **240px**, bottom **420px**, sides **90px**?
- [ ] **Music** — ducked under voice throughout, dropped out under the hook line?
- [ ] **SFX** — mark visual events only, not on every word or beat?
- [ ] **Payoff** — held, not resolved early?
- [ ] **CTA** — one clean call to action, nothing louder than the rest of the video?
- [ ] **No UI chrome** — no watermark, no "follow for more" banner, no progress bar baked into the export?
- [ ] **Frames verified** — `export_frame` pulled at the hook, every graphic cue, and the end card, and each one visually confirmed correct?
- [ ] **FPS match** — sequence fps equals the fps every graphic was rendered at?
- [ ] **`validate_project_for_export`** — clean, no offline media, no missing assets?

Any unchecked box is a stop. Route it to the owning skill (bottom table), fix, re-check, then re-run the whole list — a fix in one layer can knock another loose (e.g. a re-cut hook shifts every downstream graphic cue).

---

## Export Settings

| Setting | Value |
|---|---|
| Codec | H.264 |
| Resolution | **1080×1920 — not 4K** |
| Bitrate mode | VBR, 2-pass |
| Target bitrate | ~12 Mbps |
| Audio | AAC, 320kbps |
| Output path | `exports/` |

**Why 1080p and not 4K:** Instagram re-encodes every upload on its own hardware with its own settings. Hand it a 4K master and that re-encode is a lossy downscale happening outside your control. Export at delivery resolution and you keep the control — the platform is doing less work to the file, and what it does do is compression at the resolution it's actually going to serve. This is the SOP's stated rule, not something verified frame-by-frame in this pass, but the reasoning holds and there's no cost to following it.

**FPS**: match the sequence to whatever the graphics were rendered at — this is a build-time decision, not fixable at export. If `get_sequence_settings` and the graphics' render fps disagree, the export will show it as stutter and there is no export setting that undoes that; it has to be fixed upstream by re-rendering the graphic or conforming the sequence, before this pass runs.

---

## Export Sequence

1. `validate_project_for_export` **first** — catches offline media and missing assets before a long render burns time on a doomed export.
2. `export_sequence` with the settings above.
3. Confirm the output file exists on disk at the expected `exports/` path before saying done.

**Handing the cut elsewhere instead of a render:** `export_as_fcp_xml` or `export_aaf` — use when the deliverable is the edit itself (another editor, another app), not a finished video file.

---

## The Pixel-Verification Pass

A tool returning success is not proof a graphic landed on the right frame — timecodes, track order, and alpha handling can all be silently wrong. Run `export_frame` at:

- the hook (0–3s)
- every graphic cue timecode
- the end card

and actually look at each one. This is the only honest check that what the blueprint specified is what's on screen.

---

## Common Export Failures

| Symptom | Cause | Fix |
|---|---|---|
| `validate_project_for_export` flags offline media | Source file moved/renamed/deleted since import | Relink or re-import, then re-validate |
| Overlay stutters or drifts | Sequence fps ≠ graphic render fps | Re-render the graphic at sequence fps (this skill doesn't fix it — belongs upstream) |
| Alpha `.mov` imports opaque / with a black box | Premiere misreads the alpha channel | *Interpret Footage → Alpha Channel: Straight (Unmatted)* |
| Graphic shows as a solid black rectangle | Graphic was rendered without an alpha channel | Re-render with `--format mov` (alpha), not `mp4` |
| Audio drifts out of sync partway through | A/V cut unlinked, razored at different frames | Re-cut both tracks at the same timeline frame, or `link_audio_video` before future cuts |

---

## Task → Premiere Tool

| Task | Tool(s) |
|---|---|
| Confirm bridge/project is live | `verify_premiere_connection` |
| Check sequence fps / frame size | `get_sequence_settings` |
| Pre-export sanity check | `validate_project_for_export` |
| Render the final file | `export_sequence` |
| Hand off the edit instead of a render | `export_as_fcp_xml`, `export_aaf` |
| Confirm a frame's actual pixels | `export_frame` |
| Confirm a track/clip exists before checking it | `list_sequence_tracks`, `get_clip_properties` |

---

## Where Fixes Belong

This skill is the last link in the chain — it consumes the work of `ig-cut` (spine, silence removal), `ig-captions` (word-by-word text, safe-zone placement), `ig-show` (graphics), `ig-sound` (music/SFX mix), and `ig-pacing` (shot scale, cut rhythm). If QA fails:

- Weak hook, static pacing, wrong shot scale → **ig-cut** or **ig-pacing**
- Caption wording, placement, or styling wrong → **ig-captions**
- Graphic missing, wrong, or off-cue → **ig-show** (and re-render before this skill re-runs)
- Music/SFX levels, ducking, or timing wrong → **ig-sound**

Fix it in the owning skill, then come back here and re-run the full checklist — don't spot-check just the one box that failed.
