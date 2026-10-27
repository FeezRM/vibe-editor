# presets/vertical/default — the mechanical defaults for 9:16

| File | Read by | Holds |
|---|---|---|
| `numbers.json` | every node | canvas, transcript, cut thresholds, caption look, framing, audio targets, export |
| `captions.md` | `ig-captions` | the caption look in words |
| `transcript-corrections.json` | `transcribe.py` | phrase → replacement (product names, the creator's name); the only place the transcript is edited |
| `sfx.json` + `sfx/` | `sfx-plan.py` | verb → file; a synthesised default pack, replace with your own |
| `fonts/` | captions and compositions | Inter, Playfair Display Italic, TikTok Sans (all OFL) |

What the edit should look like is not here: it comes from the reference reels in `samples/` (see `samples/STYLE.md`).
