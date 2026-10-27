"""HyperFrames helpers: make the job folder a renderable project, render a composition to alpha .mov.

Re-renders always go to a NEW filename (Premiere may hold the old one open); the caller records the
mtime it got back and never trusts a file older than its plan.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from _lib import REPO, die, preset_file

# Windows installs npx as npx.cmd; CreateProcess does not search PATHEXT the way a shell does
NPX = shutil.which("npx") or "npx"


def scaffold_hf(job) -> None:
    d = job.dir
    if not (d / "hyperframes.json").exists():
        (d / "hyperframes.json").write_text(json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": False},
        }, indent=2))
    if not (d / "meta.json").exists():
        (d / "meta.json").write_text(json.dumps({"id": job.state["job"], "name": job.state["job"]}))
    if not (d / "index.html").exists():
        (d / "index.html").write_text("<!doctype html><html><head><meta charset='utf-8'><link rel='stylesheet' href='tokens.css'></head>"
                                      "<body style='background:#000;color:#fff'>job index — compositions render individually</body></html>")
    tokens_src = REPO / "brand" / "tokens.css"
    if tokens_src.exists():
        shutil.copy2(tokens_src, d / "tokens.css")
    fonts_src = preset_file(job.state.get("preset", "vertical/default"), "fonts")
    (d / "fonts").mkdir(exist_ok=True)
    if fonts_src.exists():
        for f in fonts_src.glob("*.ttf"):
            if not (d / "fonts" / f.name).exists():
                shutil.copy2(f, d / "fonts" / f.name)
    (d / "compositions").mkdir(exist_ok=True)
    (d / "renders").mkdir(exist_ok=True)


def unique_out(job, rel: str) -> Path:
    """renders/x.mov → a name this job has NEVER used (x-r2, x-r3, …), counted in renders/.seq — never a name Premiere
    may already hold, even if that file is gone from disk (a re-used name is a dead clip in the sequence)."""
    p = job.p(rel)
    stem, suf = re.sub(r"-r\d+$", "", p.stem), p.suffix
    seq = p.parent / ".seq"
    seq.parent.mkdir(parents=True, exist_ok=True)
    counts = json.loads(seq.read_text(encoding="utf-8")) if seq.exists() else {}
    n = max(counts.get(stem, 1), *[int(m.group(1)) for f in p.parent.glob(f"{stem}-r*{suf}") if (m := re.search(r"-r(\d+)$", f.stem))], 1)
    if n == 1 and not p.exists() and stem not in counts:
        counts[stem] = 1
        seq.write_text(json.dumps(counts), encoding="utf-8")
        return p
    n += 1
    counts[stem] = n
    seq.write_text(json.dumps(counts), encoding="utf-8")
    return p.with_name(f"{stem}-r{n}{suf}")


def render(job, comp_rel: str, out_rel: str, fmt: str = "mov", timeout: int = 1800) -> Path:
    out = unique_out(job, out_rel)
    cmd = [NPX, "--yes", "hyperframes", "render", str(job.dir), "-c", comp_rel, "--format", fmt, "--fps", str(int(job.fps)),
           "--low-memory-mode", "-o", str(out)]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
    if r.returncode != 0 or not out.exists():
        sys.stderr.write(r.stdout[-2000:] + "\n" + r.stderr[-3000:] + "\n")
        die(f"hyperframes render failed for {comp_rel}")
    if out.stat().st_mtime < t0 - 1:
        die(f"render output {out} is older than the render start — stale file")
    # superseded renders of the same stem are pruned on the ffmpeg lane only: on the premiere lane the sequence
    # still references them (deleting one leaves a dead clip; the new render is placed as a new clip)
    if job.state.get("lane", "ffmpeg") != "premiere":
        base = re.sub(r"-r\d+$", "", out.stem)
        for sib in out.parent.glob(f"{base}*{out.suffix}"):
            if sib != out and re.sub(r"-r\d+$", "", sib.stem) == base:
                try:
                    sib.unlink()
                except OSError:
                    pass
    return out


def lint(job, comp_rel: str) -> tuple[bool, str]:
    """Lint the whole job project (the CLI has no per-composition flag); report lines mentioning comp_rel."""
    r = subprocess.run([NPX, "--yes", "hyperframes", "lint", str(job.dir), "--json"], capture_output=True, text=True, cwd=str(REPO))
    try:
        data = json.loads(r.stdout[r.stdout.index("{"):]) if "{" in r.stdout else {}
    except Exception:
        data = {}
    findings = data.get("findings") or data.get("issues") or []
    mine = [f for f in findings if comp_rel.split("/")[-1] in json.dumps(f)]
    errors = [f for f in mine if str(f.get("severity", f.get("level", ""))).lower() == "error"]
    text = "\n".join(f"{f.get('severity', f.get('level'))}: {f.get('rule', f.get('id'))} — {f.get('message', '')[:160]}" for f in mine[:12])
    return not errors, text
