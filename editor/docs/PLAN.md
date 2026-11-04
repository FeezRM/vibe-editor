# Plan: Vibe Studio, a Rust NLE for vibe-editing

> Branch `rust-editor` · 2026-11-04 · status: **approved; M0–M3 first cut built** (see Progress).
> The evidence is in `RESEARCH.md`; the look is in `DESIGN.md`; the code is in `../../studio/`
> (`studio/VIBE-STUDIO.md` lists every change from FilmCraft).

## Decisions (2026-11-04, from the owner)

- **Name:** Vibe Studio.
- **Base:** FilmCraft. Because only the UI would be reshaped and upstream merges must stay easy, the whole repo
  came in as a git subtree at `studio/` (an evolution of option D below): the engine is unmodified except for one
  new module and its registration, and the UI and app crates carry the Vibe Studio changes.
- **Accent:** the creator's brand colour (`brand/brand.json` `palette.accent`; default amber `#FFC531`).
- **Role:** edit by hand, see what the AI and agents did, ask the AI, **and export**.

## Progress

| Milestone | State |
|---|---|
| M0 spike | ✓ builds on Linux in ~10 min cold (4 cores), ~2 min incremental; runs under Xvfb (software Vulkan); headless export of a 1080×1920 H.264 works |
| M1 headless bridge | ✓ first cut: `vibe.importJob` (engine command): takes, camera, zoom punches, captions, graphics, SFX, voice gain, transcript. Tested on a synthetic job: 267 frames = the EDL, captions muted under the graphic, gains set. ✗ not yet: holds, per-word accent styling, b-roll, the PSNR gate against a real job's ffmpeg-lane final |
| M2 desktop shell | ✓ first cut: renamed, own icon, brand accent, flat dark tokens, page tabs, `Vibe` workspace, Export button. ✗ not yet: the CapCut-style inspector tabs, overview strip, safe-zone overlay |
| M3 agent lane | ✓ first cut: Assistant panel (Ask Claude with tool use over every command + frame look; Activity feed of Claude's and agents' commands); `lanes/vibe/{open,export}.sh`; `finalize.sh --lane vibe` with ffmpeg fallback. ✗ not yet: ig-* skill sections, LANES.md parity runs |
| M4–M6 | not started |


## 1. Goal

A desktop video editor, written in Rust, that:

1. **Works like the editors people know.** It uses Premiere's timeline, tools and keys (switchable to Resolve
   or CapCut layouts), CapCut's one-panel inspector and asset browser, and Resolve's pages. The ig-* skills and
   the user's hands carry over unchanged.
2. **Opens every pipeline job as a fully editable timeline.** Each take is a clip; each zoom is a keyframe;
   each caption is editable text; each graphic is a layer; each SFX is an audio clip. Nothing is baked in that
   the user might want to change.
3. **Is the agent's native lane.** The agent edits through the same commands as the user's buttons, with no
   bridge, typed results, and headless renders it can watch. It replaces `lanes/premiere` as the
   refinement lane and can become the delivery lane.
4. **Looks simple, clean and dark.** Flat, neutral and quiet, with one accent colour and no gradients
   (`DESIGN.md`).

**Not goals (for now):** replacing the Python pipeline (it stays the editing brain, §6), plugin hosting
(VST/OFX), `.prproj` import, a Fusion-style node compositor, multi-user projects, or a mobile app.

## 2. The key decision: build on FilmCraft's engine, own the surface

| Option | Effort to Premiere-grade | Verdict |
|---|---|---|
| A. Write a new NLE from scratch in Rust | FilmCraft, at ~457 k lines and ~86 % breadth, estimates **1,550–2,750 agent-hours** left to full parity. A from-scratch start is years behind that | ✗ |
| B. Rust UI over ffmpeg/GStreamer | Fast first light, but no exact-time edit algebra, no keyframe engine, no tested compositor. We would rebuild FilmCraft's L1–L4 badly | ✗ |
| C. Fork all of FilmCraft and rebrand it | Day-one parity, but 457 k lines to maintain, upstream fixes lost, and a "Premiere clone" UI that is busier than we want | ✗ |
| **D. Downstream of FilmCraft:** depend on its engine crates (L0–L4) at a pinned rev; **fork only the UI crate** as a template we reskin and reshape; add our own short-form crates | Parity on editing, codecs, render and interchange from day one. Our effort goes to what is ours: surface, look, short-form tools, pipeline bridge, agent | **✓ chosen** |

