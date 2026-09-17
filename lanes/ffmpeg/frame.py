#!/usr/bin/env python3
"""Composite a still: a video frame at t, optionally with one or more alpha overlays at their own times.

The ONLY way stills are made in this pipeline. Never trust a tool's return code for pixels.

Usage: python lanes/ffmpeg/frame.py <video> <t> <out.png> [--overlay file.mov@t ...] [--scale W]
"""
import argparse
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("t", type=float)
ap.add_argument("out")
ap.add_argument("--overlay", action="append", default=[], help="path@seconds (seconds into the overlay file)")
ap.add_argument("--scale", type=int, default=0, help="output width (0 = native)")
a = ap.parse_args()

cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a.t:.3f}", "-i", a.video]
chain = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg]"
last = "bg"
for i, ov in enumerate(a.overlay, start=1):
    path, _, t = ov.rpartition("@")
    if not path:
        path, t = ov, "0"
    cmd += ["-ss", f"{float(t):.3f}", "-i", path]
    chain += f";[{i}:v]format=rgba[ov{i}];[{last}][ov{i}]overlay=0:0:format=auto[c{i}]"
    last = f"c{i}"
if a.scale:
    chain += f";[{last}]scale={a.scale}:-1[fin]"
    last = "fin"
cmd += ["-filter_complex", chain, "-map", f"[{last}]", "-frames:v", "1", a.out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0 or not Path(a.out).exists():
    print(r.stderr, file=sys.stderr)
    sys.exit(1)
print(a.out)
