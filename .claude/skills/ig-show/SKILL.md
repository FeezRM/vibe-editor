---
name: ig-show
description: "The visual layer of an edit: decide which beats (if any) get a graphic, design and write each one as a HyperFrames composition for this video, place it where the frame has room, build and watch it. Use for: motion graphic, show this visually, overlay, mockup, b-roll, graphics for this script, looks AI-generated, what should this graphic look like."
---

# ig-show — node 05

A graphic earns its place by making the video clearer or more engaging than the face and the words alone. The bar is
`samples/STYLE.md`: before you plan, re-read its graphics section and open a few full-size frames from the samples so
the look is in your eyes, not just in words.

## Decide what the video needs

Read `captions.json` as a script. For each beat ask what a viewer would want to *see* at that moment — the thing being
talked about, proof of a claim, a change happening — and whether it is worth covering part of the face for. Many beats
need nothing. Frequency, kind, size and motion follow the samples; where this video's content suggests something the
samples don't do but would clearly be more engaging, do it and note why.

Signs of an AI edit to avoid unless the samples do it: a graphic on every line, text that restates the caption, a
box around everything, generic icons and stock art, stills that only slowly zoom, everything centred, mismatched
styles from beat to beat, motion for its own sake.

## Real material

Show the real thing. In order: on disk (`assets/`, the creator's library) → a frame from the footage → capture the
real page (`workflows/capture-url.py <url> assets/x.png --mobile`, or the creator's logged-in Chrome for their own
profiles and tools) → look it up → ask the creator → build nothing. Never invent a number, a screenshot, a comment or
a result; a number on screen says where it came from in `provenance`.

## Write it

Each graphic is a HyperFrames composition you write for this video — `projects/<job>/compositions/<id>.html`, 1080×1920,
transparent background, one paused GSAP timeline registered on `window.__timelines`. Load `hyperframes-core` for the
composition contract and `hyperframes-animation` for motion before writing one. Fonts are in the job's `fonts/`;
assets are paths under `assets/`. Design it for this video: the type, colour and motion of the samples, sized for a
phone.

The four presets in `presets/graphics/` (`app-mock`, `receipt`, `thumb-wall`, `comment`) are there if one is exactly
right — use `"preset"` and `"params"` (the preset's `params.schema.json`) instead of `"html"`.

## The plan

`projects/<job>/graphics-plan.json`:

```json
{
  "notes": "what this edit does visually and why — one paragraph",
  "graphics": [
    {"id": "g01", "html": "compositions/g01-profile.html", "cue": 2.40, "duration": 2.8,
     "why": "he says 'my account' — show the real profile", "provenance": "captured 2026-10-26 from instagram.com/<handle>",
     "mute_captions": false, "sfx": "whoosh"}
  ]
}
```

`cue` is a timeline second read from `captions.json`. `mute_captions: true` when the graphic carries its own words.
`sfx` / `sfx_events` only where a sound helps (`presets/vertical/default/sfx.json` lists the verbs). A preset graphic
takes `"placement"` (its schema lists them) or `"box": {"x", "y", "w"}` anywhere on the canvas.

## Placement

Put it where the frame has room in *this* shot: look at a frame of the spine at the cue (`lanes/ffmpeg/frame.py
projects/<job>/preview/spine.mp4 <t> f.png`). Keep the face readable unless covering it is the point (a full cutaway)
and keep it off the live caption unless the captions are muted.

## Build and watch

`./run.sh projects/<job> --from graphics` validates (files exist, real params, cues in range), renders and composites.
Then look at full-size frames at the start, middle and end of each graphic over the real footage, next to a sample
frame. If it would not belong in the sample reel, change it — mark it `"dirty": true` to re-render. Look at the
motion, not one frame: render issues (a GSAP `keyframes` array that mis-seeks, a visible-start `fromTo` without
`immediateRender: false`, a class name HyperFrames reserves like `stage`) only show up in motion.
