# samples/ — your reference corpus

**Empty on a fresh clone, and that is correct.** This folder is a bring-your-own slot.

The reels this repo's style was measured from are real creators' copyrighted work. They are
not redistributed here, and neither is any other footage — see the media rules in
`../.gitignore`. What *is* shipped is the analysis: `TEARDOWN.md` (style measurements),
`SAMPLES.md` (the structural teardown), and `VISUAL-HOOK.md` all carry the findings, so the
skills work with this folder empty.

## What to put here

Three to five short-form reels you want the output to resemble — **yours, or ones you have a
right to keep a local copy of.** Anything in `samples/` is gitignored, so nothing you drop
here is ever committed or published.

```
samples/
  01-<what-it-does>.mp4
  02-<what-it-does>.mp4
```

Name them for the *device* they demonstrate, not the account they came from.

## What the skills do with them

| Skill | Uses `samples/` for | With the folder empty |
|---|---|---|
| `ig-show` | Step 1 of the asset acquisition ladder — reuse a frame you already have | Falls through to the next rung; nothing breaks |
| `ig-show` §"compare against the corpus" | Pull a still with `ffmpeg -ss <t> -i samples/<file> -frames:v 1 ref.png` and hold it beside your composite | Compare against the written spec in `SAMPLES.md` instead |
| `ig-delivery` | The final QA side-by-side | Checklist item is skipped; say so in `RESULT.md` rather than claiming it passed |

## The one hard rule

**Copy layout, never identity.** Every account, handle, display name, and avatar in a mockup
uses `creator.handle` from `brand/brand.json`. Lifting a handle out of a reference reel puts
a real person's name in your video. `ig-show/SKILL.md` bans it and the pre-render checklist
greps for it.
