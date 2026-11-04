#!/usr/bin/env bash
# Open a job in Vibe Studio to edit by hand (and ask Claude in the Assistant panel).
#
#   lanes/vibe/open.sh <job-dir> [--fresh] [--port 9876]
#
# The first open builds <job>/vibe/<slug>.fcproj from the pipeline's files (vibe.importJob); later
# opens reuse it, so hand edits stay. --fresh rebuilds it from the files (hand edits are lost).
# The app listens for agents on --port (Claude Code: `filmcraft-cli mcp --bridge 127.0.0.1:<port>`
# with the same FILMCRAFT_CONTROL_TOKEN); what they do shows in the Assistant ▸ Activity tab.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_studio.sh"
JOB=""; FRESH=""; PORT=9876
while [[ $# -gt 0 ]]; do case "$1" in --fresh) FRESH=--fresh; shift;; --port) PORT="$2"; shift 2;; *) JOB="$1"; shift;; esac; done
[[ -n "$JOB" && -f "$JOB/RUN.md" ]] || { echo "usage: lanes/vibe/open.sh <job-dir> [--fresh] [--port N]" >&2; exit 64; }
JOB="$(cd "$JOB" && pwd)"
PROJ="$(ensure_project "$JOB" "$FRESH")"
APP="$(pick_bin vibe-studio)"
: "${FILMCRAFT_CONTROL_TOKEN:=$(python3 -c 'import secrets; print(secrets.token_hex(32))')}"
export FILMCRAFT_CONTROL_TOKEN
echo "Vibe Studio: $PROJ (agents: 127.0.0.1:$PORT; the token is in this shell's FILMCRAFT_CONTROL_TOKEN)"
cd "$REPO"   # brand/brand.json is found from here
exec "$APP" --control "$PORT" "$PROJ"
