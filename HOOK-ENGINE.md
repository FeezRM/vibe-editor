# The Vibe Editor Visual Hook Engine

The hook engine makes the first eight seconds a separate, testable product. It sits above
HyperFrames and Premiere rather than asking either engine to make creative decisions it is
not equipped to own.

## Architecture

```text
script + transcript + footage + goal
                 │
                 ▼
         EVIDENCE LEDGER
  real screens · clips · props · metrics
                 │
                 ▼
          IG-HOOK DIRECTOR
   three complete 0–8s candidates
 receipt · scene · demonstration · etc.
                 │
                 ▼
          HOOK-PACKET.json
 claim · beats · owners · score · cues
                 │
        validate-hook-packet.py
                 │
                 ▼
       3 × FIVE-FRAME STORYBOARDS
  0.15 · 1.25 · 3.25 · 5.25 · 7.25
                 │
          select or trial A/B/C
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
 HYPERFRAMES           PREMIERE MCP
 proof objects         real footage
 UI · charts           cuts · role-play
 labels · masks        timing · sound
       └─────────┬─────────┘
                 ▼
      HOOK-LAB sandbox sequence
                 │
          pixel + mute QA
                 │
                 ▼
          main edit / Trial Reels
                 │
                 ▼
      results return to hook ledger
```

## The interface that prevents improvisation

The agent writes one artifact per video:

`projects/<slug>/HOOK-PACKET.json`

It contains:

- the unchanged promise and intended buyer;
- every evidence item and its provenance;
- three complete candidates, each with 0–2, 2–5, and 5–8 second beats;
- which engine owns every beat;
- exact speech, visual change, and caption mute windows;
- a 12-point score and explicit risk list;
- the Premiere sandbox sequence name;
- five QA snapshot times and the final gate state.

The packet is what converts “make the hook pop” into deterministic work queues.

## Why the split works

| Decision | Owner |
|---|---|
| Which visual grammar fits the claim | `ig-hook` |
| Which evidence is true and available | `ig-hook` evidence ledger |
| Designed UI, charts, comparisons, masks, lockups | HyperFrames through `ig-show` |
| Real performance, source selection, cuts, split screens, timing | Premiere MCP |
| Media acquisition or generation | `media-use` / the acquisition ladder |
| Body pacing after second eight | `ig-pacing` |
| Whether the opening can ship | Hook validator + storyboard/pixel QA |

Premiere is never asked to invent the design. HyperFrames is never asked to fake footage.
The agent never edits the live sequence before the cheap storyboard decision is made.

## Seven opening modes

| Mode | Frame-zero proof | Example |
|---|---|---|
| Receipt-first | literal result | **4M VIEWS / $0** |
| Comparison-first | both outcomes | **SAME REEL / 1,469 vs 294** |
| Demonstration-first | visible mistake | white shirt swallowing captions |
| Roleplay-first | conflict already happening | “looks good here, bad after posting” |
| Interface-dive | real UI in motion | ContentSpy rejecting a hook |
| Pattern-break | repetition then disruption | **YOUR SET IS WALLPAPER** |
| Lockup-first | short thesis + one proof object | **SECOND 3 KILLED IT** |

Lockup-first is one option. The old system treated it as mandatory, which forced literal
demonstrations and receipts into the same title-card shape.

## The gate

Every candidate receives 0–2 for:

1. specificity;
2. literal proof;
3. tension;
4. meaningful second beat;
5. mute-test clarity;
6. build feasibility.

The selected candidate needs 9/12 or better and may not score zero in proof, second beat, or
mute-test clarity.

Run:

```bash
python analysis/validate-hook-packet.py projects/<slug>/HOOK-PACKET.json
```

The valid tracked example is [templates/hook-packet.example.json](templates/hook-packet.example.json).

## Operating modes

### Design mode

Create three storyboard strips, select one, and build only the winner. This is the default.

### Trial mode

Build three different openings against the same body in:

```text
HOOK-LAB__<slug>__A
HOOK-LAB__<slug>__B
HOOK-LAB__<slug>__C
```

These become genuine Trial Reel variants. Reposting the same file is not a hook test.

### Fast mode

Score three candidates on paper and build the highest one without an approval pause. The
evidence and pixel gates remain mandatory.

## Feedback loop

After publication, preserve the prediction and append the result:

- candidate and mode;
- exact 0–8 second speech;
- frame-zero object;
- Trial/feed status;
- reach, views, average watch time, saves, shares;
- qualified profile actions or DMs when the goal is leads.

Do not learn from one small upload. Below roughly 300 reached accounts, record
`insufficient-signal`. Prefer comparisons between sibling variants and use retention and
quality actions before raw views.

## Agent invocation

For a complete edit:

> Use `ig-reel`. Run `ig-hook` in design mode before touching the main sequence. Show me
> the three five-frame opening strips and the Hook Packet scorecard, then build the selected
> opening and continue the body edit.

For real hook testing:

> Run `ig-hook` in Trial mode. Keep the body identical and build three different 0–8 second
> openings in sandbox Premiere sequences. Do not duplicate the same file.

