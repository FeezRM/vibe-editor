//! Client for the desktop app's JSON-lines control protocol. A connection per request in flight,
//! reused once its reply is in; reconnect on failure.

use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

use serde_json::{Value, json};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpStream;
use tokio::sync::Mutex;

use crate::AutomationError;

/// How often a blocking export's app job is polled.
const JOB_POLL: Duration = Duration::from_millis(250);
/// Idle connections kept for reuse; the app serves at most 16 at once.
const MAX_IDLE: usize = 4;

type Conn = (BufReader<tokio::net::tcp::OwnedReadHalf>, tokio::net::tcp::OwnedWriteHalf);

pub struct BridgeClient {
    addr: String,
    /// Inherited from the same owner-controlled environment as the desktop app.
    token: Option<String>,
    /// Connections with no request in flight. A request takes one (or opens one) for its whole
    /// round trip and puts it back only once the reply is read, so a slow or abandoned request
    /// never holds up the others or leaves its late reply for the next one to read (#1538).
    idle: Mutex<Vec<Conn>>,
    next_id: AtomicU64,
    /// Vibe Studio: `--bridge vibe-studio` finds the running app through this file (written by the
    /// app while it is open, readable by the user only), read again on every connect, so the
    /// client works whichever of the two started first and follows an app restart.
    live: Option<std::path::PathBuf>,
    /// The address and token last read from `live`.
    current: std::sync::Mutex<Option<(String, String)>>,
}

/// Where a running Vibe Studio says how to reach it: `VIBE_STUDIO_LIVE`, else
/// `~/.vibe-studio/live.json`.
pub fn vibe_studio_live_file() -> Option<std::path::PathBuf> {
    if let Some(p) = std::env::var_os("VIBE_STUDIO_LIVE").filter(|v| !v.is_empty()) {
        return Some(p.into());
    }
    let home = std::env::var_os("HOME").or_else(|| std::env::var_os("USERPROFILE")).filter(|v| !v.is_empty())?;
    Some(std::path::PathBuf::from(home).join(".vibe-studio").join("live.json"))
}

impl BridgeClient {
    /// `addr` such as `127.0.0.1:9876` (loopback only). Reads `FILMCRAFT_CONTROL_TOKEN`
    /// from the environment; the desktop app requires this credential on every request.
    pub fn new(addr: impl Into<String>) -> Result<Self, AutomationError> {
        let addr = addr.into();
        if addr == "vibe-studio" {
            let live = vibe_studio_live_file().ok_or_else(|| AutomationError::BadRequest("no home folder to find Vibe Studio in".into()))?;
            return Ok(Self {
                addr,
                token: None,
                idle: Mutex::new(Vec::new()),
                next_id: AtomicU64::new(1),
                live: Some(live),
                current: std::sync::Mutex::new(None),
            });
        }
        let host = addr.rsplit_once(':').map(|(h, _)| h).unwrap_or(&addr);
        if !matches!(host, "127.0.0.1" | "localhost" | "[::1]" | "::1") {
            return Err(AutomationError::BadRequest(format!("bridge address must be loopback, got `{addr}`")));
        }
        Ok(Self {
            addr,
            token: std::env::var("FILMCRAFT_CONTROL_TOKEN").ok(),
            idle: Mutex::new(Vec::new()),
            next_id: AtomicU64::new(1),
            live: None,
            current: std::sync::Mutex::new(None),
        })
    }

