# SAMPLES — the four reels, torn down

`TEARDOWN.md` measured the *style* of the reference reels: palette, caption cap heights,
placement percentages. It never described their **structure**, and structure is the entire
gap between what this repo builds and what the samples are.

This file is the structural teardown. Four reels in `samples/`, each ~45–51s, 720×1280,
watched frame-by-frame at ~1.2s intervals (frames via the bundled `/watch` skill; no Whisper
key configured, so this is a **visual** teardown — quoted on-screen text is read off the
pixels, spoken audio was not transcribed).

> **Copy layout, never identity.** These are real people's accounts. Every mockup you build
> uses `creator.handle` from `brand/brand.json`. `SKILL.md` bans lifting a handle out of
> `samples/`; grep for it before you render. The handles below are recorded because the
> *device* is "a real named account", and you need to know that to reproduce the device —
> not so you can paste them in.

---

## The finding that matters more than any single technique

**All four commit to one persistent object that mutates across the whole runtime, plus a
motif that returns and advances.** Not one of them is a sequence of graphics.

| | Contract | The persistent object | The returning motif |
|---|---|---|---|
| **S1** | SPLIT-STAGE | An Instagram profile filling in from a grey skeleton over 45s | A tier pyramid, 5 returns, one tier taller each time |
| **S2** | NESTED-SCALE | A simulated phone session that navigates | The phone; + one pure-emotion beat |
| **S3** | TWO-WORLDS | The same worksheet run 3× with different content | The 3-thumbnail brace, returning resolved |
| **S4** | OBJECT-OVER-GROUND | A phone-in-hand that later tiles into a 3×3 wall | Competitor cards that park in the corners |

This repo's rule — **one composition file per graphic** — makes all four impossible. That
rule is why the output is a slideshow, and it has been replaced by the SCENE model in
`SKILL.md` §4.

---

## S1 — the profile build
`AQM50V104ygDLCaZWicBD-…mp4` · 45.5s · SPLIT-STAGE

**The single best example of progressive disclosure in the set. If you read one teardown,
read this one.**

### Structure

The top half is one Instagram profile, present from frame 1 to the end. It begins as a
**grey wireframe skeleton** — flat grey bars where the name, bio lines and highlights will
go, flat grey circles where the highlight covers will go, a white star placeholder where the
avatar will go. Then it fills in, one field at a time, roughly one field per spoken beat:

| ~t | What fills in |
|---|---|
| 0:00 | Skeleton only. Star avatar placeholder, glowing. |
| 0:02 | **Avatar** → real photo, green ring |
| 0:09 | **Name** → `Alex Hormozi | Business Strategy`, with a green highlight swipe on the second half that then settles to white |
| 0:15 | **Bio line 1** → `I Scale Businesses At Workshops` (green as it lands, then white) |
| 0:19 | **Bio lines 2–3** → `Portfolio Does $250M+ Per Year`, `👇 Get Your Free Scaling Roadmap` |
| 0:22 | **Link** → `🔗 scalingroadmap` |
| 0:23 | **Highlights** fill left→right: `CLIENT WINS` 🏆 · `TESTIMONIALS` 📣 · `APPLY NOW` ✉ |
| 0:30 | **Grid tiles** → real thumbnails carrying **real** view counts `28.8M` · `8.6M` · `7.8M` |
| 0:36 | Tiles go to **wireframe placeholders** labelled `Your Offer` / `Client Case Study` / `Top Follower Post` — the profile becomes a *template for the viewer* |
| 0:38 | Those slots fill with real covers carrying real hook copy: `HOW OUR WORKSHOP WORKS`, `CLIENT WENT $9M → $150M`, `CONTENT IS KING` |
| 0:43 | Hard swap to **the creator's own** profile card — 462K followers, `Following` state already set. The CTA. |

**That is ~13 pattern interrupts out of one composition.** The repo currently spends one
composition per interrupt.

### Devices to steal

- **Skeleton → fill is the whole spine.** The wireframe is not a loading state; it is the
  *"before"* half of every reveal, and it tells the viewer what is coming so each fill lands
  as a payoff. The `.skel-*` classes in `tokens.css` already implement the mechanic — a
  skeleton bar flashes pure white, then unmasks the real value beneath. The mistake this repo
  kept making was using it *once*, for five bars, instead of as the architecture.
- **Green-then-white on landing.** New text arrives in the accent colour and settles to
  white over ~0.4s. Cheap, and it makes every fill legible as an *event*.
- **Focus by brightness.** The active field glows; everything else sits at ~0.3. Nothing
  slides. In a 45s single composition this is the only sane focus mechanism — motion would
  never stop.
- **The template turn.** Real content → wireframe slots → the viewer's content. The graphic
  stops being about the subject and becomes about the viewer. Strong CTA setup.

### The motif

A tier pyramid flies in over the profile **five times**, and each return adds exactly one
tier, bottom-up:

`80%` → `+50%` → `+30%` → `+20%` → `+10%` → `TOP 1%`

