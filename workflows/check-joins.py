#!/usr/bin/env python3
"""Gate — no whitespace anywhere in the cut. Measures, on the spine's own audio, every pause: a run of frames where the
voice sits cut.pause_rel_db under its own speech level (the 95th percentile of the spine). A pause that spans a clip
join fails over cut.join_gap_max_s, one inside a clip over cut.pause_gate_s. Frozen holds are deliberate and skipped.

Two misses this replaced: the spine silence gate only catches ≥ audio.silence_max_s, and a 0.25 s gap at every join
passed it (9278: "too much whitespace"); then an absolute −50 dB floor passed the gap after "Muse" (−43 dB room tone on
the final, digital silence on the gated lav) and 16 breaths inside clips (9278: "still too much pause"). His posted
reels never drop that far between words.

Usage: python workflows/check-joins.py <job>
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _lib import Job, Timeline  # noqa: E402

job = Job(sys.argv[1])
cfg = job.numbers["cut"]
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)
sr, hop = 16000, 160                       # 10 ms frames
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(job.p("preview", "spine.mp4")), "-vn", "-ac", "1", "-ar", str(sr),
                      "-f", "s16le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
n = len(x) // hop
db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
speech = float(np.percentile(db, 95))
quiet = db < speech - cfg.get("pause_rel_db", 30)
# holds: the frozen frame plays apad silence on purpose
held = np.zeros(n, bool)
for i, k in enumerate(cuts["keep"]):
    if k.get("hold"):
        end = tl.offsets[i] + k["out"] - k["in"]
        held[int(end * 100) - 5: int((end + k["hold"]) * 100) + 5] = True
joins = [int(round(j * 100)) for j in tl.offsets[1:]]
join_max, pause_max = cfg.get("join_gap_max_s", 0.12), cfg.get("pause_gate_s", 0.12)
rows, bad = [], 0
i = 0
while i < n:
    if not quiet[i]:
        i += 1
        continue
    e = i
    while e < n and quiet[e]:
        e += 1
    if i > 0 and e < n and not held[i:e].any():          # head and tail of the reel are not pauses
        gap = (e - i) / 100
        at_join = any(i - 2 <= j <= e + 2 for j in joins)
        limit = join_max if at_join else pause_max
        if gap > limit + 1e-6:
            bad += 1
            rows.append(f"  {'join ' if at_join else 'pause'} {i / 100:6.2f}s  {gap:.2f}s TOO LONG (> {limit:.2f})")
        elif gap >= 0.06:
            rows.append(f"  {'join ' if at_join else 'pause'} {i / 100:6.2f}s  {gap:.2f}s ok")
    i = e
print(f"  speech {speech:.1f} dB · quiet below {speech - cfg.get('pause_rel_db', 30):.1f} dB")
print("\n".join(rows))
job.gate("join_gaps", "pass" if not bad else "fail")
print(f"check-joins: {'pass' if not bad else 'FAIL'} · {len(joins)} joins · {bad} pauses over the limit")
sys.exit(0 if not bad else 1)
