#!/usr/bin/env node
// Premiere lane — put the pipeline's layers onto <job>__CUT after replay-edl.mjs:
//   V2  renders/captions*.mov at 0        (the caption composition, one clip)
//   V3  renders/g*.mov at each plan cue   (V4 when two graphics overlap in time)
//   A1  voice gain from audio/voice-gain.json on every A-roll clip
//   V2+A2  b-roll (windowed clips from build-broll.py carry their audio to A2)
// Overlays are placed with linkAudio:false (a ProRes 4444 render carries no voice) and never repositioned here —
// a wrong-looking graphic is fixed in the plan and re-rendered. They ARE scaled to the sequence: renders are
// canvas-sized (1080×1920) and a creator's 4K sequence (2160×3840) shows them at half size, centred, unless each
// overlay is set to seqW/canvasW (200 %). Premiere does not re-fit script-placed clips (9077, 2026-09-28). Read-back is the gate:
// every clip is listed again and written to premiere/layers-verify.json.
//
//   node lanes/premiere/place-layers.mjs <job-dir> [--sequence <name>] [--no-gain]
//     --sequence  place onto this sequence instead of <job>__CUT (e.g. a duplicate of the creator's own cut, whose
//                 clips must match cuts.json — the layers are timed to it); missing overlay tracks are added
//     --no-gain   leave A1 alone (the creator's own audio chain)

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, resolve, basename } from "node:path";
import { Bridge, readJob } from "./bridge.mjs";

const argv = process.argv.slice(2);
const opt = (k) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : null; };
const jobDir = resolve(argv.find((a) => !a.startsWith("--") && argv[argv.indexOf(a) - 1] !== "--sequence") || ".");
const state = readJob(jobDir);
const seqName = opt("--sequence") || `${state.job}__CUT`;
const NO_GAIN = argv.includes("--no-gain");
const fps = Number(state.fps || 30);
const plan = JSON.parse(readFileSync(join(jobDir, "graphics-plan.json"), "utf8"));
const caps = JSON.parse(readFileSync(join(jobDir, "captions.json"), "utf8"));
const gain = existsSync(join(jobDir, "audio", "voice-gain.json")) ? JSON.parse(readFileSync(join(jobDir, "audio", "voice-gain.json"), "utf8")) : null;
const bplan = existsSync(join(jobDir, "broll-plan.json")) ? JSON.parse(readFileSync(join(jobDir, "broll-plan.json"), "utf8")) : {};
const broll = bplan.clips || [];
const titles = bplan.titles || [];   // hook titles: own layer on the top graphics track (V5) — no graphics share it here
// 0-based. With B-roll: V2 B-roll, V3 captions, V4/V5 graphics; without: V2 captions, V3/V4 graphics
const TRACK = broll.length ? { broll: 1, captions: 2, gfx: 3, gfx2: 4 } : { captions: 1, gfx: 2, gfx2: 3 };

