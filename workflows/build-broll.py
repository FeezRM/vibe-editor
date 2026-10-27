#!/usr/bin/env python3
"""B-roll windows — a clip that plays INSIDE the frame (where the speaker points), with its own audio.

broll-plan.json clips that carry `box` (and optionally `title`) are pre-rendered here to
renders/broll/<id>.mov: a canvas-sized ProRes 4444 with alpha (the clip cropped to the box aspect, rounded,
stroked; the title in the caption band) plus the clip's audio normalised to audio.voice_lufs. Both lanes
place that one file: assemble.py overlays it and mixes its audio, place-layers.mjs puts it on V2 + A2.
Clips without `box` stay full-frame cutaways (no audio), unchanged.

Clip fields: file, src_in, start, end (timeline s) · box {cx, top, w, aspect} (canvas px; defaults in
numbers.json broll_window) · audio (bool, default true for a box) · views {text, provenance} (a real count,
drawn as a pill in the window) · title {line_1, line_2} — words as
[{"t": "...", "acc": "hot|em|good|bad"}], drawn lowercase Inter 800 with Playfair italic accents.
A title says what the clip IS (the hook it demonstrates) — never invented; the plan's `why` names the source.
Top-level `titles` [{id, start, end, line_1, line_2}] are the same type as their own layer (title-<id>.mov), for a
title that must come up before its clips (on the spoken line); captions are dropped under every title.

Usage: python workflows/build-broll.py <job>
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job, die, ffprobe  # noqa: E402

job = Job(sys.argv[1])
N = job.numbers
W, H = N["canvas"]["width"], N["canvas"]["height"]
C, BW, A = N["captions"], N["broll_window"], N["audio"]
FONTS = REPO / "presets" / "vertical" / "default" / "fonts"   # looks extend default; fonts are inherited
plan_p = job.p("broll-plan.json")
if not plan_p.exists():
    print("build-broll: no broll-plan.json — nothing to build"); sys.exit(0)
plan = job.read_json("broll-plan.json")
out_dir = job.p("renders", "broll")
out_dir.mkdir(parents=True, exist_ok=True)


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if weight:   # set by axis name: Inter's first axis is optical size, not weight
        axes = f.get_variation_axes()
        f.set_variation_by_axes([weight if a["name"] in (b"Weight", "Weight") else a["maximum"] if a["name"] in (b"Optical size", "Optical size") else a["default"] for a in axes])
    return f


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def title_img(title):
    """Lowercase Inter 800 lines, accents in Playfair italic, centred in the caption band, soft dark glow."""
    size = C["hook_size_px"]
    sans = font("Inter.ttf", size, C["font_weight"])
    serif = font("PlayfairDisplay-Italic.ttf", int(size * C["accent_scale"]), C["accent_weight"])
    lines = [title[k] for k in ("line_1", "line_2") if title.get(k)]
    space = int(size * 0.28)
    rows = []
    for ln in lines:
        parts = []
        for w in ln:
            t = w["t"].lower() if C["case"] == "lower" else w["t"]
            f = serif if w.get("acc") else sans
            col = hexrgb(C["colors"].get(w.get("acc", "ink"), C["colors"]["ink"]))
            x0, y0, x1, y1 = f.getbbox(t)
            parts.append((t, f, col, x1 - x0, x0))
        width = sum(p[3] for p in parts) + space * (len(parts) - 1)
        if width > W * C["max_width_frac"]:
            die(f"build-broll: title line too wide ({width}px > {W * C['max_width_frac']:.0f}) — shorten it")
        rows.append((parts, width))
    lh = int(size * 1.18)
    band_c = (C["band_top"] + C["band_bottom"]) / 2
    y = int(band_c - lh * len(rows) / 2)
    ink = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ink)
    for parts, width in rows:
        x = (W - width) / 2
        for t, f, col, pw, x0 in parts:
            d.text((x - x0, y + lh * 0.82), t, font=f, fill=col + (255,), anchor="ls")
            x += pw + space
        y += lh
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow.putalpha(ink.getchannel("A").point(lambda a: int(a * 0.8)).filter(ImageFilter.GaussianBlur(16)))
    return Image.alpha_composite(glow, ink)


def badge_img(text, bx, by, bw, bh):
    """The platform's own view-count read: a dark pill with a play glyph, inside the window's bottom-left corner."""
    B = BW["badge"]
    f = font("Inter.ttf", B["size_px"], C["font_weight"])
    x0, y0, x1, y1 = f.getbbox(text)
    tw, th = x1 - x0, B["size_px"]
    pad, tri = B["pad_px"], int(B["size_px"] * 0.62)
    pw, ph = pad * 2 + tri + pad * 0.6 + tw, th + pad * 1.2
    px, py = bx + B["inset_px"], by + bh - B["inset_px"] - ph
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph / 2, fill=(0, 0, 0, int(255 * B["bg_alpha"])))
    cy = py + ph / 2
    d.polygon([(px + pad, cy - tri / 2), (px + pad, cy + tri / 2), (px + pad + tri * 0.87, cy)], fill=(255, 255, 255, 255))
    d.text((px + pad + tri + pad * 0.6 - x0, cy), text, font=f, fill=(255, 255, 255, 255), anchor="lm")
    return im


def still_mov(img, dur, out):
    """A canvas-sized still with alpha as a ProRes 4444 of exactly `dur` — placeable like any render on both lanes."""
    png = out.with_suffix(".png")
    img.save(png)
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-r", str(job.fps), "-i", str(png), "-t", f"{dur:.3f}",
                        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(out)], capture_output=True, text=True)
    png.unlink(missing_ok=True)
    if r.returncode or not out.exists():
        die(f"build-broll: still {out.name} failed: {r.stderr[-400:]}")


def window_mask(w, h, r, path):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    m.save(path)


built = 0
for c in plan.get("clips", []):
    if "box" not in c and "title" not in c:
        continue
    src = Path(c["file"]) if Path(c["file"]).is_absolute() else job.p(c["file"])
    if not src.exists():
        die(f"build-broll: missing on disk: {src}")
    info = ffprobe(src)
    box = {**{k: BW[k] for k in ("cx", "top", "w", "aspect")}, **c.get("box", {})}
    bw = int(box["w"]) // 2 * 2
    bh = int(round(bw / box["aspect"])) // 2 * 2
    bx, by = int(box["cx"] - bw / 2), int(box["top"])
    dur = c["end"] - c["start"]
    sx = BW["stroke_px"]
    tmp = out_dir / f"{c['id']}"
    window_mask(bw, bh, BW["radius_px"], f"{tmp}.mask.png")
    window_mask(bw + 2 * sx, bh + 2 * sx, BW["radius_px"] + sx, f"{tmp}.stroke.png")
    inputs = ["-f", "lavfi", "-i", f"color=c=black@0.0:s={W}x{H}:r={job.fps}:d={dur:.3f},format=rgba",
              "-ss", f"{c['src_in']:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
              "-loop", "1", "-i", f"{tmp}.mask.png", "-loop", "1", "-i", f"{tmp}.stroke.png"]
    pan = c.get("pan", 0.5)
    fc = [f"[1:v]setpts=PTS-STARTPTS,fps={job.fps},scale={bw}:{bh}:force_original_aspect_ratio=increase,"
          f"crop={bw}:{bh}:(iw-{bw})*{pan:.3f}:(ih-{bh})/2,setsar=1,format=rgba[clip]",
          "[2:v]format=gray[m]", "[clip][m]alphamerge[win]",
          f"color=c={BW['stroke_color']}:s={bw + 2 * sx}x{bh + 2 * sx}:r={job.fps}:d={dur:.3f},format=rgba[sc]",
          "[3:v]format=gray[smask]", "[sc][smask]alphamerge[stroke]",
          f"[0:v][stroke]overlay={bx - sx}:{by - sx}:shortest=1[b1]",
          f"[b1][win]overlay={bx}:{by}:shortest=1[b2]"]
    last = "b2"
    if c.get("title") or c.get("views"):
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if c.get("title"):
            ov = Image.alpha_composite(ov, title_img(c["title"]))
        if c.get("views"):   # a real count with provenance, never estimated
            if not c["views"].get("provenance"):
                die(f"build-broll: {c['id']} views without provenance")
            ov = Image.alpha_composite(ov, badge_img(c["views"]["text"], bx, by, bw, bh))
        ov.save(f"{tmp}.over.png")
        inputs += ["-loop", "1", "-i", f"{tmp}.over.png"]
        fc.append(f"[{last}][4:v]overlay=0:0:shortest=1,format=yuva444p10le[v]")
    else:
        fc.append(f"[{last}]format=yuva444p10le[v]")
    has_audio = c.get("audio", True) and info.get("has_audio", True)
    if has_audio:
        # measured, then a static gain (one-pass loudnorm under-corrects a 2 s clip by ~5 dB) + the voice's peak ceiling
        m = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{c['src_in']:.3f}", "-t", f"{dur:.3f}", "-i", str(src), "-vn",
                            "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
        lu = re.findall(r"I:\s+(-?[0-9.]+) LUFS", m.split("Summary")[-1])
        gain = (A["voice_lufs"] - float(lu[0])) if lu else 0.0
        fc.append(f"[1:a]asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"volume={gain:.2f}dB,alimiter=limit={10 ** (A['peak_dbfs'] / 20):.4f}:level=false,aresample=48000,"
                  f"afade=t=in:d=0.02,afade=t=out:st={max(dur - 0.04, 0):.3f}:d=0.04,apad,atrim=0:{dur:.3f}[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]"]
    # content-addressed name: Premiere holds placed renders open, and re-rendering onto an open file fails (archive#rerender-eperm)
    tag = hashlib.sha1(json.dumps([cmd, c.get("title"), c.get("views")], ensure_ascii=False).encode()).hexdigest()[:8]
    out = out_dir / f"{c['id']}-{tag}.mov"
    if has_audio:
        cmd += ["-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000"]
    cmd += ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-t", f"{dur:.3f}", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True) if not out.exists() else subprocess.CompletedProcess(cmd, 0)
    if r.returncode or not out.exists():
        print(r.stderr[-2000:], file=sys.stderr)
        die(f"build-broll: {c['id']} failed")
    for suf in ("mask", "stroke"):
        Path(f"{tmp}.{suf}.png").unlink(missing_ok=True)
    c["render"] = str(out.relative_to(job.dir)).replace("\\", "/")
    c["render_audio"] = bool(has_audio)
    built += 1
    print(f"  {c['id']}: {bw}x{bh} window at ({bx},{by}) · {dur:.2f}s · audio {'yes' if has_audio else 'no'}"
          f"{' · title' if c.get('title') else ''} → {c['render']}")
# hook titles: their own layer, timed independently of the clips (they come up on the spoken line, before the clip)
for t in plan.get("titles", []):
    img = title_img(t)
    tag = hashlib.sha1(json.dumps([t.get("line_1"), t.get("line_2"), round(t["end"] - t["start"], 3), C, job.fps],
                                  ensure_ascii=False).encode()).hexdigest()[:8]
    out = out_dir / f"title-{t['id']}-{tag}.mov"
    if not out.exists():
        still_mov(img, t["end"] - t["start"], out)
    t["render"] = str(out.relative_to(job.dir)).replace("\\", "/")
    built += 1
    print(f"  title {t['id']}: {t['start']:.2f}–{t['end']:.2f}s → {t['render']}")
job.write_json(plan, "broll-plan.json")
print(f"build-broll: {built} windowed clips → renders/broll/")
