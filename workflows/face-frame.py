#!/usr/bin/env python3
"""Face / chin bbox per graphic cue, from the spine (timeline time). → review/faces.json

Uses OpenCV's bundled Haar cascade (no model download). Reports the largest face at cue+0.3s and at
cue+duration/2 and takes the union; falls back to the previous cue's face when none is found (a
turned head), and to a centred default when nothing was ever found.

Usage: python workflows/face-frame.py <job> [--times 1.0,2.5]  (times = timeline seconds; default = every plan cue)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--times", default=None)
a = ap.parse_args()
job = Job(a.job)
spine = job.p("preview", "spine.mp4")
if not spine.exists():
    sys.exit("preview/spine.mp4 missing — run lanes/ffmpeg/assemble.py --stage spine first")
W, H = job.numbers["canvas"]["width"], job.numbers["canvas"]["height"]
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def frame_at(t: float):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(spine), "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True)
    arr = np.frombuffer(r.stdout, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR) if arr.size else None


def face_at(t: float):
    img = frame_at(t)
    if img is None:
        return None
    small = cv2.resize(img, (W // 3, H // 3))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    faces = casc.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return {"x": int(x * 3), "y": int(y * 3), "w": int(w * 3), "h": int(h * 3)}


if a.times:
    items = [(f"t{t}", float(t), 0.0) for t in a.times.split(",")]
else:
    plan = job.read_json("graphics-plan.json")
    items = [(g["id"], g["cue"], g["duration"]) for g in plan["graphics"]]

out = {}
last = None
for gid, cue, dur in items:
    cands = [face_at(cue + 0.3)]
    if dur > 1.0:
        cands.append(face_at(cue + dur / 2))
    cands = [c for c in cands if c]
    if cands:
        x0 = min(c["x"] for c in cands); y0 = min(c["y"] for c in cands)
        x1 = max(c["x"] + c["w"] for c in cands); y1 = max(c["y"] + c["h"] for c in cands)
        f = {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "found": True}
        last = f
    elif last:
        f = {**last, "found": False}
    else:
        f = {"x": W // 2 - 180, "y": 380, "w": 360, "h": 420, "found": False}
    f["cx"] = round((f["x"] + f["w"] / 2) / W, 3)
    f["chin_y"] = f["y"] + f["h"]
    out[gid] = f
job.write_json(out, "review", "faces.json")
found = sum(1 for f in out.values() if f["found"])
print(f"face-frame: {found}/{len(out)} cues with a detected face → review/faces.json")
for k, f in out.items():
    print(f"  {k:<6} cx={f['cx']:.2f} chin_y={f['chin_y']} {'' if f['found'] else '(fallback)'}")
