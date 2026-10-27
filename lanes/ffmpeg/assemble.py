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
SFPS = float(src_info["fps"])
stage_rank = ["spine", "captions", "graphics", "audio", "final"].index(a.stage)
FR = N.get("framing", {})
PC = N.get("pacing", {})

inputs: list[str] = []
input_opts: list[list[str]] = []
fc = []  # filter_complex lines

# --- 1. replay the EDL --------------------------------------------------------
# Pass 1: every clip is rendered on its own — input-seeked, so only its own seconds are decoded, framed and punched,
# straight to canvas size — into preview/clips/ (cached by everything that shapes it). Pass 2 joins them with the concat
# demuxer, so the main graph never holds a 4K frame. One graph replaying N clips from a 4K raw queued every decoded
# frame ahead of concat: 23 GB and an out-of-memory abort on a 19 s cut (archive#assemble-ram).
import hashlib  # noqa: E402

S = float(FR.get("scale", 1.0))
clip_dir = job.p("preview", "clips")
clip_dir.mkdir(parents=True, exist_ok=True)
src_mtime = job.source.stat().st_mtime
_ws = sorted(k["face"][2] for k in cuts["keep"] if k.get("face"))
WREF = _ws[len(_ws) // 2] if _ws else None          # the median face width: every cut is matched to it
if S > 1.0001 and WREF and FR.get("face_w"):
    # frame to a face size, not a fixed zoom: a take shot from further back gets the same tight shot (9280 at 1.45×
    # left the face 0.23 wide where 9278's was 0.27) — capped at framing.max_scale (2.0 on a 2160-wide source is 1:1 pixels)
    S = min(max(S, float(FR["face_w"]) / WREF), float(FR.get("max_scale", 1.8)))
listing = []
for i, k in enumerate(cuts["keep"]):
    dur = k["out"] - k["in"]
    z = k.get("zoom")
    v = "setpts=PTS-STARTPTS"
    if z or S > 1.0001:
        # base framing × punch, anchored on the face (cuts.json keep.face_in → face_out, from rough-cut): the window glides
        # from where the face is on the clip's first frame to where it is on its last, so across every cut the face sits
        # in the same place and only the pose changes (a framing that jumped at each cut read as a snap — 9278). With
        # framing the face lands at (0.5, face_y); without, a punch keeps it where it is. zoompan, not scale+crop
        # (archive#zoom-anchor). A punch snaps in on its word, holds, and eases back out before the cut.
        f0 = (k.get("face_in") or k.get("face") or [0.5, 0.42])[:2]
        f1 = (k.get("face_out") or k.get("face") or [0.5, 0.42])[:2]
        g = f"clip(in/{SFPS:.3f}/{dur:.3f},0,1)"
        fx, fy = f"({f0[0]:.4f}+({f1[0] - f0[0]:.4f})*{g})", f"({f0[1]:.4f}+({f1[1] - f0[1]:.4f})*{g})"
        mid = (k.get("face") or [0.5, 0.42])[:2]
        tx, ty = (0.5, float(FR.get("face_y", 0.36))) if S > 1.0001 else tuple(mid)
        # the face the same size across cuts: the base scale follows face_in → face_out width toward the cut's median,
        # within ±framing.size_match (takes shot at different distances jumped 11 % at a cut)
        SB = f"{S:.4f}"
        if S > 1.0001 and WREF:
            w0 = (k.get("face_in") or k.get("face") or [0, 0, WREF])[2]
            w1 = (k.get("face_out") or k.get("face") or [0, 0, WREF])[2]
            m = float(FR.get("size_match", 0.1))
            SB = f"({S:.4f}*clip({WREF:.4f}/({w0:.4f}+({w1 - w0:.4f})*{g}),{1 - m:.3f},{1 + m:.3f}))"
        # match-cuts.py's measured trim (keep.fit = [first frame, last frame]): the prediction above is made on the
        # source, the cut is judged on the framed spine — the loop closes the last few percent
        fi, fo = (k.get("fit") or [1.0, 1.0])
        if abs(fi - 1) > 1e-4 or abs(fo - 1) > 1e-4:
            SB = f"({SB}*({fi:.4f}+({fo - fi:.4f})*{g}))"
        zexpr = SB
        if z:
            A = z["at"] - tl.offsets[i]
            P, D = z["pct"] / 100.0, max(0.02, z["dur"])
            up = f"clip((in/{SFPS:.3f}-{A:.3f})/{D:.3f},0,1)"
            ramp = f"({up}*{up}*(3-2*{up}))"
            OUT, HOLD = float(PC.get("zoom_out_s", 0.4)), float(PC.get("zoom_hold_s", 1.4))
            o0 = min(A + D + HOLD, dur - OUT - 0.08)          # the punch is all the way out before the cut
            if o0 > A + D:
                dn = f"clip((in/{SFPS:.3f}-{o0:.3f})/{OUT:.3f},0,1)"
                ramp = f"({ramp}*(1-{dn}*{dn}*(3-2*{dn})))"
            zexpr = f"{SB}*(1+{P:.4f}*{ramp})"
        # window left/top at the base scale follows the face path; a punch then zooms around the face measured at the
        # punch (zoom.face): left' = P − (P − left)·S/zoom keeps P where it was on screen
        lx, ly = f"({fx}-{tx:.4f}/{SB})", f"({fy}-{ty:.4f}/{SB})"
        px, py = (z.get("face") or [None, None]) if z else (None, None)
        xe = f"({px:.4f}-({px:.4f}-{lx})*{SB}/zoom)" if px is not None else lx
        ye = f"({py:.4f}-({py:.4f}-{ly})*{SB}/zoom)" if py is not None else ly
        v += (f",zoompan=z='{zexpr}':x='clip({xe}*iw,0,iw-iw/zoom)'"
              f":y='clip({ye}*ih,0,ih-ih/zoom)':d=1:s={W}x{H}:fps={SFPS:.3f}")
    else:
        v += f",scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    # a whole number of frames, and the audio cut to exactly that: trim=duration kept a partial last frame, every clip
    # ran up to a frame long, and 34 clips drifted the spine 0.17 s off the EDL (9287 — cut checks measured the wrong frames)
    nf = max(1, round(dur * fps))
    v += f",setsar=1,fps={fps},trim=end_frame={nf},format=yuv420p"
    af = f"asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=end_sample={round(nf / fps * 48000)}"
    hold = k.get("hold", 0.0)   # a frozen beat after the keep: last frame cloned, silence under it
    if hold:
        v += f",tpad=stop_mode=clone:stop_duration={hold:.3f}"
        af += f",apad=pad_dur={hold:.3f}"
    key = hashlib.sha1(json.dumps([str(job.source), src_mtime, k["in"], k["out"], v, af, W, H, fps]).encode()).hexdigest()[:12]
    cp = clip_dir / f"c{i:02d}-{key}.mkv"
    if not cp.exists():
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{k['in']:.3f}", "-t", f"{dur + 0.25:.3f}", "-i", str(job.source),
                            "-vf", v, "-af", af, "-c:v", "libx264", "-crf", "10", "-preset", "veryfast", "-c:a", "pcm_s16le",
                            str(cp)], capture_output=True, text=True)
        if r.returncode != 0 or not cp.exists():
            print(r.stderr[-2000:], file=sys.stderr)
            die(f"assemble: clip {i} failed")
    listing.append(f"file '{cp.as_posix()}'")
