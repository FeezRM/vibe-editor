---
name: ig-captions
description: "Builds and styles burnt-in captions for short-form vertical video — step 2 of the six-step editing SOP. Owns transcription-to-timing accuracy, the caption band placement (45-60% of frame height, under the chin, NOT the bottom third), the locked type spec, semantic colour emphasis, the hard-cut rule (captions never slide or fade), and the choice between HyperFrames-rendered caption compositions and Premiere's native caption track. Use whenever the user wants to: add captions or subtitles, fix caption timing or sync, restyle captions, change caption placement or font, emphasise words, or asks why their captions look cheap. Most short-form is watched on mute, so captions are not an accessory — the video does not work without them. Triggers: add captions, captions, subtitles, caption timing, caption style, word by word captions, kinetic captions, sync the captions, captions are off, caption font, caption placement, burn in subtitles, emphasise the keyword, highlight a word."
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

## The four things that go wrong

Almost every bad caption job is one of these:

1. **Timing drift** — the word appears a beat after it's spoken. Auto-generated captions do
   this constantly and it reads as lag.
2. **Parked too low** — bottom-third captions force the viewer to choose between the face
   and the words.
3. **Grammar-corrected** — the transcriber "fixes" the speaker's voice and the captions
   stop sounding like a person.
4. **Running on top of a graphic that already has words** — two text layers competing. See
   *Mute windows* below. This one is invisible to every automated check, because each layer
   is individually correct.

Fix those four and the captions are already better than most.

---

## Mute windows — the caption is not always on

> **Only one text layer at a time.** Where a graphic carries its own words, the caption
> track goes silent for that window. It does not shrink, and it does not move — it goes
> away.

Measured across the reference reels: whenever a content card with baked-in text is on
screen, there is **no burnt-in caption**. When the caption is running big and centred, there
is no competing text. They alternate.

`ig-show` owns the decision and hands you the list. It appears in the MOTION PLAN as its
own block:

```
CAPTION MUTE WINDOWS
  0.00 – 4.50    hook lockup
  20.27 – 30.17  trial reel covers carry their own copy
```

**Two windows are effectively always present:**

| Window | Why |
|---|---|
| The **hook lockup**, for its whole life | the lockup *is* the caption — bigger, better set, carrying the accent |
| Any **content card with its own caption** — a reel cover, a screenshot, a DM | the card's text is the beat |

**Not a mute window:** app UI whose text is *chrome* — a tab bar, stat row, nav, buttons.
Captions over chrome are in-style and the references do it constantly. The distinction is
**content vs chrome**, not graphic vs no-graphic.

### Building them

- **HyperFrames path** — the caption composition simply emits nothing in those ranges. Drop
  the caption groups whose midpoint falls inside a window; do not just set opacity 0, or the
  glow still renders.
- **Premiere native path** — split the caption track at the window edges and delete the
  spans, or hard-cut the caption clip around them.

**Check it in a composited frame, not in the caption comp alone.** A mute window is only
visible when the caption layer and the graphic layer are composited together — which is the
same reason it gets shipped broken.

If muting leaves a stretch longer than ~2s with no text at all *and* no graphic carrying
words, that is a signal the graphic is too quiet, not that the caption should come back.
Kick it to `ig-show`.

---

## Placement — the correction

**Caption band: y 920–1130 on a 1080×1920 frame (48–59% of height).**

*(Measured off three reference reels — see `ig-show/reference/TEARDOWN.md §4`. The older
864–1152 figure was the right idea and slightly too generous; captions in the references
sit in a tighter band centred a little lower.)*

This is deliberately **higher** than a conventional bottom third. With eyes on the upper
third of frame — the recommended framing — this band sits **directly under the chin**.

The reasoning, from the SOP: *"Putting your captions too low will make your viewer have to
choose whether to focus on you or the captions."* The eye cannot read text and watch a
face at that separation, so it ping-pongs and loses both. Analysis of reference creators
independently found captions at centre to centre-low, in the same 45–60% band.

Also:
- Centred horizontally; clear of the right-side action rail (avoid centreX > ~0.85).
- Never overlapping a graphic. `ig-show`'s two default placements both stay clear:
  `.cutaway` is full-frame with captions riding on top, and `.beside` sits at head height
  (y 200–900) well above this band. `.stage` (y 1180–1560) is below it. If a graphic and a
  caption ever collide, the graphic moves — the caption band is fixed.
- Hook text is the one exception — it sits higher, but still inside the safe zone.

---

## Type spec

