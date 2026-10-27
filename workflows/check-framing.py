#!/usr/bin/env python3
"""Gate — the shot is framed on the face, and every zoom punch lands on it. Measured on the spine with the face
detector, never judged from a contact sheet:

  framing   per clip (middle frame): face centre y within framing.face_y_tol of framing.face_y and face width at least
            framing.min_face_w (both only when framing.scale > 1 — a creator whose look is the tight shot)
  cuts      the face either side of every join moves ≤ framing.cut_jump_tol (match on the face)
  punches   0.05 s before vs 0.05 s after each snap: the face centre moves ≤ framing.anchor_tol (a punch that grows from
            the frame corner slid the face 6 % on 9278 — "the zooming in is completely off"), and it actually zooms in

Usage: python workflows/check-framing.py <job>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _faces import FaceFinder  # noqa: E402
from _lib import Job, Timeline  # noqa: E402

job = Job(sys.argv[1])
FR = job.numbers.get("framing", {})
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)
spine = job.p("preview", "spine.mp4")
w, h = job.numbers["canvas"]["width"] // 3, job.numbers["canvas"]["height"] // 3
ff = FaceFinder(w, h)


def face(t):
    f = ff.at(spine, t)
    return None if f is None else ((f[0] + f[2] / 2) / w, (f[1] + f[3] / 2) / h, f[2] / w)


def avg(t, ds):
    """Three frames averaged: one detector box is ±5 % in width."""
    got = [f for f in (face(t + d) for d in ds) if f]
    return tuple(sum(f[i] for f in got) / len(got) for i in range(3)) if got else None


errs, rows = [], []
S = float(FR.get("scale", 1.0))
for i, k in enumerate(cuts["keep"]):
    off, dur = tl.offsets[i], k["out"] - k["in"]
    if S > 1.0001:
        f = face(off + dur / 2)
        if f is None:
            rows.append(f"  clip {i}  no face at {off + dur / 2:.2f}s")
        else:
            dy = abs(f[1] - FR.get("face_y", 0.36))
            rows.append(f"  clip {i}  face y {f[1]:.2f} (target {FR.get('face_y', 0.36):.2f})  width {f[2]:.2f}")
            if dy > FR.get("face_y_tol", 0.06):
                errs.append(f"clip {i}: face centre y {f[1]:.2f} is {dy:.2f} off framing.face_y")
            if f[2] < FR.get("min_face_w", 0.0):
                errs.append(f"clip {i}: face width {f[2]:.2f} < framing.min_face_w {FR.get('min_face_w')}")
    z = k.get("zoom")
    if z:
        a, b = face(z["at"] - 0.05), face(min(z["at"] + z["dur"] + 0.05, off + dur - 0.05))   # the snap itself, not the speaker moving
        if a and b:
            drift = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
            rows.append(f"  punch {z['at']:.2f}s  face ({a[0]:.2f},{a[1]:.2f})→({b[0]:.2f},{b[1]:.2f})  drift {drift:.3f}  width {a[2]:.2f}→{b[2]:.2f}")
            if drift > FR.get("anchor_tol", 0.03):
                errs.append(f"punch at {z['at']:.2f}s moves the face {drift:.3f} (> framing.anchor_tol) — not anchored on the face")
            # a punch cued in the last frames of a clip eases out before it ever lands (9287: 0.28 → 0.28 at 43.10 s,
            # 0.03 s before the cut) — at least a quarter of the punch must show
            wa, wb = avg(z["at"], (-0.13, -0.09, -0.05)), avg(z["at"] + z["dur"], (0.05, 0.09, 0.13))   # one box is ±5 %
            if wa and wb and wb[2] / wa[2] < 1 + z["pct"] / 100 * 0.25:
                errs.append(f"punch at {z['at']:.2f}s does not zoom (face ×{wb[2] / wa[2]:.2f}) — cue it on a word with room before the cut")
        else:
            rows.append(f"  punch {z['at']:.2f}s  face not found on both sides — check by eye")
# cuts: the face sits in the same place on both sides of every join, only the pose changes (9278: "between clips
# there's a clear cut, it looks snappy instead of smooth": the framing jumped 0.15 of the width at one cut)
for j in tl.offsets[1:]:
    a, b = avg(j, (-0.12, -0.08, -0.04)), avg(j, (0.02, 0.06, 0.10))
    if a and b:
        jump = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        rows.append(f"  cut {j:6.2f}s  face ({a[0]:.2f},{a[1]:.2f})→({b[0]:.2f},{b[1]:.2f})  jump {jump:.3f}  size ×{b[2] / a[2]:.2f}")
        if abs(b[2] / a[2] - 1) > FR.get("cut_size_tol", 0.06):
            errs.append(f"cut at {j:.2f}s: the face changes size ×{b[2] / a[2]:.2f} (> framing.cut_size_tol)")
        if jump > FR.get("cut_jump_tol", 0.04):
            errs.append(f"cut at {j:.2f}s: the face jumps {jump:.3f} (> framing.cut_jump_tol) — framing not matched across the cut")
print("\n".join(rows))
for e in errs:
    print("error:", e)
job.gate("framing", "pass" if not errs else "fail")
print(f"check-framing: {'pass' if not errs else 'FAIL'} · {len(cuts['keep'])} clips · {sum(1 for k in cuts['keep'] if k.get('zoom'))} punches")
sys.exit(0 if not errs else 1)
