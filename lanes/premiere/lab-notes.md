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
