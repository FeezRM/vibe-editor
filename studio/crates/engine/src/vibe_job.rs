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
    vec![
        CommandSpec {
            id: CMD,
            label: "Open Vibe Job…",
            menu: &["File"],
            shortcut: None,
            params: r#"{"dir":str (the job folder, projects/<job>),"name":str? (sequence name; default the job's slug),"captions":"styled"|"track"|"render"|"none"="styled" (styled: one text clip per caption on V5 in the look, accent words and keywords in its second face and colour; track: a plain caption track (SRT/VTT export); render: the pipeline's rendered captions .mov on V5),"transcript":bool=true}"#,
            enabled: always,
            run: import_job,
            journal: true,
        },
        CommandSpec {
            id: DIFF,
            label: "Compare with Vibe Job",
            menu: &[],
            shortcut: None,
            params: r#"{"dir":str (the job folder),"sequence":id? (default: the open sequence)} → the sequence in pipeline terms (keeps in source seconds, captions, graphics) and what differs from the job's files: takes trimmed / removed / added, captions retyped / retimed / removed / added, graphics moved / removed / added"#,
            enabled: always,
            run: diff_job,
            journal: false,
        },
        CommandSpec {
            id: "sequence.magnetic",
            label: "Magnetic Timeline",
            menu: &["Sequence"],
            shortcut: None,
            params: r#"{"on":bool? (default: toggle)} — a ripple edit trims captions, graphics and sounds that cross the stretch it closes instead of refusing (CapCut's main-track magnet)"#,
            enabled: crate::commands::has_seq,
            run: set_magnetic,
            journal: true,
        },
    ]
}

fn set_magnetic(s: &mut Session, p: &Value) -> Result<Value> {
    let now = s.active_sequence().is_some_and(|q| q.magnetic);
    let on = p.get("on").and_then(Value::as_bool).unwrap_or(!now);
    s.edit_sequence("Magnetic Timeline", |q, _, _| {
        q.magnetic = on;
        Ok(())
    })?;
    Ok(json!({"magnetic": on}))
}

