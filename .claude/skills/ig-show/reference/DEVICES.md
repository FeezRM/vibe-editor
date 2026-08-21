# DEVICES — spoken line → what goes on screen

The lookup that decides *what to build*. [BLOCKS.md](BLOCKS.md) says how to build it.

---

## 0. The gate

Before choosing anything, run the line through this in order:

```
1. Does the line name a THING the viewer could recognise?
      profile · story · DM · reel · comment · document · button · phone
   -> SHOW THAT THING.  (blocks 01, 02, 05, 10, 13, 14)

2. Does the line name a NUMBER, RANK, or CHANGE?
      views · followers · %  · top 10% · 72 hours · before/after
   -> DRAW THE MEASUREMENT.  (blocks 03, 04, 07, 08, 09)

3. Does the line contrast a BAD way against a GOOD way?
   -> COLOUR WASH the pair, or COMPARISON if artefacts exist.  (11, 04)

4. None of the above?
   -> Does an object from an EARLIER beat still belong on screen, dimmed?
      Almost always yes. Keep it (.dim) rather than cutting to bare footage.
   -> Only if genuinely not: NO NEW GRAPHIC. Let the caption and the cut carry it.
```

> ⚠️ **Corrected.** This section previously claimed *"roughly 40% of runtime has no graphic
> at all"* and told you step 4 fires often. **Measured, the figure is 0–15%** — S1 never
> shows a bare talking head in its entire 45 seconds. That wrong number was the direct
> cause of reels where the visuals were barely there. See `TEARDOWN.md §5` and
> `analysis/DEEP-ANALYSIS.md §7.2`.

Step 4 fires **rarely**. The graphic layer is the default state of the frame; bare footage
is the exception you spend for emphasis. Target **≥85% graphic presence**.

The way you hit that without inventing filler is **not** to build more cards. It is to keep
one object alive across many beats and change one element of it per sentence — which is
what all three references do. When step 3 returns nothing, the right answer is usually
"the object from four seconds ago is still relevant, keep it and dim it", not "cut to a
bare shot".

> **The disqualifier still stands.** If the only thing you can think to put on screen is
> the sentence itself in a nicer font — build nothing *new*. But that is an argument
> against a bad graphic, not an argument for an empty frame.

---

## 1. The table

### Things the viewer can recognise

| The line says… | Put on screen |
|---|---|
| "your profile / your bio / your name / your pfp" | **APP SCREEN** — the profile, with that field lit |
| "post a story" | **APP SCREEN** — a story frame |
| "say something like…" / "write this" | **TYPE-IN** — the words typed into the real field |
| "reply / comment / DM me X" | **THE INTERACTION** — the comment box, word typed |
| "your highlights" | **APP SCREEN** — the highlight circles filling |
| "pin your best videos" | **APP SCREEN** — the grid, pins landing on tiles |
| "this video / this reel / that post" | **CONTENT + METRIC** — the actual reel with its count |
| "scrolling / on your phone" | **PHONE IN HAND** |
| "I made a document / template / guide" | **THE DOCUMENT** |
| "hit follow" | **THE INTERACTION** — the button pressed |

### Numbers, ranks, change

| The line says… | Put on screen |
|---|---|
| "top 10% / tier / level / rank" | **TIER STACK**, one layer per rank named |
| "X views vs Y views" | **THE COMPARISON** |
| "people drop off / nobody watches / retention" | **THE CHART** — retention curve with real axes |
| "grew from A to B" | **THE CHART** (line) or **READOUT** counting A→B |
| "in the next 72 hours" | **THE READOUT** — countdown |
| "X% of people" | **TIER STACK** or a labelled bar — never a pie |
| "write 5 different X" | five real X's, or the numbered list **only if** the items get named |

### Bad vs good

| The line says… | Put on screen |
|---|---|
| "don't say X, say Y" | **COLOUR WASH** red on X, green on Y, captions matching |
| "most people do X, instead do Y" | **COMPARISON** if artefacts exist, else wash |
| "this hook flopped, this one went viral" | **COMPARISON** with both view counts |

---

## 2. Worked example — the line that broke the old system

> *"Like I used to waste so much time on a video that people didn't even watch cuz the
> hooks suck."*

**What the old system built:** a dark plate reading `WHAT A WEAK HOOK DOES`, with a tiny
unlabelled curve and the words `VIEWERS` and `TIME`, docked in a 320px strip at the bottom
of frame.

That is the caption again, plus a squiggle.

**What the reference does with the same idea** (S3, 0–2s): a **retention curve on a large
card at 57–75% of frame height**, y-axis `100% / 50% / 0%`, x-axis `00:00 → 01:10`, a red
line falling off a cliff in the first two seconds and flat-lining — under a caption reading
`STOP USING` in red above `HOOKS` in white, both at ~88px with a glow.

The difference is not polish. The reference frame **states the claim** — *viewers leave in
the first two seconds* — as a shape with units on it. The old frame stated nothing.

**Rule extracted:** when the line is about people not watching, the graphic is a retention
curve **with labelled axes**, big, directly under the caption.

---

## 3. Worked example — a hook

> *"how do you know if your hook's actually good?"*

**Wrong:** a dial labelled `BAD ← → GOOD` with a needle that never settles. Abstract; it
measures nothing; the viewer cannot tell what it refers to.

**Right:** two real hooks as **CONTENT + METRIC** cards — one that did 7K, one that did
1.2M — same topic, both readable. The question answers itself.

If no real examples exist, **ask the creator for two** rather than inventing an instrument.
Getting two real screenshots is a two-minute favour and it is the difference between a reel
that proves something and one that asserts it.

---

## 4. When the script does not name the specifics

Common, and the correct response is **not** to invent a placeholder.

The old system rendered "write 5 different hooks" as five empty numbered slots — a table
with nothing in it, which shows the viewer nothing.

Do one of:

0. **Work the acquisition ladder in `SKILL.md` §2 first.** Extract the frames from footage
   with ffmpeg or `/watch`; screenshot the real interface with Chrome automation; look up the
   real public figure; generate the texture. Most "missing specifics" are not missing, just
   un-fetched. **Ask only for what is genuinely private.**
1. **Ask the creator** for the five hooks, the two screenshots, the real number. Cheap.
2. **Use a block that does not need the specifics** — a colour wash, a tier stack, a chart
   whose shape is the claim.
3. **Build nothing** and let the caption carry the beat.

Never ship a container with placeholder contents. An empty ledger communicates less than a
plain talking-head frame, because it visibly promises information and then withholds it.
