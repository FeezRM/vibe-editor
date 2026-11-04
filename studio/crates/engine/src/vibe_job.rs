//! Vibe Studio: open a vibe-editor pipeline job (`projects/<job>/`) as an editable sequence.
//!
//! The pipeline makes the editing decisions as files: `cuts.json` (the takes kept, zoom punches),
//! `preview/framing.json` (the camera), `captions.json` (+ `captions.overrides.json`),
//! `graphics-plan.json` (+ `renders/*.mov`), `sfx-plan.json` and `audio/voice-gain.json`.
//! `vibe.importJob` turns them into a timeline that every tool can edit:
//!
//! | file | becomes |
//! |---|---|
//! | `RUN.md` `source` | one media item, its transcript from `transcript/words.json` |
//! | `cuts.json` keep ranges | linked V1 + A1 clips back to back, each a whole number of frames |
//! | `framing.json` | Motion Scale and Position on every V1 clip (one fixed camera) |
//! | `keep.zoom` | eased Scale and Position keyframes anchored on the face |
//! | `captions.json` | a caption track `Captions` (text and times editable), styled from the look |
//! | `graphics-plan.json` renders | alpha clips on V3 (V4 when V3 is busy) at their cue |
//! | `sfx-plan.json` | clips on A3 at their cue and level; the music bed on A4 |
//! | `voice-gain.json` | clip gain on every A1 clip |
//!
//! Everything goes through the same commands as the menus, in one undo step. Times from the
//! pipeline (float seconds) are converted once here, snapped to the sequence's frame grid, and
//! clips are laid end to end by whole frames so the cut never drifts from the EDL.

use std::path::{Path, PathBuf};

use serde_json::{Map, Value, json};

use crate::commands::{CommandSpec, always, bad, str_p};
use crate::{EngineError, Result, Session};
use filmcraft_time::TICKS_PER_SECOND;

const CMD: &str = "vibe.importJob";
/// Largest pipeline JSON file read (they are a few hundred KB at most).
const MAX_JSON: u64 = 64 * 1024 * 1024;

pub fn commands() -> Vec<CommandSpec> {
    vec![CommandSpec {
        id: CMD,
        label: "Open Vibe Job…",
        menu: &["File"],
        shortcut: None,
        params: r#"{"dir":str (the job folder, projects/<job>),"name":str? (sequence name; default the job's slug),"captions":"track"|"render"|"none"="track" (track: editable captions; render: the pipeline's rendered captions .mov on V5),"transcript":bool=true}"#,
        enabled: always,
        run: import_job,
        journal: true,
    }]
}

fn ticks(seconds: f64) -> i64 {
    // pipeline times are a few minutes at most; clamp keeps the cast in range for hostile input
    (seconds.clamp(0.0, 86_400.0) * TICKS_PER_SECOND as f64).round() as i64
}

fn read_json(path: &Path) -> Result<Value> {
    use std::io::Read as _;
    let file = std::fs::File::open(path).map_err(|e| bad(CMD, format!("{}: {e}", path.display())))?;
    let mut bytes = Vec::new();
    file.take(MAX_JSON + 1).read_to_end(&mut bytes).map_err(|e| bad(CMD, format!("{}: {e}", path.display())))?;
    if bytes.len() as u64 > MAX_JSON {
        return Err(bad(CMD, format!("{} is too large", path.display())));
    }
    serde_json::from_slice(&bytes).map_err(|e| bad(CMD, format!("{}: {e}", path.display())))
}

fn read_opt(path: &Path, warnings: &mut Vec<String>) -> Option<Value> {
    if !path.is_file() {
        return None;
    }
    match read_json(path) {
        Ok(v) => Some(v),
        Err(e) => {
            warnings.push(e.to_string());
            None
        }
    }
}

