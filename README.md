<div align="center">

# Vibe Editor

**Describe the cut. The agent builds it in Premiere Pro.**

An end-to-end, agent-driven video editing workspace.
[HyperFrames](https://github.com/heygen-com/hyperframes) draws the motion graphics.
[Adobe Premiere Pro](https://github.com/hetpatel-11/adobe_premiere_pro_mcp) — driven over MCP — does everything else:
ingest, cutting, captions, color, audio, and the export.

<br>

![Node](https://img.shields.io/badge/node-22%2B-339933?style=flat-square&logo=node.js&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-supported-000000?style=flat-square&logo=apple&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-supported-0078D4?style=flat-square&logo=windows&logoColor=white)
![Premiere Pro](https://img.shields.io/badge/Premiere%20Pro-2020%2B-9999FF?style=flat-square&logo=adobepremierepro&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-283%20tools-5fd3c6?style=flat-square)
![License](https://img.shields.io/badge/license-GPL--3.0-blue?style=flat-square)

[Quick start](#quick-start) ·
[How it works](#how-it-works) ·
[The workflow](#the-workflow) ·
[Say this](#say-this) ·
[Layout](#repository-layout) ·
[Troubleshooting](#troubleshooting)

</div>

---

Most "AI video editors" are a black box: you hand over footage, you get back a render, and
the only knob is *try again*. This one is the opposite. Your agent operates **your** Premiere
Pro project on **your** machine — the real timeline, real tracks, real clips — and writes its
motion graphics as HTML that renders deterministically to alpha video.

Nothing is hidden behind a service. Every cut is a tool call you can inspect, every graphic
is a file you can open, and when the agent walks away you're left with a normal Premiere
project you can keep editing by hand.

## How it works

```
  you ──▶ "cut the dead air, put a counter on the 4M views line, then export 9:16"
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │  BLUEPRINT           │  timestamped, shot by shot
                            │  you approve it      │  cheap to change here
                            └──────────┬───────────┘
                                       │
                     ┌─────────────────┴────────────────────┐
                     ▼                                      ▼
        ┌────────────────────────┐              ┌────────────────────────┐
        │  HYPERFRAMES           │              │  PREMIERE PRO · MCP    │
        │  HTML + CSS + GSAP     │              │  283 tools             │
        │           ↓            │              │  ingest · cut · color  │
        │  deterministic render  │              │  audio · captions      │
        │           ↓            │   import     │                        │
        │  alpha .mov / .mp4     │ ────────────▶│  your real timeline    │
        └────────────────────────┘              └───────────┬────────────┘
                                                            │ export_sequence
                                                            ▼
                                                    exports/reel.mp4
```

Two engines, one conversation:

| | **HyperFrames** | **Premiere Pro MCP** |
|---|---|---|
| **Owns** | Motion graphics, titles, kinetic captions, data viz | The timeline: ingest, cuts, transitions, effects, color, audio, captions, export |
| **Interface** | HTML compositions + a CLI | 283 MCP tools over a local CEP bridge |
| **Output** | Alpha `.mov`, `.mp4`, PNG sequences | Your `.prproj`, and the final render |
| **Runs** | Headless Chrome + FFmpeg, locally | Inside Premiere Pro, locally |
| **Deterministic** | Yes — same HTML, same frames, every time | Yes — you can see and undo every operation |

The seam between them is deliberate. HyperFrames is far better at typography and motion
than any NLE's title tool, and Premiere is far better at cutting than any web renderer.
The agent uses each for what it's good at, and hands the alpha `.mov` across.

## Quick start

**macOS**

```bash
git clone <your-fork-url> vibe-editor && cd vibe-editor
./scripts/setup-macos.sh
```

**Windows** (PowerShell)

```powershell
git clone <your-fork-url> vibe-editor; cd vibe-editor
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
```

The script clones both engines into `vendor/`, builds the MCP server, installs the Premiere
CEP bridge panel, installs the HyperFrames and Premiere agent skills, registers the MCP
server in `.mcp.json`, and runs diagnostics. It is idempotent — re-run it any time to update.

Then three things only Premiere can do:

1. Restart Premiere Pro and open a project.
2. Open **Window → Extensions → MCP Bridge (CEP)**.
   *(Missing? Enable **Preferences → Plugins → Enable developer mode**, then restart.)*
3. Set **Temp Directory** to the bridge path the installer printed
   (`/tmp/premiere-mcp-bridge` on macOS, `%TEMP%\premiere-mcp-bridge` on Windows),
   then **Save Configuration → Start Bridge → Test Connection**.

Finally, start your agent in this folder and confirm the link:

> Run `verify_premiere_connection`. Make no changes.

When it reports your Premiere build, open project, and active sequence — you're live.

<details>
<summary><b>Setup script options</b></summary>

```bash
./scripts/setup-macos.sh --skip-premiere      # HyperFrames only
./scripts/setup-macos.sh --skip-hyperframes   # Premiere MCP only
./scripts/setup-macos.sh --skip-skills        # clone + build, install no agent skills
./scripts/setup-macos.sh --skip-doctor        # skip post-install diagnostics
```

The Windows script takes the same switches in PowerShell form: `-SkipPremiere`,
`-SkipHyperframes`, `-SkipSkills`, `-SkipDoctor`.

</details>

## The workflow

The agent works **blueprint-first**. It plans in text — cheap to change — and only then
touches the timeline, where changes are expensive.

**1 · Connect.** `verify_premiere_connection` before anything else. It's read-only and
confirms Premiere, the bridge, the open project, and the active sequence in one call.

**2 · Ingest.** `import_media` / `import_folder` pull footage into the project.
`detect_scene_edits` finds cuts in long takes; a transcription pass turns speech into
timestamped words the blueprint can key off.

**3 · Blueprint.** A timestamped, shot-by-shot plan: every cut, caption, push-in, B-roll
cue, graphic, and SFX. **You approve this before the timeline moves.** Say *"just do it"*
to collapse it to one line per beat and skip ahead — the quality bar doesn't move.

**4 · Cut the spine.** `razor_timeline_at_time`, `split_clip`, `trim_clip`, `move_clip`,
`link_audio_video`. Silence and filler come out first; nothing gets polished before the
story flows end to end.

**5 · Graphics.** Each graphic is a HyperFrames composition — one HTML file, one job.
Lint it, render it to alpha `.mov`, then `import_media` it and place it on the overlay track.

```bash
npx hyperframes lint  projects/<slug>
npx hyperframes check projects/<slug>
npx hyperframes render projects/<slug> -c compositions/03-counter.html \
  --format mov --resolution portrait --fps 30 --quality high \
  -o renders/03-counter.mov
```

`--format mov` and `--format webm` carry a real alpha channel; Premiere imports the MOV with
transparency intact. Every render ships with a `renders/IMPORT.md` cue sheet — file,
timecode, track, blend mode — so placement is mechanical, not guesswork.

**6 · Finish.** `color_correct`, `adjust_audio_levels`, `apply_audio_effect`,
`add_transition`, `create_caption_track`, `add_marker`.

**7 · Export.** `validate_project_for_export` first, then `export_sequence` —
or `export_as_fcp_xml` / `export_aaf` to hand the cut to another suite.

At every step the project is just a Premiere project. Close the agent, open the timeline,
and keep working.

## Say this

Natural language in, tool calls out:

> *"Import the DJI mic track, sync it to the camera audio, then cut every pause longer than 400ms across both."*

> *"Razor the interview at 12.5 seconds across all tracks and drop a cross dissolve on every cut on V1."*

> *"Build a counter graphic for the 4 million views line — it lands on the 12-second beat."*

> *"Alternate the shot scale beat to beat for the whole middle section; nothing should sit static for more than four seconds."*

> *"Grade it for the dark-room look: deep contrast, cool shadows, controlled highlights."*

> *"Duck the music 18dB under the voice and pull it out entirely under the hook."*

> *"Validate the sequence and export 9:16 H.264 to exports/."*

## Make it yours

The repo ships with one opinionated house style. **You are not stuck with it, and you
should never have to edit a skill to change it.** Two files own everything:

```bash
node scripts/brand.mjs init      # wizard: colours, fonts, skin, fps
```

That writes `brand/brand.json` and compiles `brand/tokens.css`. Then open
`brand/BRAND.md` and write your rules in plain English.

The setup scripts already create `brand/` for you — if either file is missing they scaffold
a blank one to fill in, and they never overwrite a file you've edited. To do it by hand:

```bash
node scripts/brand.mjs scaffold  # blank brand/brand.json + brand/BRAND.md
```

| File | Holds | Format |
|---|---|---|
| **`brand/brand.json`** | palette, fonts, canvas, fps, texture, density, export | JSON, schema-backed |
| **`brand/BRAND.md`** | voice, subject matter, banned visuals, CTA, sound taste | free text |

**Every skill reads both before it plans or builds anything**, and the precedence is
explicit:

```
repo defaults  →  brand/  →  the project's own tokens.css / MOTION-PLAN.md  →  what you say in chat
```

Change your accent once in `brand.json`, run `node scripts/brand.mjs build`, and every
future project picks it up. `brand/tokens.css` is **generated** — never hand-edit it. It's
built by substituting your values into the skin stylesheet, so the design system stays in
one place and your fork only carries the diff.

```bash
node scripts/brand.mjs show      # resolved config + contrast readout
node scripts/brand.mjs check     # validate without writing
node scripts/brand.mjs build     # brand.json -> tokens.css
```

`check` and `build` also warn you about the things that quietly ruin a render: pure-black
grounds, ink/ground contrast below 7:1, an accent that vanishes over dark footage, a font
stack with no fallback, and captions parked in the bottom third.

Omit `accentHi`, `accentLo`, `groundLift`, or `ink2` and they're derived from your accent
and ground automatically. Most people only ever set three colours.

## The house style (the default)

Seven skills load automatically whenever an agent runs here — one per step of the editing
process, plus an orchestrator:

| Skill | Owns |
|---|---|
| **`ig-reel`** | Orchestrator. The edit blueprint, the sequence, the track layout. Dispatches the rest. |
| **`ig-cut`** | Step 1 — silence and filler. The spine. |
| **`ig-captions`** | Step 2 — word-accurate captions, banded at 45–60% of frame. |
| **`ig-sound`** | Steps 3 + 5 — music bed, ducking, SFX. One mix. |
| **`ig-show`** | Step 4 — **the motion graphics.** 20 named blocks, two skins. The one that matters most. |
| **`ig-pacing`** | Step 6 — pattern interrupts, zoom pulses, shot scale. |
| **`ig-delivery`** | QA and export. |

The system in six lines:

1. **Graphics are instrumentation, not decoration.** Every graphic answers *what does this
   measure, prove, or compare?* Dials, counters, deltas, curves, ledgers, diffs — never
   swooshes, highlight blobs, or emoji. Lines that prove nothing get **no graphic at all.**
2. **One accent per project.** Max two accent elements per frame.
3. **Entrances 0.28–0.42s. Hold ≥0.8s. No exits — the cut is the exit.**
   Never bounce, elastic, or back.
4. **≤8 graphics per 30s reel**, one every 3–5s, exactly one in the first three seconds —
   but something changes on screen every **1–2s**, mostly on the caption layer.
5. **Texture is mandatory.** Grain, vignette, feathered edges, and a ~15fps stutter on
   mechanical motion. Perfectly smooth, perfectly flat output is what reads AI-generated.
6. **Zero UI chrome.** No counters, no watermark, no follow banner.

Full spec in [`.claude/skills/ig-show/reference/`](.claude/skills/ig-show/reference/) —
`DEVICES.md` (spoken idea → visual device), `BLOCKS.md`, `MOTION-LANGUAGE.md`,
`TEXTURE.md`, `PIPELINE.md`. `templates/base/` is a lint-clean HyperFrames starter.

To bring your own system entirely: rewrite `brand/BRAND.md`, or delete `.claude/skills/`
and let the agent work from your prompts alone.

## Repository layout

```
vibe-editor/
├── scripts/
│   ├── setup-macos.sh              one-shot install / update (macOS)
│   └── setup-windows.ps1           one-shot install / update (Windows)
├── brand/                          YOUR customisation — edit these two, rebuild
│   ├── brand.json                  palette, fonts, canvas, density  (schema-backed)
│   ├── BRAND.md                    voice, banned visuals, CTA       (free text)
│   └── tokens.css                  GENERATED — never hand-edit
├── .claude/skills/
│   ├── ig-reel/                    orchestrator — blueprint, tracks, dispatch
│   ├── ig-cut/                     step 1 — silence and filler
│   ├── ig-captions/                step 2 — captions
│   ├── ig-sound/                   steps 3+5 — music and SFX
│   ├── ig-show/                    step 4 — the motion graphics
│   │   └── reference/              DEVICES · BLOCKS · MOTION-LANGUAGE · TEXTURE · PIPELINE · INTAKE · tokens-*.css
│   ├── ig-pacing/                  step 6 — pattern interrupts
│   └── ig-delivery/                QA and export
├── templates/base/                 lint-clean HyperFrames starter, 4 working blocks
├── projects/                       one folder per video (compositions + renders)
├── exports/                        finished masters out of Premiere
├── vendor/                         cloned engines — gitignored, managed by the setup script
│   ├── hyperframes/
│   └── adobe-premiere-pro-mcp/
├── .mcp.json                       generated: registers the premiere-pro MCP server
├── scripts/brand.mjs               the brand generator (scaffold / init / build / show / check)
└── ig-show.skill                  the motion-graphics skill, packaged for distribution
```

## Requirements

| | |
|---|---|
| **OS** | macOS, or Windows 10/11 |
| **Node.js** | 22 or newer (HyperFrames needs 22; the Premiere MCP needs 20) |
| **FFmpeg** | Required by HyperFrames — `brew install ffmpeg` / `winget install Gyan.FFmpeg` |
| **Adobe Premiere Pro** | 2020 or newer, tested on 26.0 |
| **Git** | For cloning the engines |
| **MCP client** | Claude Code, Claude Desktop, Codex, Cursor, Copilot in VS Code — anything that speaks MCP |

Premiere Pro, the MCP client, and this repo must all be on the **same machine**. The bridge
is local by design — no footage ever leaves your computer.

## Troubleshooting

**The agent sees the tools but every call fails.**
Almost always the bridge, not the server. Check, in order: Premiere is open → a project is
open → the CEP panel is running → the panel's Temp Directory matches the installer's bridge
path. Then right-click the panel → **Reload**.

**The CEP panel isn't in the Extensions menu.**
Enable **Preferences → Plugins → Enable developer mode** and restart Premiere. The setup
script already sets Adobe's `PlayerDebugMode`.

**Diagnostics.**

```bash
npm --prefix vendor/adobe-premiere-pro-mcp run setup:doctor   # bridge, build, client config
npx hyperframes doctor                                        # node, ffmpeg, chrome, skills
```

On Windows the first command is `npm --prefix vendor\adobe-premiere-pro-mcp run setup:doctor:win`.

The CEP panel's **Run Diagnostics** button writes a full report next to the bridge directory.

**A graphic renders as a black rectangle in Premiere.**
It was rendered without alpha. Re-render with `--format mov`. If a MOV imports opaque,
right-click it → **Modify → Interpret Footage → Alpha Channel: Straight (Unmatted)**.

**A graphic stutters on the timeline.**
The composition's fps doesn't match the sequence. Re-render at the sequence fps rather than
letting Premiere conform it.

**Never resize or reposition a graphic in Premiere.** It was composed at full frame for a
reason. Fix the composition and re-render — twenty seconds of render beats a graphic that's
eight pixels off the shared axis.

More failure modes, with causes and fixes, in
[`PIPELINE.md`](.claude/skills/ig-show/reference/PIPELINE.md#7-common-failures).

## Built on

- **[HyperFrames](https://github.com/heygen-com/hyperframes)** by HeyGen — write HTML, render
  video, built for agents. Apache-2.0.
- **[MCP Bridge for Adobe Premiere Pro](https://github.com/hetpatel-11/adobe_premiere_pro_mcp)**
  by [@hetpatel-11](https://github.com/hetpatel-11) — 283 MCP tools over a local CEP bridge. MIT.

Both are cloned into `vendor/` at their upstream versions and are never vendored into this
repo's history. Their licenses are their own.

Adobe and Premiere Pro are trademarks of Adobe Inc. This project is not affiliated with,
endorsed by, or sponsored by Adobe.

## License

Copyright © 2026 Faiz Kerawala. Licensed under the [GNU General Public License v3.0](LICENSE).

This program is free software: you can redistribute it and/or modify it under the terms of
the GPL as published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. It is distributed **without any warranty** — without even
the implied warranty of merchantability or fitness for a particular purpose. See the
[LICENSE](LICENSE) for details.

In practice: fork it, edit the skills, sell what you make with it. But if you **distribute** a
modified version of the editor itself, that version has to ship its source under the GPL too.
Reels you cut with it are your own work and carry no obligation — the license covers the tool,
not its output.

That scope is this repository: the skills, the brand layer, the scripts, and the templates.
The engines in `vendor/` are cloned at their upstream versions and keep their own licenses
(HyperFrames: Apache-2.0 · MCP Bridge for Premiere Pro: MIT) — both are one-way compatible
with the GPL, and neither is redistributed here. The licensed typefaces aren't distributed
here either; each machine supplies its own copies, and those EULAs are between you and their
foundries.