const DIFF: &str = "vibe.diffJob";

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
    /// broll-plan.json: cutaways, windowed clips and hook titles.
    broll: Option<Value>,
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
    let captions = match str_p(p, "captions").unwrap_or("styled") {
        "none" => None,
        mode => read_opt(&dir.join("captions.json"), warnings).map(|c| (mode.to_string(), c)),
    };
    let transcript = p.get("transcript").and_then(Value::as_bool).unwrap_or(true);
    Ok(Job {
        framing: read_opt(&dir.join("preview").join("framing.json"), warnings),
        graphics: read_opt(&dir.join("graphics-plan.json"), warnings),
        broll: read_opt(&dir.join("broll-plan.json"), warnings),
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
    let (broll, titles) = place_broll(s, job, warnings)?;
    let (graphics, mut mute) = place_graphics(s, job, warnings)?;
    mute.extend(titles);
    let captions = place_captions(s, job, aroll.frames, &mut mute, warnings)?;
    let sfx = place_sound(s, job, aroll.frames, warnings)?;
    voice_limiter(s, job, warnings);
    set_transcript(s, job, src, warnings);
    // edits by hand: trimming or deleting a take carries the captions, graphics and sounds with it,
    // and the music bed stays one continuous piece
    set_magnetic(s, &json!({"on": true}))?;
    if let Err(e) = s.execute("timeline.setTrack", json!({"track": "A4", "syncLock": false})) {
        warnings.push(format!("music track: {e}"));
    }
    Ok(json!({
        "sequence": seq,
        "source": src,
        "clips": aroll.v1.len() - aroll.holds,
        "holds": aroll.holds,
        "broll": broll,
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
    holds: usize,
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
    let mut out = Aroll { frames: 0, v1: vec![], a1: vec![], punches: 0, holds: 0 };
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
        // the framing the keep ends on (a punch holds until the next cut)
        let mut last = fr.base;
        if let Some(z) = k.get("zoom").filter(|z| z.is_object()) {
            last = punch(s, &fr, vc, k, z, kin, start as f64 / job.fps, job.fps)?;
            out.punches += 1;
        }
        out.frames += nf;
        if let Some(hold) = f(k, "hold").filter(|h| *h > 0.0) {
            match place_hold(s, src, kin, kout, hold, out.frames, last, job.fps) {
                Ok(Some((hc, hf))) => {
                    out.v1.push(hc);
                    out.frames += hf;
                    out.holds += 1;
                }
                Ok(None) => {}
                Err(e) => warnings.push(format!("keep {i}: its frozen hold was not rebuilt ({e})")),
            }
        }
    }
    Ok(out)
}

/// A zoom punch on clip `vc`: base → punched about the face, eased (the opening move `out`:
/// punched → base). `kin` is the clip's source in, `tl_start` its timeline start (seconds).
#[allow(clippy::too_many_arguments)]
fn punch(s: &mut Session, fr: &Framing, vc: u64, k: &Value, z: &Value, kin: f64, tl_start: f64, fps: f64) -> Result<(f64, [f64; 2])> {
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
    Ok(second)
}

/// A frozen beat after a keep (`keep.hold`): its last frame held for `hold` seconds, video only
/// (the pipeline puts silence under it, or b-roll with its own sound), framed as the keep ended.
/// Returns the clip and its length in frames.
#[allow(clippy::too_many_arguments)]
fn place_hold(s: &mut Session, src: u64, kin: f64, kout: f64, hold: f64, frame: i64, motion: (f64, [f64; 2]), fps: f64) -> Result<Option<(u64, i64)>> {
    let hf = (hold * fps).round() as i64;
    if hf < 1 {
        return Ok(None);
    }
    let last = (kout - 1.0 / fps).max(kin);
    let placed =
        s.execute("timeline.place", json!({"item": src, "track": "V1", "frame": frame, "sourceIn": ticks(last), "duration": {"frame": hf}, "audio": false}))?;
    let Some(&hc) = clip_ids(&placed).first() else { return Ok(None) };
    s.execute("clip.frameHoldOptions", json!({"clips": [hc], "enabled": true, "holdOn": "in"}))?;
    set_motion(s, hc, motion.0, motion.1, None)?;
    Ok(Some((hc, hf)))
}

/// broll-plan.json: full-frame cutaways (filled to the frame, panned, sped) and windowed clips on
/// V2 (their own sound on A2), hook titles on V4. Returns how many, and the title windows (no
/// captions under them, as on the ffmpeg lane).
fn place_broll(s: &mut Session, job: &Job, warnings: &mut Vec<String>) -> Result<(usize, Vec<(f64, f64)>)> {
    let Some(plan) = &job.broll else { return Ok((0, vec![])) };
    let fps = job.fps;
    let mut count = 0;
    let mut titles = vec![];
    for c in plan.get("clips").and_then(Value::as_array).cloned().unwrap_or_default() {
        let (Some(start), Some(end)) = (f(&c, "start"), f(&c, "end")) else { continue };
        let nf = ((end - start) * fps).round() as i64;
        if nf < 1 {
            continue;
        }
        let id = c.get("id").and_then(Value::as_str).unwrap_or("?").to_string();
        if c.get("box").is_some_and(|b| !b.is_null()) || c.get("title").is_some_and(|t| !t.is_null()) {
            // a pre-rendered window (alpha, canvas-sized) with its own sound
            let Some(path) = c.get("render").and_then(Value::as_str).map(|r| job.dir.join(r)).filter(|p| p.is_file()) else {
                warnings.push(format!("b-roll {id} is not built yet (workflows/build-broll.py)"));
                continue;
            };
            let item = import(s, &path)?;
            let audio = c.get("render_audio").and_then(Value::as_bool).unwrap_or(false);
            let placed = s.execute(
                "timeline.place",
                json!({"item": item, "track": "V2", "audioTrack": "A2", "frame": (start * fps).round() as i64, "duration": {"frame": nf}, "audio": audio}),
            )?;
            if audio && let Some(db) = f(&c, "audio_db") {
                let ids = clip_ids(&placed);
                set_gain(s, ids.get(1..).unwrap_or_default(), db)?;
            }
            count += 1;
            continue;
        }
        let Some(file) = c.get("file").and_then(Value::as_str) else { continue };
        let path = if Path::new(file).is_absolute() { PathBuf::from(file) } else { job.dir.join(file) };
        if !path.is_file() {
            warnings.push(format!("b-roll {id}: {} is missing", path.display()));
            continue;
        }
        let item = import(s, &path)?;
        let speed = f(&c, "speed").filter(|v| *v > 0.01 && *v <= 100.0).unwrap_or(1.0);
        let src_frames = ((end - start) * speed * fps).round() as i64;
        let placed = s.execute(
            "timeline.place",
            json!({"item": item, "track": "V2", "frame": (start * fps).round() as i64, "sourceIn": ticks(f(&c, "src_in").unwrap_or(0.0)), "duration": {"frame": src_frames.max(1)}, "audio": false}),
        )?;
        let Some(&vc) = clip_ids(&placed).first() else { continue };
        if (speed - 1.0).abs() > 0.001 {
            s.execute("clip.speedDuration", json!({"clips": [vc], "speed": speed * 100.0, "ripple": false}))?;
        }
        // filled to the frame; `pan` 0 shows the source's left edge, 1 its right edge
        let (sw, sh) =
            s.project.source_size(filmcraft_project::ItemId(item)).map(|(a, b)| (f64::from(a), f64::from(b))).unwrap_or((job.w as f64, job.h as f64));
        let (wf, hf) = (job.w as f64, job.h as f64);
        let cover = (wf / sw.max(1.0)).max(hf / sh.max(1.0));
        let pan = f(&c, "pan").unwrap_or(0.5).clamp(0.0, 1.0);
        set_motion(s, vc, cover * 100.0, [wf / 2.0 + (0.5 - pan) * (sw * cover - wf), hf / 2.0], None)?;
        if f(&c, "crop_top").is_some_and(|t| t > 0.0) {
            warnings.push(format!("b-roll {id}: crop_top is not rebuilt; crop it with Effects ▸ Crop"));
        }
        count += 1;
    }
    for t in plan.get("titles").and_then(Value::as_array).cloned().unwrap_or_default() {
        let (Some(start), Some(end)) = (f(&t, "start"), f(&t, "end")) else { continue };
        let Some(path) = t.get("render").and_then(Value::as_str).map(|r| job.dir.join(r)).filter(|p| p.is_file()) else {
            warnings.push(format!("title {} is not built yet (workflows/build-broll.py)", t.get("id").and_then(Value::as_str).unwrap_or("?")));
            continue;
        };
        let item = import(s, &path)?;
        let nf = (((end - start) * fps).round() as i64).max(1);
        s.execute("timeline.place", json!({"item": item, "track": "V4", "frame": (start * fps).round() as i64, "duration": {"frame": nf}, "audio": false}))?;
        titles.push((start, end));
        count += 1;
    }
    Ok((count, titles))
}

/// The voice's true-peak ceiling, as the ffmpeg lane's `alimiter` (`audio.peak_dbfs`).
fn voice_limiter(s: &mut Session, job: &Job, warnings: &mut Vec<String>) {
    let Some(peak) = job.n.pointer("/audio/peak_dbfs").and_then(Value::as_f64).filter(|p| p.is_finite()) else { return };
    let r = s.execute("mixer.addInsert", json!({"strip": "A1", "effect": "hard_limiter"})).and_then(|v| {
        let slot = v.get("slot").and_then(Value::as_u64).unwrap_or(0);
        s.execute("mixer.setInsert", json!({"strip": "A1", "slot": slot, "params": {"max": peak.clamp(-30.0, 0.0)}}))
    });
    if let Err(e) = r {
        warnings.push(format!("voice limiter: {e}"));
    }
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
    if mode == "styled" {
        return place_captions_styled(s, job, caps, mute);
    }
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

/// A font style name for a CSS weight (and italic).
fn style_name(weight: u64, italic: bool) -> String {
    let w = match weight {
        0..=150 => "Thin",
        151..=250 => "ExtraLight",
        251..=350 => "Light",
        351..=450 => "Regular",
        451..=550 => "Medium",
        551..=650 => "SemiBold",
        651..=750 => "Bold",
        751..=850 => "ExtraBold",
        _ => "Black",
    };
    match (italic, w) {
        (true, "Regular") => "Italic".into(),
        (true, w) => format!("{w} Italic"),
        (false, w) => w.into(),
    }
}

/// One caption's text in the look: case, punctuation, keyword caps. Returns the text and the
/// character range of its accent word.
fn styled_text(g: &Value, c: &Value) -> (String, Option<std::ops::Range<usize>>) {
    let case = c.get("case").and_then(Value::as_str).unwrap_or("natural");
    let strip: Vec<char> = c.get("strip_punct").and_then(Value::as_str).unwrap_or("").chars().collect();
    let accent_upper = c.get("accent_case").and_then(Value::as_str) == Some("uppercase");
    let keyword = g.get("keyword").is_some_and(|k| !k.is_null());
    let accent = g.pointer("/accent/word").and_then(Value::as_str);
    let mut text = String::new();
    let mut range = None;
    for w in g.get("words").and_then(Value::as_array).cloned().unwrap_or_default() {
        let Some(t) = w.get("w").and_then(Value::as_str) else { continue };
        let punct: String = w.get("end_punct").and_then(Value::as_str).unwrap_or("").chars().filter(|ch| !strip.contains(ch)).collect();
        let base = t.trim_end_matches(|ch| strip.contains(&ch));
        let mut word = match case {
            "lower" => base.to_lowercase(),
            "upper" => base.to_uppercase(),
            _ => base.to_string(),
        };
        let is_accent = range.is_none() && accent == Some(t);
        if accent_upper && (keyword || is_accent) {
            word = word.to_uppercase();
        }
        if !word.ends_with(&punct) {
            word.push_str(&punct);
        }
        if !text.is_empty() {
            text.push(' ');
        }
        let at = text.chars().count();
        text.push_str(&word);
        if is_accent {
            range = Some(at..at + word.chars().count());
        }
    }
    (text, range)
}

/// Captions as the look draws them: one text clip per caption on V5, in the caption face and
/// size at the look's band, accent words and keyword groups in the accent face, scale and colour.
/// Each is ordinary text: retype it, restyle a word, move or trim the clip.
fn place_captions_styled(s: &mut Session, job: &Job, caps: &Value, mute: &[(f64, f64)]) -> Result<usize> {
    let c = job.n.get("captions").cloned().unwrap_or(json!({}));
    let (w, h, fps) = (job.w as f64, job.h as f64, job.fps);
    let size = f(&c, "size_px").unwrap_or(78.0);
    let hook_size = f(&c, "hook_size_px").unwrap_or(size);
    let scale = f(&c, "accent_scale").unwrap_or(1.0);
    let font = c.get("font_family").and_then(Value::as_str).unwrap_or("Inter").to_string();
    let font_style = style_name(c.get("font_weight").and_then(Value::as_u64).unwrap_or(700), false);
    let accent_font = c.get("accent_family").and_then(Value::as_str).unwrap_or(&font).to_string();
    let accent_style =
        style_name(c.get("accent_weight").and_then(Value::as_u64).unwrap_or(700), c.get("accent_style").and_then(Value::as_str) == Some("italic"));
    let ink = c.pointer("/colors/ink").and_then(Value::as_str).unwrap_or("#FFFFFF").to_string();
    let colour = |cls: &str| c.pointer(&format!("/colors/{cls}")).and_then(Value::as_str).unwrap_or(&ink).to_string();
    let band = (f(&c, "band_top").unwrap_or(h * 0.48) + f(&c, "band_bottom").unwrap_or(h * 0.59)) / 2.0;
    let max_w = f(&c, "max_width_frac").unwrap_or(0.78) * w;
    let tracking = f(&c, "tracking_em").unwrap_or(0.0) * 1000.0;
    let mut count = 0;
    for g in caps.get("groups").and_then(Value::as_array).cloned().unwrap_or_default() {
        let (Some(a), Some(b)) = (f(&g, "s"), f(&g, "e")) else { continue };
        let mid = (a + b) / 2.0;
        if mute.iter().any(|(x, y)| mid >= *x && mid < *y) {
            continue;
        }
        let (text, accent) = styled_text(&g, &c);
        if text.is_empty() {
            continue;
        }
        let keyword = g.get("keyword").and_then(Value::as_str).map(str::to_string);
        let mut px = if g.get("hook").and_then(Value::as_bool).unwrap_or(false) { hook_size } else { size };
        if keyword.is_some() {
            px *= scale;
        }
        // one line inside the look's width (an average glyph is about half an em wide)
        let est = text.chars().count() as f64 * px * 0.55;
        if est > max_w * 0.94 {
            px *= max_w * 0.94 / est;
        }
        let fa = (a * fps).round();
        let fb = (b * fps).round().max(fa + 1.0);
        let made = s.execute(
            "graphics.newText",
            json!({"text": text, "position": [w / 2.0, band + 0.36 * px], "size": px, "font": font, "fontStyle": font_style, "seconds": (fb - fa) / fps, "track": 4, "time": ticks(fa / fps)}),
        )?;
        let Some(clip) = made.get("clip").and_then(Value::as_u64) else { continue };
        s.execute("graphics.set", json!({"clip": clip, "props": {"align": "center", "fill_color": ink, "shadow": true, "tracking": tracking}}))?;
        let n = text.chars().count();
        let styled = match (&keyword, &accent) {
            (Some(k), _) => Some((0..n, json!({"font": accent_font, "fontStyle": accent_style, "size": px, "color": colour(k)}))),
            (None, Some(r)) => {
                let cls = g.pointer("/accent/cls").and_then(Value::as_str).unwrap_or("hot");
                Some((r.clone(), json!({"font": accent_font, "fontStyle": accent_style, "size": px * scale, "color": colour(cls)})))
            }
            _ => None,
        };
        if let Some((r, style)) = styled {
            s.execute("graphics.setCharStyle", json!({"clip": clip, "start": r.start, "end": r.end, "style": style}))?;
        }
        count += 1;
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
        // the bed starts with the cut, from `onset_s` into the track (the ffmpeg lane's -ss)
        let placed = s.execute(
            "timeline.place",
            json!({"item": item, "track": "A4", "frame": 0, "sourceIn": ticks(f(m, "onset_s").unwrap_or(0.0)), "duration": {"frame": frames.max(1)}, "video": false}),
        )?;
        let audio = job.n.get("audio").cloned().unwrap_or(json!({}));
        let bed = f(m, "db").or_else(|| f(&audio, "music_db")).unwrap_or(-18.0);
        let hook = f(m, "hook_db").or_else(|| f(&audio, "music_hook_db")).unwrap_or(bed);
        let hook_end = f(m, "hook_end_s").unwrap_or(0.0);
        for clip in clip_ids(&placed) {
            music_levels(s, clip, hook, bed, hook_end, job.fps)?;
        }
    }
    Ok(count)
}

/// The bed's level: `hook` dB under the hook (until `hook_end`), then `bed` dB, as keyframes on
/// the clip's Volume so the user can drag them.
fn music_levels(s: &mut Session, clip: u64, hook: f64, bed: f64, hook_end: f64, fps: f64) -> Result<()> {
    let level = |s: &mut Session, db: f64, t: Option<f64>| {
        let mut p = json!({"clip": clip, "effect": "volume", "param": "level", "value": db.clamp(-96.0, 15.0)});
        if let Some(t) = t {
            p["time"] = json!(ticks(t));
            p["keyframe"] = json!(true);
        }
        s.execute("effects.setParam", p).map(|_| ())
    };
    if hook_end * fps < 1.0 || (hook - bed).abs() < 0.01 {
        return level(s, bed, None);
    }
    level(s, hook, Some(0.0))?;
    level(s, hook, Some((hook_end - 1.0 / fps).max(0.0)))?;
    level(s, bed, Some(hook_end))
}

/// Seconds of a tick count.
fn secs(t: filmcraft_time::Tick) -> f64 {
    t.0 as f64 / TICKS_PER_SECOND as f64
}

fn round3(x: f64) -> f64 {
    (x * 1000.0).round() / 1000.0
}

/// The file a project item plays, if any.
fn item_file(s: &Session, id: filmcraft_project::ItemId) -> Option<PathBuf> {
    match &s.project.item(id)?.kind {
        filmcraft_project::ItemKind::Media(m) => match &m.media {
            filmcraft_project::MediaRef::File { path } => Some(PathBuf::from(path)),
            filmcraft_project::MediaRef::Generator(_) => None,
        },
        _ => None,
    }
}

fn same_file(a: &Path, b: &Path) -> bool {
    match (a.canonicalize(), b.canonicalize()) {
        (Ok(x), Ok(y)) => x == y,
        _ => a == b,
    }
}

/// Words compared loosely: case, punctuation and spacing don't count as an edit.
fn norm(t: &str) -> String {
    t.chars().filter(|c| c.is_alphanumeric() || c.is_whitespace()).collect::<String>().to_lowercase().split_whitespace().collect::<Vec<_>>().join(" ")
}

/// `vibe.diffJob`: what the user changed by hand, in the pipeline's terms, so an agent can carry it
/// into the job's decision files (cuts.overrides.json, captions.overrides.json, graphics-plan.json)
/// before it re-runs a node, instead of replacing the user's edit with a fresh import.
fn diff_job(s: &mut Session, p: &Value) -> Result<Value> {
    let mut warnings = vec![];
    let job = load(p, &mut warnings)?;
    let seq_id = p.get("sequence").and_then(Value::as_u64).map(filmcraft_project::ItemId).or(s.state.active_sequence).ok_or(EngineError::NoSequence)?;
    let q = s.project.sequence(seq_id).ok_or(EngineError::NoSequence)?.clone();
    let fps = job.fps;
    let tol = 1.5 / fps;

    // takes: V1 clips of the job's source (frame holds are holds)
    let mut keeps = vec![];
    let mut holds = vec![];
    for it in q.video_tracks.first().map(|t| t.items.clone()).unwrap_or_default() {
        if !item_file(s, it.item).is_some_and(|f| same_file(&f, &job.source)) {
            continue;
        }
        let start = secs(it.start);
        if it.frame_hold.is_some() {
            holds.push(json!({"at": round3(start), "seconds": round3(secs(it.duration))}));
            continue;
        }
        let a = secs(it.source_in);
        let b = a + secs(it.duration) * it.speed.abs().max(0.0);
        let zoom: Vec<Value> = it
            .effects
            .iter()
            .find(|e| e.effect == "motion")
            .and_then(|e| e.params.get("scale"))
            .map(|p| serde_json::to_value(p).unwrap_or(Value::Null))
            .into_iter()
            .collect();
        keeps.push(
            json!({"in": round3(a), "out": round3(b), "at": round3(start), "enabled": it.enabled, "scale": zoom.first().cloned().unwrap_or(Value::Null)}),
        );
    }
    let span = |v: &Value| (f(v, "in").unwrap_or(0.0), f(v, "out").unwrap_or(0.0));
    let overlaps = |a: (f64, f64), b: (f64, f64)| a.0 < b.1 - tol && b.0 < a.1 - tol;
    let mut cut = vec![];
    for (i, k) in job.keeps.iter().enumerate() {
        let want = span(k);
        let now: Vec<&Value> = keeps.iter().filter(|c| overlaps(want, span(c))).collect();
        match now.as_slice() {
            [] => cut.push(json!({"change": "removed", "keep": i, "in": want.0, "out": want.1})),
            [one] => {
                let got = span(one);
                if (got.0 - want.0).abs() > tol || (got.1 - want.1).abs() > tol {
                    cut.push(json!({"change": "trimmed", "keep": i, "was": [want.0, want.1], "now": [got.0, got.1]}));
                }
            }
            many => cut.push(
                json!({"change": "split", "keep": i, "was": [want.0, want.1], "now": many.iter().map(|c| json!([span(c).0, span(c).1])).collect::<Vec<_>>()}),
            ),
        }
    }
    for c in &keeps {
        if !job.keeps.iter().any(|k| overlaps(span(k), span(c))) {
            cut.push(json!({"change": "added", "in": c["in"], "out": c["out"], "at": c["at"]}));
        }
    }

    let (captions, caption_changes) = diff_captions(s, &job, &q, tol);
    let (graphics, graphic_changes) = diff_graphics(s, &job, &q, tol);
    let want_holds = job.keeps.iter().filter(|k| f(k, "hold").is_some_and(|h| h > 0.0)).count();
    if want_holds != holds.len() {
        cut.push(json!({"change": "holds", "was": want_holds, "now": holds.len()}));
    }
    let changed = !(cut.is_empty() && caption_changes.is_empty() && graphic_changes.is_empty());
    Ok(json!({
        "sequence": seq_id.0,
        "changed": changed,
        "cut": cut,
        "captions": caption_changes,
        "graphics": graphic_changes,
        "timeline": {"keeps": keeps, "holds": holds, "captions": captions, "graphics": graphics},
        "warnings": warnings,
    }))
}

fn diff_captions(s: &mut Session, job: &Job, q: &filmcraft_project::Sequence, tol: f64) -> (Vec<Value>, Vec<Value>) {
    // captions: text clips on V5 (styled) and caption tracks
    let mut captions = vec![];
    for it in q.video_tracks.get(4).map(|t| t.items.clone()).unwrap_or_default() {
        let listed = s.execute("graphics.list", json!({"clip": it.id.0})).unwrap_or(Value::Null);
        let text: Vec<String> = listed
            .get("layers")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter_map(|l| l.get("text").and_then(Value::as_str).map(str::to_string))
            .collect();
        if !text.is_empty() {
            captions.push(json!({"s": round3(secs(it.start)), "e": round3(secs(it.start) + secs(it.duration)), "text": text.join(" "), "enabled": it.enabled}));
        }
    }
    for t in &q.caption_tracks {
        for c in &t.captions {
            captions.push(json!({"s": round3(secs(c.start)), "e": round3(secs(c.start) + secs(c.duration)), "text": c.text, "enabled": t.enabled}));
        }
    }
    let mut caption_changes = vec![];
    if let Some((_, caps)) = &job.captions {
        let groups = caps.get("groups").and_then(Value::as_array).cloned().unwrap_or_default();
        let gspan = |g: &Value| (f(g, "s").unwrap_or(0.0), f(g, "e").unwrap_or(0.0));
        let cspan = |c: &Value| (f(c, "s").unwrap_or(0.0), f(c, "e").unwrap_or(0.0));
        let gtext = |g: &Value| {
            g.get("words")
                .and_then(Value::as_array)
                .map(|ws| ws.iter().filter_map(|w| w.get("w").and_then(Value::as_str)).collect::<Vec<_>>().join(" "))
                .unwrap_or_default()
        };
        // what the pipeline itself keeps off screen: under graphics that carry words, hook titles
        let mut muted = windows(caps.get("mute_windows"));
        if let Some(plan) = &job.graphics {
            muted.extend(windows(plan.get("caption_mute_windows")));
            for g in plan.get("graphics").and_then(Value::as_array).into_iter().flatten() {
                if g.get("mute_captions").and_then(Value::as_bool).unwrap_or(false)
                    && let (Some(c), Some(d)) = (f(g, "cue"), f(g, "duration"))
                {
                    muted.push((c, c + d));
                }
            }
        }
        for t in job.broll.as_ref().and_then(|b| b.get("titles")).and_then(Value::as_array).into_iter().flatten() {
            if let (Some(a), Some(b)) = (f(t, "start"), f(t, "end")) {
                muted.push((a, b));
            }
        }
        let shared = |x: (f64, f64), y: (f64, f64)| (x.1.min(y.1) - x.0.max(y.0)).max(0.0);
        for (i, g) in groups.iter().enumerate() {
            let (a, b) = gspan(g);
            if muted.iter().any(|(x, y)| (a + b) / 2.0 >= *x && (a + b) / 2.0 < *y) {
                continue;
            }
            // the clip sharing the most time with the group, if it shares at least half of either
            let best = captions.iter().map(|c| (shared((a, b), cspan(c)), c)).filter(|(t, _)| *t > 0.0).max_by(|x, y| x.0.total_cmp(&y.0));
            let found = best.filter(|(t, c)| *t >= 0.5 * (b - a).min(cspan(c).1 - cspan(c).0)).map(|(_, c)| c);
            let Some(c) = found else {
                caption_changes.push(json!({"change": "removed", "group": i, "text": gtext(g), "s": a, "e": b}));
                continue;
            };
            let now = c.get("text").and_then(Value::as_str).unwrap_or("");
            if norm(now) != norm(&gtext(g)) {
                caption_changes.push(json!({"change": "retyped", "group": i, "was": gtext(g), "now": now}));
            }
            let (ca, cb) = cspan(c);
            if (ca - a).abs() > tol || (cb - b).abs() > tol {
                caption_changes.push(json!({"change": "retimed", "group": i, "was": [a, b], "now": [ca, cb]}));
            }
        }
        for c in &captions {
            let (ca, cb) = cspan(c);
            if !groups.iter().any(|g| shared(gspan(g), (ca, cb)) >= 0.5 * (cb - ca).min(gspan(g).1 - gspan(g).0)) {
                caption_changes.push(json!({"change": "added", "text": c["text"], "s": c["s"], "e": c["e"]}));
            }
        }
    }

    (captions, caption_changes)
}

fn diff_graphics(s: &mut Session, job: &Job, q: &filmcraft_project::Sequence, tol: f64) -> (Vec<Value>, Vec<Value>) {
    // graphics: renders on V2–V4, matched to the plan by file
    let mut graphics = vec![];
    let mut graphic_changes = vec![];
    let plan: Vec<Value> = job.graphics.as_ref().and_then(|g| g.get("graphics")).and_then(Value::as_array).cloned().unwrap_or_default();
    let placed: Vec<(PathBuf, f64, f64)> = q
        .video_tracks
        .iter()
        .skip(1)
        .take(3)
        .flat_map(|t| t.items.clone())
        .filter_map(|it| item_file(s, it.item).map(|f| (f, secs(it.start), secs(it.duration))))
        .collect();
    for g in &plan {
        let id = g.get("id").and_then(Value::as_str).unwrap_or("?");
        let Some(render) = g.get("render").and_then(Value::as_str).map(|r| job.dir.join(r)) else { continue };
        let (cue, len) = (f(g, "cue").unwrap_or(0.0), f(g, "duration").unwrap_or(0.0));
        match placed.iter().find(|(f, ..)| same_file(f, &render)) {
            None => graphic_changes.push(json!({"change": "removed", "id": id})),
            Some((_, at, d)) => {
                graphics.push(json!({"id": id, "cue": round3(*at), "duration": round3(*d)}));
                if (at - cue).abs() > tol || (d - len).abs() > tol {
                    graphic_changes
                        .push(json!({"change": "moved", "id": id, "was": {"cue": cue, "duration": len}, "now": {"cue": round3(*at), "duration": round3(*d)}}));
                }
            }
        }
    }
    let known = |f: &Path| plan.iter().filter_map(|g| g.get("render").and_then(Value::as_str)).any(|r| same_file(f, &job.dir.join(r)));
    for (f, at, d) in &placed {
        let broll = job.broll.as_ref().map(|b| b.to_string()).unwrap_or_default();
        let name = f.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
        if !known(f) && !broll.contains(&name) {
            graphic_changes.push(json!({"change": "added", "file": f.display().to_string(), "cue": round3(*at), "duration": round3(*d)}));
        }
    }

    (graphics, graphic_changes)
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
    fn styled_text_follows_the_look() {
        let look = json!({"case": "natural", "strip_punct": ".,", "accent_case": "uppercase"});
        let g = json!({"words": [{"w": "It's", "end_punct": ""}, {"w": "actually", "end_punct": ""}, {"w": "insane.", "end_punct": "."}], "accent": {"word": "insane.", "cls": "hot"}});
        let (text, r) = styled_text(&g, &look);
        assert_eq!(text, "It's actually INSANE");
        assert_eq!(r, Some(14..20));
        let kw = json!({"words": [{"w": "use", "end_punct": ""}, {"w": "it", "end_punct": ""}], "keyword": "good"});
        assert_eq!(styled_text(&kw, &look).0, "USE IT");
        assert_eq!(style_name(900, true), "Black Italic");
        assert_eq!(style_name(400, true), "Italic");
        assert_eq!(style_name(700, false), "Bold");
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
