#!/usr/bin/env python3
"""Node 02a — transcript. WhisperX once → transcript/words.json + segments.json.

words.json shape (the one every later node reads):
  [{"w": "imma", "s": 0.42, "e": 0.61, "score": 0.91, "seg": 0, "end_punct": "", "interp": false}]

Usage: python workflows/transcribe.py <job> [--engine whisperx|hyperframes] [--model large-v3]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO, Job, die  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--engine", default=None)
ap.add_argument("--model", default=None)
ap.add_argument("--force", action="store_true")
a = ap.parse_args()

job = Job(a.job)
job.require("transcript")
cfg = job.numbers["transcript"]
engine = a.engine or cfg["engine"]
model = a.model or cfg["model"]
tdir = job.p("transcript")
tdir.mkdir(exist_ok=True)
wav = tdir / "audio.wav"
out_words = tdir / "words.json"
if out_words.exists() and not a.force:
    print(f"transcript exists: {out_words} (use --force)")
    sys.exit(0)

t0 = time.time()
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(job.source), "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", str(wav)], capture_output=True, text=True)
if r.returncode != 0:
    die(f"audio extract failed: {r.stderr}")


def run_whisperx(model_name: str) -> dict:
    py = REPO / ".venv-whisperx" / "bin" / "whisperx"
    if not py.exists():
        die("WhisperX venv missing: uv venv --python 3.11 .venv-whisperx && uv pip install --python .venv-whisperx/bin/python whisperx")
    wxdir = tdir / "wx"
    shutil.rmtree(wxdir, ignore_errors=True)
    cmd = [str(py), str(wav), "--model", model_name, "--compute_type", cfg["compute_type"], "--device", "cpu",
           "--language", "en", "--vad_method", cfg["vad"], "--output_format", "json", "--output_dir", str(wxdir),
           "--print_progress", "False"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    jf = wxdir / "audio.json"
    if r.returncode != 0 or not jf.exists():
        die(f"whisperx failed:\n{r.stderr[-2000:]}")
    return json.loads(jf.read_text())


def normalise_whisperx(d: dict) -> tuple[list, list]:
    words, segs = [], []
    for si, seg in enumerate(d["segments"]):
        segs.append({"i": si, "s": seg["start"], "e": seg["end"], "text": seg["text"].strip()})
        raw = seg.get("words", [])
        # interpolate unaligned tokens ($10k, 2014., emoji) between aligned neighbours — never drop a word
        for wi, w in enumerate(raw):
            if "start" in w:
                continue
            prev_e = next((raw[j]["end"] for j in range(wi - 1, -1, -1) if "end" in raw[j]), seg["start"])
            nxt_s = next((raw[j]["start"] for j in range(wi + 1, len(raw)) if "start" in raw[j]), seg["end"])
            n_un = 1
            k = wi + 1
            while k < len(raw) and "start" not in raw[k]:
                n_un += 1
                k += 1
            span = max(nxt_s - prev_e, 0.12 * n_un)
            # this token is the first of a run of unaligned tokens; assign its slot
            run_start = wi
            while run_start > 0 and "start" not in raw[run_start - 1] and raw[run_start - 1].get("interp"):
                run_start -= 1
            idx_in_run = wi - run_start
            w["start"] = prev_e + span * idx_in_run / n_un if idx_in_run == 0 else raw[wi - 1]["end"]
            w["end"] = w["start"] + span / n_un
            w["interp"] = True
            w["score"] = w.get("score", 0.0)
        for w in raw:
            tok = w["word"].strip()
            if not tok:
                continue
            m = re.match(r"^(.*?)([.,!?;:…]+)$", tok)
            core, punct = (m.group(1), m.group(2)) if m else (tok, "")
            if not core:
                core, punct = tok, ""
            words.append({
                "w": core, "s": round(float(w["start"]), 3), "e": round(float(w["end"]), 3),
                "score": round(float(w.get("score", 0.0)), 3), "seg": si, "end_punct": punct,
                "interp": bool(w.get("interp", False)),
            })
    return words, segs


def run_hyperframes() -> tuple[list, list]:
    r = subprocess.run(["npx", "hyperframes", "transcribe", str(wav), "--json"], capture_output=True, text=True, cwd=str(tdir))
    m = re.search(r"\{.*\}", r.stdout, re.S)
    if not m:
        die(f"hyperframes transcribe failed: {r.stderr[-1500:]}")
    info = json.loads(m.group(0))
    tp = Path(info.get("transcriptPath", tdir / "transcript.json"))
    raw = json.loads(tp.read_text())
    items = raw if isinstance(raw, list) else raw.get("words", [])
    words = []
    for i, w in enumerate(items):
        tok = str(w.get("word") or w.get("text") or w.get("w") or "").strip()
        mm = re.match(r"^(.*?)([.,!?;:…]+)$", tok)
        core, punct = (mm.group(1), mm.group(2)) if mm else (tok, "")
        words.append({"w": core or tok, "s": round(float(w.get("start", w.get("s", 0))), 3),
                      "e": round(float(w.get("end", w.get("e", 0))), 3), "score": 1.0, "seg": 0,
                      "end_punct": punct, "interp": False})
    return words, [{"i": 0, "s": words[0]["s"] if words else 0, "e": words[-1]["e"] if words else 0, "text": " ".join(x["w"] for x in words)}]


if engine == "whisperx":
    try:
        data = run_whisperx(model)
    except SystemExit:
        if model != cfg["fallback_model"]:
            print(f"retrying with {cfg['fallback_model']}", file=sys.stderr)
            data = run_whisperx(cfg["fallback_model"])
            model = cfg["fallback_model"]
        else:
            raise
    words, segs = normalise_whisperx(data)
else:
    words, segs = run_hyperframes()
    model = "whisper.cpp"

# corrections: the ONLY place the transcript is edited. Whole-phrase, case-insensitive. Grammar is never touched.
corr_path = REPO / "presets" / job.state.get("preset", "vertical/default") / "transcript-corrections.json"
corrections = json.loads(corr_path.read_text()) if corr_path.exists() else {}
applied = []
if corrections:
    lower = [w["w"].lower() for w in words]
    for phrase, repl in sorted(corrections.items(), key=lambda kv: -len(kv[0].split())):
        toks = phrase.lower().split()
        n = len(toks)
        i = 0
        while i <= len(lower) - n:
            if lower[i:i + n] == toks:
                repl_toks = repl.split()
                first = words[i]
                merged = {**first, "w": repl, "e": words[i + n - 1]["e"], "end_punct": words[i + n - 1]["end_punct"]}
                applied.append({"at": first["s"], "from": " ".join(w["w"] for w in words[i:i + n]), "to": repl})
                words[i:i + n] = [merged]
                lower[i:i + n] = [repl.lower()]
                i += 1
            else:
                i += 1

job.write_json(words, "transcript", "words.json")
job.write_json(segs, "transcript", "segments.json")
job.write_json(applied, "transcript", "corrections-applied.json")
dur = words[-1]["e"] if words else 0
job.mark("transcript", "done", out="transcript/words.json", engine=f"{engine}-{model}", words=len(words),
         wall_s=round(time.time() - t0, 1))
job.note("transcript", f"{engine} {model}: {len(words)} words, {len(segs)} segments, {len(applied)} corrections, {time.time()-t0:.0f}s")
print(f"transcript: {len(words)} words · {len(segs)} segments · {len(applied)} corrections · {time.time()-t0:.0f}s → {out_words}")
