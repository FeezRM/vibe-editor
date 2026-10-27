#!/usr/bin/env python3
"""Gate — graphics-plan.json is buildable and honest. Taste is not checked here; that is the editor's job.

Fails on: a graphic with neither `html` nor `preset`, a missing composition file, an unknown preset, invalid preset
params (placeholder text, missing assets), a metric without provenance, a cue outside the timeline, a handle lifted
from samples/. A graphic that carries its own words sets `"mute_captions": true` (or its preset declares
x-mute-captions) and gets a caption mute window.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline  # noqa: E402
import _presets as P  # noqa: E402

job = Job(sys.argv[1])
plan = job.read_json("graphics-plan.json")
tl = Timeline(job.read_json("cuts.json"))
errs = []
gfx = plan.get("graphics", [])
ids = set()
mutes = plan.setdefault("caption_mute_windows", [])
handles = P._sample_handles()

for g in gfx:
    gid = g.get("id", "?")
    if gid in ids:
        errs.append(f"{gid}: duplicate id")
    ids.add(gid)
    for k in ("cue", "duration"):
        if k not in g:
            errs.append(f"{gid}: missing '{k}'")
    if g.get("cue", 0) < 0 or g.get("cue", 0) + g.get("duration", 0) > tl.duration + 0.05:
        errs.append(f"{gid}: cue {g.get('cue')}+{g.get('duration')} outside the {tl.duration:.1f}s timeline")
    mute = bool(g.get("mute_captions"))
    if g.get("html"):
        fp = job.p(g["html"])
        if not fp.exists():
            errs.append(f"{gid}: composition not found: {g['html']}")
        else:
            body = fp.read_text(encoding="utf-8", errors="ignore")
            for h in handles:
                if h and h in body:
                    errs.append(f"{gid}: handle '{h}' from samples/ appears in {g['html']} — use creator.handle")
    elif g.get("preset"):
        try:
            preset = P.load(g["preset"])
        except SystemExit:
            errs.append(f"{gid}: unknown preset '{g['preset']}' (have: {', '.join(P.list_presets())})")
            continue
        sch = preset["schema"]
        for e in P.validate_params(preset, g.get("params", {}), job.dir):
            errs.append(f"{gid}: {e}")
        if sch.get("x-needs-provenance") and not (g.get("provenance") or g.get("params", {}).get("source")):
            errs.append(f"{gid}: a number without provenance — where does it come from?")
        mute = mute or bool(sch.get("x-mute-captions"))
    else:
        errs.append(f"{gid}: needs 'html' (a composition written for this video) or 'preset'")
    if mute and "cue" in g and "duration" in g:
        win = [round(g["cue"], 3), round(g["cue"] + g["duration"], 3)]
        if not any(abs(m[0] - win[0]) < 0.05 and abs(m[1] - win[1]) < 0.05 for m in mutes):
            mutes.append(win)

job.write_json(plan, "graphics-plan.json")
if errs:
    for e in errs:
        print("error:", e)
    job.gate("validate_plan", "fail")
    sys.exit(1)
job.gate("validate_plan", "pass")
print(f"validate-plan: pass · {len(gfx)} graphics · {len(mutes)} mute windows")
