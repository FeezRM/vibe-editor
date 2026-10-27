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
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)
# the spine transcript (transcribe.py --spine) is already in timeline time and is what the viewer hears;
# the raw transcript is remapped through the EDL and loses/shifts words near cuts on multi-take raws
spine_w, spine_v = job.p("transcript", "spine-words.json"), job.p("preview", "spine.mp4")
spine_k = job.p("transcript", "spine-words.key")
if spine_w.exists() and spine_k.exists():          # the words belong to this cut (keep ranges), whatever the file times
    import hashlib
    import json as _json
    _keys = [[k["in"], k["out"], k.get("hold", 0.0)] for k in cuts["keep"]]
    USE_SPINE = spine_k.read_text().strip() == hashlib.sha1(_json.dumps(_keys).encode()).hexdigest()
else:
    USE_SPINE = spine_w.exists() and (not spine_v.exists() or spine_w.stat().st_mtime >= spine_v.stat().st_mtime)
words = job.read_json("transcript", "spine-words.json" if USE_SPINE else "words.json")

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
    if USE_SPINE:
        if w["s"] < tl.duration:
            tw.append({**w, "s": round(w["s"], 3), "e": round(min(max(w["e"], w["s"] + 0.05), tl.duration), 3)})
        continue
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

# 2b. numbers back to digits for display. The transcript spells them out (transcript.suppress_numerals: the aligner
#     cannot time "30%"), a caption reads "30%". A run merges into one word spanning its time; a lone small number
#     word ("the best one") stays a word unless "percent" follows it.
UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                       "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
SCALE = {"hundred": 100, "thousand": 1000, "million": 1000000}


def numword(w):
    return w["w"].lower().strip(".,!?").replace("-", " ")


def is_num(w):
    return all(p in UNITS or p in TENS or p in SCALE for p in numword(w).split())


out_w, i = [], 0
while i < len(tw):
    j = i
    while j < len(tw) and is_num(tw[j]) and (j == i or not tw[j - 1]["end_punct"]):
        j += 1
    pct = j < len(tw) and j > i and numword(tw[j]) == "percent"
    run = tw[i:j]
    big = any(p in TENS or p in SCALE or (p in UNITS and UNITS[p] >= 10) for w in run for p in numword(w).split())
    if run and (pct or big or len(run) > 1):
        total, cur_n = 0, 0
        for p in " ".join(numword(w) for w in run).split():
            if p in SCALE:
                cur_n = max(cur_n, 1) * SCALE[p]
                if SCALE[p] >= 1000:
                    total, cur_n = total + cur_n, 0
            else:
                cur_n += UNITS.get(p, 0) + TENS.get(p, 0)
        last = tw[j] if pct else run[-1]
        first = run[0]
        # "a thousand followers": the "a" is the one — it folds into the number (9287 read "a 1000 followers")
        if numword(run[0]).split()[0] in SCALE and out_w and out_w[-1]["w"].lower() == "a" and not out_w[-1].get("end_punct"):
            first = {**run[0], "s": out_w.pop()["s"]}
        out_w.append({**first, "w": f"{total + cur_n}{'%' if pct else ''}", "e": last["e"], "end_punct": last.get("end_punct", "")})
        i = j + 1 if pct else j
    else:
        out_w.append(tw[i])
        i += 1
tw = out_w

# 3. greedy single-line grouping; never cross a sentence end; never end on glue
groups, cur = [], []


def emit():
    if cur:
        groups.append({"words": [dict(x) for x in cur], "s": cur[0]["s"], "e": cur[-1]["e"]})


for wd in tw:
    trial = cur + [wd]
    if cur and not fits([x["w"] for x in trial]):
        held = []
        while len(cur) > 1 and cur[-1]["w"].lower().strip(".,!?’'") in GLUE:
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
    ends = lambda grp: (grp["words"][-1].get("end_punct") or " ")[0] in ".!?"
    # never glue across a sentence end: a sentence's last word joins its own sentence
    if ends(g) and prv and not ends(prv) and fits([x["w"] for x in prv["words"] + g["words"]]):
        prv["words"] += g["words"]
        prv["e"] = g["e"]
        groups.pop(i)
        continue
    if nxt and not ends(g) and fits([x["w"] for x in g["words"] + nxt["words"]]):
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
# hard cuts only: a caption never outlives the start of the next one (two lines on screen read as a glitch)
for i, g in enumerate(groups[:-1]):
    nxt = groups[i + 1]
    if g["e"] > nxt["s"]:
        g["e"] = nxt["s"]
    if g["s"] >= g["e"]:   # timings collided — keep the word, give it a frame
        g["e"] = g["s"] + 1 / job.numbers["canvas"]["fps"]
        nxt["s"] = max(nxt["s"], g["e"])
# two text layers never share a frame: under a hook title (broll-plan "titles", or a titled b-roll window) the title
# carries the beat — a caption that starts under it is dropped, one that runs into it ends where it begins
dropped_for_titles = []
if job.p("broll-plan.json").exists():
    bp = job.read_json("broll-plan.json")
    spans = [(t["start"], t["end"]) for t in bp.get("titles", [])] +             [(c["start"], c["end"]) for c in bp.get("clips", []) if c.get("title")]
    keep_g = []
    for g in groups:
        if any(a - 1e-3 <= g["s"] < b for a, b in spans):
            dropped_for_titles.append(" ".join(w["w"] for w in g["words"]))
            continue
        for a, b in spans:
            if g["s"] < a < g["e"]:
                g["e"] = a
        keep_g.append(g)
    groups = keep_g
    if dropped_for_titles:
        print(f"plan-captions: {len(dropped_for_titles)} groups under hook titles dropped: {' | '.join(dropped_for_titles)}")

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

# 7. the agent's accent picks survive a re-run: captions.overrides.json {"accents": {"Muse": "hot", "insane": "hot", …}}
#    replaces the lexicon's picks — a group gets the first listed word it contains, never two accented groups in a row.
#    (Re-running from the rough cut re-planned captions.json and silently dropped hand-set accents — 9278.)
ov = job.read_json("captions.overrides.json") if job.p("captions.overrides.json").exists() else {}
if ov.get("accents"):
    want = {w.lower(): c for w, c in ov["accents"].items()}
    last_accented = -2
    for i, g in enumerate(groups):
        g["accent"] = None
        hit = next((x for x in g["words"] if x["w"].lower().strip(".,!?’'") in want), None)
        if hit and i - last_accented >= 2:
            g["accent"] = {"word": hit["w"], "cls": want[hit["w"].lower().strip(".,!?’'")]}
            last_accented = i

for g in groups:
    g["words"] = [{"w": x["w"], "s": x["s"], "e": x["e"], "end_punct": x.get("end_punct", "")} for x in g["words"]]

out = {"duration": round(tl.duration, 3), "groups": groups, "mute_windows": []}
job.write_json(out, "captions.json")
n_acc = sum(1 for g in groups if g["accent"])
avg = sum(len(g["words"]) for g in groups) / max(1, len(groups))
job.note("captions", f"planned {len(groups)} groups, {avg:.1f} words avg, {n_acc} accented")
print(f"plan-captions: {'spine' if USE_SPINE else 'raw→EDL'} words · {len(groups)} groups · {avg:.1f} words avg · {n_acc} accented · {tl.duration:.1f}s → captions.json")