/// RUN.md front matter: the top-level `key: value` lines between the `---` fences.
fn run_md(dir: &Path) -> Result<Map<String, Value>> {
    let text =
        std::fs::read_to_string(dir.join("RUN.md")).map_err(|e| bad(CMD, format!("no RUN.md in {} ({e}); is this a vibe job folder?", dir.display())))?;
    let body = text.strip_prefix("---\n").ok_or_else(|| bad(CMD, "RUN.md has no front matter"))?;
    let front = body.split("\n---").next().unwrap_or_default();
    let mut out = Map::new();
    for line in front.lines() {
        if line.starts_with([' ', '\t', '#']) {
            continue;
        }
        let Some((k, v)) = line.split_once(':') else { continue };
        let v = v.trim().trim_matches('"').trim_matches('\'');
        if v.is_empty() {
            continue;
        }
        let value = v.parse::<f64>().ok().filter(|f| f.is_finite()).map_or_else(|| json!(v), |f| json!(f));
        out.insert(k.trim().to_string(), value);
    }
    Ok(out)
}

fn merge(base: &mut Value, over: &Value) {
    match (base, over) {
        (Value::Object(b), Value::Object(o)) => {
            for (k, v) in o {
                merge(b.entry(k.clone()).or_insert(Value::Null), v);
            }
        }
        (b, o) => *b = o.clone(),
    }
}

/// The look's numbers: `presets/<preset>/numbers.json` with its `extends` chain, then the job's
/// own `numbers.json`. The presets folder is found above the job (the vibe-editor checkout).
fn numbers(dir: &Path, preset: &str, warnings: &mut Vec<String>) -> Value {
    let Some(presets) = dir.ancestors().take(8).map(|d| d.join("presets")).find(|p| p.is_dir()) else {
        warnings.push("no presets/ folder above the job: using 1080x1920 and the default caption look".into());
        return Value::Null;
    };
    let mut chain = vec![];
    let mut name = preset.to_string();
    for _ in 0..8 {
        let Some(v) = read_opt(&presets.join(&name).join("numbers.json"), warnings) else { break };
        let parent = v.get("extends").and_then(Value::as_str).map(str::to_string);
        chain.push(v);
        match parent {
            Some(p) if p != name => name = p,
            _ => break,
        }
    }
    let mut out = json!({});
    for v in chain.iter().rev() {
        merge(&mut out, v);
    }
    if let Some(own) = read_opt(&dir.join("numbers.json"), warnings) {
        merge(&mut out, &own);
    }
    out
}

fn f(v: &Value, k: &str) -> Option<f64> {
    v.get(k).and_then(Value::as_f64).filter(|x| x.is_finite())
}

fn import(s: &mut Session, path: &Path) -> Result<u64> {
    let r = s.execute("file.import", json!({"paths": [path.to_string_lossy()]}))?;
    r.pointer("/items/0").and_then(Value::as_u64).ok_or_else(|| {
        let why = r.pointer("/errors/0").map(|e| e.to_string()).unwrap_or_default();
        bad(CMD, format!("could not import {}{}", path.display(), if why.is_empty() { String::new() } else { format!(": {why}") }))
    })
}

/// Motion for a camera window: the clip scaled by `fit · z` with the source point `(left + 0.5/z,
/// top + 0.5/z)` (normalised) at the frame centre. The same model as the ffmpeg lane's zoompan.
#[derive(Clone, Copy, Debug, PartialEq)]
struct Camera {
    /// Clip scale for a cover fit of the source in the frame, in percent.
    fit: f64,
    /// Source size scaled by the cover fit, in sequence pixels.
    fw: f64,
    fh: f64,
    w: f64,
    h: f64,
}

impl Camera {
    fn motion(&self, z: f64, left: f64, top: f64) -> (f64, [f64; 2]) {
        let z = z.max(0.01);
        let cx = left + 0.5 / z;
        let cy = top + 0.5 / z;
        let x = self.w / 2.0 + (0.5 - cx) * self.fw * z;
        let y = self.h / 2.0 + (0.5 - cy) * self.fh * z;
        (self.fit * z, [x, y])
    }
    /// The window after zooming the base window (`s`, `left`, `top`) to `z` about point `p`, as
    /// the ffmpeg lane does: left' = p − (p − left)·s/z.
    fn about(&self, s: f64, left: f64, top: f64, z: f64, p: [f64; 2]) -> (f64, [f64; 2]) {
        let z = z.max(0.01);
        let l = p[0] - (p[0] - left) * s / z;
        let t = p[1] - (p[1] - top) * s / z;
        self.motion(z, l.clamp(0.0, (1.0 - 1.0 / z).max(0.0)), t.clamp(0.0, (1.0 - 1.0 / z).max(0.0)))
    }
}