| | Value |
|---|---|
| Face | `Europa Grotesk SH` — exact family string. **Not** "...SH Bol" (the GDI name) and **not** "...Bold". Verified by render. |
| Fallback | `Anton` (free, OFL, auto-resolves) if the licensed file isn't on the machine |
| Size | **88px** (`--cap-size`) — cap height ~59px. Hook block only: **140px** (`--cap-size-hook`) |
| **Max line width** | **842px = 78% of frame width.** Hard ceiling. |
| Case | ALL CAPS |
| Colour | `--ink` **pure white** |
| Tracking | `-0.015em` |
| Line height | `0.94` — lines stack tight |
| Legibility | **glow**: a dark halo `0 0 18px rgba(0,0,0,.85)` plus a soft bloom in the text's own colour. **No stroke. No box.** |
| Group size | **2–4 words** |
| Lines | **ONE. Always. Never two.** |

### One line, 2–4 words — the house rule

**Every caption is a single line of 2–4 words. A second line is a build error.**

This is a deliberate deviation from the reference reels, which do use two-line blocks
(`STOP USING` / `HOOKS`). Stated plainly so nobody "corrects" it back later.

The consequence, and it matters: **four words do not fit inside the references'
62%-of-frame width ceiling at 88px.** Two ways out — shrink the type, or widen the
ceiling. Shrinking drops below the reference cap height and makes captions look weedy, so
the ceiling moves to **78%**, which is what the references' own *single-line* captions
measure at anyway.

### Width is the constraint, not the word count

The size spec was wrong twice. It said **140–165px**, which is the **hook** caption
measured off S3's opening frame and applied to every caption in the video. A first
correction changed it to 104px — a bad average of the hook and body sizes, still ~25%
oversized. Body captions measure **cap 58–65px → 88px**.

| | Reference body | Reference hook | Original spec |
|---|---|---|---|
| Cap height @1080×1920 | **58–65px** | 100px | 93–100px everywhere |
| Font size | **88px** | 140px | 140–165px everywhere |

⚠️ **Measure with a brightness threshold of 245, not 225.** At 225 the caption's own glow
passes the test and inflates cap height by 20–40% — which is how *both* wrong figures
survived a "verified with pixels" check.

**Word count alone does not protect you.** `PEOPLE DIDN'T EVEN WATCH` is four words and
measures **100% of frame width**. The width cap does the work — when a group overflows,
split it into two captions. Never shrink the type to make copy fit.

A stroke or a box behind captions is a 2020 tell. The glow survives any background: the
dark halo holds it against bright footage, the coloured bloom makes the emphasis word read
before it is parsed.

### Calibration — measured with the real font

Rendered with `assets/europa-grotesk-sh-bold.otf` at 1080×1920, single line, 88px:

| String | Words | Cap height | Line width | Verdict |
|---|---|---|---|---|
| `WILL TELL YOU` | 3 | 59px | 54.6% | ✅ |
| `TO JUST WRITE A` | 4 | 60px | 62.8% | ✅ |
| `AND RECORD EACH` | 3 | 60px | 71.7% | ✅ |
| `MOST PEOPLE WILL` | 3 | 60px | 71.9% | ✅ top of the band |
| `PEOPLE DIDN'T EVEN WATCH` | 4 | 59px | **100.0%** | ❌ split into two captions |
| ~~104px~~ `MOST PEOPLE` | 2 | 74px | 62.0% | ❌ the first correction |
| ~~140px~~ `MOST PEOPLE` | 2 | 100px | 83.6% | ❌ the original spec |

### Grouping rule: ~11 characters per line

At 88px in this face the mean glyph advance is ~48px, so:

> **Max ~17 characters including spaces, on one line**, and 2–4 words within that.

Group greedily to the character budget, and **never end a caption on a function word** —
`tell you to`, `just write a`, `time on a` all read as a sentence chopped mid-phrase. Pop
trailing function words onto the front of the next caption, repeatedly (a group can end on
a run of them), always leaving at least two words behind. Reference implementation:
`analysis/build-captions.py`.

Verify by measurement, not by eye:

```bash
python analysis/measure.py <frame-or-video> <t>
```

A stroke or a box behind captions is a 2020 tell. The glow survives any background: the
dark halo holds it against bright footage, the coloured bloom makes the emphasis word read
before it is parsed.

---

## Emphasis — colour and scale, not weight

The caption face ships in **one weight**, so weight-based emphasis isn't available. This is
an improvement, because colour can carry *meaning* where weight only carries volume.

| Class | Colour | Means |
|---|---|---|
| `.bad` | `#EB0408` vivid red | the wrong way, the old way, the myth, the thing to stop |
| `.good` | `#00E800` vivid green | the right way, the fix, the thing to do |
| `.hot` | `#FFC531` gold | the live value — a metric, a winner |

