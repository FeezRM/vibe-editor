#!/usr/bin/env python3
"""Node 06b — SFX derived from the PLACED graphics. graphics-plan.json → sfx-plan.json

One sound per visual event, never per word: each graphic's entrance and each of its reveal events
gets the verb its preset declares (or the plan's `sfx` override), mapped through presets/.../sfx.json
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

# entrance verb and per-event verb per preset; priority: higher survives the density cap
VERBS = {
    "phrase":     ("pop",     None,     3),
    "list-card":  ("whoosh",  "click",  2),
    "flow":       ("slide",   "slide",  2),
    "thumb-wall": ("whoosh",  None,     2),
    "app-mock":   ("whoosh",  "click",  2),
    "chat":       ("pop",     "pop",    3),
    "metric":     ("tick",    "ding",   3),
    "wash":       (None,      None,     1),
    "receipt":    ("shutter", None,     2),
    "rec-frame":  ("click",   None,     1),
    # demonstration presets: the entrance, then one hit per reveal (slash, feed, drop, break, merge, stamp, send)
    "script-cut": ("whoosh",  "slide",  3),
    "transform":  ("pop",     "whoosh", 2),
    "drag-drop":  ("click",   "pop",    2),
    "dead-space": ("whoosh",  "wrong",  3),
    "layer-stack":("slide",   "pop",    2),
    "stamp":      ("tick",    "ding",   3),
    "phone-play": ("whoosh",  "pop",    2),
    "comment":    ("pop",     "click",  3),
    "shatter":    ("riser",   "wrong",  3),
    "split":      ("pop",     "tick",   3),
    "pixel-quest":("pop",     "ding",   3),   # spawn pop; the bonk and the landing ding
    "pixel-crowd":("pop",     "ding",   3),
    "agent-chat": ("whoosh",  "pop",    3),
    "ad-stack":   ("pop",     "whoosh", 3),   # each ad slams onto the pile
    "bot-team":   ("pop",     "pop",    3),
    "bg-swap":    (None,      "whoosh", 3),   # every background switch whooshes   # the team scene: a plan's sfx_events picks a verb per beat   # the phone slams up; each send / reply pops (a plan's sfx_events can vary it)
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
    enter, per_event, prio = VERBS.get(g["preset"], ("pop", None, 1))
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
            if g["preset"] == "metric":
                # the ding lands when the count finishes
                r = r + float(g.get("params", {}).get("count_s", 1.2))
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
