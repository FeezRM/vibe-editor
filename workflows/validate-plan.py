#!/usr/bin/env python3
"""Gate — graphics-plan.json is buildable and honest.

Fails on: unknown preset, invalid params, placeholder text in x-real params, missing assets, a metric
without provenance, overlapping graphics on the same placement, cues outside the timeline, a caption
mute missing for a preset that carries its own words (x-mute-captions), four+ consecutive uses of one
preset. Warns on: presence below graphics.min_presence, a static stretch over pacing.max_static_s,
three consecutive uses of one preset. Lenient by design: warnings never block.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline  # noqa: E402
import _presets as P  # noqa: E402

job = Job(sys.argv[1])
plan = job.read_json("graphics-plan.json")
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)
G, PC = job.numbers["graphics"], job.numbers["pacing"]
errs, warns = [], []
gfx = plan.get("graphics", [])
ids = set()
mutes = plan.setdefault("caption_mute_windows", [])

for g in gfx:
    gid = g.get("id", "?")
    if gid in ids:
        errs.append(f"{gid}: duplicate id")
    ids.add(gid)
    for k in ("preset", "cue", "duration"):
        if k not in g:
            errs.append(f"{gid}: missing '{k}'")
    if "preset" not in g:
        continue
    try:
        preset = P.load(g["preset"])
    except SystemExit:
        errs.append(f"{gid}: unknown preset '{g['preset']}'")
        continue
    sch = preset["schema"]
    for e in P.validate_params(preset, g.get("params", {}), job.dir):
        errs.append(f"{gid}: {e}")
    if g.get("cue", 0) < 0 or g.get("cue", 0) + g.get("duration", 0) > tl.duration + 0.05:
        errs.append(f"{gid}: cue {g.get('cue')}+{g.get('duration')} outside the {tl.duration:.1f}s timeline")
    if g.get("duration", 0) < G["hold_min_s"] + 0.3:
        errs.append(f"{gid}: duration {g.get('duration')}s too short to enter and hold")
    if sch.get("x-needs-provenance") and not (g.get("provenance") or g.get("params", {}).get("source")):
        errs.append(f"{gid}: metric without provenance — where does the number come from?")
    if sch.get("x-mute-captions"):
        win = [g["cue"], g["cue"] + g["duration"]]
        if not any(abs(m[0] - win[0]) < 0.05 and abs(m[1] - win[1]) < 0.05 for m in mutes):
            mutes.append([round(win[0], 3), round(win[1], 3)])
    pl = g.get("placement", "auto")
    allowed = sch.get("x-placements", [])
    if pl != "auto" and allowed and pl not in allowed:
        errs.append(f"{gid}: placement '{pl}' not allowed for {g['preset']} ({allowed})")
    if pl == "cutaway" or (pl == "auto" and sch.get("x-default-placement") == "cutaway"):
        if not sch.get("x-no-content"):
            win = [g["cue"], g["cue"] + g["duration"]]
            if not any(m[0] <= win[0] + 0.05 and m[1] >= win[1] - 0.05 for m in mutes):
                warns.append(f"{gid}: full-frame {g['preset']} with captions still on — consider a mute window")

# overlaps on the same resolved placement family
def fam(g):
    p = g.get("placement", "auto")
    if p == "auto":
        p = P.load(g["preset"])["schema"].get("x-default-placement", "beside-r")
    return "beside" if p.startswith("beside") else p

sorted_g = sorted([g for g in gfx if "cue" in g], key=lambda g: g["cue"])
for i, g in enumerate(sorted_g):
    for h in sorted_g[i + 1:]:
        if h["cue"] >= g["cue"] + g["duration"]:
            break
        if fam(g) == fam(h) and fam(g) != "wash":
            errs.append(f"{g['id']} and {h['id']} overlap on '{fam(g)}' ({g['cue']:.2f}–{g['cue']+g['duration']:.2f} vs {h['cue']:.2f})")

# repeats
run, prev = 0, None
for g in sorted_g:
    run = run + 1 if g["preset"] == prev else 1
    prev = g["preset"]
    if run == 3:
        warns.append(f"{g['id']}: third consecutive '{g['preset']}' — vary the device")
    if run >= 4:
        errs.append(f"{g['id']}: fourth consecutive '{g['preset']}'")

# presence and static stretches (captions count as change events)
cov = [(g["cue"], g["cue"] + g["duration"]) for g in sorted_g]
merged = []
for s, e in sorted(cov):
    if merged and s <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], e))
    else:
        merged.append((s, e))
presence = sum(e - s for s, e in merged) / tl.duration if tl.duration else 0
if presence < G["min_presence"]:
    warns.append(f"graphic presence {presence:.0%} < {G['min_presence']:.0%} of runtime")

# show, don't caption: graphics that are only words (phrase, list-card, flow, metric, chat) may carry at most
# graphics.max_text_share of the graphic time. The captions already carry the words; the layer's job is to SHOW.
text_presets = set(G.get("text_presets", []))
gfx_time = sum(g["duration"] for g in sorted_g) or 1.0
text_time = sum(g["duration"] for g in sorted_g if g["preset"] in text_presets)
text_share = text_time / gfx_time
if sorted_g and text_share > G.get("max_text_share", 1.0):
    errs.append(f"text-only presets carry {text_share:.0%} of graphic time (max {G['max_text_share']:.0%}) — show the noun: "
                f"app-mock / receipt / thumb-wall / rec-frame + zoom / wash, or build nothing")

# variety: the viewer is bored by the same kind of thing twice. Every preset belongs to a visual family
# (graphics.families); a family never runs twice in a row, appears at most max_family_uses times and only as a
# callback separated by callback_gap other graphics, no asset file appears in more than max_asset_uses graphics,
# and a reel with ≥ min_families graphics shows at least that many different families. Floods and footage are exempt.
FAM = G.get("families", {})
V = G.get("variety", {})
if V:
    exempt = set(V.get("exempt", []))
    seq = [(g["id"], FAM.get(g["preset"], g["preset"])) for g in sorted_g if FAM.get(g["preset"], g["preset"]) not in exempt]
    for (a_id, a_f), (b_id, b_f) in zip(seq, seq[1:]):
        if a_f == b_f:
            errs.append(f"{a_id} → {b_id}: two '{a_f}' visuals in a row — show a different kind of thing")
    seen = {}
    for i, (gid, fam) in enumerate(seq):
        if fam in seen:
            uses, last = seen[fam]
            if uses >= V.get("max_family_uses", 2):
                errs.append(f"{gid}: '{fam}' used {uses + 1} times — a family returns once, as a callback, not as a habit")
            elif i - last <= V.get("callback_gap", 2):
                errs.append(f"{gid}: '{fam}' returns after only {i - last - 1} other graphics — a callback needs ≥ {V.get('callback_gap', 2)} between")
            seen[fam] = (uses + 1, i)
        else:
            seen[fam] = (1, i)
    fams = {f for _, f in seq}
    if len(seq) >= V.get("min_families", 4) and len(fams) < V.get("min_families", 4):
        errs.append(f"only {len(fams)} visual families across {len(seq)} graphics (min {V.get('min_families', 4)}): {sorted(fams)}")
    # asset reuse, by file
    def assets_of(v):
        if isinstance(v, str) and v.startswith("assets/"):
            yield v
        elif isinstance(v, dict):
            for x in v.values(): yield from assets_of(x)
        elif isinstance(v, list):
            for x in v: yield from assets_of(x)
    uses = {}
    for g in sorted_g:
        for a in set(assets_of(g.get("params", {}))):
            uses.setdefault(a, []).append(g["id"])
    for a, ids in uses.items():
        if len(ids) > V.get("max_asset_uses", 2):
            errs.append(f"{a} appears in {len(ids)} graphics ({', '.join(ids)}) — max {V.get('max_asset_uses', 2)}; find other real material")

events = set()
if job.p("captions.json").exists():
    events.update(round(g["s"], 2) for g in job.read_json("captions.json")["groups"])
for g in sorted_g:
    events.add(round(g["cue"], 2))
    for r in g.get("reveal_at", []):
        events.add(round(g["cue"] + r, 2))
for k in tl.offsets:
    events.add(round(k, 2))
ev = sorted(events)
gaps = [(ev[i], ev[i + 1] - ev[i]) for i in range(len(ev) - 1) if ev[i + 1] - ev[i] > PC["max_static_s"]]
for t, d in gaps[:8]:
    warns.append(f"static stretch {d:.1f}s from {t:.1f}s")

job.write_json(plan, "graphics-plan.json")
for w in warns:
    print("warn:", w)
if errs:
    for e in errs:
        print("error:", e)
    job.gate("validate_plan", "fail")
    sys.exit(1)
job.gate("validate_plan", "pass")
print(f"validate-plan: pass · {len(gfx)} graphics · presence {presence:.0%} · text {text_share:.0%} · families {len({FAM.get(g['preset'], g['preset']) for g in sorted_g})} · {len(mutes)} mute windows · {len(warns)} warnings")
