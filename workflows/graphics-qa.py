#!/usr/bin/env python3
"""Gate — every placed graphic, checked in composited pixels. → review/qa-round-N.json + .png

Per graphic, at cue+0.3, cue+1.0 and cue+duration-0.2:
  render newer than the plan · alpha present · content bbox (from the alpha) clear of the caption band
  while a caption is live · content clear of the face bbox (+pad) · mean luma within max_luma_delta of
  the bare frame · no rgba() surface fills in the composition (scrim/hairline/glow/wash excepted).

Objective defects only. Exit 1 lists them for the review loop; taste is the human's.

Usage: python workflows/graphics-qa.py <job> [--round N]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job  # noqa: E402
import _presets as P  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--round", type=int, default=None)
a = ap.parse_args()
job = Job(a.job)
G, C = job.numbers["graphics"], job.numbers["captions"]
W, H = job.numbers["canvas"]["width"], job.numbers["canvas"]["height"]
plan = job.read_json("graphics-plan.json")
faces = job.read_json("review", "faces.json") if job.p("review", "faces.json").exists() else {}
caps = job.read_json("captions.json")["groups"] if job.p("captions.json").exists() else []
mutes = plan.get("caption_mute_windows", [])
spine = job.p("preview", "spine.mp4")
rnd = a.round or (int(job.state.get("nodes", {}).get("graphics", {}).get("rounds", 0)) + 1)
plan_mtime = job.p("graphics-plan.json").stat().st_mtime


def caption_live(t):
    if any(m[0] <= t < m[1] for m in mutes):
        return False
    return any(g["s"] <= t < g["e"] for g in caps)


def overlay_rgba(mov: Path, t: float):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(mov), "-frames:v", "1", "-pix_fmt", "rgba",
                        "-f", "rawvideo", "-"], capture_output=True)
    if len(r.stdout) != W * H * 4:
        return None
    return np.frombuffer(r.stdout, np.uint8).reshape(H, W, 4)


def bare_luma(t: float):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(spine), "-frames:v", "1", "-vf", "format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(H, W) if len(r.stdout) == W * H else None


defects, notes = [], []
tiles = []
for g in plan["graphics"]:
    gid = g["id"]
    if not g.get("render") or not job.p(g["render"]).exists():
        defects.append({"id": gid, "kind": "missing-render", "msg": "no render on disk"})
        continue
    mov = job.p(g["render"])
    if mov.stat().st_mtime < plan_mtime - 5 and g.get("dirty"):
        defects.append({"id": gid, "kind": "stale-render", "msg": "render older than plan"})
    comp = job.p(g.get("composition", "")) if g.get("composition") else None
    if comp and comp.exists():
        css = comp.read_text()
        for m in re.finditer(r"background(?:-color)?\s*:\s*[^;]*rgba\(", css):
            line = css[max(0, m.start() - 80):m.end() + 40]
            if not re.search(r"gradient|scrim|hairline|\.w\b|wash|glow|shadow", line):
                defects.append({"id": gid, "kind": "rgba-surface", "msg": line.strip()[:120]})
                break
    sch = P.load(g["preset"])["schema"]
    no_content = sch.get("x-no-content", False)
    face = faces.get(gid)
    samples = sorted({round(min(0.3, g["duration"] / 2), 3), round(min(1.0, g["duration"] * 0.6), 3), round(max(g["duration"] - 0.2, 0.1), 3)})
    for s in samples:
        t = g["cue"] + s
        rgba = overlay_rgba(mov, s)
        if rgba is None:
            defects.append({"id": gid, "kind": "no-alpha", "msg": f"cannot read rgba at +{s}s"})
            break
        alpha = rgba[:, :, 3]
        ys, xs = np.where(alpha > 40)
        if len(xs) == 0:
            if s >= 0.5:
                defects.append({"id": gid, "kind": "blank", "msg": f"nothing visible at +{s}s"})
            continue
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
        if not no_content:
            if caption_live(t):
                band = alpha[C["band_top"]:C["band_bottom"], :]
                dense = (band > 40).mean()
                if dense > 0.06:
                    defects.append({"id": gid, "kind": "caption-band", "msg": f"+{s}s: {dense:.0%} of the caption band covered while a caption is live"})
            if face and face.get("found"):
                pad = G["face_pad_px"]
                fx0, fy0 = max(0, face["x"] - pad), max(0, face["y"] - pad)
                fx1, fy1 = min(W, face["x"] + face["w"] + pad), min(H, face["y"] + face["h"] + pad)
                over = (alpha[fy0:fy1, fx0:fx1] > 40).mean()
                if over > 0.08:
                    defects.append({"id": gid, "kind": "face-overlap", "msg": f"+{s}s: {over:.0%} of the face box covered"})
        base = bare_luma(t)
        if base is not None:
            a_f = alpha.astype(np.float32) / 255.0
            ov_l = (0.299 * rgba[:, :, 0] + 0.587 * rgba[:, :, 1] + 0.114 * rgba[:, :, 2]).astype(np.float32)
            comp_l = base.astype(np.float32) * (1 - a_f) + ov_l * a_f
            b, c = float(base.mean()), float(comp_l.mean())
            # darkening the frame is the defect (a scrim behaving like a grade); a bright real screenshot is allowed more
            if b > 8 and not no_content and ((b - c) / b > G["max_luma_delta"] or (c - b) / b > G["max_luma_delta"] * 2):
                defects.append({"id": gid, "kind": "luma", "msg": f"+{s}s: frame luma {b:.0f}→{c:.0f} ({(c-b)/b:+.0%})"})
    # contact tile at +1.0 (or mid) for the human
    tile = job.p("review", f"qa-{gid}.png")
    subprocess.run([sys.executable, str(REPO / "lanes" / "ffmpeg" / "frame.py"), str(spine), f"{g['cue'] + samples[1]:.3f}", str(tile),
                    "--overlay", f"{mov}@{samples[1]:.3f}", "--scale", "270"], capture_output=True)
    if tile.exists():
        tiles.append(str(tile))

# dedupe defects per (id, kind)
seen, uniq = set(), []
for d in defects:
    k = (d["id"], d["kind"])
    if k not in seen:
        seen.add(k)
        uniq.append(d)
report = {"round": rnd, "defects": uniq, "graphics": len(plan["graphics"])}
job.write_json(report, "review", f"qa-round-{rnd}.json")
if tiles:
    n = len(tiles)
    cols = min(n, 6)
    inputs = []
    for t in tiles:
        inputs += ["-i", t]
    fc = "".join(f"[{i}:v]" for i in range(n)) + f"xstack=inputs={n}:layout=" + "|".join(
        f"{(i % cols) * 270}_{(i // cols) * 480}" for i in range(n)) + ":fill=black" if n > 1 else "[0:v]null"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", fc, str(job.p("review", f"qa-round-{rnd}.png"))],
                   capture_output=True)
for d in uniq:
    print(f"defect {d['id']} {d['kind']}: {d['msg']}")
job.gate("graphics_qa", "pass" if not uniq else "fail")
print(f"graphics-qa round {rnd}: {len(uniq)} defects across {len(plan['graphics'])} graphics → review/qa-round-{rnd}.json")
sys.exit(1 if uniq else 0)
