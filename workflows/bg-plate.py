#!/usr/bin/env python3
"""Background replacement as data: the speaker's own matte → a hole-cut background plate the `bg-swap` preset plays.

Input: assets/subject.webm (`npx hyperframes remove-background preview/spine.mp4 -o assets/subject.webm`, alpha
in timeline time) and a schedule in assets/bg-plan.json:
    {"segments": [{"at": 0.0, "bg": "azure"}, {"at": 1.45, "bg": "none"}, {"at": 2.77, "bg": "mid"}, …]}
`bg` is a generated texture (azure · sunset · neon · space · chroma), "mid" (the real background drained of colour),
"none" (the real room, plate transparent) or a path to a 1080×1920 image. Textures are generated, never a fact.

Output: assets/bg-plate.webm — RGB = the background, alpha = everything that is NOT the speaker. The speaker stays the
real footage underneath; the plate only covers the room. The matte is repaired first: soft (motion-blurred) alpha is
boosted, and holes are closed hard around the face, where a held mic or a hand at the mouth gets keyed out.

The plate is in spine time: a zoom punch in cuts.json would move the speaker under it — none inside a bg-swap window.

Usage: python workflows/bg-plate.py <job> [--subject assets/subject.webm] [--plan assets/bg-plan.json]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, die  # noqa: E402
from _faces import FaceFinder  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--subject", default="assets/subject.webm")
ap.add_argument("--plan", default="assets/bg-plan.json")
ap.add_argument("--out", default="assets/bg-plate.webm")
ap.add_argument("--textures-only", action="store_true")
a = ap.parse_args()

job = Job(a.job)
W, H = job.numbers["canvas"]["width"], job.numbers["canvas"]["height"]
fps = job.fps
spine, subject = job.p("preview", "spine.mp4"), job.p(a.subject)
for f in (spine, subject):
    if not f.exists():
        die(f"missing {f}")
segs = sorted(job.read_json(a.plan)["segments"], key=lambda s: s["at"])
rng = np.random.default_rng(7)


# ---------------------------------------------------------------------------------------------- generated textures
def grad(top, bot, mid=None):
    t = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array(top, float), np.array(bot, float)
    if mid is None:
        g = top * (1 - t) + bot * t
    else:
        mid = np.array(mid, float)
        g = np.where(t < 0.5, top * (1 - t * 2) + mid * (t * 2), mid * (1 - (t - 0.5) * 2) + bot * ((t - 0.5) * 2))
    return np.broadcast_to(g, (H, W, 3)).copy()


def bokeh(img, n, colors, rmin, rmax, amin, amax, ymin=0.0, ymax=1.0, soft=0.18):
    """Out-of-focus lights: soft discs with a faint bright rim, screen-blended so overlaps glow instead of clipping."""
    out = img.astype(np.float32)
    for _ in range(n):
        c = np.array(colors[rng.integers(len(colors))], float)
        x, y = int(rng.uniform(0, W)), int(rng.uniform(ymin, ymax) * H)
        r = int(rng.uniform(rmin, rmax))
        disc = np.zeros((H, W), np.float32)
        cv2.circle(disc, (x, y), r, 0.75, -1, cv2.LINE_AA)
        cv2.circle(disc, (x, y), r, 1.0, max(2, r // 10), cv2.LINE_AA)
        disc = cv2.GaussianBlur(disc, (0, 0), max(1.5, r * soft))
        a = disc[..., None] * rng.uniform(amin, amax)
        out = 255 - (255 - out) * (1 - a * c / 255.0)
    return out


def clouds(scale, octaves=4):
    out = np.zeros((H, W), np.float32)
    for o in range(octaves):
        s = max(2, int(scale * 2 ** o))
        n = rng.random((max(2, H // s), max(2, W // s))).astype(np.float32)
        out += cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC) / 2 ** o
    out -= out.min()
    return out / out.max()


def finish(img, grain=5.0, vignette=0.35):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H / 2)) ** 2)
    img = img * (1 - vignette * np.clip(d - 0.35, 0, 1)[..., None])
    img = img + rng.normal(0, grain, (H, W, 1))
    return np.clip(img, 0, 255).astype(np.uint8)


def texture(kind: str) -> np.ndarray:
    if kind == "azure":     # luminous blue-white, soft bokeh, light from above (the creator's blue-LED room, upgraded)
        img = grad((235, 245, 255), (12, 52, 140), (40, 132, 237))
        img = bokeh(img, 34, [(255, 255, 255), (150, 210, 255), (84, 179, 233)], 14, 64, 0.18, 0.5, 0.0, 0.7)
        rays = np.zeros((H, W), np.float32)
        for k in range(5):
            x0 = int(W * (0.1 + 0.2 * k))
            cv2.line(rays, (x0, -50), (x0 + 520, H), 1.0, 70)
        img += cv2.GaussianBlur(rays, (0, 0), 50)[..., None] * np.array([60, 80, 90])
        return finish(img, 4, 0.3)
    if kind == "sunset":    # warm dusk, a big soft sun behind the head
        img = grad((92, 44, 140), (255, 128, 64), (255, 96, 120))
        sun = np.zeros((H, W), np.float32)
        cv2.circle(sun, (W // 2, int(H * 0.33)), 260, 1.0, -1, cv2.LINE_AA)
        img += cv2.GaussianBlur(sun, (0, 0), 70)[..., None] * np.array([255, 190, 120]) * 0.85
        img = bokeh(img, 22, [(255, 220, 170), (255, 170, 130)], 12, 52, 0.2, 0.55, 0.45, 1.0)
        return finish(img, 5, 0.4)
    if kind == "neon":      # a city at night, out of focus
        img = grad((10, 6, 30), (22, 8, 40), (34, 10, 60))
        img = bokeh(img, 70, [(255, 40, 160), (40, 220, 255), (150, 60, 255), (255, 170, 40)], 12, 58, 0.25, 0.75, 0.0, 1.0)
        return finish(img, 6, 0.45)
    if kind == "space":     # deep space: a diagonal band of nebula and stars, fine detail, never blotchy
        img = grad((5, 5, 18), (3, 3, 10))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        band = np.exp(-(((xx * 0.8 - yy * 0.45) - (W * 0.4 - H * 0.2)) / 330.0) ** 2)
        neb = (clouds(260, 7) ** 2.6) * band
        img += neb[..., None] * np.array([170, 80, 230]) + ((clouds(180, 7) ** 4) * band)[..., None] * np.array([60, 140, 255])
        stars = rng.random((H, W))
        img += (cv2.GaussianBlur((stars > 0.9993).astype(np.float32), (0, 0), 0.9) * 700)[..., None]
        img += (cv2.GaussianBlur((stars > 0.99995).astype(np.float32), (0, 0), 3.5) * 900)[..., None] * np.array([0.8, 0.9, 1.0])
        img += ((stars > 0.996) * band * 160)[..., None]
        return finish(img, 3, 0.3)
    if kind == "chroma":    # a literal green screen
        return np.full((H, W, 3), (0, 177, 64), np.uint8)
    p = job.p(kind)
    if not p.exists():
        die(f"unknown background '{kind}' (azure, sunset, neon, space, chroma, mid, none or an image path)")
    return cv2.cvtColor(cv2.resize(cv2.imread(str(p)), (W, H)), cv2.COLOR_BGR2RGB)


tex = {s["bg"]: texture(s["bg"]) for s in segs if s["bg"] not in ("mid", "none")}
if a.textures_only:                 # look at the textures before rendering 400 frames of plate
    for k, v in tex.items():
        cv2.imwrite(str(job.p("review", f"bg-{k}.png")), cv2.cvtColor(v, cv2.COLOR_RGB2BGR))
    print(f"bg-plate: wrote {len(tex)} textures to review/")
    sys.exit(0)


def seg_at(t):
    cur, start, end = segs[0], segs[0]["at"], None
    for i, s in enumerate(segs):
        if s["at"] <= t + 1e-6:
            cur, start = s, s["at"]
            end = segs[i + 1]["at"] if i + 1 < len(segs) else None
    return cur, start, end


# ---------------------------------------------------------------------------------------------- the frames
def frames(path, pix, ch, vcodec=None):
    cmd = ["ffmpeg", "-loglevel", "error"] + (["-c:v", vcodec] if vcodec else []) + ["-i", str(path),
           "-vf", f"scale={W}:{H}", "-pix_fmt", pix, "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * ch
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, ch)


out = job.p(a.out)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps),
                        "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M", "-auto-alt-ref", "0", str(out)],
                       stdin=subprocess.PIPE)
ff = FaceFinder(W // 3, H // 3)
k_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
k_big = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))
face = None
n = 0
for rgb, sub in zip(frames(spine, "rgb24", 3), frames(subject, "rgba", 4, "libvpx-vp9")):
    t = n / fps
    seg, s0, s1 = seg_at(t)
    plate = np.zeros((H, W, 4), np.uint8)
    if seg["bg"] != "none":
        al = sub[..., 3].astype(np.float32) / 255.0
        al = np.clip((al - 0.08) * 1.7, 0, 1)                                   # motion blur reads as solid, not ghost
        m = (al > 0.3).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k_small)
        if n % 3 == 0:                                                          # the face moves slowly; every 3rd frame
            small = cv2.cvtColor(cv2.resize(rgb, (W // 3, H // 3)), cv2.COLOR_RGB2BGR)
            f = ff.find(small)
            face = tuple(v * 3 for v in f) if f else face
        if face:                                                                # a mic or hand at the mouth: close hard
            x, y, w, h = face
            roi = np.zeros_like(m)
            cv2.ellipse(roi, (x + w // 2, y + int(h * 0.9)), (int(w * 1.15), int(h * 1.35)), 0, 0, 360, 1, -1)
            big = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k_big)
            m = np.where(roi > 0, np.maximum(m, big), m)
            # above the face only the head is the speaker: the matte model kept a framed picture on the wall that
            # touches the hair (9280: a figure standing on his head). Over the head's columns, rows above the face box
            # keep only an ellipse continuing the skull (hair ends ~0.31 face heights up; the ellipse reaches 0.34, 0.9 face widths out).
            cap = np.zeros_like(m)
            cv2.ellipse(cap, (x + w // 2, y + int(h * 0.45)), (int(w * 0.9), int(h * 0.79)), 0, 0, 360, 1, -1)
            x0, x1 = max(0, x - int(w * 0.7)), min(W, x + w + int(w * 0.7))
            above = np.zeros_like(m)
            above[:max(0, y), x0:x1] = 1
            m = np.where((above > 0) & (cap == 0), 0, m)
            al = np.where((above > 0) & (cap == 0), 0.0, al)
        al = np.maximum(al, cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0))
        hole = 1.0 - al
        if seg["bg"] == "mid":                                                  # the real room, drained of colour
            g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) * 0.82
            bg = np.repeat(g[..., None], 3, axis=2).astype(np.uint8)
        else:
            src = tex[seg["bg"]]
            span = (s1 - s0) if s1 is not None else 3.0
            z = 1.0 + 0.035 * min(1.0, (t - s0) / max(span, 0.5))               # a slow push, so a still never sits dead
            M = cv2.getRotationMatrix2D((W / 2, H * 0.42), 0, z)
            bg = cv2.warpAffine(src, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        plate[..., :3] = bg
        plate[..., 3] = (hole * 255).astype(np.uint8)
    enc.stdin.write(plate.tobytes())
    n += 1
enc.stdin.close()
enc.wait()
if enc.returncode != 0 or not out.exists():
    die("bg-plate: encode failed")
job.note("graphics", f"bg-plate: {n} frames, {len(segs)} segments → {a.out}")
print(f"bg-plate: {n} frames · {len(segs)} segments ({', '.join(s['bg'] + '@' + str(s['at']) for s in segs)}) → {out.relative_to(job.dir)}")
