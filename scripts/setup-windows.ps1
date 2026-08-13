<#
.SYNOPSIS
    Vibe Editor - Windows setup.

.DESCRIPTION
    Installs the two engines the agent drives:
      1. HyperFrames      - HTML -> deterministic video, for motion graphics
      2. Premiere Pro MCP - 283 MCP tools that drive a local Premiere Pro

    Idempotent. Safe to re-run to update both engines.

.PARAMETER SkipHyperframes
    Do not clone HyperFrames or install its skills.

.PARAMETER SkipPremiere
    Do not clone or build the Premiere Pro MCP bridge.

.PARAMETER SkipSkills
    Clone the repos, but do not install any agent skills.

.PARAMETER SkipDoctor
    Do not run the post-install diagnostics.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
#>

[CmdletBinding()]
param(
    [switch] $SkipHyperframes,
    [switch] $SkipPremiere,
    [switch] $SkipSkills,
    [switch] $SkipDoctor
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot  = Split-Path -Parent $PSScriptRoot
$vendorDir = Join-Path $repoRoot 'vendor'
$hfDir     = Join-Path $vendorDir 'hyperframes'
$ppDir     = Join-Path $vendorDir 'adobe-premiere-pro-mcp'
$bridgeDir = Join-Path $env:TEMP 'premiere-mcp-bridge'

$hfRepo = 'https://github.com/heygen-com/hyperframes.git'
$ppRepo = 'https://github.com/hetpatel-11/adobe_premiere_pro_mcp.git'

# ---------------------------------------------------------------- output ----

function Write-Step { param([string] $Message) Write-Host ''; Write-Host "==> $Message" -ForegroundColor Cyan }
function Write-Ok   { param([string] $Message) Write-Host "  [ok] $Message" -ForegroundColor Green }
function Write-Warn { param([string] $Message) Write-Host "  [!]  $Message" -ForegroundColor Yellow }
function Write-Note { param([string] $Message) Write-Host "       $Message" -ForegroundColor DarkGray }

function Invoke-Checked {
    param([string] $Command, [string[]] $Arguments, [string] $WorkingDirectory = $repoRoot)

    $previous = Get-Location
    Set-Location $WorkingDirectory
    try {
        # Out-Host keeps child output off the pipeline so the boolean below is
        # the function's only return value.
        & $Command @Arguments | Out-Host
        return ($LASTEXITCODE -eq 0)
    } finally {
        Set-Location $previous
    }
}

Write-Host @'
  +----------------------------------------------+
  |  VIBE EDITOR - setup                         |
  |  HyperFrames . Adobe Premiere Pro MCP        |
  +----------------------------------------------+
'@ -ForegroundColor White

# -------------------------------------------------------------- preflight ---

Write-Step 'Checking prerequisites'

if ($env:OS -ne 'Windows_NT') {
    throw 'This script is for Windows. Use scripts/setup-macos.sh on macOS.'
}

# npm and npx are batch shims on Windows; they must be invoked through cmd.
$npm = 'npm.cmd'
$npx = 'npx.cmd'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'git is required. Install it from https://git-scm.com/download/win or: winget install Git.Git'
}
Write-Ok "git $((git --version) -replace 'git version ', '')"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js 22+ is required. Install it from https://nodejs.org or: winget install OpenJS.NodeJS.LTS'
}
$nodeMajor = [int](node -p 'process.versions.node.split(".")[0]')
if ($nodeMajor -lt 22) {
    throw "Node.js 22+ is required (HyperFrames needs 22, Premiere MCP needs 20). Found $(node -v)."
}
Write-Ok "node $(node -v)"

if (-not (Get-Command $npm -ErrorAction SilentlyContinue)) {
    throw 'npm is required and ships with Node.js.'
}
Write-Ok "npm $(& $npm -v)"

if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Ok 'ffmpeg found'
} else {
    Write-Warn 'ffmpeg not found - HyperFrames cannot encode video without it.'
    Write-Note 'Install with: winget install Gyan.FFmpeg'
}

