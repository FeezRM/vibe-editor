#!/usr/bin/env bash
# MCP server for any Claude Code session in the vibe-editor folder (the Claude app, a terminal):
# the open Vibe Studio window, found through ~/.vibe-studio/live.json each time a tool runs, so it
# works whether Vibe Studio or the session started first. Registered in .mcp.json by
# lanes/vibe/setup.sh. When Vibe Studio isn't open, its tools say so and how to open it.
set -euo pipefail
STUDIO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/studio"
for b in "$STUDIO/target/release/vibe-studio-cli" "$STUDIO/target/debug/vibe-studio-cli"; do
  [[ -x "$b" ]] && exec "$b" mcp --bridge vibe-studio
done
echo "vibe-studio MCP: Vibe Studio isn't built yet — run lanes/vibe/setup.sh" >&2
exit 1