Colour ramp is `#EB0408 → #FF7A00 → #FFC531 → #9BE300 → #00E800 → #7B5CFF` — which
`BLOCKS.md:201` already hard-codes. On the final return the pyramid **crosses the split
line** and sits in front of the speaker's head, with `TOP 1%` in chrome-blue above it. That
crossing is the contract's one legal break.

### Captions

**There are none.** Forty-five seconds, zero burnt-in captions. The graphic carries every
word that matters.

---

## S2 — the DM workflow
`AQMhkqN3zcsdnJmx5E61Ndd…mp4` · 47.6s · NESTED-SCALE

**The most technically advanced of the four.** It is a simulated user session that never
existed, shot as if it were a screen recording.

### The scale ladder

```
talking head  →  reel cards  →  IG feed  →  [A-roll AS A POST in that feed]
              →  IG story    →  story + testimonials  →  [zoom out] iPhone in frame
              →  push notification  →  story viewer list  →  DM thread  →  back out
```

### Devices to steal

- **The A-roll becomes a post.** At ~0:20 the talking head stops being the frame and becomes
  a *post inside the rebuilt feed* — same footage, now with IG chrome above and below it.
  The transition is a scale-out, not a cut. **This is the move the current pipeline cannot
  do**; see the cost warning in `FRAME-CONTRACTS.md` §2.
- **One winner among peers.** Three reel cards, real counts `10.7K` / `1.2M` / `11.4K`. The
  winner takes a gold border + gold glow + gold eye-icon; the losers **desaturate**, they do
  not fade. `tokens-viral.css` already ships `.reel--win` / `.reel--lose` doing exactly this
  and `:302-304` records the reasoning.
- **Progressive typing into a real UI.** The story's text field types in over several beats:
  `"Hey [Name],` → `"Hey [Name], What's It Like Working With You?"`. The bracket placeholder
  is deliberate — it reads as a *template the viewer can use*, which is the one legitimate
  use of `[Name]` (contrast `SKILL.md` §3c, which bans it as placeholder content; the
  difference is that here the template-ness is the point).
- **Real testimonial screenshots fly in.** Four real Skool "Wins" posts with real names and
  real numbers — `$166k for September`, `Added $4500/m off 1 video`, `Record Month - Finally
  6 Figures`, `300k cash collected in a month` — arriving one per beat around the story.
  Nothing here is rebuilt; they are screenshots.
- **The zoom-out reveal.** The story turns out to be on an iPhone — real bezel, `9:41` status
  bar — and a push notification slides in from a named account. Context arrives *after* the
  content, which is the opposite of how this repo builds and much stronger.
- **A real named audience.** The story viewer list is real creators; each avatar then morphs
  to a `$` icon with a green glow. Recognisable names doing the work that a number cannot.
- **Directional motion blur** on the fastest scale changes. Not a stylistic flourish — it is
  what stops a 1.4s scale move from strobing.

### The emotion beat

At ~0:05: gold serif `Congratulations` over **fireworks**, full frame, carrying **zero
information**. The current mute test would delete this. It should not — see the carve-out in
`SKILL.md` §3b. One per video, and it must be nameable as an emotion.

---

## S3 — the hook teardown
`AQN-7UQ9kk43YLrxJfldTbJ…mp4` · 48.3s · TWO-WORLDS

**The best example of proof-by-repetition, and of annotating live third-party footage.**

### Structure

**World 1** — outdoor A-roll, speaker holding a laptop, small white captions low in frame,
big neon-green (`#C6F000`-ish) chapter punches: `EXAMPLE #2`, `EXAMPLE #3`.

**World 2** — full-frame **solid neon green**. A small portrait window plays the *real source
reel*, watermarked with the real handle, with a real view badge under it. Beneath, the
analysis fills in line by line **as the source plays and the speaker narrates it**:

```
OUTCOME:          If giving yourself a blowout
3 PAIN POINTS:    - Pulls out too much hair
                  - Takes too much time
                  - And ultimately just pisses you off
INTRO TO SOLUTION: ...
```

World 2 runs **three times, identically**, with three genuinely different niches:
a hair account (1.6M) · a dog-training account (2.3M) · a baking account (416K). Three real,
named, unrelated creators — the *unrelatedness* is the argument, and the follower counts are
what make each one land as a real account rather than a mockup.

### Devices to steal

- **Live annotation of playing footage.** The source video keeps running while the
  annotation builds beside it. Not a screenshot with labels — a clip with labels arriving on
  the beat. This is what "show the noun" looks like at full strength.
- **Identical repetition as the argument.** Three runs, same layout, different content. The
  sameness *is* the proof that the structure generalises. `SKILL.md` §3b's "vary the device"
  rule bans this; it now carries a carve-out.
- **Long-form text, and it works** — because world 2 has no competing caption. This is
  WORKSHEET mode.
