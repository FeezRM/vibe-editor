//! Vibe Studio: the Assistant. Ask Claude about the edit or ask it to change the edit, and watch
//! what it, or an outside agent on the control channel, does to the project.
//!
//! The conversation runs on a worker thread. Each request goes to the host's [`ClaudeTransport`];
//! the desktop app supplies it, so this crate holds no network code and stays web-portable. When
//! Claude asks for tools, the worker hands the calls to the UI thread. [`poll`] runs them there
//! through the same command path as a menu click, logs each one in [`Assistant::activity`], and
//! sends the results back. Every edit Claude makes is an ordinary undo step.
//!
//! The history the worker sends is append-only: assistant turns go back to the API unchanged,
//! thinking and fallback blocks included.

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{Receiver, Sender, channel};
#[cfg(test)]
use std::sync::{Mutex, PoisonError};

use serde_json::{Value, json};

use crate::FilmcraftApp;

/// Sends one Messages API request body and returns the decoded response body (or an error the
/// panel shows as-is). `key` is a key the user typed in the panel, used before the host's own
/// credentials. Supplied by the native host (`HostHooks::claude`).
pub type ClaudeTransport = Arc<dyn Fn(&Value, Option<&str>) -> Result<Value, String> + Send + Sync>;

/// The model the Assistant talks to.
pub const MODEL: &str = "claude-opus-5-5";
/// Most rounds of tool use in one turn before the Assistant stops and says so.
const MAX_ROUNDS: usize = 40;
/// Longest tool result sent back to the model, in characters.
const MAX_RESULT_CHARS: usize = 24_000;
/// Activity entries kept (oldest dropped first).
const MAX_ACTIVITY: usize = 500;

/// Who ran a command shown in the Activity list.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    /// The Assistant panel's Claude.
    Claude,
    /// An outside agent over the control channel or MCP bridge (Claude Code running the vibe pipeline, for example).
    Agent,
}

impl Source {
    pub fn label(self) -> &'static str {
        match self {
            Source::Claude => "Claude",
            Source::Agent => "Agent",
        }
    }
}

/// One command that changed or read the project, as the Activity list shows it.
#[derive(Clone, Debug)]
pub struct Activity {
    /// UI clock seconds when it ran.
    pub at: f64,
    pub source: Source,
    pub command: String,
    /// Parameters, compact JSON, shortened for display.
    pub params: String,
    pub ok: bool,
    /// The error, or a short form of the result.
    pub detail: String,
}

/// A line of the visible conversation.
#[derive(Clone, Debug)]
pub enum ChatLine {
    User(String),
    Claude(String),
    /// A tool Claude ran: label and whether it succeeded.
    Tool {
        label: String,
        ok: bool,
    },
    Note(String),
    Error(String),
}

/// One tool call Claude asked for.
#[derive(Clone, Debug)]
struct ToolCall {
    id: String,
    name: String,
    input: Value,
}

enum ToUi {
    Text(String),
    Tools(Vec<ToolCall>),
    Note(String),
    Error(String),
    /// The turn ended; the full API history to keep.
    Done(Vec<Value>),
}

struct Turn {
    rx: Receiver<ToUi>,
    results: Sender<Vec<Value>>,
    cancel: Arc<AtomicBool>,
}

/// The Assistant's state, kept on the app.
#[derive(Default)]
pub struct Assistant {
    pub lines: Vec<ChatLine>,
    pub activity: Vec<Activity>,
    pub input: String,
    /// A key typed into the panel (kept in memory only, never saved).
    pub key: String,
    /// Show the Activity tab instead of the conversation.
    pub show_activity: bool,
    history: Vec<Value>,
    turn: Option<Turn>,
}

impl Assistant {
    pub fn busy(&self) -> bool {
        self.turn.is_some()
    }