**These are near-maximum saturation on purpose.** The older muted `#A33` / `#6A9E72` read
as timid; measured off the references, the colours are essentially pure. Each carries a
glow in its own hue.

### Colour by LINE, and the accent goes on the payload

**Default: accent the payload WORD, inline.** `How To **MELT** Fat Off Your Body`,
`3 **SECRETS** to **FAT LOSS**`, `WRITE **5** DIFFERENT`.

A whole line takes the colour **only when that line is itself a complete payload phrase** —
`STOP USING` / `HOOKS`, `DISGUSTINGLY` / `EASY`, `YOU FINALLY` / `DID IT!`.

⚠️ **Do not colour a line merely because it contains an accent word.** A build that did
exactly that rendered `TO WASTE SO` entirely red — an arbitrary slice of a sentence, which
communicates nothing and looks like a bug. Caught by looking at a rendered frame, 2026-08.
The limit is still one emphasis colour per line.

**Which line gets the accent is not positional — the accent goes on the payload words and
white on the connective words.** It is the second line about half the time and the first
line the other half:

| Caption | White | Accent |
|---|---|---|
| STOP USING / HOOKS | HOOKS | STOP USING — red |
| HERE'S MY / ULTIMATE HACK | HERE'S MY | ULTIMATE HACK — green |
| STEAL MY / SECRET STRATEGY | STEAL MY | SECRET STRATEGY — blue |
| DISGUSTINGLY / EASY | EASY | DISGUSTINGLY — green |
| MIND-NUMBINGLY / SIMPLE | SIMPLE | MIND-NUMBINGLY — green |
| YOU FINALLY / DID IT! | YOU FINALLY | DID IT! — green |

The emphasised words are the ones hit hardest in the audio — not the ones that seem most
important on the page.

### Accent about 40% of the time — the rest is plain white

**Measured: roughly 40% of caption blocks in the references carry an accent. The other 60%
are plain white on both lines.** `BUT INSTEAD`, `WHICH`, `WENT SO VIRAL`, `POWER WORDS`,
`A MILLION TIMES`, `THAT COST THEM` are all white.

Colouring a keyword in every block destroys the signal — if everything is emphasised,
nothing is. When you catch yourself accenting three consecutive blocks, the second one is
almost certainly decoration.

### Two treatments that break the caption font on purpose

- **A number that is the point gets a different type treatment, not just a colour.** In the
  references `99%` renders hollow/outlined with an inner sheen beside solid white
  `BUSINESS OWNERS`. Colour alone under-reads on a figure.
- **A sentiment word gets one bespoke setting per reel, maximum.** `Congratulations` is set
  in a gold serif with a light-ray burst — the type matches the emotion and deliberately
  breaks the house face. Once per reel. The "no serif anywhere" rule in `ig-show` governs
  graphics; this single caption exception is deliberate and is the only one.

### Pair it with the frame

When the script contrasts a bad phrasing with a good one, the caption colour and the
`COLOUR WASH` behind the speaker move together — red caption on a red-washed frame, then
green on green. `ig-show` owns the wash; cue both off the same timecode.

### Semantic colour-coding

Don't recolour for decoration — let colour carry the argument. Observed in reference work:
a bad example appears in red, the better alternative appears in green moments later, and
the background glow shifts with it. The viewer knows which is endorsed before parsing the
sentence.

Use it for: bad way → good way · old → new · myth → truth · them → us.
Do **not** use it for: random keywords, every noun, or "making it pop."

---

## Captions do not animate — they cut

**HOUSE RULE: a caption cuts on and cuts off. No slide, no fade, no movement of any
kind.** It is either fully on screen or fully off, never mid-transition.

```js
// hard cut, zero-duration sets -- seek-safe and frame-exact
tl.set(el, { opacity: 1 }, START);
tl.set(el, { opacity: 0 }, END);
```

That is the whole implementation. Do not add an entrance.

### What this replaces, and why it is written down

This section previously prescribed **match-cut chaining** — parenting consecutive captions
so one's exit motion carried into the next's entrance (`x: 120 → 0`, `expo.out`), and
called it "the most premium-reading caption technique available". A later build used a
gentler `y: 26 → 0` slide-up. **Both were rejected by the owner on sight.** The captions
rise into place and it reads as a template effect.

Do not reintroduce either. If a future pass is tempted to "add a little life" to the
caption layer: that is the thing that was explicitly removed.

### The one thing worth keeping from the old section

