#!/usr/bin/env bash
# Regression: every preset renders to its golden (SSIM ≥ 0.97), and the fixture's deterministic
# artefacts (cuts.json keep ranges, caption grouping) are byte-stable across a re-run.
# Run before calling any change to presets/ or workflows/ done.
#
#   tests/regress.sh [--presets-only] [--fixture projects/<job>]
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PRESETS_ONLY=0; FIXTURE="projects/fixture-summer"
while [[ $# -gt 0 ]]; do case "$1" in --presets-only) PRESETS_ONLY=1; shift;; --fixture) FIXTURE="$2"; shift 2;; *) shift;; esac; done
fail=0
echo "== presets"
for p in presets/graphics/*/; do
  n=$(basename "$p")
  if python3 workflows/build-graphics.py --preset "$p" --golden 2>&1 | grep -E "golden ssim|FAIL"; then :; else echo "FAIL preset $n"; fail=1; fi
done
if [[ $PRESETS_ONLY -eq 0 && -f "$FIXTURE/RUN.md" && -f "$FIXTURE/transcript/words.json" ]]; then
  echo "== fixture determinism ($FIXTURE)"
  tmp=$(mktemp -d)
  cp "$FIXTURE/cuts.json" "$tmp/cuts.before.json"; cp "$FIXTURE/captions.json" "$tmp/captions.before.json"; cp "$FIXTURE/RUN.md" "$tmp/RUN.before.md"
  python3 workflows/rough-cut.py "$FIXTURE" >/dev/null
  python3 workflows/plan-captions.py "$FIXTURE" >/dev/null
  python3 - "$tmp" "$FIXTURE" <<'EOF'
import json, sys
tmp, job = sys.argv[1], sys.argv[2]
a = json.load(open(f"{tmp}/cuts.before.json")); b = json.load(open(f"{job}/cuts.json"))
ka = [(k["in"], k["out"]) for k in a["keep"]]; kb = [(k["in"], k["out"]) for k in b["keep"]]
assert ka == kb, f"EDL changed: {ka} != {kb}"
ca = [g["text"] for g in json.load(open(f"{tmp}/captions.before.json"))["groups"]]
cb = [g["text"] for g in json.load(open(f"{job}/captions.json"))["groups"]]
assert ca == cb, "caption grouping changed"
print(f"EDL identical ({len(kb)} clips) · captions identical ({len(cb)} groups)")
EOF
  # restore the zoom punches the pacing node wrote (rough-cut regenerates without them)
  cp "$tmp/cuts.before.json" "$FIXTURE/cuts.json"; cp "$tmp/captions.before.json" "$FIXTURE/captions.json"; cp "$tmp/RUN.before.md" "$FIXTURE/RUN.md"
fi
[[ $fail -eq 0 ]] && echo "regress: pass" || { echo "regress: FAIL"; exit 1; }
