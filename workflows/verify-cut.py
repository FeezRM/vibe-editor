#!/usr/bin/env python3
"""Gate — the cut says what it was meant to say. The words the EDL keeps (raw transcript, inside every keep, in
order) against what the spine actually says (transcript/spine-words.json, its own audio). A run of
cut.coverage_max_run or more words missing = a clipped line; the same run extra = a doubled take or a leftover.

Usage: python workflows/verify-cut.py <job>
"""
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import json

from _lib import Job, preset_file  # noqa: E402

job = Job(sys.argv[1])
cfg = job.numbers["cut"]
cuts = job.read_json("cuts.json")
raw = job.read_json("transcript", "words.json")
spine = job.read_json("transcript", "spine-words.json")


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("-", " ").replace(" ", ""))


want = [w for w in raw if any(k["in"] - 0.03 <= w["s"] and w["e"] <= k["out"] + 0.03 for k in cuts["keep"])]
a, b = [norm(w["w"]) for w in want], [norm(w["w"]) for w in spine]
# the spine transcript gets transcript-corrections.json (a phrase merges into one token); a raw transcript made before a
# correction was added does not — fold the same phrases on the raw side or a correction reads as missing words
corr_path = preset_file(job.state.get("preset", "vertical/default"), "transcript-corrections.json")
for phrase, repl in sorted((json.loads(corr_path.read_text(encoding="utf-8")) if corr_path.exists() else {}).items(),
                           key=lambda kv: -len(kv[0].split())):
    toks, n = [norm(t) for t in phrase.split()], len(phrase.split())
    i = 0
    while i <= len(a) - n:
        if a[i:i + n] == toks and n > 1:
            a[i:i + n], want[i:i + n] = [norm(repl)], [dict(want[i], w=repl, e=want[i + n - 1]["e"])]
        i += 1
run = cfg.get("coverage_max_run", 2)
problems = []
for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if op in ("delete", "replace") and i2 - i1 >= run and (op == "delete" or (i2 - i1) - (j2 - j1) >= run or j2 - j1 == 0
                                                          or SequenceMatcher(None, a[i1:i2], b[j1:j2]).ratio() < 0.5):
        problems.append(f"missing  @ {want[i1]['s']:.2f}s (source): '{' '.join(w['w'] for w in want[i1:i2])}'")
    if op in ("insert", "replace") and j2 - j1 >= run and (op == "insert" or (j2 - j1) - (i2 - i1) >= run
                                                          or SequenceMatcher(None, a[i1:i2], b[j1:j2]).ratio() < 0.5):
        problems.append(f"extra    @ {spine[j1]['s']:.2f}s (timeline): '{' '.join(w['w'] for w in spine[j1:j2])}'")
ratio = SequenceMatcher(None, a, b, autojunk=False).ratio()
for p in problems:
    print(" ", p)
ok = not problems
job.gate("cut_coverage", "pass" if ok else "fail")
job.note("rough_cut", f"verify-cut: {len(a)} words meant, {len(b)} heard, match {ratio:.0%}, {len(problems)} problems")
print(f"verify-cut: {'pass' if ok else 'FAIL'} · {len(a)} words meant · {len(b)} heard in the spine · match {ratio:.0%}")
sys.exit(0 if ok else 1)
