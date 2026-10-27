# lanes/premiere — lab notes and locks

- **Bridge:** `bridge.mjs` is a dependency-free MCP client (JSON-RPC 2.0 over stdio) that spawns
  `vendor/adobe-premiere-pro-mcp/dist/index.js` with the env from `.mcp.json`. `Bridge.connect()`
  runs `verify_premiere_connection` first and exits 2 with the CEP checklist when it fails.
- **Replay, never a flat render:** `replay-edl.mjs` creates `<job>__CUT` with
  `create_sequence_from_clips` (inherits the raw's 1080×1920 and fps), lifts the auto-placed full
  clip, places every keep range with `add_to_timeline_batch` (`sourceInPoint`/`sourceOutPoint`), and
  reads every clip back with `get_clip_properties` into `premiere/replay-verify.json`. The gate is the
  read-back count and start times within 1.5 frames — not the tool's `success`.
- **Track architecture** V1 A-roll · V2 B-roll · V3 primary graphics · V4 secondary · A1 voice ·
  A2 alt · A3/A4 SFX · A5 music — created with `add_track`, confirmed with `list_sequence_tracks`.
- **Never** scale or reposition a rendered graphic in Premiere; fix the plan and re-render.
- **Export:** `export.mjs` calls `export_sequence` and proves the file exists and is newer than the
  call; otherwise exit 1 and `finalize.sh` renders on the ffmpeg lane.
- **Status on this Mac (2026-09-12):** Premiere Pro 2022 installed; bridge panel not started;
  every script here is ⚠️ unvalidated. Start the panel (Window → Extensions → MCP Bridge (CEP) →
  Temp Directory `/tmp/premiere-mcp-bridge` → Start Bridge) and run
  `node lanes/premiere/replay-edl.mjs projects/<job>` to validate.
- **Not written yet:** `place-graphics.mjs`, `place-audio.mjs`, zoom keyframes — ✋ in `LANES.md`.
- **Validated on Windows, 2026-09-20 (Premiere 25.3, server 1.2.8):** `replay-edl.mjs` and the new
  `place-layers.mjs` built `9028-reel__CUT` end to end; the program monitor matched the ffmpeg final at
  4.1 / 9.8 / 18.8 / 21.6 s. Findings, each now handled in the scripts:
  - `verify_premiere_connection` keys on `bridge-heartbeat.json`; a panel running pre-1.2.8 JavaScript in memory
    never writes it while commands still round-trip → `Bridge.connect()` falls back to a real read-back
    (`list_sequences`). Reload the panel after updating `cep-plugin/`.
  - Server ≥ 1.2 wraps results as `{success, tool, data}` → `Bridge.call` flattens `data`.
  - `create_sequence_from_clips` inherits the raw's size (2160×3840 here) → `set_sequence_settings` to the preset canvas.
  - Clips placed by script are **not** re-fit: a 4K source sits at 100 % (2× punch-in) → `set_clip_properties {scale: canvas/source}`.
    `get_clip_properties` returns `motion.scale: true` (a boolean), so scale cannot be read back — PrintWindow is the check.
  - A computed start of 574/30 s landed one frame late (a black flash); the previous clip's Premiere-reported `endTime`
    round-trips exactly → clips are placed sequentially at that value, source in/out frame-quantised.
  - `RUN.md` may be CRLF on Windows → `readJob` normalises.
- **Captions "gone" (2026-09-20, second pass):** two causes, both now handled. (1) `_hf.unique_out` re-used
  `renders/captions.mov` after the old file was pruned — Premiere still referenced that name, so the clip went
  dead. Render names now come from `renders/.seq` and are never reused within a job; nothing is pruned on the
  premiere lane. (2) V2's track output (the eye) was off — every read-back still said "found". `place-layers.mjs`
  now calls `toggle_track_visibility(visible:true)` on V2–V4 every run; the pixel check is PrintWindow.

