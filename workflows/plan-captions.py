#!/usr/bin/env python3
"""Node 03a — captions as data. words.json + cuts.json → captions.json (timeline times).

Groups words into single-line captions (min..max words, ≤ width ceiling, never ending on a glue
word), remaps every time through the EDL, and assigns a lenient default emphasis (numbers and a
small good/bad lexicon, ≤ accent_share_max of groups). The agent may edit captions.json — text,
grouping, accent — before build-captions.py runs; edits survive because the builder reads this
file, not the transcript.

Usage: python workflows/plan-captions.py <job>
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline  # noqa: E402

job = Job(sys.argv[1])
job.require("captions")
C = job.numbers["captions"]
words = job.read_json("transcript", "words.json")
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)

MAX_W = int(C["max_width_frac"] * job.numbers["canvas"]["width"])
CPX = MAX_W / C["chars_per_line"]  # calibrated against a measured render of the caption face
GLUE = {"a", "an", "the", "to", "of", "in", "on", "at", "for", "and", "or", "but", "so", "if", "with", "as",
        "than", "then", "that", "my", "your", "is", "are", "was", "were", "be", "into", "from", "about",
        "let", "cause", "cuz", "because", "which"}
GOOD = {"good", "best", "works", "viral", "win", "won", "achieved", "golden", "free", "easy", "monetize", "profit"}
BAD = {"no", "not", "never", "sucked", "waste", "wrong", "worst", "fail", "failed", "lost", "zero", "nothing", "none"}
REAL = {"a", "i", "o", "ok", "so", "to", "do", "no", "go", "up", "us", "it", "is", "at", "in", "on", "of", "or",
        "my", "me", "we", "he", "by", "am", "an", "as", "be", "if", "hi"}


def low_all(g):
    return " ".join(x["w"] for x in g["words"]).lower()


def width(ws):
    return (sum(len(w) for w in ws) + max(0, len(ws) - 1)) * CPX


def fits(ws):
    return len(ws) <= C["max_words"] and width(ws) <= MAX_W


# 1. keep only words that survived the cut, mapped to timeline time
tw = []
for w in words:
    s, e = tl.to_timeline(w["s"]), tl.to_timeline(w["e"])
    if s is None and e is None:
        continue
    if s is None:
        s = max(0.0, e - (w["e"] - w["s"]))
    if e is None:
        e = min(tl.duration, s + (w["e"] - w["s"]))
    tw.append({**w, "s": round(s, 3), "e": round(max(e, s + 0.05), 3)})

# 2. repair token fragments ('c' + 'uz' → 'cuz')
rep = []
i = 0
while i < len(tw):
    w = dict(tw[i])
    while (i + 1 < len(tw) and len(w["w"]) <= 2 and w["w"].islower() and w["w"].isalpha()
           and w["w"] not in REAL and not w["end_punct"]):
        nxt = tw[i + 1]
        w = {**w, "w": w["w"] + nxt["w"], "e": nxt["e"], "end_punct": nxt.get("end_punct", "")}
        i += 1
    rep.append(w)
    i += 1
tw = rep

# 3. greedy single-line grouping; never cross a sentence end; never end on glue
groups, cur = [], []


def emit():
    if cur:
        groups.append({"words": [dict(x) for x in cur], "s": cur[0]["s"], "e": cur[-1]["e"]})


for wd in tw:
    trial = cur + [wd]
    if cur and not fits([x["w"] for x in trial]):
        held = []
        while len(cur) > 2 and cur[-1]["w"].lower().strip(".,!?’'") in GLUE:
            held.insert(0, cur.pop())
        emit()
        cur = held + [wd]
    else:
        cur = trial
    if wd.get("end_punct") and (wd["end_punct"][0] in ".!?" or (wd["end_punct"][0] == "," and len(cur) >= 2)):
        emit()
        cur = []
emit()

# 4. un-orphan single-word groups unless they are held ≥0.7s
i = 0
while i < len(groups):
    g = groups[i]
    if len(g["words"]) > 1 or g["e"] - g["s"] >= 0.7:
        i += 1
        continue
    nxt = groups[i + 1] if i + 1 < len(groups) else None
    prv = groups[i - 1] if i > 0 else None
    if nxt and fits([x["w"] for x in g["words"] + nxt["words"]]):
        nxt["words"] = g["words"] + nxt["words"]
        nxt["s"] = g["s"]
        groups.pop(i)
        continue
    if prv and fits([x["w"] for x in prv["words"] + g["words"]]):
        prv["words"] += g["words"]
        prv["e"] = g["e"]
        groups.pop(i)
        continue
    if prv and len(prv["words"]) >= 3:
        moved = prv["words"][-1]
        if fits([moved["w"]] + [x["w"] for x in g["words"]]):
            prv["words"] = prv["words"][:-1]
            prv["e"] = prv["words"][-1]["e"]
            g["words"] = [moved] + g["words"]
            g["s"] = moved["s"]
    i += 1

# 5. hold each caption until the next begins (never flicker off), cap the hold
for i, g in enumerate(groups[:-1]):
    g["e"] = max(g["e"], min(groups[i + 1]["s"], g["e"] + 0.35))
if groups:
    groups[-1]["e"] = min(tl.duration, groups[-1]["e"] + 0.3)

# 6. emphasis: the payload word of a phrase in the italic serif (white "em"); colour only for numbers
#    and the bad/good lexicon. ≤ accent_share_max of groups, never two accented groups in a row.
budget = int(len(groups) * C["accent_share_max"])
last_accented = -2
for i, g in enumerate(groups):
    g["idx"] = i
    g["text"] = " ".join(x["w"] + x["end_punct"] for x in g["words"])
    g["accent"] = None
    g["hook"] = i == 0 and 2 <= len(g["words"]) <= 3
    if budget <= 0 or i - last_accented < 2:
        continue
    pick = None
    for x in g["words"]:
        base = x["w"].lower().strip(".,!?’'")
        if re.search(r"\d", base) or base.startswith("$"):
            pick = {"word": x["w"], "cls": "good" if ("$" in base or "k" in base or "revenue" in low_all(g)) else "hot"}
            break
        if base in BAD:
            pick = {"word": x["w"], "cls": "bad"}
            break
        if base in GOOD:
            pick = {"word": x["w"], "cls": "good"}
            break
    if pick is None:
        content = [x for x in g["words"] if len(x["w"].strip(".,!?’'")) >= 5 and x["w"].lower().strip(".,!?’'") not in GLUE]
        if content:
            pick = {"word": max(content, key=lambda x: len(x["w"]))["w"], "cls": "em"}
    if pick:
        g["accent"] = pick
        budget -= 1
        last_accented = i

for g in groups:
    g["words"] = [{"w": x["w"], "s": x["s"], "e": x["e"], "end_punct": x.get("end_punct", "")} for x in g["words"]]

out = {"duration": round(tl.duration, 3), "groups": groups, "mute_windows": []}
job.write_json(out, "captions.json")
n_acc = sum(1 for g in groups if g["accent"])
avg = sum(len(g["words"]) for g in groups) / max(1, len(groups))
job.note("captions", f"planned {len(groups)} groups, {avg:.1f} words avg, {n_acc} accented")
print(f"plan-captions: {len(groups)} groups · {avg:.1f} words avg · {n_acc} accented · {tl.duration:.1f}s → captions.json")
