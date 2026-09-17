#!/usr/bin/env bash
#
# Vibe Editor — macOS setup
#
# Installs the three engines the agent drives:
#   1. HyperFrames  — HTML -> deterministic video, for motion graphics
#   2. Premiere Pro MCP — 283 MCP tools that drive a local Premiere Pro
#   3. Claude Video — /watch, so the agent can see footage and reference reels
#
# Idempotent. Safe to re-run to update all three engines.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$REPO_ROOT/vendor"
HF_DIR="$VENDOR_DIR/hyperframes"
PP_DIR="$VENDOR_DIR/adobe-premiere-pro-mcp"
CV_DIR="$VENDOR_DIR/claude-video"
BRIDGE_DIR="/tmp/premiere-mcp-bridge"

HF_REPO="https://github.com/heygen-com/hyperframes.git"
PP_REPO="https://github.com/hetpatel-11/adobe_premiere_pro_mcp.git"
CV_REPO="https://github.com/bradautomates/claude-video.git"

SKIP_HYPERFRAMES=false
SKIP_PREMIERE=false
SKIP_WATCH=false
SKIP_SKILLS=false
SKIP_DOCTOR=false

# ---------------------------------------------------------------- output ----

if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; RESET=$'\033[0m'
  GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; CYAN=$'\033[36m'
else
  BOLD=''; DIM=''; RESET=''; GREEN=''; YELLOW=''; RED=''; CYAN=''
fi

step()  { printf '\n%s==>%s %s%s%s\n' "$CYAN" "$RESET" "$BOLD" "$1" "$RESET"; }
ok()    { printf '  %s✓%s %s\n' "$GREEN" "$RESET" "$1"; }
warn()  { printf '  %s!%s %s\n' "$YELLOW" "$RESET" "$1"; }
fail()  { printf '  %s✗%s %s\n' "$RED" "$RESET" "$1" >&2; }
note()  { printf '    %s%s%s\n' "$DIM" "$1" "$RESET"; }

die() { fail "$1"; exit 1; }

usage() {
  cat <<'EOF'
Vibe Editor — macOS setup

Usage: scripts/setup-macos.sh [options]

Options:
  --skip-hyperframes   Don't clone HyperFrames or install its skills
  --skip-premiere      Don't clone/build the Premiere Pro MCP bridge
  --skip-watch         Don't clone Claude Video or install the /watch skill
  --skip-skills        Clone the repos, but don't install any agent skills
  --skip-doctor        Don't run the post-install diagnostics
  --skip-whisperx      Don't install the WhisperX transcript engine
  -h, --help           Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-hyperframes) SKIP_HYPERFRAMES=true ;;
    --skip-premiere)    SKIP_PREMIERE=true ;;
    --skip-watch)       SKIP_WATCH=true ;;
    --skip-skills)      SKIP_SKILLS=true ;;
    --skip-doctor)      SKIP_DOCTOR=true ;;
    --skip-whisperx)    SKIP_WHISPERX=true ;;
    -h|--help)          usage; exit 0 ;;
    *)                  usage; die "Unknown option: $1" ;;
  esac
  shift
done

printf '%s\n' "$BOLD"
cat <<'EOF'
  ┌──────────────────────────────────────────────┐
  │  VIBE EDITOR — setup                         │
  │  HyperFrames · Premiere Pro MCP · /watch     │
  └──────────────────────────────────────────────┘
EOF
printf '%s' "$RESET"

# -------------------------------------------------------------- preflight ---

step "Checking prerequisites"

[[ "$(uname -s)" == "Darwin" ]] || die "This script is for macOS. Use scripts/setup-windows.ps1 on Windows."

command -v git >/dev/null 2>&1 || die "git is required. Install Xcode Command Line Tools: xcode-select --install"
ok "git $(git --version | awk '{print $3}')"

command -v node >/dev/null 2>&1 || die "Node.js 22+ is required. Install it from https://nodejs.org or with: brew install node"
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
if [[ "$NODE_MAJOR" -lt 22 ]]; then
  die "Node.js 22+ is required (HyperFrames needs 22, Premiere MCP needs 20). Found $(node -v)."
fi
ok "node $(node -v)"

command -v npm >/dev/null 2>&1 || die "npm is required and ships with Node.js."
ok "npm $(npm -v)"

if command -v ffmpeg >/dev/null 2>&1; then
  ok "ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}')"
else
  warn "ffmpeg not found — HyperFrames cannot encode video without it."
  note "Install with: brew install ffmpeg"
fi

# /watch runs bundled Python and pulls video with yt-dlp. Neither is fatal here:
# the skill's own preflight installs yt-dlp on first run.
if [[ "$SKIP_WATCH" == false ]]; then
  if command -v python3 >/dev/null 2>&1; then
    ok "python3 $(python3 -c 'import platform; print(platform.python_version())')"
  else
    warn "python3 not found — /watch cannot run without it."
    note "Install Xcode Command Line Tools: xcode-select --install"
  fi

  if command -v yt-dlp >/dev/null 2>&1; then
    ok "yt-dlp $(yt-dlp --version 2>/dev/null)"
  else
    warn "yt-dlp not found — /watch installs it on first run."
    note "Or install it now with: brew install yt-dlp"
  fi