Licence: FilmCraft is MIT OR Apache-2.0, and vibe-editor is GPL-3.0, which is compatible. We keep their
`NOTICE`, both licence texts and per-file attribution in the forked UI code (`editor/UPSTREAM.md`). Their asset
rule binds us too: no Adobe (or ByteDance, or Blackmagic) artwork, icons, fonts, LUTs or presets, ever.

**What we upstream instead of forking:** any engine-level gap we hit (an engine command, an effect parameter,
a caption feature) goes upstream as a PR. We keep a patch on our pinned rev only until it merges. The engine
stays theirs; the surface is ours.

## 3. Architecture

```
editor/                                  (new Cargo workspace on this branch)
├── Cargo.toml                           filmcraft-* = { git = "https://github.com/storytold/filmcraft", rev = "<pinned>" }
├── UPSTREAM.md                          pinned rev, what we forked, attribution, how to bump
├── crates/
│   ├── vibe-job/        L1  pure serde model of a pipeline job: RUN.md state, cuts.json (keep/hold/zoom), spine-words,
│   │                        captions.json + overrides, graphics-plan.json, sfx-plan.json, voice-gain.json, framing.json,
│   │                        the preset numbers. No engine dependency, so the Python side can be tested against it
│   ├── vibe-bridge/     L4  job → engine commands (import) and timeline → job files (round trip, §5.3). One undo step per import
│   ├── vibe-shortform/  L4  macro commands, registered next to FilmCraft's: vibe.importJob, vibe.zoomPunch,
│   │                        vibe.captions.applyLook, vibe.captions.accent, vibe.reframe, vibe.safeZone, vibe.verify …
│   ├── vibe-theme/      L5  design tokens (DESIGN.md) → egui Visuals; the only place a colour is defined
│   ├── vibe-ui/         L5  fork of filmcraft-ui-egui @ pinned rev: reskinned, pages instead of workspaces,
│   │                        CapCut-style inspector and asset rail, 9:16-first monitor, caption track editor
│   └── vibe-agent/      L5  MCP server (stdio) and JSON-lines control: every engine command + vibe.* + render/verify tools
└── apps/
    ├── vibe/            L6  desktop app (eframe/wgpu, cpal)
    └── vibe-cli/        L6  headless: import <job> · render <job> --stage … · verify · mcp · exec <command>
```

The layering rule is FilmCraft's, enforced by our own `xtask layers`: nothing below L5 knows a UI exists, so
everything the user can do, the agent and CI can do headless.

**Time:** the pipeline speaks float seconds; the engine speaks integer ticks. `vibe-bridge` converts **once**
at import, snapping to the sequence's frame grid (the frame-drift lock), and converts back when it writes job
files.

## 4. Pipeline → timeline mapping (the heart of the bridge)

Sequence: `canvas` from the preset (1080×1920 at 30 fps by default). Tracks: V1 A-roll, V2 b-roll, V3/V4
graphics, a caption track, A1 voice, A2 b-roll audio, A3 SFX, A4 music.

