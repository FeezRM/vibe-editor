---
name: ig-pacing
description: "Keeps a short-form edit from ever going flat by auditing and filling pattern-interrupt gaps — something changing on screen or in the mix at least once every 1-2 seconds — and owns zoom pulses and shot-scale alternation, driving Adobe Premiere Pro over MCP to place the fixes; the interrupt budget is spent on the graphics/caption layer as often as on the cut, so a single static talking-head take can still cut fast. Use this as step 6 of the editing SOP, after captions/graphics/music/SFX exist, whenever an edit feels boring, drags in the middle, needs energy, or needs its retention risk audited before export. Triggers: pacing, pattern interrupt, this feels boring, add zoom, zoom pulse, push in, shot scale, it drags, retention, keep attention, energy, the middle sags."
---

# IG Pacing — Pattern Interrupts

Step 6 of 6. By now captions, graphics, music, and SFX already exist on the timeline. This step's only job: make sure nothing sits still for too long. Owns zoom pulses and shot-scale alternation. Don't overthink it — audit the gaps, fill the cheapest way that works, move on.

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

## The corrected interval

The SOP says "something happening every 3-5 seconds." **That number is too slow — supersede it.**

Measured from a real 40-second short's actual Premiere timeline: 7 video tracks + a dedicated caption track firing continuously, 40-60+ individual clip instances in 40 seconds, A-roll cut every ~3s with graphic tracks landing bursts every 1-3s on top. Measured independently from a primary-source 45-second short: a new graphic/caption/overlay change every **1-3 seconds**, longest static beat ~3-4s, essentially continuous visual/audio interrupt.

**Working rule: something changes on screen or in the mix at least once every 1-2 seconds on average, and never let a beat run past ~3-4 seconds with nothing changing.** 3-5s was someone's guess; 1-2s is what fast edits actually measure at.

---

## The reframe: interrupts don't need a cut

This is the finding that should shape how you spend the budget. In the primary-source short above, the camera **barely cut** — one near-static talking-head take, essentially locked off, for the whole 45 seconds. The fast feel came entirely from graphics and captions changing every 1-3 seconds on top of that one shot. Zoom/push simulated via scale, not a dolly.

Implication: **the interrupt budget can be spent on the graphics layer instead of the footage layer.** A creator with one clean take and no B-roll can still cut fast — spend the budget on caption swaps, emphasis hits, and overlay changes instead of forcing hard cuts the footage doesn't support. Don't reach for a cut just because the SOP says "pattern interrupt" — check the graphics layer first.

---

## The interrupt menu, ranked by cost

Cheapest first. Default to the cheapest one that fills the gap; escalate only when the beat actually needs it.

1. **Caption emphasis hit** — color/weight swap on the power word, a new phrase popping in. Costs nothing, already scheduled by the caption pass.
2. **SFX** — soft click/whoosh/riser landing on a beat. No visual change required.
3. **Zoom pulse** — push in on the line that matters (spec below).
4. **Graphic** — a stat card, badge, arrow, icon landing/leaving.
5. **B-roll insert** — 0.8-2s cutaway that covers and illustrates.
6. **Angle/shot-scale change** — cut to a different framing of the same take.
7. **Hard cut** — most expensive; a real edit point, not just a layer change.

Work down this list when auditing a gap. If a caption swap alone closes it, stop there.

---

## Zoom pulse spec

- Slow push-in on the important line: **2-4% scale increase over ~1.2s**, then cut wide to reset. Never a visible/obvious zoom — if the viewer consciously notices "the camera zoomed," it's too big or too fast.
- Implement with `add_keyframe` on scale (and position if the push should also re-center the subject). Verify placement and value with `get_keyframes` — don't trust the call, read the keyframes back.
- One pulse per beat, not continuous creeping motion. Reset to the base scale on the next cut/shot-scale change, don't stack pulses.

## Shot-scale alternation spec

