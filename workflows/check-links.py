#!/usr/bin/env python3
"""Gate — every relative link and every `archive#anchor` pointer in the tracked docs resolves."""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO  # noqa: E402

files = [Path(p) for p in subprocess.run(["git", "ls-files", "*.md"], capture_output=True, text=True, cwd=REPO).stdout.split()]
files = [REPO / f for f in files if not str(f).startswith("vendor/") and f.name != "REWORK-PLAN.md"]  # the plan carries intentional forward references
archive = (REPO / "docs" / "lab-notes-archive.md").read_text() if (REPO / "docs" / "lab-notes-archive.md").exists() else ""
anchors = set(re.findall(r"^## ([a-z0-9-]+)$", archive, re.M))
bad = []
for f in files:
    text = f.read_text(errors="ignore")
    for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
        target = m.group(1)
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        target = target.split("#")[0]
        if not target:
            continue
        if not (f.parent / target).exists() and not (REPO / target).exists():
            bad.append(f"{f.relative_to(REPO)}: link → {target}")
    for a in re.findall(r"archive#([a-z0-9-]+)", text):
        if a not in anchors:
            bad.append(f"{f.relative_to(REPO)}: archive#{a} has no section in docs/lab-notes-archive.md")
    for m in re.finditer(r"`((?:workflows|lanes|presets|scripts|tests|docs)/[A-Za-z0-9_./-]+)`", text):
        p = m.group(1).rstrip("/")
        if "<" in p or "*" in p or "…" in p:
            continue
        if not (REPO / p).exists():
            bad.append(f"{f.relative_to(REPO)}: path `{p}` does not exist")
for b in bad:
    print("broken:", b)
print(f"check-links: {len(files)} docs · {len(anchors)} archive anchors · {len(bad)} broken")
sys.exit(1 if bad else 0)
