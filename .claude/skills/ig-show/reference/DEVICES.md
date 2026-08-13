# DEVICES — spoken idea → visual device

The lookup table. You have a line of script; you need to know what goes on screen.

This is the practical core of the SHOW step. [BLOCKS.md](BLOCKS.md) says how each device
is built; this file says **which one to reach for**, and it is organised by the *shape of
the idea being spoken*, not by the shape of the graphic.

Every mapping here was derived from observed work, not invented.

---

## 0. The gate — before you pick anything

> **Graphics are reserved for concrete numbers, comparisons, and callouts.
> Plain explanatory lines get NO graphic.**

This is the discipline that separates the reference work from imitations of it. In the
primary-source material, most runtime is unadorned talking head; graphics appear at
"prove it," "compare it," and "here's the number" beats only. Scarcity is what makes each
one land.

Two questions, in order:

1. **What does this graphic measure, prove, or compare?** No answer → no graphic.
   Recommend a cut, a push-in, or a caption emphasis instead.
2. **Could a viewer with sound off understand the line from the graphic alone?**
   No → the graphic is decoration, not instrumentation.

A graphic that exists to fill a static shot is the problem, not the fix. Fill it from
`ig-pacing`'s cheap end of the interrupt menu instead.

---

## 1. The map

### Quantity — "a number worth staring at"

| Spoken shape | Device | Block |
|---|---|---|
| "four million views" | Number counts up, unit label beneath | `THE COUNTER` |
| "$85,730 in the account" | Counting figure on a plate with dashed chart axes behind it | `THE COUNTER` + plate |
| "we're at 60% of the goal" | Value between two labelled bounds | `THE DIAL` (analog) / `THE METER` (digital) |
| "seven categories" / "step three of five" | Ring divided into exactly N segments, one lit | `THE DIAL`, segmented |
| "$2,997 a month" | Small corner tag, not shouted | `THE CHIP` |

**Rules:** real numbers with real units — `4,000,000`, never `4M+`. If it's a projection
or an average, the label says so. `tabular-nums` on every counting figure or the digits
jitter. Segment count is computed from the number actually spoken (`360° / N`), never
approximated.

### Change — "before and after"

| Spoken shape | Device | Block |
|---|---|---|
| "went from 7,000 to 1.2 million" | Two figures, strike on the old, count from old→new | `THE DELTA` |
| "this used to cost $2,500" | Illustrated "before" scene + handwritten price annotation | `THE VIGNETTE` |
| "it collapsed" | A drawn line strikes an object, which visibly cracks | `THE IMPACT` |
| "growth over six months" | Line draws left→right, one marked point | `THE CURVE` |
| "retention falls off a cliff" | Curve crashing 100%→0%, drop line at the cliff | `THE CURVE` |

**Rule:** the after-value counts **from** the before-value, not from zero. Counting from
zero throws away the comparison, which is the entire point of the beat.

### Comparison — "theirs vs. ours"

| Spoken shape | Device | Block |
|---|---|---|
| "this hook got 7K, this one got 1.2M" | Two cards side by side with view-count badges, the winner scaled up | `THE VERSUS` |
| "most people write X, you should write Y" | Removed lines then added lines, code-review style | `THE DIFF` |
| "the wrong way / the right way" | Same caption band, accent shifts oxblood → forest | caption `.pop--bad` / `.pop--good` |
| "mine vs. the industry average" | Two stacked scales, the losing one left neutral | `THE DIAL`, dual |

**Rule:** the loser is never red-and-angry — it sits neutral (`--ink-ghost`). Making the
losing side ugly is editorialising; making it *quiet* is confident. Red is permitted only
inside `THE DIFF`, where it carries an actual meaning.

### Structure — "it's a system with parts"

| Spoken shape | Device | Block |
|---|---|---|
| "there are four steps" | Indexed rows, active row walks down per spoken beat | `THE STACK` |
| "let me define X" | Rule enters from off-frame, turns, terminates at a label | `THE RAIL` |
| "here's the actual command" | Real terminal output typing on | `THE TERMINAL` |
| "I printed boards to visualise this" | Genuinely analog — real paper, real marker, in shot | *(not a graphic — shoot it)* |

**Rule:** `THE STACK` caps at 5 rows and 4 words per row. If it needs six, it's a carousel,
not a reel. `THE TERMINAL` content must be **real** — fake terminal text is exactly the
"posing as technical" failure the whole system exists to avoid.

### Killing a claim — "that's wrong"

| Spoken shape | Device | Block |
|---|---|---|
| "everyone says you need X" → "you don't" | Claim types on, a rule strikes it, replacement lands | `THE REDACTION` |
| "you don't need to win every battle" | Hand-drawn squiggle "corrects" the phrase like a red pen | `THE ANNOTATION` |
| "stop doing this" | Caption word turns oxblood as it's said | caption `.pop--bad` |

**Rule:** the strike rule is `--ink`, not red. Killing a claim quietly is more confident
than killing it loudly. **Never redact a named person.**

### Proof — "here's the receipt"

