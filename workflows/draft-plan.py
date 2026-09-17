#!/usr/bin/env python3
"""Node 05a — draft graphics-plan.json from captions.json (timeline times) with the basic-tier presets.

Heuristics, in priority order per beat:
  a spoken number            → metric (provenance = the spoken line)
  "comment <WORD>" / "DM"    → chat (the literal CTA)
  a list of 3+ nouns         → list-card (rows = the spoken items)
  a URL / app name           → app-mock IF a screenshot exists in assets/ (else a note in RUN.md: capture it)
  "look" / "see this" / REC  → rec-frame
  a strong negative → positive turn → wash pair
  the opening line           → phrase (hook lockup, captions muted)
Cues are the group start times; durations run to the next beat, clamped. The agent edits the result
before validate-plan / build. Never invents an asset: presets that need a file are only drafted
when the file is already in assets/.

Usage: python workflows/draft-plan.py <job> [--force]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline, now  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--force", action="store_true")
a = ap.parse_args()
job = Job(a.job)
job.require("graphics")
if job.p("graphics-plan.json").exists() and not a.force:
    print("graphics-plan.json exists (use --force to redraft)")
    sys.exit(0)
G = job.numbers["graphics"]
caps = job.read_json("captions.json")["groups"]
tl = Timeline(job.read_json("cuts.json"))
handle = job.brand.get("creator", {}).get("handle", "")
assets = {p.name.lower(): f"assets/{p.name}" for p in job.p("assets").glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")}

NEG = {"no", "not", "never", "none", "nothing", "zero", "failed", "wrong", "sucked", "waste"}
POS = {"achieved", "soon", "best", "works", "viral", "golden", "win", "free", "easy", "good"}
NUM = re.compile(r"(\$?\d[\d,.]*)\s*(k|m|%|x)?", re.I)

gfx, notes = [], []
used_until = 0.0


def add(preset, cue, dur, params, provenance, placement="auto", reveal=None, trigger=""):
    global used_until
    # a new beat wins: shorten the previous graphic to make room, as long as it still enters and holds
    if gfx and cue < used_until:
        prev = gfx[-1]
        room = cue - 0.15 - prev["cue"]
        if room >= G["hold_min_s"] + 0.45:
            prev["duration"] = round(room, 3)
            used_until = prev["cue"] + prev["duration"] + 0.15
    cue = round(max(cue, used_until), 3)
    dur = round(min(dur, tl.duration - cue - 0.05), 3)
    if dur < G["hold_min_s"] + 0.4:
        return
    g = {"id": f"g{len(gfx)+1:02d}", "preset": preset, "cue": cue, "duration": dur, "trigger": trigger,
         "placement": placement, "params": params, "provenance": provenance}
    if reveal:
        g["reveal_at"] = reveal
    gfx.append(g)
    used_until = cue + dur + 0.25


text_all = " ".join(g["text"] for g in caps).lower()

# 1. opening phrase: the first 2 groups become a two-line lockup
if caps:
    g0 = caps[0]
    g1 = caps[1] if len(caps) > 1 else None
    def line(ws):
        out = [{"t": w["w"]} for w in ws][:4]
        content = [i for i, w in enumerate(out) if len(w["t"].strip(".,!?")) >= 5]
        if content:
            out[content[-1]]["acc"] = "em"   # the payload word in the italic serif
        return out
    l1 = line(g0["words"])
    l2 = line(g1["words"]) if g1 else []
    num_soon = any(NUM.search(c["text"]) for c in caps[1:4])
    if num_soon:
        l2, g1 = [], None
    end = (g1["e"] if g1 else g0["e"])
    add("phrase", g0["s"], min(max(end - g0["s"], 1.3), 3.0), {"line_1": l1, "line_2": l2}, "spoken opening line",
        placement="inline", reveal=[round(g1["s"] - g0["s"], 3)] if g1 else None, trigger=g0["text"])

# 2. walk the beats
i = 0
while i < len(caps):
    g = caps[i]
    t, txt = g["s"], g["text"]
    low = txt.lower()
    nxt_end = caps[min(i + 2, len(caps) - 1)]["e"]
    m = NUM.search(txt)
    if m and t > used_until - 0.6:
        raw = m.group(1).replace(",", "")
        val = float(re.sub(r"[^\d.]", "", raw) or 0)
        unit = (m.group(2) or "").lower()
        prefix = "$" if raw.startswith("$") or "dollar" in low or (unit == "k" and "k" in low) else ""
        after = " ".join(w["w"] for w in g["words"] if w["s"] > g["words"][0]["s"]).lower()
        unit_txt = {"k": "k", "m": "M", "%": "%", "x": "x"}.get(unit, "")
        per = re.search(r"per (\w+)|a (month|week|day|year)", (txt + " " + (caps[i + 1]["text"] if i + 1 < len(caps) else "")).lower())
        if per:
            unit_txt += f" / {per.group(1) or per.group(2)}"
        add("metric", t, min(nxt_end - t, 3.2), {"value": val, "prefix": prefix, "unit": unit_txt,
                                                  "source": f"spoken at {t:.1f}s: “{txt}”"}, f"spoken at {t:.1f}s", trigger=txt)
        i += 1
        continue
    low2 = low + " " + (caps[i + 1]["text"].lower() if i + 1 < len(caps) else "")
    cm = re.search(r"comment\s+[\"“']?(\w+)", low2)
    if cm and t > used_until - 0.6:
        word = cm.group(1).upper()
        add("chat", t, min(nxt_end - t + 0.6, 3.5), {"name": handle or "you", "messages": [
            {"from": "them", "text": word}, {"from": "me", "text": "sent ✅"}]}, "the spoken CTA", reveal=[0.3, 1.3], trigger=txt)
        i += 1
        continue
    if re.search(r"\b(look|see this|watch this|check this|recorded|recording)\b", low) and t > used_until - 0.6:
        add("rec-frame", t, min(caps[min(i + 1, len(caps) - 1)]["e"] - t, 2.4), {}, "deictic line", placement="cutaway", trigger=txt)
        i += 1
        continue
    words_neg = [w["w"].lower().strip(".,!?") for w in g["words"] if w["w"].lower().strip(".,!?") in NEG]
    if words_neg and t > used_until - 0.6:
        # find the positive turn within the next 6 groups
        j = next((k for k in range(i + 1, min(i + 7, len(caps))) if any(w["w"].lower().strip(".,!?") in POS for w in caps[k]["words"])), None)
        if j:
            dur = min(caps[j]["e"] - t, 6.0)
            add("wash", t, dur, {"pair": [{"cls": "bad"}, {"cls": "good"}]}, "negative → positive turn", placement="wash",
                reveal=[0.0, round(caps[j]["s"] - t, 3)], trigger=txt)
            i = j + 1
            continue
    # list of items: 3+ comma-separated nouns across this and the next groups
    span = " ".join(caps[k]["text"] for k in range(i, min(i + 4, len(caps))))
    items = [s.strip(" .") for s in re.split(r",|\band\b", span) if 2 < len(s.strip(" .")) < 28 and len(s.split()) <= 3]
    if len(items) >= 3 and span.count(",") >= 2 and re.search(r"\b(like|such as|including)\b|:", span) and t > used_until - 0.6:
        rows = [{"text": it[0].upper() + it[1:], "mark": "check"} for it in items[:5]]
        # reveal each row at the group where its first word is spoken
        reveal = []
        for r in rows:
            first = r["text"].split()[0].lower().strip(".,")
            k = next((k for k in range(i, min(i + 4, len(caps))) if first in caps[k]["text"].lower()), i)
            reveal.append(round(max(0.2, caps[k]["s"] - t), 3))
        end = caps[min(i + 3, len(caps) - 1)]["e"]
        add("list-card", t, min(end - t + 0.8, 6.0), {"rows": rows}, "spoken list", reveal=sorted(reveal), trigger=txt)
        i += 4
        continue
    um = re.search(r"([a-z0-9-]+\.(me|com|io|app|ai))", low)
    if um and t > used_until - 0.6:
        key = next((k for k in assets if um.group(1).split(".")[0] in k), None)
        if key:
            add("app-mock", t, min(nxt_end - t + 0.5, 4.0), {"screenshot": assets[key], "scroll_px": 200}, f"captured {um.group(1)}",
                reveal=[0.5], trigger=txt)
        else:
            notes.append(f"asset needed: a screenshot of {um.group(1)} (assets/) for an app-mock at {t:.1f}s")
        i += 1
        continue
    i += 1

plan = {"tier": job.state.get("tier", "basic"), "drafted": now(), "graphics": gfx, "caption_mute_windows": [], "notes": notes}
job.write_json(plan, "graphics-plan.json")
for n in notes:
    job.note("graphics", n)
pres = sum(g["duration"] for g in gfx) / tl.duration if tl.duration else 0
print(f"draft-plan: {len(gfx)} graphics · presence {pres:.0%} · {len(notes)} asset notes → graphics-plan.json")
for g in gfx:
    print(f"  {g['id']} {g['preset']:<10} {g['cue']:6.2f}+{g['duration']:.1f}s  «{g['trigger'][:40]}»")
for n in notes:
    print("  note:", n)
