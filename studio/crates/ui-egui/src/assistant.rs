//! Vibe Studio: the Assistant. The user's own coding agent (Claude Code) runs inside the editor,
//! the way the vibe-editor has always been used from a terminal, but with the edit in view.
//!
//! The host (the desktop app) starts `claude` in the vibe-editor checkout, so the agent has the
//! repository's `CLAUDE.md`, skills (ig-reel, ig-cut…), samples and permission settings, and the
//! user's own login. The host also hands the agent this app as an MCP server, so the agent can
//! read and change the open timeline as well as run the pipeline. This module holds the
//! conversation and turns Claude Code's stream-json output into [`ChatLine`]s. Permission prompts
//! and the agent's questions become cards the user answers in the panel, and every command that
//! reaches the app over the control channel goes in [`Assistant::activity`].
//!
//! No API key is involved: the agent is the user's Claude Code, signed in as they are in a
//! terminal.

use std::sync::Arc;
use std::sync::mpsc::{Receiver, Sender};

use serde_json::{Value, json};

use crate::FilmcraftApp;

/// Activity entries kept (oldest dropped first).
const MAX_ACTIVITY: usize = 500;
/// Lines of the conversation kept (oldest dropped first).
const MAX_LINES: usize = 2_000;

/// What the host needs to start the agent.
#[derive(Clone, Debug, Default)]
pub struct AgentLaunch {
    /// A path inside the vibe-editor checkout (the open project or job), used to find the
    /// repository the agent runs in; the host also looks from the working directory.
    pub near: Option<String>,
    /// Claude Code permission mode: `default` (ask), `acceptEdits`, `plan`.
    pub permission_mode: String,
    /// Continue this Claude Code session (`--resume`).
    pub resume: Option<String>,
    /// Continue the most recent session in the repository (`--continue`).
    pub continue_last: bool,
}

/// Input to a running agent, written to its stdin by the host.
#[derive(Clone, Debug)]
pub enum AgentInput {
    /// One stream-json line (a user message or a control response / request).
    Line(Value),
    /// End the agent process.
    Stop,
}

/// Output of a running agent, read by the host.
#[derive(Clone, Debug)]
pub enum AgentOutput {
    /// One stream-json line from Claude Code's stdout.
    Line(Value),
    /// A line of stderr worth showing.
    Stderr(String),
    /// The process ended.
    Exited(String),
}

/// A running agent process, as the host hands it over.
pub struct AgentProcess {
    pub output: Receiver<AgentOutput>,
    pub input: Sender<AgentInput>,
    /// Which agent and where it runs, for the panel header (`Claude Code · ~/vibe-editor`).
    pub label: String,
}

/// Starts the user's agent (native hosts only).
pub type AgentLauncher = Arc<dyn Fn(&AgentLaunch) -> Result<AgentProcess, String> + Send + Sync>;

/// Who ran a command shown in the Activity list.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    /// The agent in the Assistant panel or any other client of the control channel / MCP bridge.
    Agent,
}

impl Source {
    pub fn label(self) -> &'static str {
        match self {
            Source::Agent => "Agent",
        }
    }
}

/// One command that changed the project, as the Activity list shows it.
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

/// A permission prompt or question waiting for the user.
#[derive(Clone, Debug)]
pub struct Prompt {
    pub request_id: String,
    pub tool: String,
    /// What the agent wants to do, in a line or two.
    pub summary: String,
    pub input: Value,
    /// Claude Code's "always allow" rules for this call.
    pub suggestions: Value,
    /// For AskUserQuestion: the chosen option per question (by question index).
    pub picks: Vec<Option<String>>,
    /// Answered: true allowed, false denied.
    pub answered: Option<bool>,
}

impl Prompt {
    pub fn is_question(&self) -> bool {
        self.tool == "AskUserQuestion"
    }
    pub fn questions(&self) -> Vec<Value> {
        self.input.get("questions").and_then(Value::as_array).cloned().unwrap_or_default()
    }
}

