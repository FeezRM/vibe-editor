#!/usr/bin/env python3
"""ffmpeg lane — replay the EDL and stack the layers into preview/<stage>.mp4.

Stages (cumulative):
  spine     cuts.json only (plus zoom punches if present)
  captions  + renders/captions.mov
  graphics  + every render in graphics-plan.json at its timeline cue
  audio     + voice gain, sfx-plan.json, music bed
  final     everything, export-quality encode → outputs/<job>.final.mp4

This lane is the verification lane on every machine and the delivery lane when Premiere is
absent or broken. Deterministic: same inputs, same file.

Usage: python lanes/ffmpeg/assemble.py <job> --stage spine|captions|graphics|audio|final [--out path]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "workflows"))
from _lib import REPO, Job, Timeline, die, ffprobe  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--stage", default="spine", choices=["spine", "captions", "graphics", "audio", "final"])
ap.add_argument("--out", default=None)
ap.add_argument("--quiet", action="store_true")
a = ap.parse_args()

job = Job(a.job)
N = job.numbers
fps = job.fps
W, H = N["canvas"]["width"], N["canvas"]["height"]
cuts = job.read_json("cuts.json")
tl = Timeline(cuts)
src_info = ffprobe(job.source)
SW, SH = src_info["width"], src_info["height"]
stage_rank = ["spine", "captions", "graphics", "audio", "final"].index(a.stage)

inputs = [str(job.source)]
fc = []  # filter_complex lines

# --- 1. replay the EDL --------------------------------------------------------
vparts, aparts = [], []
for i, k in enumerate(cuts["keep"]):
    v = f"[0:v]trim=start={k['in']:.3f}:end={k['out']:.3f},setpts=PTS-STARTPTS"
    z = k.get("zoom")
    if z:
        A = z["at"] - tl.offsets[i]
        P, D = z["pct"] / 100.0, z["dur"]
        u = f"clip((t-{A:.3f})/{D:.3f},0,1)"
        zexpr = f"(1+{P:.4f}*({u}*{u}*(3-2*{u})))"
        v += f",scale=w='iw*{zexpr}':h='ih*{zexpr}':eval=frame,crop={SW}:{SH}"
    fc.append(f"{v}[v{i}]")
    fc.append(f"[0:a]atrim=start={k['in']:.3f}:end={k['out']:.3f},asetpts=PTS-STARTPTS[a{i}]")
    vparts.append(f"[v{i}]")
    aparts.append(f"[a{i}]")
n = len(cuts["keep"])
fc.append("".join(vparts) + f"concat=n={n}:v=1:a=0[vcat]")
fc.append("".join(aparts) + f"concat=n={n}:v=0:a=1[acat]")
fc.append(f"[vcat]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps},format=yuv420p[base]")
vlast = "base"

# --- 2. overlays --------------------------------------------------------------
input_opts: list[list[str]] = [[]]

if stage_rank >= 1:
    cap_rel = (job.read_json("captions.json").get("render") if job.p("captions.json").exists() else None) or "renders/captions.mov"
    cap = job.p(cap_rel)
    if cap.exists():
        idx = len(inputs)
        inputs.append(str(cap))
        input_opts.append([])
        fc.append(f"[{idx}:v]format=rgba[o_cap]")
        fc.append(f"[{vlast}][o_cap]overlay=0:0:format=auto:eof_action=pass[capd]")
        vlast = "capd"
    elif a.stage != "spine":
        print("note: renders/captions.mov missing — captions layer skipped", file=sys.stderr)

if stage_rank >= 2 and job.p("graphics-plan.json").exists():
    plan = job.read_json("graphics-plan.json")
    for g in plan.get("graphics", []):
        render = g.get("render")
        if not render:
            continue
        rp = job.p(render)
        if not rp.exists():
            print(f"note: render missing for {g['id']}: {render}", file=sys.stderr)
            continue
        idx = len(inputs)
        inputs.append(str(rp))
        input_opts.append(["-itsoffset", f"{g['cue']:.3f}"])
        tag = f"g_{g['id']}"
        fc.append(f"[{idx}:v]format=rgba[o_{tag}]")
        fc.append(f"[{vlast}][o_{tag}]overlay=0:0:format=auto:eof_action=pass:enable='between(t,{g['cue']:.3f},{g['cue']+g['duration']:.3f})'[{tag}]")
        vlast = tag

# --- 3. audio -----------------------------------------------------------------
alast = "acat"
if stage_rank >= 3:
    A = N["audio"]
    gain = job.read_json("audio", "voice-gain.json") if job.p("audio", "voice-gain.json").exists() else None
    if gain:
        fc.append(f"[acat]volume={gain['gain_db']:.2f}dB,alimiter=limit={10**(A['peak_dbfs']/20):.4f}:level=false[voice]")
    else:
        fc.append("[acat]anull[voice]")
    mix = ["[voice]"]
    if job.p("sfx-plan.json").exists():
        sp = job.read_json("sfx-plan.json")
        for s in sp.get("sfx", []):
            f = job.p(s["file"])
            if not f.exists():
                continue
            idx = len(inputs)
            inputs.append(str(f))
            input_opts.append([])
            tag = f"s{len(mix)}"
            fc.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={s.get('db', A['sfx_db']):.1f}dB,adelay={int(s['cue']*1000)}|{int(s['cue']*1000)}[{tag}]")
            mix.append(f"[{tag}]")
    music = sp.get("music") if job.p("sfx-plan.json").exists() else None
    if music and job.p(music["file"]).exists():
        idx = len(inputs)
        inputs.append(str(job.p(music["file"])))
        input_opts.append(["-ss", f"{music.get('onset_s', 0):.3f}"])
        hook_end = music.get("hook_end_s", 0)
        bed, hook = music.get("db", A["music_db"]), music.get("hook_db", A["music_hook_db"])
        tail = A["music_tail_s"]
        vol = f"if(lt(t,{hook_end:.3f}),{10**(hook/20):.5f},{10**(bed/20):.5f})"
        fc.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{tl.duration + tail:.3f},"
                  f"volume='{vol}':eval=frame,afade=t=out:st={tl.duration:.3f}:d={tail:.3f}[mus]")
        mix.append("[mus]")
    if len(mix) > 1:
        fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:dropout_transition=0[amixed]")
        alast = "amixed"
    else:
        alast = "voice"

# --- 4. encode ----------------------------------------------------------------
out = Path(a.out) if a.out else (job.p("outputs", f"{job.state['job']}.final.mp4") if a.stage == "final"
                                   else job.p("preview", f"{a.stage}.mp4"))
out.parent.mkdir(parents=True, exist_ok=True)
E = N["export"]
cmd = ["ffmpeg", "-y", "-loglevel", "error" if a.quiet else "warning"]
for opts, src in zip(input_opts + [[]] * (len(inputs) - len(input_opts)), inputs):
    cmd += opts + ["-i", src]
cmd += ["-filter_complex", ";\n".join(fc), "-map", f"[{vlast}]", "-map", f"[{alast}]",
        "-c:v", E["codec"], "-pix_fmt", E["pix_fmt"], "-r", str(fps),
        "-c:a", "aac", "-b:a", f"{E['audio_kbps']}k", "-ar", "48000", "-movflags", "+faststart", "-shortest"]
if a.stage == "final":
    cmd += ["-crf", str(E["crf"]), "-preset", "slow", "-maxrate", f"{E['bitrate_mbps']}M", "-bufsize", f"{E['bitrate_mbps']*2}M"]
else:
    cmd += ["-crf", "23", "-preset", "veryfast"]
cmd += [str(out)]

t0 = time.time()
(job.p("preview") / f"{a.stage}.filtergraph.txt").write_text(";\n".join(fc))
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0 or not out.exists():
    print(r.stderr[-3000:], file=sys.stderr)
    die(f"assemble {a.stage} failed")
print(f"assemble[{a.stage}]: {out} · {tl.duration:.1f}s · {time.time()-t0:.0f}s")