| Pipeline file | Becomes | Editable as |
|---|---|---|
| `raw/<source>` | one media item, plus a proxy if the source is 4K or 10-bit HEVC | Project bin |
| `cuts.json` `keep[i]` (`in`/`out`) | one linked V1+A1 clip per keep, back to back | trims, slips, ripples, rolls: everything |
| `keep[i].hold` | a frame-hold segment after the clip | normal clip |
| `preview/framing.json` (scale, face-centred offset, opening zoom) | Motion Scale/Position on every V1 clip; opening zoom-out as two eased keyframes | Inspector ▸ Transform |
| `keep[i].zoom` (`at`, `pct`, `dur`, `face`, `out`) | Scale + Position keyframes (ease in/out) anchored on the face point, on the clip that holds `at` | keyframe lane, graph |
| `transcript/spine-words.json` | the item's transcript (`transcript.set`, media time) | Transcript panel (text-based editing) |
| `captions.json` + `captions.overrides.json` accents | a caption track: one text clip per caption with word timings; accent words carry the look's accent style (font, colour, caps) | Captions page: text, timing, style per caption or per track |
| caption look (`presets/vertical/<look>`: font, size, band y, max width, colours) | a **track style preset**, applied to the whole caption track as in Resolve and CapCut | Captions page ▸ Style |
| `graphics-plan.json` + `renders/g*.mov` | an alpha clip at `cue` on V3 (V4 when V3 is busy), with the plan's `id` and `provenance` as clip metadata | move, trim, keyframe; **Re-render** sends it back to the pipeline |
| `mute_captions` windows | captions in that window disabled (not deleted) | toggle |
| `audio/voice-gain.json` | clip volume on every A1 clip; a −16 LUFS target in the loudness meter | Inspector ▸ Audio |
| `sfx-plan.json` | clips on A3 at their level, labelled with their reason | normal audio clips |
| music bed (if any) | A4 with ducking keyframes under the voice | volume rubber band |
| `review/takes.md` removals | markers (hidden by default) at each removed range with its reason | Markers panel: "why was this cut?" |

Every imported object carries `vibe.origin` metadata (`{file, id}`), so the round trip knows what the agent made
and what the user changed.

## 5. What we build, by phase

Each milestone ends with a gate: something measured, not a feeling. Hours are agent-hours, rough, for
planning only.

### M0. Spike: does the base hold? (≈ 6–10 h)
- Build FilmCraft's engine and CLI on Linux (this container) and macOS (the creator's machine). Record
  build time, binary size and warm-start time. *(Building third-party code needs your go-ahead in this
  session; see §9.)*
- Import `samples/baseline/` source media through `filmcraft-cli`, then place, render and export a 10 s
  vertical clip. Probe it with ffprobe.
- Decode check on real creator media: iPhone HEVC 10-bit 4K, an Android H.264, a screen recording.
- **Gate:** headless render of a 1080×1920 H.264 that ffprobe accepts; decode works or falls back to
  proxy for every test file. Choose and write down the pinned rev.

### M1. Headless bridge: a job becomes a project (≈ 30–50 h)
- `vibe-job`: serde types and loaders, tested against the Python writers' real output (job 9278).
- `vibe-bridge import`: the full §4 mapping → `.fcproj` (one undo step, read back with `sequence.inspect`).
- `vibe-cli render <job>`: final render through the engine.
- **Gate (parity with the ffmpeg lane on the 9278 baseline):** duration equal to the EDL to the frame;
  per-frame PSNR ≥ 38 dB against `outputs/9278.final.mp4` on spine frames; captions and graphics on within
  one frame of their cue; integrated loudness within ±0.5 LU of the ffmpeg lane; `verify-final.py` passes on
  the engine's export.

### M2. Desktop shell: clean, dark, familiar (≈ 60–100 h)
- Fork `ui-egui` into `vibe-ui` and write `UPSTREAM.md`. Replace the token set with `DESIGN.md`. Remove
  brand, update prompt and splash.
- Pages instead of workspaces: **Edit · Captions · Color · Audio · Export** (§DESIGN 3).
- Edit page layout: asset rail (Media / Audio / Text / Captions / Effects / Transitions / Templates) · 9:16
  Program monitor with Source as a tab · CapCut-style **Inspector** (Video / Audio / Speed / Animation /
  Captions tabs, a ◇ keyframe toggle on every row) · timeline with V/A/caption tracks · a thin dual-timeline
  overview strip for reels.
- Keep every FilmCraft panel reachable (Effect Controls, Lumetri, mixer, scopes, Essential Sound…) behind the
  pages. Hide nothing an advanced user needs; show nothing a reel doesn't need.
- **Gate:** open the M1 project, then trim, ripple, roll, slip, razor, keyframe, grade, mix and export by hand
  with Premiere keys. Every page screenshot passes the design checklist (`DESIGN.md` §9).

### M3. Agent lane (≈ 25–40 h)
- `vibe-agent`: MCP tools = engine commands (`command_run`, `commands_list`, `inspect`) + `vibe.*` macros +
  `render_frame` (a PNG at any time, headless: what `export_frame` never did) + `render_preview` + `verify`.