fn set_motion(s: &mut Session, clip: u64, scale: f64, pos: [f64; 2], time: Option<i64>) -> Result<()> {
    let mut a = json!({"clip": clip, "effect": "motion", "param": "scale", "value": scale});
    let mut b = json!({"clip": clip, "effect": "motion", "param": "position", "value": pos});
    if let Some(t) = time {
        for p in [&mut a, &mut b] {
            p["time"] = json!(t);
            p["keyframe"] = json!(true);
        }
    }
    s.execute("effects.setParam", a)?;
    s.execute("effects.setParam", b)?;
    Ok(())
}

fn ease(s: &mut Session, clip: u64, media_time: i64, interpolation: &str) {
    for param in ["scale", "position"] {
        let _ = s.execute(
            "effects.setInterpolation",
            json!({"clip": clip, "effect": "motion", "param": param, "mediaTime": media_time, "interpolation": interpolation}),
        );
    }
}

fn caption_text(g: &Value, case: &str, accent_upper: bool) -> String {
    let accent = g.pointer("/accent/word").and_then(Value::as_str).map(str::to_lowercase);
    let keyword = g.get("keyword").is_some_and(|k| !k.is_null());
    let words: Vec<String> = g
        .get("words")
        .and_then(Value::as_array)
        .map(|ws| {
            ws.iter()
                .filter_map(|w| {
                    let t = w.get("w").and_then(Value::as_str)?;
                    let punct = w.get("end_punct").and_then(Value::as_str).unwrap_or("");
                    let mut word = match case {
                        "lower" => t.to_lowercase(),
                        "upper" => t.to_uppercase(),
                        _ => t.to_string(),
                    };
                    let is_accent = accent.as_deref().is_some_and(|a| t.to_lowercase() == a);
                    if keyword || (accent_upper && is_accent) {
                        word = word.to_uppercase();
                    }
                    if !word.ends_with(punct) {
                        word.push_str(punct);
                    }
                    Some(word)
                })
                .collect()
        })
        .unwrap_or_default();
    words.join(" ")
}

/// Everything read from the job folder before the sequence is built.
struct Job {
    dir: PathBuf,
    source: PathBuf,
    name: String,
    w: u64,
    h: u64,
    fps: f64,
    /// The look's numbers (preset chain + the job's own).
    n: Value,
    keeps: Vec<Value>,
    framing: Option<Value>,
    /// Caption mode (`track` / `render`) and captions.json.
    captions: Option<(String, Value)>,
    graphics: Option<Value>,
    sfx: Option<Value>,
    gain: Option<Value>,
    words: Option<Value>,
}

