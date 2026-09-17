#!/usr/bin/env python3
"""Create a job folder: copy the source (never move), record its facts, write RUN.md.

Usage: python workflows/new-job.py <source-file> --slug <slug> [--brief "..."] [--lane ffmpeg|premiere]
                                   [--tier basic|premium] [--preset vertical/default]
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, die, ffprobe, load_numbers, now, sha256, _dump_front  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("source")
ap.add_argument("--slug", required=True)
ap.add_argument("--brief", default="Edit this video end to end.")
ap.add_argument("--lane", default="ffmpeg", choices=["ffmpeg", "premiere"])
ap.add_argument("--tier", default="basic", choices=["basic", "premium"])
ap.add_argument("--preset", default="vertical/default")
ap.add_argument("--music", default=None, help="optional music file to copy into audio/")
ap.add_argument("--force", action="store_true")
a = ap.parse_args()

src = Path(a.source).expanduser().resolve()
if not src.exists():
    die(f"source not found: {src}")
job = REPO / "projects" / a.slug
if job.exists() and not a.force:
    die(f"job exists: {job} (use --force to recreate RUN.md; raw/ is kept)")
for d in ("raw", "transcript", "compositions", "renders", "assets", "audio", "preview", "outputs", "review"):
    (job / d).mkdir(parents=True, exist_ok=True)

dst = job / "raw" / src.name
if not dst.exists():
    shutil.copy2(src, dst)
info = ffprobe(dst)
if not info["has_audio"]:
    die("source has no audio track — nothing to transcribe")
fmt = "vertical" if info["height"] > info["width"] else "horizontal"
numbers = load_numbers(a.preset)

if a.music:
    m = Path(a.music).expanduser().resolve()
    shutil.copy2(m, job / "audio" / m.name)

state = {
    "job": a.slug,
    "source": f"raw/{src.name}",
    "checksum": sha256(dst),
    "source_duration_s": round(info["duration"], 3),
    "source_fps": round(info["fps"], 3),
    "format": fmt,
    "fps": int(round(info["fps"])) if int(round(info["fps"])) in (24, 25, 30, 60) else numbers["canvas"]["fps"],
    "lane": a.lane,
    "tier": a.tier,
    "preset": a.preset,
    "created": now(),
    "nodes": {"intake": {"status": "done", "at": now(), "out": f"raw/{src.name}"}},
    "gates": {},
}
body = f"## Brief\n{a.brief}\n\n## Notes\n- intake: copied {src.name} ({info['width']}x{info['height']} @ {info['fps']:.2f}fps, {info['duration']:.1f}s) → raw/\n"
(job / "RUN.md").write_text("---\n" + _dump_front(state) + "\n---\n" + body)
print(f"job ready: {job}\n  format={fmt} duration={info['duration']:.1f}s lane={a.lane} tier={a.tier}")
