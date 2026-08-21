# templates/base — the starter, not the standard

A lint-clean HyperFrames project you can copy as a starting point. `npx hyperframes lint`
passes on it out of the box, and `tokens.css` here is a generated copy of the **default**
brand — replace it with your own (`cp brand/tokens.css projects/<slug>/tokens.css`) as soon
as you scaffold a real project.

## Read this before you judge the four blocks

`compositions/` holds four tiny demo blocks — a hook slam, a dial, a meter, a counter, a
chip. **They deliberately fail the motion floor:**

```
python analysis/motion-density.py --baseline templates/base/compositions/*.html
→ 0/5 compositions clear the motion floor.
```

That is the correct result, not a broken repo. The floor (≥25 tweens, ≥6 animated
properties, ≤50% fades, ≥1 element with depth) applies to a **scene** — one persistent
object mutating through a labelled state machine for 15–40 seconds. These are single blocks
showing the mechanics of the contract: the `data-*` attributes, the paused timeline
registered on `window.__timelines`, root-relative asset paths, deterministic values only.

Copy the *plumbing* from them. Get the *ambition* from
`.claude/skills/ig-show/reference/SAMPLES.md`.

## Scaffolding a real project

```bash
cd projects
npx hyperframes init <slug> --example blank --non-interactive
cd ..
cp brand/tokens.css projects/<slug>/tokens.css
mkdir projects/<slug>/textures
```

Then plan every beat in `projects/<slug>/MOTION-PLAN.md` before you build a composition.
`ig-show` owns that process end to end.
