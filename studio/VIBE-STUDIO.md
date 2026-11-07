# Vibe Studio

The vibe-editor's own video editor: a Premiere-style NLE in pure Rust, built on
[FilmCraft](https://github.com/storytold/filmcraft) (MIT OR Apache-2.0, by the ArtCraft team).
It opens anything the vibe pipeline produced as a timeline you can edit by hand. It shows what
Claude or an outside agent did to the edit, lets you ask Claude about the edit or for a change,
and exports the result.

This folder is FilmCraft, imported as a git subtree at upstream commit `c9be142` (2026-11-03), with
the changes listed below. FilmCraft's own docs (`README.md`, `docs/`, `AGENTS.md`, `CLAUDE.md`)
still describe the engine and apply to this code: never crash, exact time, everything is a command,
no Adobe assets.

## Run it

```sh
cd studio
cargo build -p filmcraft -p filmcraft-cli          # ~10 min the first time; binaries in target/debug/
../lanes/vibe/open.sh ../projects/<job>             # the job as a sequence, hand edits kept in <job>/vibe/<job>.vibeproj
../lanes/vibe/export.sh ../projects/<job> out.mp4   # headless export, captions burned in
target/debug/vibe-studio projects/<job>             # or open a job folder directly (it has a RUN.md)
```

In the app, **File ▸ Open Vibe Job…** picks a job folder.

## The Assistant: your Claude Code, inside the editor

No API key. The **Assistant** panel (the speech-bubble button in the header, or the Edit page's
right column) runs your own **Claude Code** the way you use it in a terminal. It starts
`claude` in the vibe-editor checkout, so `CLAUDE.md`, the skills (ig-reel, ig-cut, ig-show…),
`samples/` and the project's permission settings all apply, signed in with your own account. Ask
it to edit a video as you always have; the difference is that you watch it happen and can step in.

- **It sees and edits the timeline.** Vibe Studio hands the session an MCP server that is the live
  app (`vibe-studio`: `sequence_inspect`, `render_frame`, `command_run`, `ui_*`…), over a private
  control channel on a random local port with a fresh token. Reading never prompts. Every change is
  one undo step and is listed in **Activity**.
- **Prompts are buttons.** Claude Code's permission prompts become cards in the panel (Allow /
  Always allow / Deny; "Always" saves the rule as the terminal would). Its questions
  (AskUserQuestion) become option buttons, and a plan (Plan mode) shows with Approve / Keep planning.
- **Modes:** Ask (your settings decide, the rest prompts), Auto-edit (`acceptEdits`), Plan.
- **Sessions:** one Claude Code session per conversation (`--resume` if it has to restart);
  **New session** starts over; "Continue my last Claude Code session" picks up the folder's last
  terminal session (`--continue`).
- **Finding things:** `claude` is looked up on your login shell's PATH (an app opened from the
  Finder has a bare PATH), or set `VIBE_AGENT_CLAUDE`. The checkout is found above the open
  project, else from where the app started, else `VIBE_EDITOR_REPO`.
- **Scripts:** the control channel has `assistant.send {text}`, `assistant.inspect` and
  `assistant.answer {line, allow, always}`.

### From any Claude Code session (the Claude app, a terminal)

Your usual flow is unchanged: open a Claude Code session on the vibe-editor folder (in the Claude
app on your Mac or a terminal) and tell it what to make. The pipeline, skills and samples work as
before, and nothing needs Vibe Studio. With Vibe Studio set up (`lanes/vibe/setup.sh` builds it
and registers `vibe-studio` in `.mcp.json`), that session can also open the edit in the editor
(`lanes/vibe/open.sh projects/<job>`) and see and change what is open there. The `vibe-studio` MCP
server (`lanes/vibe/mcp.sh` → `vibe-studio-cli mcp --bridge vibe-studio`) finds the running app
through `~/.vibe-studio/live.json` (port and token, readable by you only, written while the app is
open and removed when it quits) each time a tool runs, so it doesn't matter which starts first.
When the app isn't open, its tools say so and how to open it. Approve the server once when Claude
Code asks. The Assistant panel's own session gets its private link and skips this one.

Codex is not wired in yet: its non-interactive mode has no equivalent of Claude Code's stream
protocol for answering permission prompts from a host app.

## What `vibe.importJob` builds

