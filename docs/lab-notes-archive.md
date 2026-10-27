# Lab notes archive — the story behind every lock

`CLAUDE.md` carries one line per lock and points here. Nothing in this file is a rule; the rules
live at their homes. This is why they exist.

## export-frame
Premiere's `export_frame` (MCP) returned `{"success": true}` and wrote nothing on Windows 11 /
Premiere 26; backslash paths were also read as C escapes (`\v`, `\f`). A previous QA checklist said
"verified with pixels" for a step producing no pixels. Lock: stills only via `lanes/ffmpeg/frame.py`.

## rerender-eperm
Re-rendering a `.mov` Premiere had open failed at ~90 % (`EPERM … rename … .hf-transaction-*`)
and left the old file, so the next check inspected the previous render. Lock: `workflows/_hf.py`
renders to a new filename (`-r2`, `-r3`…), checks the output mtime, and prunes older siblings
best-effort (a locked file survives the unlink).

## encode-throws
`encodeSequence` can throw in Premiere; the old workaround was a per-project ffmpeg rebuild in
`analysis/`. Lock: the ffmpeg lane is the delivery lane by default; `finalize.sh` falls back to it and
never reports a file that is not on disk and newer than the run.

## whisper-drift
`npx hyperframes transcribe` (whisper.cpp `small.en`) gives token-level timestamps that drift
100–300 ms on fast speech and merge fillers, so "cut on the breath" was never achievable. WhisperX
(VAD + wav2vec2 forced alignment) measured 49 s for a 42 s clip on this M2 Pro with models cached.
Lock: `workflows/transcribe.py` engine `whisperx`, `hyperframes` as fallback.

