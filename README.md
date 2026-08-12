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

## The house style

This repo ships with an opinionated design system for short-form vertical video. It's
**optional** — delete `.claude/skills/` and you have a clean, style-agnostic vibe editor —
but if you keep it, two skills load automatically whenever an agent runs here:

| Skill | Owns |
|---|---|
| **`ig-video-editor`** | The cut — silence removal, shot scale, pacing, B-roll, captions, sound design. Produces the edit blueprint. |
| **`ig-motion-graphics`** | The look — *"The Terminal, in motion"*: 1080×1920, near-black `#0F0F10`, off-white `#F0EEE8`, one declared accent. 13 named graphic blocks, 7 reveal verbs. Produces the motion plan. |

Both cue off the same timecodes, so the cut and the graphics stay in sync.

The system in five lines:

1. **Graphics are instrumentation, not decoration.** Every graphic answers *what does this
   measure or prove?* Meters, counters, deltas, curves, diffs, terminal logs, receipts —
   never swooshes, highlight blobs, or emoji.
2. **One accent per project.** Max two accent elements per frame.
3. **Entrances 0.28–0.42s. Hold ≥0.8s. No exits — the cut is the exit.**
   Never bounce, elastic, back, or linear.
4. **≤8 graphics per 30s reel**, one every 3–5s, exactly one in the first three seconds.
5. **Zero UI chrome.** No counters, no watermark, no follow banner.

Full spec in [`.claude/skills/ig-motion-graphics/reference/`](.claude/skills/ig-motion-graphics/reference/) —
the motion language, the block catalog, the intake questions, and the render pipeline.
`templates/base/` is a lint-clean HyperFrames starter with four working blocks.

To bring your own style instead: replace these two skills with your own, or drop them and
let the agent work from your prompts alone.

## Repository layout

```
vibe-editor/
├── scripts/
│   ├── setup-macos.sh              one-shot install / update (macOS)
│   └── setup-windows.ps1           one-shot install / update (Windows)
├── .claude/skills/
│   ├── ig-video-editor/            the cut — blueprint, pacing, captions, sound
│   └── ig-motion-graphics/         the look — motion language, 13 blocks, pipeline
│       └── reference/              MOTION-LANGUAGE · BLOCKS · INTAKE · PIPELINE · tokens.css
├── templates/base/                 lint-clean HyperFrames starter, 4 working blocks
├── projects/                       one folder per video (compositions + renders)
├── exports/                        finished masters out of Premiere
├── vendor/                         cloned engines — gitignored, managed by the setup script
│   ├── hyperframes/
│   └── adobe-premiere-pro-mcp/
├── .mcp.json                       generated: registers the premiere-pro MCP server
└── ig-motion-graphics.skill        the motion-graphics skill, packaged for distribution
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
[`PIPELINE.md`](.claude/skills/ig-motion-graphics/reference/PIPELINE.md#6-common-failures-and-what-they-actually-mean).

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

The engines above carry their own licenses. This repository has not declared one yet — add a
`LICENSE` file before publishing if you intend others to use, fork, or contribute to it.