/// A line of the visible conversation.
#[derive(Clone, Debug)]
pub enum ChatLine {
    User(String),
    Agent(String),
    /// A tool the agent ran: its id, label and outcome (None while it runs).
    Tool {
        id: String,
        label: String,
        ok: Option<bool>,
    },
    Prompt(Prompt),
    Note(String),
    Error(String),
}

/// The Assistant's state, kept on the app.
#[derive(Default)]
pub struct Assistant {
    pub lines: Vec<ChatLine>,
    pub activity: Vec<Activity>,
    pub input: String,
    /// Show the Activity tab instead of the conversation.
    pub show_activity: bool,
    /// Claude Code permission mode for new sessions: `default`, `acceptEdits` or `plan`.
    pub permission_mode: String,
    /// Continue the folder's most recent Claude Code session instead of starting a new one.
    pub continue_last: bool,
    /// The Claude Code session (from its `init`), resumed if the process has to be restarted.
    pub session_id: Option<String>,
    /// What the agent is doing now (Claude Code's task summaries), for the status line.
    pub status: String,
    /// Header label of the running agent.
    pub label: String,
    /// A turn is in progress (a message was sent and its result has not come back).
    pub busy: bool,
    process: Option<AgentProcess>,
    next_request: u64,
}

impl Assistant {
    pub fn busy(&self) -> bool {
        self.busy
    }

