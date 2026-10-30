# STYLE — what the reference reels do

Measured 2026-10-27 from the 8 reels in `samples/` (see `INDEX.md`): seated talking heads, 8–42 s, 1080×1920,
24–30 fps. Every number below was read off the files; where something is a judgement it says so. The mechanical
values are in the look `presets/vertical/samples` — start every job with `--preset vertical/samples`.

**The approved baseline edit is `samples/BASELINE.md`** (9278 v5, 2026-10-28). This file describes the reference
reels; that one shows the level a finished edit from this pipeline has to reach. Read both.

---

## The shape of a reel

- **Speech starts on frame 1** (first word at 0.07–0.10 s in all 8). No intro, no logo, no lead-in.
- **The hook is said in the first 1–2 s and is shown as big text**: the hook words appear as keyword captions (heavy
  italic caps, one in a colour) — "NEVER / EVER", "IF YOUR / INSTAGRAM / PROFILE / LOOKS LIKE / THIS…", "NEVER WEAR
  WHITE AGAIN…", "THESE ARE / ALL 5 TOOLS / YOU NEED". After the hook, captions drop to normal lowercase.
- **A visual lands within the first second** in 6 of 8: an icon under the word (Instagram logo at 0.27 s), a screenshot
  over the head (profile at 1.0 s), a row of 5 gold "?" blocks for "5 tools", a cut-out reaction image, the example
  clip itself.
- **Body**: one idea per 2–5 s, each with at most one visual. Lists are numbered on screen ("1.", "2." as giant
  white italic numerals in the caption spot, held ~0.5 s, then the item name + its real logo).
- **The end is the CTA, said and shown**: `comment "WORD"` with WORD in cyan inside quotes (01, 03, 07), often followed
  by 1–2 s of the thing being offered (a scroll of the actual doc/guide, full screen); or `follow for more sauce` with a
  follow button animating under the caption (red "+" → white circle → check, 0.75 s) (04, 08). Ends on the last word —
  no outro, no end card.

## The cut

- **No pauses at all.** Median gap between words 0.04–0.08 s, 90th percentile 0.10–0.18 s, longest gap in a whole
  reel 0.18–0.34 s (WhisperX, all 8). Breaths are gone. Speech runs 236–304 words/min. The only longer silences are
  deliberate: 05 holds ~0.6–1.4 s for each ✗/✓ stamp, 08 lets the subject's clip play for the 8 s cold open.
- **Jump cuts on a locked camera**: the face stays the same size and position across every cut (face width 0.23–0.28
  of the frame for the whole of 04 and 08). Only the pose changes. No dissolves, no whip transitions between takes.
- Different takes/outfits are used *on purpose* as a device: 05 alternates a dark sweatshirt ("bad") and a denim
  jacket ("good") per comparison; 06 cuts from a white tee to a black tee on "instead wear any other color".
- Real b-roll from the creator's own footage is cut in for 1–2 s when it literally shows the line: a hand hitting
  "post" on a phone (04, 9.3 s), him outdoors for "take a sexy pic of yourself" (03, 8.0 s), him in another room
  scrolling for "you go find a viral video" (08, 18.5 s), a laptop screen being scrolled (04, 07).

## The camera

- **Framing**: seated, head-and-chest, **face width 0.22–0.30 of the frame (median 0.255), face centre at 0.29–0.37 of
  the height (median 0.33)** — measured on all 8 with the face finder. A raw shot wider than that is cropped in once
  for the whole video to match (`framing.face_w` 0.255, `face_y` 0.33 in the look). Never re-cropped per clip. The
  9278 raw at source framing had the face at 0.20 wide and 0.43 down: "the frame and default zoom is off".
- **No zoom punches in the body.** Across all 8 reels the face size never steps up mid-video.
- **The one move: an opening zoom-out.** 4 of 8 (03, 04, 06, 07) open ~1.35× punched in and ease out to 1.0× over
  the first 6–8 frames (0.2–0.27 s), on the first word. It is fast enough to read as an impact, not a camera move.
  (`pacing-audit.py --zoom-out-open 35`.)
- Split screen when a screen recording needs room: the talking head keeps the top ~half (face moves up to ~0.25),
  the recording fills the bottom 40–50 % edge to edge, the caption sits on the seam (03 at 9.3 s, 08 at 20.5 s).

## Captions (look: `presets/vertical/samples`)

- **One line, 1–3 words**, hard cut on and off, no animation, no box, no stroke — white with a soft drop shadow. No
  periods or commas; `?`, `!` and `…` only where they add tone ("INDIANS???", "THIS…").
- **Position: the exact centre of the frame** (block centre y 960–968 of 1920, baseline ~990), over the chest.
  Width 28–55 % of the frame.
