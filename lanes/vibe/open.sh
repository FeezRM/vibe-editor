#!/usr/bin/env bash
# Open a job in Vibe Studio to edit by hand, and return (the app keeps running).
#
#   lanes/vibe/open.sh <job-dir> [--fresh]
#
# The first open builds <job>/vibe/<slug>.vibeproj from the pipeline's files (vibe.importJob); later
# opens reuse it, so hand edits stay. --fresh rebuilds it from the files (hand edits are lost).
# While the app is open, any Claude Code session in this folder (the Claude app, a terminal) reaches
# it through the vibe-studio MCP server (.mcp.json, lanes/vibe/setup.sh), and its own Assistant panel
# runs Claude Code too. Every change an agent makes shows in Assistant ▸ Activity.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_studio.sh"
JOB=""; FRESH=""
while [[ $# -gt 0 ]]; do case "$1" in --fresh) FRESH=--fresh; shift;; *) JOB="$1"; shift;; esac; done
[[ -n "$JOB" && -f "$JOB/RUN.md" ]] || { echo "usage: lanes/vibe/open.sh <job-dir> [--fresh]" >&2; exit 64; }
JOB="$(cd "$JOB" && pwd)"
PROJ="$(ensure_project "$JOB" "$FRESH")"
APP="$(pick_bin vibe-studio)"
cd "$REPO"   # brand/brand.json and the checkout are found from here
nohup "$APP" "$PROJ" >/dev/null 2>&1 &
disown || true
echo "Vibe Studio is opening $PROJ"