fn load(p: &Value, warnings: &mut Vec<String>) -> Result<Job> {
    let dir = PathBuf::from(str_p(p, "dir").ok_or_else(|| bad(CMD, "`dir` (the job folder) is required"))?);
    let dir = dir.canonicalize().map_err(|e| bad(CMD, format!("{}: {e}", dir.display())))?;
    let front = run_md(&dir)?;
    let source_rel = front.get("source").and_then(Value::as_str).ok_or_else(|| bad(CMD, "RUN.md names no `source`"))?;
    let source = dir.join(source_rel);
    if !source.is_file() {
        return Err(bad(CMD, format!("the job's source {} is missing", source.display())));
    }
    let slug = front
        .get("job")
        .or_else(|| front.get("slug"))
        .and_then(Value::as_str)
        .map(str::to_string)
        .or_else(|| dir.file_name().map(|n| n.to_string_lossy().into_owned()))
        .unwrap_or_else(|| "vibe job".into());
    let preset = front.get("preset").and_then(Value::as_str).unwrap_or("vertical/default").to_string();
    let n = numbers(&dir, &preset, warnings);
    let w = n.pointer("/canvas/width").and_then(Value::as_u64).unwrap_or(1080).clamp(16, 16_384);
    let h = n.pointer("/canvas/height").and_then(Value::as_u64).unwrap_or(1920).clamp(16, 16_384);
    let fps = front
        .get("fps")
        .and_then(Value::as_f64)
        .or_else(|| n.pointer("/canvas/fps").and_then(Value::as_f64))
        .filter(|f| *f > 1.0 && *f <= 240.0)
        .unwrap_or(30.0);
    let cuts = read_json(&dir.join("cuts.json"))?;
    let keeps = cuts.get("keep").and_then(Value::as_array).cloned().ok_or_else(|| bad(CMD, "cuts.json has no `keep` list"))?;
    if keeps.is_empty() {
        return Err(bad(CMD, "cuts.json keeps nothing"));
    }
    let captions = match str_p(p, "captions").unwrap_or("track") {
        "none" => None,
        mode => read_opt(&dir.join("captions.json"), warnings).map(|c| (mode.to_string(), c)),
    };
    let transcript = p.get("transcript").and_then(Value::as_bool).unwrap_or(true);
    Ok(Job {
        framing: read_opt(&dir.join("preview").join("framing.json"), warnings),
        graphics: read_opt(&dir.join("graphics-plan.json"), warnings),
        sfx: read_opt(&dir.join("sfx-plan.json"), warnings),
        gain: read_opt(&dir.join("audio").join("voice-gain.json"), warnings),
        words: if transcript { read_opt(&dir.join("transcript").join("words.json"), warnings) } else { None },
        name: str_p(p, "name").map(str::to_string).unwrap_or(slug),
        dir,
        source,
        w,
        h,
        fps,
        n,
        keeps,
        captions,
    })
}

fn import_job(s: &mut Session, p: &Value) -> Result<Value> {
    let mut warnings: Vec<String> = vec![];
    let job = load(p, &mut warnings)?;
    s.edit_group("Open Vibe Job", |s| build(s, &job, &mut warnings)).map_err(|e| match e {
        EngineError::BadParams { .. } => e,
        other => bad(CMD, other.to_string()),
    })
}

fn clip_ids(placed: &Value) -> Vec<u64> {
    placed.get("clips").and_then(Value::as_array).map(|a| a.iter().filter_map(Value::as_u64).collect()).unwrap_or_default()
}

fn set_gain(s: &mut Session, clips: &[u64], db: f64) -> Result<()> {
    if !clips.is_empty() {
        s.execute("clip.audioGain", json!({"clips": clips, "mode": "set", "db": db.clamp(-60.0, 24.0)}))?;
    }
    Ok(())
}

fn build(s: &mut Session, job: &Job, warnings: &mut Vec<String>) -> Result<Value> {
    let src = import(s, &job.source)?;
    let seq = s
        .execute("file.newSequence", json!({"name": job.name, "width": job.w, "height": job.h, "fps": job.fps, "video": 5, "audio": 4}))?
        .get("sequence")
        .and_then(Value::as_u64)
        .ok_or_else(|| bad(CMD, "no sequence was made"))?;
    let aroll = place_aroll(s, job, src, warnings)?;
    if let Some(db) = job.gain.as_ref().and_then(|g| f(g, "gain_db")).filter(|d| d.abs() > 0.01) {
        set_gain(s, &aroll.a1, db)?;
    }
    let (graphics, mut mute) = place_graphics(s, job, warnings)?;
    let captions = place_captions(s, job, aroll.frames, &mut mute, warnings)?;
    let sfx = place_sound(s, job, aroll.frames, warnings)?;
    set_transcript(s, job, src, warnings);
    Ok(json!({
        "sequence": seq,
        "source": src,
        "clips": aroll.v1.len(),
        "durationSeconds": aroll.frames as f64 / job.fps,
        "zoomPunches": aroll.punches,
        "captions": captions,
        "graphics": graphics,
        "sfx": sfx,
        "warnings": warnings,
    }))
}