for old in clip_dir.glob("c*.mkv"):            # clips of an older cut
    if f"file '{old.as_posix()}'" not in listing:
        old.unlink()
concat_list = clip_dir / "concat.txt"
concat_list.write_text("\n".join(listing) + "\n")
inputs.append(str(concat_list))
input_opts.append(["-f", "concat", "-safe", "0"])
fc.append(f"[0:v]setpts=PTS-STARTPTS,format=yuv420p[base]")
fc.append(f"[0:a]asetpts=PTS-STARTPTS[acat]")
vlast = "base"

# --- 2. overlays --------------------------------------------------------------

# B-roll (broll-plan.json): full-frame cutaways in timeline time, filled to the canvas, under every other layer.
# A voice-only job (no A-roll) is a black raw covered end to end by these. A windowed clip (`box`) is a
# pre-render from build-broll.py — canvas-sized with alpha, carrying its own audio, which joins the mix on
# every stage but the spine (the spine is what transcribe --spine captions: the voice only).
broll_audio = []
if job.p("broll-plan.json").exists():
    for i, c in enumerate(job.read_json("broll-plan.json").get("clips", [])):
        if c.get("box") or c.get("title"):
            rp = job.p(c["render"]) if c.get("render") else None
            if not rp or not rp.exists():
                die(f"b-roll window {c['id']} not built — run workflows/build-broll.py")
            idx = len(inputs)
            inputs.append(str(rp))
            input_opts.append(["-itsoffset", f"{c['start']:.3f}"])
            fc.append(f"[{idx}:v]format=rgba[bw{i}]")
            fc.append(f"[{vlast}][bw{i}]overlay=0:0:format=auto:eof_action=pass:enable='between(t,{c['start']:.3f},{c['end']:.3f})'[bd{i}]")
            vlast = f"bd{i}"
            if c.get("render_audio") and stage_rank >= 1:
                ms = int(round(c["start"] * 1000))
                fc.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
                          f"volume={c.get('audio_db', 0.0):.1f}dB,adelay={ms}|{ms}[ba{i}]")
                broll_audio.append(f"[ba{i}]")
            continue
        bp = Path(c["file"]) if Path(c["file"]).is_absolute() else job.p(c["file"])
        if not bp.exists():
            die(f"b-roll missing on disk: {bp}")
        idx = len(inputs)
        inputs.append(str(bp))
        spd, pan = c.get("speed", 1.0), c.get("pan", 0.5)   # pan: 0 = left edge of the source, 1 = right edge
        top = int(c.get("crop_top", 0))                      # source rows to drop (a recorded app's top bar)
        input_opts.append(["-ss", f"{c['src_in']:.3f}", "-t", f"{(c['end'] - c['start']) * spd + 0.1:.3f}"])
        fc.append(f"[{idx}:v]setpts=(PTS-STARTPTS)/{spd:.4f}+{c['start']:.3f}/TB,crop=iw:ih-{top}:0:{top},"
                  f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:(iw-{W})*{pan:.3f}:(ih-{H})/2,setsar=1,fps={fps},format=yuv420p[b{i}]")
        fc.append(f"[{vlast}][b{i}]overlay=0:0:eof_action=pass:enable='between(t,{c['start']:.3f},{c['end']:.3f})'[bd{i}]")
        vlast = f"bd{i}"

# hook titles (broll-plan.json "titles"): their own layer over the b-roll; captions are dropped under them
if job.p("broll-plan.json").exists():
    for i, t in enumerate(job.read_json("broll-plan.json").get("titles", [])):
        rp = job.p(t["render"]) if t.get("render") else None
        if not rp or not rp.exists():
            die(f"title {t['id']} not built — run workflows/build-broll.py")
        idx = len(inputs)
        inputs.append(str(rp))
        input_opts.append(["-itsoffset", f"{t['start']:.3f}"])
        fc.append(f"[{idx}:v]format=rgba[tt{i}]")
        fc.append(f"[{vlast}][tt{i}]overlay=0:0:format=auto:eof_action=pass:enable='between(t,{t['start']:.3f},{t['end']:.3f})'[td{i}]")
        vlast = f"td{i}"

def overlay_graphics(gs):
    """Graphic renders onto the stack, each enabled for its own window (itsoffset puts render t=0 at the cue)."""
    global vlast
    for g in gs:
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


# a `wash` layer (a colour flood, a replaced background) is part of the picture: it goes UNDER the captions;
# every other graphic sits above them (QA keeps those out of the caption band)
gfx = job.read_json("graphics-plan.json").get("graphics", []) if stage_rank >= 2 and job.p("graphics-plan.json").exists() else []
under = [g for g in gfx if g.get("placement_resolved", g.get("placement")) == "wash"]
overlay_graphics(under)

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

overlay_graphics([g for g in gfx if g not in under])

# --- 3. audio -----------------------------------------------------------------
alast = "acat"
if broll_audio and stage_rank < 3:
    fc.append("[acat]" + "".join(broll_audio) + f"amix=inputs={1 + len(broll_audio)}:normalize=0:dropout_transition=0:duration=first[amixb]")
    alast = "amixb"
if stage_rank >= 3:
    A = N["audio"]
    gain = job.read_json("audio", "voice-gain.json") if job.p("audio", "voice-gain.json").exists() else None
    if gain:
        fc.append(f"[acat]volume={gain['gain_db']:.2f}dB,alimiter=limit={10**(A['peak_dbfs']/20):.4f}:level=false[voice]")
    else:
        fc.append("[acat]anull[voice]")
    mix = ["[voice]"] + broll_audio
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
