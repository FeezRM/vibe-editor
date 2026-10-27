#!/usr/bin/env node
// Premiere lane — export the job's sequence to a file, then prove the file exists and is fresh.
//   node lanes/premiere/export.mjs <job-dir> <out.mp4>
// Exit 1 on any failure so finalize.sh falls back to the ffmpeg lane. Never trust the tool's success flag.
import { existsSync, statSync, readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { Bridge, readJob } from "./bridge.mjs";

const jobDir = resolve(process.argv[2] || ".");
const out = resolve(process.argv[3] || join(jobDir, "outputs", "final.mp4"));
const state = readJob(jobDir);
const verify = JSON.parse(readFileSync(join(jobDir, "premiere", "replay-verify.json"), "utf8"));
// encodeSequence needs an absolute .epr: PREMIERE_EXPORT_PRESET, else AME's own H.264 "Match Source - High bitrate"
const findPreset = () => {
  if (process.env.PREMIERE_EXPORT_PRESET) return process.env.PREMIERE_EXPORT_PRESET;
  const roots = ["C:/Program Files/Adobe", "/Applications"];
  for (const root of roots) {
    if (!existsSync(root)) continue;
    for (const app of readdirSync(root).filter((d) => /Media Encoder/i.test(d)).sort().reverse()) {
      for (const dir of [`${root}/${app}/MediaIO/systempresets/4E49434B_48323634`, `${root}/${app}/Contents/MediaIO/systempresets/4E49434B_48323634`]) {
        const f = `${dir}/01 - Match Source - High bitrate.epr`;
        if (existsSync(f)) return f;
      }
    }
  }
  return null;
};
const presetPath = findPreset();
const t0 = Date.now() / 1000;
const b = await Bridge.connect();
try {
  const r = await b.call("export_sequence", { sequenceId: verify.sequenceId, outputPath: out.replace(/\\/g, "/"), allowOverwrite: true, ...(presetPath ? { presetPath } : {}) }, 1800000);
  const fresh = existsSync(out) && statSync(out).mtimeMs / 1000 >= t0 - 1;
  console.log(`export_sequence said ${JSON.stringify(r).slice(0, 120)} · on disk: ${fresh}`);
  process.exit(fresh ? 0 : 1);
} finally {
  await b.close();
}
