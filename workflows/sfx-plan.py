#!/usr/bin/env python3
"""Node 06b — SFX derived from the PLACED graphics. graphics-plan.json → sfx-plan.json

Sound on the visual events, never per word: a kept preset's entrance and reveal events get the verb it declares,
a composition written for the video only what the plan asks for (`sfx`, `sfx_events`), mapped through presets/.../sfx.json
to a file in the job's assets/sfx/ (copied from the preset pack if absent). Density-capped at
audio.max_sfx_per_10s by dropping the lowest-priority events. Music is opt-in: only when the brief
names a file that exists in audio/.

Usage: python workflows/sfx-plan.py <job>
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job, Timeline, preset_file  # noqa: E402

job = Job(sys.argv[1])
job.require("audio")
A = job.numbers["audio"]
_preset = job.state.get("preset", "vertical/default")
verb_map = __import__("json").loads(preset_file(_preset, "sfx.json").read_text())
plan = job.read_json("graphics-plan.json")
tl = Timeline(job.read_json("cuts.json"))

# entrance verb and per-event verb for the kept presets; priority: higher survives the density cap. A composition written
# for the video (`html`) gets sound only where the plan asks for it: `sfx` (entrance) and `sfx_events` (one per reveal_at).
VERBS = {
    "thumb-wall": ("whoosh",  None,     2),
    "app-mock":   ("whoosh",  "click",  2),
    "receipt":    ("shutter", None,     2),
    "comment":    ("pop",     "click",  3),
}

sfx_dir = job.p("assets", "sfx")
sfx_dir.mkdir(parents=True, exist_ok=True)


def resolve(verb):
    fn = verb_map.get(verb)
    if not fn:
        return None
    dst = sfx_dir / fn
    if not dst.exists():
        src = preset_file(_preset, "sfx") / fn
        if src.exists():
            shutil.copy2(src, dst)
        else:
            return None
    return f"assets/sfx/{fn}"


events = []
for g in plan["graphics"]:
    enter, per_event, prio = VERBS.get(g.get("preset"), (None, None, 2))
    if g.get("sfx") is not None:
        enter = g["sfx"] or None
    if enter:
        f = resolve(enter)
        if f:
            events.append({"cue": round(g["cue"], 3), "verb": enter, "file": f, "graphic": g["id"], "prio": prio, "db": A["sfx_db"]})
    ev_verbs = g.get("sfx_events")   # optional: one verb (or null) per reveal_at entry, for presets with mixed events
    if per_event or ev_verbs:
        for i, r in enumerate(g.get("reveal_at", [])):
            if i == 0 and r < 0.2:
                continue  # coincides with the entrance
            verb = ev_verbs[i] if ev_verbs and i < len(ev_verbs) else per_event
            if not verb:
                continue
            f = resolve(verb)
            if f:
                events.append({"cue": round(g["cue"] + r, 3), "verb": verb, "file": f, "graphic": g["id"], "prio": prio - 1, "db": A["sfx_db"] - 3})

# density cap per rolling 10s window: drop lowest priority first
events.sort(key=lambda e: e["cue"])
kept = []
for e in events:
    window = [k for k in kept if e["cue"] - 10 < k["cue"] <= e["cue"]]
    if len(window) >= A["max_sfx_per_10s"]:
        lowest = min(window, key=lambda k: k["prio"])
        if lowest["prio"] < e["prio"]:
            kept.remove(lowest)
        else:
            continue
    # never two hits within 120ms
    if kept and e["cue"] - kept[-1]["cue"] < 0.12:
        continue
    kept.append(e)

music = None
brief = job.brief
mfiles = [p for p in job.p("audio").glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".aac", ".flac")]
if mfiles and re.search(r"\bmusic\b|\btrack\b|\bsong\b", brief, re.I):
    mf = mfiles[0]
    first_gfx = min((g["cue"] for g in plan["graphics"]), default=2.0)
    music = {"file": f"audio/{mf.name}", "onset_s": 0.0, "db": A["music_db"], "hook_db": A["music_hook_db"],
             "hook_end_s": round(max(1.5, min(first_gfx, 4.0)), 3)}

out = {"sfx": kept, "dropped": len(events) - len(kept), "music": music}
job.write_json(out, "sfx-plan.json")
job.note("audio", f"sfx: {len(kept)} hits ({len(events)-len(kept)} dropped by density cap); music {'on' if music else 'off (opt-in)'}")
print(f"sfx-plan: {len(kept)} hits, {len(events)-len(kept)} dropped · music {'on: ' + music['file'] if music else 'off'} → sfx-plan.json")
for e in kept:
    print(f"  {e['cue']:6.2f}  {e['verb']:<8} {e['graphic']}")