    pub fn running(&self) -> bool {
        self.process.is_some()
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

    fn push(&mut self, line: ChatLine) {
        self.lines.push(line);
        if self.lines.len() > MAX_LINES {
            let excess = self.lines.len() - MAX_LINES;
            self.lines.drain(..excess);
        }
    }

    fn write(&mut self, line: Value) {
        if let Some(p) = &self.process
            && p.input.send(AgentInput::Line(line)).is_err()
        {
            self.process = None;
            self.busy = false;
        }
    }

    fn request_id(&mut self) -> String {
        self.next_request = self.next_request.wrapping_add(1);
        format!("vibe-{}", self.next_request)
    }

    /// End the agent and start the next message in a new session.
    pub fn new_session(&mut self) {
        self.stop_process();
        self.session_id = None;
        self.lines.clear();
        self.status.clear();
    }

    fn stop_process(&mut self) {
        if let Some(p) = self.process.take() {
            let _ = p.input.send(AgentInput::Stop);
        }
        self.busy = false;
    }

    /// Interrupt the turn in progress (the session stays).
    pub fn interrupt(&mut self) {
        if !self.busy {
            return;
        }
        let id = self.request_id();
        self.write(json!({"type": "control_request", "request_id": id, "request": {"subtype": "interrupt"}}));
        self.push(ChatLine::Note("Interrupted.".into()));
    }

    /// Answer the permission prompt at `line`: allow (optionally always) or deny.
    pub fn answer(&mut self, line: usize, allow: bool, always: bool) {
        let Some(ChatLine::Prompt(p)) = self.lines.get_mut(line) else { return };
        if p.answered.is_some() {
            return;
        }
        p.answered = Some(allow);
        let response = if allow {
            let mut input = p.input.clone();
            if p.is_question()
                && let Some(o) = input.as_object_mut()
            {
                let answers: serde_json::Map<String, Value> =
                    p.questions().iter().zip(&p.picks).filter_map(|(q, pick)| Some((q.get("question")?.as_str()?.to_string(), json!(pick.clone()?)))).collect();
                o.insert("answers".into(), Value::Object(answers));
            }
            let mut r = json!({"behavior": "allow", "updatedInput": input});
            if always && let Some(rules) = p.suggestions.as_array().filter(|a| !a.is_empty()) {
                r["updatedPermissions"] = Value::Array(rules.clone());
            }
            r
        } else {
            json!({"behavior": "deny", "message": "The user declined this in Vibe Studio."})
        };
        let id = p.request_id.clone();
        self.write(json!({"type": "control_response", "response": {"subtype": "success", "request_id": id, "response": response}}));
    }

    /// Set the permission mode, also on the running session.
    pub fn set_permission_mode(&mut self, mode: &str) {
        self.permission_mode = mode.to_string();
        if self.process.is_some() {
            let id = self.request_id();
            self.write(json!({"type": "control_request", "request_id": id, "request": {"subtype": "set_permission_mode", "mode": mode}}));
        }
    }
}

/// Send the panel's input to the agent, starting it (or resuming its session) first.
pub fn send(app: &mut FilmcraftApp) {
    let text = app.assistant.input.trim().to_string();
    if text.is_empty() || app.assistant.busy {
        return;
    }
    if app.assistant.process.is_none() {
        let Some(launcher) = app.hooks.agent.clone() else {
            app.assistant.push(ChatLine::Error("This build can't start an agent: run the Vibe Studio desktop app.".into()));
            return;
        };
        let near = app.session.path.clone().or_else(|| app.session.project.items.values().find_map(media_path));
        let mode = if app.assistant.permission_mode.is_empty() { "default".to_string() } else { app.assistant.permission_mode.clone() };
        let launch = AgentLaunch { near, permission_mode: mode, resume: app.assistant.session_id.clone(), continue_last: app.assistant.continue_last };
        match launcher(&launch) {
            Ok(p) => {
                app.assistant.label = p.label.clone();
                app.assistant.process = Some(p);
            }
            Err(e) => {
                app.assistant.push(ChatLine::Error(e));
                return;
            }
        }
    }
    app.assistant.input.clear();
    app.assistant.push(ChatLine::User(text.clone()));
    let context = editor_context(app);
    let content = format!("{text}\n\n<vibe_studio_context>\n{context}\n</vibe_studio_context>");
    app.assistant.busy = true;
    app.assistant.status = "Thinking…".into();
    app.assistant.write(json!({"type": "user", "message": {"role": "user", "content": content}}));
}

fn media_path(item: &filmcraft_project::ProjectItem) -> Option<String> {
    match &item.kind {
        filmcraft_project::ItemKind::Media(m) => match &m.media {
            filmcraft_project::MediaRef::File { path } => Some(path.clone()),
            filmcraft_project::MediaRef::Generator(_) => None,
        },
        _ => None,
    }
}

/// Run on every frame: show what the agent said and did.
pub fn poll(app: &mut FilmcraftApp, ctx: &egui::Context) {
    let mut lines = vec![];
    let mut ended = None;
    if let Some(p) = &app.assistant.process {
        loop {
            match p.output.try_recv() {
                Ok(AgentOutput::Line(v)) => lines.push(v),
                Ok(AgentOutput::Stderr(s)) => app.assistant.lines.push(ChatLine::Note(s)),
                Ok(AgentOutput::Exited(why)) => {
                    ended = Some(why);
                    break;
                }
                Err(std::sync::mpsc::TryRecvError::Empty) => break,
                Err(std::sync::mpsc::TryRecvError::Disconnected) => {
                    ended = Some(String::new());
                    break;
                }
            }
        }
        ctx.request_repaint_after(std::time::Duration::from_millis(150));
    }
    let changed = !lines.is_empty() || ended.is_some();
    for v in &lines {
        apply(&mut app.assistant, v);
    }
    if let Some(why) = ended {
        app.assistant.process = None;
        if app.assistant.busy {
            app.assistant.busy = false;
            app.assistant.push(ChatLine::Error(if why.is_empty() { "The agent stopped.".into() } else { format!("The agent stopped: {why}") }));
        }
        app.assistant.status.clear();
    }
    if changed {
        ctx.request_repaint();
    }
}

/// Fold one line of Claude Code's stream-json output into the conversation.
pub fn apply(a: &mut Assistant, v: &Value) {
    match v.get("type").and_then(Value::as_str).unwrap_or("") {
        "system" => match v.get("subtype").and_then(Value::as_str).unwrap_or("") {
            "init" => {
                if let Some(id) = v.get("session_id").and_then(Value::as_str) {
                    a.session_id = Some(id.to_string());
                }
            }
            "task_summary" => {
                if let Some(d) = v.get("detail").and_then(Value::as_str) {
                    a.status = short(d, 120);
                }
            }
            _ => {}
        },
        "assistant" => {
            for b in blocks(v) {
                match b.get("type").and_then(Value::as_str).unwrap_or("") {
                    "text" => {
                        if let Some(t) = b.get("text").and_then(Value::as_str).map(str::trim).filter(|t| !t.is_empty()) {
                            a.push(ChatLine::Agent(t.to_string()));
                        }
                    }
                    "tool_use" => {
                        let id = b.get("id").and_then(Value::as_str).unwrap_or("").to_string();
                        let name = b.get("name").and_then(Value::as_str).unwrap_or("tool");
                        // loading deferred tool schemas is bookkeeping, not something the user needs to see
                        if name == "ToolSearch" {
                            continue;
                        }
                        let label = tool_label(name, b.get("input").unwrap_or(&Value::Null));
                        a.status = label.clone();
                        a.push(ChatLine::Tool { id, label, ok: None });
                    }
                    _ => {}
                }
            }
        }
        "user" => {
            for b in blocks(v) {
                if b.get("type").and_then(Value::as_str) == Some("tool_result")
                    && let Some(id) = b.get("tool_use_id").and_then(Value::as_str)
                {
                    let ok = !b.get("is_error").and_then(Value::as_bool).unwrap_or(false);
                    for line in a.lines.iter_mut().rev() {
                        if let ChatLine::Tool { id: tid, ok: o, .. } = line
                            && tid == id
                        {
                            *o = Some(ok);
                            break;
                        }
                    }
                }
            }
        }
        "control_request" => {
            let req = v.get("request").cloned().unwrap_or(Value::Null);
            if req.get("subtype").and_then(Value::as_str) == Some("can_use_tool") {
                let tool = req.get("tool_name").and_then(Value::as_str).unwrap_or("tool").to_string();
                let input = req.get("input").cloned().unwrap_or(json!({}));
                let summary = match req.get("description").and_then(Value::as_str).filter(|d| !d.is_empty()) {
                    Some(d) if tool != "AskUserQuestion" => format!("{}\n{}", tool_label(&tool, &input), d),
                    _ => tool_label(&tool, &input),
                };
                let n = input.get("questions").and_then(Value::as_array).map_or(0, Vec::len);
                a.status = format!("Waiting for you: {tool}");
                a.push(ChatLine::Prompt(Prompt {
                    request_id: v.get("request_id").and_then(Value::as_str).unwrap_or("").to_string(),
                    tool,
                    summary,
                    input,
                    suggestions: req.get("permission_suggestions").cloned().unwrap_or(Value::Null),
                    picks: vec![None; n],
                    answered: None,
                }));
            }
        }
        "result" => {
            a.busy = false;
            a.status.clear();
            let secs = v.get("duration_ms").and_then(Value::as_f64).map(|ms| ms / 1000.0);
            match v.get("subtype").and_then(Value::as_str) {
                Some("success") => {
                    if let Some(s) = secs.filter(|s| *s >= 1.0) {
                        a.push(ChatLine::Note(format!("Done in {}", duration(s))));
                    }
                }
                Some(other) => a.push(ChatLine::Error(format!("The turn ended early ({other}).").replace('_', " "))),
                None => {}
            }
        }
        _ => {}
    }
}

fn blocks(v: &Value) -> Vec<Value> {
    v.pointer("/message/content").and_then(Value::as_array).cloned().unwrap_or_default()
}

/// "12 s", "3 min 20 s".
fn duration(s: f64) -> String {
    if s < 60.0 { format!("{} s", s.round() as u64) } else { format!("{} min {} s", (s / 60.0) as u64, (s % 60.0).round() as u64) }
}

/// A one-line label for a tool call: what it touches, not its JSON.
pub fn tool_label(name: &str, input: &Value) -> String {
    let s = |k: &str| input.get(k).and_then(Value::as_str).unwrap_or("");
    let file = |k: &str| {
        let p = s(k);
        std::path::Path::new(p).file_name().map_or(p.to_string(), |n| n.to_string_lossy().into_owned())
    };
    let (verb, what) = match name {
        "Bash" => ("Run", short(s("command"), 140)),
        "Read" => ("Read", file("file_path")),
        "Edit" | "MultiEdit" => ("Edit", file("file_path")),
        "Write" => ("Write", file("file_path")),
        "Glob" | "Grep" => ("Search", short(s("pattern"), 80)),
        "Skill" => ("Skill", s("skill").to_string()),
        "Task" | "Agent" => ("Agent", short(s("description"), 80)),
        "WebSearch" => ("Search the web", short(s("query"), 80)),
        "WebFetch" => ("Fetch", short(s("url"), 80)),
        "AskUserQuestion" => ("Question", String::new()),
        "ExitPlanMode" => ("Plan ready", String::new()),
        "TodoWrite" => ("Update the to-do list", String::new()),
        other => {
            // the live app over MCP: mcp__vibe-studio__command_run {"id": …, "params": …}
            let tool = other.rsplit("__").next().unwrap_or(other);
            let id = input.get("id").and_then(Value::as_str);
            return match (tool, id) {
                ("command_run", Some(id)) => format!("Editor: {id} {}", short(&input.get("params").map(compact).unwrap_or_default(), 90)),
                (t, _) if other.starts_with("mcp__vibe-studio__") => format!("Editor: {}", t.replace('_', " ")),
                _ => format!("{other} {}", short(&compact(input), 90)),
            };
        }
    };
    if what.is_empty() { verb.to_string() } else { format!("{verb}: {what}") }
}

/// What the agent is told about the editor with each message: small and current.
fn editor_context(app: &FilmcraftApp) -> String {
    let s = &app.session;
    let mut lines = vec![format!("project: {} ({})", s.project.name, s.path.as_deref().unwrap_or("not saved yet"))];
    match s.state.active_sequence.and_then(|id| s.project.sequence(id).map(|q| (id, q))) {
        Some((id, q)) => {
            let fr = q.settings.frame_rate;
            let playhead = s.state.playheads.get(&id).copied().unwrap_or_default();
            let secs = playhead.0 as f64 / filmcraft_time::TICKS_PER_SECOND as f64;
            lines.push(format!(
                "open sequence: \"{}\" (item {}), {}x{} at {}/{} fps, playhead {secs:.2} s",
                s.project.item(id).map_or("", |i| i.name.as_str()),
                id.0,
                q.settings.width,
                q.settings.height,
                fr.num,
                fr.den
            ));
        }
        None => lines.push("no sequence is open".into()),
    }
    lines.push(format!("selected clips: {}", s.state.selection.len()));
    lines.join("\n")
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
    let s = s.trim();
    if s.chars().count() <= max {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max.saturating_sub(1)).collect();
    out.push('…');
    out
}

/// The conversation as JSON (`assistant.inspect` on the control channel).
pub fn inspect(a: &Assistant) -> Value {
    let lines: Vec<Value> = a
        .lines
        .iter()
        .enumerate()
        .map(|(i, l)| match l {
            ChatLine::User(s) => json!({"line": i, "kind": "user", "text": s}),
            ChatLine::Agent(s) => json!({"line": i, "kind": "agent", "text": s}),
            ChatLine::Tool { label, ok, .. } => json!({"line": i, "kind": "tool", "label": label, "ok": ok}),
            ChatLine::Prompt(p) => json!({"line": i, "kind": "prompt", "tool": p.tool, "summary": p.summary, "answered": p.answered}),
            ChatLine::Note(s) => json!({"line": i, "kind": "note", "text": s}),
            ChatLine::Error(s) => json!({"line": i, "kind": "error", "text": s}),
        })
        .collect();
    json!({"running": a.running(), "busy": a.busy, "session": a.session_id, "status": a.status, "agent": a.label, "lines": lines})
}

/// Whether a control-channel command goes in the Activity list: everything but the read-only
/// queries an agent polls (they would bury the edits).
pub fn worth_logging(command: &str) -> bool {
    !(command.ends_with(".inspect") || command.ends_with(".list") || command == "perf.stats")
}

/// The text Claude Code gets appended to its system prompt inside Vibe Studio.
pub const AGENT_CONTEXT: &str = "You are running inside Vibe Studio, the vibe-editor's own video editor, as its built-in agent. \
The user is watching the edit in the app and may edit by hand at the same time; they talk to you in its Assistant panel, \
and every permission prompt and question you raise appears there as buttons. Work exactly as you would in a terminal \
session in this repository: CLAUDE.md, the skills (ig-reel, ig-cut, ig-captions, ig-show, ig-sound, ig-pacing, \
ig-delivery) and samples/ decide the edit. \
The `vibe-studio` MCP server is the live app: `sequence_inspect` / `project_inspect` read the edit as it is now (including \
the user's hand edits), `render_frame` shows a frame, and `command_run` / `command_batch` change it with editor commands \
(each is one undo step the user sees in Assistant ▸ Activity). Captions are text clips on V5 \
(read and retype them with `graphics.list` / `graphics.setText`, restyle a word with `graphics.setCharStyle`). \
Before re-running a pipeline node on a job the user has edited here, run `vibe.diffJob {\"dir\": \"<job>\"}` and carry \
what they changed into the job's decision files (cuts.overrides.json, captions.overrides.json, graphics-plan.json) so \
the re-run keeps their edits. `vibe.importJob {\"dir\": \"<job folder>\"}` builds a \
sequence from a pipeline job's files: run it after the pipeline produced or changed a cut so the user sees it (it adds a \
new sequence and leaves their hand-edited one alone). For a precise change the user asks for on the timeline (trim this, \
move that caption, punch in here), change the timeline directly with commands rather than re-running the pipeline. \
Each message ends with <vibe_studio_context>, the app's state when the user sent it.";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn short_cuts_at_char_boundaries() {
        assert_eq!(short("héllo", 10), "héllo");
        assert_eq!(short("héllo wörld", 5), "héll…");
    }

