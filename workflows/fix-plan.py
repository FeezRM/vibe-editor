#!/usr/bin/env python3
"""Review loop — deterministic remedies for graphics-qa defects. Edits graphics-plan.json, never a preset.

  face-overlap  beside-l ⇄ beside-r; if both sides were tried (or top) → inline if allowed → drop
  caption-band  → inline if allowed (below the band) → cutaway + mute window if allowed → drop
  luma          → drop
  blank / missing-render / stale-render / no-alpha → mark dirty (rebuild)
  rgba-surface  → drop (a preset bug — report it)

An agent in the loop can do better (re-plan the beat); this exists so a one-shot run converges.

Usage: python workflows/fix-plan.py <job> <review/qa-round-N.json>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job  # noqa: E402
import _presets as P  # noqa: E402

job = Job(sys.argv[1])
report = job.read_json(sys.argv[2]) if not Path(sys.argv[2]).is_absolute() else __import__("json").loads(Path(sys.argv[2]).read_text())
plan = job.read_json("graphics-plan.json")
by_id = {g["id"]: g for g in plan["graphics"]}
mutes = plan.setdefault("caption_mute_windows", [])
notes = plan.setdefault("notes", [])
changed, dropped = [], []


def drop(g, why):
    plan["graphics"] = [x for x in plan["graphics"] if x["id"] != g["id"]]
    dropped.append(g["id"])
    notes.append(f"{g['id']} {g['preset']} dropped by fix-plan: {why}")


for d in report["defects"]:
    g = by_id.get(d["id"])
    if not g or g["id"] in dropped:
        continue
    allowed = P.load(g["preset"])["schema"].get("x-placements", [])
    pl = g.get("placement_resolved", g.get("placement", "auto"))
    tried = set(g.setdefault("tried_placements", [pl]))
    kind = d["kind"]
    if kind in ("blank", "missing-render", "stale-render", "no-alpha"):
        g["dirty"] = True
        changed.append(f"{g['id']}: rebuild ({kind})")
    elif kind == "face-overlap":
        other = "beside-r" if pl == "beside-l" else "beside-l"
        if pl.startswith("beside") and other not in tried and other in allowed:
            g["placement"] = other; tried.add(other); g["dirty"] = True
            changed.append(f"{g['id']}: flip to {other}")
        elif "inline" in allowed and "inline" not in tried:
            g["placement"] = "inline"; tried.add("inline"); g["dirty"] = True
            changed.append(f"{g['id']}: move inline")
        else:
            drop(g, "covers the face on every allowed placement")
    elif kind == "caption-band":
        if "inline" in allowed and "inline" not in tried:
            g["placement"] = "inline"; tried.add("inline"); g["dirty"] = True
            changed.append(f"{g['id']}: move inline (below the band)")
        elif "cutaway" in allowed and "cutaway" not in tried:
            g["placement"] = "cutaway"; tried.add("cutaway"); g["dirty"] = True
            mutes.append([round(g["cue"], 3), round(g["cue"] + g["duration"], 3)])
            changed.append(f"{g['id']}: cutaway + caption mute")
        else:
            drop(g, "content in the caption band on every allowed placement")
    elif kind == "luma":
        drop(g, d["msg"])
    elif kind == "rgba-surface":
        drop(g, f"preset bug: {d['msg'][:60]}")
    g["tried_placements"] = sorted(tried)

job.write_json(plan, "graphics-plan.json")
for c in changed:
    print("fix:", c)
for i in dropped:
    print("drop:", i)
print(f"fix-plan: {len(changed)} changes, {len(dropped)} dropped")
