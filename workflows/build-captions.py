#!/usr/bin/env python3
"""Node 03b — captions.json → compositions/captions.html → renders/captions.mov (alpha, sequence fps).

Applies caption_mute_windows from graphics-plan.json (if present) by DROPPING groups whose midpoint
falls inside a window — not by opacity, the glow would still draw. Hard cuts only: a caption is on
or off, never mid-transition. Timing gate: every group starts within one frame of its first word.

Usage: python workflows/build-captions.py <job> [--no-render]
"""
import argparse
import html
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, die  # noqa: E402
from _hf import scaffold_hf, render  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--keep-downstream", action="store_true", help="re-applying mute windows inside the graphics loop: do not stale later nodes")
a = ap.parse_args()

job = Job(a.job)
C = job.numbers["captions"]
W, H = job.numbers["canvas"]["width"], job.numbers["canvas"]["height"]
fps = job.fps
caps = job.read_json("captions.json")
groups = caps["groups"]

mute = list(caps.get("mute_windows", []))
if job.p("graphics-plan.json").exists():
    mute += job.read_json("graphics-plan.json").get("caption_mute_windows", [])
kept, dropped = [], []
for g in groups:
    mid = (g["s"] + g["e"]) / 2
    (dropped if any(m[0] <= mid < m[1] for m in mute) else kept).append(g)

# timing gate: first word onset == group start (within one frame)
for g in kept:
    if abs(g["s"] - g["words"][0]["s"]) > 1.0 / fps + 1e-6:
        die(f"caption {g['idx']} '{g['text']}' starts {g['s']} but its first word is at {g['words'][0]['s']}")
    if len(g["words"]) > C["max_words"] + 1:
        die(f"caption {g['idx']} has {len(g['words'])} words")

scaffold_hf(job)
band_mid = (C["band_top"] + C["band_bottom"]) / 2
max_w = int(C["max_width_frac"] * W)
case_css = "uppercase" if C["case"] == "upper" else ("lowercase" if C["case"] == "lower" else "none")
col = C["colors"]


def _rgba(hex_: str, a: float) -> str:
    h = hex_.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a:.2f})"


divs = []
rows = []
for i, g in enumerate(kept):
    cls = "cap hook" if g.get("hook") else "cap"
    parts = []
    used = False
    for x in g["words"]:
        tok = html.escape(x["w"] + x.get("end_punct", ""))
        acc = g.get("accent")
        if acc and not used and x["w"] == acc["word"]:
            parts.append(f'<em class="{acc["cls"]}">{tok}</em>')
            used = True
        else:
            parts.append(tok)
    divs.append(f'      <div class="{cls}" id="c{i}"><b>{" ".join(parts)}</b></div>')
    rows.append({"i": i, "s": round(g["s"], 3), "e": round(g["e"], 3)})

duration = caps["duration"] + 0.1
page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <link rel="stylesheet" href="tokens.css" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: 'CapSans'; src: url('fonts/{C.get("font_file", "Inter.ttf")}') format('truetype'); font-weight: 100 900; font-display: block; }}
      @font-face {{ font-family: 'CapSerif'; src: url('fonts/{C.get("accent_file", "PlayfairDisplay-Italic.ttf")}') format('truetype'); font-weight: 100 900; font-style: {C.get("accent_style", "italic")}; font-display: block; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: transparent; }}
      .cap {{
        position: absolute; left: 50%; top: {band_mid}px; transform: translate(-50%, -50%);
        width: {max_w}px; text-align: center;
        font-family: 'CapSans', '{C["font_family"]}', sans-serif; font-weight: {C["font_weight"]};
        font-size: {C["size_px"]}px; line-height: {C["line_height"]};
        letter-spacing: {C["tracking_em"]}em;
        text-transform: {case_css}; color: {col["ink"]};
        text-shadow: {C["glow"]}, 0 6px 26px rgba(0,0,0,0.7), 0 0 44px rgba(255,255,255,0.18);
        opacity: 0; will-change: opacity;
      }}
      .cap.hook {{ font-size: {C["hook_size_px"]}px; top: {band_mid - 40}px; }}
      .cap b {{ font-weight: inherit; display: block; white-space: nowrap; }}
      .cap em {{ font-family: 'CapSerif', '{C["accent_family"]}', serif; font-style: {C.get("accent_style", "italic")}; font-weight: {C["accent_weight"]};
                 font-size: {C["accent_scale"]}em; letter-spacing: 0; }}
      .em   {{ color: {col["em"]}; }}
      .bad  {{ color: {col["bad"]};  text-shadow: 0 0 18px rgba(0,0,0,.88), 0 0 34px {_rgba(col["bad"], .72)}; }}
      .good {{ color: {col["good"]}; text-shadow: 0 0 18px rgba(0,0,0,.88), 0 0 34px {_rgba(col["good"], .72)}; }}
      .hot  {{ color: {col["hot"]};  text-shadow: 0 0 18px rgba(0,0,0,.88), 0 0 34px {_rgba(col["hot"], .72)}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="captions" data-start="0" data-duration="{duration:.3f}"
         data-width="{W}" data-height="{H}" data-fps="{fps}">
{chr(10).join(divs)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const ROWS = {json.dumps(rows)};
      const tl = gsap.timeline({{ paused: true }});
      ROWS.forEach(function (r) {{
        const el = document.getElementById('c' + r.i);
        tl.set(el, {{ opacity: 1 }}, r.s);   // hard cut on
        tl.set(el, {{ opacity: 0 }}, r.e);   // hard cut off
      }});
      window.__timelines['captions'] = tl;
    </script>
  </body>
</html>
"""
comp = job.p("compositions", "captions.html")
comp.write_text(page)
print(f"build-captions: {len(kept)} captions ({len(dropped)} muted) → {comp.relative_to(job.dir)}")
for g in dropped:
    print(f"   muted {g['s']:6.2f}–{g['e']:6.2f}  {g['text']}")

if a.no_render:
    sys.exit(0)
t0 = time.time()
out = render(job, "compositions/captions.html", "renders/captions.mov")
caps["render"] = out.relative_to(job.dir).as_posix()
job.write_json(caps, "captions.json")
job.mark("captions", "done", invalidate=not a.keep_downstream, out=caps["render"], groups=len(kept), muted=len(dropped))
job.note("captions", f"built {len(kept)} captions ({len(dropped)} muted) → renders/captions.mov in {time.time()-t0:.0f}s")
print(f"rendered → {out.relative_to(job.dir)} in {time.time()-t0:.0f}s")