    /// Record a command in the Activity list.
    pub fn log(&mut self, at: f64, source: Source, command: &str, params: &Value, result: &Result<Value, String>) {
        let (ok, detail) = match result {
            Ok(v) => (true, short(&compact(v), 160)),
            Err(e) => (false, short(e, 240)),
        };
        self.activity.push(Activity { at, source, command: command.to_string(), params: short(&compact(params), 160), ok, detail });
        if self.activity.len() > MAX_ACTIVITY {
            let excess = self.activity.len() - MAX_ACTIVITY;
            self.activity.drain(..excess);
        }
    }

    /// Forget the conversation (the Activity list stays).
    pub fn clear(&mut self) {
        if let Some(t) = self.turn.take() {
            t.cancel.store(true, Ordering::Relaxed);
        }
        self.history.clear();
        self.lines.clear();
    }

    /// Stop the turn in progress. Calls already sent to the model are answered as cancelled.
    pub fn stop(&mut self) {
        if let Some(t) = &self.turn {
            t.cancel.store(true, Ordering::Relaxed);
        }
    }
}

/// Send the panel's input as a new user turn.
pub fn send(app: &mut FilmcraftApp) {
    let text = app.assistant.input.trim().to_string();
    if text.is_empty() || app.assistant.busy() {
        return;
    }
    let Some(transport) = app.hooks.claude.clone() else {
        app.assistant.lines.push(ChatLine::Error("The Assistant needs the desktop app: this build has no connection to Claude.".into()));
        return;
    };
    app.assistant.input.clear();
    app.assistant.lines.push(ChatLine::User(text.clone()));
    let context = editor_context(app);
    let mut history = app.assistant.history.clone();
    history.push(json!({"role": "user", "content": [
        {"type": "text", "text": format!("<editor_context>\n{context}\n</editor_context>")},
        {"type": "text", "text": text},
    ]}));
    let key = Some(app.assistant.key.trim().to_string()).filter(|k| !k.is_empty());
    let (to_ui, rx) = channel();
    let (results, results_rx) = channel();
    let cancel = Arc::new(AtomicBool::new(false));
    let flag = Arc::clone(&cancel);
    let spawned = std::thread::Builder::new().name("assistant".into()).spawn(move || {
        let tx = to_ui.clone();
        let run = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| worker(&transport, key.as_deref(), history, &to_ui, &results_rx, &flag)));
        if run.is_err() {
            let _ = tx.send(ToUi::Error("The Assistant stopped on an internal error.".into()));
        }
    });
    match spawned {
        Ok(_) => app.assistant.turn = Some(Turn { rx, results, cancel }),
        Err(e) => app.assistant.lines.push(ChatLine::Error(format!("Could not start the Assistant: {e}"))),
    }
}

/// Run on every frame: show what the worker said and run the tools it asked for.
pub fn poll(app: &mut FilmcraftApp, ctx: &egui::Context) {
    loop {
        let Some(turn) = &app.assistant.turn else { return };
        let msg = match turn.rx.try_recv() {
            Ok(m) => m,
            Err(std::sync::mpsc::TryRecvError::Empty) => {
                ctx.request_repaint_after(std::time::Duration::from_millis(100));
                return;
            }
            Err(std::sync::mpsc::TryRecvError::Disconnected) => {
                app.assistant.turn = None;
                return;
            }
        };
        match msg {
            ToUi::Text(t) => app.assistant.lines.push(ChatLine::Claude(t)),
            ToUi::Note(t) => app.assistant.lines.push(ChatLine::Note(t)),
            ToUi::Error(e) => app.assistant.lines.push(ChatLine::Error(e)),
            ToUi::Tools(calls) => {
                let cancelled = turn.cancel.load(Ordering::Relaxed);
                let mut out = Vec::with_capacity(calls.len());
                for c in calls {
                    let (content, ok) = if cancelled { (json!("Cancelled by the user."), false) } else { run_tool(app, ctx, &c) };
                    app.assistant.lines.push(ChatLine::Tool { label: tool_label(&c), ok });
                    out.push(json!({"type": "tool_result", "tool_use_id": c.id, "content": content, "is_error": !ok}));
                }
                if let Some(turn) = &app.assistant.turn {
                    let _ = turn.results.send(out);
                }
            }
            ToUi::Done(history) => {
                app.assistant.history = history;
                app.assistant.turn = None;
            }
        }
        ctx.request_repaint();
    }
}

