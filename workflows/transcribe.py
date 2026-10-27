#!/usr/bin/env python3
"""Node 02a — transcript. WhisperX once → transcript/words.json + segments.json.

Two repairs after the main pass, both timing-only (the words are never edited): a word longer than
transcript.clamp_word_s is clamped to the first silence after it (the aligner stretches the last word before
a pause across the pause), and any stretch of speech ≥ transcript.gap_min_s with no word is transcribed on
its own and merged back (WhisperX drops a repeated take as if it were a hallucination).

words.json shape (the one every later node reads):
  [{"w": "imma", "s": 0.42, "e": 0.61, "score": 0.91, "seg": 0, "end_punct": "", "interp": false}]

--spine transcribes the assembled cut (preview/spine.mp4) instead of the raw → transcript/spine-words.json, in
TIMELINE time. Captions read it when present: a raw with retakes aligns words to the wrong take, and a remap through
the EDL then drops or shifts every word near a cut (9077: "This video" and "and the final result is" vanished and the
caption after them ran 1 s early). The spine's audio is exactly what the viewer hears, so its words need no remap.

Usage: python workflows/transcribe.py <job> [--engine whisperx|hyperframes] [--model large-v3] [--spine]
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
from _lib import REPO, Job, die, preset_file  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--engine", default=None)
ap.add_argument("--model", default=None)
ap.add_argument("--force", action="store_true")
ap.add_argument("--spine", action="store_true", help="transcribe preview/spine.mp4 → transcript/spine-words.json (timeline time)")
a = ap.parse_args()

job = Job(a.job)
job.require("captions" if a.spine else "transcript")
cfg = job.numbers["transcript"]
engine = a.engine or cfg["engine"]
model = a.model or cfg["model"]
tdir = job.p("transcript")
tdir.mkdir(exist_ok=True)
src_media = job.p("preview", "spine.mp4") if a.spine else job.source
if a.spine and not src_media.exists():
    die("--spine needs preview/spine.mp4 (assemble.py --stage spine)")
wav = tdir / ("spine.wav" if a.spine else "audio.wav")
out_words = tdir / ("spine-words.json" if a.spine else "words.json")
if a.spine and out_words.exists() and out_words.stat().st_mtime < src_media.stat().st_mtime:
    a.force = True   # the cut changed since the last spine transcript
if out_words.exists() and not a.force:
    print(f"transcript exists: {out_words} (use --force)")
    sys.exit(0)

t0 = time.time()
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src_media), "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", str(wav)], capture_output=True, text=True)
if r.returncode != 0:
    die(f"audio extract failed: {r.stderr}")


def run_whisperx(model_name: str, src: Path = None) -> dict:
    src = src or wav
    py = next((c for c in (REPO / ".venv-whisperx" / "bin" / "python",
                           REPO / ".venv-whisperx" / "Scripts" / "python.exe") if c.exists()), None)
    if py is None:
        die("WhisperX venv missing: uv venv --python 3.11 .venv-whisperx && uv pip install --python .venv-whisperx/bin/python whisperx")
    wxdir = tdir / ("wx" if src == wav else f"wx-{src.stem}")
    shutil.rmtree(wxdir, ignore_errors=True)
    # _wx_spell.py = the WhisperX CLI with digits spelled out before alignment (wav2vec2 cannot time "30%")
    cmd = [str(py), str(Path(__file__).parent / "_wx_spell.py"), str(src), "--model", model_name, "--compute_type", cfg["compute_type"], "--device", "cpu",
           "--language", "en", "--vad_method", cfg["vad"], "--output_format", "json", "--output_dir", str(wxdir),
           "--print_progress", "False"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    jf = wxdir / f"{src.stem}.json"
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
    r = subprocess.run([shutil.which("npx") or "npx", "hyperframes", "transcribe", str(wav), "--json"], capture_output=True, text=True, cwd=str(tdir))
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

# aligner overshoot: WhisperX stretches the last word before a pause across the whole pause ("faster" 8 s long).
# Clamp any word longer than clamp_word_s to the first silence (silence_db / ≥ 0.25 s) after its start. Timing only;
# the word itself is never edited. Flagged `clamped` so the gate and the cut can see it.
_env = None


def envelope(wav_path: Path) -> tuple[list, float]:
    """20 ms peak envelope of the 16 kHz mono wav -> (peaks, hop_s). Computed once."""
    global _env
    if _env is None:
        import wave
        with wave.open(str(wav_path), "rb") as f:
            sr = f.getframerate()
            pcm = memoryview(f.readframes(f.getnframes())).cast("h")
        hop = int(sr * 0.02)
        _env = ([max(abs(v) for v in pcm[i:i + hop]) if len(pcm[i:i + hop]) else 0 for i in range(0, len(pcm), hop)], hop / sr)
    return _env


def clamp_overlong(words: list, wav_path: Path) -> int:
    limit = cfg.get("clamp_word_s", 1.0)
    longs = [w for w in words if w["e"] - w["s"] > limit]
    if not longs:
        return 0
    peaks, hop_s = envelope(wav_path)
    thr = 10 ** (job.numbers["audio"]["silence_db"] / 20) * 32768
    n = 0
    for w in longs:
        quiet = 0
        end = None
        for i in range(int((w["s"] + 0.12) / hop_s), min(int(w["e"] / hop_s), len(peaks))):
            quiet = quiet + 1 if peaks[i] < thr else 0
            if quiet * hop_s >= 0.25:
                end = (i + 1) * hop_s - 0.25
                break
        if end is not None and end < w["e"]:
            w["e"] = round(end + 0.05, 3)
            w["clamped"] = True
            n += 1
    return n


def speech_regions(wav_path: Path, min_len: float = 0.6, min_gap: float = 0.4) -> list:
    peaks, hop_s = envelope(wav_path)
    thr = 10 ** (job.numbers["audio"]["silence_db"] / 20) * 32768
    regions, start, quiet = [], None, 0
    for i, pk in enumerate(peaks):
        if pk >= thr:
            if start is None:
                start = i * hop_s
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * hop_s >= min_gap:
                end = (i - quiet + 1) * hop_s
                if end - start >= min_len:
                    regions.append((start, end))
                start, quiet = None, 0
    if start is not None:
        regions.append((start, len(peaks) * hop_s))
    return regions


def fill_gaps(words: list, segs: list, model_name: str) -> int:
    """WhisperX drops a repeated take (the second "So if you want to do this...") as if it were a hallucination.
    Any stretch of speech >= gap_min_s that holds no word is transcribed on its own and merged back as a new segment."""
    gap_min = cfg.get("gap_min_s", 1.0)
    holes = []
    for a, b in speech_regions(wav):
        cursor = a
        for w in words:
            if w["e"] <= a or w["s"] >= b:
                continue
            if w["s"] - cursor > gap_min:
                holes.append((cursor, w["s"]))
            cursor = max(cursor, w["e"])
        if b - cursor > gap_min:
            holes.append((cursor, b))
    added = 0
    for hi, (a, b) in enumerate(holes):
        a0, b0 = max(0.0, a - 0.35), b + 0.35
        chunk = tdir / f"{'sgap' if wav.name == 'spine.wav' else 'gap'}{hi:02d}.wav"   # raw and spine runs must not share chunks
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a0:.3f}", "-t", f"{b0-a0:.3f}", "-i", str(wav), str(chunk)], check=True)
        try:
            d = run_whisperx(model_name, chunk)
        except SystemExit:
            continue
        new, _ = normalise_whisperx(d)
        seg_i = (max(x["seg"] for x in words) + 1) if words else 0
        kept = []
        for w in new:
            w["s"], w["e"] = round(w["s"] + a0, 3), round(w["e"] + a0, 3)
            mid = (w["s"] + w["e"]) / 2
            if a - 0.1 <= mid <= b + 0.1:
                # the chunk is padded; a word may reach into the neighbours — clamp it to the hole
                w["s"], w["e"] = max(w["s"], round(a, 3)), min(w["e"], round(b, 3))
                if w["e"] - w["s"] < 0.02:
                    continue
                w["seg"] = seg_i
                w["gapfill"] = True
                kept.append(w)
        if kept:
            text = " ".join(x["w"] + x["end_punct"] for x in kept)
            words.extend(kept)
            words.sort(key=lambda x: x["s"])
            segs.append({"i": seg_i, "s": kept[0]["s"], "e": kept[-1]["e"], "text": text})
            segs.sort(key=lambda x: x["s"])
            added += len(kept)
            print(f"gap {a:.2f}-{b:.2f}: +{len(kept)} words '{text[:60]}'")
    return added


clamped = clamp_overlong(words, wav)
filled = fill_gaps(words, segs, model) if engine == "whisperx" else 0
clamped += clamp_overlong(words, wav)

# corrections: the ONLY place the transcript is edited. Whole-phrase, case-insensitive. Grammar is never touched.
corr_path = preset_file(job.state.get("preset", "vertical/default"), "transcript-corrections.json")
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

if a.spine:
    job.write_json(words, "transcript", "spine-words.json")
    # which cut these words belong to: plan-captions compares this, not file times (the pacing node re-assembles
    # the spine for zoom punches — same audio, newer file — and the mtime test fell back to the raw transcript)
    import hashlib
    keys = [[k["in"], k["out"], k.get("hold", 0.0)] for k in job.read_json("cuts.json")["keep"]]
    job.p("transcript", "spine-words.key").write_text(hashlib.sha1(json.dumps(keys).encode()).hexdigest())
    job.note("captions", f"spine transcript: {len(words)} words in timeline time, {len(applied)} corrections, {clamped} clamped, {filled} gap-filled, {time.time()-t0:.0f}s")
    print(f"transcript --spine: {len(words)} words · {len(applied)} corrections · {time.time()-t0:.0f}s → {out_words}")
    sys.exit(0)
job.write_json(words, "transcript", "words.json")
job.write_json(segs, "transcript", "segments.json")
job.write_json(applied, "transcript", "corrections-applied.json")
dur = words[-1]["e"] if words else 0
job.mark("transcript", "done", out="transcript/words.json", engine=f"{engine}-{model}", words=len(words),
         wall_s=round(time.time() - t0, 1))
job.note("transcript", f"{engine} {model}: {len(words)} words, {len(segs)} segments, {len(applied)} corrections, {clamped} clamped, {filled} gap-filled, {time.time()-t0:.0f}s")
print(f"transcript: {len(words)} words · {len(segs)} segments · {len(applied)} corrections · {clamped} clamped · {filled} gap-filled · {time.time()-t0:.0f}s → {out_words}")
