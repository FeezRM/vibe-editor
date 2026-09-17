#!/usr/bin/env python3
"""Node 06a — measured voice gain. preview/spine.mp4 → audio/voice-gain.json

Measures integrated loudness and true peak with ffmpeg loudnorm (measure pass only) and computes
the gain to audio.voice_lufs; the lane applies gain + a limiter at audio.peak_dbfs. Measured, never
a fixed number; re-run after any re-replay.

Usage: python workflows/voice-gain.py <job>
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, die  # noqa: E402

job = Job(sys.argv[1])
job.require("audio")
A = job.numbers["audio"]
src = job.p("preview", "spine.mp4")
if not src.exists():
    die("preview/spine.mp4 missing — run lanes/ffmpeg/assemble.py --stage spine")
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={A['voice_lufs']}:TP={A['peak_dbfs']}:LRA=11:print_format=json",
                    "-f", "null", "-"], capture_output=True, text=True)
m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
if not m:
    die(f"loudnorm measurement failed:\n{r.stderr[-800:]}")
meas = json.loads(m.group(0))
in_i, in_tp = float(meas["input_i"]), float(meas["input_tp"])
gain = A["voice_lufs"] - in_i
out = {"measured_lufs": in_i, "measured_tp": in_tp, "target_lufs": A["voice_lufs"], "peak_dbfs": A["peak_dbfs"],
       "gain_db": round(gain, 2), "lra": float(meas.get("input_lra", 0)), "limiter_engaged": in_tp + gain > A["peak_dbfs"]}
job.write_json(out, "audio", "voice-gain.json")
job.note("audio", f"voice measured {in_i:.1f} LUFS / TP {in_tp:.1f} dB → gain {gain:+.1f} dB (limiter {'on' if out['limiter_engaged'] else 'idle'})")
print(f"voice-gain: {in_i:.1f} LUFS, TP {in_tp:.1f} → gain {gain:+.1f} dB to {A['voice_lufs']} LUFS (limiter {'engaged' if out['limiter_engaged'] else 'idle'})")