    /// Run engine command `id` in the app. A blocking export (`file.exportMedia` with
    /// `wait: true`, see [`crate::long_job::LONG_COMMANDS`]) is started as an app job and polled
    /// here until it finishes, so the app keeps repainting (its status bar shows the progress) and
    /// answering other requests, and no request waits on the control server's 60 s reply limit
    /// (#91, #92). The reply is the same as a blocking export's: `{job, path, result}`, or the
    /// export's error.
    pub async fn execute(&self, id: &str, mut params: Value) -> Result<Value, AutomationError> {
        if !crate::long_job::is_long(id, &params) {
            return self.call("engine.execute", json!({"command": id, "params": params})).await;
        }
        if let Some(p) = params.as_object_mut() {
            p.insert("wait".into(), json!(false));
        }
        let mut start = self.call("engine.execute", json!({"command": id, "params": params})).await?;
        let Some(job) = start.get("job").and_then(Value::as_u64) else { return Ok(start) };
        let (result, offline) = loop {
            tokio::time::sleep(JOB_POLL).await;
            let jobs = self.call("engine.execute", json!({"command": "jobs.list", "params": {}})).await?;
            let Some(j) = jobs.as_array().and_then(|a| a.iter().find(|j| j["id"].as_u64() == Some(job))).cloned() else {
                break (Value::Null, None);
            };
            if j["finished"].as_bool() == Some(true) {
                break (j["result"].clone(), j.get("offlineMedia").cloned());
            }
        };
        if let Some(e) = result.get("error").and_then(Value::as_str) {
            return Err(AutomationError::App(format!("export failed: {e}")));
        }
        if let Some(o) = start.as_object_mut() {
            o.insert("result".into(), result);
            if let Some(off) = offline {
                o.insert("offlineMedia".into(), off);
            }
        }
        Ok(start)
    }

    /// Call a control method; returns `result` or the app's error.
    pub async fn call(&self, method: &str, params: Value) -> Result<Value, AutomationError> {
        for attempt in 0..2 {
            // A retry gets a fresh connection: the failed one may have been closed by an app restart.
            let idle = if attempt == 0 { self.idle.lock().await.pop() } else { None };
            let mut conn = match idle {
                Some(c) => c,
                None => self.connect().await?,
            };
            let id = self.next_id.fetch_add(1, Ordering::Relaxed);
            let token = self.token_now();
            let line = format!("{}\n", json!({"id": id, "token": token, "method": method, "params": params}));
            let res: Result<Value, AutomationError> = async {
                conn.1.write_all(line.as_bytes()).await.map_err(|e| AutomationError::Bridge(e.to_string()))?;
                let mut buf = String::new();
                tokio::time::timeout(Duration::from_secs(90), conn.0.read_line(&mut buf))
                    .await
                    .map_err(|_| AutomationError::Bridge("timeout".into()))?
                    .map_err(|e| AutomationError::Bridge(e.to_string()))?;
                serde_json::from_str(&buf).map_err(|e| AutomationError::Bridge(format!("bad reply: {e}")))
            }
            .await;
            match res {
                Ok(v) => {
                    let mut idle = self.idle.lock().await;
                    if idle.len() < MAX_IDLE {
                        idle.push(conn);
                    }
                    drop(idle);
                    return if v.get("ok").and_then(Value::as_bool) == Some(true) {
                        Ok(v.get("result").cloned().unwrap_or(Value::Null))
                    } else {
                        Err(AutomationError::App(v.get("error").and_then(Value::as_str).unwrap_or("error").to_string()))
                    };
                }
                Err(_) if attempt == 0 => {}
                Err(e) => return Err(e),
            }
        }
        Err(AutomationError::Bridge("unreachable".into()))
    }

    /// The token for the next request: the one `live` gave with the address, else the environment's.
    fn token_now(&self) -> Option<String> {
        if self.live.is_some() {
            return self.current.lock().unwrap_or_else(std::sync::PoisonError::into_inner).as_ref().map(|(_, t)| t.clone());
        }
        self.token.clone()
    }

    /// Vibe Studio: read the running app's address and token from `live`.
    fn read_live(&self, live: &std::path::Path) -> Result<String, AutomationError> {
        let not_open = || {
            AutomationError::Bridge(
                "Vibe Studio isn't open. Open a job in it with `lanes/vibe/open.sh projects/<job>` (or start the app), then try again.".into(),
            )
        };
        let bytes = std::fs::read(live).map_err(|_| not_open())?;
        let v: Value = serde_json::from_slice(bytes.get(..bytes.len().min(64 * 1024)).unwrap_or_default()).map_err(|_| not_open())?;
        let port = v.get("port").and_then(Value::as_u64).and_then(|p| u16::try_from(p).ok()).filter(|p| *p > 0).ok_or_else(not_open)?;
        let token = v.get("token").and_then(Value::as_str).map(str::to_string).ok_or_else(not_open)?;
        let addr = format!("127.0.0.1:{port}");
        *self.current.lock().unwrap_or_else(std::sync::PoisonError::into_inner) = Some((addr.clone(), token));
        Ok(addr)
    }

