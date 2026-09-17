#!/usr/bin/env python3
"""Node 02b — rough cut as data. transcript/words.json → cuts.json (the EDL).

Removes: dead air between words ≥ cut.min_gap_s (leaving cut.lead_s before the next onset — the
"cut on the breath" rule as a number), filler tokens, immediate repeats (false starts). Never
removes voice tics listed in cut.keep_tics. Never produces a kept clip shorter than cut.min_clip_s.

--review prints every removal with an id; vetoes go in cuts.overrides.json as {"keep_ids": [..]}
and are re-applied deterministically on the next run.

Usage: python workflows/rough-cut.py <job> [--review]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--review", action="store_true")
a = ap.parse_args()

job = Job(a.job)
job.require("rough_cut")
cfg = job.numbers["cut"]
fps = job.fps
duration = float(job.state["source_duration_s"])
words = job.read_json("transcript", "words.json")
overrides = job.read_json("cuts.overrides.json") if job.p("cuts.overrides.json").exists() else {}
vetoed = set(overrides.get("keep_ids", []))

fillers = set(cfg["fillers"])
keep_tics = set(cfg["keep_tics"])


def norm(w):
    return w["w"].lower().strip("'’\"")


removals = []  # {"id", "in", "out", "reason"}


def add(rin, rout, reason):
    rin, rout = max(0.0, rin), min(duration, rout)
    if rout - rin >= 1.0 / fps:
        removals.append({"id": f"r{len(removals)+1:03d}", "in": round(rin, 3), "out": round(rout, 3), "reason": reason})


# 1. head and tail
if words[0]["s"] - cfg["lead_s"] > 0.15:
    add(0.0, words[0]["s"] - cfg["lead_s"], "silence:head")
tail_end = words[-1]["e"] + max(cfg["tail_s"], 0.35)
if duration - tail_end > 0.25:
    add(tail_end, duration, "silence:tail")

# 2. gaps between words
for i in range(1, len(words)):
    p, w = words[i - 1], words[i]
    gap = w["s"] - p["e"]
    if gap >= cfg["min_gap_s"]:
        add(p["e"] + cfg["tail_s"], w["s"] - cfg["lead_s"], "silence")

# 3. fillers (whole tokens), never tics
for i, w in enumerate(words):
    n = norm(w)
    if n in fillers and n not in keep_tics:
        add(w["s"] - 0.02, w["e"] + 0.02, f"filler:{n}")

# 4. false starts: immediate repeat of a word or bigram
if cfg.get("remove_false_starts", True):
    i = 0
    while i < len(words) - 1:
        a1, b1 = norm(words[i]), norm(words[i + 1])
        if a1 == b1 and a1 not in keep_tics and len(a1) > 1 and words[i + 1]["s"] - words[i]["e"] < 0.6:
            add(words[i]["s"] - 0.02, words[i + 1]["s"] - cfg["lead_s"], f"repeat:{a1}")
            i += 2
            continue
        if i < len(words) - 3:
            bg1 = (norm(words[i]), norm(words[i + 1]))
            bg2 = (norm(words[i + 2]), norm(words[i + 3]))
            if bg1 == bg2 and words[i + 2]["s"] - words[i + 1]["e"] < 0.6:
                add(words[i]["s"] - 0.02, words[i + 2]["s"] - cfg["lead_s"], f"repeat:{' '.join(bg1)}")
                i += 4
                continue
        i += 1

# apply vetoes, sort, merge overlaps
removals = [r for r in removals if r["id"] not in vetoed]
removals.sort(key=lambda r: r["in"])
merged = []
for r in removals:
    if merged and r["in"] <= merged[-1]["out"] + 1e-6:
        merged[-1]["out"] = max(merged[-1]["out"], r["out"])
        if r["reason"] not in merged[-1]["reason"]:
            merged[-1]["reason"] += "+" + r["reason"]
    else:
        merged.append(dict(r))

# complement → keep; kill slivers by merging tiny keeps back into the neighbouring removal (i.e. drop the removal)
keep = []
cursor = 0.0
for r in merged:
    if r["in"] > cursor:
        keep.append({"in": round(cursor, 3), "out": round(r["in"], 3)})
    cursor = r["out"]
if cursor < duration:
    keep.append({"in": round(cursor, 3), "out": round(duration, 3)})

changed = True
while changed:
    changed = False
    for i, k in enumerate(keep):
        if k["out"] - k["in"] < cfg["min_clip_s"] and len(keep) > 1:
            # merge with the neighbour that costs the smallest re-inclusion of removed audio
            if i + 1 < len(keep):
                keep[i + 1]["in"] = k["in"]
            else:
                keep[i - 1]["out"] = k["out"]
            keep.pop(i)
            changed = True
            break

# recompute removed from the final keep list so stats are exact
removed = []
cursor = 0.0
for k in keep:
    if k["in"] > cursor + 1e-6:
        reason = "+".join(sorted({m["reason"] for m in merged if m["in"] < k["in"] and m["out"] > cursor})) or "silence"
        removed.append({"in": round(cursor, 3), "out": k["in"], "reason": reason})
    cursor = k["out"]
if cursor < duration - 1e-6:
    removed.append({"in": round(cursor, 3), "out": round(duration, 3), "reason": "silence:tail"})

old_zooms = {}
if job.p("cuts.json").exists():
    for k in job.read_json("cuts.json").get("keep", []):
        if k.get("zoom"):
            old_zooms[round(k["in"], 2)] = k["zoom"]
for k in keep:
    k["reason"] = "speech"
    k["lead_s"] = cfg["lead_s"]
    if round(k["in"], 2) in old_zooms:
        k["zoom"] = old_zooms[round(k["in"], 2)]
kept_s = sum(k["out"] - k["in"] for k in keep)
cuts = {
    "source": job.state["source"], "fps": fps, "source_duration_s": duration,
    "keep": keep, "removed": removed, "removal_ids": merged,
    "stats": {"kept_s": round(kept_s, 3), "removed_s": round(duration - kept_s, 3), "clips": len(keep),
              "mean_clip_s": round(kept_s / len(keep), 3) if keep else 0},
}
job.write_json(cuts, "cuts.json")
job.mark("rough_cut", "done", out="cuts.json", kept_s=round(kept_s, 2), cut_s=round(duration - kept_s, 2), clips=len(keep))
job.note("rough_cut", f"{len(keep)} clips, kept {kept_s:.1f}s of {duration:.1f}s, removed {len(merged)} ranges ({len(vetoed)} vetoed)")
print(f"rough-cut: {len(keep)} clips · kept {kept_s:.1f}s · removed {duration-kept_s:.1f}s · mean clip {cuts['stats']['mean_clip_s']}s")

if a.review:
    print("\nREMOVALS (veto with cuts.overrides.json {\"keep_ids\": [...]})")
    for r in merged:
        ws = [w["w"] for w in words if w["s"] >= r["in"] - 0.05 and w["e"] <= r["out"] + 0.05]
        print(f"  {r['id']}  {r['in']:7.2f}–{r['out']:7.2f}  {r['out']-r['in']:5.2f}s  {r['reason']:<18} {' '.join(ws)}")
