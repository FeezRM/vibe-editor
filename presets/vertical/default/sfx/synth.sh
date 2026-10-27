#!/usr/bin/env bash
# Rebuild the default SFX pack: short, tactile, synthesised with ffmpeg (no samples, no licences).
# *.wav is gitignored, so a fresh clone runs this once; a creator's own file with the same name wins —
# existing files are never overwritten unless --force.
#   presets/vertical/default/sfx/synth.sh [--force]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
FORCE=0; [[ "${1:-}" == "--force" ]] && FORCE=1
mk() {  # name duration expression [extra -af filters]
  local f="$1.wav"
  [[ -f "$f" && $FORCE -eq 0 ]] && { echo "keep $f"; return; }
  ffmpeg -v error -y -f lavfi -i "aevalsrc='$3':s=48000:d=$2" -af "${4:-anull},alimiter=limit=0.7,afade=t=out:st=$(python -c "print(max(0,$2-0.02))"):d=0.02" -ac 1 -c:a pcm_s16le "$f"
  echo "made $f"
}
mk pop     0.14 "sin(2*PI*(300*t+10*(1-exp(-60*t))))*exp(-38*t)"
mk click   0.04 "(random(0)*2-1)*exp(-500*t)" "highpass=f=1800"
mk tick    0.06 "sin(2*PI*2200*t)*exp(-110*t)"
mk ding    0.90 "(sin(2*PI*1320*t)+0.45*sin(2*PI*2640*t)+0.2*sin(2*PI*3960*t))*exp(-5*t)*0.6"
mk whoosh  0.38 "(random(0)*2-1)*pow(sin(PI*t/0.38),2)" "highpass=f=350,lowpass=f=2600"
mk slide   0.22 "(random(0)*2-1)*pow(sin(PI*t/0.22),2)" "highpass=f=900,lowpass=f=5000"
mk shutter 0.12 "(random(0)*2-1)*(exp(-400*t)+0.8*exp(-400*abs(t-0.065))*gte(t,0.065))" "highpass=f=1200"
mk wrong   0.36 "(sgn(sin(2*PI*140*t))+sgn(sin(2*PI*147*t)))*0.3*exp(-6*t)" "lowpass=f=1800"
mk riser   0.80 "(0.6*sin(2*PI*(200*t+625*t*t))+0.4*(random(0)*2-1))*pow(t/0.8,2)" "highpass=f=200,lowpass=f=6000"