fn worker(transport: &ClaudeTransport, key: Option<&str>, mut history: Vec<Value>, tx: &Sender<ToUi>, results: &Receiver<Vec<Value>>, cancel: &AtomicBool) {
    let finish = |history: Vec<Value>| {
        let _ = tx.send(ToUi::Done(history));
    };
    let start_len = history.len();
    for _ in 0..MAX_ROUNDS {
        if cancel.load(Ordering::Relaxed) {
            let _ = tx.send(ToUi::Note("Stopped.".into()));
            return finish(history);
        }
        let body = request_body(&history);
        let response = match transport(&body, key) {
            Ok(r) => r,
            Err(e) => {
                let _ = tx.send(ToUi::Error(e));
                // drop the unanswered user message so the next turn starts clean
                history.truncate(start_len.saturating_sub(1));
                return finish(history);
            }
        };
        let content = response.get("content").and_then(Value::as_array).cloned().unwrap_or_default();
        let stop = response.get("stop_reason").and_then(Value::as_str).unwrap_or("");
        history.push(json!({"role": "assistant", "content": content}));
        for block in &content {
            if block.get("type").and_then(Value::as_str) == Some("text")
                && let Some(t) = block.get("text").and_then(Value::as_str)
                && !t.trim().is_empty()
            {
                let _ = tx.send(ToUi::Text(t.trim().to_string()));
            }
        }
        match stop {
            "tool_use" => {
                let calls: Vec<ToolCall> = content
                    .iter()
                    .filter(|b| b.get("type").and_then(Value::as_str) == Some("tool_use"))
                    .map(|b| ToolCall {
                        id: b.get("id").and_then(Value::as_str).unwrap_or_default().to_string(),
                        name: b.get("name").and_then(Value::as_str).unwrap_or_default().to_string(),
                        input: b.get("input").cloned().unwrap_or(json!({})),
                    })
                    .collect();
                if calls.is_empty() {
                    return finish(history);
                }
                let ids: Vec<String> = calls.iter().map(|c| c.id.clone()).collect();
                if tx.send(ToUi::Tools(calls)).is_err() {
                    return;
                }
                // every tool_use needs its tool_result, even when the UI went away
                let out = results.recv().unwrap_or_else(|_| {
                    ids.iter().map(|id| json!({"type": "tool_result", "tool_use_id": id, "content": "The editor closed.", "is_error": true})).collect()
                });
                history.push(json!({"role": "user", "content": out}));
            }
            "refusal" => {
                let _ = tx.send(ToUi::Error("Claude declined this request.".into()));
                return finish(history);
            }
            "max_tokens" => {
                let _ = tx.send(ToUi::Note("The answer hit the length limit.".into()));
                return finish(history);
            }
            _ => return finish(history),
        }
    }
    let _ = tx.send(ToUi::Note(format!("Stopped after {MAX_ROUNDS} rounds of edits. Say \"continue\" to go on.")));
    finish(history);
}

fn request_body(history: &[Value]) -> Value {
    json!({
        "model": MODEL,
        "max_tokens": 16000,
        "output_config": {"effort": "medium"},
        "fallbacks": "default",
        "cache_control": {"type": "ephemeral"},
        "system": [{"type": "text", "text": SYSTEM}],
        "tools": tools(),
        "messages": history,
    })
}