struct Aroll {
    frames: i64,
    v1: Vec<u64>,
    a1: Vec<u64>,
    punches: usize,
}

/// The fixed camera of the whole video and its Motion values.
struct Framing {
    cam: Camera,
    s: f64,
    left: f64,
    top: f64,
    base: (f64, [f64; 2]),
    moves: bool,
}

fn framing(s: &Session, job: &Job, src: u64) -> Framing {
    // the source fills the frame (cover), then framing.json's fixed crop
    let (wf, hf) = (job.w as f64, job.h as f64);
    let (sw, sh) = s.project.source_size(filmcraft_project::ItemId(src)).map(|(a, b)| (f64::from(a), f64::from(b))).unwrap_or((wf, hf));
    let cover = (wf / sw.max(1.0)).max(hf / sh.max(1.0));
    let cam = Camera { fit: cover * 100.0, fw: sw * cover, fh: sh * cover, w: wf, h: hf };
    let fr = job.framing.clone().unwrap_or(json!({}));
    let scale = f(&fr, "scale").unwrap_or(1.0).max(1.0);
    let (left, top) = if scale > 1.0001 { (f(&fr, "left").unwrap_or(0.0), f(&fr, "top").unwrap_or(0.0)) } else { (0.0, 0.0) };
    let moves = (sw - cam.fw).abs() > 0.5 || (sh - cam.fh).abs() > 0.5 || scale > 1.0001;
    Framing { cam, s: scale, left, top, base: cam.motion(scale, left, top), moves }
}

/// A-roll: one linked V1/A1 clip per keep, whole frames, back to back.
fn place_aroll(s: &mut Session, job: &Job, src: u64, warnings: &mut Vec<String>) -> Result<Aroll> {
    let fr = framing(s, job, src);
    let mut out = Aroll { frames: 0, v1: vec![], a1: vec![], punches: 0 };
    for (i, k) in job.keeps.iter().enumerate() {
        let (Some(kin), Some(kout)) = (f(k, "in"), f(k, "out")) else {
            warnings.push(format!("keep {i} has no in/out; skipped"));
            continue;
        };
        let nf = ((kout - kin) * job.fps).round() as i64;
        if nf < 1 {
            continue;
        }
        let start = out.frames;
        let placed = s.execute(
            "timeline.place",
            json!({"item": src, "track": "V1", "audioTrack": "A1", "frame": start, "sourceIn": ticks(kin), "duration": {"frame": nf}}),
        )?;
        let clips = clip_ids(&placed);
        let Some(&vc) = clips.first() else { return Err(bad(CMD, format!("keep {i} was not placed"))) };
        out.v1.push(vc);
        out.a1.extend(clips.get(1).copied());
        if fr.moves {
            set_motion(s, vc, fr.base.0, fr.base.1, None)?;
        }
        if let Some(z) = k.get("zoom").filter(|z| z.is_object()) {
            punch(s, &fr, vc, k, z, kin, start as f64 / job.fps, job.fps)?;
            out.punches += 1;
        }
        out.frames += nf;
        if f(k, "hold").is_some_and(|h| h > 0.0) {
            warnings.push(format!("keep {i} has a frozen hold; it is not rebuilt yet (add a frame hold by hand)"));
        }
    }
    Ok(out)
}

