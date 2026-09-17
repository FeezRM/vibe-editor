#!/usr/bin/env python3
"""Gate — cuts.json is a sane EDL: monotonic, inside the source, no slivers, no overlap, stats exact."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, die  # noqa: E402

job = Job(sys.argv[1])
cuts = job.read_json("cuts.json")
cfg = job.numbers["cut"]
fps = float(cuts["fps"])
dur = float(cuts["source_duration_s"])
errs = []
prev = -1.0
for i, k in enumerate(cuts["keep"]):
    if k["in"] < prev - 1e-6:
        errs.append(f"clip {i} overlaps previous")
    if k["in"] < -1e-6 or k["out"] > dur + 1e-3:
        errs.append(f"clip {i} outside source [{k['in']},{k['out']}]")
    if (k["out"] - k["in"]) * fps < cfg["min_sliver_frames"]:
        errs.append(f"clip {i} is a sliver ({(k['out']-k['in'])*fps:.1f} frames)")
    prev = k["out"]
kept = sum(k["out"] - k["in"] for k in cuts["keep"])
if abs(kept - cuts["stats"]["kept_s"]) > 0.01:
    errs.append("stats.kept_s does not match keep ranges")
if not cuts["keep"]:
    errs.append("no clips kept")
if errs:
    for e in errs:
        print("error:", e)
    job.gate("validate_edl", "fail")
    sys.exit(1)
job.gate("validate_edl", "pass")
print(f"validate-edl: pass · {len(cuts['keep'])} clips · {kept:.1f}s")