Two captions must **never** be on screen at once. They occupy the same band, so any
temporal overlap stacks them and neither is readable. With hard cuts this is automatic —
caption N's `opacity: 0` and caption N+1's `opacity: 1` land on the same frame — but if
anyone ever reintroduces a fade, the overlap bug comes straight back. An earlier build had
B entering 60ms before A finished leaving; it passed lint and was invisible until a frame
was pulled and looked at.

Motion belongs to the graphics layer (`ig-show`), which has its own entrance vocabulary.
The caption layer is typography, and it holds still.

---

## Two build paths — pick one and stay on it

| | **(a) HyperFrames** | **(b) Premiere native** |
|---|---|---|
| How | a caption composition rendered to alpha `.mov`, imported to the captions track | `create_caption_track` / `add_text_overlay` |
| Typography | exact — the full locked spec, real tracking, hard-cut timing | approximate |
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
4. **Group.** **One line, 2–4 words** per hit, following the cut rhythm. When speech speeds
   up, captions speed up — expect ~1.5 captions/second on fast delivery.
5. **Mark emphasis.** One colour per line, on the payload words, on roughly 40% of blocks.
6. **Build** via path (a) or (b).
7. **Verify with pixels — and measure, don't eyeball.** `export_frame` at 3–4 caption hits,
   then run the measurement rather than judging by sight:
   ```bash
   python analysis/measure.py <exported-frame-or-video> <t1,t2,t3>
   ```
   It reports cap height at 1080×1920 and line width as a percentage of frame width. Assert
   **cap height 58–65px**, **width ≤78%**, and **no caption on two lines**. This step exists because the previous
   spec was verified by looking at frames and the wrong size passed every time.

---

## Premiere mechanics

| Task | Tool |
|---|---|
| Native caption track | `create_caption_track`, `read_sequence_captions` |
| One-off title | `add_text_overlay` |
| Import a rendered caption `.mov` | `import_media` |
| Make the track exist | `add_track`, then confirm with `list_sequence_tracks` |
| Check placement | `export_frame` |

> ⚠️ **`export_frame` can report success and write nothing.** Pass **forward slashes** in
> `outputPath` (backslashes get read as escapes and the path is silently mangled), and
> **assert the file exists on disk** before believing the result — on this machine the
> exporter is broken and returns `success: true` with no file. Fall back to an ffmpeg
> composite over a real A-roll frame. See `ig-show/SKILL.md` for the full note and the
> fallback command. A verification step that cannot fail is not a verification step.


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
- **Any caption entrance or exit animation at all** — no slide-up, no slide-in, no fade,
  no scale, no bounce. Captions cut on and cut off. This was rejected twice; it stays out.
- More than one emphasis colour per line
- **A line wider than 78% of the frame** — split into two captions instead
- **More than 4 words in a caption**
- **A second line — ever**
- **Ending a caption on a function word** (`to`, `a`, `the`, `and`, `with`)
- **Shrinking the type to make copy fit**
- **Accenting a keyword in every block** — accent ~40%, leave the rest white
- Emoji
- Captions in the bottom third
- Captions over the face
- **A caption running over a graphic that carries its own words** — see *Mute windows*
- **Shrinking or repositioning a caption to "make room" for a graphic** — it mutes instead
- Grammar-correcting the speaker

---

## QA

- [ ] Every group lands on the frame its first word is spoken
- [ ] Band is 920–1130; nothing in the bottom third; face not covered
- [ ] Clear of the right-side action rail
- [ ] `Europa Grotesk SH` actually rendered — verified in a frame, not assumed
- [ ] ALL CAPS, glow not stroke, no box
- [ ] **Measured with `analysis/measure.py` (threshold 245): cap 58–65px, width ≤78%**
- [ ] **Every caption is ONE line of 2–4 words — zero two-line blocks**
- [ ] **Captions hard-cut — no slide, fade, or scale on entrance or exit**
- [ ] one emphasis colour per line, on the payload words
- [ ] **~40% of blocks accented — the rest plain white; no run of 3 accented blocks**
- [ ] Speaker's exact words — slang and phrasing intact, not "corrected"
- [ ] Caption rhythm follows cut rhythm
- [ ] One build path only, not both
- [ ] No overlap with any `ig-show` graphic
- [ ] **Every mute window from the MOTION PLAN is actually empty — verified in a composited frame with both layers, not in the caption comp alone**
- [ ] **Nothing renders inside a mute window** — groups dropped, not set to opacity 0 (the glow still draws)

---

## Handoff

Captions and graphics must not collide — cue both off the same timecodes and keep
`ig-show`'s graphics out of the 920–1130 band. Caption emphasis hits are also the cheapest
item on `ig-pacing`'s pattern-interrupt menu, so a dense caption rhythm reduces how many
graphics the reel actually needs.