/// A zoom punch on clip `vc`: base → punched about the face, eased (the opening move `out`:
/// punched → base). `kin` is the clip's source in, `tl_start` its timeline start (seconds).
#[allow(clippy::too_many_arguments)]
fn punch(s: &mut Session, fr: &Framing, vc: u64, k: &Value, z: &Value, kin: f64, tl_start: f64, fps: f64) -> Result<()> {
    let at = f(z, "at").unwrap_or(tl_start).max(tl_start);
    let pct = f(z, "pct").unwrap_or(8.0) / 100.0;
    let dur = f(z, "dur").unwrap_or(0.12).max(1.0 / fps);
    let face = z
        .get("face")
        .or_else(|| k.get("face"))
        .and_then(Value::as_array)
        .map(|a| [a.first().and_then(Value::as_f64).unwrap_or(0.5), a.get(1).and_then(Value::as_f64).unwrap_or(0.42)])
        .unwrap_or([0.5, 0.42]);
    let punched = fr.cam.about(fr.s, fr.left, fr.top, fr.s * (1.0 + pct), face);
    let out = z.get("out").and_then(Value::as_bool).unwrap_or(false);
    let (first, second) = if out { (punched, fr.base) } else { (fr.base, punched) };
    let (t0, t1) = (ticks(at), ticks(at + dur));
    set_motion(s, vc, first.0, first.1, Some(t0))?;
    set_motion(s, vc, second.0, second.1, Some(t1))?;
    let media = |t: i64| ticks(kin) + (t - ticks(tl_start));
    ease(s, vc, media(t0), "easeOut");
    ease(s, vc, media(t1), "easeIn");
    Ok(())
}

fn windows(v: Option<&Value>) -> Vec<(f64, f64)> {
    v.and_then(Value::as_array)
        .map(|a| a.iter().filter_map(|w| Some((w.get(0).and_then(Value::as_f64)?, w.get(1).and_then(Value::as_f64)?))).collect())
        .unwrap_or_default()
}

/// Graphics renders on V3 (V4 while V3 is busy). Returns how many, and the caption mute windows.
fn place_graphics(s: &mut Session, job: &Job, warnings: &mut Vec<String>) -> Result<(usize, Vec<(f64, f64)>)> {
    let Some(plan) = &job.graphics else { return Ok((0, vec![])) };
    let mut count = 0;
    let mut busy: Vec<(f64, f64)> = vec![];
    let mut mute = windows(plan.get("caption_mute_windows"));
    for g in plan.get("graphics").and_then(Value::as_array).cloned().unwrap_or_default() {
        let (Some(cue), Some(render)) = (f(&g, "cue"), g.get("render").and_then(Value::as_str)) else { continue };
        let path = job.dir.join(render);
        if !path.is_file() {
            warnings.push(format!("graphic {} has no render at {render}", g.get("id").and_then(Value::as_str).unwrap_or("?")));
            continue;
        }
        let item = import(s, &path)?;
        let len = f(&g, "duration").unwrap_or(2.0);
        let track = if busy.iter().any(|(a, b)| cue < *b && cue + len > *a) { "V4" } else { "V3" };
        if track == "V3" {
            busy.push((cue, cue + len));
        }
        let nf = ((len * job.fps).round() as i64).max(1);
        s.execute("timeline.place", json!({"item": item, "track": track, "frame": (cue * job.fps).round() as i64, "duration": {"frame": nf}, "audio": false}))?;
        if g.get("mute_captions").and_then(Value::as_bool).unwrap_or(false) {
            mute.push((cue, cue + len));
        }
        count += 1;
    }
    Ok((count, mute))
}

/// Captions: an editable caption track styled from the look, or the rendered captions .mov.
fn place_captions(s: &mut Session, job: &Job, frames: i64, mute: &mut Vec<(f64, f64)>, warnings: &mut Vec<String>) -> Result<usize> {
    let Some((mode, caps)) = &job.captions else { return Ok(0) };
    mute.extend(windows(caps.get("mute_windows")));
    if mode == "render" {
        let Some(path) = caps.get("render").and_then(Value::as_str).map(|r| job.dir.join(r)).filter(|p| p.is_file()) else {
            warnings.push("captions.json has no render yet; run build-captions".into());
            return Ok(0);
        };
        let item = import(s, &path)?;
        s.execute("timeline.place", json!({"item": item, "track": "V5", "frame": 0, "duration": {"frame": frames.max(1)}, "audio": false}))?;
        return Ok(1);
    }
    let c = job.n.get("captions").cloned().unwrap_or(json!({}));
    let case = c.get("case").and_then(Value::as_str).unwrap_or("as-is").to_string();
    let accent_upper = c.get("accent_case").and_then(Value::as_str) == Some("uppercase");
    s.execute("captions.newTrack", json!({"format": "Subtitle", "name": "Captions"}))?;
    let mut count = 0;
    for g in caps.get("groups").and_then(Value::as_array).cloned().unwrap_or_default() {
        let (Some(a), Some(b)) = (f(&g, "s"), f(&g, "e")) else { continue };
        let mid = (a + b) / 2.0;
        let text = caption_text(&g, &case, accent_upper);
        if text.is_empty() || mute.iter().any(|(x, y)| mid >= *x && mid < *y) {
            continue;
        }
        let fa = (a * job.fps).round();
        let fb = (b * job.fps).round().max(fa + 1.0);
        s.execute("captions.add", json!({"track": "C1", "text": text, "seconds": fa / job.fps, "durationSeconds": (fb - fa) / job.fps}))?;
        count += 1;
    }
    if let Err(e) = s.execute("captions.setStyle", caption_style(&c, job.h as f64)) {
        warnings.push(format!("caption style: {e}"));
    }
    Ok(count)
}