const SYSTEM: &str = "You are the editing assistant inside Vibe Studio, a non-linear video editor for short-form vertical reels (Premiere-style timeline: V1 A-roll, V2 b-roll, V3+ graphics, caption tracks, A1 voice, A3 SFX, A4 music). \
The user is editing by hand and asks you questions or asks for changes. \
Every action in the editor is a command with an id and JSON params; you act only through the tools. \
Before changing anything, look: `inspect` the sequence (and `look` at the frame when the picture matters). Find the right command with `list_commands` and read its params before running it. \
Make the smallest change that does what was asked, then check it (inspect again). Each command you run is one undo step the user can take back. \
Times in params can be given as `seconds`, `frame`, `timecode` or `time` (ticks, 254016000000 per second). \
Never invent media, numbers or text the user did not give you. If a request is ambiguous or would remove a lot of work, say what you would do and ask first. \
Answer briefly, in plain sentences: what you did, and anything the user should check.";

fn tools() -> Value {
    json!([
        {
            "name": "inspect",
            "description": "Read the editor's state. `sequence`: tracks, clips (ids, start, duration, source in, effects), markers, playhead. `project`: bins and media items. `state`: selection, playhead, targeting, active sequence. `transcript`: the open sequence's words with times. `history`: the undo stack.",
            "input_schema": {"type": "object", "properties": {"what": {"type": "string", "enum": ["sequence", "project", "state", "transcript", "history"]}}, "required": ["what"]}
        },
        {
            "name": "list_commands",
            "description": "List editor commands whose id or label contains `filter` (e.g. \"razor\", \"timeline.\", \"keyframe\", \"caption\", \"export\"), with their parameter docs and whether they are enabled now.",
            "input_schema": {"type": "object", "properties": {"filter": {"type": "string"}}, "required": ["filter"]}
        },
        {
            "name": "run_command",
            "description": "Run one editor command by id with its JSON params, exactly as a menu click or shortcut would. Returns the command's result or its error.",
            "input_schema": {"type": "object", "properties": {"command": {"type": "string"}, "params": {"type": "object"}}, "required": ["command", "params"]}
        },
        {
            "name": "look",
            "description": "See the Program monitor: renders the sequence frame at `seconds` (default: the playhead) and returns it as an image.",
            "input_schema": {"type": "object", "properties": {"seconds": {"type": "number"}}}
        }
    ])
}

/// Run one tool call on the UI thread. Returns the tool_result content and whether it succeeded.
fn run_tool(app: &mut FilmcraftApp, ctx: &egui::Context, c: &ToolCall) -> (Value, bool) {
    let at = app.ui_clock;
    match c.name.as_str() {
        "inspect" => {
            let what = c.input.get("what").and_then(Value::as_str).unwrap_or("sequence");
            let id = match what {
                "project" => "project.inspect",
                "state" => "state.inspect",
                "transcript" => "transcript.inspect",
                "history" => "history.list",
                _ => "sequence.inspect",
            };
            text_result(app.session.execute(id, json!({})).map_err(|e| e.to_string()))
        }
        "list_commands" => {
            let filter = c.input.get("filter").and_then(Value::as_str).unwrap_or("").to_lowercase();
            let all = app.session.execute("command.list", json!({})).map_err(|e| e.to_string());
            text_result(all.map(|v| {
                let found: Vec<Value> = v
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter(|c| {
                                let id = c.get("id").and_then(Value::as_str).unwrap_or("").to_lowercase();
                                let label = c.get("label").and_then(Value::as_str).unwrap_or("").to_lowercase();
                                filter.is_empty() || id.contains(&filter) || label.contains(&filter)
                            })
                            .take(120)
                            .map(|c| json!({"id": c["id"], "label": c["label"], "params": c["params"], "enabled": c["enabled"]}))
                            .collect()
                    })
                    .unwrap_or_default();
                Value::Array(found)
            }))
        }
        "run_command" => {
            let Some(id) = c.input.get("command").and_then(Value::as_str) else { return (json!("missing `command`"), false) };
            let params = c.input.get("params").cloned().filter(Value::is_object).unwrap_or(json!({}));
            let r = crate::menus::invoke_command(app, ctx, id, params.clone());
            app.assistant.log(at, Source::Claude, id, &params, &r);
            text_result(r)
        }
        "look" => look(app, c.input.get("seconds").and_then(Value::as_f64)),
        other => (json!(format!("unknown tool `{other}`")), false),
    }
}