    #[test]
    fn tool_labels_read_like_actions() {
        assert_eq!(tool_label("Bash", &json!({"command": "./run.sh projects/x --to rough_cut"})), "Run: ./run.sh projects/x --to rough_cut");
        assert_eq!(tool_label("Edit", &json!({"file_path": "/r/projects/x/cuts.overrides.json"})), "Edit: cuts.overrides.json");
        assert_eq!(tool_label("Skill", &json!({"skill": "ig-reel"})), "Skill: ig-reel");
        assert_eq!(
            tool_label("mcp__vibe-studio__command_run", &json!({"id": "timeline.razor", "params": {"seconds": 3}})),
            "Editor: timeline.razor {\"seconds\":3}"
        );
        assert_eq!(tool_label("mcp__vibe-studio__sequence_inspect", &json!({})), "Editor: sequence inspect");
    }

    /// The stream Claude Code wrote in a real run (trimmed): init, a Bash call, its permission
    /// prompt, the result, the answer, the end of the turn.
    #[test]
    fn a_turn_with_a_permission_prompt_folds_into_the_conversation() {
        let mut a = Assistant { busy: true, ..Default::default() };
        let stream = [
            json!({"type": "system", "subtype": "init", "session_id": "c849ab43"}),
            json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "touch vibe-probe.txt"}}]}}),
            json!({"type": "control_request", "request_id": "r1", "request": {"subtype": "can_use_tool", "tool_name": "Bash", "input": {"command": "touch vibe-probe.txt"}, "description": "Create empty probe file", "permission_suggestions": [{"type": "addRules", "rules": [{"toolName": "Bash", "ruleContent": "touch vibe-probe.txt"}], "behavior": "allow", "destination": "localSettings"}]}}),
            json!({"type": "system", "subtype": "task_summary", "detail": "Creating empty probe file"}),
            json!({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "", "is_error": false}]}}),
            json!({"type": "assistant", "message": {"content": [{"type": "text", "text": "DONE"}]}}),
            json!({"type": "result", "subtype": "success", "duration_ms": 2218, "session_id": "c849ab43"}),
        ];
        for v in &stream {
            apply(&mut a, v);
        }
        assert_eq!(a.session_id.as_deref(), Some("c849ab43"));
        assert!(!a.busy);
        assert!(matches!(&a.lines[0], ChatLine::Tool { label, ok: Some(true), .. } if label == "Run: touch vibe-probe.txt"));
        assert!(matches!(&a.lines[1], ChatLine::Prompt(p) if p.tool == "Bash" && p.summary.contains("Create empty probe file")));
        assert!(matches!(&a.lines[2], ChatLine::Agent(t) if t == "DONE"));
        assert!(matches!(&a.lines[3], ChatLine::Note(t) if t == "Done in 2 s"));
    }

    #[test]
    fn answering_writes_the_control_response_claude_code_expects() {
        let (tx, rx) = std::sync::mpsc::channel();
        let (_otx, orx) = std::sync::mpsc::channel();
        let mut a = Assistant { process: Some(AgentProcess { output: orx, input: tx, label: String::new() }), ..Default::default() };
        apply(
            &mut a,
            &json!({"type": "control_request", "request_id": "r1", "request": {"subtype": "can_use_tool", "tool_name": "Bash", "input": {"command": "ls"}, "permission_suggestions": [{"type": "addRules"}]}}),
        );
        a.answer(0, true, true);
        let Ok(AgentInput::Line(v)) = rx.try_recv() else { panic!("no response written") };
        assert_eq!(v["type"], "control_response");
        assert_eq!(v["response"]["request_id"], "r1");
        assert_eq!(v["response"]["response"]["behavior"], "allow");
        assert_eq!(v["response"]["response"]["updatedInput"]["command"], "ls");
        assert_eq!(v["response"]["response"]["updatedPermissions"][0]["type"], "addRules");
        // a second click does nothing
        a.answer(0, false, false);
        assert!(rx.try_recv().is_err());
    }

    #[test]
    fn a_question_is_answered_with_the_picked_options() {
        let (tx, rx) = std::sync::mpsc::channel();
        let (_otx, orx) = std::sync::mpsc::channel();
        let mut a = Assistant { process: Some(AgentProcess { output: orx, input: tx, label: String::new() }), ..Default::default() };
        let q =
            json!({"questions": [{"question": "Which take?", "header": "Take", "options": [{"label": "First"}, {"label": "Second"}], "multiSelect": false}]});
        apply(
            &mut a,
            &json!({"type": "control_request", "request_id": "q1", "request": {"subtype": "can_use_tool", "tool_name": "AskUserQuestion", "input": q}}),
        );
        if let Some(ChatLine::Prompt(p)) = a.lines.get_mut(0) {
            p.picks[0] = Some("Second".into());
        }
        a.answer(0, true, false);
        let Ok(AgentInput::Line(v)) = rx.try_recv() else { panic!("no response written") };
        assert_eq!(v["response"]["response"]["updatedInput"]["answers"]["Which take?"], "Second");
    }
}
