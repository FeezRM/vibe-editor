#!/usr/bin/env bash
# Promote the lane's render to outputs/<job>.final.mp4 and drop a copy in ~/Downloads.
# Never reports an export that is not on disk and newer than the run start.
#
#   ./finalize.sh <job-dir> [--lane ffmpeg|premiere]
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB=""; LANE="ffmpeg"
while [[ $# -gt 0 ]]; do case "$1" in --lane) LANE="$2"; shift 2;; *) JOB="$1"; shift;; esac; done
JOB="$(cd "$JOB" && (pwd -W 2>/dev/null || pwd))"
SLUG="$(grep -E '^job:' "$JOB/RUN.md" | awk '{print $2}')"
OUT="$JOB/outputs/$SLUG.final.mp4"
T0=$(date +%s)
cd "$REPO"
if [[ "$LANE" == "premiere" ]]; then
  if node lanes/premiere/export.mjs "$JOB" "$OUT"; then :; else
    echo "premiere export failed — rendering on the ffmpeg lane instead" >&2; LANE=ffmpeg
  fi
fi
if [[ "$LANE" == "ffmpeg" ]]; then
  python3 lanes/ffmpeg/assemble.py "$JOB" --stage final --quiet --out "$OUT"
fi
[[ -f "$OUT" ]] || { echo "FAIL: no final on disk at $OUT" >&2; exit 1; }
MT=$(python3 -c "import os,sys; print(int(os.stat(sys.argv[1]).st_mtime))" "$OUT")   # portable (BSD/GNU stat differ)
[[ $MT -ge $T0 ]] || { echo "FAIL: $OUT is older than this run" >&2; exit 1; }
cp -f "$OUT" "$HOME/Downloads/$SLUG.final.mp4" 2>/dev/null || true
python3 - "$JOB" "$OUT" "$LANE" <<'EOF'
import sys; sys.path.insert(0, "workflows"); from _lib import Job
j = Job(sys.argv[1]); j.mark("export", "done", out=f"outputs/{sys.argv[2].split('/')[-1]}", lane=sys.argv[3])
j.note("export", f"final on {sys.argv[3]} lane → {sys.argv[2]} (+ ~/Downloads)")
EOF
echo "final: $OUT  ($(du -h "$OUT" | cut -f1), lane $LANE)"