/// The caption track style for the look's numbers on a frame `h` pixels tall.
fn caption_style(c: &Value, h: f64) -> Value {
    let mut style = json!({"track": "C1", "anchor": "middle", "align": "center", "background": false});
    if let Some(font) = c.get("font_family").and_then(Value::as_str) {
        style["font"] = json!(font);
    }
    style["fontStyle"] = json!(match c.get("font_weight").and_then(Value::as_u64).unwrap_or(700) {
        0..=450 => "Regular",
        451..=550 => "Medium",
        551..=650 => "SemiBold",
        651..=750 => "Bold",
        _ => "ExtraBold",
    });
    // the look gives pixels of this frame; caption sizes are for a 1080-line frame
    if let Some(px) = f(c, "size_px") {
        style["size"] = json!(px * 1080.0 / h);
    }
    // the band where the look puts captions: below the middle, anchored at the bottom with a margin
    if let (Some(top), Some(bottom)) = (f(c, "band_top"), f(c, "band_bottom")) {
        let centre = (top + bottom) / 2.0 / h;
        if centre > 0.5 {
            style["anchor"] = json!("bottom");
            style["margin"] = json!((1.0 - centre - 0.5 * (bottom - top) / h).clamp(0.0, 0.45));
        }
    }
    if let Some(ink) = c.pointer("/colors/ink").and_then(Value::as_str) {
        style["color"] = json!(ink);
    }
    style
}

fn sound_file(dir: &Path, file: &str) -> Option<PathBuf> {
    [dir.join(file), PathBuf::from(file)].into_iter().find(|p| p.is_file()).or_else(|| dir.ancestors().take(6).map(|d| d.join(file)).find(|p| p.is_file()))
}

/// SFX on A3 at their cue and level; the music bed on A4 under the whole cut.
fn place_sound(s: &mut Session, job: &Job, frames: i64, warnings: &mut Vec<String>) -> Result<usize> {
    let Some(plan) = &job.sfx else { return Ok(0) };
    let mut count = 0;
    for e in plan.get("sfx").and_then(Value::as_array).cloned().unwrap_or_default() {
        let (Some(cue), Some(file)) = (f(&e, "cue"), e.get("file").and_then(Value::as_str)) else { continue };
        let Some(path) = sound_file(&job.dir, file) else {
            warnings.push(format!("sfx {file} not found"));
            continue;
        };
        let item = import(s, &path)?;
        let placed = s.execute("timeline.place", json!({"item": item, "track": "A3", "frame": (cue * job.fps).round() as i64, "video": false}))?;
        if let Some(db) = f(&e, "db") {
            set_gain(s, &clip_ids(&placed), db)?;
        }
        count += 1;
    }
    if let Some(m) = plan.get("music").filter(|m| m.is_object())
        && let Some(path) = m.get("file").and_then(Value::as_str).map(|f| job.dir.join(f)).filter(|p| p.is_file())
    {
        let item = import(s, &path)?;
        let placed = s.execute(
            "timeline.place",
            json!({"item": item, "track": "A4", "seconds": f(m, "onset_s").unwrap_or(0.0), "duration": {"frame": frames.max(1)}, "video": false}),
        )?;
        if let Some(db) = f(m, "db") {
            set_gain(s, &clip_ids(&placed), db)?;
        }
    }
    Ok(count)
}

