"""Shared helpers for every workflow node: job folder, RUN.md state, preset numbers, ffprobe.

Nodes exchange files, not chat. This module is the only place that knows the job layout.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NODE_ORDER = ["intake", "transcript", "rough_cut", "captions", "graphics", "audio", "pacing", "export"]


def die(msg: str, code: int = 1):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ffprobe(path: Path) -> dict:
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if r.returncode != 0:
        die(f"ffprobe failed on {path}: {r.stderr.strip()}")
    info = json.loads(r.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    fps = 30.0
    if v and v.get("r_frame_rate"):
        n, d = v["r_frame_rate"].split("/")
        fps = float(n) / float(d) if float(d) else 30.0
    return {
        "duration": float(info["format"].get("duration", 0)),
        "width": int(v["width"]) if v else 0,
        "height": int(v["height"]) if v else 0,
        "fps": fps,
        "has_audio": a is not None,
    }


def sha256(path: Path, limit_mb: int = 64) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(limit_mb * 1024 * 1024))
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# preset numbers
# ---------------------------------------------------------------------------

def load_numbers(preset: str = "vertical/default") -> dict:
    p = REPO / "presets" / preset / "numbers.json"
    if not p.exists():
        die(f"preset numbers not found: {p}")
    return json.loads(p.read_text())


def load_brand() -> dict:
    p = REPO / "brand" / "brand.json"
    return json.loads(p.read_text()) if p.exists() else {}


# ---------------------------------------------------------------------------
# RUN.md — YAML-ish front matter we read and write ourselves (no PyYAML dependency)
# ---------------------------------------------------------------------------

class Job:
    def __init__(self, job_dir: str | Path):
        self.dir = Path(job_dir).resolve()
        self.run_md = self.dir / "RUN.md"
        if not self.run_md.exists():
            die(f"no RUN.md in {self.dir} — create the job with workflows/new-job.py")
        self.state = self._read()
        self.numbers = load_numbers(self.state.get("preset", "vertical/default"))
        self.brand = load_brand()

    # paths ---------------------------------------------------------------
    def p(self, *parts) -> Path:
        return self.dir.joinpath(*parts)

    def read_json(self, *parts):
        return json.loads(self.p(*parts).read_text())

    def write_json(self, obj, *parts):
        path = self.p(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
        return path

    @property
    def source(self) -> Path:
        return self.p(self.state["source"])

    @property
    def fps(self) -> float:
        return float(self.state.get("fps", 30))

    # state ---------------------------------------------------------------
    def _read(self) -> dict:
        text = self.run_md.read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if not m:
            die("RUN.md has no front matter")
        self._body = m.group(2)
        return _parse_front(m.group(1))

    def save(self):
        self.run_md.write_text("---\n" + _dump_front(self.state) + "\n---\n" + self._body)

    def node_status(self, node: str) -> str:
        return self.state.get("nodes", {}).get(node, {}).get("status", "pending")

    def require(self, node: str):
        """Refuse to run when a predecessor is not done."""
        idx = NODE_ORDER.index(node)
        for prev in NODE_ORDER[:idx]:
            if self.node_status(prev) != "done":
                die(f"node '{node}' needs '{prev}' done first (status: {self.node_status(prev)})", 3)

    def mark(self, node: str, status: str, invalidate: bool = True, **fields):
        nodes = self.state.setdefault("nodes", {})
        entry = {"status": status, "at": now()}
        entry.update(fields)
        nodes[node] = entry
        if status == "done" and invalidate:
            for later in NODE_ORDER[NODE_ORDER.index(node) + 1:]:
                if nodes.get(later, {}).get("status") == "done":
                    nodes[later]["status"] = "stale"
        self.save()

    def gate(self, name: str, result: str):
        self.state.setdefault("gates", {})[name] = result
        self.save()

    def note(self, node: str, text: str):
        self._body = self._body.rstrip("\n") + f"\n- {node}: {text}\n"
        self.save()

    @property
    def brief(self) -> str:
        m = re.search(r"## Brief\n(.*?)(?:\n## |\Z)", self._body, re.S)
        return m.group(1).strip() if m else ""


def _parse_scalar(v: str):
    v = v.strip()
    if v in ("true", "false"):
        return v == "true"
    if v == "null" or v == "":
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for part in _split_top(v[1:-1]):
            if ":" in part:
                k, val = part.split(":", 1)
                out[k.strip()] = _parse_scalar(val)
        return out
    if v.startswith("[") and v.endswith("]"):
        return [_parse_scalar(x) for x in _split_top(v[1:-1]) if x.strip()]
    return v.strip("'\"")


def _split_top(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def _parse_front(text: str) -> dict:
    root: dict = {}
    stack = [(-1, root)]
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val.strip() == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(val)
    return root


def _dump_scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {_dump_scalar(x)}" for k, x in v.items()) + "}"
    if isinstance(v, list):
        return "[" + ", ".join(_dump_scalar(x) for x in v) + "]"
    if isinstance(v, float):
        return f"{v:.3f}".rstrip("0").rstrip(".")
    s = str(v)
    return s if re.match(r"^[A-Za-z0-9_./:@+-]+$", s) else json.dumps(s)


def _dump_front(d: dict, indent: int = 0) -> str:
    lines = []
    for k, v in d.items():
        pad = "  " * indent
        if isinstance(v, dict) and v and all(isinstance(x, dict) for x in v.values()):
            lines.append(f"{pad}{k}:")
            lines.append(_dump_front(v, indent + 1))
        elif isinstance(v, dict) and v and k in ("nodes", "gates"):
            lines.append(f"{pad}{k}:")
            for kk, vv in v.items():
                lines.append(f"{pad}  {kk}: {_dump_scalar(vv)}")
        else:
            lines.append(f"{pad}{k}: {_dump_scalar(v)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# time mapping between source and timeline through cuts.json
# ---------------------------------------------------------------------------

class Timeline:
    """Map source seconds -> timeline seconds using the EDL's keep ranges."""

    def __init__(self, cuts: dict):
        self.keep = cuts["keep"]
        self.offsets = []
        t = 0.0
        for k in self.keep:
            self.offsets.append(t)
            t += k["out"] - k["in"]
        self.duration = t

    def to_timeline(self, src_t: float) -> float | None:
        for k, off in zip(self.keep, self.offsets):
            if k["in"] - 1e-6 <= src_t <= k["out"] + 1e-6:
                return off + (src_t - k["in"])
        return None

    def to_source(self, tl_t: float) -> float | None:
        for k, off in zip(self.keep, self.offsets):
            d = k["out"] - k["in"]
            if off - 1e-6 <= tl_t <= off + d + 1e-6:
                return k["in"] + (tl_t - off)
        return None
