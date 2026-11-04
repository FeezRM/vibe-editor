//! Vibe Studio's host pieces: the brand accent, where the app keeps its data, and the Assistant's
//! agent, the user's own Claude Code, run in the vibe-editor checkout and connected to this app.

use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::mpsc::channel;
use std::sync::{Arc, Mutex, PoisonError};

use filmcraft_ui_egui::assistant::{AGENT_CONTEXT, AgentInput, AgentLaunch, AgentLauncher, AgentOutput, AgentProcess};
use serde_json::{Value, json};

/// The app's name in windows, dialogs and the data folder.
pub const APP_NAME: &str = "Vibe Studio";

/// Set the theme's accent to the creator's brand colour (`brand/brand.json` `palette.accent`).
/// The file is found from `VIBE_BRAND` (a path to brand.json), else in a `brand/` folder of the
/// current directory or the executable's folder or any of their parents (the vibe-editor checkout).
/// Without one, the theme keeps the brand default.
pub fn apply_brand() {
    let Some(path) = brand_file() else {
        log::info!("brand: no brand/brand.json found; using the default accent");
        return;
    };
    match std::fs::read(&path).ok().and_then(|b| serde_json::from_slice::<Value>(&b).ok()) {
        Some(v) => match v.pointer("/palette/accent").and_then(Value::as_str).and_then(filmcraft_ui_egui::theme::parse_hex) {
            Some(rgb) => {
                filmcraft_ui_egui::theme::set_brand_accent(rgb);
                log::info!("brand: accent from {}", path.display());
            }
            None => log::warn!("brand: {} has no valid palette.accent", path.display()),
        },
        None => log::warn!("brand: could not read {}", path.display()),
    }
}

fn brand_file() -> Option<PathBuf> {
    if let Some(p) = std::env::var_os("VIBE_BRAND").map(PathBuf::from).filter(|p| p.is_file()) {
        return Some(p);
    }
    starts().into_iter().find_map(|start| start.ancestors().take(12).map(|d| d.join("brand").join("brand.json")).find(|p| p.is_file()))
}

fn starts() -> Vec<PathBuf> {
    [std::env::current_dir().ok(), std::env::current_exe().ok().and_then(|e| e.parent().map(Path::to_path_buf))].into_iter().flatten().collect()
}

/// The per-user data folder: `VIBE_STUDIO_DATA_DIR`, else FilmCraft's location under Vibe
/// Studio's own name. An explicit `FILMCRAFT_DATA_DIR` or a portable install's folder is used as is.
pub fn data_dir() -> Option<PathBuf> {
    if let Some(d) = std::env::var_os("VIBE_STUDIO_DATA_DIR").filter(|v| !v.is_empty()) {
        return Some(PathBuf::from(d));
    }
    let base = filmcraft_engine::autosave::default_data_dir()?;
    if std::env::var_os("FILMCRAFT_DATA_DIR").is_some_and(|v| !v.is_empty()) {
        return Some(base);
    }
    Some(match base.file_name().and_then(|n| n.to_str()) {
        Some("FilmCraft") => base.with_file_name("Vibe Studio"),
        Some("filmcraft") => base.with_file_name("vibe-studio"),
        _ => base,
    })
}

// ---------------------------------------------------------------------------------------------
// The agent
// ---------------------------------------------------------------------------------------------

/// How the agent reaches this app: the control channel's port and token.
#[derive(Clone)]
pub struct ControlLink {
    pub port: u16,
    pub token: String,
}

/// Where this app tells other Claude Code sessions how to reach it (`filmcraft-cli mcp --bridge
/// vibe-studio`, the repository's `.mcp.json`): `VIBE_STUDIO_LIVE`, else `~/.vibe-studio/live.json`.
fn live_file() -> Option<PathBuf> {
    if let Some(p) = std::env::var_os("VIBE_STUDIO_LIVE").filter(|v| !v.is_empty()) {
        return Some(p.into());
    }
    let home = std::env::var_os("HOME").or_else(|| std::env::var_os("USERPROFILE")).filter(|v| !v.is_empty())?;
    Some(PathBuf::from(home).join(".vibe-studio").join("live.json"))
}