- **Font: Europa Grotesk SH Bold** (the creator's own font; TikTok Sans is the fallback), ~84 px (line widths of
  "you lowkey" / "will get you" / "he takes a" fit 86–89 px at zero tracking), tracking −0.01 em. Confirmed by the
  creator 2026-10-27 after TikTok Sans read as wrong.
- **Case**: lowercase, but names keep their capitals ("and Instagram", "PS5", "for Tony", "cuz ChatGPT") — `case:
  natural`.
- **Keywords** (roughly 1 group in 6–10): the whole group switches to **Tactic Sans Ultra Italic** caps (wide, heavy,
  true italic — "INSTAGRAM" is ~600 px wide → ~87 px), in one colour — cyan "PROFILE PICTURE" / "RIZZ UP" / "MCPs", green "BLEW UP" / "GOATED" / "YOUR NAME", yellow "YOUR BIO",
  red "COOKED" / "THIS…", white "THE ALGORITHM" / "3 LINE FORMAT". A single word can go red caps inside a lowercase
  line ("does NOT"). Set them in `captions.overrides.json` → `{"keywords": {"profile picture": "cyan"}}` and
  `{"accents": {"not": "bad"}}`.
- Colours are pure and saturated: red `#E80000`, green `#13FF12`, yellow `#FAFF0A`, cyan `#13FFFB`, magenta
  `#E300F6`. Red = wrong/never/bad, green = good/win, cyan = the thing to remember or the CTA word, yellow = a
  feature/section name. Colour follows meaning, not rotation.
- Captions keep running over every cutaway, split and screen recording, in the same spot.
- A persistent **section label** is used when the video is a comparison or a list of types: 05 keeps "BAD ENERGY" (red)
  / "GOOD ENERGY" (green) caps at the top (y ~0.15) for the whole section; 01 builds "THIS IS A / RAGEBAIT / HOOK" word
  by word on the left at y 0.62–0.75 and holds it while the example plays. Then plain captions are not shown.

## Graphics — what gets shown

The rule the samples follow: **show the real thing he names, small and fast, or cut away to it fully.** Kinds seen,
by how often:

| Kind | Where / size | Timing | Examples |
|---|---|---|---|
| **App logo / icon** under the caption | centred, just below the caption, ~150–190 px | appears with the word (hard cut), leaves with the caption group, 0.5–1 s | Instagram, TikTok, Claude, Notion, Hemingway, Google Trends, Vidyard logos; ghost for "ghosting"; peach emoji; flying-money emoji for "blew up" |
| **Real screenshot / UI card** on the chest | centred under the caption, ~40 % width | fades in ~0.3–0.5 s, holds across several captions (2–5 s) | the $2,997 offer page (02), a profile header (03, top of frame), a readability score panel (07), "▷ 4.9M" view-count pill under "mega viral video" (02, 08) |
| **The example clip** playing (other creators' reels he's talking about) | picture-in-picture 9:16, ~32–43 % width, top-right (01) or bottom-left (08), no border, sharp corners | slides/fades in ~0.3 s, plays with its own audio while he waits; a "1.4 m views" label fades in beside it ~1.5 s later | 01 (one per hook type), 08 (cold open + while he explains) |
| **Full-screen cutaway** | rounded-corner card (~60 px inset, ~30 px radius) on black, or edge to edge | 1–4 s, captions continue on top | screen recordings of the tool/site (Google Trends, a script timer with the cursor dragging a doc in), a meme reaction (anime "taking notes" for "save this"), his own b-roll |
| **Verdict stamp** | big red ✗ or green ✓ (~600 px) over his torso, footage desaturated underneath | pops in on the verdict word, 0.5–0.75 s, with a hit SFX | 05 (every comparison), 02 ("afford them") |
| **Numbered list card** | full screen on a deep purple gradient, items stacked at y 0.3/0.5/0.7, yellow/cyan/green caps | builds item by item on the words, then fills with a real example | 03 (bio "3 line format") |
| **Light-leak flash** | full frame warm orange/pink | ~0.25 s, on a punchline word or into b-roll | 04 "STUPID", 08 into b-roll. **Rejected as "tacky" when the pipeline did it (9278 v4): don't use it** |
| **Cut-out reaction image** | under the caption, ~40 % width | 0.5–1 s | a person cut-out for "INDIANS", a streamer screaming for "INDIANS???" (02) |

How often: **a new real visual every ~2–3 s** — three visuals in an 18 s reel read as "barely any visuals" to the
creator (2026-10-27). Stretches of 2–4 s with only the face and captions are normal in every reel (04: 11.0–16.0 s; 08: 23.8–27.3 s). Nothing is decorative: every visual is the noun or verb being said
at that moment.

Motion style: almost everything **hard-cuts in on the word** and hard-cuts out with the caption. The only eased moves
are fades on bigger cards (~0.3–0.5 s), the PIP slide-in, the follow-button morph and the opening zoom-out. No
bouncing, no spinning, no elastic overshoot, no text typing animations except the list card.