$premiereInstalls = @(Get-ChildItem -Path 'C:\Program Files\Adobe' -Filter 'Adobe Premiere Pro*' -Directory -ErrorAction SilentlyContinue)
if ($premiereInstalls.Count -gt 0) {
    Write-Ok "Adobe Premiere Pro found ($($premiereInstalls[-1].Name))"
} else {
    Write-Warn 'Adobe Premiere Pro not found under C:\Program Files\Adobe.'
    Write-Note 'The MCP bridge installs fine now, but Premiere 2020+ must be installed to edit.'
}

New-Item -ItemType Directory -Force -Path $vendorDir | Out-Null

# ----------------------------------------------------------------- clone ----

function Sync-Repo {
    param([string] $Directory, [string] $Repo, [string] $Name)

    if (Test-Path (Join-Path $Directory '.git')) {
        Write-Ok "$Name already cloned - updating"
        # A failed update is not fatal: the existing clone still works.
        git -C $Directory fetch --depth 1 origin HEAD *>$null
        if ($LASTEXITCODE -eq 0) {
            git -C $Directory reset --hard FETCH_HEAD *>$null
        }
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "$Name at $(git -C $Directory rev-parse --short HEAD)"
        } else {
            Write-Warn "Could not update $Name - keeping the existing clone at $(git -C $Directory rev-parse --short HEAD)"
        }
    } else {
        if (Test-Path $Directory) { Remove-Item -Recurse -Force $Directory }
        git clone --depth 1 $Repo $Directory *>$null
        if ($LASTEXITCODE -ne 0) { throw "Failed to clone $Repo" }
        Write-Ok "$Name cloned to vendor\$(Split-Path -Leaf $Directory)"
    }
}

# ------------------------------------------------------------- hyperframes --

if (-not $SkipHyperframes) {
    Write-Step 'Installing HyperFrames (motion graphics engine)'
    Sync-Repo -Directory $hfDir -Repo $hfRepo -Name 'HyperFrames'

    if (-not $SkipSkills) {
        Write-Note 'Installing the HyperFrames core skill set for your agent...'
        if (Invoke-Checked -Command $npx -Arguments @('-y', 'hyperframes@latest', 'skills', 'update')) {
            Write-Ok 'HyperFrames skills installed (~\.claude\skills)'
            Write-Note 'The /hyperframes router installs creation workflows on demand.'
        } else {
            Write-Warn 'Skill install failed - run it manually: npx hyperframes skills update'
        }
    }
} else {
    Write-Step 'Skipping HyperFrames'
}

# ------------------------------------------------------------ premiere mcp --