/// Say where this app listens, for a Claude Code session started anywhere else (the Claude app,
/// a terminal) in the vibe-editor folder. The file holds the control token, so the folder and
/// the file are the user's only. The last Vibe Studio started wins.
pub fn publish_live(link: &ControlLink) {
    let Some(path) = live_file() else { return };
    let write = || -> std::io::Result<()> {
        if let Some(dir) = path.parent() {
            std::fs::create_dir_all(dir)?;
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                std::fs::set_permissions(dir, std::fs::Permissions::from_mode(0o700))?;
            }
        }
        let tmp = path.with_extension("json.tmp");
        let mut opts = std::fs::OpenOptions::new();
        opts.write(true).create(true).truncate(true);
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            opts.mode(0o600);
        }
        let mut f = opts.open(&tmp)?;
        f.write_all(json!({"port": link.port, "token": link.token, "pid": std::process::id()}).to_string().as_bytes())?;
        drop(f);
        std::fs::rename(&tmp, &path)
    };
    match write() {
        Ok(()) => log::info!("agents in the vibe-editor folder can reach this app (see {})", path.display()),
        Err(e) => log::warn!("could not write {}: {e}", path.display()),
    }
}

/// Remove the live file when this app wrote it (another Vibe Studio may have since).
pub fn unpublish_live() {
    let Some(path) = live_file() else { return };
    let ours = std::fs::read(&path)
        .ok()
        .and_then(|b| serde_json::from_slice::<Value>(&b).ok())
        .and_then(|v| v.get("pid").and_then(Value::as_u64))
        .is_some_and(|pid| pid == u64::from(std::process::id()));
    if ours {
        let _ = std::fs::remove_file(path);
    }
}

/// The vibe-editor checkout: `VIBE_EDITOR_REPO`, else the nearest folder above `near` (the open
/// project or its media), the working directory or the app that has the pipeline in it.
pub fn repo_root(near: Option<&str>) -> Option<PathBuf> {
    if let Some(p) = std::env::var_os("VIBE_EDITOR_REPO").map(PathBuf::from).filter(|p| is_repo(p)) {
        return Some(p);
    }
    let mut from: Vec<PathBuf> = near.map(PathBuf::from).into_iter().collect();
    from.extend(starts());
    from.into_iter().find_map(|s| s.ancestors().take(16).find(|d| is_repo(d)).map(Path::to_path_buf))
}

fn is_repo(d: &Path) -> bool {
    d.join("CLAUDE.md").is_file() && d.join("workflows").is_dir() && d.join("run.sh").is_file()
}

/// The PATH a terminal would have. An app opened from the Finder or a desktop menu starts with a
/// bare PATH, without Homebrew, npm or the folder the Claude Code installer uses, and `claude` (a
/// Node program) would not start. Asks the user's login shell once.
fn shell_path() -> Option<String> {
    static PATH: std::sync::OnceLock<Option<String>> = std::sync::OnceLock::new();
    PATH.get_or_init(|| {
        #[cfg(unix)]
        {
            let shell = std::env::var("SHELL").ok().filter(|s| !s.is_empty()).unwrap_or_else(|| "/bin/sh".into());
            let out = Command::new(shell).args(["-l", "-c", "printf %s \"$PATH\""]).stdin(Stdio::null()).stderr(Stdio::null()).output().ok()?;
            String::from_utf8(out.stdout).ok().map(|s| s.trim().to_string()).filter(|s| !s.is_empty())
        }
        #[cfg(not(unix))]
        {
            None
        }
    })
    .clone()
}

