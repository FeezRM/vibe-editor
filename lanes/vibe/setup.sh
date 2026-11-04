#!/usr/bin/env bash
# Build Vibe Studio and register its MCP server for this folder, so a Claude Code session opened
# here (the Claude app on your Mac, or a terminal) can see and change the edit open in Vibe Studio.
#
#   lanes/vibe/setup.sh [--dev] [--no-build]
#
#   --dev       a dev build (quicker to build, slower to play back) instead of release
#   --no-build  only register the MCP server
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROFILE=release; BUILD=1
for a in "$@"; do case "$a" in --dev) PROFILE=dev;; --no-build) BUILD=0;; *) echo "unknown option $a" >&2; exit 64;; esac; done

if [[ $BUILD == 1 ]]; then
  command -v cargo >/dev/null || { echo "Rust isn't installed: get it from https://rustup.rs, then run this again." >&2; exit 1; }
  echo "==> Building Vibe Studio ($PROFILE; the first build takes 10–30 min)"
  (cd "$REPO/studio" && cargo build --profile "$PROFILE" -p filmcraft -p filmcraft-cli)
fi

echo "==> Registering the vibe-studio MCP server in .mcp.json"
python3 - "$REPO/.mcp.json" "$REPO/lanes/vibe/mcp.sh" <<'PY'
import json, os, shutil, sys
target, entry = sys.argv[1], sys.argv[2]
config = {}
if os.path.exists(target):
    raw = open(target, encoding="utf-8").read().strip()
    if raw:
        try:
            config = json.loads(raw)
        except ValueError:
            shutil.copyfile(target, target + ".bak")
            print(f"  ! .mcp.json was not valid JSON — backed up to {target}.bak")
config.setdefault("mcpServers", {})["vibe-studio"] = {"command": entry, "args": []}
with open(target, "w", encoding="utf-8") as f:
    f.write(json.dumps(config, indent=2) + "\n")
print('  ✓ .mcp.json has the "vibe-studio" server (approve it once when Claude Code asks)')
PY
echo "Done. Open a job: lanes/vibe/open.sh projects/<job>"