    async fn connect(&self) -> Result<Conn, AutomationError> {
        if let Some(live) = &self.live {
            let addr = self.read_live(live)?;
            let s = tokio::time::timeout(Duration::from_secs(5), TcpStream::connect(&addr))
                .await
                .map_err(|_| AutomationError::Bridge(format!("timed out connecting to Vibe Studio at {addr}")))?
                .map_err(|_| AutomationError::Bridge("Vibe Studio isn't open (it closed or quit). Open it again, then try again.".into()))?;
            let (r, w) = s.into_split();
            return Ok((BufReader::new(r), w));
        }
        let s = tokio::time::timeout(Duration::from_secs(5), TcpStream::connect(&self.addr))
            .await
            .map_err(|_| AutomationError::Bridge(format!("timed out connecting to {}", self.addr)))?
            .map_err(|e| AutomationError::Bridge(format!(
                "cannot connect to {} ({e}); start the app with `vibe-studio --control <port>` and set FILMCRAFT_CONTROL_TOKEN to the same 64-hex-character value on both sides (see docs/control-protocol.md)",
                self.addr
            )))?;
        let (r, w) = s.into_split();
        Ok((BufReader::new(r), w))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use tokio::net::TcpListener;

    /// Vibe Studio: `--bridge vibe-studio` reads the app's port and token from the live file on
    /// connect, sends that token, and says plainly when the app isn't open.
    #[tokio::test]
    async fn vibe_studio_bridge_follows_the_live_file() {
        let dir = std::env::temp_dir().join(format!("vibe-live-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let live = dir.join("live.json");
        let mut b = BridgeClient::new("vibe-studio").unwrap();
        b.live = Some(live.clone());
        let err = b.call("ui.inspect", json!({})).await.unwrap_err().to_string();
        assert!(err.contains("Vibe Studio isn't open"), "{err}");
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let port = listener.local_addr().unwrap().port();
        std::fs::write(&live, json!({"port": port, "token": "t0k", "pid": 1}).to_string()).unwrap();
        let seen = Arc::new(Mutex::new(None));
        let log = seen.clone();
        tokio::spawn(async move {
            let (s, _) = listener.accept().await.unwrap();
            let (r, mut w) = s.into_split();
            let mut lines = BufReader::new(r).lines();
            if let Ok(Some(line)) = lines.next_line().await {
                let req: Value = serde_json::from_str(&line).unwrap();
                *log.lock().await = Some(req["token"].clone());
                w.write_all(format!("{}\n", json!({"id": req["id"], "ok": true, "result": 7})).as_bytes()).await.unwrap();
            }
        });
        assert_eq!(b.call("ui.inspect", json!({})).await.unwrap(), json!(7));
        assert_eq!(seen.lock().await.clone(), Some(json!("t0k")));
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// A stand-in for the app's control server: the export starts job 7, which `jobs.list` reports
    /// running twice and then finished with `result`. Every request is recorded.
    async fn fake_app(result: Value) -> (String, Arc<Mutex<Vec<Value>>>) {
        fake_app_with(result, None).await
    }

    /// [`fake_app`] whose finished job also lists `offline` as its `offlineMedia`.
    async fn fake_app_with(result: Value, offline: Option<Value>) -> (String, Arc<Mutex<Vec<Value>>>) {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap().to_string();
        let seen = Arc::new(Mutex::new(Vec::new()));
        let log = seen.clone();
        tokio::spawn(async move {
            let (s, _) = listener.accept().await.unwrap();
            let (r, mut w) = s.into_split();
            let mut lines = BufReader::new(r).lines();
            let mut polls = 0;
            while let Ok(Some(line)) = lines.next_line().await {
                let req: Value = serde_json::from_str(&line).unwrap();
                log.lock().await.push(req.clone());
                let reply = match req["params"]["command"].as_str() {
                    Some("file.exportMedia") => json!({"job": 7, "path": "/tmp/out.mov"}),
                    Some("jobs.list") => {
                        polls += 1;
                        let finished = polls >= 3;
                        let mut j = json!({"id": 7, "finished": finished, "result": if finished { result.clone() } else { Value::Null }});
                        if let Some(o) = offline.clone().filter(|_| finished) {
                            j["offlineMedia"] = o;
                        }
                        json!([j])
                    }
                    _ => json!(null),
                };
                let line = format!("{}\n", json!({"id": req["id"], "ok": true, "result": reply}));
                w.write_all(line.as_bytes()).await.unwrap();
            }
        });
        (addr, seen)
    }

    /// A refused connection names the launch command and the token requirement (#3436): the
    /// reporter spent two ports and a debug-level console capture on a bare "connection refused".
    #[tokio::test]
    async fn refused_connection_error_names_the_token_requirement() {
        // Bind and drop: connecting to the freed address is deterministically refused.
        let listener = tokio::net::TcpListener::bind(("127.0.0.1", 0)).await.unwrap();
        let addr = listener.local_addr().unwrap().to_string();
        drop(listener);
        let b = BridgeClient::new(addr.as_str()).unwrap();
        let err = b.call("ui.inspect", json!({})).await.unwrap_err().to_string();
        assert!(err.contains("--control"), "{err}");
        assert!(err.contains("FILMCRAFT_CONTROL_TOKEN"), "{err}");
    }

    /// A blocking bridge export runs as an app job (#91, #92): the app never sees `wait: true` (it
    /// would encode on its UI thread and the reply would time out after 60 s), and the caller still
    /// gets the finished result.
    #[tokio::test]
    async fn a_blocking_export_is_polled_as_a_job() {
        let (addr, seen) = fake_app(json!({"frames": 642})).await;
        let b = BridgeClient::new(addr).unwrap();
        let r = b.execute("file.exportMedia", json!({"path": "/tmp/out.mov", "wait": true})).await.unwrap();
        assert_eq!(r, json!({"job": 7, "path": "/tmp/out.mov", "result": {"frames": 642}}));
        let seen = seen.lock().await;
        assert_eq!(seen[0]["params"]["params"]["wait"], json!(false));
        assert!(seen.iter().all(|q| q["params"]["params"]["wait"] != json!(true)));
        assert_eq!(seen.iter().filter(|q| q["params"]["command"] == "file.exportMedia").count(), 1, "started once");
        assert_eq!(seen.iter().filter(|q| q["params"]["command"] == "jobs.list").count(), 3);
    }

    /// The offline media a polled export drew comes back as in a blocking export's reply (#1054).
    #[tokio::test]
    async fn a_polled_export_reports_its_offline_media() {
        let off = json!([{"item": 8, "status": "missing"}]);
        let (addr, _) = fake_app_with(json!({"frames": 3}), Some(off.clone())).await;
        let b = BridgeClient::new(addr).unwrap();
        let r = b.execute("file.exportMedia", json!({"path": "/tmp/out.mov", "wait": true})).await.unwrap();
        assert_eq!(r["offlineMedia"], off, "{r}");
    }

    #[tokio::test]
    async fn a_failed_blocking_export_is_an_error() {
        let (addr, _) = fake_app(json!({"error": "encode: disk full"})).await;
        let b = BridgeClient::new(addr).unwrap();
        let e = b.execute("file.exportMedia", json!({"path": "/tmp/out.mov", "wait": true})).await.unwrap_err();
        assert!(e.to_string().contains("export failed: encode: disk full"), "{e}");
    }

    /// A stand-in for the app that serves any number of connections and answers each request on
    /// its own, as the app does: `slow` after `slow_reply` (never when `None`), anything else at
    /// once with its command id. The ids of the requests it receives are sent to the returned channel.
    async fn slow_app(slow_reply: Option<Duration>) -> (String, tokio::sync::mpsc::UnboundedReceiver<String>) {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap().to_string();
        let (seen, rx) = tokio::sync::mpsc::unbounded_channel();
        tokio::spawn(async move {
            while let Ok((s, _)) = listener.accept().await {
                let seen = seen.clone();
                tokio::spawn(async move {
                    let (r, w) = s.into_split();
                    let w = Arc::new(Mutex::new(w));
                    let mut lines = BufReader::new(r).lines();
                    while let Ok(Some(line)) = lines.next_line().await {
                        let req: Value = serde_json::from_str(&line).unwrap();
                        let cmd = req["params"]["command"].as_str().unwrap_or_default().to_string();
                        let _ = seen.send(cmd.clone());
                        let delay = if cmd == "slow" { slow_reply } else { Some(Duration::ZERO) };
                        let w = w.clone();
                        tokio::spawn(async move {
                            let Some(d) = delay else { return };
                            tokio::time::sleep(d).await;
                            let line = format!("{}\n", json!({"id": req["id"], "ok": true, "result": cmd}));
                            let _ = w.lock().await.write_all(line.as_bytes()).await;
                        });
                    }
                });
            }
        });
        (addr, rx)
    }

    /// A command the app is slow to answer holds up only itself: a later call is answered at once
    /// instead of queueing behind it, and behind every call queued after it (#1538).
    #[tokio::test]
    async fn a_slow_command_does_not_block_later_calls() {
        let (addr, mut seen) = slow_app(None).await;
        let b = Arc::new(BridgeClient::new(addr).unwrap());
        let slow = tokio::spawn({
            let b = b.clone();
            async move { b.execute("slow", json!({})).await }
        });
        assert_eq!(seen.recv().await.as_deref(), Some("slow"));
        let fast = tokio::time::timeout(Duration::from_secs(5), b.execute("fast", json!({}))).await;
        assert_eq!(fast.expect("the later call waited on the slow one").unwrap(), json!("fast"));
        slow.abort();
    }

    /// A call given up while it waits leaves no late reply on a connection for the next call to read
    /// as its own (#1538).
    #[tokio::test]
    async fn an_abandoned_call_leaves_no_late_reply_behind() {
        let (addr, mut seen) = slow_app(Some(Duration::from_millis(100))).await;
        let b = Arc::new(BridgeClient::new(addr).unwrap());
        let slow = tokio::spawn({
            let b = b.clone();
            async move { b.execute("slow", json!({})).await }
        });
        assert_eq!(seen.recv().await.as_deref(), Some("slow"));
        slow.abort();
        tokio::time::sleep(Duration::from_millis(300)).await;
        assert_eq!(b.execute("fast", json!({})).await.unwrap(), json!("fast"));
    }

    /// Everything else is forwarded unchanged.
    #[tokio::test]
    async fn other_commands_are_forwarded() {
        let (addr, seen) = fake_app(Value::Null).await;
        let b = BridgeClient::new(addr).unwrap();
        b.execute("file.exportMedia", json!({"path": "/tmp/out.mov"})).await.unwrap();
        b.execute("sequence.inspect", json!({})).await.unwrap();
        let seen = seen.lock().await;
        assert_eq!(seen.len(), 2);
        assert_eq!(seen[1]["params"]["command"], "sequence.inspect");
    }

    #[tokio::test]
    async fn credential_is_sent_on_every_request() {
        let (addr, seen) = fake_app(Value::Null).await;
        let mut b = BridgeClient::new(addr).unwrap();
        // Inject directly to avoid mutating the process environment in parallel tests.
        let token = "0123456789abcdef".repeat(4);
        b.token = Some(token.clone());
        b.call("ui.inspect", json!({})).await.unwrap();
        b.execute("file.saveAs", json!({"path": "/owner/project.vibeproj"})).await.unwrap();
        let seen = seen.lock().await;
        assert_eq!(seen.len(), 2);
        assert!(seen.iter().all(|request| request["token"] == token));
        assert_eq!(seen[1]["params"]["params"]["path"], "/owner/project.vibeproj");
    }
}