/// The PATH for the agent: the app's own, then the login shell's, then the usual install folders.
fn agent_path() -> std::ffi::OsString {
    let mut dirs: Vec<PathBuf> = std::env::var_os("PATH").map(|p| std::env::split_paths(&p).collect()).unwrap_or_default();
    if let Some(p) = shell_path() {
        dirs.extend(std::env::split_paths(&std::ffi::OsString::from(p)));
    }
    if let Some(home) = std::env::var_os("HOME").map(PathBuf::from) {
        for d in [".local/bin", ".claude/local", ".npm-global/bin", ".bun/bin", ".volta/bin"] {
            dirs.push(home.join(d));
        }
    }
    dirs.extend(["/opt/homebrew/bin", "/usr/local/bin"].map(PathBuf::from));
    let mut seen = std::collections::HashSet::new();
    dirs.retain(|d| seen.insert(d.clone()));
    std::env::join_paths(dirs).unwrap_or_default()
}

fn find_in(path: &std::ffi::OsString, name: &str) -> Option<PathBuf> {
    let names: Vec<String> = if cfg!(windows) { vec![format!("{name}.exe"), format!("{name}.cmd")] } else { vec![name.to_string()] };
    std::env::split_paths(path).flat_map(|d| names.iter().map(move |n| d.join(n))).find(|p| p.is_file())
}

/// `claude`: `VIBE_AGENT_CLAUDE`, else on the agent's PATH.
fn find_claude(path: &std::ffi::OsString) -> Option<PathBuf> {
    std::env::var_os("VIBE_AGENT_CLAUDE").map(PathBuf::from).filter(|p| p.is_file()).or_else(|| find_in(path, "claude"))
}

/// The MCP server that is this app: `filmcraft-cli mcp --bridge`, beside this executable.
fn bridge_cli() -> Option<PathBuf> {
    let dir = std::env::current_exe().ok()?.parent()?.to_path_buf();
    let name = if cfg!(windows) { "filmcraft-cli.exe" } else { "filmcraft-cli" };
    Some(dir.join(name)).filter(|p| p.is_file())
}

