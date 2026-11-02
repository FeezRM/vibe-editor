#!/usr/bin/env node
// Premiere lane — replay cuts.json onto a fresh sequence as separate, trimmable clips. Never a flat render.
//
//   node lanes/premiere/replay-edl.mjs <job-dir>
//
// Creates <job>__CUT (sequence from the raw clip, so it inherits 1080x1920 and the source fps),
// lifts the auto-placed full clip, places every keep range with add_to_timeline_batch, then reads
// every clip back with get_clip_properties and writes premiere/replay-verify.json. The gate is the
// read-back, not the tool's success flag.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, resolve, basename } from "node:path";
import { Bridge, readJob, readNumbers } from "./bridge.mjs";

const jobDir = resolve(process.argv[2] || ".");
const state = readJob(jobDir);
const cuts = JSON.parse(readFileSync(join(jobDir, "cuts.json"), "utf8"));
const rawPath = resolve(jobDir, state.source);
const seqName = `${state.job}__CUT`;
const canvas = readNumbers(state.preset || "vertical/default").canvas;
const fps = Number(state.fps || canvas.fps || 30);
// lav.json: the untouched lav recording ({file, offset}: video_time = wav_time + offset). Then V1 carries picture only
// and A1 is the WAV itself, cut to the same ranges — no re-encode, no gain (the creator finishes the sound in Premiere)
const lav = existsSync(join(jobDir, "lav.json")) ? JSON.parse(readFileSync(join(jobDir, "lav.json"), "utf8")) : null;

