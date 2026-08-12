---
name: ig-video-editor
description: "Edits short-form video (Instagram Reels, TikTok, YouTube Shorts) into retention-optimized, premium-looking cuts using an MCP-connected timeline editor (Palmier Pro by default). Built on the 'Dynamic Minimalism + Devin Jatho' editing style and Feez's Content Alchemy / Cave brand: silence-removal jump cuts, slow zoom 'pulses', clean word-by-word captions, cinematic/memetic B-roll, and subtle premium sound design. Works blueprint-first — produces a timestamped, shot-by-shot edit plan the user approves, then executes it on the timeline via the editor's MCP. Use this skill whenever the user wants to: edit a reel or video, cut down raw footage, turn a talking-head recording into a finished reel, add captions, add B-roll, tighten pacing, do silence removal, design sound, restyle an edit, clip a long video into shorts, or get a shot-by-shot edit plan / EDL. Triggers: edit my reel, edit this video, cut this footage, make this a reel, add captions, add b-roll, polish this video, edit my talking head, edit my Cave footage, speed up this edit, clip this long video, edit plan, blueprint this edit, Palmier, finish this video."
---

# IG Video Editor — Dynamic Minimalism Method

Turn raw footage into retention-optimized short-form video that looks **premium, not hype-y** — and do it fast. This skill encodes the modern viral editing meta (Dynamic Minimalism + the Devin Jatho style) tuned to Feez's Cave brand, and drives an MCP-connected timeline editor (Palmier Pro) to actually build the cut.

The output is not vague advice. It is a **timestamped edit blueprint** (every cut, caption, zoom, B-roll cue, and SFX) that the user approves, then this skill **executes it on the timeline** via the editor's MCP tools.

> North star: every second earns the next second. Target 70%+ watch-through. If a frame isn't holding attention, it gets cut, zoomed, or covered.

---

## Default Mode: Blueprint → Approve → Execute

1. **Ingest** — load the footage, the script (if any), the goal, and the brand context. **Transcribe first** (Palmier `inspect_media`, or a Whisper/Scribe pass for accuracy), then check the transcript actually contains what the chosen format needs: a tier list needs the *rankings*, a listicle needs the *items*, a "3 reasons" needs the *three*. If the footage is just raw takes without that structure (common — e.g. someone naming items but never ranking them), **get the missing pieces from the user before blueprinting** rather than inventing them.
2. **Blueprint** — write the shot-by-shot edit plan (the deliverable below). This is where the craft lives.
3. **Approve** — show the blueprint, take edits. Cheap to change here, expensive to change on the timeline.
4. **Execute** — build it on the Palmier timeline via MCP, pass by pass.
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
- B-roll to generate: [list of prompts for Palmier, if any]
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
- **Sizing reality:** text is very easy to oversize — on a tall canvas `fontSize` renders large. Start small (Palmier: ~44 caption, ~60 hook title, ~78 stamp) and only grow if it reads too small; verify with `inspect_timeline` before moving on.
- **Pace match:** caption rhythm follows the cut rhythm — when speech speeds up, captions speed up.
- **Hook text:** oversized, first 3 seconds, the one moment that breaks the minimal rule.

---

## B-roll Spec

- **Purpose-first:** every insert either (a) covers a jump cut or (b) shows the concept (a number, a tool, a result, a place). If it does neither, cut it.
- **On-brand sources:** screen recordings, whiteboard, dashboards/analytics, code, the product. Generated cinematic B-roll for abstract concepts.
- **Generating in Palmier:** use the timeline's generation models (e.g. Seedance/Kling/Nano Banana Pro) with first/last-frame and reference-image control for consistency. Write prompts that match the **Cave grade** (dark, moody, filmic, cool shadows) so generated shots cut seamlessly against A-roll. **Generation costs credits** — batch the prompts, generate only what the blueprint calls for, and prefer real screen-recordings/stock when they're just as strong.
- **Timing:** 0.8–2s per insert, cut on the beat, never lingering past the point it makes.
- **No clip-art / no flying emojis.**

---

## Sound Design Spec

- **Music bed:** low, moody/cinematic/lo-fi at low volume, ducked ~-18dB under voice. Matches Cave energy. Optional subtle build into the payoff.
- **Hook:** drop music out (or near-out) under the hook line for contrast, then bring it in — instant lift.
- **SFX (subtle, premium):** soft whoosh on B-roll transitions, low click/pop on keyword reveals, a light riser into the hook. Auditory bullet points only — not on every word.
- **Voice:** clean, slight compression for presence, audible over the bed at all times. Voice always wins the mix.

---

## Execution via the MCP Editor (Palmier Pro)

Palmier Pro is a macOS, Premiere-style timeline editor that exposes an **MCP server**; the agent sees full project context and edits the timeline directly.

**Before executing:**

