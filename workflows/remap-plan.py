#!/usr/bin/env python3
"""Keep the graphics plan on its words after a re-cut. graphics-plan.json times are TIMELINE seconds; when rough-cut
writes a new EDL (tighter pauses, a removed take) every cue after the change drifts. rough-cut.py keeps the previous
EDL as cuts.prev.json; this maps each plan time old timeline → source → new timeline, so a beat stays on the word it
was cued to. A time whose source moment was cut snaps to the next kept moment. Remapped graphics are marked dirty so
build-graphics re-renders them.

Also assets/bg-plan.json (bg-plate.py segments). Fields moved: graphics[].cue and cue + duration (the end) — timeline times; reveal_at[] and every number in params under a
key named "at" or ending in "_at" — LOCAL to the graphic (sfx-plan adds the cue), so cue + t is mapped and the new cue
subtracted; caption_mute_windows [[a, b], …] and assets/bg-plan.json — timeline times.

Usage: python workflows/remap-plan.py <job>      (no-op when there is no cuts.prev.json or no plan)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline  # noqa: E402

job = Job(sys.argv[1])
if not (job.p("cuts.prev.json").exists() and job.p("graphics-plan.json").exists()):
    sys.exit(0)
old, new = Timeline(job.read_json("cuts.prev.json")), Timeline(job.read_json("cuts.json"))
if [(k["in"], k["out"], k.get("hold", 0)) for k in old.keep] == [(k["in"], k["out"], k.get("hold", 0)) for k in new.keep]:
    print("remap-plan: EDL unchanged")
    sys.exit(0)


def move(t):
    src = old.to_source(float(t))
    if src is None:
        return round(min(float(t), new.duration), 3)
    got = new.to_timeline(src)
    if got is None:                                   # the moment was cut: the next kept moment
        nxt = [(k["in"], off) for k, off in zip(new.keep, new.offsets) if k["in"] >= src]
        got = nxt[0][1] if nxt else new.duration
    return round(got, 3)


def walk(o, f):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool) and (k == "at" or k.endswith("_at")):
                o[k] = f(v)
            else:
                walk(v, f)
    elif isinstance(o, list):
        for v in o:
            walk(v, f)


plan = job.read_json("graphics-plan.json")
for g in plan.get("graphics", []):
    c0 = g["cue"]
    c1 = move(c0)
    end = move(c0 + g["duration"])
    rel = lambda t, c0=c0, c1=c1: round(max(0.0, move(c0 + t) - c1), 3)   # graphic-local: cue + t → new cue + t'
    g["cue"], g["duration"] = c1, round(end - c1, 3)
    g["reveal_at"] = [rel(t) for t in g.get("reveal_at", [])]
    walk(g.get("params", {}), rel)
    g["dirty"] = True
plan["caption_mute_windows"] = [[move(a), move(b)] for a, b in plan.get("caption_mute_windows", [])]
job.write_json(plan, "graphics-plan.json")
print(f"remap-plan: {len(plan.get('graphics', []))} graphics moved {old.duration:.2f}s -> {new.duration:.2f}s timeline")
# the background plan (bg-plate.py) is cued in timeline time as well; its plate must be rebuilt on the new spine
if job.p("assets", "bg-plan.json").exists():
    bg = job.read_json("assets", "bg-plan.json")
    walk(bg, move)
    job.write_json(bg, "assets", "bg-plan.json")
    print("remap-plan: assets/bg-plan.json moved — re-matte the new spine and re-run bg-plate.py")
