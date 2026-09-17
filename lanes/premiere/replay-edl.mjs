#!/usr/bin/env node
// Premiere lane — replay cuts.json onto a fresh sequence as separate, trimmable clips. Never a flat render.
//
//   node lanes/premiere/replay-edl.mjs <job-dir>
//
// Creates <job>__CUT (sequence from the raw clip, so it inherits 1080x1920 and the source fps),
// lifts the auto-placed full clip, places every keep range with add_to_timeline_batch, then reads
// every clip back with get_clip_properties and writes premiere/replay-verify.json. The gate is the
// read-back, not the tool's success flag.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { Bridge, readJob } from "./bridge.mjs";

const jobDir = resolve(process.argv[2] || ".");
const state = readJob(jobDir);
const cuts = JSON.parse(readFileSync(join(jobDir, "cuts.json"), "utf8"));
const rawPath = resolve(jobDir, state.source);
const seqName = `${state.job}__CUT`;

const b = await Bridge.connect();
try {
  // 1. import the raw (idempotent: find first)
  let item = null;
  const found = await b.call("find_project_item_by_name", { name: rawPath.split("/").pop() }).catch(() => null);
  const hits = found?.items || found?.results || (Array.isArray(found) ? found : []);
  if (hits.length) item = hits[0];
  if (!item) {
    const imp = await b.call("import_media", { filePath: rawPath });
    item = imp.item || imp.projectItem || imp;
  }
  const itemId = item.id || item.projectItemId || item.nodeId;
  if (!itemId) throw new Error(`could not resolve project item id from ${JSON.stringify(item).slice(0, 300)}`);

  // 2. sequence that matches the source
  const created = await b.call("create_sequence_from_clips", { name: seqName, projectItemIds: [itemId] });
  const sequenceId = created.sequenceId;
  if (!sequenceId) throw new Error(`no sequenceId: ${JSON.stringify(created).slice(0, 300)}`);
  await b.call("set_active_sequence", { sequenceId }).catch(() => {});

  // 3. lift the auto-placed full clip(s)
  const tracks = await b.call("list_sequence_tracks", { sequenceId });
  const allClips = [];
  for (const t of [...(tracks.videoTracks || tracks.video || []), ...(tracks.audioTracks || tracks.audio || [])]) {
    for (const c of t.clips || []) allClips.push(c);
  }
  for (const c of allClips) {
    await b.call("remove_from_timeline", { clipId: c.id || c.clipId, sequenceId, deleteMode: "lift" }).catch(() => {});
  }

  // 4. track architecture: V1 A-roll · V2 B-roll · V3 primary gfx · V4 secondary · A1 voice · A2 alt · A3/A4 sfx · A5 music
  const want = { video: 4, audio: 5 };
  const have = { video: (tracks.videoTracks || tracks.video || []).length, audio: (tracks.audioTracks || tracks.audio || []).length };
  for (const kind of ["video", "audio"]) {
    for (let i = have[kind]; i < want[kind]; i++) await b.call("add_track", { sequenceId, trackType: kind });
  }

  // 5. place every keep range as its own clip
  let t = 0;
  const clips = cuts.keep.map((k) => {
    const c = { projectItemId: itemId, trackIndex: 0, time: +t.toFixed(3), sourceInPoint: k.in, sourceOutPoint: k.out };
    t += k.out - k.in;
    return c;
  });
  const placed = await b.call("add_to_timeline_batch", { sequenceId, clips }, 300000);

  // 6. read back — the gate
  const after = await b.call("list_sequence_tracks", { sequenceId });
  const v1 = (after.videoTracks || after.video || [])[0] || {};
  const readback = [];
  for (const c of v1.clips || []) {
    const p = await b.call("get_clip_properties", { clipId: c.id || c.clipId, sequenceId }).catch(() => c);
    readback.push({ id: c.id || c.clipId, start: p.start ?? p.startTime ?? c.start, end: p.end ?? p.endTime ?? c.end,
                    inPoint: p.inPoint ?? p.sourceIn, outPoint: p.outPoint ?? p.sourceOut });
  }
  const fps = Number(state.fps || 30);
  const tol = 1.5 / fps;
  let mismatches = 0;
  cuts.keep.forEach((k, i) => {
    const r = readback[i];
    if (!r) { mismatches++; return; }
    const expStart = cuts.keep.slice(0, i).reduce((s, x) => s + (x.out - x.in), 0);
    if (Math.abs((r.start ?? 0) - expStart) > tol) mismatches++;
  });
  mkdirSync(join(jobDir, "premiere"), { recursive: true });
  const verify = { sequenceId, sequenceName: seqName, expected: cuts.keep.length, placed: readback.length, mismatches,
                   placedResult: placed?.status || placed?.success, readback };
  writeFileSync(join(jobDir, "premiere", "replay-verify.json"), JSON.stringify(verify, null, 2));
  console.log(`replay-edl: ${readback.length}/${cuts.keep.length} clips on ${seqName}, ${mismatches} mismatches → premiere/replay-verify.json`);
  if (readback.length !== cuts.keep.length || mismatches) process.exit(1);
} finally {
  await b.close();
}
