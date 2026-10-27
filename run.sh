#!/usr/bin/env bash
# One-shot entry. Runs the nodes in order, stops at the first failing gate, prints the gate verbatim.
#
#   ./run.sh <job-dir> [--lane ffmpeg|premiere] [--tier basic|premium] [--from NODE] [--to NODE] [--no-auto-fix]
#
# Nodes: transcript rough_cut captions graphics audio pacing export
# The graphics node: (draft-plan if no plan) → validate → face-frame → build → qa → fix-plan, ≤3 rounds.
# An agent in the loop authors graphics-plan.json before this script reaches `graphics` (run --to captions
# first, plan with real material, then run --from graphics). Without an agent the deterministic drafter
# and fixer converge on a defect-free basic-tier edit.
set -euo pipefail
export PYTHONUTF8=1   # review listings print "└"/"→"; a logged run on a cp1252 console crashed on them
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=python3
JOB=""; LANE=""; FROM="transcript"; TO="export"; AUTOFIX=1; MAX_ROUNDS=3
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lane) LANE="$2"; shift 2;;
    --tier) TIER="$2"; shift 2;;
    --from) FROM="$2"; shift 2;;
    --to) TO="$2"; shift 2;;
    --no-auto-fix) AUTOFIX=0; shift;;
    -*) echo "unknown flag $1" >&2; exit 64;;
    *) JOB="$1"; shift;;
  esac
done
[[ -n "$JOB" && -f "$JOB/RUN.md" ]] || { echo "usage: run.sh <job-dir> (create one with workflows/new-job.py)" >&2; exit 64; }
JOB="$(cd "$JOB" && (pwd -W 2>/dev/null || pwd))"   # -W: a Windows path Git Bash's python can open
[[ -n "$LANE" ]] || LANE="$(grep -E '^lane:' "$JOB/RUN.md" | awk '{print $2}')"
ORDER=(transcript rough_cut captions graphics audio pacing export)
idx() { local i; for i in "${!ORDER[@]}"; do [[ "${ORDER[$i]}" == "$1" ]] && { echo "$i"; return; }; done; echo -1; }
FROM_I=$(idx "$FROM"); TO_I=$(idx "$TO")
[[ $FROM_I -ge 0 && $TO_I -ge 0 ]] || { echo "bad --from/--to" >&2; exit 64; }
T0=$(date +%s)
log() { printf '\n\033[1m== %s\033[0m  (%ss)\n' "$1" "$(( $(date +%s) - T0 ))"; }
run_node() { [[ $(idx "$1") -ge $FROM_I && $(idx "$1") -le $TO_I ]]; }
cd "$REPO"

if run_node transcript; then
  log transcript
  $PY workflows/transcribe.py "$JOB"
  $PY workflows/validate-transcript.py "$JOB"
