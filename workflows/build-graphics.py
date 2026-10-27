#!/usr/bin/env python3
"""Node 05b — build. graphics-plan.json → compositions/*.html → renders/*.mov (alpha, sequence fps).

A graphic is either a composition written for this video (`"html": "compositions/<file>.html"`, a HyperFrames
composition the editor authored — rendered as is) or a preset filled from `params` (`"preset": "<name>"`).

Also the preset self-test:  build-graphics.py --preset presets/graphics/<name> --params <name>/example.json [--golden]
renders the example into a scratch job and compares frame t=1.0 against golden.png (SSIM ≥ 0.97);
--write-golden (re)creates the golden after a deliberate preset change.

Re-renders always go to a new filename; the plan records the render path and its mtime.

Usage: python workflows/build-graphics.py <job> [--only g01,g02] [--no-render]
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job, die, load_numbers, load_brand, now  # noqa: E402
from _hf import scaffold_hf, render, lint  # noqa: E402
import _presets as P  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job", nargs="?")
ap.add_argument("--preset")
ap.add_argument("--params")
ap.add_argument("--golden", action="store_true")
ap.add_argument("--write-golden", action="store_true")
ap.add_argument("--vertical", default="vertical/default", help="self-test only: the vertical preset whose numbers to render with")
ap.add_argument("--only", default=None)
ap.add_argument("--no-render", action="store_true")
a = ap.parse_args()


def build_one(job, g: dict, numbers: dict) -> dict:
    if g.get("html"):
        comp_rel = g["html"]
        if not job.p(comp_rel).exists():
            die(f"{g['id']}: composition not found: {comp_rel}")
        comp_id = Path(comp_rel).stem
        placement = "own"
    else:
        preset = P.load(g["preset"])
        params = dict(g.get("params", {}))
        params["duration"] = g["duration"]
        params["reveal_at"] = g.get("reveal_at", params.get("reveal_at", []))
        if g.get("box"):
            params["box"] = g["box"]
        placement = g.get("placement") or preset["schema"].get("x-default-placement", "inline")
        if placement == "auto":
            placement = preset["schema"].get("x-default-placement", "inline")
        comp_id = f"{g['id']}-{g['preset']}"
        html = P.fill(preset, params, comp_id, int(job.fps), numbers, placement, job.dir)
        comp_rel = f"compositions/{comp_id}.html"
        job.p(comp_rel).write_text(html, encoding="utf-8")
    ok, out = lint(job, comp_rel)
    if not ok and "error" in out.lower():
        print(f"lint[{g['id']}]:\n{out}", file=sys.stderr)
    return {"comp": comp_rel, "comp_id": comp_id, "placement": "box" if g.get("box") else placement}


# ---------------------------------------------------------------------------
# preset self-test mode
# ---------------------------------------------------------------------------
if a.preset:
    pdir = Path(a.preset)
    name = pdir.name
    preset = P.load(name)
    params = json.loads(Path(a.params or (pdir / "example.json")).read_text(encoding="utf-8"))
    numbers = load_numbers(a.vertical)
    numbers["_handle"] = load_brand().get("creator", {}).get("handle", "")
    errs = P.validate_params(preset, params)
    if errs:
        die(f"{name}: example params invalid: {errs}")
    scratch = REPO / "projects" / "_preset-test"
    scratch.mkdir(parents=True, exist_ok=True)
    # a minimal fake job for scaffold/render
    (scratch / "RUN.md").write_text("---\njob: _preset-test\nsource: raw/none\nfps: 30\npreset: vertical/default\nnodes:\n  intake: {status: done}\ngates: {}\n---\n")
    job = Job(scratch)
    scaffold_hf(job)
    # copy example assets referenced by the example, if any
    for k, spec in preset["schema"].get("properties", {}).items():
        if spec.get("x-asset") and k in params:
            files = params[k] if isinstance(params[k], list) else [params[k]]
            for f in files:
                src = f["src"] if isinstance(f, dict) else f
                sp = pdir / src
                if sp.exists():
                    dst = scratch / src
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sp, dst)
    placement = params.get("placement", preset["schema"].get("x-default-placement", "beside-r"))
    comp_id = f"test-{name}"
    html = P.fill(preset, params, comp_id, 30, numbers, placement, pdir)
    comp_rel = f"compositions/{comp_id}.html"
    (scratch / comp_rel).write_text(html, encoding="utf-8")
    ok, out = lint(job, comp_rel)
    print(f"lint[{name}]: {'ok' if ok else 'issues'}")
    if not ok:
        print(out[-1200:])
    for old in (scratch / "renders").glob(f"{comp_id}*.mov"):
        old.unlink()
    mov = render(job, comp_rel, f"renders/{comp_id}.mov")
    frame = scratch / "renders" / f"{comp_id}-t1.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.0", "-i", str(mov), "-frames:v", "1", str(frame)], check=True)
    golden = pdir / "golden.png"
    if a.write_golden or not golden.exists():
        shutil.copy2(frame, golden)
        print(f"golden written: {golden}")
    elif a.golden:
        s = P.ssim(frame, golden)
        print(f"golden ssim: {s:.4f}")
        if s < 0.97:
            die(f"{name}: render drifted from golden (ssim {s:.4f} < 0.97). Re-run with --write-golden if deliberate.")
    # composite preview over a neutral plate for a human look
    prev = scratch / "renders" / f"{comp_id}-preview.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=0x2a2f3a:s=1080x1920", "-i", str(frame),
                    "-filter_complex", "[1:v]format=rgba[o];[0:v][o]overlay=0:0", "-frames:v", "1", str(prev)], check=True)
    print(f"preview: {prev}")
    sys.exit(0)

# ---------------------------------------------------------------------------
# job mode
# ---------------------------------------------------------------------------
if not a.job:
    die("job dir or --preset required")
job = Job(a.job)
job.require("graphics")
numbers = job.numbers
numbers["_handle"] = job.brand.get("creator", {}).get("handle", "")
plan = job.read_json("graphics-plan.json")
scaffold_hf(job)
only = set(a.only.split(",")) if a.only else None

t0 = time.time()
built = 0
for g in plan["graphics"]:
    if only and g["id"] not in only:
        continue
    if g.get("render") and job.p(g["render"]).exists() and not g.get("dirty") and not only:
        continue
    info = build_one(job, g, numbers)
    if not g.get("html"):
        g["composition"] = info["comp"]
    if a.no_render:
        continue
    mov = render(job, info["comp"], f"renders/{info['comp_id']}.mov")
    g["render"] = mov.relative_to(job.dir).as_posix()
    g["render_mtime"] = mov.stat().st_mtime
    g["dirty"] = False
    built += 1
    job.write_json(plan, "graphics-plan.json")
    print(f"  {g['id']} {g.get('preset') or g['html']:<10} {info['placement']:<9} cue {g['cue']:6.2f}  → {g['render']}")

plan["built_at"] = now()
job.write_json(plan, "graphics-plan.json")
job.note("graphics", f"built {built} renders in {time.time()-t0:.0f}s")
print(f"build-graphics: {built} rendered · {time.time()-t0:.0f}s")
