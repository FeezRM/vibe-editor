#!/usr/bin/env python3
"""Real audio data for the graphics layer: the loudness envelope of the raw and of the cut, plus the EDL's keep
ranges, as one JSON a preset reads through an `x-json` param (dead-space, anything that draws a waveform).

  {"raw_s": 165.6, "kept_s": 20.6, "bins": 110,
   "raw":  [0..1 × bins]   RMS envelope of the raw source (what was recorded)
   "cut":  [0..1 × bins]   RMS envelope of preview/spine.mp4 (what survived)
   "keep": [[a, b], …]     keep ranges as fractions of the raw}

Nothing is smoothed into a shape it did not have: RMS per bin, normalised to the loudest bin, square-rooted so
quiet speech still reads as speech next to silence.

Usage: python workflows/waveform.py <job> [--bins 110] [--out assets/waveform.json]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, die  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--bins", type=int, default=110)
ap.add_argument("--out", default="assets/waveform.json")
a = ap.parse_args()
job = Job(a.job)
cuts = job.read_json("cuts.json")


def envelope(src: Path, bins: int) -> tuple[list, float]:
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        die(f"cannot read audio from {src}")
    x = np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768.0
    dur = len(x) / 8000.0
    edges = np.linspace(0, len(x), bins + 1).astype(int)
    rms = np.array([np.sqrt(np.mean(x[edges[i]:edges[i + 1]] ** 2)) if edges[i + 1] > edges[i] else 0.0 for i in range(bins)])
    rms = np.sqrt(rms / (rms.max() or 1.0))
    return [round(float(v), 3) for v in rms], dur


raw, raw_s = envelope(job.source, a.bins)
spine = job.p("preview", "spine.mp4")
cut, cut_s = envelope(spine, a.bins) if spine.exists() else ([], 0.0)
keep = [[round(k["in"] / raw_s, 4), round(k["out"] / raw_s, 4)] for k in cuts["keep"]]
out = {"raw_s": round(raw_s, 1), "kept_s": round(sum(k["out"] - k["in"] for k in cuts["keep"]), 1), "bins": a.bins,
       "raw": raw, "cut": cut, "keep": keep, "provenance": f"{job.source.name} + preview/spine.mp4 RMS, cuts.json keeps"}
job.write_json(out, *Path(a.out).parts)
print(f"waveform: {a.bins} bins · raw {raw_s:.1f}s → kept {out['kept_s']}s · {len(keep)} keeps → {a.out}")
