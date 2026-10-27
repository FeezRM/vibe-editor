#!/usr/bin/env node
// Premiere lane — adopt the creator's OWN cut as the job's EDL.
//
//   node lanes/premiere/import-edl.mjs <job-dir> --sequence "<name>"
//
// Reads V1 of that sequence (source in/out per clip, in the raw's own time — the job's raw must be the same
// footage, e.g. the camera file with a lav muxed in), writes cuts.json with those keep ranges, marks rough_cut
// done, and validates. From there the pipeline runs as usual (`run.sh --from captions`), and place-layers.mjs
// --sequence "<name>__GFX" puts the layers on a duplicate of the creator's sequence (duplicate_sequence with
// clearContents:false keeps their grade, audio chain and framing). Use it when the creator prefers their cut.

import { readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { Bridge, readJob } from "./bridge.mjs";

const argv = process.argv.slice(2);
const si = argv.indexOf("--sequence");
if (si < 0 || !argv[si + 1]) { console.error('usage: import-edl.mjs <job-dir> --sequence "<name>"'); process.exit(64); }
const seqName = argv[si + 1];
const jobDir = resolve(argv.find((a, i) => !a.startsWith("--") && i !== si + 1) || ".");
const state = readJob(jobDir);
const fps = Number(state.fps || 30);
const duration = Number(state.source_duration_s);

const b = await Bridge.connect();
try {
  const seq = ((await b.call("list_sequences", {})).sequences || []).find((s) => s.name === seqName);
  if (!seq) throw new Error(`sequence "${seqName}" not found`);
  const t = await b.call("list_sequence_tracks", { sequenceId: seq.id });
  const v1 = ((t.videoTracks || [])[0] || {}).clips || [];
  const keep = [];
  for (const c of v1) {
    const p = (await b.call("get_clip_properties", { clipId: c.id, sequenceId: seq.id })).properties;
    keep.push({ in: +p.inPoint.toFixed(3), out: +p.outPoint.toFixed(3), reason: `creator's cut: ${seqName}`, lead_s: 0.08, start: +p.start.toFixed(3) });
  }
  keep.sort((a, b2) => a.start - b2.start);
  // the timeline must be contiguous for the EDL model (timeline time = running sum of keeps)
  let run = 0, gaps = 0;
  for (const k of keep) { if (Math.abs(k.start - run) > 1.5 / fps) gaps++; run += k.out - k.in; delete k.start; }
  if (gaps) throw new Error(`${gaps} clip(s) do not start where the previous ends — close the gaps in "${seqName}" first`);
  const removed = [];
  let cur = 0;
  for (const k of keep) { if (k.in > cur + 1e-6) removed.push({ in: +cur.toFixed(3), out: k.in, reason: "not in the creator's cut" }); cur = k.out; }
  if (cur < duration - 1e-6) removed.push({ in: +cur.toFixed(3), out: duration, reason: "silence:tail" });
  const kept = keep.reduce((s, k) => s + k.out - k.in, 0);
  const cuts = { source: state.source, fps, source_duration_s: duration, keep, removed, removal_ids: [],
                 stats: { kept_s: +kept.toFixed(3), removed_s: +(duration - kept).toFixed(3), clips: keep.length, mean_clip_s: +(kept / keep.length).toFixed(3) },
                 provenance: `Premiere sequence "${seqName}" (${seq.id}) V1, read back ${new Date().toISOString().slice(0, 10)}` };
  writeFileSync(join(jobDir, "cuts.json"), JSON.stringify(cuts, null, 2));
  const py = spawnSync("python3", ["-c", `import sys; sys.path.insert(0, "workflows"); from _lib import Job\nj = Job(sys.argv[1]); j.mark("rough_cut", "done", out="cuts.json", kept_s=${kept.toFixed(2)}, cut_s=${(duration - kept).toFixed(2)}, clips=${keep.length}); j.note("rough_cut", "EDL adopted from Premiere sequence '${seqName}' (${keep.length} clips) - not computed")`, jobDir],
                       { cwd: resolve(jobDir, "..", ".."), encoding: "utf8", env: { ...process.env, PYTHONUTF8: "1" } });
  if (py.status !== 0) throw new Error(py.stderr);
  const v = spawnSync("python3", ["workflows/validate-edl.py", jobDir], { cwd: resolve(jobDir, "..", ".."), encoding: "utf8", env: { ...process.env, PYTHONUTF8: "1" } });
  process.stdout.write(v.stdout);
  if (v.status !== 0) { process.stderr.write(v.stderr); process.exit(1); }
  console.log(`import-edl: ${keep.length} clips · ${kept.toFixed(2)}s from "${seqName}" → cuts.json`);
} finally {
  await b.close();
}