- Adjacent beats must differ in scale: **MED → CU → MED-WIDE → CU**, never the same size twice in a row.
- An identical medium shot held 30+ seconds is a retention problem no graphic fixes — that's a footage problem, kick it back to the spine (ig-cut) or force a scale change via reframe/zoom, not just another caption.
- **Longest permitted static beat is ~3-4 seconds.** Past that, something — cut, scale, graphic, or caption — must change, no exceptions.
- The hook (0-3s) is the densest region of the whole video; it should never sit still even for one beat.

---

## The gap-audit pass (the main deliverable of this step)

Run this on every edit before calling pacing done:

1. `verify_premiere_connection` first — confirm the bridge is live before touching anything.
2. Walk the timeline start to end. Log the timestamp of **every** on-screen or audible change: cut, caption swap, graphic in/out, zoom pulse, SFX hit, music beat.
3. Find every gap in that log **longer than 3 seconds**.
4. For each gap, prescribe the cheapest fix from the interrupt menu that closes it — usually a caption emphasis hit or a graphic already scheduled by another pass, not a new cut.
5. Place the fix (`add_marker` to mark the cue point first if useful, then the actual tool), and confirm with `export_frame` at the cue timecode — verify the frame actually changed, don't take the call's success on faith.
6. Re-walk the log after fixes land. No gap should remain over ~3-4s.

Report the audit as a short table: timestamp of gap start → gap length → interrupt applied → tool used. This is what "step 6 done" looks like — not a vague "pacing is good" claim.

---

## Task → Premiere tool

| Task | Tool(s) |
|---|---|
| Zoom pulse (push in / reset) | `add_keyframe` on scale/position, verify with `get_keyframes` |
| Shot-scale change via cut | `razor_timeline_at_time`, then place/trim the next scale |
| Speed nudge to sell a push | `speed_change` |
| Cut in a transition on a hard cut | `add_transition`, `add_transition_to_clip`, `batch_add_transitions` |
| Mark a gap or a cue point during audit | `add_marker` |
| Verify a fix actually landed | `export_frame` |
| Confirm bridge is live before starting | `verify_premiere_connection` |

No other Premiere tools are needed for this step — captions, B-roll placement, and SFX levels belong to earlier passes; this step only times and fills the gaps between them.

---

## Banned

- Constant shake/spin/whip on every beat — reads cheap, not fast. Interrupts need a baseline of calm to interrupt against; if everything moves, nothing reads as a hit.
- Zoom pulses stacked on top of each other or left running past the reset point.
- Treating "pattern interrupt" as "must be a cut" — check the graphics layer before reaching for the razor.
- Filling every single second — diminishing returns. A gap-audit that flags 1s as a violation is over-tuned; 1-4s is the working band, not a hard floor of zero stillness.

---

## QA checklist

- [ ] Walked the full timeline and logged every visual/audio change with a timestamp.
- [ ] No gap longer than ~3-4 seconds anywhere, hook (0-3s) included.
- [ ] Each fix used the cheapest tool from the interrupt menu that closed the gap — not a reflex hard cut.
- [ ] Adjacent shots differ in scale (MED/CU/MED-WIDE alternation) — no two same-size shots back to back.
- [ ] Every zoom pulse is 2-4% over ~1.2s, resets to base, verified with `get_keyframes`.
- [ ] No beat has more than one interrupt type stacked on it without reason (no shake+zoom+SFX all firing at once).
- [ ] `export_frame` checked at every fixed gap — the frame actually changed, not just the timeline metadata.

---

## Handoff

Consumes graphics from `ig-show` and SFX cues from `ig-sound` — this step doesn't create new assets, it times gaps between what those steps already placed and, where a gap remains, cues a caption hit, zoom pulse, or scale change off the same timecodes those steps used. If a gap can't be closed without new B-roll or a new graphic, kick it back to the relevant earlier step rather than inventing an asset here.