## Sound

- **Loud master**: −11 to −13 LUFS integrated, peaks at 0 dBFS (look sets −13 LUFS, −1 dB peak).
- **A quiet music bed under the voice in most reels** (03, 07 show a continuous tonal bed in the spectrogram; the
  quiet floor sits only 3–6 dB under speech in the gaps). 05 has none.
- **SFX on the verdicts and transitions, not on every graphic**: 05's ✗/✓ each land with a hit; whooshes with the
  light-leak flashes. Icons appear silently.
- Example clips play with their own audio while he is silent.

## Never (absent from all 8)

- Light-leaks, glows or flashes as emphasis. The samples have two, and the creator rejected ours. Emphasis is a
  keyword caption.
- A stand-in clip that only loosely matches the line (stock typing for "tell it to…"). Show the thing itself, or
  act it out (see BASELINE.md).

- Text boxes or cards that restate what he is saying (the only text-only screens are the list card and section
  labels, both structural).
- A graphic on every line, or anything on screen that isn't the thing being said.
- Zoom punches or slow push-ins during the body; per-clip re-framing.
- Slow zooms on stills, Ken Burns, parallax.
- Transitions between takes (dissolves, whips, spins).
- Caption animations (pop, bounce, typewriter, word-by-word highlight karaoke).
- Two-line captions (except a keyword stacked on two lines) and captions in the bottom third.
- Stock footage, stock icons in a different style per beat, invented UI, borders/drop shadows/frames around clips.
- Intros, outros, end cards, logos.

## What makes them engaging — and where there's room to vary

- The hook is **said and shown big in the first second**, and something real appears before 1 s.
- **Proof on screen**: real view counts ("1.4 m views", "▷ 4.9M"), real prices, real UIs, the actual example videos.
- **Format devices carry the structure**: a numbered countdown (07), a type-by-type showcase with the example playing
  (01 — the 973K one), a bad/good comparison with outfit changes and verdict stamps (05), a reaction with the subject's
  clip open (08), a step-by-step screen walkthrough (02, 03). Pick the device that fits the script; the samples show
  that each video commits to one.
- **Payoff for the CTA**: the offered thing is shown, not just named.
- Room to vary: which device, where the PIP sits, when to cut away fully vs. keep the face, the colour of a keyword, a
  meme cutaway for comic timing (04, 07). The constants are the captions, the locked camera, the zero-pause cut and
  "only real things".

## Per sample (short)

- **01 hook types (973K)** — 31.6 s. Five sections "THIS IS A [TYPE] HOOK", title built word by word at left-centre,
  type word in its own colour (red/yellow/cyan/magenta/green); each section a PIP of a real example reel top-right with
  a view count; no running captions. CTA "COMMENT "HOOK"" then 1.5 s full-screen scroll of the hook library doc.
- **02 settings walkthrough (26K)** — 29.6 s, wide framing. Cut-out reaction images on "INDIANS", IG icon, the $2,997
  offer card held 4.5 s then ✗; "▷ 4.9M" pill; 7 s full-screen phone recording of the settings path with red curved
  arrows on each tap, on a purple starfield; split (screen top, face bottom) for the result.
- **03 profile teardown (19K)** — 26.4 s. Hook as keyword captions + IG icon + profile screenshot over the head; creator
  headshot pair for "people making bank"; b-roll outdoors; split screen of the pfp site and the profile being typed;
  purple list card; CTA "guide" + doc scroll.
- **04 never post and ghost (12K)** — 30.7 s. Opening zoom-out on "NEVER" (red); caps hook captions; phone mock of
  the reel; light-leak on "STUPID"; ghost icon; real b-roll of hitting post; film-scratch overlay on "i don't care";
  laptop scroll b-roll; 4 s anime meme card; follow-button CTA.
- **05 good/bad split (8K)** — 20.2 s. Three comparisons; top label red/green; outfit change per side; ✗/✓ stamp over
  a desaturated frame with SFX after each half.
- **06 never wear white (4K)** — 8.3 s. Opening zoom-out with a 2-line caps hook, then plain captions; the cut to a
  black tee *is* the visual.
- **07 five tools (4K)** — 42.2 s, close framing. Gold "?" blocks for "5 tools"; meme card for "save this"; "1." … "5."
  numerals; each tool = keyword caps + its real logo, then 2–4 s of its real screen (rounded card or laptop footage);
  CTA "script".
- **08 reference screenshots (3K)** — 37 s. Cold open: 8 s of him scrolling with the subject's reel inset bottom-left
  playing; "?" block, "CONTENT / STRATEGY", flying money, "▷ 4.9M"; inset clips recur; light-leak into b-roll; split
  with a TikTok explore grid; follow CTA.
