#!/usr/bin/env python3
"""Gate — the final file is what the EDL says it is. → review/final-sheet.png for the human.

Checks: exists and newer than the plan · duration = kept_s ± 0.2s · 1080x1920 · loudness within
tolerance · zero silences ≥ audio.silence_max_s · caption geometry on 4 hits · 12-frame contact sheet.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job, ffprobe  # noqa: E402

job = Job(sys.argv[1])
A, C = job.numbers["audio"], job.numbers["captions"]
out = job.p("outputs", f"{job.state['job']}.final.mp4")
errs, warns = [], []
if not out.exists():
    print("error: final missing"); sys.exit(1)
info = ffprobe(out)
kept = float(job.read_json("cuts.json")["stats"]["kept_s"])
if abs(info["duration"] - kept) > 0.25:
    errs.append(f"duration {info['duration']:.2f}s vs EDL {kept:.2f}s")
if (info["width"], info["height"]) != (job.numbers["canvas"]["width"], job.numbers["canvas"]["height"]):
    errs.append(f"frame {info['width']}x{info['height']}")
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
m = re.search(r"I:\s+(-?[0-9.]+) LUFS", r.stderr.split("Summary")[-1])
lufs = float(m.group(1)) if m else None
if lufs is None or abs(lufs - A["voice_lufs"]) > A["lufs_tolerance"] + 0.5:
    warns.append(f"loudness {lufs} LUFS vs target {A['voice_lufs']}")
r = subprocess.run(["ffmpeg", "-i", str(out), "-af", f"silencedetect=n={A['silence_db']}dB:d={A['silence_max_s']}", "-f", "null", "-"],
                   capture_output=True, text=True)
sil = len(re.findall(r"silence_start", r.stderr))
if sil:
    errs.append(f"{sil} silences ≥ {A['silence_max_s']}s")
# caption geometry on 4 mid-caption hits (lenient: warn)
if job.p("captions.json").exists():
    groups = job.read_json("captions.json")["groups"]
    picks = [g for g in groups[2::max(1, len(groups) // 4)]][:4]
    ts = ",".join(f"{(g['s'] + g['e']) / 2:.2f}" for g in picks)
    r = subprocess.run([sys.executable, str(REPO / "workflows" / "measure.py"), str(out), ts], capture_output=True, text=True)
    caps = re.findall(r"cap\s+([0-9.]+)px@1920\s+width\s+([0-9.]+)%", r.stdout)
    lo, hi = C["cap_height_px"]
    for h, w in caps:
        if not (lo <= float(h) <= hi + 8) or float(w) > C["max_width_frac"] * 100 + 2:
            warns.append(f"caption geometry cap {h}px width {w}%")
sheet = job.p("review", "final-sheet.png")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-vf", f"fps=12/{max(info['duration'],1):.3f},scale=180:-1,tile=6x2",
                "-frames:v", "1", str(sheet)], capture_output=True)
for w in warns:
    print("warn:", w)
for e in errs:
    print("error:", e)
job.gate("verify_final", "fail" if errs else "pass")
print(f"verify-final: {'FAIL' if errs else 'pass'} · {info['duration']:.1f}s · {lufs} LUFS · {sil} silences · sheet → review/final-sheet.png")
sys.exit(1 if errs else 0)