if (-not $SkipPremiere) {
    Write-Step 'Installing the Premiere Pro MCP bridge (editing engine)'
    Sync-Repo -Directory $ppDir -Repo $ppRepo -Name 'Premiere Pro MCP'

    Write-Note 'Building the MCP server and installing the CEP panel...'
    Write-Note 'This runs the upstream installer: npm install, npm run build, CEP install,'
    Write-Note 'Adobe CEP debug mode, and MCP config for Claude Desktop + Copilot in VS Code.'
    if (-not (Invoke-Checked -Command $npm -Arguments @('run', 'setup:win') -WorkingDirectory $ppDir)) {
        throw 'Premiere MCP install failed. See the output above.'
    }

    $serverEntry = Join-Path $ppDir 'dist\index.js'
    if (-not (Test-Path $serverEntry)) {
        throw "Build finished but $serverEntry is missing."
    }
    Write-Ok 'MCP server built'

    New-Item -ItemType Directory -Force -Path $bridgeDir | Out-Null
    Write-Ok "Bridge directory ready: $bridgeDir"

    if (-not $SkipSkills) {
        Write-Note 'Installing the Premiere Pro MCP agent skill...'
        if (Invoke-Checked -Command $npx -Arguments @('-y', 'skills', 'add', 'hetpatel-11/Adobe_Premiere_Pro_MCP', '--skill', 'premiere-pro-mcp')) {
            Write-Ok 'premiere-pro-mcp skill installed'
        } else {
            Write-Warn 'Skill install failed - the MCP still works; retry with:'
            Write-Note 'npx skills add hetpatel-11/Adobe_Premiere_Pro_MCP --skill premiere-pro-mcp'
        }
    }

    # Register the server for this project so any MCP client opened here finds it.
    Write-Step 'Registering the MCP server for this project'

    $mcpHelper = Join-Path $env:TEMP 'vibe-editor-mcp-config.cjs'
    @'
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
      console.log(`  [!]  .mcp.json was not valid JSON - backed up to ${backup}`);
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
console.log('  [ok] .mcp.json updated with the "premiere-pro" server');
'@ | Set-Content -Path $mcpHelper -Encoding ASCII

    $env:MCP_JSON = Join-Path $repoRoot '.mcp.json'
    $env:SERVER_ENTRY = $serverEntry
    $env:BRIDGE_PATH = $bridgeDir
    try {
        node $mcpHelper
        if ($LASTEXITCODE -ne 0) { throw 'Failed to write .mcp.json' }
    } finally {
        Remove-Item $mcpHelper -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Step 'Skipping the Premiere Pro MCP bridge'
}

# ------------------------------------------------------------- workspace ----

Write-Step 'Preparing the workspace'
New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot 'projects') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot 'exports')  | Out-Null
$keep = Join-Path $repoRoot 'projects\.keep'
if (-not (Test-Path $keep)) { New-Item -ItemType File -Path $keep | Out-Null }
Write-Ok 'projects\ and exports\ ready'
Write-Ok 'House-style skills live in .claude\skills\ and load automatically here'

# ------------------------------------------------------------------ brand ----

Write-Step 'Building brand tokens'
$brandCfg = Join-Path $repoRoot 'brand\brand.json'
if (Test-Path $brandCfg) {
    node (Join-Path $repoRoot 'scripts\brand.mjs') build | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Ok 'brand\tokens.css built from brand\brand.json'
    } else {
        Write-Warn 'Brand build failed - fix brand\brand.json, then: node scripts\brand.mjs build'
    }
    Write-Note 'Make it yours:  node scripts\brand.mjs init   (colours, fonts, fps)'
    Write-Note 'Then edit brand\BRAND.md for voice, banned visuals, and CTA.'
} else {
    Write-Warn 'brand\brand.json missing - run: node scripts\brand.mjs init'
}

# ---------------------------------------------------------------- doctor ----

if (-not $SkipDoctor) {
    Write-Step 'Running diagnostics'
    if (-not $SkipPremiere) {
        if (-not (Invoke-Checked -Command $npm -Arguments @('run', 'setup:doctor:win') -WorkingDirectory $ppDir)) {
            Write-Warn 'Premiere doctor reported issues - see above.'
        }
    }
    if (-not $SkipHyperframes) {
        if (-not (Invoke-Checked -Command $npx -Arguments @('-y', 'hyperframes@latest', 'doctor'))) {
            Write-Warn 'HyperFrames doctor reported issues - see above.'
        }
    }
}

# ------------------------------------------------------------- next steps ---

Write-Host ''
Write-Host 'Setup complete.' -ForegroundColor Green -NoNewline
Write-Host ' Three manual steps remain - only Premiere can do these.'
Write-Host ''
Write-Host '  1. Restart Adobe Premiere Pro and open a project.'
Write-Host '  2. Open Window > Extensions > MCP Bridge (CEP).'
Write-Host "  3. Set Temp Directory to $bridgeDir,"
Write-Host '     click Save Configuration, then Start Bridge, then Test Connection.'
Write-Host ''
Write-Host 'Then restart your agent in this folder and say:'
Write-Host ''
Write-Host '    "Run verify_premiere_connection. Make no changes."' -ForegroundColor DarkGray
Write-Host ''
Write-Host "When that returns your Premiere build and active sequence, you're live."
Write-Host ''