- `lanes/vibe/`: `import.sh`, `export.sh`. `run.sh --lane vibe`. A new column in `LANES.md`. The ig-* skills
  gain a vibe lane section. `finalize.sh` proves the file on disk, as today.
- Archive the Premiere-only technical locks that no longer apply (keep the lane working for users who
  have Premiere).
- **Gate:** `./run.sh projects/9278 --lane vibe` produces the same final as the ffmpeg lane (M1 numbers), and
  the agent completes ig-pacing (add, move and remove a zoom) and ig-captions (re-accent a word) through MCP
  only, with read-back after each.

### M4. Short-form layer: CapCut-grade where it matters (≈ 80–140 h)
Ordered by how often the samples need them:
1. **Caption styles as track presets**, with word-timed animation: pop-in per word, active-word highlight,
   accent words in the look's second face, one-line band, safe-zone aware. Imported from
   `presets/vertical/<look>`; editable and saved back as a look.
2. **Zoom punch tool** (`Z`-drag on the monitor, or `vibe.zoomPunch` at the playhead): a face-anchored
   Scale/Position pair with the samples' ease, one undo step.
3. **Animation presets** for any clip or text: In / Out / Loop (slide-up 0.18 s, fade, pop, scale-in, hard
   cut), written as plain keyframes so they stay editable.
4. **Safe-zone overlay** for IG Reels, TikTok and Shorts UI chrome on the Program monitor.
5. **Speed:** constant, ramp presets (Montage, Hero, Bullet, Flash In/Out) and custom curves, as editable
   time-remap keyframes.
6. **Auto-reframe** of 16:9 sources into 9:16 with face tracking (reuses `workflows/_faces.py` logic, ported or
   called), producing keyframes.
7. **SFX and music browser** over `presets/vertical/default/sfx/` and the brand's library; drop on a beat
   marker.
8. **Templates** from `presets/graphics/` (app-mock, receipt, thumb-wall, comment), shown as graphics with
   editable fields. These are HyperFrames renders in M4; native graphic clips are the M6 stretch.
9. Transcript panel tuned for takes: the `review/takes.md` view (cut words bracketed) where restoring a
   bracketed word restores the frames.
- **Gate:** rebuild the 9278 v5 edit by hand in the app from the raw in under 30 minutes, and put it next to
  `samples/baseline/9278-muse-v5.mp4`.

### M5. Round trip and interchange (≈ 25–40 h)
- `vibe-bridge export`: timeline → `cuts.json` (keeps, holds, zooms from keyframes), `captions.json` and
  `captions.overrides.json`, graphics cues → `graphics-plan.json`, and A3 → `sfx-plan.json`. The agent can
  continue after a human edit, and the human can continue after the agent.
- Conflict rule: anything the user touched (`vibe.origin` differs from the file) wins over an upstream
  re-run, and is reported, not overwritten (the caption-rerun lesson).
- Out to other editors: FCP7 XML / FCPXML / OTIO through FilmCraft's interchange, tested by opening in
  Resolve (free) and Premiere.
- **Gate:** import → hand edit → export → `./run.sh --from captions` → re-import, with no lost edit.

