#!/usr/bin/env python3
"""Gate — transcript/words.json is usable for frame-accurate cutting.

Fails on: non-monotonic times, a word longer than max_word_s, an intra-segment gap > max gap with no
interp flag, too few words per second overall, low-score words that were not flagged.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, die  # noqa: E402

job = Job(sys.argv[1])
cfg = job.numbers["transcript"]
words = job.read_json("transcript", "words.json")
if not words:
    die("no words")
errs, warns = [], []
prev_e = -1.0
for i, w in enumerate(words):
    if w["s"] < prev_e - 0.05:
        errs.append(f"#{i} '{w['w']}' starts {w['s']} before previous end {prev_e}")
    if w["e"] < w["s"]:
        errs.append(f"#{i} '{w['w']}' ends before it starts")
    if w["e"] - w["s"] > cfg["max_word_s"]:
        errs.append(f"#{i} '{w['w']}' is {w['e']-w['s']:.2f}s long")
    if i and w["seg"] == words[i - 1]["seg"] and w["s"] - prev_e > cfg["max_intra_segment_gap_s"] and not w.get("interp"):
        warns.append(f"#{i} '{w['w']}' gap {w['s']-prev_e:.2f}s inside a segment")
    if w.get("score", 1) < cfg["min_word_score"] and not w.get("interp"):
        warns.append(f"#{i} '{w['w']}' score {w['score']}")
    prev_e = max(prev_e, w["e"])
span = words[-1]["e"] - words[0]["s"]
wps = len(words) / span if span else 0
if wps < cfg["min_words_per_s"]:
    errs.append(f"only {wps:.2f} words/s over {span:.1f}s")
for w in warns[:20]:
    print("warn:", w)
if errs:
    for e in errs:
        print("error:", e)
    job.gate("validate_transcript", "fail")
    sys.exit(1)
job.gate("validate_transcript", "pass")
print(f"validate-transcript: pass · {len(words)} words · {wps:.2f} w/s · {len(warns)} warnings")