fi
if run_node rough_cut; then
  log rough_cut
  $PY workflows/rough-cut.py "$JOB" --review
  $PY workflows/remap-plan.py "$JOB"   # an existing graphics plan follows the new EDL (cuts.prev.json → cuts.json)
  $PY workflows/validate-edl.py "$JOB"
  $PY lanes/ffmpeg/assemble.py "$JOB" --stage spine --quiet
  read -r SIL_DB SIL_S < <($PY -c "import sys; sys.path.insert(0,'workflows'); from _lib import Job; a=Job(sys.argv[1]).numbers['audio']; print(a['silence_db'], a['silence_max_s'])" "$JOB")
  [[ -n "$SIL_DB" && -n "$SIL_S" ]] || { echo "FAIL: could not read audio.silence_db / silence_max_s" >&2; exit 1; }
  # a silence inside an authored hold (cuts.json keep.hold — b-roll audio plays there) is not dead air
  n=$(ffmpeg -i "$JOB/preview/spine.mp4" -af "silencedetect=n=${SIL_DB}dB:d=${SIL_S}" -f null - 2>&1 | $PY -c "
import re, sys; sys.path.insert(0, 'workflows'); from _lib import Job, Timeline
h = Timeline(Job(sys.argv[1]).read_json('cuts.json')).holds(); t = sys.stdin.read()
ss = [float(x) for x in re.findall(r'silence_start: (-?[0-9.]+)', t)]; ee = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', t)]
ee += [1e9] * (len(ss) - len(ee))
print(sum(1 for s, e in zip(ss, ee) if not any(a - 0.6 <= s and e <= b + 0.6 for a, b in h)))" "$JOB")
  echo "spine silences ≥ threshold: $n (holds exempt)"
  [[ "$n" == "0" ]] || { echo "FAIL: dead air survived the cut" >&2; exit 1; }
  $PY workflows/check-joins.py "$JOB" || { echo "FAIL: whitespace in the cut (cut.join_gap_max_s / pause_gate_s)" >&2; exit 1; }
  if [[ "$LANE" == "premiere" ]]; then
    node lanes/premiere/replay-edl.mjs "$JOB" || { echo "premiere lane unavailable — continuing on ffmpeg lane"; LANE=ffmpeg; sed -i.bak 's/^lane: premiere/lane: ffmpeg/' "$JOB/RUN.md" && rm -f "$JOB/RUN.md.bak"; }
  fi
fi
if run_node captions; then
  log captions
  [[ -f "$JOB/preview/spine.mp4" ]] || $PY lanes/ffmpeg/assemble.py "$JOB" --stage spine --quiet
  $PY workflows/build-broll.py "$JOB"                  # windowed b-roll (box/title) → renders/broll/*.mov
  $PY workflows/transcribe.py "$JOB" --spine          # words in timeline time — what the viewer hears
  $PY workflows/verify-cut.py "$JOB"                   # the cut says every kept word once: nothing clipped, nothing doubled
  $PY workflows/plan-captions.py "$JOB"
  $PY workflows/build-captions.py "$JOB"
  $PY lanes/ffmpeg/assemble.py "$JOB" --stage captions --quiet
  $PY workflows/measure.py "$JOB/preview/captions.mp4" "$($PY -c "import json;g=json.load(open('$JOB/captions.json'))['groups'];print(','.join(f\"{(x['s']+x['e'])/2:.2f}\" for x in g[1:40:12]))")" | grep -E "cap|centre" || true
fi
if run_node graphics; then
  log graphics
  [[ -f "$JOB/graphics-plan.json" ]] || $PY workflows/draft-plan.py "$JOB"
  round=1; ok=0
  while [[ $round -le $MAX_ROUNDS ]]; do
    echo "-- graphics round $round"
    $PY workflows/validate-plan.py "$JOB"
    $PY workflows/face-frame.py "$JOB" >/dev/null
    $PY workflows/build-graphics.py "$JOB" 2>&1 | grep -E "^  g|build-graphics|FAIL|Error" || true
    if $PY workflows/graphics-qa.py "$JOB" --round "$round"; then ok=1; break; fi
    if [[ $AUTOFIX -eq 1 ]]; then $PY workflows/fix-plan.py "$JOB" "review/qa-round-$round.json"; else break; fi
    round=$((round+1))
  done
  if [[ $ok -eq 1 ]]; then
    $PY workflows/build-captions.py "$JOB" --keep-downstream | grep -E "muted|build-captions" || true   # apply mute windows
    $PY - "$JOB" "$round" <<'EOF'
import sys; sys.path.insert(0, "workflows"); from _lib import Job
j = Job(sys.argv[1]); j.mark("graphics", "done", out="graphics-plan.json", rounds=int(sys.argv[2]))
EOF
  else
    $PY - "$JOB" "$round" <<'EOF'
import sys; sys.path.insert(0, "workflows"); from _lib import Job
j = Job(sys.argv[1]); j.mark("graphics", "blocked", rounds=int(sys.argv[2])); j.note("graphics", "blocked: defects remain after the review loop — see review/qa-round-*.json")
EOF
    echo "FAIL: graphics blocked after $MAX_ROUNDS rounds" >&2; exit 1
  fi
  $PY lanes/ffmpeg/assemble.py "$JOB" --stage graphics --quiet
fi
if run_node audio; then
  log audio
  $PY workflows/voice-gain.py "$JOB"
  $PY workflows/sfx-plan.py "$JOB" | head -3
  $PY - "$JOB" <<'EOF'
import sys; sys.path.insert(0, "workflows"); from _lib import Job
Job(sys.argv[1]).mark("audio", "done", out="sfx-plan.json")
EOF
  $PY lanes/ffmpeg/assemble.py "$JOB" --stage audio --quiet
  if [[ "$LANE" == "premiere" ]]; then
    node lanes/premiere/place-layers.mjs "$JOB" || echo "premiere lane: overlays/gain not placed — see premiere/layers-verify.json (ffmpeg lane continues)"
  fi
fi
if run_node pacing; then
  log pacing
  $PY workflows/pacing-audit.py "$JOB" --fix
  $PY lanes/ffmpeg/assemble.py "$JOB" --stage spine --quiet   # zoom punches live in the EDL
  $PY workflows/match-cuts.py "$JOB"   # measured on the spine: trims each cut to the same face size
  $PY workflows/check-framing.py "$JOB" || { echo "FAIL: framing / zoom punches off the face" >&2; exit 1; }
fi
if run_node export; then
  log export
  ./finalize.sh "$JOB" --lane "$LANE"
  $PY workflows/verify-final.py "$JOB"
fi
log done