### M6. Hardening and speed (ongoing)
- Real-media corpus (the creator's last 20 raws). Hardware decode on macOS. Proxies by default for 4K or
  10-bit sources.
- Keyboard presets: Premiere (inherited), **Resolve** and **CapCut** layouts (measured from the apps, not
  guessed).
- Performance budget: 60 fps UI on a 60 s reel timeline, scrub latency under 50 ms on proxies, export of a
  60 s reel in under 30 s on an M2 Pro.
- Packaging: a signed macOS `.app`, an AppImage.
- Stretch: native graphic clips replacing HyperFrames renders for simple cards (text, logo under word,
  ring draw), so graphics are editable as layers, not just as clips.

## 6. How the pipeline and the editor divide the work

| | Python pipeline (unchanged) | Vibe Studio |
|---|---|---|
| Transcription (WhisperX) | ✓ | shows and edits the transcript |
| Take selection, captions plan, graphics decisions, SFX plan | ✓ the agent's decisions as files | renders those files as a timeline; hand edits flow back |
| Graphics rendering (HyperFrames) | ✓ | places, trims and re-requests renders |
| Assembly, mix, export | ffmpeg lane (verification) | engine lane (delivery or refinement) |
| Verification | `verify-final.py`, contact sheet | the same scripts on its export, plus headless frame renders |

The CLAUDE.md principle holds: the scripts do the mechanical work, and the agent is the editor. The app is the
timeline both of them, and the user, hold in their hands.

## 7. Feature matrix: Premiere / Resolve / CapCut → us

✓ inherited from FilmCraft · ◐ inherited, reshaped in our surface · ★ we build · — not planned

| Feature | P | R | C | Us |
|---|:-:|:-:|:-:|---|
| Bins, source/program, 3-point editing | ✓ | ✓ | ~ | ✓ |
| Ripple / roll / slip / slide / rate stretch / razor / trim mode | ✓ | ✓ | ~ | ✓ |
| Magnetic main track + linked overlays | ~ | ~ | ✓ | ★ an Edit-page toggle (ripple on V1, sync-lock overlays) |
| Keyframes with ease/Bezier + graph | ✓ | ✓ | ✓ | ✓ engine · ◐ ◇ toggles in the Inspector |
| One context inspector | ✓ (Properties) | ~ | ✓ | ★ |
| Text-based editing | ✓ | ✓ | ✓ | ✓ engine · ★ takes view |
| Auto captions, track style presets, word animation | ✓ | ✓ | ✓ | ✓ tracks · ★ looks + word animation |
| Zoom punch, safe zones, auto-reframe | ~ | ✓ | ✓ | ★ |
| Speed ramps with presets | ✓ | ✓ | ✓ | ✓ time remap · ★ presets |
| Lumetri-style colour + scopes | ✓ | ✓✓ | ~ | ✓ |
| Node colour, Power Windows tracking | — | ✓ | — | — |
| Mixer, EQ, dynamics, loudness, ducking | ✓ | ✓ | ~ | ✓ · ★ ducking preset |
| Interchange (XML/OTIO/AAF) | ✓ | ✓ | — | ✓ |
| Agent control (MCP) | bridge | Studio | — | ✓ native · ★ vibe.* |
| Generative AI (extend, masks) | ✓ | ✓ | ✓ | — later, through the pipeline |

## 8. Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | FilmCraft is alpha (56 % "ready for real work") | Our use is narrow: one vertical A-roll, overlays, captions. M1's parity gate against the ffmpeg lane catches engine bugs before the user does; the ffmpeg lane stays the delivery fallback |
| R2 | Upstream churn breaks us | Pinned rev; bump deliberately with M1's gate as the regression test; upstream our fixes |
| R3 | Phone HEVC 10-bit decode is slow in software (their G3) | Proxies by default at import (ffmpeg CLI, already a dependency); hardware decode on macOS |
| R4 | egui redraw cost on a dense timeline | Repaint on change only; FilmCraft's perf counters; the budget in M6 |
| R5 | The forked UI drifts from upstream | Fork once and reshape deliberately; pull upstream fixes by file, noted in `UPSTREAM.md` |
| R6 | HyperFrames renders are baked pixels | They stay clips you can move and trim, with "Re-render" back through the pipeline; native graphic clips are the M6 stretch |
| R7 | Looking like Premiere invites trade-dress or asset problems | Workflow and keys are fine; artwork is not. Our own icons (Lucide, ISC licence), our own palette, no vendor assets, as FilmCraft's AGENTS.md requires |
| R8 | GUI testing in a headless container | Everything below L5 is headless; UI screenshots through the control channel (`ui.screenshot`) under Xvfb |

## 9. Decisions needed from you

1. **Approve option D** (FilmCraft engine as a pinned dependency; fork the UI; our own short-form crates).
2. **Allow building third-party code** in the session. The M0 spike compiles FilmCraft; the sandbox blocked
   that during research pending your OK.
3. **Name:** "Vibe Studio" or something else.
4. **Accent colour:** the neutral blue proposed in `DESIGN.md`, or your brand colour from `brand/brand.json`.
5. **Lane priority:** should the app become the **delivery** lane (export from the engine) or stay the
   **refinement** lane (the ffmpeg lane delivers; the app is for hand edits)? The recommendation: refinement
   first, delivery once M1's gate has held on five real jobs.