fi

# bash 3.2 (macOS default) has no negative array subscripts, so walk the glob.
PREMIERE_APP=""
for candidate in /Applications/Adobe\ Premiere\ Pro*; do
  [[ -d "$candidate" ]] && PREMIERE_APP="$candidate"
done
if [[ -n "$PREMIERE_APP" ]]; then
  ok "Adobe Premiere Pro found ($(basename "$PREMIERE_APP"))"
else
  warn "Adobe Premiere Pro not found in /Applications."
  note "The MCP bridge installs fine now, but Premiere 2020+ must be installed to edit."
fi

mkdir -p "$VENDOR_DIR"
cd "$REPO_ROOT"

# ------------------------------------------------------------- hyperframes --

clone_or_update() {
  local dir="$1" repo="$2" name="$3"
  if [[ -d "$dir/.git" ]]; then
    ok "$name already cloned — updating"
    # A failed update is not fatal: the existing clone still works.
    if git -C "$dir" fetch --depth 1 origin HEAD >/dev/null 2>&1 \
      && git -C "$dir" reset --hard FETCH_HEAD >/dev/null 2>&1; then
      ok "$name at $(git -C "$dir" rev-parse --short HEAD)"
    else
      warn "Could not update $name — keeping the existing clone at $(git -C "$dir" rev-parse --short HEAD)"
    fi
  else
    rm -rf "$dir"
    git clone --depth 1 "$repo" "$dir" >/dev/null 2>&1 || die "Failed to clone $repo"
    ok "$name cloned to vendor/$(basename "$dir")"
  fi
}

if [[ "$SKIP_HYPERFRAMES" == false ]]; then
  step "Installing HyperFrames (motion graphics engine)"
  clone_or_update "$HF_DIR" "$HF_REPO" "HyperFrames"

  if [[ "$SKIP_SKILLS" == false ]]; then
    note "Installing the HyperFrames core skill set for your agent…"
    if npx -y hyperframes@latest skills update; then
      ok "HyperFrames skills installed (~/.claude/skills)"
      note "The /hyperframes router installs creation workflows on demand."
    else
      warn "Skill install failed — run it manually: npx hyperframes skills update"
    fi
  fi
else
  step "Skipping HyperFrames"
fi

# ------------------------------------------------------------ premiere mcp --

if [[ "$SKIP_PREMIERE" == false ]]; then
  step "Installing the Premiere Pro MCP bridge (editing engine)"
  clone_or_update "$PP_DIR" "$PP_REPO" "Premiere Pro MCP"

  note "Building the MCP server and installing the CEP panel…"
  note "This runs the upstream installer: npm install, npm run build, CEP install,"
  note "Adobe CEP debug mode, and Claude Desktop MCP config."
  ( cd "$PP_DIR" && npm run setup:mac ) || die "Premiere MCP install failed. See the output above."

  [[ -f "$PP_DIR/dist/index.js" ]] || die "Build finished but $PP_DIR/dist/index.js is missing."
  ok "MCP server built"

  mkdir -p "$BRIDGE_DIR"
  ok "Bridge directory ready: $BRIDGE_DIR"

  if [[ "$SKIP_SKILLS" == false ]]; then
    note "Installing the Premiere Pro MCP agent skill…"
    if npx -y skills add hetpatel-11/Adobe_Premiere_Pro_MCP --skill premiere-pro-mcp; then
      ok "premiere-pro-mcp skill installed"
    else
      warn "Skill install failed — the MCP still works; retry with:"
      note "npx skills add hetpatel-11/Adobe_Premiere_Pro_MCP --skill premiere-pro-mcp"
    fi
  fi

  # Register the server for this project so any MCP client opened here finds it.
  step "Registering the MCP server for this project"
  MCP_JSON="$REPO_ROOT/.mcp.json" \
  SERVER_ENTRY="$PP_DIR/dist/index.js" \
  BRIDGE_PATH="$BRIDGE_DIR" \
  node <<'NODE'
const fs = require('node:fs');

const target = process.env.MCP_JSON;
const entry = process.env.SERVER_ENTRY;
const bridge = process.env.BRIDGE_PATH;

let config = {};
if (fs.existsSync(target)) {
  const raw = fs.readFileSync(target, 'utf8').trim();
  if (raw) {
    try {
      config = JSON.parse(raw);
    } catch {
      const backup = `${target}.bak`;
      fs.copyFileSync(target, backup);
      console.log(`  ! .mcp.json was not valid JSON — backed up to ${backup}`);
      config = {};
    }
  }
}

config.mcpServers = config.mcpServers ?? {};
config.mcpServers['premiere-pro'] = {
  command: 'node',
  args: [entry],
  env: { PREMIERE_TEMP_DIR: bridge },
};

fs.writeFileSync(target, `${JSON.stringify(config, null, 2)}\n`);
console.log('  ✓ .mcp.json updated with the "premiere-pro" server');
NODE
else
  step "Skipping the Premiere Pro MCP bridge"
fi

# ------------------------------------------------------------ claude video --