1. **Confirm the editor's MCP is connected** and **list its available tools** — use the actual tool names the connected server exposes. Do **not** assume tool names; read them from the live MCP. (If it isn't connected, point the user to the app's *Help → MCP Instructions* for one-click setup, and in the meantime deliver the blueprint + an NLE-importable plan.)
2. **Map blueprint → tool calls.** Capabilities to expect: import footage, trim/split/reorder/adjust clips, generate image/video/audio onto the timeline, rerun/tweak generated clips by prompt, add captions, find key moments in long footage, and upscale. (There is **no** export tool — see point 5.)
3. **Build in the 3-pass order** (spine → retention layer → polish). Verify the project state between passes rather than firing everything blind.
4. **Be credit-aware:** editing is free; **generative AI features cost credits.** Read `canGenerate` from `get_timeline` first — if `false`, the user isn't signed in/subscribed and **every `generate_*` / `upscale` call silently fails.** Don't propose AI b-roll/music/SFX in that case; generate icons & graphics with **codex** instead (see below).
5. **Export:** there is **no export MCP tool.** Build and QA the whole timeline over MCP, then tell the user to render manually in the app (**File → Export → 9:16 MP4 / H.264**). Don't claim the video is "exported" — it isn't until they do this.

If the connected editor is something other than Palmier, the blueprint is tool-agnostic — discover that editor's MCP tools and map the same beats.

### Palmier MCP — hard-won gotchas (read before executing)

These cost real iteration. Internalize them so you don't relearn them live.

- **Text size is `fontSize`, and it's scaled HEAVILY on a tall (e.g. 2160×3840) canvas.** Ignore the docs' "1080p" numbers. Working values: **~62 = caption/label, ~98 = title, ~115 = big tier stamp.** Start there, then verify.
- **`transform` width/height CROP the text, they do not scale it to fit.** A too-small box silently slices text into slivers with no error. Rule: control size with `fontSize`; give a **generous** width/height box so nothing clips. Passing *only* `centerX/centerY` (no width/height) balloons text to fill the frame. There is no size preview — add a throwaway test clip, `inspect_timeline` one frame, read the real size, then delete it.
- **Simultaneous overlays must each be on a different track.** Two clips at the same start frame on one track → the second **silently overwrites/destroys the first** (matches the UI's drag-to-overwrite; invisible over MCP). This is also why deleting a "missing" clip errors — it was already clobbered.
- **Auto-created track order/indices are unpredictable** and shift when empty tracks get pruned. Don't address tracks by index across calls; separate elements *spatially* (different `centerY`) so layer order stops mattering.
- **Cutting unlinked A/V** (talking head + separate lav/DJI mic that aren't link-grouped): split **both** clips at the **same timeline frames, in descending order** (the original id stays as the left piece, so you can keep splitting it and capture each new right-piece id), `remove_clips` the gaps, then `move_clips` both tracks by the **same delta** to compact. Trims report in **timeline frames**, not source frames — even when source fps ≠ project fps.
- **Square images need an aspect-correct box:** `height_frac = width_frac × (canvasWidth / canvasHeight)` (e.g. ×0.5625 on 2160×3840), or they stretch.
- **Verify between passes, don't fire blind:** `inspect_media` with `startSeconds/endSeconds` + `wordTimestamps` confirms a cut lands on the right words and isn't sliced mid-word; `inspect_timeline` (single frame, or a range with `maxFrames`) confirms the *composite* — text size, position, layer order, icon placement.
- **Card "pops" / reveals need `set_keyframes` per clip** (scale/opacity). Budget for that work, or accept hard cuts on the beat as the fallback.

### Generating graphics with codex (when Palmier can't, or for crisp icons/text-art)

`canGenerate:false`, or you need transparent icons/logos/tier-badges? Use the **codex CLI** (logged in via ChatGPT, has a built-in imagegen skill that outputs transparent PNGs):

```
codex exec --cd <project_dir> --dangerously-bypass-approvals-and-sandbox "<prompt: cohesive SET, transparent bg, save each to ./assets/icons/<name>.png>" </dev/null
```

The `</dev/null` is **required** when backgrounding — otherwise codex hangs waiting on stdin. Ask for a *cohesive set* (same render style, lighting, transparent alpha) in one call so the icons match. Then `import_media` (path) each PNG and place with an aspect-correct transform.

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
- [ ] **Export (manual handoff):** no MCP export tool — confirm 9:16, safe zones respected, audio levels consistent, then have the user render via *File → Export → 9:16 MP4 / H.264*.

---

## Iteration

Be ready to quickly: re-cut the hook (most common ask), tighten pacing further, swap B-roll, change caption styling, adjust music/energy, restyle from Dynamic Minimalism toward classic Hormozi (more aggressive) or further toward clean/premium, or re-clip a long source into multiple shorts. Change the **blueprint** first, then re-execute the affected beats — don't rebuild the whole timeline.
