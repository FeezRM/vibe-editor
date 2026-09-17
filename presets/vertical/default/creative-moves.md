# creative moves — the basic-tier vocabulary

Ten presets. Consistent and defect-free beats spectacular and broken. The plan author's job is to
match each *beat* to the one preset that shows what the words cannot, filled with real material.

## Match the beat

| The speaker… | Use | Fill it with |
|---|---|---|
| makes the claim / lands the payoff | `phrase` | the exact words, one accent (mutes captions) |
| lists things | `list-card` | the spoken items in order; rows land on the words |
| describes a process, a before → after | `flow` | 2–4 nouns; the last node `hi: true` when it is the point |
| says a number | `metric` | the number **and its provenance** |
| names an app / page / profile / DM | `app-mock` | a real capture (`workflows/capture-url.py`), one annotation max |
| proves something (date, result, doc) | `receipt` | a real still, a factual label |
| generalises ("everyone", "all of these") | `thumb-wall` | 2–12 real images; hero or strike |
| gives the CTA | `chat` | the literal comment word; `creator.handle` |
| turns from bad to good, or wins | `wash` | `bad` → `good` pair; once or twice per video |
| points at the footage itself | `rec-frame` (+ a zoom punch) | nothing |

## Taste rules

- **Show the noun.** If the footage already shows it (he holds the phone up), punch in instead.
- **Vary the device.** Three of the same preset in a row is a warning; four is a failure.
- **Placement is computed** (`auto`): beside the side the face is not on; inline sits below the
  caption band; cutaway only with a caption mute.
- **Reveal on the word.** Every row / node / message has a `reveal_at` that lands on the word naming it.
- **One text layer.** Only `phrase` mutes captions; everything else lives with them.
- **Presence** ≥ 60 % of runtime for basic tier. The beat matters more than the percentage.
- **Never invent.** No placeholder rows, no estimated numbers, no duplicate assets pretending to differ.

## Opening (0–8 s)

Proof or action at frame zero, never a topic label over a talking head. A number → `metric` at ≤ 0.5 s;
a result → `receipt`; a claim → `phrase` with the strongest word accented, and a proof object by 2 s.
Something changes by second five.
