#!/usr/bin/env python3
"""The feedback loop — append a published result to docs/ledger.jsonl with what the opening was.

Records the hook mode, the frame-zero preset, the first spoken line, and the numbers you pass. Below
~300 reached accounts the row is marked insufficient-signal. Read the ledger before planning the
next opening; do not learn from one small upload.

Usage: python workflows/ledger.py <job> --add-result views=1200 reach=980 retention_3s=0.61 saves=12 [--note "..."]
       python workflows/ledger.py --show
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job, now  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job", nargs="?")
ap.add_argument("--add-result", nargs="*", default=None)
ap.add_argument("--note", default="")
ap.add_argument("--show", action="store_true")
a = ap.parse_args()
LEDGER = REPO / "docs" / "ledger.jsonl"

if a.show or not a.job:
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines()] if LEDGER.exists() else []
    for r in rows:
        print(f"{r['at'][:10]} {r['job']:<22} {r.get('hook_mode', '-'):<12} {r.get('frame_zero', '-'):<12} "
              f"reach={r.get('reach', '-')} r3s={r.get('retention_3s', '-')} {r.get('signal', '')}  «{r.get('first_line', '')[:40]}»")
    print(f"{len(rows)} rows")
    sys.exit(0)

job = Job(a.job)
plan = job.read_json("graphics-plan.json") if job.p("graphics-plan.json").exists() else {}
caps = job.read_json("captions.json")["groups"] if job.p("captions.json").exists() else []
first = next((g for g in sorted(plan.get("graphics", []), key=lambda g: g["cue"])), None)
row = {
    "at": now(), "job": job.state["job"], "hook_mode": plan.get("hook", {}).get("mode", first["preset"] if first else "-"),
    "frame_zero": first["preset"] if first else "-", "first_line": " ".join(g["text"] for g in caps[:2]),
    "graphics": len(plan.get("graphics", [])), "duration_s": job.read_json("cuts.json")["stats"]["kept_s"] if job.p("cuts.json").exists() else None,
    "note": a.note,
}
for kv in a.add_result or []:
    k, _, v = kv.partition("=")
    try:
        row[k] = float(v) if "." in v else int(v)
    except ValueError:
        row[k] = v
row["signal"] = "insufficient-signal" if float(row.get("reach", 0) or 0) < 300 else "ok"
LEDGER.parent.mkdir(exist_ok=True)
with open(LEDGER, "a") as f:
    f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"ledger: appended {row['job']} ({row['signal']})")