| Pipeline file | Timeline |
|---|---|
| `RUN.md` `source` | one media item; `transcript/words.json` becomes its transcript (Text panel ▸ Transcript) |
| `cuts.json` keeps | linked V1/A1 clips back to back, whole frames (no drift from the EDL) |
| `preview/framing.json` | Motion Scale/Position on every V1 clip (the ffmpeg lane's fixed camera) |
| `keep.zoom` | eased Scale/Position keyframes anchored on the face; `out` = the opening zoom-out |
| `captions.json` | one text clip per caption on V5 in the look: caption face and size at its band, accent words and keyword groups in the accent face, scale and colour (per-character styles), retypable and restylable; groups under `mute_captions` graphics and hook titles are left out (`"captions": "track"` gives a plain caption track for SRT/VTT instead) |
| `keep.hold` | a frame-hold clip of the keep's last frame, framed as the keep ended |
| `broll-plan.json` | cutaways on V2 (filled, panned, sped), windowed clips on V2 with their sound on A2, hook titles on V4 |
| `graphics-plan.json` + `renders/*.mov` | alpha clips on V3 (V4 when V3 is busy) at their cue |
| `sfx-plan.json` | SFX on A3 at their dB; the music bed on A4 from `onset_s`, at the hook level then the bed level (Volume keyframes) |
| `audio/voice-gain.json` | clip gain on every A1 clip, and a Hard Limiter on A1 at `audio.peak_dbfs` (the ffmpeg lane's `alimiter`) |

`vibe.importJob {"dir", "captions": "track"|"render"|"none"}` is an engine command like any other,
so it also runs from the CLI (`vibe-studio-cli exec vibe.importJob dir=projects/<job>`), the control
channel, MCP and the Assistant. The whole import is one undo step.

**Editing by hand.** Imported sequences are *magnetic* (Sequence ▸ Magnetic Timeline): trimming or
deleting a take ripples the captions, graphics and SFX after it and trims whatever crosses the cut,
as CapCut's main track does (FilmCraft, like Premiere, refuses such an edit). The music bed is not
sync-locked, so it stays one piece. `vibe.diffJob {"dir"}` reports what you changed against the
job's files (takes trimmed / removed / added / split, holds, captions retyped / retimed / removed /
added, graphics moved / removed / added), so the agent can keep your edits when it re-runs the
pipeline.

Not rebuilt yet: crop_top on b-roll cutaways, the captions' text glow (a drop shadow stands in),
the opening zoom's exact smoothstep (an ease stands in). Fonts come from the system: install the
look's fonts (e.g. Europa Grotesk, Tactic Sans) on the Mac, as the samples look expects.

## Changes from FilmCraft

| Area | Change | Files |
|---|---|---|
| Name and icon | "Vibe Studio" in the header, window, About, dialogs; binary `vibe-studio`; own icon (an amber V); data in its own folder (`…/Vibe Studio`, `VIBE_STUDIO_DATA_DIR`) | `apps/filmcraft/src/{main,vibe}.rs`, `apps/filmcraft/Cargo.toml`, `crates/ui-egui/src/brand.rs`, `assets/app-icon/vibe-studio-*` |
| Trademarks | the ArtCraft wordmark and Discord button are gone (ArtCraft's marks, not code-licensed); the updater is off (it would install FilmCraft over Vibe Studio) | `brand.rs`, `header.rs`, `main.rs` |
| Rebrand | every user-facing string says Vibe Studio (all 17 languages); projects are `.vibeproj` (same format as `.fcproj`: rename a FilmCraft project to open it); the CLI is `vibe-studio-cli`, the MCP server `vibe-studio` with `vibe-studio://` resources; Help and About link to vibe-editor on GitHub, and About credits FilmCraft; logs are `vibe-studio.log` | `links.rs`, `menus.rs`, `panels/dialogs.rs`, `i18n/*.tsv`, `automation/src/server.rs`, `apps/filmcraft-cli/Cargo.toml` |
| Look | the design in `../editor/docs/DESIGN.md`: neutral near-black greys, one accent, the creator's brand colour from `brand/brand.json` (`VIBE_BRAND` overrides; default amber `#FFC531`), dark text on accent fills, 4 px radii | `crates/ui-egui/src/theme.rs`, accent buttons in `panels/export_mode/*`, `panels/text.rs`, `panels/timeline.rs` |
| Header | page tabs Import · Edit · Captions · Color · Audio · Export (Edit = the `Vibe` workspace); Assistant and Export buttons | `crates/ui-egui/src/header.rs` |
| Workspace | `Vibe` (the default): assets │ Program │ Properties over the Assistant, with the timeline under the first two | `crates/ui-egui/src/dock.rs`, `state.rs`, `menus.rs` |
| Assistant | the user's Claude Code run in the checkout with this app as its MCP server; permission prompts and questions as cards; Activity | `crates/ui-egui/src/assistant.rs`, `panels/assistant.rs`, `control.rs`, `hooks.rs`; the process and the private control channel in `apps/filmcraft/src/{vibe,control_server,main}.rs` |
| Vibe jobs | `vibe.importJob`; File ▸ Open Vibe Job…; job folders on the command line | `crates/engine/src/vibe_job.rs`, `commands.rs`, `menus.rs`, `main.rs` |

Upstream crate names (`filmcraft-*`) are unchanged on purpose, so upstream merges stay small.

## Pulling upstream FilmCraft

```sh
git subtree pull --prefix=studio https://github.com/storytold/filmcraft.git main --squash
```

Conflicts land in the files in the table above. Re-run the gates afterwards: `cargo test -p
filmcraft-engine vibe_job`, `cargo test -p filmcraft-ui-egui assistant`, then
`lanes/vibe/export.sh` on a real job compared against the ffmpeg lane's final.

## Licence

FilmCraft is MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`, `ATTRIBUTION.md`, all
kept). Vibe Studio's changes are under the same terms inside `studio/`. The vibe-editor repository
around it is GPL-3.0. Apache-2.0 and MIT code can be combined into a GPL-3.0 work, and FilmCraft's
notices stay with its files.