fn text_result(r: Result<Value, String>) -> (Value, bool) {
    match r {
        Ok(v) => (json!(short(&compact(&v), MAX_RESULT_CHARS)), true),
        Err(e) => (json!(e), false),
    }
}

/// Render the Program frame to a temporary PNG, scale it to at most 960 px tall and return it as
/// an image block.
fn look(app: &mut FilmcraftApp, seconds: Option<f64>) -> (Value, bool) {
    let path = std::env::temp_dir().join(format!("vibe-studio-look-{}.png", std::process::id()));
    let mut params = json!({"target": "program", "path": path.to_string_lossy()});
    // the command takes integer ticks; a day is far past any reel and keeps the cast in range
    if let Some(s) = seconds.filter(|s| s.is_finite() && (0.0..=86_400.0).contains(s)) {
        params["time"] = json!((s * filmcraft_time::TICKS_PER_SECOND as f64).round() as i64);
    }
    let rendered = app.session.execute("file.exportFrame", params).map_err(|e| e.to_string());
    let png = rendered.and_then(|_| std::fs::read(&path).map_err(|e| e.to_string())).and_then(|bytes| {
        let img = image::load_from_memory_with_format(&bytes, image::ImageFormat::Png).map_err(|e| e.to_string())?;
        let img = if img.height() > 960 { img.resize(960, 960, image::imageops::FilterType::Triangle) } else { img };
        let mut out = std::io::Cursor::new(Vec::new());
        img.write_to(&mut out, image::ImageFormat::Png).map_err(|e| e.to_string())?;
        Ok(out.into_inner())
    });
    let _ = std::fs::remove_file(&path);
    match png {
        Ok(bytes) => (json!([{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64(&bytes)}}]), true),
        Err(e) => (json!(format!("could not render the frame: {e}")), false),
    }
}

/// What the model is told about the editor with each message: small and current.
fn editor_context(app: &FilmcraftApp) -> String {
    let s = &app.session;
    let mut lines = vec![format!("project: {}", s.project.name)];
    match s.state.active_sequence.and_then(|id| s.project.sequence(id).map(|q| (id, q))) {
        Some((id, q)) => {
            lines.push(format!("open sequence: item {}", id.0));
            let fr = q.settings.frame_rate;
            lines.push(format!("frame size: {}x{} at {}/{} fps", q.settings.width, q.settings.height, fr.num, fr.den));
            lines.push(format!("tracks: {} video, {} audio", q.video_tracks.len(), q.audio_tracks.len()));
        }
        None => lines.push("no sequence is open".into()),
    }
    lines.push(format!("selected clips: {}", s.state.selection.len()));
    lines.join("\n")
}

fn tool_label(c: &ToolCall) -> String {
    match c.name.as_str() {
        "run_command" => {
            let id = c.input.get("command").and_then(Value::as_str).unwrap_or("?");
            let params = c.input.get("params").map(compact).unwrap_or_default();
            format!("{id} {}", short(&params, 90))
        }
        "inspect" => format!("inspect {}", c.input.get("what").and_then(Value::as_str).unwrap_or("sequence")),
        "list_commands" => format!("list commands \"{}\"", c.input.get("filter").and_then(Value::as_str).unwrap_or("")),
        "look" => "look at the frame".into(),
        other => other.to_string(),
    }
}

fn compact(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Null => String::new(),
        other => serde_json::to_string(other).unwrap_or_default(),
    }
}

/// At most `max` characters, with an ellipsis when cut (cut at a char boundary).
pub fn short(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max.saturating_sub(1)).collect();
    out.push('…');
    out
}

