"""Measure burnt-in caption geometry from a video frame or still.

Reports cap height and line width normalised to 1080x1920.

Method notes (v2, after v1 gave bad numbers):
  * threshold 245, not 225 -- the soft glow around reference captions is bright
    enough to pass a lower threshold and inflates cap height by 20-40%.
  * a text row must contain >= MIN_HOT bright pixels; specular highlights on
    skin, jewellery and background lights trip a low bar and produce phantom
    "lines" a few px tall.
  * rows are grouped into lines allowing a 3px gap, and a line must be
    >= MIN_ROWS tall to count.
Always sanity-check the output against a visual crop of the same frame.

Usage:  python analysis/measure.py <frame-or-video> [t1,t2,...]
"""
import subprocess, sys, os

THRESH = 245
MIN_HOT = 40        # bright pixels in a row before it counts as text
MIN_ROWS = 20       # a caption line is at least this many rows tall
BAND = (0.38, 0.72)  # search window as a fraction of frame height


def frame_pgm(src, t, out):
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if t is not None:
        cmd += ["-ss", str(t)]
    cmd += ["-i", src, "-frames:v", "1", "-pix_fmt", "gray",
            "-f", "image2", "-vcodec", "pgm", out]
    subprocess.run(cmd, check=True)


def read_pgm(path):
    data = open(path, "rb").read()
    idx, fields = 0, []
    while len(fields) < 4:
        while data[idx:idx + 1].isspace():
            idx += 1
        if data[idx:idx + 1] == b"#":
            while data[idx:idx + 1] != b"\n":
                idx += 1
            continue
        start = idx
        while not data[idx:idx + 1].isspace():
            idx += 1
        fields.append(data[start:idx])
    idx += 1
    w, h = int(fields[1]), int(fields[2])
    return w, h, data[idx:idx + w * h]


def measure(src, t=None):
    tmp = f"_m{os.getpid()}.pgm"
    frame_pgm(src, t, tmp)
    w, h, px = read_pgm(tmp)
    os.remove(tmp)

    y0, y1 = int(h * BAND[0]), int(h * BAND[1])
    hot = []
    for y in range(y0, y1):
        base = y * w
        c = 0
        for x in range(w):
            if px[base + x] >= THRESH:
                c += 1
        if c >= MIN_HOT:
            hot.append(y)
    if not hot:
        return None

    lines, cur = [], [hot[0]]
    for y in hot[1:]:
        if y - cur[-1] <= 3:
            cur.append(y)
        else:
            lines.append(cur); cur = [y]
    lines.append(cur)
    lines = [L for L in lines if len(L) >= MIN_ROWS]

    sx, sy = 1080 / w, 1920 / h
    out = []
    for L in lines:
        xs = [x for y in L for x in range(w) if px[y * w + x] >= THRESH]
        out.append({
            "cap": (L[-1] - L[0] + 1) * sy,
            "width_pct": 100 * (max(xs) - min(xs) + 1) / w,
            "y_top": L[0] * sy, "y_bot": L[-1] * sy,
        })
    return {"w": w, "h": h, "lines": out}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip())
    src = sys.argv[1]
    ts = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [None]
    for t in ts:
        r = measure(src, t)
        label = f"t={t}" if t is not None else "still"
        if not r or not r["lines"]:
            print(f"{label}: no caption found"); continue
        print(f"{label}  ({r['w']}x{r['h']})")
        for l in r["lines"]:
            print(f"   cap {l['cap']:5.1f}px@1920   width {l['width_pct']:5.1f}%   "
                  f"y {l['y_top']:.0f}-{l['y_bot']:.0f}")
        c = (r["lines"][0]["y_top"] + r["lines"][-1]["y_bot"]) / 2
        print(f"   block centre y = {c:.0f}/1920 = {100*c/1920:.1f}%")