## caption-font
The first pipeline output used Anton ALL CAPS with wide word spacing (the old repo's spec) and the owner
called it terrible on sight; graphics at 500 px / 34 px text in a 1080 frame read as “a box around text”.
Measured against the reference (Jason's intro) and Faiz's own reels: both use a heavy geometric sans in
sentence/lower case with an italic serif accent word, and cards at ~2× the size. Lock: Inter 800 lowercase +
Playfair Display Italic (local OFL files), cards centred at 920 px with 42–48 px text, no provenance text on
screen, and every look change is checked at full frame size, never on a contact sheet.

## anton-font
CLAUDE.md used to say Anton auto-resolves. hyperframes 0.8.36's deterministic font list is Inter,
Montserrat, Outfit, Nunito, Oswald, League Gothic, Archivo Black, Space Mono, IBM Plex Mono, JetBrains
Mono, EB Garamond, Playfair, Source Code Pro, Noto Sans JP, Roboto, Open Sans, Lato, Poppins — no
Anton. Lock: `presets/vertical/default/fonts/Anton-Regular.ttf` (OFL) via a local `@font-face`
named `CapFace`; the family string `Anton` is never used in a stack (lint flags it).

## low-memory
`hyperframes render` estimated ~9.9 GB of temp frame storage for a 40 s alpha render and failed with
9.7 GB free. Lock: `--low-memory-mode` always (streams frames; 22 s instead of 36 s here).

## crop-expr
ffmpeg `crop`'s `w`/`h` are evaluated once at init, where `t` does not exist, so a zoom expressed as
`crop=iw/z(t)` fails ("No such filter: '0'" when the commas inside `clip()` were unquoted, then
"Error when evaluating the expression"). Lock: `scale` with `eval=frame` grows the frame, then
`crop=<source w>:<source h>` centred; the source dims come from ffprobe.

## jinja-leak
`thumb-wall` rendered nothing but its strike: `at(images | length, 1.4)` was written in the script
block without `{{ }}`, JavaScript threw on `images`, the timeline never registered, and every
`gsap.from()` left its element at opacity 0. Lock: every preset renders its example to a golden
(`build-graphics.py --preset … --golden`), which catches an empty render immediately.

## tokens-collision
The `metric` preset used a `.metric` container and `brand/tokens.css` already defines `.metric` as a
light frosted view-badge pill, so the number sat on a white pill. Lock: presets prefix their own
containers (`.mt`, `.rc`, `.w`) and never reuse a tokens.css class name for a container.

## caption-motion
Match-cut chaining (`x: 120 → 0`) and a gentler `y: 26 → 0` slide were both rejected by the owner on
sight as template effects. Lock: `build-captions.py` emits `tl.set(opacity 1)` / `tl.set(opacity 0)`
only.

## mute-windows
Two text layers in one frame was the most common reason a technically correct build looked cheap,
and no automated check saw it because each layer was individually fine. Lock: presets declare
`x-mute-captions`; `validate-plan.py` writes the window; `build-captions.py` drops the groups (a hidden
group still draws its glow).

## no-fabrication
Three builds paid for it: five empty grey bars standing in for hook copy, a build abandoned because
one screenshot never arrived, and two central numbers invented outright. Lock: `x-real` params refuse
placeholders, `x-asset` params must exist on disk, `metric` needs provenance. Before asking the
creator, work the ladder: disk → footage (`ffmpeg -ss`) → real UI (`workflows/capture-url.py`) → lookup
→ generated texture → ask → build nothing.

## sample-handles
A past build shipped a reference creator's real handle in a mockup. Lock: `creator.handle` from
`brand/brand.json`; `validate-plan.py` greps every plan for handles found in `samples/*.md`.

## no-scrim
A `radial-gradient(… rgba(0,0,0,.9))` behind a profile grid dropped mean frame luma from 62 to 14
for 9.9 s — the viewer saw the video get darker, not a graphic arrive. Lock: `graphics-qa.py` fails
darkening > 25 %; brightening (a real white screenshot) is allowed up to 50 %.

## footage-is-receipt
On the fixture the plan put a `receipt` of the Aug 27 lock screen at 4.85 s, exactly where the
speaker holds that phone up to camera; QA flagged 54–79 % face overlap on either side. The footage
was already the receipt. Lock: `creative-moves.md` — if the footage shows the object, punch in
(`pacing-audit.py --zoom-at`) instead of adding a graphic of it.

## premiere-2022-bridge
On this Mac Premiere Pro 2022 (22.0) is installed; the MCP server (v1.2.0, tested by upstream on
26.0) initialises over stdio but `verify_premiere_connection` times out because the CEP bridge panel
was never started. `lanes/premiere/bridge.mjs` exits 2 with the checklist; `run.sh` continues on
the ffmpeg lane. Premiere-lane scripts are ⚠️ unvalidated here (see `LANES.md`).

## fixture-caveat
`this summer.mp4` (the regression fixture) is Faiz's own hand-edited reel with burnt-in lowercase
captions and B-roll. It exercises every node, but the final composite shows both caption layers.
A raw take with no burnt-in text is the right fixture; the pipeline is unchanged by the swap.

## stage-class
2026-09-20, building the `multiply` preset on Windows. The composition rendered as 150 fully transparent frames
with `lint: ok` and no console error, while the same HTML in plain headless Chrome drew everything. Bisected by
deleting one thing at a time (timeline, grid, CSS rules, duration): the only change that brought pixels back
was renaming the wrapper `<div class="stage">` to `.mstage` — HyperFrames treats `stage` as one of its own
structural classes. Same family as `tokens-collision`. Rule: preset containers carry a preset-specific prefix,
and a blank-but-clean render is checked for a name collision before anything else.

## spine-captions
2026-09-28, 9077 (the creator's own Premiere cut of a 165 s multi-take raw, 8 clips, 20.6 s). Captions planned
from the raw's WhisperX words and remapped through the EDL: the creator called them "not perfectly in sync, some
missing, some overlapping". Transcribing the spine itself and diffing it against `captions.json` showed why:
"This video" (0.0–0.5) and "And the final result is" (14.4–15.5) were absent. The raw's aligner had put those
words on other takes, so the remap had nothing to map, and "the video you're" then came in ~1 s early. The
overlap was separate: group end = last word end + hold, never clamped to the next group's start. Lock:
`transcribe.py --spine` → `spine-words.json` in timeline time, which `plan-captions.py` prefers, plus the clamp.
Also: the orphan-merge joined a sentence's last word forward ("skill. Then I record"); it now joins backward.

## act-it-out
2026-09-28, 9077 v1: nine graphics, all real material, all gates green: an `agent-run` console with the job's
real steps, a real skills-page screenshot zooming, the GitHub page scrolling in a phone, a 145 s `metric`, a
Premiere timeline still zooming, a `scan` of the reel's frames, `rec-frame`, a `chat`. Creator: "6/10 … some
visuals contain text, and don't really stand out, some are just image stills slowly zooming in. I want more
motion graphics that visually demonstrate what I'm saying (if I say 'this hook is OVERPOWERED' it could show a
hook … explode into tiny pieces and turn red)". v2 replaced every beat with an action on the spoken verb
(nine new presets: script-cut, transform, drag-drop, dead-space, layer-stack, stamp, phone-play, comment,
shatter) and scored "pretty good". Real-and-static is the floor, not the bar.

## gsap-seek
2026-09-28, building the demonstration presets. (1) `tl.to(el, { keyframes: [...] })` rendered a drag that sat
still for half its duration and then jumped to the end; two consecutive `tl.to` calls rendered smoothly.
(2) `tl.fromTo(ring, { opacity: 1 … }, { opacity: 0 … }, t)` showed the ring from frame 0: fromTo renders its
start state at build time and a seek before `t` keeps it. `immediateRender: false` fixes it; fromTo from
opacity 0 is harmless. Neither shows in a golden (one frame at t=1.0). Only compositing 4–6 moments found them.

## overlay-scale
2026-09-28, 9077 in Premiere 25.3: the creator's sequence is 2160×3840; `place-layers.mjs` put the 1080×1920
caption and graphic renders at 100 %, so they sat at half size in the centre (PrintWindow showed it; every
read-back said placed). `set_clip_properties {scale: 200}` fixed it. `replace_clip` with preserveEffects then
returned "motion scale not restored", so a swapped render needs its scale set again. The opposite of the 9028
note (4K clips in a 1080 sequence → 50 %). Premiere never re-fits script-placed clips.

## timeline-eats-audio
2026-10-23, 9030 in Premiere 25.3: b-roll placed on V2 with `add_to_timeline {insertMode: overwrite, linkAudio: false}`
returned success with `unlinkedAudioRemoved: 1` every time — and the music bed on A2 was gone under every shot. The
clip's camera audio is dropped onto the A track with the SAME index in overwrite mode first, then deleted. Rebuilt the
bed from the same source offsets (the creator's −15 dB was clip gain, not the Volume effect). Since then: place video on
a V track whose A lane is empty (added V4/V5 with empty A4/A5), and diff the audio tracks after every placement.
`add_track {trackType: audio, position: below}` inserts at index 0 (above A1); `above` appends.

## punch-in-face
2026-10-24, 9030: graphics passed graphics-qa in the `top` slot (face box y 699–984 on the spine), but the creator's
V1 is punched in — on his program monitor the hair reached y≈250 in the hook and the game ledge cut across his head.
QA measures the spine, not his framing. PrintWindow at 3–4 moments per graphic found it; `inline` was clear.

## creativity-floor
2026-10-23/24, 9030: rejected in order — keyed green-screen cash ("tacky"), a hand-made PIL profile card ("out of
place"), stock `metric` ("lacks creativity in every single aspect"), a `receipt` still that zoomed ("nothing of
substance"). Asked for: a pixel-art game with a character that looks like him and a counter going white → green.
Became `pixel-quest` / `pixel-crowd`, the PixelQuest font, the `pixel-arcade` skin and the `broll-story` look.

## join-whitespace
2026-10-25, 9278: "too much whitespace". Every join carried 0.22–0.39 s of near-silence (lead 0.08 + tail 0.10 + what
the edge snapper left); the spine gate only fails silences ≥ 0.45 s. Now lead 0.04 / tail 0.05, `check-joins.py`
measures true silence (−50 dB, the lav floor is −80) across each join, max 0.18 s. Measuring at −35 dB counted a soft
final "you" (−40 dB) as silence; and `edge_rel_db` 30 had been clipping that same syllable — now 38.

## breath-pauses
2026-10-25, 9278 v4: "still too much pause. one example when i said muse theres some whitespace". The join gate counted
silence below −50 dB; the DJI lav gates itself between words (−95 dB floor), and the spine kept 0.10 s at the "Muse"
join plus 16 breaths of 0.06–0.25 s inside clips (min_gap_s 0.35 never touched them). Two of his posted reels, word
gaps and envelope: no run ever falls 20 dB under speech; max word gap 0.16 s. Now: pauses are measured relative to
speech (`pause_rel_db` 30), every one over `pause_max_s` is cut, edges sit 32 dB under speech (38 waited out the lav's
70 ms decay tail), lead/tail 0.03/0.02, gate 0.10 s. A 0.23 s silence inside "outreach" ended in a faint sound that
looked like a breath — spectrum 96 % in 2–6 kHz, centroid 4.2 kHz: the "ch". Trimming on level alone would have chopped
it, so breaths are trimmed only past the last word's end; the closure is cut and leaves a 5-frame tuck of the same
take. Re-cutting moved every cue: `remap-plan.py` + rough-cut carrying punches by source time.

## range-keeps
2026-10-26, 9287 (a standing, many-take script). The slate detector dropped the hook take as off-mark (he moves — a
standing take is not a slate: `{"mark": false}`); the retake rule swallowed Q1 "What is my desired outcome" inside the
next take's removal; an aside to the editor ("this part you're gonna show on screen") stayed in. Vetoes by id broke
when one word's timing was fixed (every later id shifted by one; a veto brought back an abandoned take) → vetoes by
range. "This … this is my other account": WhisperX timed only the first "This"; the restart (voiced burst + "s" at
5 kHz) was untranscribed, so the clip started mid-word — the word's timing was moved to the restart in words.json.
The one-word piece had first been deleted by `drop_slivers` (min_clip_s applied to pieces WITH words) — now padded.
A click after "…you retard" made 7b read the silence before it as a closure; 7c now scans clip edge to edge.

## frame-drift
2026-10-26, 9287: match-cuts made one cut worse every round (×1.05 → ×1.12). Frame-by-frame the face jump sat 0.13 s
after the EDL offset: each clip rendered `trim=duration` (a partial last frame kept), the spine ran 45.58 s for a
45.41 s EDL. Audio drifted with it (lip sync fine, captions fine — they read the spine's own words), but punch times,
check-joins, check-framing and match-cuts all index the EDL. Clips are whole frames now (rough-cut quantises `out`,
the lane trims `end_frame` and `end_sample`). Same day: remap-plan treated graphic-local times as timeline times
(9279's bot-team beats all shifted by its cue) — local times map through cue + t.

## matte-head
2026-10-26, 9280 after the tighter framing: on 5 of 12 contact-sheet frames a dark figure stood on his head — the
framed picture on the wall, which `remove-background` keeps when it touches the hair. Above the face box, over the
head's columns, the matte keeps only an ellipse continuing the skull (hair ends ~0.31 face heights up; the ellipse
reaches 0.34, 0.9 face widths out). A hand raised beside the head is outside those columns and survives.

## zoom-anchor
2026-10-25, 9278: "the zooming in is completely off". Punches were a 1.2 s smoothstep creep (3–8 %) via
`scale=…:eval=frame,crop=SW:SH` — the crop's x/y did not follow the per-frame scaled size, so the zoom grew from the
top-left and the face slid 6 % right and down (measured with the face detector before/after). Now one `zoompan` per
clip: base framing × punch, window placed so the face stays at (0.5, framing.face_y); punches snap in 0.12 s.

## assemble-ram
2026-10-25, 9278: the final export took 23.8 GB and died "Cannot allocate memory". One graph trimmed six clips out of
the 4K raw (and later six input-seeked copies of it) into `concat`; ffmpeg decodes every input at once and queues the
frames concat isn't ready for. Now pass 1 renders each clip alone (input seek, framing, punch, canvas size) into
`preview/clips/` — cached by everything that shapes it — and pass 2 reads them with the concat demuxer: 0.9 GB spine,
1.6 GB final, 15 s instead of 4.5 min.

## cut-match
2026-10-25, 9278: "between clips, there's a clear cut. it looks snappy instead of smooth." His posted reels are hard
cuts (one-frame difference spike, no dissolve) on a camera that never moves. Ours re-centred each clip on its median
face: across the six cuts the face jumped 0.012–0.154 of the width and changed size up to 11 %, and punches held to
the cut. Now the window glides from face_in to face_out (each three frames averaged), the base scale follows the face
width toward the median (±10 %), and punches ease out 0.4 s before the cut: jumps 0.006–0.014, size ≤ 6 %.

## caption-rerun
2026-10-25, 9278: re-running from the rough cut re-planned captions.json and dropped hand-set accents ("called"
lit up instead of "Muse"); a manual plan-captions after the pacing node read the raw transcript because the pacing
spine rebuild (zoom only, same audio) was newer than spine-words.json. Accents now live in captions.overrides.json;
transcribe --spine writes spine-words.key (a hash of the keep ranges) and plan-captions trusts that, not file times.

