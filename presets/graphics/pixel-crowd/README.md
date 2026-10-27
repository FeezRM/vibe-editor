# pixel-crowd

"I grew to 150K followers", acted out in the same pixel world as `pixel-quest`. The creator's hero stands on the
brick ledge; tiny pixel followers — every one a different person — run in from both edges and pack in around
them, one by one, while a follower counter (next to the creator's REAL avatar, pixelated) climbs from the growth
verb (`reveal_at[0]`) to the REAL count (`reveal_at[1]`). On the landing the counter flashes, the whole crowd
jumps and pixel hearts float up and blink out.

Use it for an audience number the speaker says (followers, subscribers, members) when a real profile proves it.
Wrong for a number without a source, or for views/money (use `metric` / `pixel-quest`).

- Placement: `top` (over the wall, where the tiny followers read) or `inline`.
- Needs ≥ 2 s: the crowd should still be arriving while the line is spoken.
- `avatar`: the creator's real profile picture, pre-pixelated to 16×16 (`PIL resize(BOX)`), shown at 8× on the same
  pixel grid as the scene. Optional — without it the counter moves to the left edge.
- `value` + `unit` + `decimals`: `151.4`, `K`, `1` → counts `0.0K … 151.4K`. Provenance is enforced.
- Same `look` keys as `pixel-quest`, so the hero is the same character in both.
