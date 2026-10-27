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
    # a short piece that continues the same take within cut.tuck_max_s on either side (a pause or long closure cut out
    # by rough-cut 7c) shows the same pose a few frames on — it does not flash like a sliver from another moment
    tm = cfg.get("tuck_max_s", 0.3)
    tuck = (i > 0 and 0 <= k["in"] - cuts["keep"][i - 1]["out"] <= tm) or            (i + 1 < len(cuts["keep"]) and 0 <= cuts["keep"][i + 1]["in"] - k["out"] <= tm)
    if (k["out"] - k["in"]) * fps < cfg["min_sliver_frames"] and not tuck:
        errs.append(f"clip {i} is a sliver ({(k['out']-k['in'])*fps:.1f} frames)")
    prev = k["out"]
kept = sum(k["out"] - k["in"] for k in cuts["keep"])
if abs(kept - cuts["stats"]["kept_s"]) > 0.01:
    errs.append("stats.kept_s does not match keep ranges")
if not cuts["keep"]:
    errs.append("no clips kept")
# every cut point must sit in a pause, measured on the voice: loud on both sides = a word chopped (9078 "value")
wav = job.p("transcript", "audio.wav")
if wav.exists():
    from _audio import Envelope
    env = Envelope(wav, job.read_json("transcript", "words.json"), cfg["edge_rel_db"])
    for i, k in enumerate(cuts["keep"]):
        for side in ("in", "out"):
            if side in k.get("exact", []):   # an edge the editor pinned between run-together words (cuts.overrides "exact")
                continue
            if env.hot(k[side]):
                errs.append(f"clip {i} {side}-point {k[side]:.2f}s is inside speech "
                            f"({env.level(k[side] - 0.03, k[side]):.0f} / {env.level(k[side], k[side] + 0.03):.0f} dB, threshold {env.thr:.0f})")
if errs:
    for e in errs:
        print("error:", e)
    job.gate("validate_edl", "fail")
    sys.exit(1)
job.gate("validate_edl", "pass")
print(f"validate-edl: pass · {len(cuts['keep'])} clips · {kept:.1f}s")