const b = await Bridge.connect();
try {
  const seq = ((await b.call("list_sequences", {})).sequences || []).find((s) => s.name === seqName);
  if (!seq) throw new Error(`${seqName} not found — run replay-edl.mjs first`);
  const sequenceId = seq.id;
  await b.call("set_active_sequence", { sequenceId }).catch(() => {});

  const tracksNow = async () => b.call("list_sequence_tracks", { sequenceId });
  const vtracks = (t) => t.videoTracks || t.video || [];
  const atracks = (t) => t.audioTracks || t.audio || [];

  // enough video tracks for V2/V3/V4
  let before = await tracksNow();
  for (let i = vtracks(before).length; i < TRACK.gfx2 + 1; i++) await b.call("add_track", { sequenceId, trackType: "video" });
  before = await tracksNow();

  // the overlay tracks must be empty: a second run would stack duplicates
  for (const ti of [TRACK.broll, TRACK.captions, TRACK.gfx, TRACK.gfx2].filter((t) => t != null)) {
    for (const c of (vtracks(before)[ti] || {}).clips || []) {
      await b.call("remove_from_timeline", { clipId: c.id || c.clipId, sequenceId, deleteMode: "lift" }).catch(() => {});
    }
  }

  if (broll.some((c) => c.render_audio)) {   // and the b-roll audio track (A2)
    for (const c of (atracks(before)[TRACK.broll] || {}).clips || []) {
      await b.call("remove_from_timeline", { clipId: c.id || c.clipId, sequenceId, deleteMode: "lift" }).catch(() => {});
    }
  }

  const importItem = async (rel) => {
    const filePath = resolve(jobDir, rel);
    if (!existsSync(filePath)) throw new Error(`render missing on disk: ${filePath}`);
    const found = await b.call("find_project_item_by_name", { name: basename(filePath) }).catch(() => null);
    const hits = found?.items || found?.results || (Array.isArray(found) ? found : []);
    let item = hits[0];
    if (!item) {
      const imp = await b.call("import_media", { filePath, binName: `${state.job} renders` });
      item = imp.item || imp.projectItem || imp;
    }
    const id = item.id || item.projectItemId || item.nodeId;
    if (!id) throw new Error(`no project item id for ${rel}: ${JSON.stringify(item).slice(0, 200)}`);
    return id;
  };

  const placeVideo = async (rel, trackIndex, time, linkAudio = false) => {
    const projectItemId = await importItem(rel);
    const r = await b.call("add_to_timeline", { sequenceId, projectItemId, trackIndex, time, insertMode: "overwrite", linkAudio }, 120000);
    if (r?.success === false) throw new Error(`add_to_timeline ${rel}: ${JSON.stringify(r).slice(0, 300)}`);
  };

  const wanted = [];
  // 0. B-roll — each cutaway is a source range of a gameplay file, filled to the frame (scale = cover), no audio
  // A windowed clip (box/title) is build-broll.py's canvas-sized render: placed whole, scaled like a graphic, and its
  // audio kept — native linking lands it on the audio track with the video track's index (A2), which nothing else uses.
  for (const c of broll) {
    if (c.box || c.title) {
      const time = Math.round(c.start * fps) / fps;
      await placeVideo(c.render, TRACK.broll, time, !!c.render_audio);
      wanted.push({ id: c.id, track: TRACK.broll, time, file: basename(c.render), audio: !!c.render_audio });
      continue;
    }
    const projectItemId = await importItem(c.file);
    const fin = Math.round(c.src_in * fps), fout = fin + Math.round((c.end - c.start) * fps);
    const time = Math.round(c.start * fps) / fps;
    const r = await b.call("add_to_timeline_batch", { sequenceId, clips: [
      { projectItemId, trackIndex: TRACK.broll, time, linkAudio: false, sourceInPoint: fin / fps, sourceOutPoint: fout / fps }] }, 120000);
    if (r?.success === false) throw new Error(`b-roll ${c.id}: ${JSON.stringify(r).slice(0, 300)}`);
    wanted.push({ id: c.id, track: TRACK.broll, time, file: basename(c.file), cover: true });
  }

  // 1. captions
  if (caps.render) {
    await placeVideo(caps.render, TRACK.captions, 0);
    wanted.push({ id: "captions", track: TRACK.captions, time: 0, file: basename(caps.render) });
  }

  // 2. graphics — V3, or V4 while V3 is still busy
  let busyUntil = -1;
  for (const g of plan.graphics) {
    if (!g.render) continue;
    const time = Math.round(g.cue * fps) / fps;
    const track = time < busyUntil - 1e-6 ? TRACK.gfx2 : TRACK.gfx;
    if (track === TRACK.gfx) busyUntil = time + g.duration;
    await placeVideo(g.render, track, time);
    wanted.push({ id: g.id, track, time, file: basename(g.render) });
  }

  // 2a. hook titles on the secondary graphics track
  for (const t of titles) {
    const time = Math.round(t.start * fps) / fps;
    await placeVideo(t.render, TRACK.gfx2, time);
    wanted.push({ id: `title-${t.id}`, track: TRACK.gfx2, time, file: basename(t.render) });
  }

  // 2b. the overlay tracks must OUTPUT: a hidden track (eye off) shows nothing and every read-back still says "found"
  for (const ti of [TRACK.broll, TRACK.captions, TRACK.gfx, TRACK.gfx2].filter((t) => t != null)) {
    await b.call("toggle_track_visibility", { sequenceId, trackIndex: ti, visible: true }).catch(() => {});
  }

  // 3. voice gain on every A1 clip
  const after = await tracksNow();
  const a1 = (atracks(after)[0] || {}).clips || [];
  let gained = 0;
  if (gain && !NO_GAIN && Math.abs(gain.gain_db) >= 0.1) {
    for (const c of a1) {
      const r = await b.call("adjust_audio_levels", { clipId: c.id || c.clipId, level: +gain.gain_db.toFixed(2) }).catch(() => ({ success: false }));
      if (r?.success !== false) gained++;
    }
  }

  // 4. read back — the gate
  const tol = 1.5 / fps;
  const readback = [];
  let missing = 0;
  for (const w of wanted) {
    const clips = (vtracks(after)[w.track] || {}).clips || [];
    const hit = clips.find((c) => Math.abs((c.startTime ?? c.start ?? -99) - w.time) <= tol && (c.name || "").startsWith(w.file.replace(/\.(mov|mp4)$/, "")));
    readback.push({ ...w, found: !!hit, start: hit?.startTime ?? hit?.start ?? null, end: hit?.endTime ?? hit?.end ?? null, clipId: hit?.id ?? null });
    if (!hit) missing++;
    if (w.audio) {   // its audio must be on the timeline too, at the same time
      const ah = ((atracks(after)[w.track] || {}).clips || []).find((c) => Math.abs((c.startTime ?? c.start ?? -99) - w.time) <= tol);
      readback[readback.length - 1].audio_found = !!ah;
      if (!ah) missing++;
    }
  }
  // 4b. scale overlays to the sequence frame (renders are canvas-sized)
  const canvasW = Number(state.canvas_width || 1080);
  const scale = seq.width ? Math.round((seq.width / canvasW) * 10000) / 100 : 100;
  let scaled = 0;
  if (Math.abs(scale - 100) > 0.01) {
    for (const r of readback) {
      if (!r.clipId || r.cover) continue;
      const res = await b.call("set_clip_properties", { clipId: r.clipId, properties: { scale } }).catch(() => ({ success: false }));
      if (res?.success !== false) scaled++;
    }
  }
  // 4c. B-roll covers the frame: scale = max(seqW/srcW, seqH/srcH)
  const seqW = seq.width || canvasW, seqH = seq.height || Number(state.canvas_height || 1920);
  for (const r of readback.filter((x) => x.cover && x.clipId)) {
    const c = broll.find((x) => x.id === r.id);
    const top = c.crop_top || 0;   // source rows hidden above the frame (a recorded app's top bar)
    const cs = +(Math.max(seqW / (c.src_w || 1920), seqH / ((c.src_h || 1080) - top)) * 100).toFixed(3);
    // pan (0 = source's left edge … 1 = right edge) slides the oversized frame; 0.5 is centred
    const over = (c.src_w || 1920) * cs / 100 - seqW;
    const position = { x: +(seqW / 2 + over * (0.5 - (c.pan ?? 0.5))).toFixed(1), y: +(seqH / 2 - (top / 2) * cs / 100).toFixed(1) };
    const res = await b.call("set_clip_properties", { clipId: r.clipId, properties: { scale: cs, position } }).catch(() => ({ success: false }));
    if (res?.success !== false) scaled++;
  }
  mkdirSync(join(jobDir, "premiere"), { recursive: true });
  const verify = { overlay_scale_pct: scale, scaled, sequenceId, sequenceName: seqName, wanted: wanted.length, missing, voice_gain_db: gain?.gain_db ?? 0, a1_clips: a1.length, gained, readback };
  writeFileSync(join(jobDir, "premiere", "layers-verify.json"), JSON.stringify(verify, null, 2));
  console.log(`place-layers: ${wanted.length - missing}/${wanted.length} overlays on ${seqName} (${broll.length ? `V2 ${broll.length} b-roll, V3 captions, V4/V5` : "V2 captions, V3/V4"} graphics) · scale ${scale}% on ${scaled} · gain ${gain?.gain_db ?? 0} dB on ${gained}/${a1.length} A1 clips → premiere/layers-verify.json`);
  if (missing || (gain && !NO_GAIN && gained !== a1.length)) process.exit(1);
} finally {
  await b.close();
}
