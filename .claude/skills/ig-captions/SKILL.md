---
name: ig-captions
description: "Builds and styles burnt-in captions for short-form vertical video — step 2 of the six-step editing SOP. Owns transcription-to-timing accuracy, the caption band placement (45-60% of frame height, under the chin, NOT the bottom third), the locked type spec, semantic colour emphasis, match-cut chaining between consecutive captions, and the choice between HyperFrames-rendered caption compositions and Premiere's native caption track. Use whenever the user wants to: add captions or subtitles, fix caption timing or sync, restyle captions, change caption placement or font, emphasise words, or asks why their captions look cheap. Most short-form is watched on mute, so captions are not an accessory — the video does not work without them. Triggers: add captions, captions, subtitles, caption timing, caption style, word by word captions, kinetic captions, sync the captions, captions are off, caption font, caption placement, burn in subtitles, emphasise the keyword, highlight a word."
---

# IG CAPTIONS — the video is watched on mute

**Step 2 of the editing SOP.** Runs after `ig-cut` has locked the spine, before graphics.

> "Most IG Reels are watched with sound OFF. So your video is literally USELESS without
> captions."

That is the entire justification and it is correct. Captions are not an accessibility
add-on here — for the majority of viewers **the captions are the video**. Dual-coding
(hearing and reading the same words) also measurably raises comprehension and hold for the
viewers who do have sound on.

---

## Brand overrides — read these before anything else

This repo ships defaults. **Whoever cloned it may have replaced them.**

| Read | Holds |
|---|---|
| `brand/BRAND.md` | free-text house rules — voice, subject matter, banned visuals, CTA, sound |
| `brand/brand.json` | values — palette, fonts, canvas, fps, density, export |

**Precedence, lowest to highest:**
repo defaults (this file) → `brand/` → the project's own `tokens.css` / `MOTION-PLAN.md`
→ what the user says in this conversation.

Where `brand/` contradicts a default below, **`brand/` wins** — and say so out loud rather
than silently following the default. If neither file exists, use the defaults here.

Values in `brand.json` are already compiled into `brand/tokens.css`; regenerate with
`node scripts/brand.mjs build` after editing. Never hand-edit `brand/tokens.css`.

---

## The three things that go wrong

Almost every bad caption job is one of these:

1. **Timing drift** — the word appears a beat after it's spoken. Auto-generated captions do
   this constantly and it reads as lag.
2. **Parked too low** — bottom-third captions force the viewer to choose between the face
   and the words.
3. **Grammar-corrected** — the transcriber "fixes" the speaker's voice and the captions
   stop sounding like a person.

Fix those three and the captions are already better than most.

---

## Placement — the correction

**Caption band: y 864–1152 on a 1080×1920 frame (45–60% of height).**

This is deliberately **higher** than a conventional bottom third. With eyes on the upper
third of frame — the recommended framing — this band sits **directly under the chin**.

The reasoning, from the SOP: *"Putting your captions too low will make your viewer have to
choose whether to focus on you or the captions."* The eye cannot read text and watch a
face at that separation, so it ping-pongs and loses both. Analysis of reference creators
independently found captions at centre to centre-low, in the same 45–60% band.

Also:
- Centred horizontally; clear of the right-side action rail (avoid centreX > ~0.85).
- Never overlapping a graphic. `ig-show` docks its overlays above (`DOCK-TL`) or below
  (`DOCK-BL`, y 1260) this band precisely to stay out of it.
- Hook text is the one exception — it sits higher, but still inside the safe zone.

---

## Type spec

| | Value |
|---|---|
| Face | `Europa Grotesk SH` — exact family string. **Not** "...SH Bol" (the GDI name) and **not** "...Bold". Verified by render. |
| Fallback | `Archivo Black` (free, OFL) if the licensed file isn't on the machine |
| Size | 76–92px |
| Case | ALL CAPS |
| Colour | `--ink` bone |
| Tracking | `-0.015em` |
| Legibility | 4px blur / 42% black drop shadow. **No stroke. No box.** |
| Group size | 2–4 words, or word-by-word |
| Lines | 1–2 maximum |

A stroke or a box behind captions is a 2020 tell. A soft shadow survives any background
and stays invisible when it isn't needed.

---

## Emphasis — colour and scale, not weight

The caption face ships in **one weight**, so weight-based emphasis isn't available. This is
an improvement, because colour can carry *meaning* where weight only carries volume.

| Class | Colour | Means |
|---|---|---|
| `.pop` | accent | the live value, the thing that matters |
| `.pop--bad` | oxblood | the wrong way, the old way, the myth |
| `.pop--good` | forest | the right way, the fix |

All three also scale to `1.14em` so they survive at scroll speed.

**One emphasised word per line, maximum.** That word is the one hit hardest in the audio —
not the one that seems most important on the page. Read the waveform or listen; the
speaker already told you which word it is.

### Semantic colour-coding

Don't recolour for decoration — let colour carry the argument. Observed in reference work:
a bad example appears in red, the better alternative appears in green moments later, and
the background glow shifts with it. The viewer knows which is endorsed before parsing the
sentence.

