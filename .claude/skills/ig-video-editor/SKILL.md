---
name: ig-video-editor
description: "Edits short-form video (Instagram Reels, TikTok, YouTube Shorts) into retention-optimized, premium-looking cuts by driving Adobe Premiere Pro over MCP. Built on the 'Dynamic Minimalism + Devin Jatho' editing style and Feez's Content Alchemy / Cave brand: silence-removal jump cuts, slow zoom 'pulses', clean word-by-word captions, cinematic/memetic B-roll, and subtle premium sound design. Works blueprint-first — produces a timestamped, shot-by-shot edit plan the user approves, then executes it on the Premiere Pro timeline via MCP. Use this skill whenever the user wants to: edit a reel or video, cut down raw footage, turn a talking-head recording into a finished reel, add captions, add B-roll, tighten pacing, do silence removal, design sound, restyle an edit, clip a long video into shorts, or get a shot-by-shot edit plan / EDL. Triggers: edit my reel, edit this video, cut this footage, make this a reel, add captions, add b-roll, polish this video, edit my talking head, edit my Cave footage, speed up this edit, clip this long video, edit plan, blueprint this edit, premiere, premiere pro, finish this video."
---

# IG Video Editor — Dynamic Minimalism Method

Turn raw footage into retention-optimized short-form video that looks **premium, not hype-y** — and do it fast. This skill encodes the modern viral editing meta (Dynamic Minimalism + the Devin Jatho style) tuned to Feez's Cave brand, and drives **Adobe Premiere Pro over MCP** to actually build the cut.

The output is not vague advice. It is a **timestamped edit blueprint** (every cut, caption, zoom, B-roll cue, and SFX) that the user approves, then this skill **executes it on the Premiere timeline** via the MCP bridge's tools.

Motion graphics are **not** built here. Anything designed — a counter, a meter, a stat card, kinetic titles, an end card — belongs to the `ig-motion-graphics` skill, which builds it as a HyperFrames composition and renders an alpha `.mov` this skill imports and places. Cue both off the same timecodes.

> North star: every second earns the next second. Target 70%+ watch-through. If a frame isn't holding attention, it gets cut, zoomed, or covered.

---

## Default Mode: Blueprint → Approve → Execute