- **The brace connector.** The hook shows three thumbnails with real counts `1.6M` / `2.3M` /
  `416K` and a curly brace converging on one label: `TALKING FORM`. It is a *relationship
  diagram*, not a card — it states "these three different things share one structure" without
  words.
- **The callback resolved.** At ~0:36 the three thumbnails return, now labelled with their
  niches (`Hair Tutorial` / `Dog Training` / `Baking`), and the brace now converges on the
  full three-part formula. **The opening question gets its visual answer.** This is the
  cleanest motif payoff in the corpus.
- **Recolour as emphasis.** The formula card's text turns from white to neon green in place
  when it becomes the active idea. No new card.
- **Deliberate blur as curiosity.** The CTA resource — a Google Doc — is shown *blurred*.
  You can see it is dense and real; you cannot read it. Withholding, done honestly.

---

## S4 — the power words reel
`AQOSfLVVpoIw8clZcu9qmkoi…mp4` · 51.0s · OBJECT-OVER-GROUND

### Devices to steal

- **The hook already does what this repo's own docs prescribe and never build.** `STOP USING`
  (red) / `HOOKS` (white), two-tone, over a **real retention curve** — `100% / 50% / 0%`
  axes, `00:00 → 01:10`, a red line falling off a cliff in the first two seconds.
  `SKILL.md:172` literally uses "a retention curve falling off a cliff, real axes" as its
  example of good invention. S4 is the proof it works.
- **Phone in hand, rebuilt Reels UI.** A real hand holding a real device; inside it, IG Reels
  chrome rebuilt accurately — back chevron, `Reels` title, camera icon, like/comment/share
  column with counts, handle + `Follow` pill, caption line, bottom nav. The A-roll plays
  inside with its own two-tone caption. Multiple variants cycle through the same frame.
- **The tile-out.** That single phone becomes a **3×3 grid** of nine variants with the live
  A-roll as the centre cell. One object, one dramatic scale change, enormous impact. This is
  the contract's one break.
- **Annotation drawn onto real evidence.** Competitor reels (`7K`, `1.2M`) appear as rounded
  cards, **greyscaled with one word kept in green** (`SECRETS`, `MELT`), that word boxed in
  blue, with a **hand-drawn curved arrow** pointing at it. Then the cards **park** in the
  corners and stay while the speaker continues.
- **The ground recolours.** Full-frame red backlight on `SUPER`; full-frame green on
  `DISGUSTINGLY EASY` and `MIND-NUMBINGLY SIMPLE`. Emotional, not informational.
- **Pixel/glitch text** as a censor and transition texture.
- **The CTA is the actual deliverable.** A real Notion doc — `Viral Power Words 👇`,
  collapsible toggles, `Unique Power Word 2: Generate + Dangerously`, Original Hook /
  Template blockquotes with purple highlights, an embedded video thumbnail. Not a promise of
  a resource: the resource.

### Captions

Two-tone lockup, mid-frame, heavy dark halo + bloom, hard cuts, 2–4 words, frequently one
word. White line + accent line, accent chosen per beat (`green` = good, `red` = bad,
`pink`/`blue` = category). This is the corpus's most reproducible single feature and the
thing that most makes output read as "the same tier".

---

## The technique index

Where to look when you need one thing:

| Technique | Best example |
|---|---|
| Progressive disclosure / skeleton→fill | **S1** |
| A motif that returns and advances | **S1** (pyramid ×5) |
| Focus by brightness, not motion | **S1** |
| Nested scale as narrative | **S2** |
| A-roll composited inside a mockup | **S2**, S4 |
| One winner among peers (desaturate the losers) | **S2** |
| Real third-party screenshots as evidence | **S2** |
| Zoom-out context reveal | **S2** |
| Pure-emotion beat | **S2** (fireworks), S4 (washes) |
| Live annotation of playing footage | **S3** |
| Proof by identical repetition | **S3** |
| Long-form worksheet text | **S3** |
| Relationship diagram (brace) | **S3** |
| Motif payoff / callback resolved | **S3** |
| Real chart with real axes in the hook | **S4** |
| Rebuilt app UI at high fidelity | **S4**, S1 |
| Tile-out / wall of variants | **S4** |
| Greyscale with one colour kept | **S4** |
| Hand-drawn arrow + word box | **S4** |
| Two-tone caption lockup | **S4**, S2 |
| The CTA *is* the deliverable | **S4** (Notion doc), S3 (blurred doc) |

---

## The compare step

After rendering, composite the graphic over a real A-roll frame (ffmpeg fallback in
`SKILL.md` §5 — `export_frame` returns success and writes nothing on this machine), open a
still from the matching sample beside it, and answer three questions in `RESULT.md`:

1. **Does one object own the frame?** Or is this a card that arrived and will leave?
2. **Has it changed state since the last check?** Name the change. "It is still on screen"
   is not a change.
3. **Would a viewer read these two frames as the same tier?** If no, say what is missing —
   depth, real content, glow, density, or continuity.

Cheap, once per build, and the only check in the whole pipeline that asks whether the work is
any *good* rather than whether it is correct.