/// The raw's transcript (media time), for text-based editing in the Text panel.
fn set_transcript(s: &mut Session, job: &Job, src: u64, warnings: &mut Vec<String>) {
    let Some(ws) = job.words.as_ref().and_then(|v| v.get("words").or(Some(v))).and_then(Value::as_array) else { return };
    let list: Vec<Value> = ws
        .iter()
        .filter_map(|w| {
            let text = w.get("w").or_else(|| w.get("word")).or_else(|| w.get("text")).and_then(Value::as_str)?;
            let a = f(w, "s").or_else(|| f(w, "start"))?;
            let b = f(w, "e").or_else(|| f(w, "end"))?;
            Some(json!({"text": text, "start": ticks(a), "end": ticks(b.max(a))}))
        })
        .collect();
    if !list.is_empty()
        && let Err(e) = s.execute("transcript.set", json!({"item": src, "transcript": {"language": "en", "speakers": [], "words": list}}))
    {
        warnings.push(format!("transcript: {e}"));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cam() -> Camera {
        Camera { fit: 50.0, fw: 1080.0, fh: 1920.0, w: 1080.0, h: 1920.0 }
    }

    #[test]
    fn an_uncropped_camera_centres_the_source() {
        let (s, p) = cam().motion(1.0, 0.0, 0.0);
        assert!((s - 50.0).abs() < 1e-9);
        assert!((p[0] - 540.0).abs() < 1e-9 && (p[1] - 960.0).abs() < 1e-9);
    }

    #[test]
    fn a_punch_keeps_the_face_where_it_was() {
        let c = cam();
        let face = [0.4, 0.3];
        let (s0, p0) = c.motion(1.0, 0.0, 0.0);
        let (s1, p1) = c.about(1.0, 0.0, 0.0, 1.1, face);
        // the face's screen position: pos + (face − 0.5)·size·scale/fit
        let screen = |s: f64, p: [f64; 2]| [p[0] + (face[0] - 0.5) * 1080.0 * s / 50.0, p[1] + (face[1] - 0.5) * 1920.0 * s / 50.0];
        let (a, b) = (screen(s0, p0), screen(s1, p1));
        assert!((a[0] - b[0]).abs() < 1e-6 && (a[1] - b[1]).abs() < 1e-6, "{a:?} {b:?}");
        assert!((s1 / s0 - 1.1).abs() < 1e-9);
    }

    #[test]
    fn caption_text_applies_case_and_accent() {
        let g = json!({"words": [{"w": "It's", "end_punct": ""}, {"w": "actually", "end_punct": ""}, {"w": "insane", "end_punct": "!"}], "accent": {"word": "insane", "cls": "hot"}});
        assert_eq!(caption_text(&g, "lower", true), "it's actually INSANE!");
        assert_eq!(caption_text(&g, "as-is", false), "It's actually insane!");
    }

    #[test]
    fn run_md_front_matter_reads_top_level_scalars() {
        let dir = std::env::temp_dir().join(format!("vibe-runmd-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("RUN.md"), "---\nslug: demo\nsource: raw/take.mov\nfps: 30\nnodes:\n  intake:\n    status: done\n---\n# notes\n").unwrap();
        let m = run_md(&dir).unwrap();
        assert_eq!(m["slug"], "demo");
        assert_eq!(m["source"], "raw/take.mov");
        assert_eq!(m["fps"], 30.0);
        assert!(!m.contains_key("status"));
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn hostile_params_are_errors_not_panics() {
        let mut s = Session::default();
        for p in [json!({}), json!({"dir": 3}), json!({"dir": "/nonexistent/vibe/job"})] {
            assert!(s.execute(CMD, p).is_err());
        }
    }
}