/// Standard base64 (RFC 4648, padded).
fn base64(bytes: &[u8]) -> String {
    const T: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut out = String::with_capacity(bytes.len().div_ceil(3) * 4);
    for chunk in bytes.chunks(3) {
        let b = [chunk.first().copied().unwrap_or(0), chunk.get(1).copied().unwrap_or(0), chunk.get(2).copied().unwrap_or(0)];
        let n = (u32::from(b[0]) << 16) | (u32::from(b[1]) << 8) | u32::from(b[2]);
        let idx = |shift: u32| T.get(((n >> shift) & 63) as usize).copied().map(char::from).unwrap_or('A');
        out.push(idx(18));
        out.push(idx(12));
        out.push(if chunk.len() > 1 { idx(6) } else { '=' });
        out.push(if chunk.len() > 2 { idx(0) } else { '=' });
    }
    out
}

/// Whether a control-channel command goes in the Activity list: everything but the read-only
/// queries an agent polls (they would bury the edits).
pub fn worth_logging(command: &str) -> bool {
    !(command.ends_with(".inspect") || command.ends_with(".list") || command == "perf.stats")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn base64_matches_rfc4648_vectors() {
        assert_eq!(base64(b""), "");
        assert_eq!(base64(b"f"), "Zg==");
        assert_eq!(base64(b"fo"), "Zm8=");
        assert_eq!(base64(b"foo"), "Zm9v");
        assert_eq!(base64(b"foobar"), "Zm9vYmFy");
    }

    #[test]
    fn short_cuts_at_char_boundaries() {
        assert_eq!(short("héllo", 10), "héllo");
        assert_eq!(short("héllo wörld", 5), "héll…");
    }

    #[test]
    fn request_body_has_model_tools_and_history() {
        let h = vec![json!({"role": "user", "content": "hi"})];
        let b = request_body(&h);
        assert_eq!(b["model"], MODEL);
        assert_eq!(b["messages"], json!(h));
        assert_eq!(b["tools"].as_array().map(Vec::len), Some(4));
    }

    #[test]
    fn worker_runs_tools_and_keeps_history_append_only() {
        // a fake Claude: first asks for one tool, then answers
        let calls = Arc::new(Mutex::new(0));
        let n = Arc::clone(&calls);
        let transport: ClaudeTransport = Arc::new(move |body: &Value, _key: Option<&str>| {
            let mut n = n.lock().unwrap_or_else(PoisonError::into_inner);
            *n += 1;
            if *n == 1 {
                Ok(json!({"stop_reason": "tool_use", "content": [
                    {"type": "thinking", "thinking": "", "signature": "s"},
                    {"type": "tool_use", "id": "t1", "name": "inspect", "input": {"what": "sequence"}}
                ]}))
            } else {
                // the tool result came back after the unchanged assistant turn
                let msgs = body["messages"].as_array().cloned().unwrap_or_default();
                assert_eq!(msgs[1]["content"][0]["type"], "thinking");
                assert_eq!(msgs[2]["content"][0]["tool_use_id"], "t1");
                Ok(json!({"stop_reason": "end_turn", "content": [{"type": "text", "text": "Done."}]}))
            }
        });
        let (tx, rx) = channel();
        let (rtx, rrx) = channel();
        let cancel = AtomicBool::new(false);
        let history = vec![json!({"role": "user", "content": "hi"})];
        let h = std::thread::spawn(move || worker(&transport, None, history, &tx, &rrx, &cancel));
        let mut done = None;
        while let Ok(m) = rx.recv() {
            match m {
                ToUi::Tools(c) => {
                    assert_eq!(c[0].name, "inspect");
                    rtx.send(vec![json!({"type": "tool_result", "tool_use_id": "t1", "content": "{}"})]).unwrap();
                }
                ToUi::Done(h) => done = Some(h),
                _ => {}
            }
        }
        h.join().unwrap();
        let done = done.unwrap();
        assert_eq!(done.len(), 4);
        assert_eq!(*calls.lock().unwrap(), 2);
    }
}
