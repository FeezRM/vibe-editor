#!/usr/bin/env python3
"""Close the loop on cut matching. rough-cut predicts each clip's face size from the source; the lane frames on that
prediction; but the cut is judged on the framed spine, where the detector reads the face larger and the speaker may
still be settling on the first frames (9278 v4: fixing one cut's prediction moved a ×0.93 to another). This measures
every join on preview/spine.mp4 exactly as check-framing.py does, splits the size ratio between the two sides
(keep.fit = [first-frame trim, last-frame trim], within ±framing.fit_max), re-assembles the spine (only the changed
clips render) and measures again — up to framing.match_rounds rounds, stopping once every cut is within half of
framing.cut_size_tol.

Usage: python workflows/match-cuts.py <job>
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _faces import FaceFinder  # noqa: E402
from _lib import Job, Timeline  # noqa: E402

job = Job(sys.argv[1])
FR = job.numbers.get("framing", {})
if float(FR.get("scale", 1.0)) <= 1.0001:
    sys.exit(0)
w, h = job.numbers["canvas"]["width"] // 3, job.numbers["canvas"]["height"] // 3
ff = FaceFinder(w, h)
tol, fmax = FR.get("cut_size_tol", 0.06), FR.get("fit_max", 0.08)
lane = Path(__file__).resolve().parent.parent / "lanes" / "ffmpeg" / "assemble.py"


def avg(spine, t, ds):
    got = [f for f in (ff.at(spine, t + d) for d in ds) if f is not None]
    return sum(f[2] for f in got) / len(got) / w if got else None


for rnd in range(1, int(FR.get("match_rounds", 3)) + 1):
    cuts = job.read_json("cuts.json")
    tl, spine = Timeline(cuts), job.p("preview", "spine.mp4")
    worst, changed = 0.0, False
    for n, j in enumerate(tl.offsets[1:], start=1):
        a, b = avg(spine, j, (-0.12, -0.08, -0.04)), avg(spine, j, (0.02, 0.06, 0.10))   # check-framing's windows
        if not a or not b:
            continue
        r = b / a
        worst = max(worst, abs(r - 1))
        if abs(r - 1) <= tol / 2:
            continue
        before, after = cuts["keep"][n - 1], cuts["keep"][n]
        fb, fa = before.get("fit") or [1.0, 1.0], after.get("fit") or [1.0, 1.0]
        fb[1] = round(min(1 + fmax, max(1 - fmax, fb[1] * r ** 0.5)), 4)
        fa[0] = round(min(1 + fmax, max(1 - fmax, fa[0] / r ** 0.5)), 4)
        before["fit"], after["fit"] = fb, fa
        changed = True
        print(f"  round {rnd}  cut {j:6.2f}s  size ×{r:.2f} → trims {fb[1]:.3f} / {fa[0]:.3f}")
    if not changed:
        print(f"match-cuts: every cut within ±{tol / 2:.0%} after {rnd - 1} round(s) (worst ×{1 + worst:.2f})")
        break
    job.write_json(cuts, "cuts.json")
    subprocess.run([sys.executable, str(lane), str(job.dir), "--stage", "spine", "--quiet"], check=True)
else:
    print(f"match-cuts: stopped after {FR.get('match_rounds', 3)} rounds — check-framing has the last word")
