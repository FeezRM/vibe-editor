# vertical/tiktok-sans

Captions in TikTok Sans Black (OFL, `default/fonts/TikTokSans-Black.ttf`), lowercase, white with the default halo.
The accent word is the same face, slightly larger, in colour (`em`/`hot` yellow, `good` green, `bad` red) instead of
the Playfair italic. Everything else is `vertical/default`.

## Framing (2026-10-26)

`framing.face_w` 0.31 frames to a face size, not a fixed zoom: the lane scales by `max(scale, face_w / median raw face
width)`, capped at `max_scale` 2.0 (1:1 pixels on a 2160-wide source). A seated take lands near 1.6×, a standing one at
2.0×. The face then fills the head zone, so `graphics.top_top` 130 / `top_h` 260 keep a top graphic (and `comment`'s DM)
above the hair; ad-stack and shatter go `inline` under the captions.
