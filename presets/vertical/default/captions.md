# captions — the default look (numbers in `numbers.json` → `captions`)

One line, a few words, white with a dark halo, centred in the band `band_top`–`band_bottom`, hard cut on the frame the
first word is spoken. Font, size, case and band are numbers; change them in a look (`presets/vertical/<look>/numbers.json`
with `extends`) when the reference reels in `samples/` do it differently.

No word is accented by default. When a word earns it, name it in `captions.overrides.json`
(`{"accents": {"word": "hot"}}`; classes `em`, `hot`, `good`, `bad` → `captions.colors`).

Where a graphic carries its own words, the plan sets `"mute_captions": true` and the caption is dropped for that window.
