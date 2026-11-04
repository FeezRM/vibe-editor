---
name: ig-delivery
description: "Export and final QA: the ffmpeg lane renders the final (or Premiere exports and the file is proven on disk), verify-final checks duration, loudness, silences, caption geometry and writes the contact sheet. Use for: export, render it out, ship it, final check, is this ready, deliver."
---

# ig-delivery — node 08

```bash
./finalize.sh projects/<job> [--lane ffmpeg|premiere|vibe]   # → outputs/<job>.final.mp4 + ~/Downloads copy
python workflows/verify-final.py projects/<job>          # gate + review/final-sheet.png
```

**Never report an export that is not on disk and newer than the run.** `finalize.sh` checks both; on
the Premiere lane `lanes/premiere/export.mjs` proves the file itself and falls back to ffmpeg.

**Vibe Studio** (`studio/`, the vibe lane) is the editor the user refines in: `lanes/vibe/open.sh projects/<job>`
opens the job as an editable timeline (their hand edits live in `<job>/vibe/<job>.fcproj`), and `--lane vibe`
exports that project with captions burned in, falling back to ffmpeg. When the user has edited by hand, export on
the vibe lane so their edits ship; then run `verify-final.py` as usual.

Export numbers: `numbers.json` → `export` (libx264 crf 18, 20 Mbps cap, AAC 320k, yuv420p, sequence fps).

Then watch the final yourself (`ig-reel` → watch it) before handing it over. If something mechanical is wrong
(duration, loudness, dead air), a gate is missing — add the check to `verify-final.py` rather than fixing the one file.
