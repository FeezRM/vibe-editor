"""Preset library access: load a preset, validate params, fill the template, compare goldens."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import jinja2

from _lib import REPO, die

PRESETS = REPO / "presets" / "graphics"
PLACEHOLDER = re.compile(r"^\s*$|lorem|\bTBD\b|\[[^\]]*\]|^\?+$|^hook \d|^item \d|^row \d|placeholder|xxx", re.I)


def list_presets() -> list[str]:
    return sorted(p.name for p in PRESETS.iterdir() if p.is_dir() and (p / "template.html").exists())


def load(name: str) -> dict:
    d = PRESETS / name
    if not (d / "template.html").exists():
        die(f"unknown preset '{name}' (have: {', '.join(list_presets())})")
    schema = json.loads((d / "params.schema.json").read_text()) if (d / "params.schema.json").exists() else {}
    return {"name": name, "dir": d, "schema": schema}


def _sample_handles() -> set[str]:
    out = set()
    s = REPO / "samples"
    if s.exists():
        for f in s.glob("*.md"):
            out.update(re.findall(r"@([A-Za-z0-9_.]{3,})", f.read_text(errors="ignore")))
    return out


def _walk_real(value, path, errs):
    if isinstance(value, str):
        if PLACEHOLDER.search(value):
            errs.append(f"{path}: placeholder text '{value[:40]}'")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _walk_real(v, f"{path}[{i}]", errs)
    elif isinstance(value, dict):
        for k, v in value.items():
            _walk_real(v, f"{path}.{k}", errs)


def validate_params(preset: dict, params: dict, job_dir: Path | None = None) -> list[str]:
    """Light schema check + x-real placeholder refusal + asset existence. Returns error strings."""
    errs = []
    sch = preset["schema"]
    props = sch.get("properties", {})
    for req in sch.get("required", []):
        if req not in params:
            errs.append(f"missing required param '{req}'")
    for k, v in params.items():
        if k in ("duration", "placement", "reveal_at", "id"):
            continue
        spec = props.get(k)
        if spec is None:
            continue
        t = spec.get("type")
        if t == "array" and not isinstance(v, list):
            errs.append(f"'{k}' must be a list")
        if t == "string" and not isinstance(v, str):
            errs.append(f"'{k}' must be a string")
        if t in ("integer", "number") and not isinstance(v, (int, float)):
            errs.append(f"'{k}' must be a number")
        if isinstance(v, list) and "maxItems" in spec and len(v) > spec["maxItems"]:
            errs.append(f"'{k}' has {len(v)} items, max {spec['maxItems']}")
        if isinstance(v, list) and "minItems" in spec and len(v) < spec["minItems"]:
            errs.append(f"'{k}' has {len(v)} items, min {spec['minItems']}")
        if spec.get("x-real"):
            _walk_real(v, k, errs)
        if spec.get("x-asset") and job_dir is not None:
            files = v if isinstance(v, list) else [v]
            for f in files:
                fp = f["src"] if isinstance(f, dict) else f
                if not (job_dir / fp).exists():
                    errs.append(f"'{k}': asset not found: {fp}")
    handles = _sample_handles()
    blob = json.dumps(params)
    for h in handles:
        if h and h in blob:
            errs.append(f"handle '{h}' from samples/ appears in params — use creator.handle")
    return errs


def defaults(preset: dict) -> dict:
    out = {}
    for k, spec in preset["schema"].get("properties", {}).items():
        if "default" in spec:
            out[k] = spec["default"]
    return out


_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(PRESETS)), autoescape=True, undefined=jinja2.ChainableUndefined)


def fill(preset: dict, params: dict, comp_id: str, fps: int, numbers: dict, placement: str) -> str:
    G = numbers["graphics"]
    ctx = defaults(preset)
    ctx.update(params)
    ctx.setdefault("reveal_at", [])
    ctx.setdefault("line_2", None)
    ctx.update({
        "id": comp_id, "fps": fps, "placement": placement,
        "duration": float(params.get("duration", 3.0)),
        "entrance": round(sum(G["entrance_s"]) / 2, 3),
        "beside_top": G["beside_top"], "beside_inset": G["beside_inset"], "beside_width": G["beside_width"],
        "inline_top": G.get("inline_top", 1180), "inline_width": G.get("inline_width", 920),
        "handle": numbers.get("_handle", ""),
    })
    tpl = _env.get_template(f"{preset['name']}/template.html")
    return tpl.render(**ctx)


def ssim(a: Path, b: Path) -> float:
    r = subprocess.run(["ffmpeg", "-loglevel", "info", "-i", str(a), "-i", str(b), "-lavfi", "ssim", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"All:([0-9.]+)", r.stderr)
    return float(m.group(1)) if m else 0.0
