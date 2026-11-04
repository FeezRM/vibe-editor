#!/usr/bin/env bash
# Export a job's Vibe Studio project (hand edits included) to an MP4, headless.
#
#   lanes/vibe/export.sh <job-dir> <out.mp4> [--fresh] [--preset "Social Vertical 1080×1920"]
#
# Captions are burned in. The default preset keeps the mix as edited (voice-gain.json sets the
# A1 clip gain); the TikTok / Instagram Reels / YouTube Shorts presets normalise to −14 LUFS.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_studio.sh"
JOB=""; OUT=""; FRESH=""; PRESET="Social Vertical 1080×1920"
while [[ $# -gt 0 ]]; do
  case "$1" in --fresh) FRESH=--fresh; shift;; --preset) PRESET="$2"; shift 2;; *) if [[ -z "$JOB" ]]; then JOB="$1"; else OUT="$1"; fi; shift;; esac
done
[[ -n "$JOB" && -n "$OUT" && -f "$JOB/RUN.md" ]] || { echo "usage: lanes/vibe/export.sh <job-dir> <out.mp4> [--fresh] [--preset name]" >&2; exit 64; }
JOB="$(cd "$JOB" && pwd)"
PROJ="$(ensure_project "$JOB" "$FRESH")"
CLI="$(pick_bin filmcraft-cli)"
mkdir -p "$(dirname "$OUT")"
script="$(mktemp)"
python3 - "$OUT" "$PRESET" > "$script" <<'PY'
import json, sys
print(json.dumps({"id": "file.exportMedia", "params": {"path": sys.argv[1], "preset": sys.argv[2], "burnCaptions": True}}))
PY
"$CLI" --project "$PROJ" run "$script" >&2
rm -f "$script"
[[ -f "$OUT" ]] || { echo "FAIL: no export at $OUT" >&2; exit 1; }
echo "$OUT"