1. **Ingest** — load the footage, the script (if any), the goal, and the brand context. **Transcribe first** (`npx hyperframes transcribe <file>`, or a Whisper/Scribe pass for accuracy — Premiere's MCP has no transcription tool), then check the transcript actually contains what the chosen format needs: a tier list needs the *rankings*, a listicle needs the *items*, a "3 reasons" needs the *three*. If the footage is just raw takes without that structure (common — e.g. someone naming items but never ranking them), **get the missing pieces from the user before blueprinting** rather than inventing them.
2. **Blueprint** — write the shot-by-shot edit plan (the deliverable below). This is where the craft lives.
3. **Approve** — show the blueprint, take edits. Cheap to change here, expensive to change on the timeline.
4. **Execute** — build it on the Premiere Pro timeline via MCP, pass by pass.
5. **QA** — run the retention checklist, fix, export 9:16.

**Fast mode:** if the user says "just do it" / "fast" / "don't overthink it," collapse to a condensed one-line-per-beat blueprint and go straight to execute. Quality bar stays the same; the approval step shrinks.

---

## The Look: Dynamic Minimalism + Devin Jatho

This is the 2026 meta. It keeps the retention *mechanics* of the old Hormozi style (word-by-word captions, hard cuts, zooms, sound design) but strips the *noise* (neon fonts, flying emojis, cartoon SFX). It reads **premium**, which is exactly Feez's lane — high-ticket, focus-over-flash, "the flex is the work."

| Element | Do | Don't |
|--------|-----|-------|
| **Captions** | Clean sans-serif (SF Pro / Helvetica Now / Inter), white, subtle shadow/soft stroke for legibility, word-by-word or tight phrase pops | Bulky Impact/Komika fonts, neon green/yellow, rainbow keywords |
| **Emphasis** | One restrained move: a **bold weight** or a single brand-accent color on the 1–2 power words per line | Highlighting half the sentence, multiple colors |
| **Motion** | Smooth, intentional — hard cuts on the beat + slow zoom *pulses* | Constant shake, spin transitions, jarring pops |
| **B-roll** | Cinematic or "memetic" footage that illustrates the point | Random stock, literal clip-art, flying emojis |
| **SFX** | Subtle, premium — soft whoosh, low click/pop on key reveals, a riser into the hook | Cartoon boings, airhorns, SFX on every word |
| **Energy** | Something changes every 1–3s (cut / zoom / B-roll / caption hit / SFX) | Static talking head for 8 seconds |

**The Devin Jatho signature:** the frame never sits still — a cut, push-in, graphic, or sound lands every 1–3 seconds — but it stays *clean*. Movement with restraint. Minimal, high quality.

---

## The Retention Mechanics (non-negotiable)

These are the load-bearing techniques. Apply them to every edit regardless of style.

1. **Silence removal = jump cuts.** Cut every breath, "um," and dead beat. Cut *on* the breath, not after it. Raw footage is ~40% air; remove it. This alone is the single biggest retention lever.
2. **The hook frame (0–3s).** Biggest text of the whole video, hardest visual, no dead air, no slow intro. The first frame must make the thumb stop. If the spoken hook is weak, open on the most visual / highest-tension moment and let the line catch up.
3. **The zoom pulse.** Slow push-in on the important line (mimics a human leaning in), then cut wide to reset. Alternate scale so no two adjacent shots are the same size — this manufactures pacing even when the speaker is calm.
4. **Kinetic captions.** Word-by-word or phrase-by-phrase. 85% watch on mute — the captions *are* the video. Dual-coding (hearing + reading the same words) raises comprehension and hold.
5. **Pattern interrupt every 3–5s.** A cut, B-roll insert, caption emphasis, SFX, or angle change. Resets the attention span before it drops.
6. **B-roll covers and illustrates.** Use it to hide jump cuts and to *show* what's being said (a number, a tool, a result). Never decorative.
7. **Sound design as bullet points.** Subtle SFX mark idea transitions; a low music bed (ducked under voice) sets energy. Silence the music under the hook line for impact, then drop it back in.
8. **Hold the payoff.** Retention drops the instant the viewer gets the answer — delay it, then land it. Don't resolve the hook early.

---

## Brand Standards: The Cave (Feez)

Bake these in unless the footage is clearly a different creator/brand.

- **Aesthetic:** dark room, laptop glow, single light source, 1am energy. Deep contrast, slightly cool shadows, controlled highlights. Filmic, not bright/clean-vlog.
- **B-roll that's on-brand:** whiteboard breakdowns, screen recordings (dashboards, analytics, ContentSpy, the editor itself), code, terminal, content-system diagrams. The flex is **focus and the system**, not the spoils.
- **Banned visuals:** gym mirrors, cars, hotels, watches, luxury/lifestyle b-roll. These break the positioning instantly.
- **Caption voice = his voice.** Captions are his spoken words on screen — keep them **lowercase, spoken, blunt**, with his phrasing intact ("mans," double negatives, slang). Do **not** clean up grammar or formalize. If transcription "corrects" him, change it back.
- **Accent color:** default to **white captions with bold-weight emphasis** (most premium). If a single brand accent is used for power words, lock ONE color and use it consistently — never a palette. (Set `[BRAND ACCENT]` once and reuse.)
- **CTA end card:** keep it clean — comment-trigger or DM word in the same caption system, no loud "FOLLOW FOR MORE" banners.

---

## The Edit, in 3 Passes

Build on the timeline in this order. Don't polish before the spine is right.

**Pass 1 — The Spine (rough cut).** Import footage. Pick the best takes. Strip silence and filler into a tight A-roll spine. Lock the hook. Get the story/argument flowing end-to-end with zero dead air. Nothing pretty yet — just tight.

**Pass 2 — The Retention Layer.** Add zoom pulses (vary shot scale beat to beat). Drop B-roll over jump cuts and on every number/tool/result. Add captions (word-by-word, on-brand styling, safe-zone placement). Insert pattern interrupts where attention would sag.

**Pass 3 — The Polish.** Sound design (SFX on key reveals, music bed ducked under voice, music out under the hook). Color/grade consistency for the Cave look. Tighten every transition frame-by-frame. Re-cut the first 3 seconds until the hook is undeniable.

Then **QA → export 9:16**.

---

## The Deliverable: Edit Blueprint

This is the core output. Produce it before touching the timeline (Default Mode). Every row is an executable instruction.

```
EDIT BLUEPRINT — [Title]
Source: [file/clip], Duration in: [Xs] → target out: [Ys]
Goal: [views / leads / sales]   Style: Dynamic Minimalism + Devin Jatho   Ratio: 9:16

HOOK (0–3s)
- A-roll: [take/timestamp from source] | Shot scale: [wide/med/CU]
- Caption: "[exact on-screen words — his voice]" | Emphasis: [power word]
- Motion: [hard in / fast push] | B-roll: [if any] | SFX: [riser / none] | Music: [out under hook]

[BEAT 2 — 3–7s] — label what this beat does (build-up / mind-read / authority)
- A-roll: [timestamp] | Scale: [..] | Caption: "[..]" | Motion: [zoom pulse / cut] | B-roll: [..] | SFX: [..]

[BEAT 3 — value] ...
- (one row per beat; a beat is ~1–4s — something changes every beat)

[PAYOFF] — resolve the hook, held as long as possible
[CTA] — [comment trigger / DM word], clean end card

GLOBAL:
- Captions: [font], white + [emphasis style], safe-zone centered-lower
- Music: [track/vibe], ducked -18dB under voice, out under hook
- Grade: Cave look — deep contrast, cool shadows
- B-roll to source or generate: [screen recordings to capture, prompts for media-use, if any]
- Graphics to build: [one line per HyperFrames composition + its cue timecode]
```

Keep beats short — if a row covers more than ~4 seconds of static A-roll, split it; the frame should change.

---

## Caption Spec

- **Font:** **Tactic Sans — Bold Italic is Feez's default.** Look up the installed PostScript name first (`system_profiler SPFontsDataType | grep -i tactic`); if it isn't installed, fall back to `Helvetica-BoldOblique` (keeps the bold-italic look) and tell Feez to install Tactic Sans, then swap every text clip's `fontName` to the real name in one batch. Other acceptable clean sans fallbacks: SF Pro Display, Helvetica Now, Inter (Bold/Heavy).
- **Color:** white. Emphasis via **bolder weight** or a single `[BRAND ACCENT]` on the 1–2 power words per line only.
- **Legibility:** subtle drop shadow or thin stroke so it survives any background. Never rely on raw text over bright footage.
- **Animation:** word-by-word pop or tight 2–4 word phrase reveals, synced to speech. Smooth, fast, no bounce/spin.
- **Placement & safe zone (hard rule):** keep ALL text and graphic overlays inside the IG safe zone — vertically **centerY ~0.13–0.77** (clear of the top status row and the bottom caption/handle/audio strip), centered horizontally and clear of the **right-side button rail** (avoid centerX > ~0.85). Captions sit lower-middle (~0.62); tier/badge stamps just below (~0.72, never past 0.77). Hook text sits higher (~0.14) but still inside the band.
- **Don't cover the face:** icons, badges, logos and B-roll stickers go ABOVE the head (~centerY 0.22–0.26) or off to a clear side — never parked over the speaker's eyes/mouth. Graphic up top, captions in the lower third, face visible in between.
- **Where captions get built:** two paths, pick one per project and stay on it. **(a) HyperFrames** — a caption composition rendered to alpha `.mov` and imported to V4. Better typography, exact word timing, deterministic. Use it for anything styled. **(b) Premiere natively** — `create_caption_track` for a straight subtitle read, `add_text_overlay` for one-off titles. Faster, plainer, and edited in the app afterwards. Never mix both in one video.
- **Sizing reality:** text is very easy to oversize on a 1080×1920 canvas. Build the caption at its real pixel size in the composition and verify with `hyperframes snapshot` before rendering the set. If you're using Premiere text, place one throwaway clip, `export_frame` it, read the real size, then delete it — there is no live size preview over MCP.
- **Pace match:** caption rhythm follows the cut rhythm — when speech speeds up, captions speed up.
- **Hook text:** oversized, first 3 seconds, the one moment that breaks the minimal rule.

---

## B-roll Spec

- **Purpose-first:** every insert either (a) covers a jump cut or (b) shows the concept (a number, a tool, a result, a place). If it does neither, cut it.
- **On-brand sources:** screen recordings, whiteboard, dashboards/analytics, code, the product. Generated cinematic B-roll for abstract concepts.
- **Sourcing it:** Premiere's MCP imports, it does not generate. Real screen recordings, whiteboard, and dashboard captures are first choice and usually stronger anyway. For abstract concepts, generate through the `media-use` skill (image/video models, background removal, LUTs), write the file to `projects/<slug>/assets/`, then `import_media` it. Match the **Cave grade** in the prompt (dark, moody, filmic, cool shadows) so generated shots cut seamlessly against A-roll. Generation costs credits — batch it, and generate only what the blueprint calls for.
- **Timing:** 0.8–2s per insert, cut on the beat, never lingering past the point it makes.
- **No clip-art / no flying emojis.**

---

## Sound Design Spec

- **Music bed:** low, moody/cinematic/lo-fi at low volume, ducked ~-18dB under voice. Matches Cave energy. Optional subtle build into the payoff.
- **Hook:** drop music out (or near-out) under the hook line for contrast, then bring it in — instant lift.
- **SFX (subtle, premium):** soft whoosh on B-roll transitions, low click/pop on keyword reveals, a light riser into the hook. Auditory bullet points only — not on every word.
- **Voice:** clean, slight compression for presence, audible over the bed at all times. Voice always wins the mix.

---

## Execution in Premiere Pro (over MCP)

The `premiere-pro` MCP server drives a **real, local Premiere Pro** through a CEP bridge panel. There is no sandbox and no undo stack the agent controls — every call lands on the user's open project. Work deliberately.

**Before executing, in this order:**

1. **`verify_premiere_connection`.** Read-only. It returns the Premiere build, the open project, and the active sequence. If it fails, the bridge isn't running — Premiere open → project open → *Window → Extensions → MCP Bridge (CEP)* → Temp Directory matches `PREMIERE_TEMP_DIR` → *Start Bridge*. Don't try to edit around a dead bridge; fix it or hand over the blueprint.
2. **Attach the `premiere://config/get_instructions` resource** before any project-modifying work. It carries the server's own operating guidance and overrides guesses made here.
3. **List the live tool set.** ~283 tools ship, and the catalog moves. Use the names the connected server actually exposes; the ones referenced below are stable but verify rather than assume.
4. **Confirm the sequence.** `get_active_sequence` / `list_sequences`, and `get_sequence_settings` for fps and frame size. **Every graphic must be rendered at the sequence fps** — a mismatch is what makes overlays stutter. `create_sequence` at 1080×1920 if there isn't a vertical one.
5. **Build in the 3-pass order** (spine → retention layer → polish), verifying between passes rather than firing everything blind.

### Blueprint → tools

| Blueprint row | Tools |
|---|---|
| Import footage / assets | `import_media`, `import_folder` |
| Find cuts in a long take | `detect_scene_edits` |
| Silence removal, jump cuts | `razor_timeline_at_time`, `split_clip`, `remove_from_timeline`, `move_clip` |
| Trim to the frame | `trim_clip`, `set_clip_properties` |
| Talking head + separate mic | `link_audio_video` before cutting |
| Zoom pulse / push-in | `add_keyframe` on scale/position, `get_keyframes` to verify |
| Speed ramps, freeze | `speed_change` |
| B-roll and graphic overlays | `import_media`, then place on the overlay track |
| Transitions | `add_transition`, `add_transition_to_clip`, `batch_add_transitions` |
| Look and grade | `color_correct`, `apply_effect` (use the `Black & White` effect for mono — don't fake it with saturation) |
| Captions | `create_caption_track`, `add_text_overlay`, `read_sequence_captions` |
| Sound | `adjust_audio_levels`, `apply_audio_effect`, `add_audio_keyframes` for ducking |
| Beat / cue marking | `add_marker`, `set_playhead_position` |
| Frame check | `export_frame` |
| Export | `validate_project_for_export`, then `export_sequence` (or `export_as_fcp_xml` / `export_aaf` to hand off) |

### Premiere MCP — read before executing

- **It edits the live project. There is no dry run.** Before a destructive pass (razoring, ripple-style removal, replacing clips), say what you're about to do and how many operations it is. If the user has unsaved manual work, have them save first — your calls and their Cmd-Z share one history.
- **Track convention, bottom to top:** `V1` A-roll · `V2` B-roll / proof panels / full-frame cards · `V3` motion-graphic overlays (alpha) · `V4` captions · `A1` voice · `A2` music · `A3` SFX. Create tracks with `add_track` before placing, and confirm with `list_sequence_tracks` — never assume an index exists.
- **Two clips can't share a start frame on one track.** Simultaneous overlays each need their own track, or the later placement overwrites the earlier one.
- **Cutting unlinked A/V** (camera audio + a separate lav/DJI mic): `link_audio_video` first so one razor moves both. If they can't be linked, razor **both** at the *same* timeline frames and shift both by the *same* delta — otherwise the audio drifts and you won't see it until export.
- **Timecodes are timeline frames, not source frames.** They diverge whenever source fps ≠ sequence fps. Read positions back with `get_clip_properties` / `get_clip_at_position` instead of computing them.
- **Verify with pixels, not with faith.** `export_frame` at a cue timecode is the only honest check that a graphic landed where the blueprint says. Do it at the hook, at every graphic cue, and at the end card.
- **Premiere generates nothing.** No transcription, no image/video/music generation. Transcribe with `hyperframes transcribe` or Whisper; generate assets via the `media-use` skill; write them to disk, then `import_media`.
- **`import_ae_comps` is not advertised** and `.aep` imports can wedge the bridge. Don't reach for After Effects round-trips.
- **When something fails twice the same way, run the panel's Run Diagnostics** rather than retrying a third time. Report what it says instead of guessing.

### Motion graphics handoff (HyperFrames → Premiere)

Anything designed is built by `ig-motion-graphics` as a HyperFrames composition, one file per graphic, and rendered to `projects/<slug>/renders/`:

```bash
npx hyperframes lint projects/<slug>
npx hyperframes render projects/<slug> -c compositions/03-counter.html \
  --format mov --resolution portrait --fps <sequence fps> --quality high \
  -o renders/03-counter.mov
```

`--format mov` carries a real alpha channel and imports into Premiere with transparency intact. Then `import_media` the file and place it on `V3` at the cue timecode from `renders/IMPORT.md` — **snap the head to the frame the keyword lands on**, not the start of the sentence.

Light-on-transparent graphics with no dark plate (a bare counter, a hairline rail) can render as `mp4` on pure black and sit on the timeline with a **Screen** blend instead — smaller, faster, and lossless for this palette.

**Never scale, reposition, or add effects to a rendered graphic in Premiere.** It was composed at full frame for a reason. If it's in the wrong place, fix the composition and re-render.

### Export

`validate_project_for_export` first — it catches missing media and offline clips before a long render. Then `export_sequence` to H.264, 1080×1920, VBR 2-pass, ~12 Mbps, AAC 320kbps, into `exports/`.

Only call it exported once the tool has returned successfully **and** the file exists on disk. If the export tool fails, say so and hand the user *File → Export → Media* — don't report a render that didn't happen.

---

## QA Checklist (run before export)

- [ ] **Hook:** does the first frame + first line stop the scroll? Biggest text, hardest cut, zero dead air?
- [ ] **Silence:** every breath/pause/filler removed? No dead air anywhere?
- [ ] **Pacing:** something changes every 1–3s? No static shot longer than ~4s?
- [ ] **Shot scale:** do adjacent shots differ in size (zoom pulse working)?
- [ ] **Captions:** word-by-word, on-brand font/color, in the safe zone, his exact words/voice (not "corrected")?
- [ ] **B-roll:** every insert covers a cut or shows the point — nothing decorative? On-brand (no banned visuals)?
- [ ] **Sound:** music ducked under voice, out under the hook, SFX subtle not gimmicky?
- [ ] **Payoff:** held, not resolved early?
- [ ] **CTA:** clean, single, on-brand (comment trigger / DM word)?
- [ ] **Look:** premium, not hype-y? Would this read as high-ticket, not "guru"?
- [ ] **Frames checked:** `export_frame` at the hook and at every graphic cue — did each one land where the blueprint says?
- [ ] **Export:** `validate_project_for_export` clean, 9:16 confirmed, safe zones respected, audio levels consistent, then `export_sequence` to `exports/`.

---

## Iteration

Be ready to quickly: re-cut the hook (most common ask), tighten pacing further, swap B-roll, change caption styling, adjust music/energy, restyle from Dynamic Minimalism toward classic Hormozi (more aggressive) or further toward clean/premium, or re-clip a long source into multiple shorts. Change the **blueprint** first, then re-execute the affected beats — don't rebuild the whole timeline.
