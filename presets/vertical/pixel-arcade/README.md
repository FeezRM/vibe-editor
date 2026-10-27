# vertical/pixel-arcade

`vertical/default` wearing the **Pixel Arcade** graphics style: the game world of `pixel-quest` and `pixel-crowd`
applied to every preset. Born on the 9030 reel (2026-10-24), where the creator rejected a stock counter ("lacks
creativity in every single aspect") and a zooming screenshot ("nothing of substance"), and asked for a pixel-art
video-game scene with a character that looks like him.

What changes:

| Layer | Pixel Arcade |
|---|---|
| Type | **PixelQuest** (`presets/vertical/default/fonts/PixelQuest.ttf`), the same 5×7 letterforms the canvas presets draw. Built by `scripts/pixel-font.py` from `presets/graphics/_pixel.html`: edit the table there, rebuild, and both stay identical. |
| Surfaces | Square corners, brick-framed panels (`#141A2E` panel, `#3B5590` brick, `#7F9BE0` lit edge), stepped hard drop shadows. No blur anywhere. |
| Text over footage | A 1-font-pixel ink outline (`#0B0D14`) plus a hard drop, never a soft glow. |
| Colour meaning | gold `#FFC531` = the number · green `#3BFF7A` = gained / good · red `#FF4D4D` = lost / bad · pink `#FF4D8D` = love / followers · white = everything else. |
| Motion | `graphics.motion_fps: 12`: `_base.html` samples every preset's timeline on a 12 fps grid ("on twos"), so cards pop like sprites. Presets that step themselves (`x-own-steps`: the pixel-* presets) are left alone. |
| Captions | Still Inter (legibility first), with arcade accent colours and a hard ink outline. |

- `numbers.json` carries `"extends": "vertical/default"` and only the keys above; fonts, sfx, geometry and audio are inherited.
- The skin is `presets/graphics/_skins/pixel-arcade.css`. Presets own the motion, the skin owns the look.
- Pick it at intake: `workflows/new-job.py <src> --slug <job> --preset vertical/pixel-arcade`. For b-roll-driven
  talking-head reels use `vertical/broll-story`, which extends this look.
- Preview any preset in it: `python workflows/build-graphics.py --preset presets/graphics/list-card --vertical vertical/pixel-arcade`.
- The signature pieces are `pixel-quest` (money goal) and `pixel-crowd` (audience number). Dress the hero with
  `look` from the creator's footage, and reuse the same look in every graphic of a reel so it's one character.