| Spoken shape | Device | Block |
|---|---|---|
| "look at the analytics" | Real screenshot, darkened to ~72%, corner brackets, source label | `THE PROOF PANEL` |
| "I got this DM" | Same, with names and figures blurred | `THE PROOF PANEL` |
| "4,912,004 views" as an aside | Quiet corner tag with the figure | `THE CHIP` |

**Rule:** never at 100% brightness — a bright screenshot over a dark grade is the loudest
amateur tell there is. Redact anything not yours to show with a 6px blur bar, never a
black box: a black box looks like hiding, a blur looks like discretion.

### Scale and overwhelm — "there's too much of it"

| Spoken shape | Device | Block |
|---|---|---|
| "you've been scrolling for hours" | Full-frame mock feed grid of near-identical thumbnails | `THE MOCK UI` |
| "everyone's searching for this" | Fake search bar with autocomplete typing out | `THE MOCK UI` |
| "there are a hundred tools" | Dense grid, one cell lit, the rest ghosted | `THE MOCK UI` |

**Rule:** mock UI is monochrome — black ground, bone text, ghost chrome. Only real
thumbnail art may carry colour. A full-colour UI recreation reads as a screenshot you
forgot to grade.

### The hook — "one line, first three seconds"

| Spoken shape | Device | Block |
|---|---|---|
| the opening assertion | One line, slams in a single frame, one word accented | `HOOK SLAM` |

**Rule:** exactly one per reel, in the first 3 seconds, ≤7 words. Never combined with a
counter, a dial, or a caption on the same frame. Nothing competes with the first line.

### The ask — "do this"

| Spoken shape | Device | Block |
|---|---|---|
| "comment WORD and I'll send it" | One instruction line, trigger word accented in quotes | `THE END CARD` |

**Rule:** one CTA. Comment trigger *or* DM word, never both, never "link in bio" as well.
On screen ≥1.8s or it isn't readable at scroll speed. **Zero UI chrome** — no handle, no
logo, no follow banner, no arrows.

---

## 2. The colour-coding technique

Worth calling out separately because it is the highest-leverage trick in the corpus and
costs almost nothing.

Don't recolour words for decoration. **Let colour carry the argument:**

- the bad example / the old way → oxblood (`.pop--bad`)
- the good example / the new way → forest (`.pop--good`)
- the live value / the one thing that matters → accent (`.pop`)

Observed in the wild: "super easy" appears in red, then "mind-numbingly simple" appears
in green, and the background glow shifts with it. The viewer understands which one is
being endorsed before parsing the sentence.

This also solves a practical constraint — the caption face ships in a single weight, so
weight-based emphasis isn't available. Colour and scale do the job instead, and do it
better.

---

## 3. Match-cut chaining

The hardest-to-fake, most premium-reading technique found in the research.

Consecutive graphics are **parented so one's exit motion continues into the next's
entrance.** The second element inherits the first's velocity and direction rather than
starting from rest. The result reads as one continuous move through a scene instead of a
sequence of independent pop-ins.

```js
// element B enters carrying A's motion, instead of from zero
tl.to(a, { x: -180, opacity: 0, duration: 0.30, ease: "power2.in" }, 1.40)
  .from(b, { x:  180, opacity: 0, duration: 0.34, ease: "power3.out" }, 1.46);
```

The 60ms overlap is what sells it. Cut the overlap and you get two separate animations.

---

## 4. Overlay or cutaway?

Two modes, and the research found both used deliberately:

| | **Overlay** (alpha `.mov`, sits over A-roll) | **Cutaway** (full-frame `.mp4`, replaces the shot) |
|---|---|---|
| Use for | chips, counters, dials, rails, annotations | hook slams, diffs, curves, terminals, mock UI, end cards |
| The speaker | keeps talking underneath | is off screen |
| Needs a scrim? | only its own box, feathered | no — the graphic supplies its own ground |
| Risk | covering the face | breaking the connection with the speaker |

**Default to overlay** for anything short and additive; **cut away** when the graphic *is*
the beat. A cutaway held longer than ~3.5s starts to feel like a different video.

**Never park a graphic over the face.** Overlays go above the head or below the caption
band — never across the eyes or mouth.

---

## 5. Density

| Rule | Value |
|---|---|
| Graphics per 30s reel | ≤ 8 |
| Gap between graphics | 3–5s |
| In the first 3 seconds | exactly 1 |
| Two overlays at once | never |
| Longest cutaway | ~3.5s |

Note this is *graphics* density, not *interrupt* density. `ig-pacing` wants something
changing every 1–2s — most of those changes are caption hits, SFX, and push-ins, which are
cheap. Graphics are the expensive interrupt and stay rationed.

---

## 6. Landing them

**Land the graphic on the word, not the sentence.** The entrance frame is the frame the
spoken keyword hits. One frame late reads as lag.

Cue every graphic off a timecode **and** a specific word — `00:00:12:18 · on "million"` —
so `ig-sound` and `ig-pacing` can key off the same instant. Verify with `export_frame` at
the cue; a tool returning success is not proof the graphic landed on the right frame.
