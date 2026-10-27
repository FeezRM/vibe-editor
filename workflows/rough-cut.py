#!/usr/bin/env python3
"""Node 02b — rough cut as data. transcript/words.json → cuts.json (the EDL).

Writes review/takes.md: every line of the raw with each word marked kept or [cut]. The rules are mechanical; which
take is the right one is the editor's call, made from that file (ig-cut).

Removes: dead air between words ≥ cut.min_gap_s (leaving cut.lead_s before the next onset — the
"cut on the breath" rule as a number), filler tokens, immediate repeats (false starts), and retakes
(a segment whose opening cut.retake_min_words words open a later segment within cut.retake_window_s —
the last take stays). Never removes voice tics listed in cut.keep_tics. Never produces a kept clip
shorter than cut.min_clip_s.

--review prints every removal with an id; vetoes go in cuts.overrides.json as {"keep": [{"in", "out", "why"}]} (by
range — stable) or {"keep_ids": [..]} (ids shift when the transcript changes),
review removals (judgment the rules cannot make) as {"remove": [{"in", "out", "why"}]}, a keep with "exact": true pins
its edges as written (a cut between run-together words, placed on the quietest frame by hand),
deliberate frozen beats as {"holds": [{"at", "s", "why"}]} (the keep ending nearest `at` freezes its last
frame `s` seconds — b-roll with its own audio plays over it), {"mark": false} when the speaker moves on purpose (a
standing take is not a slate), and are re-applied deterministically on the next run.

Usage: python workflows/rough-cut.py <job> [--review]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--review", action="store_true")
a = ap.parse_args()

job = Job(a.job)
job.require("rough_cut")
cfg = job.numbers["cut"]
fps = job.fps
duration = float(job.state["source_duration_s"])
words = job.read_json("transcript", "words.json")
overrides = job.read_json("cuts.overrides.json") if job.p("cuts.overrides.json").exists() else {}
vetoed = set(overrides.get("keep_ids", []))

fillers = set(cfg["fillers"])
keep_tics = set(cfg["keep_tics"])


def norm(w):
    return w["w"].lower().strip("'’\"")


removals = []  # {"id", "in", "out", "reason"}


def add(rin, rout, reason):
    rin, rout = max(0.0, rin), min(duration, rout)
    if rout - rin >= 1.0 / fps:
        removals.append({"id": f"r{len(removals)+1:03d}", "in": round(rin, 3), "out": round(rout, 3), "reason": reason})


# 1. head and tail
if words[0]["s"] - cfg["lead_s"] > 0.15:
    add(0.0, words[0]["s"] - cfg["lead_s"], "silence:head")
tail_end = words[-1]["e"] + max(cfg["tail_s"], 0.35)
if duration - tail_end > 0.25:
    add(tail_end, duration, "silence:tail")

# 2. gaps between words
for i in range(1, len(words)):
    p, w = words[i - 1], words[i]
    gap = w["s"] - p["e"]
    if gap >= cfg["min_gap_s"]:
        add(p["e"] + cfg["tail_s"], w["s"] - cfg["lead_s"], "silence")

# 3. fillers (whole tokens), never tics
for i, w in enumerate(words):
    n = norm(w)
    if n in fillers and n not in keep_tics:
        add(w["s"] - 0.02, w["e"] + 0.02, f"filler:{n}")

# 4. false starts: immediate repeat of a word or bigram
if cfg.get("remove_false_starts", True):
    i = 0
    while i < len(words) - 1:
        a1, b1 = norm(words[i]), norm(words[i + 1])
        if a1 == b1 and a1 not in keep_tics and len(a1) > 1 and words[i + 1]["s"] - words[i]["e"] < 0.6:
            add(words[i]["s"] - 0.02, words[i + 1]["s"] - cfg["lead_s"], f"repeat:{a1}")
            i += 2
            continue
        if i < len(words) - 3:
            bg1 = (norm(words[i]), norm(words[i + 1]))
            bg2 = (norm(words[i + 2]), norm(words[i + 3]))
            if bg1 == bg2 and words[i + 2]["s"] - words[i + 1]["e"] < 0.6:
                add(words[i]["s"] - 0.02, words[i + 2]["s"] - cfg["lead_s"], f"repeat:{' '.join(bg1)}")
                i += 4
                continue
        # a pickup: the same 3+ word phrase said twice back to back ("…on the hook and 30% on the value
        # on the hook and 30% on the value"). When the first reading ends the sentence (a pause after it), the
        # sentence is already whole: drop the re-said fragment. Splicing onto the pickup cut 9078 mid-sentence.
        # Only a first reading that runs straight on (no pause) is the abandoned one.
        hit = 0
        for n in range(cfg.get("restart_max_words", 8), 2, -1):
            if i + 2 * n <= len(words) and [norm(x) for x in words[i:i + n]] == [norm(x) for x in words[i + n:i + 2 * n]] \
                    and words[i + n]["s"] - words[i + n - 1]["e"] < 0.6:
                hit = n
                break
        if hit:
            phrase = " ".join(norm(x) for x in words[i:i + hit])
            first_whole = words[i + hit - 1]["end_punct"] in (".", "!", "?") or words[i + hit]["s"] - words[i + hit - 1]["e"] >= 0.2
            if first_whole:
                end = words[i + 2 * hit]["s"] - cfg["lead_s"] if i + 2 * hit < len(words) else words[i + 2 * hit - 1]["e"] + 0.35
                add(words[i + hit - 1]["e"] + cfg["tail_s"], end, f"pickup:{phrase}")
            else:
                add(words[i]["s"] - 0.02, words[i + hit]["s"] - cfg["lead_s"], f"restart:{phrase}")
            i += 2 * hit
            continue
        i += 1

# 5. retakes: a segment whose first retake_min_words words are spoken again at the start of a later segment
#    within retake_window_s is an abandoned take — the creator re-recorded until satisfied, so the LAST take stays.
if cfg.get("remove_retakes", True):
    n_pref = cfg.get("retake_min_words", 3)
    window = cfg.get("retake_window_s", 45.0)
    split_gap = cfg.get("retake_split_gap_s", 1.0)
    segs = []   # takes: a WhisperX segment, split where the speaker paused (9078: three "For the idea…" false starts in one)
    for w in words:
        if segs and segs[-1][-1]["seg"] == w["seg"] and w["s"] - segs[-1][-1]["e"] < split_gap:
            segs[-1].append(w)
        else:
            segs.append([w])
    # A retake range runs from the abandoned take to its redo and can cross a whole other line. That line stays when
    # it is the SURVIVOR of its own takes: said before (same opening, or the same words re-worded) and never again.
    # 9078: "For the hook" … 24 s … "For the hook" crossed the last take of the idea line — kept now. 9077: the crossed
    # "This video was scripted…" was said again later as "This video is scripted…" — not a survivor, still dropped.
    from difflib import SequenceMatcher
    head_n = cfg.get("retake_similar_words", 8)
    # a take's words run on past a pause ("This video … is scripted"): compare the words that FOLLOW its start
    starts = {id(sg[0]): words.index(sg[0]) for sg in segs}
    toks = [[norm(x) for x in words[starts[id(sg[0])]: starts[id(sg[0])] + head_n]] for sg in segs]

    def same_line(i, j):
        a_, b_ = toks[i], toks[j]
        if len(a_) >= n_pref and len(b_) >= n_pref and a_[:n_pref] == b_[:n_pref]:
            return True
        return min(len(a_), len(b_)) >= 5 and SequenceMatcher(None, a_, b_).ratio() >= cfg.get("retake_similarity", 0.75)

    def near(i, j):
        return abs(segs[j][0]["s"] - segs[i][0]["s"]) <= window

    # only a real line is protected — a short aside said three times ("What do you think", 9077) is not
    survivor = {j for j in range(len(segs)) if len(segs[j]) >= cfg.get("retake_protect_words", 6)
                and any(same_line(i, j) for i in range(j) if near(i, j))
                and not any(same_line(j, k) for k in range(j + 1, len(segs)) if near(j, k))}
    for i, sg in enumerate(segs):
        if len(sg) < n_pref:
            continue
        pref = tuple(norm(x) for x in sg[:n_pref])
        for j in range(i + 1, len(segs)):
            later = segs[j]
            if later[0]["s"] - sg[0]["s"] > window:
                break
            if same_line(i, j):
                stop = next((k for k in range(i + 1, j) if k in survivor), j)
                add(sg[0]["s"] - 0.02, segs[stop][0]["s"] - cfg["lead_s"], f"retake:{' '.join(pref)}")
                break
    # a fragment: one or two words alone between pauses ("Your content" … "No") — an attempt that was abandoned
    frag_n, frag_gap = cfg.get("fragment_max_words", 2), cfg.get("fragment_gap_s", 1.0)
    for i, sg in enumerate(segs):
        gap_before = sg[0]["s"] - segs[i - 1][-1]["e"] if i else 99
        gap_after = segs[i + 1][0]["s"] - sg[-1]["e"] if i + 1 < len(segs) else 99
        if len(sg) <= frag_n and gap_before >= frag_gap and gap_after >= frag_gap:
            add(sg[0]["s"] - 0.02, sg[-1]["e"] + 0.05, f"fragment:{' '.join(norm(x) for x in sg)}")

# 6. review removals: a judgment the rules cannot make (an earlier take in different words, the speaker
#    talking to the crew) — {"remove": [{"in", "out", "why"}]} in cuts.overrides.json, ids o001…
for k, r in enumerate(overrides.get("remove", []), 1):
    n0 = len(removals)
    add(float(r["in"]), float(r["out"]), f"review:{r.get('why', '')}")
    if len(removals) > n0:
        removals[-1]["id"] = f"o{k:03d}"

# apply vetoes, sort, merge overlaps
removals = [r for r in removals if r["id"] not in vetoed]
# {"keep": [{"in", "out", "why"}]}: a take kept by range. Removal ids are positional — a transcript fix renumbers every
# later one, and a keep_ids veto then hits the wrong removal (9287). A kept range clips every removal around it.
for f in overrides.get("keep", []):
    clipped = []
    for r in removals:
        for lo, hi in ((r["in"], min(r["out"], f["in"])), (max(r["in"], f["out"]), r["out"])):
            if hi - lo >= 1.0 / fps:
                clipped.append(dict(r, **{"in": round(lo, 3), "out": round(hi, 3)}))
    removals = clipped
removals.sort(key=lambda r: r["in"])
merged = []
for r in removals:
    if merged and r["in"] <= merged[-1]["out"] + 1e-6:
        merged[-1]["out"] = max(merged[-1]["out"], r["out"])
        merged[-1]["parts"].append(f'{r["id"]} {r["in"]:.2f}-{r["out"]:.2f} {r["reason"]}')
        if r["reason"] not in merged[-1]["reason"]:
            merged[-1]["reason"] += "+" + r["reason"]
    else:
        merged.append(dict(r, parts=[f'{r["id"]} {r["in"]:.2f}-{r["out"]:.2f} {r["reason"]}']))

# complement → keep; kill slivers by merging tiny keeps back into the neighbouring removal (i.e. drop the removal)
keep = []
cursor = 0.0
for r in merged:
    if r["in"] > cursor:
        keep.append({"in": round(cursor, 3), "out": round(r["in"], 3)})
    cursor = r["out"]
if cursor < duration:
    keep.append({"in": round(cursor, 3), "out": round(duration, 3)})

changed = True
while changed:
    changed = False
    for i, k in enumerate(keep):
        if k["out"] - k["in"] < cfg["min_clip_s"] and len(keep) > 1:
            has_word = any(w["s"] < k["out"] and w["e"] > k["in"] for w in words)
            cost_prev = k["in"] - keep[i - 1]["out"] if i > 0 else None
            cost_next = keep[i + 1]["in"] - k["out"] if i + 1 < len(keep) else None
            if not has_word:
                pass                                   # a word-less sliver between two removals: just drop it
            elif cost_next is not None and (cost_prev is None or cost_next <= cost_prev):
                keep[i + 1]["in"] = k["in"]            # merge with the neighbour that re-includes the least removed audio
            else:
                keep[i - 1]["out"] = k["out"]
            keep.pop(i)
            changed = True
            break


def drop_slivers(keep):
    """A piece without a word goes. A piece WITH a word is content: splitting at a pause must never delete it (9287:
    "This … is my other account" — the 0.3 s "This" was dropped as a sliver and the next clip started mid-word). One
    shorter than min_clip_s is padded into its own trailing pause up to min_sliver_frames, never into the next piece."""
    out, floor = [], cfg["min_sliver_frames"] / fps
    for n, k in enumerate(keep):
        if not any(w["s"] < k["out"] and w["e"] > k["in"] for w in words):
            continue
        if k["out"] - k["in"] < cfg["min_clip_s"]:
            nxt = keep[n + 1]["in"] if n + 1 < len(keep) else duration
            k = dict(k, out=round(min(max(k["out"], k["in"] + floor + 0.002), nxt), 3))   # + 2 ms: 8.0 frames, not 7.99
        out.append(k)
    return out


# 7. edges on the AUDIO. Everything above decided which words stay; where a clip starts and stops is measured on
#    the voice itself: WhisperX word edges drift 50–150 ms — a cut placed lead_s before a late word start clipped
#    onsets, a tail placed after an early word end chopped "value" (9078), and gaps the words hid stayed in as dead air.
wav = job.p("transcript", "audio.wav")
hot_edges = []
if wav.exists():
    from _audio import HOP, Envelope
    env = Envelope(wav, words, cfg["edge_rel_db"])
    win = cfg["edge_search_s"]
    # 7a. silences the transcript hid (a word stretched across a pause) are dead air like any other
    split = []
    for k in keep:
        cur = k["in"]
        for qa, qb in env.quiet_runs(k["in"] + 0.05, k["out"] - 0.05, cfg["min_gap_s"]):
            split.append({"in": cur, "out": qa + cfg["tail_s"]})
            cur = qb - cfg["lead_s"]
        split.append({"in": cur, "out": k["out"]})
    keep = drop_slivers(split)
    # 7b. snap each edge to the voice: in = onset − lead_s, out = offset + tail_s, never reaching into a removed word
    for n, k in enumerate(keep):
        inside = [w for w in words if w["s"] < k["out"] and w["e"] > k["in"]]
        w0, wl = inside[0], inside[-1]
        before = [w for w in words if w["e"] <= w0["s"] and w["s"] < k["in"]]
        after = [w for w in words if w["s"] >= wl["e"] and w["e"] > k["out"]]
        lo = max(w0["s"] - win, before[-1]["e"] + 0.02 if before else 0.0, keep[n - 1]["out"] if n else 0.0)
        on = env.onset(lo, w0["s"] + win / 2)
        k["in"] = max(lo, on - cfg["lead_s"]) if on is not None else env.quietest(max(lo, w0["s"] - 0.15), w0["s"] + 0.05)
        hi = min(wl["e"] + win, after[0]["s"] - 0.02 if after else duration)
        off = env.offset(max(wl["s"], wl["e"] - 0.15), hi)
        k["out"] = min(hi, off + cfg["tail_s"]) if off is not None else env.quietest(max(wl["e"] - 0.05, wl["s"]), hi)
        k["in"], k["out"] = round(k["in"], 3), round(k["out"], 3)
    keep = drop_slivers(keep)
    # 7c. every breath between words goes, not only the ≥ min_gap_s ones: a pause the voice drops pause_rel_db under
    #     its own level for longer than pause_max_s is cut down to tail_s + lead_s (a jump cut on the breath). 9278 kept
    #     pauses of 0.1–0.25 s inside clips and at joins — "still too much pause … when i said muse" — where his posted
    #     reels never drop that far between words. A short quiet run inside a word is a stop closure, so it is cut only
    #     at a word boundary; one longer than closure_max_s is dead air wherever it falls. A breath or click quieter
    #     than any word (breath_rel_db under speech) after the last word or before the first goes with its pause.
    #     The cut points sit where the voice is fully gone (the edge threshold), never leaving a piece < pause_min_piece_s.
    pq = env.db < env.speech_db - cfg.get("pause_rel_db", 30)
    pmax, pmin = cfg.get("pause_max_s", 0.08), cfg.get("pause_min_piece_s", 0.3)
    weak = env.speech_db - cfg.get("breath_rel_db", 14)
    tight = []
    for k in keep:
        inside = [w for w in words if w["s"] < k["out"] and w["e"] > k["in"]]
        # scanned edge to edge: a click after the last word made 7b read the silence before it as a closure inside the
        # word, and a clip ended 0.1 s late (9287 "…you retard" → "See you")
        cur, j, hi_i = k["in"], env.i(k["in"]), env.i(k["out"])
        while j < hi_i:
            if not pq[j]:
                j += 1
                continue
            e = j
            while e < hi_i and pq[e]:
                e += 1
            gone = np.flatnonzero(~env.loud[j:e])
            qa, qb = (env.t(j + gone[0]), env.t(j + gone[-1] + 1)) if len(gone) else (env.t(j), env.t(e))
            cut_in, cut_out = qa + cfg["tail_s"], qb - cfg["lead_s"]
            if e >= hi_i:                                       # silence runs to the clip's end: trim it to tail_s
                if inside and qa >= inside[-1]["e"] - 0.03 and k["out"] - cut_in > 0.01:
                    k = dict(k, out=round(max(cut_in, cur + pmin), 3))
                break
            if j <= env.i(k["in"]) + 1:                         # silence from the clip's start: trim it to lead_s
                if inside and qb <= inside[0]["s"] + 0.03 and cut_out - cur > 0.01:
                    cur = round(cut_out, 3)
                j = e
                continue
            if (e - j) * HOP <= pmax:
                j = e
                continue
            # the quiet run must lie AFTER the last word (BEFORE the first): testing its far end let a softly spoken last
            # word ("…viral videos for you", 9278-v2) read as a breath and be cut with its pause
            if inside and qa >= inside[-1]["e"] - 0.03 and float(env.db[e: env.i(k["out"]) + 1].max()) < weak:
                k = dict(k, out=round(min(k["out"], cut_in), 3))
                break
            if inside and qb <= inside[0]["s"] + 0.03 and float(env.db[env.i(cur): j + 1].max()) < weak:
                cur = round(max(cur, cut_out), 3)
                j = e
                continue
            boundary = any(p["e"] <= qb + 0.08 and w["s"] >= qa - 0.08 for p, w in zip(inside, inside[1:]))
            if (boundary or (e - j) * HOP > cfg.get("closure_max_s", 0.15)) and cut_out > cut_in \
                    and cut_in - cur >= pmin and k["out"] - cut_out >= pmin:
                tight.append(dict(k, **{"in": cur, "out": round(cut_in, 3)}))
                tight[-1].pop("hold", None)
                cur = round(cut_out, 3)
            j = e
        tight.append(dict(k, **{"in": cur}))
    keep = tight
    # an editor's {"keep": [...]} range is protected from every rule, the audio edges included: a word inside it that
    # the edge steps trimmed (a swallowed last word the envelope reads as silence — 9278-v2 "…videos for you") is put
    # back, up to the range and never into the neighbouring clip
    for f in overrides.get("keep", []):
        lo, hi = float(f["in"]), float(f["out"])
        for n, k in enumerate(keep):
            if k["out"] <= lo or k["in"] >= hi:
                continue
            ws = [w for w in words if w["s"] >= lo - 0.02 and w["e"] <= hi + 0.02]
            nxt = keep[n + 1]["in"] if n + 1 < len(keep) else duration
            prv = keep[n - 1]["out"] if n else 0.0
            tail = [w for w in ws if w["s"] >= k["out"] - 0.05 and w["s"] < nxt]
            if tail and k["out"] < hi:
                k["out"] = round(min(hi, nxt, max(k["out"], tail[-1]["e"] + cfg["tail_s"])), 3)
            head = [w for w in ws if w["e"] <= k["in"] + 0.05 and w["e"] > prv]
            if head and k["in"] > lo:
                k["in"] = round(max(lo, prv, min(k["in"], head[0]["s"] - cfg["lead_s"])), 3)
            # "exact": true — the editor's edge stands as written: a cut between words that run together (no silence to
            # snap to) is placed by hand on the quietest frame, and validate-edl skips its inside-speech check
            if f.get("exact"):
                if abs(k["out"] - hi) <= 0.12 and (n + 1 == len(keep) or hi < keep[n + 1]["in"]):
                    k["out"] = round(hi, 3)
                    k.setdefault("exact", []).append("out")
                if abs(k["in"] - lo) <= 0.12 and (n == 0 or lo > keep[n - 1]["out"]):
                    k["in"] = round(lo, 3)
                    k.setdefault("exact", []).append("in")
    # every clip a whole number of frames (the lane cuts by frame count), so the EDL's timeline IS the spine's: an
    # unquantised 34-clip cut drifted 0.17 s and every offset-based check read the wrong frames (9287)
    for n, k in enumerate(keep):
        nxt = keep[n + 1]["in"] if n + 1 < len(keep) else duration
        nf = max(1, round((k["out"] - k["in"]) * fps))
        while nf > 1 and k["in"] + nf / fps > nxt + 1e-6:
            nf -= 1
        k["out"] = round(k["in"] + nf / fps, 4)
    hot_edges = [round(k[s_], 3) for k in keep for s_ in ("in", "out") if s_ not in k.get("exact", []) and env.hot(k[s_])]

# 8. the speaker on the mark: leading / trailing clips where the face is missing or far from where it sits for the
#    rest of the video are a slate — walking to the chair, sitting down ("Idea, hook, value" on 9078) — not content.
mark = cfg.get("mark", {})
off_mark = []
if overrides.get("mark", mark.get("enabled", True)) and len(keep) > 2:   # {"mark": false}: a standing, moving take (9287) is not a slate
    from _faces import FaceFinder
    W, H = job.numbers["canvas"]["width"] // 3, job.numbers["canvas"]["height"] // 3
    ff = FaceFinder(W, H)
    src = job.source

    def samples(k):
        out = []
        for p in mark["at"]:
            f = ff.at(src, k["in"] + (k["out"] - k["in"]) * p)
            out.append(None if f is None else ((f[0] + f[2] / 2) / W, (f[1] + f[3] / 2) / H, f[2] / W))
        return out

    seen = {n: samples(k) for n, k in enumerate(keep)}
    faces = [f for fs in seen.values() for f in fs if f]
    if len(faces) >= 3:
        med = [float(sorted(v)[len(v) // 2]) for v in zip(*faces)]

        def on_mark(n):
            ok = sum(1 for f in seen[n] if f and abs(f[0] - med[0]) <= mark["dx"] and abs(f[1] - med[1]) <= mark["dy"]
                     and abs(f[2] / med[2] - 1) <= mark["dw"])
            return ok >= mark["min_on"]
        lead_n = 0
        while lead_n < len(keep) - 1 and not on_mark(lead_n):
            lead_n += 1
        tail_n = len(keep)
        while tail_n > lead_n + 1 and not on_mark(tail_n - 1):
            tail_n -= 1
        off_mark = keep[:lead_n] + keep[tail_n:]
        keep = keep[lead_n:tail_n]

# 9. where the face is in every clip (centre x, centre y, width — fractions of the frame): the lane places its one fixed
#    camera on the median of these (framing.scale) and anchors hand-placed zoom punches on them. `face` is the median of
#    three samples; a clip where no face is found falls back to the median of all clips.
from _faces import FaceFinder
_fw, _fh = job.numbers["canvas"]["width"] // 3, job.numbers["canvas"]["height"] // 3
_ff = FaceFinder(_fw, _fh)


def _face(t):
    f = _ff.at(job.source, t)
    return None if f is None else [round((f[0] + f[2] / 2) / _fw, 4), round((f[1] + f[3] / 2) / _fh, 4), round(f[2] / _fw, 4)]


for k in keep:
    fs = [f for f in (_face(k["in"] + (k["out"] - k["in"]) * p) for p in (0.25, 0.5, 0.75)) if f]
    k["face"] = [round(float(np.median([f[i] for f in fs])), 4) for i in range(3)] if fs else None
_found = [k["face"] for k in keep if k["face"]]
for k in keep:
    if not k["face"] and _found:
        k["face"] = [round(float(np.median([f[i] for f in _found])), 4) for i in range(3)]

# recompute removed from the final keep list so stats are exact
removed = []
cursor = 0.0
for k in keep:
    if k["in"] > cursor + 1e-6:
        reason = "+".join(sorted({m["reason"] for m in merged if m["in"] < k["in"] and m["out"] > cursor})) or "silence"
        if any(o["in"] >= cursor - 1e-6 and o["out"] <= k["in"] + 1e-6 for o in off_mark):
            reason = "off-mark+" + reason
        removed.append({"in": round(cursor, 3), "out": k["in"], "reason": reason})
    cursor = k["out"]
if cursor < duration - 1e-6:
    removed.append({"in": round(cursor, 3), "out": round(duration, 3), "reason": "silence:tail"})

# punches survive a re-cut by SOURCE time (the word they land on), not by the clip's in point — a tighter cut moves
# both. The previous EDL is kept as cuts.prev.json so remap-plan.py can move the graphics plan the same way.
old_zooms = []
if job.p("cuts.json").exists():
    prev = job.read_json("cuts.json")
    job.write_json(prev, "cuts.prev.json")
    from _lib import Timeline
    ptl = Timeline(prev)
    for k, off in zip(prev.get("keep", []), ptl.offsets):
        if k.get("zoom"):
            old_zooms.append((k["in"] + (k["zoom"]["at"] - off), k["zoom"]))
for k in keep:
    k["reason"] = "speech"
    k["lead_s"] = cfg["lead_s"]
for src_t, z in old_zooms:
    k = next((k for k in keep if k["in"] <= src_t < k["out"]), None)
    if k is not None and "zoom" not in k:
        k["zoom"] = dict(z, src=round(src_t, 3))
holds = []
for h in overrides.get("holds", []):
    k = min(keep, key=lambda k: abs(k["out"] - float(h["at"])), default=None)
    if k is None or abs(k["out"] - float(h["at"])) > cfg["hold_snap_s"]:
        sys.exit(f"rough-cut: hold at {h['at']}s matches no keep end within {cfg['hold_snap_s']}s")
    k["hold"] = round(float(h["s"]), 3)
    holds.append({"at": k["out"], "s": k["hold"], "why": h.get("why", "")})
_t = 0.0
for k in keep:
    if k.get("zoom"):
        k["zoom"]["at"] = round(_t + k["zoom"].pop("src") - k["in"], 3)
    _t += k["out"] - k["in"] + k.get("hold", 0.0)
kept_s = sum(k["out"] - k["in"] for k in keep)
cuts = {
    "source": job.state["source"], "fps": fps, "source_duration_s": duration,
    "keep": keep, "removed": removed, "removal_ids": merged,
    "stats": {"kept_s": round(kept_s, 3), "removed_s": round(duration - kept_s, 3), "clips": len(keep),
              "mean_clip_s": round(kept_s / len(keep), 3) if keep else 0,
              "hold_s": round(sum(h["s"] for h in holds), 3), "timeline_s": round(kept_s + sum(h["s"] for h in holds), 3)},
    "holds": holds,
    "off_mark": [{"in": o["in"], "out": o["out"]} for o in off_mark],
    "hot_edges": hot_edges,
}
job.write_json(cuts, "cuts.json")
job.mark("rough_cut", "done", out="cuts.json", kept_s=round(kept_s, 2), cut_s=round(duration - kept_s, 2), clips=len(keep))
job.note("rough_cut", f"{len(keep)} clips, kept {kept_s:.1f}s of {duration:.1f}s, removed {len(merged)} ranges ({len(vetoed)} vetoed)")
print(f"rough-cut: {len(keep)} clips · kept {kept_s:.1f}s · removed {duration-kept_s:.1f}s · mean clip {cuts['stats']['mean_clip_s']}s"
      f" · {len(off_mark)} off-mark · {len(hot_edges)} edges inside speech")
for o in off_mark:
    print(f"  off-mark  {o['in']:7.2f}–{o['out']:7.2f}  {' '.join(w['w'] for w in words if w['s'] < o['out'] and w['e'] > o['in'])}")


# review/takes.md — the whole raw read as lines, every word marked kept or [cut]. The rules above only catch what looks
# alike on paper (repeats, restarts, fillers); a fumbled line said once, a sentence abandoned for a better one in other
# words, a wrong fact corrected later, an aside to the camera person all pass them. The editor reads this file and
# decides the takes in cuts.overrides.json.
def _kept(w):
    """kept when most of the word is heard — a stop closure shortened inside a word ("out|reach") does not cut it"""
    heard = sum(max(0.0, min(k["out"], w["e"]) - max(k["in"], w["s"])) for k in keep)
    return heard >= 0.5 * max(w["e"] - w["s"], 1e-3)


lines, cur = [], [words[0]]
for p_, w in zip(words, words[1:]):
    if w["s"] - p_["e"] >= 0.6 or p_["w"].rstrip().endswith((".", "?", "!")):
        lines.append(cur)
        cur = []
    cur.append(w)
lines.append(cur)
out = ["# takes — every line of the raw, in order", "",
       "Words in [brackets] are cut. Read it as the viewer will hear it: is every kept line the best, complete take? Is",
       "anything kept that the speaker fumbled, abandoned, corrected or said again better later? Decide in",
       "cuts.overrides.json ({\"remove\"|\"keep\": [{\"in\", \"out\", \"why\"}]}) and re-run rough_cut.", ""]
for n, ln in enumerate(lines, 1):
    marks = [_kept(w) for w in ln]
    tag = "KEEP" if all(marks) else "CUT " if not any(marks) else "PART"
    text, run = [], []
    for w, k_ in zip(ln, marks):
        if k_:
            if run:
                text.append("[" + " ".join(run) + "]")
                run = []
            text.append(w["w"])
        else:
            run.append(w["w"])
    if run:
        text.append("[" + " ".join(run) + "]")
    out.append(f"L{n:03d}  {ln[0]['s']:7.2f}–{ln[-1]['e']:7.2f}  {tag}  {' '.join(text)}")
job.p("review").mkdir(exist_ok=True)
job.p("review", "takes.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"rough-cut: review/takes.md — {len(lines)} lines, {sum(1 for l in out if '  KEEP  ' in l or '  PART  ' in l)} kept in whole or part")

if a.review:
    print("\nREMOVALS (veto with cuts.overrides.json {\"keep_ids\": [...]})")
    for r in merged:
        ws = [w["w"] for w in words if w["s"] >= r["in"] - 0.05 and w["e"] <= r["out"] + 0.05]
        print(f"  {r['id']}  {r['in']:7.2f}–{r['out']:7.2f}  {r['out']-r['in']:5.2f}s  {r['reason']:<18} {' '.join(ws)}")
        if len(r["parts"]) > 1:
            for part in r["parts"]:
                print(f"           └ {part}")
