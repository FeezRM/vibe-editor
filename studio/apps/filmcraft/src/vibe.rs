//! Vibe Studio's host pieces: the brand accent, the Assistant's connection to Claude, and where
//! the app keeps its data (apart from FilmCraft's, so the two never share settings or recovery).

use std::path::{Path, PathBuf};
use std::sync::Arc;

use filmcraft_ui_egui::assistant::ClaudeTransport;
use serde_json::Value;

/// The app's name in windows, dialogs and the data folder.
pub const APP_NAME: &str = "Vibe Studio";

/// Messages API version this build speaks.
const API_VERSION: &str = "2026-10-21";
/// Largest response body read (a long answer with tool calls is far smaller).
const MAX_RESPONSE: u64 = 32 * 1024 * 1024;

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
    let starts = [std::env::current_dir().ok(), std::env::current_exe().ok().and_then(|e| e.parent().map(Path::to_path_buf))];
    starts.into_iter().flatten().find_map(|start| start.ancestors().take(12).map(|d| d.join("brand").join("brand.json")).find(|p| p.is_file()))
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

enum Auth {
    Key(String),
    Bearer(String),
}

/// A key typed in the panel, else `ANTHROPIC_API_KEY`, else `ANTHROPIC_AUTH_TOKEN` (an OAuth
/// access token, sent as a bearer token).
fn credentials(typed: Option<&str>) -> Option<Auth> {
    if let Some(k) = typed.map(str::trim).filter(|k| !k.is_empty()) {
        return Some(Auth::Key(k.to_string()));
    }
    let env = |name: &str| std::env::var(name).ok().map(|v| v.trim().to_string()).filter(|v| !v.is_empty());
    env("ANTHROPIC_API_KEY").map(Auth::Key).or_else(|| env("ANTHROPIC_AUTH_TOKEN").map(Auth::Bearer))
}

fn agent() -> ureq::Agent {
    let provider = Arc::new(rustls_rustcrypto::provider());
    ureq::Agent::config_builder()
        .tls_config(
            ureq::tls::TlsConfig::builder()
                .provider(ureq::tls::TlsProvider::Rustls)
                .root_certs(ureq::tls::RootCerts::PlatformVerifier)
                .unversioned_rustls_crypto_provider(provider)
                .build(),
        )
        .timeout_connect(Some(std::time::Duration::from_secs(30)))
        // a long answer with thinking can take minutes
        .timeout_global(Some(std::time::Duration::from_secs(600)))
        // read the API's error body instead of a bare status code
        .http_status_as_error(false)
        .build()
        .into()
}

/// The Assistant's connection to the Claude Messages API (blocking; called on its worker thread).
pub fn claude_transport() -> ClaudeTransport {
    let agent = agent();
    let base = std::env::var("ANTHROPIC_BASE_URL").ok().filter(|u| u.starts_with("https://")).unwrap_or_else(|| "https://api.anthropic.com".into());
    let url = format!("{}/v1/messages", base.trim_end_matches('/'));
    Arc::new(move |body: &Value, typed: Option<&str>| {
        let auth = credentials(typed).ok_or("No Claude API key. Set ANTHROPIC_API_KEY before starting Vibe Studio, or paste a key in the Assistant panel.")?;
        // fallbacks: "default" (server-side refusal fallback) needs its beta
        let mut betas = vec!["server-side-fallback-2026-07-01"];
        let mut req = agent.post(&url).header("content-type", "application/json").header("anthropic-version", API_VERSION);
        req = match &auth {
            Auth::Key(k) => req.header("x-api-key", k.as_str()),
            Auth::Bearer(t) => {
                betas.push("oauth-2025-04-20");
                req.header("authorization", format!("Bearer {t}").as_str())
            }
        };
        req = req.header("anthropic-beta", betas.join(",").as_str());
        let payload = serde_json::to_vec(body).map_err(|e| e.to_string())?;
        let mut resp = req.send(&payload[..]).map_err(|e| format!("Could not reach Claude: {e}"))?;
        let status = resp.status().as_u16();
        let bytes = resp.body_mut().with_config().limit(MAX_RESPONSE).read_to_vec().map_err(|e| format!("Could not read Claude's answer: {e}"))?;
        let v: Value = serde_json::from_slice(&bytes).map_err(|e| format!("Claude's answer was not JSON ({status}): {e}"))?;
        if status >= 400 {
            let msg = v.pointer("/error/message").and_then(Value::as_str).unwrap_or("request failed");
            return Err(match status {
                401 => format!("Claude rejected the API key ({status}): {msg}"),
                429 => format!("Rate limited by the Claude API ({status}): {msg}. Try again in a moment."),
                _ => format!("Claude API error {status}: {msg}"),
            });
        }
        Ok(v)
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_typed_key_wins_over_the_environment() {
        assert!(matches!(credentials(Some(" sk-test ")), Some(Auth::Key(k)) if k == "sk-test"));
    }

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
}