const b = await Bridge.connect();
try {
  // 1. import the raw (idempotent: find first)
  let item = null;
  const found = await b.call("find_project_item_by_name", { name: rawPath.split(/[\/]/).pop() }).catch(() => null);
  const hits = found?.items || found?.results || (Array.isArray(found) ? found : []);
  if (hits.length) item = hits[0];
  if (!item) {
    const imp = await b.call("import_media", { filePath: rawPath });
    item = imp.item || imp.projectItem || imp;
  }
  const itemId = item.id || item.projectItemId || item.nodeId;
  if (!itemId) throw new Error(`could not resolve project item id from ${JSON.stringify(item).slice(0, 300)}`);

  // 2. sequence that matches the source (reuse an existing <job>__CUT: its clips are lifted in step 3)
  const existing = ((await b.call("list_sequences", {}).catch(() => ({}))).sequences || []).find((s) => s.name === seqName);
  const created = existing ? { sequenceId: existing.id }
                           : await b.call("create_sequence_from_clips", { name: seqName, projectItemIds: [itemId] });
  const sequenceId = created.sequenceId;
  if (!sequenceId) throw new Error(`no sequenceId: ${JSON.stringify(created).slice(0, 300)}`);
  await b.call("set_active_sequence", { sequenceId }).catch(() => {});
  // the canvas is the preset's, not the raw's (a 4K vertical source must land on a 1080x1920 sequence; Premiere re-fits the A-roll)
  await b.call("set_sequence_settings", { sequenceId, settings: { width: canvas.width, height: canvas.height, frameRate: fps } }).catch(() => {});
  const ss = await b.call("get_sequence_settings", { sequenceId }).catch(() => ({}));
  const sz = ss.settings || ss;
  const gotW = sz.width ?? sz.frameWidth ?? sz.videoFrameWidth, gotH = sz.height ?? sz.frameHeight ?? sz.videoFrameHeight;
  if (gotW && gotH && (gotW !== canvas.width || gotH !== canvas.height)) throw new Error(`sequence is ${gotW}x${gotH}, preset canvas is ${canvas.width}x${canvas.height}`);

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
  // Sequential, not one batch: a computed start such as 574/30 can land one frame late (a black flash), while the
  // end Premiere itself reports for the previous clip round-trips exactly. Source in/out are frame-quantised.
  const expected = [], expectedEnd = [], holdsPlaced = [];
  let frames = 0, next = 0, placed = { status: "success" };
  for (const k of cuts.keep) {
    const fin = Math.round(k.in * fps), fout = Math.round(k.out * fps);
    expected.push(frames / fps);
    const r = await b.call("add_to_timeline_batch", { sequenceId, clips: [
      { projectItemId: itemId, trackIndex: 0, time: next, linkAudio: !lav, sourceInPoint: fin / fps, sourceOutPoint: fout / fps }] }, 120000);
    if (r?.success === false) { placed = r; break; }
    frames += fout - fin;
    const now = await b.call("list_sequence_tracks", { sequenceId });
    const v1now = ((now.videoTracks || now.video || [])[0] || {}).clips || [];
    const last = v1now[v1now.length - 1];
    next = last?.endTime ?? last?.end ?? frames / fps;
    // a hold (cuts.json keep.hold): the keep's last frame as its own clip — Premiere has no scriptable frame hold,
    // so the frame is rendered to premiere/holds/hold-<in>.mp4 (source size, video only) and placed after the keep
    if (k.hold) {
      const hf = Math.round(k.hold * fps);
      const hp = join(jobDir, "premiere", "holds", `hold-${k.in.toFixed(2)}-${hf}f-pad3.mp4`);
      mkdirSync(join(jobDir, "premiere", "holds"), { recursive: true });
      if (!existsSync(hp)) {
        const r = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-ss", ((fout - 1) / fps).toFixed(4), "-i", rawPath, "-frames:v", "1",
          "-f", "image2pipe", "-vcodec", "png", "-"], { maxBuffer: 1 << 28 });
        const r2 = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-i", "-", "-loop", "1", "-r", String(fps),
          "-frames:v", String(hf + 3), "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", hp], { input: r.stdout });
        if (r2.status !== 0 || !existsSync(hp)) throw new Error(`hold render failed: ${r2.stderr}`);
      }
      const hname = basename(hp);
      const hfound = await b.call("find_project_item_by_name", { name: hname }).catch(() => null);
      const hh = hfound?.items || hfound?.results || (Array.isArray(hfound) ? hfound : []);
      let hid = hh[0]?.id || hh[0]?.projectItemId || hh[0]?.nodeId;
      if (!hid) { const imp = await b.call("import_media", { filePath: hp }); const it = imp.item || imp.projectItem || imp; hid = it.id || it.projectItemId || it.nodeId; }
      const hr = await b.call("add_to_timeline_batch", { sequenceId, clips: [
        { projectItemId: hid, trackIndex: 0, time: next, linkAudio: false, sourceInPoint: 0, sourceOutPoint: (hf + 1) / fps }] }, 120000);
      if (hr?.success === false) { placed = hr; break; }   // out is hf+1: Premiere lays a short mp4 one frame short (9031) — the read-back below proves the length
      holdsPlaced.push({ name: hname, time: next, frames: hf });
      frames += hf;
      const nh = await b.call("list_sequence_tracks", { sequenceId });
      const v1h = ((nh.videoTracks || nh.video || [])[0] || {}).clips || [];
      next = v1h[v1h.length - 1]?.endTime ?? frames / fps;
    }
    expectedEnd.push(frames / fps);
  }

  // 5b. the lav on A1: one piece per V1 clip, same timeline span, source shifted by the offset
  let lavPlaced = null;
  if (lav) {
    const lname = lav.file.split(/[\/]/).pop();
    const lf = await b.call("find_project_item_by_name", { name: lname }).catch(() => null);
    const lh = lf?.items || lf?.results || (Array.isArray(lf) ? lf : []);
    let lid = lh[0]?.id || lh[0]?.projectItemId || lh[0]?.nodeId;
    if (!lid) { const imp = await b.call("import_media", { filePath: lav.file }); const it = imp.item || imp.projectItem || imp; lid = it.id || it.projectItemId || it.nodeId; }
    const v1now = ((await b.call("list_sequence_tracks", { sequenceId })).videoTracks || [])[0]?.clips || [];
    const pieces = cuts.keep.map((k, i) => {
      const c = v1now[i] || {};
      const start = c.startTime ?? c.start ?? expected[i], end = c.endTime ?? c.end ?? expectedEnd[i];
      const sin = Math.round(k.in * fps) / fps - lav.offset;
      return { projectItemId: lid, trackIndex: 0, time: start, sourceInPoint: +sin.toFixed(6), sourceOutPoint: +(sin + (end - start)).toFixed(6) };
    });
    const r = await b.call("add_to_timeline_batch", { sequenceId, clips: pieces }, 180000);
    const a1 = ((await b.call("list_sequence_tracks", { sequenceId })).audioTracks || [])[0]?.clips || [];
    lavPlaced = { requested: pieces.length, onA1: a1.length, status: r?.status ?? r?.success, file: lname, offset: lav.offset };
    if (a1.length !== pieces.length) throw new Error(`lav: ${a1.length}/${pieces.length} pieces on A1 — ${JSON.stringify(r).slice(0, 300)}`);
  }

  // 6. fit the A-roll: a source larger than the canvas lands at 100 % (a 2x punch-in on a 4K vertical). Premiere does
  //    not re-fit clips placed by script, so scale = canvas / source. motion.scale reads back as a boolean from this
  //    server, so the tool's `applied.scale` is recorded and the frame is checked on the program monitor, not here.
  const after = await b.call("list_sequence_tracks", { sequenceId });
  const v1 = (after.videoTracks || after.video || [])[0] || {};
  const srcW = Number(state.source_width || 0) || null;
  const readback = [];
  const holdNames = new Set(holdsPlaced.map((h) => h.name));
  const holdClips = (v1.clips || []).filter((c) => holdNames.has(c.name));
  // the ffmpeg lane's camera (preview/framing.json, written by assemble.py): one fixed crop on the median face, so the
  // sequence frames him exactly as the export does — Motion scale = fit × crop, position puts the crop's centre mid-frame
  const fr = existsSync(join(jobDir, "preview", "framing.json")) ? JSON.parse(readFileSync(join(jobDir, "preview", "framing.json"), "utf8")) : { scale: 1, left: 0, top: 0 };
  const S = fr.scale || 1;
  const fit = srcW ? canvas.width / srcW * 100 : 100;
  const cx = S > 1.0001 ? fr.left + 0.5 / S : 0.5, cy = S > 1.0001 ? fr.top + 0.5 / S : 0.5;
  const motion = (Z, px, py) => {     // scale Z (× fit) with source point (px,py) held where the base framing shows it
    const fx = canvas.width / 2 + (px - cx) * canvas.width * S, fy = canvas.height / 2 + (py - cy) * canvas.height * S;
    return { scale: +(fit * Z).toFixed(3), position: { x: +(fx + (0.5 - px) * canvas.width * Z).toFixed(2), y: +(fy + (0.5 - py) * canvas.height * Z).toFixed(2) } };
  };
  const base = motion(S, cx, cy);
  for (const c of (v1.clips || []).filter((c) => !holdNames.has(c.name))) {
    const r = await b.call("get_clip_properties", { clipId: c.id || c.clipId, sequenceId }).catch(() => ({}));
    const p = r.properties || r;
    let scaled = null;
    if (srcW && (srcW !== canvas.width || S > 1.0001)) {
      const sr = await b.call("set_clip_properties", { clipId: c.id || c.clipId, properties: base }).catch(() => ({}));
      scaled = sr?.applied?.scale ?? sr?.success ?? false;
    }
    readback.push({ id: c.id || c.clipId, start: p.start ?? p.startTime ?? c.startTime, end: p.end ?? p.endTime ?? c.endTime,
                    inPoint: p.inPoint ?? p.sourceIn, outPoint: p.outPoint ?? p.sourceOut, scaled });
  }
  // the opening zoom-out (pacing-audit --zoom-out-open): keyframes on the first clip, anchored on the face
  if (fr.open && (v1.clips || []).length) {
    const c0 = v1.clips[0], [px, py] = fr.open.face, Z0 = S * (1 + fr.open.pct / 100);
    const from = motion(Z0, px, py);
    for (const [t, m] of [[0, from], [fr.open.dur, base]]) {
      await b.call("add_keyframe", { clipId: c0.id || c0.clipId, componentName: "Motion", paramName: "Scale", time: t, value: m.scale }).catch((e) => console.error("keyframe", e.message));
      await b.call("add_keyframe", { clipId: c0.id || c0.clipId, componentName: "Motion", paramName: "Position", time: t,
                                     value: [m.position.x / canvas.width, m.position.y / canvas.height] }).catch((e) => console.error("keyframe", e.message));
    }
  }
  const tol = 1.5 / fps;
  let mismatches = 0;
  cuts.keep.forEach((k, i) => {
    const r = readback[i];
    if (!r) { mismatches++; return; }
    if (Math.abs((r.start ?? 0) - expected[i]) > tol) mismatches++;
    if (i > 0 && Math.abs(r.start - expectedEnd[i - 1]) > tol) mismatches++;   // a gap = a black flash (holds included)
    if (r.scaled === false) mismatches++;
  });
  mkdirSync(join(jobDir, "premiere"), { recursive: true });
  // holds: one still clip per keep.hold, scaled like the A-roll, ending where the next keep starts
  for (const h of holdsPlaced) {
    const c = holdClips.find((x) => x.name === h.name && Math.abs((x.startTime ?? x.start) - h.time) <= tol);
    if (!c) { mismatches++; continue; }
    if (srcW && srcW !== canvas.width) await b.call("set_clip_properties", { clipId: c.id || c.clipId, properties: base }).catch(() => {});
  }
  const verify = { sequenceId, sequenceName: seqName, lav: lavPlaced, expected: cuts.keep.length, placed: readback.length, holds: holdsPlaced, mismatches,
                   placedResult: placed?.status || placed?.success, readback };
  writeFileSync(join(jobDir, "premiere", "replay-verify.json"), JSON.stringify(verify, null, 2));
  console.log(`replay-edl: ${readback.length}/${cuts.keep.length} clips on ${seqName}, ${mismatches} mismatches → premiere/replay-verify.json`);
  if (readback.length !== cuts.keep.length || mismatches) process.exit(1);
} finally {
  await b.close();
}