/// Write the MCP config that hands the agent this app. It holds the control token, so it is
/// readable by the user only, kept in the data folder and removed when the agent ends.
fn write_mcp_config(link: &ControlLink, cli: &Path) -> Result<PathBuf, String> {
    let dir = data_dir().unwrap_or_else(std::env::temp_dir).join("agent");
    std::fs::create_dir_all(&dir).map_err(|e| format!("{}: {e}", dir.display()))?;
    let path = dir.join(format!("mcp-{}-{}.json", std::process::id(), link.port));
    let config = json!({"mcpServers": {"vibe-studio": {
        "type": "stdio",
        "command": cli.to_string_lossy(),
        "args": ["mcp", "--bridge", format!("127.0.0.1:{}", link.port)],
        "env": {"FILMCRAFT_CONTROL_TOKEN": link.token},
    }}});
    let mut opts = std::fs::OpenOptions::new();
    opts.write(true).create(true).truncate(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        opts.mode(0o600);
    }
    let mut f = opts.open(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    f.write_all(config.to_string().as_bytes()).map_err(|e| e.to_string())?;
    Ok(path)
}

/// The app's MCP tools that only read (the timeline, the command list, frames, the window):
/// allowed without a prompt.
const READ_ONLY_TOOLS: [&str; 9] =
    ["command_list", "doc_inspect", "project_inspect", "sequence_inspect", "render_frame", "render_preview", "ui_inspect", "ui_elements", "ui_screenshot"];

/// The command line for Claude Code in stream mode, with permission prompts sent to the panel.
fn claude_args(launch: &AgentLaunch, mcp: Option<&Path>) -> Vec<String> {
    let mode = match launch.permission_mode.as_str() {
        m @ ("acceptEdits" | "plan" | "default") => m,
        _ => "default",
    };
    let mut a: Vec<String> = [
        "-p",
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-prompt-tool",
        "stdio",
        "--permission-mode",
        mode,
        "--append-system-prompt",
        AGENT_CONTEXT,
    ]
    .map(String::from)
    .to_vec();
    if let Some(p) = mcp {
        // this session gets its own private link to this app; the repository's `.mcp.json` server
        // of the same name (for sessions started elsewhere) would find the same app another way
        a.push("--settings".into());
        a.push(r#"{"disabledMcpjsonServers":["vibe-studio"]}"#.into());
        a.push("--mcp-config".into());
        a.push(p.to_string_lossy().into_owned());
        // looking at the edit never needs a prompt; changing it does (each change is an undo step)
        a.push("--allowedTools".into());
        a.push(READ_ONLY_TOOLS.map(|t| format!("mcp__vibe-studio__{t}")).join(","));
    }
    if let Some(id) = launch.resume.as_deref().filter(|id| !id.is_empty() && id.chars().all(|c| c.is_ascii_alphanumeric() || c == '-')) {
        a.push("--resume".into());
        a.push(id.into());
    } else if launch.continue_last {
        a.push("--continue".into());
    }
    a
}

/// The Assistant's launcher: Claude Code in the vibe-editor checkout, connected to this app.
pub fn agent_launcher(link: Option<ControlLink>) -> AgentLauncher {
    Arc::new(move |launch: &AgentLaunch| {
        let path = agent_path();
        let claude = find_claude(&path).ok_or(
            "Claude Code isn't installed or isn't on your PATH. Install it (https://claude.com/claude-code), sign in once in a terminal with `claude`, then try again. (VIBE_AGENT_CLAUDE can point at it.)",
        )?;
        let repo = repo_root(launch.near.as_deref()).ok_or(
            "Couldn't find your vibe-editor folder (the one with CLAUDE.md, run.sh and workflows/). Open a project inside it, start Vibe Studio from it, or set VIBE_EDITOR_REPO.",
        )?;
        let mcp = match (&link, bridge_cli()) {
            (Some(l), Some(cli)) => Some(write_mcp_config(l, &cli)?),
            _ => {
                log::warn!("agent: no control channel or filmcraft-cli beside the app; the agent can run the pipeline but not see the timeline");
                None
            }
        };
        let mut child = Command::new(&claude)
            .args(claude_args(launch, mcp.as_deref()))
            .current_dir(&repo)
            .env("PATH", &path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Couldn't start {}: {e}", claude.display()))?;
        let (Some(stdin), Some(stdout), Some(stderr)) = (child.stdin.take(), child.stdout.take(), child.stderr.take()) else {
            let _ = child.kill();
            return Err("Couldn't connect to Claude Code's input and output.".into());
        };
        let child = Arc::new(Mutex::new(child));
        let (out_tx, out_rx) = channel();
        let (in_tx, in_rx) = channel::<AgentInput>();
        let tail = Arc::new(Mutex::new(Vec::<String>::new()));

        // stderr: keep the last lines for the exit message
        let t = Arc::clone(&tail);
        std::thread::spawn(move || {
            for line in BufReader::new(stderr).lines().map_while(Result::ok) {
                let mut t = t.lock().unwrap_or_else(PoisonError::into_inner);
                t.push(line);
                if t.len() > 6 {
                    t.remove(0);
                }
            }
        });
        // stdin: the panel's messages and answers, one JSON line each
        let c = Arc::clone(&child);
        std::thread::spawn(move || {
            let mut stdin = stdin;
            for msg in in_rx {
                match msg {
                    AgentInput::Line(v) => {
                        if writeln!(stdin, "{v}").and_then(|()| stdin.flush()).is_err() {
                            break;
                        }
                    }
                    AgentInput::Stop => {
                        let _ = c.lock().unwrap_or_else(PoisonError::into_inner).kill();
                        break;
                    }
                }
            }
        });
        // stdout: stream-json lines to the panel, then the exit
        let c = Arc::clone(&child);
        std::thread::spawn(move || {
            for line in BufReader::new(stdout).lines().map_while(Result::ok) {
                if let Ok(v) = serde_json::from_str::<Value>(&line)
                    && out_tx.send(AgentOutput::Line(v)).is_err()
                {
                    break;
                }
            }
            let status = c.lock().unwrap_or_else(PoisonError::into_inner).wait();
            if let Some(p) = &mcp {
                let _ = std::fs::remove_file(p);
            }
            let why = match status {
                Ok(s) if s.success() => String::new(),
                Ok(s) => {
                    let t = tail.lock().unwrap_or_else(PoisonError::into_inner).join("\n");
                    format!("{s}{}", if t.is_empty() { String::new() } else { format!("\n{t}") })
                }
                Err(e) => e.to_string(),
            };
            let _ = out_tx.send(AgentOutput::Exited(why));
        });
        let home = std::env::var_os("HOME").map(PathBuf::from);
        let shown = match home.as_deref().and_then(|h| repo.strip_prefix(h).ok()) {
            Some(rel) => format!("~/{}", rel.display()),
            None => repo.display().to_string(),
        };
        log::info!("agent: {} in {}", claude.display(), repo.display());
        Ok(AgentProcess { output: out_rx, input: in_tx, label: format!("Claude Code · {shown}") })
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn data_dir_is_not_filmcrafts() {
        if std::env::var_os("FILMCRAFT_DATA_DIR").is_none()
            && std::env::var_os("VIBE_STUDIO_DATA_DIR").is_none()
            && let Some(d) = data_dir()
        {
            let name = d.file_name().and_then(|n| n.to_str()).unwrap_or_default().to_string();
            assert!(name != "FilmCraft" && name != "filmcraft", "{}", d.display());
        }
    }

    #[test]
    fn claude_runs_in_stream_mode_with_prompts_in_the_panel() {
        let l = AgentLaunch { permission_mode: "acceptEdits".into(), resume: Some("c849ab43-deba".into()), ..Default::default() };
        let a = claude_args(&l, Some(Path::new("/tmp/mcp.json")));
        let s = a.join(" ");
        assert!(
            s.starts_with("-p --input-format stream-json --output-format stream-json --verbose --permission-prompt-tool stdio --permission-mode acceptEdits")
        );
        assert!(s.contains("--mcp-config /tmp/mcp.json"));
        let allowed = a.iter().position(|x| x == "--allowedTools").and_then(|i| a.get(i + 1)).cloned().unwrap_or_default();
        assert!(allowed.contains("mcp__vibe-studio__sequence_inspect") && !allowed.contains("command_run"), "{allowed}");
        assert!(s.ends_with("--resume c849ab43-deba"));
        // a hostile mode or session id never reaches the command line
        let l = AgentLaunch { permission_mode: "bypassPermissions".into(), resume: Some("x; rm -rf ~".into()), continue_last: true, ..Default::default() };
        let s = claude_args(&l, None).join(" ");
        assert!(s.contains("--permission-mode default") && !s.contains("rm -rf") && s.ends_with("--continue"));
    }

    #[test]
    fn the_repo_is_found_above_a_project_inside_it() {
        let root = std::env::temp_dir().join(format!("vibe-repo-{}", std::process::id()));
        let job = root.join("projects").join("demo").join("vibe");
        std::fs::create_dir_all(&job).unwrap();
        std::fs::create_dir_all(root.join("workflows")).unwrap();
        std::fs::write(root.join("CLAUDE.md"), "x").unwrap();
        std::fs::write(root.join("run.sh"), "x").unwrap();
        let found = repo_root(Some(job.join("demo.fcproj").to_str().unwrap()));
        assert_eq!(found.as_deref(), Some(root.as_path()));
        let _ = std::fs::remove_dir_all(&root);
    }
}
