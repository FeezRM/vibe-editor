# pixel-quest

A spoken money goal, played as a tiny video game. A pixel-art hero dressed like the creator (`look`) spawns on a
brick ledge, sprints to a `$` block and punches it on the spoken number (`reveal_at[0]`); coins spin out of the
block into an arcade counter that rolls up from dim leading zeros to the REAL value while it shifts from
`color_from` to `color_to` (white → green), and lands (`reveal_at[1]`, on the unit word) with a pixel-step pop,
sparks and the hero's arm in the air. The block goes grey: the goal is cashed in.

Use it for one money number the speaker says — a goal, a price, a monthly figure — when the line is the hook or
the payoff. Wrong for a number that isn't spoken (provenance is enforced) or for anything that isn't money.

- Placement: `top` (default, above the head — the wall reads as the sky) or `inline`.
- Needs ≥ 1.6 s to read: spawn and run ~0.8 s, the jump peaks on the bonk, the count runs to the landing.
- `look`: dress the hero from the creator's own footage (hair, skin, shirt, `shirt_accent` for a logo, pants,
  shoes, `glasses`, `beard`). The default is neutral so the example and golden carry no creator likeness.
- `unit` (e.g. `/MO`) only shows when it clears the block; the caption already carries the word.
- Everything is drawn on 8× pixelated canvases from `t` alone (`_pixel.html`), so it seeks and renders deterministically.
- Callback: `pixel-crowd` uses the same hero, ledge and font — the game world can return later, changed.
