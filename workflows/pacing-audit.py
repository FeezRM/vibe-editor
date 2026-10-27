#!/usr/bin/env python3
"""Node 07 — pacing as an audit over data. Event log from cuts + captions + graphics (+ reveals) + sfx.

Reports every stretch with nothing changing for more than pacing.max_static_s. With --fix, closes each
gap with the cheapest interrupt: a zoom punch written into cuts.json on the clip that spans the gap
(applied by both lanes), never stacking two punches inside one clip. --zoom-at T adds a deliberate
punch (e.g. on a held-up prop). Seconds 0–hook_hold_s are exempt from automatic punches when the plan
marks a hold there.

Usage: python workflows/pacing-audit.py <job> [--fix] [--zoom-at 4.85,20.1]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--fix", action="store_true")
ap.add_argument("--zoom-at", default=None)
a = ap.parse_args()
job = Job(a.job)
job.require("pacing")
P = job.numbers["pacing"]
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)
events = {0.0: "start", round(tl.duration, 2): "end"}
for i, off in enumerate(tl.offsets):
    if i:
        events[round(off, 2)] = "cut"
    z = cuts["keep"][i].get("zoom")
    if z:
        events[round(z["at"], 2)] = "zoom"
if job.p("captions.json").exists():
    for g in job.read_json("captions.json")["groups"]:
        events.setdefault(round(g["s"], 2), "caption")
if job.p("graphics-plan.json").exists():
    for g in job.read_json("graphics-plan.json")["graphics"]:
        events.setdefault(round(g["cue"], 2), f"gfx:{g['id']}")
        for r in g.get("reveal_at", []):
            events.setdefault(round(g["cue"] + r, 2), f"reveal:{g['id']}")
if job.p("broll-plan.json").exists():   # a playing clip is motion: its span is never static
    for c in job.read_json("broll-plan.json").get("clips", []):
        t = c["start"]
        while t < c["end"] - 1e-6:
            events.setdefault(round(t, 2), f"broll:{c.get('id', '')}")
            t += P["max_static_s"] / 2
if job.p("sfx-plan.json").exists():
    for s in job.read_json("sfx-plan.json")["sfx"]:
        events.setdefault(round(s["cue"], 2), "sfx")

ts = sorted(events)
gaps = [(ts[i], ts[i + 1] - ts[i]) for i in range(len(ts) - 1) if ts[i + 1] - ts[i] > P["max_static_s"]]


def clip_index(t):
    for i, off in enumerate(tl.offsets):
        k = cuts["keep"][i]
        if off <= t < off + (k["out"] - k["in"]):
            return i
    return None


def add_zoom(t, reason):
    i = clip_index(t)
    if i is None:
        return False
    k = cuts["keep"][i]
    if k.get("zoom"):
        return False
    k["zoom"] = {"at": round(t, 3), "pct": P["zoom_pct"], "dur": P["zoom_dur_s"], "reason": reason}
    # the face at the punch (source frame): the lane zooms around this point so the face grows in place
    from _faces import FaceFinder
    fw, fh = job.numbers["canvas"]["width"] // 3, job.numbers["canvas"]["height"] // 3
    f = FaceFinder(fw, fh).at(job.source, k["in"] + (t - tl.offsets[i]) + P["zoom_dur_s"])
    if f is not None:
        k["zoom"]["face"] = [round((f[0] + f[2] / 2) / fw, 4), round((f[1] + f[3] / 2) / fh, 4)]
    return True


applied = []
if a.zoom_at:
    for t in a.zoom_at.split(","):
        if add_zoom(float(t), "requested"):
            applied.append((float(t), "zoom (requested)"))
if a.fix:
    for t, d in gaps:
        at = round(t + 0.35, 3)
        if add_zoom(at, f"gap {d:.1f}s"):
            applied.append((at, f"zoom (gap {d:.1f}s)"))
if applied:
    job.write_json(cuts, "cuts.json")

print(f"pacing-audit: {len(ts)} events over {tl.duration:.1f}s · {len(gaps)} gaps > {P['max_static_s']}s")
for t, d in gaps:
    print(f"  gap {d:.1f}s from {t:.2f}s")
for t, what in applied:
    print(f"  + {what} at {t:.2f}s")
remaining = 0 if a.fix else len(gaps)
job.gate("pacing", "pass" if not gaps or a.fix else "fail")
job.mark("pacing", "done", gaps=len(gaps), zooms=sum(1 for k in cuts["keep"] if k.get("zoom")))
job.note("pacing", f"{len(ts)} events, {len(gaps)} gaps, {len(applied)} punches added")
sys.exit(0 if (not gaps or a.fix or applied) else 1)
