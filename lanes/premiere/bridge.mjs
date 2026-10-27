// Premiere lane — the one MCP client every lane script imports.
// Spawns vendor/adobe-premiere-pro-mcp over stdio and speaks JSON-RPC 2.0 (MCP) with no SDK dependency.
//
//   import { Bridge } from "./bridge.mjs";
//   const b = await Bridge.connect();          // exits 2 with the bridge checklist if Premiere is unreachable
//   const seq = await b.call("get_active_sequence", {});
//   await b.close();
//
// Every call returns the tool's parsed JSON result. A tool returning success is NOT verification —
// callers read state back (get_clip_properties, list_sequence_tracks) and check files on disk.

import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
export const REPO = resolve(HERE, "..", "..");

const BRIDGE_CHECKLIST = `Premiere bridge is down. In Premiere: open a project → Window → Extensions → MCP Bridge (CEP) →
Temp Directory = the PREMIERE_TEMP_DIR in .mcp.json → Save Configuration → Start Bridge → Test Connection.
Then re-run. (run.sh falls back to --lane ffmpeg automatically.)`;

function serverConfig() {
  const mcp = join(REPO, ".mcp.json");
  if (existsSync(mcp)) {
    const cfg = JSON.parse(readFileSync(mcp, "utf8"));
    const s = cfg.mcpServers?.["premiere-pro"];
    if (s) return { command: s.command, args: s.args, env: { ...process.env, ...(s.env || {}) } };
  }
  return {
    command: "node",
    args: [join(REPO, "vendor", "adobe-premiere-pro-mcp", "dist", "index.js")],
    env: { ...process.env, PREMIERE_TEMP_DIR: process.env.PREMIERE_TEMP_DIR || "/tmp/premiere-mcp-bridge" },
  };
}

export class Bridge {
  constructor(proc) {
    this.proc = proc;
    this.id = 0;
    this.pending = new Map();
    this.buf = "";
    proc.stdout.on("data", (d) => this._onData(d.toString()));
    proc.stderr.on("data", (d) => { if (process.env.BRIDGE_DEBUG) process.stderr.write(d); });
    proc.on("exit", (code) => {
      for (const [, p] of this.pending) p.reject(new Error(`mcp server exited (${code})`));
      this.pending.clear();
    });
  }

  static async connect({ verify = true, timeoutMs = 20000 } = {}) {
    const cfg = serverConfig();
    const proc = spawn(cfg.command, cfg.args, { env: cfg.env, stdio: ["pipe", "pipe", "pipe"] });
    const b = new Bridge(proc);
    await b._rpc("initialize", {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "vibe-editor-lane", version: "1.0" },
    }, timeoutMs);
    b._notify("notifications/initialized", {});
    if (verify) {
      let ok = false, detail = "";
      try {
        const r = await b.call("verify_premiere_connection", {}, timeoutMs);
        ok = r && (r.connected === true || r.success === true || r.status === "connected" || r.ok === true);
        detail = JSON.stringify(r).slice(0, 400);
      } catch (e) { detail = String(e.message || e); }
      if (!ok) {
        // verify_premiere_connection keys on bridge-heartbeat.json, which a panel running pre-1.2.8 JavaScript in
        // memory never writes — while commands still round-trip. The real probe is a read-back, never a flag.
        try {
          const r = await b.call("list_sequences", {}, timeoutMs);
          ok = Array.isArray(r?.sequences);
          if (ok) console.error("bridge: verify_premiere_connection failed but list_sequences answered — reload the MCP Bridge panel when convenient");
        } catch (e) { detail += " | list_sequences: " + String(e.message || e); }
      }
      if (!ok) {
        await b.close();
        console.error(BRIDGE_CHECKLIST);
        console.error("detail:", detail);
        process.exit(2);
      }
    }
    return b;
  }

  _onData(chunk) {
    this.buf += chunk;
    let nl;
    while ((nl = this.buf.indexOf("\n")) >= 0) {
      const line = this.buf.slice(0, nl).trim();
      this.buf = this.buf.slice(nl + 1);
      if (!line.startsWith("{")) continue;
      let msg;
      try { msg = JSON.parse(line); } catch { continue; }
      if (msg.id !== undefined && this.pending.has(msg.id)) {
        const p = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        clearTimeout(p.timer);
        msg.error ? p.reject(new Error(msg.error.message || JSON.stringify(msg.error))) : p.resolve(msg.result);
      }
    }
  }

  _send(obj) { this.proc.stdin.write(JSON.stringify(obj) + "\n"); }
  _notify(method, params) { this._send({ jsonrpc: "2.0", method, params }); }

  _rpc(method, params, timeoutMs = 60000) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`${method} timed out after ${timeoutMs}ms`)); }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this._send({ jsonrpc: "2.0", id, method, params });
    });
  }

  async listTools() {
    const r = await this._rpc("tools/list", {});
    return (r.tools || []).map((t) => t.name);
  }

  /** Call a tool; returns parsed JSON from its first text content block (or the raw content). */
  async call(name, args = {}, timeoutMs = 120000) {
    const r = await this._rpc("tools/call", { name, arguments: args }, timeoutMs);
    const text = (r.content || []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
    if (r.isError) throw new Error(`${name}: ${text.slice(0, 800)}`);
    let parsed;
    try { parsed = JSON.parse(text); } catch { return { text }; }
    // server ≥ 1.2 wraps results as {success, tool, data:{…}}; lane scripts read the flat shape
    if (parsed && typeof parsed === "object" && parsed.tool && parsed.data && typeof parsed.data === "object" && !Array.isArray(parsed.data)) {
      return { success: parsed.success, ...parsed.data };
    }
    return parsed;
  }

  async close() {
    try { this.proc.stdin.end(); } catch {}
    await new Promise((r) => setTimeout(r, 100));
    try { this.proc.kill(); } catch {}
  }
}

export function readJob(jobDir) {
  const text = readFileSync(join(jobDir, "RUN.md"), "utf8").replace(/\r\n/g, "\n");
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  const state = {};
  for (const line of (m ? m[1] : "").split("\n")) {
    const mm = line.match(/^(\w+):\s*(.+)$/);
    if (mm) state[mm[1]] = mm[2].replace(/^"|"$/g, "");
  }
  return state;
}

/** numbers.json of the job's vertical preset, following `extends` (the same merge as workflows/_lib.load_numbers). */
export function readNumbers(preset = "vertical/default") {
  const d = JSON.parse(readFileSync(join(REPO, "presets", preset, "numbers.json"), "utf8"));
  const parent = d.extends;
  delete d.extends;
  if (!parent || parent === preset) return d;
  const merge = (a, b) => { const o = { ...a }; for (const [k, v] of Object.entries(b)) o[k] = (v && typeof v === "object" && !Array.isArray(v) && o[k] && typeof o[k] === "object") ? merge(o[k], v) : v; return o; };
  return merge(readNumbers(parent), d);
}
