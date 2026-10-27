---
name: ig-study
description: "Study the reference reels in samples/ and write samples/STYLE.md — what good editing looks like for this creator: cut rhythm, framing and zooms, captions, graphics (what, where, how long, how they move), sound, and what makes each reel engaging. Use for: study the samples, learn from these videos, I added sample videos, update the style, what makes these edits good. Run before editing whenever samples/ changed."
---

# ig-study — learn the bar from the samples

`samples/` holds reels the creator considers clean, good editing. Your job is to understand them well enough to edit
at that level without being told what to do — and to know *why* each choice works, so you can do something different
when a video calls for it. The output is `samples/STYLE.md`, the document every editing decision is checked against.

## 1. Watch every sample, properly

Read `samples/INDEX.md` if it exists (where each sample came from, its views). Then for each video directly in
`samples/` (not in subfolders like `_previous/`):

```bash
mkdir -p "<scratch>/<name>"
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of json samples/<file>
ffmpeg -i samples/<file> -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*"   # cut times
ffmpeg -i samples/<file> -vf "fps=4,scale=270:-2,tile=6x4" "<scratch>/<name>/sheet-%02d.png"           # every 0.25 s
```

Read every sheet. Then pull full-size frames (`lanes/ffmpeg/frame.py samples/<file> <t> out.png`) wherever something
happens — a graphic enters, moves, leaves; a zoom; a cut that changes framing; a caption style change — and read
those too, 2–4 frames per event so you see the motion, not one state. Get the words with `/watch samples/<file>` or
WhisperX, so you know what each visual was *for*.

## 2. Write down what you see — measured, and why

Per sample, a short breakdown: the beat-by-beat of the first 5 seconds, every graphic (time, what it shows, which
spoken words it serves, where on the frame, size, how it enters / moves / leaves, how long it stays), every zoom
(when, how much, how fast, on which word), cut rhythm (clips per 10 s, longest hold), caption look (font, size, case,
position, colour, emphasis, animation), sound (music, SFX and on what).

Then the synthesis — this is the part the editor actually uses:

- **The cut**: how tight, what is never left in, how jump cuts are handled.
- **The camera**: base framing, whether and how it punches in, what triggers a punch.
- **Captions**: the look, in numbers you could put in `numbers.json`.
- **Graphics**: how often (and how often *not*), what kinds of things get shown and what never does, where they sit
  relative to the face and the captions, typical size, motion style (speed, easing, entrances, exits), type, colour.
- **What makes them engaging**: the specific moves that hold attention — and the ones that vary between samples,
  which is where the editor has room to be creative.
- **Never**: what none of the samples do, which an AI editor tends to do (text boxes restating the caption, stock
  icons, slow zooms on stills, everything centred in a card, a graphic on every line…). Only list what you observed
  is absent.

Keep it specific ("a screenshot slides up from the bottom edge over ~6 frames to cover the lower 45 %, sits 2–3 s,
cuts out on the next sentence") and keep it about the samples, not about any one creator's identity. Never copy a
handle, name or avatar from a sample into an edit.

## 3. Calibrate the defaults

Where the samples are consistent and the repo's mechanical defaults disagree (caption font, size, band, case; the
cut's pause tolerance; framing scale), make a look: `presets/vertical/<name>/numbers.json` with
`"extends": "vertical/default"` and only the differing values, and name it in STYLE.md so `new-job.py --preset` uses
it. Fonts go in `presets/vertical/default/fonts/` (OFL / licensed only).

## 4. Tell the creator

Summarise in a few lines what you learned and anything you could not tell from the footage — ask about that, don't
guess.
