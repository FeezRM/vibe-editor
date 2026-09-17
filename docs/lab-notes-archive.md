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
