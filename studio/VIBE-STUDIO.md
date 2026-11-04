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
../lanes/vibe/open.sh ../projects/<job>             # the job as a sequence, hand edits kept in <job>/vibe/<job>.fcproj
../lanes/vibe/export.sh ../projects/<job> out.mp4   # headless export, captions burned in
target/debug/vibe-studio projects/<job>             # or open a job folder directly (it has a RUN.md)
```

In the app, **File ▸ Open Vibe Job…** picks a job folder. **Assistant** (the speech-bubble button
in the header, or the panel in the Edit page's right column) has two tabs:

- **Ask**: talk to Claude (`claude-opus-5-5`) about the edit. Claude inspects the timeline, finds and
  runs editor commands, and looks at rendered frames. Each command it runs is listed under its
  answer and is one undo step. It uses `ANTHROPIC_API_KEY` (or `ANTHROPIC_AUTH_TOKEN`) from the
  environment, or a key pasted into the panel, which is kept in memory only. Requests use the
  server-side refusal fallback (`fallbacks: "default"`).
- **Activity**: every command Claude ran, and every command an outside agent sent over the
  control channel or MCP bridge, newest first, with its result. Claude Code running the vibe
  pipeline connects with `filmcraft-cli mcp --bridge 127.0.0.1:9876` and the same
  `FILMCRAFT_CONTROL_TOKEN`.

## What `vibe.importJob` builds

| Pipeline file | Timeline |
|---|---|
| `RUN.md` `source` | one media item; `transcript/words.json` becomes its transcript (Text panel ▸ Transcript) |
| `cuts.json` keeps | linked V1/A1 clips back to back, whole frames (no drift from the EDL) |
| `preview/framing.json` | Motion Scale/Position on every V1 clip (the ffmpeg lane's fixed camera) |
| `keep.zoom` | eased Scale/Position keyframes anchored on the face; `out` = the opening zoom-out |
| `captions.json` | caption track `Captions` (C1), text and timing editable, styled from the look; groups under `mute_captions` graphics are left out |
| `graphics-plan.json` + `renders/*.mov` | alpha clips on V3 (V4 when V3 is busy) at their cue |
| `sfx-plan.json` | SFX on A3 at their dB, the music bed on A4 |
| `audio/voice-gain.json` | clip gain on every A1 clip |

`vibe.importJob {"dir", "captions": "track"|"render"|"none"}` is an engine command like any other,
so it also runs from the CLI (`filmcraft-cli exec vibe.importJob dir=projects/<job>`), the control
channel, MCP and the Assistant. The whole import is one undo step.

Not rebuilt yet: frozen holds (`keep.hold`), per-word caption accents (the look's second face and
colour; the accent word is upper-cased when the look sets `accent_case: uppercase`), b-roll from
`broll-plan.json`. See `../editor/docs/PLAN.md` M4.

## Changes from FilmCraft

| Area | Change | Files |
|---|---|---|
| Name and icon | "Vibe Studio" in the header, window, About, dialogs; binary `vibe-studio`; own icon (an amber V); data in its own folder (`…/Vibe Studio`, `VIBE_STUDIO_DATA_DIR`) | `apps/filmcraft/src/{main,vibe}.rs`, `apps/filmcraft/Cargo.toml`, `crates/ui-egui/src/brand.rs`, `assets/app-icon/vibe-studio-*` |
| Trademarks | the ArtCraft wordmark and Discord button are gone (ArtCraft's marks, not code-licensed); the updater is off (it would install FilmCraft over Vibe Studio) | `brand.rs`, `header.rs`, `main.rs` |
| Look | the design in `../editor/docs/DESIGN.md`: neutral near-black greys, one accent, the creator's brand colour from `brand/brand.json` (`VIBE_BRAND` overrides; default amber `#FFC531`), dark text on accent fills, 4 px radii | `crates/ui-egui/src/theme.rs`, accent buttons in `panels/export_mode/*`, `panels/text.rs`, `panels/timeline.rs` |
| Header | page tabs Import · Edit · Captions · Color · Audio · Export (Edit = the `Vibe` workspace); Assistant and Export buttons | `crates/ui-egui/src/header.rs` |
| Workspace | `Vibe` (the default): assets │ Program │ Properties over the Assistant, with the timeline under the first two | `crates/ui-egui/src/dock.rs`, `state.rs`, `menus.rs` |
| Assistant | Ask Claude (tool use over the command registry, frame look) and Activity (Claude's and agents' commands) | `crates/ui-egui/src/assistant.rs`, `panels/assistant.rs`, `control.rs`, `hooks.rs`; HTTPS in `apps/filmcraft/src/vibe.rs` (ureq + rustls/RustCrypto, as `crates/speech`) |
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
