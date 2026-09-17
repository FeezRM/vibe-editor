# presets/vertical/default — the house look for 9:16

This folder is the WHAT. Every node reads `numbers.json`; nothing here is app-specific.

| File | Read by | Holds |
|---|---|---|
| `numbers.json` | every node | every constant: canvas, cut thresholds, caption geometry, graphics timing, pacing, audio targets, export |
| `captions.md` | `ig-captions`, `plan-captions.py` authors | the caption look in words, pointing at the numbers |
| `creative-moves.md` | `ig-show`, the plan author | when each of the ten presets is the right answer, and the taste rules |
| `transcript-corrections.json` | `transcribe.py` | phrase → replacement (product names, the creator's name); the only place the transcript is edited |
| `sfx.json` + `sfx/` | `sfx-plan.py` | verb → file; a synthesised default pack, replace with your own |
| `fonts/` | every composition | Anton (OFL) as the caption/display face |

Tuning the look = editing `numbers.json`, then `tests/regress.sh` (goldens will move — re-write them
deliberately with `build-graphics.py --preset … --write-golden`).