if [[ "$SKIP_WATCH" == false ]]; then
  step "Installing Claude Video (/watch — the agent's eyes)"
  clone_or_update "$CV_DIR" "$CV_REPO" "Claude Video"
  note "Reference reels in samples/ and your own rushes become readable footage."

  if [[ "$SKIP_SKILLS" == false ]]; then
    note "Installing the /watch agent skill…"
    if npx -y skills add bradautomates/claude-video --skill watch; then
      ok "watch skill installed"
    else
      warn "Skill install failed — retry with:"
      note "npx skills add bradautomates/claude-video --skill watch"
    fi
  fi

  note "Captions are free and cover most videos. For clips without them, add"
  note "GROQ_API_KEY (or OPENAI_API_KEY) to ~/.config/watch/.env for Whisper."
else
  step "Skipping Claude Video"
fi

# ------------------------------------------------------------- workspace ----

step "Preparing the workspace"
mkdir -p "$REPO_ROOT/projects" "$REPO_ROOT/exports"
[[ -f "$REPO_ROOT/projects/.keep" ]] || touch "$REPO_ROOT/projects/.keep"
ok "projects/ and exports/ ready"
ok "House-style skills live in .claude/skills/ and load automatically here"

# ------------------------------------------------------------------ brand ----

step "Setting up your brand"

# Creates brand/brand.json and brand/BRAND.md if they are missing; existing files
# are never touched, so this is safe on every re-run.
node "$REPO_ROOT/scripts/brand.mjs" scaffold ||
  warn "Could not create brand/ — run it manually: node scripts/brand.mjs scaffold"

if node "$REPO_ROOT/scripts/brand.mjs" build; then
  ok "brand/tokens.css built from brand/brand.json"
else
  warn "Brand build failed — fix brand/brand.json, then: node scripts/brand.mjs build"
fi
note "Make it yours:  node scripts/brand.mjs init   (colours, fonts, fps)"
note "Then edit brand/BRAND.md for voice, banned visuals, and CTA."

# -------------------------------------------------------------- whisperx ----
# The transcript engine (word-level forced alignment). Needs Python 3.11 + uv; ~3.5 GB of models
# download on first use. Skip with --skip-whisperx.
if [[ "${SKIP_WHISPERX:-false}" != "true" ]]; then
  if command -v uv >/dev/null 2>&1; then
    if [[ ! -x "$REPO_ROOT/.venv-whisperx/bin/whisperx" ]]; then
      info "Installing WhisperX into .venv-whisperx (Python 3.11)…"
      ( cd "$REPO_ROOT" && uv venv --python 3.11 .venv-whisperx >/dev/null && uv pip install --python .venv-whisperx/bin/python whisperx >/dev/null ) \
        && ok "WhisperX installed" || warn "WhisperX install failed — workflows/transcribe.py falls back to hyperframes transcribe"
    else
      ok "WhisperX present"
    fi
  else
    warn "uv not found (brew install uv) — WhisperX not installed; transcript falls back to whisper.cpp"
  fi
  command -v jq >/dev/null 2>&1 || warn "jq not found (brew install jq) — run.sh needs it"
  python3 -c "import cv2, numpy, jinja2" 2>/dev/null || warn "python3 needs opencv-python numpy jinja2 (pip3 install opencv-python numpy jinja2)"
fi

# ---------------------------------------------------------------- doctor ----

if [[ "$SKIP_DOCTOR" == false ]]; then
  step "Running diagnostics"
  if [[ "$SKIP_PREMIERE" == false ]]; then
    ( cd "$PP_DIR" && npm run setup:doctor ) || warn "Premiere doctor reported issues — see above."
  fi
  if [[ "$SKIP_HYPERFRAMES" == false ]]; then
    npx -y hyperframes@latest doctor || warn "HyperFrames doctor reported issues — see above."
  fi
  if [[ "$SKIP_WATCH" == false && -f "$CV_DIR/hooks/scripts/check-setup.sh" ]]; then
    # Claude Video ships no doctor; its session hook is the equivalent status line.
    bash "$CV_DIR/hooks/scripts/check-setup.sh" || warn "/watch setup check reported issues — see above."
  fi
fi

# ------------------------------------------------------------- next steps ---

cat <<EOF

${BOLD}Setup complete.${RESET} Three manual steps remain — only Premiere can do these.

  ${BOLD}1.${RESET} Restart Adobe Premiere Pro and open a project.
  ${BOLD}2.${RESET} Open ${CYAN}Window > Extensions > MCP Bridge (CEP)${RESET}.
  ${BOLD}3.${RESET} Set ${CYAN}Temp Directory${RESET} to ${BOLD}${BRIDGE_DIR}${RESET},
     click ${CYAN}Save Configuration${RESET}, then ${CYAN}Start Bridge${RESET}, then ${CYAN}Test Connection${RESET}.

If the panel is missing, enable ${CYAN}Preferences > Plugins > Enable developer mode${RESET}
and restart Premiere.

Then restart your agent in this folder and say:

  ${DIM}"Run verify_premiere_connection. Make no changes."${RESET}

When that returns your Premiere build and active sequence, you're live.

EOF