Use it for: bad way → good way · old → new · myth → truth · them → us.
Do **not** use it for: random keywords, every noun, or "making it pop."

---

## Match-cut chaining

The most premium-reading caption technique available, and it is cheap in GSAP.

Parent consecutive captions so one's **exit motion continues into the next's entrance** —
the second inherits the first's velocity and direction instead of starting from rest. The
result reads as one continuous move rather than a series of independent pop-ins.

```js
// B enters carrying A's motion. the 60ms overlap is what sells it.
tl.to(a, { x: -180, opacity: 0, duration: 0.30, ease: "power2.in"  }, 1.40)
  .from(b, { x: 180, opacity: 0, duration: 0.34, ease: "power3.out" }, 1.46);
```

Cut the overlap and you get two separate animations. Keep entrances snappy scale-pops
(0.14–0.20s, `expo.out`) with **no bounce or overshoot** — springiness reads cheap.

---

## Two build paths — pick one and stay on it

| | **(a) HyperFrames** | **(b) Premiere native** |
|---|---|---|
| How | a caption composition rendered to alpha `.mov`, imported to the captions track | `create_caption_track` / `add_text_overlay` |
| Typography | exact — the full locked spec, real tracking, match-cut chaining | approximate |
| Timing | deterministic, word-accurate | editable in-app afterwards |
| Speed | slower to build, faster to iterate at scale | faster to start |
| Use when | the captions are styled and the reel is a keeper | a straight subtitle read, or a one-off |

**Never mix both in one video.** Two caption systems in one reel is immediately visible.

---

## Workflow

1. **Transcribe first.** Premiere's MCP has no transcription tool — use
   `npx hyperframes transcribe <file>`, or a Whisper/Scribe pass for accuracy. You need
   **word-level timestamps**, not sentence-level, or nothing below works.
2. **Fix the words.** Correct genuine mis-hearings. **Restore the speaker's voice** where
   the transcriber formalised it — slang, double negatives, dropped copulas, verbal tics
   all stay. If it says "he is not" and they said "he ain't", change it back.
3. **Fix the timing.** Each group appears on the frame its first word is spoken. Auto-sync
   drifts; check it against the waveform rather than trusting it.
4. **Group.** 2–4 words per hit, following the cut rhythm. When speech speeds up, captions
   speed up.
5. **Mark emphasis.** One word per line, using the semantic classes above.
6. **Build** via path (a) or (b).
7. **Verify with pixels.** `export_frame` at 3–4 caption hits. Check placement in the band,
   the face is not covered, and the font did not fall back.

---

## Premiere mechanics

| Task | Tool |
|---|---|
| Native caption track | `create_caption_track`, `read_sequence_captions` |
| One-off title | `add_text_overlay` |
| Import a rendered caption `.mov` | `import_media` |
| Make the track exist | `add_track`, then confirm with `list_sequence_tracks` |
| Check placement | `export_frame` |

- Captions live on their **own track**, kept separate from graphics. An observed real
  project used a dedicated native captions track packed with word-level clips, with
  graphics on entirely separate video tracks.
- Premiere needs the **installed PostScript/family name** for `fontName`, and there is no
  font-list tool over MCP. Look it up on the host first:
  ```powershell
  [Drawing.Text.InstalledFontCollection]::new().Families | ? Name -like '*Europa*'
  ```
  ```bash
  system_profiler SPFontsDataType | grep -i europa     # macOS
  fc-list | grep -i europa                             # Linux
  ```
- **There is no live size preview over MCP.** Place one throwaway text clip,
  `export_frame` it, read the real size, delete it. Text is very easy to oversize at
  1080×1920.
- It edits the live project; `verify_premiere_connection` first.

---

## Banned

- Bulky Impact / Komika / bubble fonts
- Neon green, neon yellow, rainbow keywords
- Strokes, boxes, or backing plates behind caption text
- Bounce, spin, elastic, or overshoot on caption entrances
- More than one emphasised word per line
- Emoji
- Captions in the bottom third
- Captions over the face
- Grammar-correcting the speaker

---

## QA

- [ ] Every group lands on the frame its first word is spoken
- [ ] Band is 864–1152; nothing in the bottom third; face not covered
- [ ] Clear of the right-side action rail
- [ ] `Europa Grotesk SH` actually rendered — verified in a frame, not assumed
- [ ] ALL CAPS, 76–92px, shadow not stroke
- [ ] ≤4 words per group, ≤2 lines
- [ ] ≤1 emphasised word per line, semantic colour where it carries an argument
- [ ] Speaker's exact words — slang and phrasing intact, not "corrected"
- [ ] Caption rhythm follows cut rhythm
- [ ] One build path only, not both
- [ ] No overlap with any `ig-show` graphic

---

## Handoff

Captions and graphics must not collide — cue both off the same timecodes and keep
`ig-show`'s overlays out of the 864–1152 band. Caption emphasis hits are also the cheapest
item on `ig-pacing`'s pattern-interrupt menu, so a dense caption rhythm reduces how many
graphics the reel actually needs.
