---
name: azure-void-image-style
description: Generate or art-direct thumbnails, posters, social graphics, concept art, and UI visuals in a luminous electric-blue-and-white aquatic editorial style inspired by modern Japanese game UI: bright azure glow, clean white space, watery depth, glass reflections, elegant typography, and restrained grayscale accents. Use whenever the user asks for the "blue-white glow" theme, Persona-3-like visual energy, aquatic blue UI art, or a clean luminous blue thumbnail aesthetic.
---

# Azure Void Image Style

Use this skill to create images that feel **luminous, clean, aquatic, graphic, and emotionally cool** without copying any existing game's characters, logos, layouts, or proprietary UI assets.

## Core visual identity

The image should read immediately as:

- **White / near-white field first** — airy, high-key, uncluttered.
- **Electric azure second** — vivid blue used as the main visual signal and glow.
- **Cool gray / charcoal third** — only for subject linework, shadows, or contrast.
- **Water + glass behavior** — soft gradients, reflected light, ripples, translucency, shimmer, subtle bloom.
- **Editorial composition** — oversized type, purposeful asymmetry, large negative space, one dominant focal subject.
- **Motion without chaos** — flowing ribbons, liquid trails, diagonal drift, soft particles, or submerged movement.

The style is not generic neon/cyberpunk. It should feel **daylight-bright, clean, elegant, and aqueous**.

## Palette

Treat these as the default palette unless the user requests otherwise.

- **Primary Azure:** `#1F84ED` — dominant vivid blue, sampled from the supplied reference image.
- **Hot Azure:** `#1371EB` — more saturated accents, edge strokes, high-energy marks.
- **Glow Cyan:** `#54B3E9` — bloom, water shimmer, reflected light.
- **Deep Blue:** `#114BC3` — sparingly for depth and the darkest blue edge.
- **Ice White:** `#F7FAFF` — main background.
- **Paper White:** `#FFFFFF` — highlights and type knockouts.
- **Mist Gray:** `#DCE3E8` — subtle environmental texture.
- **Graphite:** `#303740` — line art, subdued subject detail, never the dominant field.

Recommended visual weighting:

- 65–80% white / near-white
- 15–25% azure family
- 5–10% gray / graphite

Do not let dark navy take over the image unless the user explicitly asks for a night version.

## Lighting and material language

Use:

- blue rim light around silhouettes
- translucent watery overlays
- light caustics and soft refracted streaks
- glass-like sparkle and reflection
- feathered bloom rather than hard neon tubes
- pale fog or desaturated haze for depth
- subtle paper / print texture when the image is editorial

Avoid:

- magenta / purple cyberpunk lighting
- rainbow gradients
- black backgrounds by default
- heavy metallic chrome
- dense particle spam
- glossy 3D gaming-logo aesthetics

## Composition rules

1. **Pick one hero element.** A person, object, symbol, or headline should dominate.
2. **Create breathing room.** Keep meaningful empty white space around the hero.
3. **Use blue as a path.** A ribbon, ripple, glow trail, reflection, or diagonal form should guide the eye.
4. **Keep depth soft.** Background elements fade into pale gray/white rather than becoming detailed scenery.
5. **Prefer asymmetric balance.** Centered is allowed, but a slightly off-center hero often works better.
6. **Use one large gesture instead of many small effects.**

For thumbnails, make the focal read at phone size in under one second.

## Typography

When the image contains text:

- Keep wording short and graphic.
- Prefer **very large display typography**.
- For an editorial thumbnail: use a high-contrast fashion/editorial serif or similarly elegant display face.
- For a game-interface feel: use a clean geometric, condensed, or slightly italic sans-serif.
- Allow type to overlap the subject or crop at edges when legibility remains strong.
- Use blue text on white most often; white text may sit on blue shapes.
- Do not mimic any Persona logo or exact proprietary type treatment.

## Subject treatment

Subjects can be realistic, illustrated, anime-adjacent, sketch-like, or graphic silhouettes depending on the brief.

Default treatment:

- mostly grayscale or muted subject
- selective blue edge light / painted accent
- one or two blue details only
- hand-drawn or ink-like contour accents are welcome
- preserve facial clarity if a portrait is central

This contrast is important: **the subject does not need to be blue; the light and graphic system around it are blue.**

## Image generation workflow

When the user asks to create an image in this style:

1. Extract the requested subject, format, and purpose.
2. If dimensions are not specified, infer them from use:
   - YouTube thumbnail: 16:9
   - Instagram feed: 4:5
   - Story/Reel cover: 9:16
   - Poster / general art: 4:5 unless context suggests otherwise
3. Build a prompt around the subject first, then apply this style system.
4. Explicitly invoke `$imagegen` when available.
5. If the user provided a reference image, attach/use it as a **style and palette reference**, not as something to reproduce literally.
6. Generate a strong first pass rather than asking unnecessary questions.
7. On revision, preserve composition elements the user liked and change only the requested attributes.

## Prompt construction template

Use this internally as a scaffold; adapt it naturally rather than pasting it verbatim every time.

> [SUBJECT + ACTION + SETTING]. High-key luminous blue-and-white visual system. Predominantly ice-white background with large negative space. Electric azure `#1F84ED` and hot azure `#1371EB` as the only strong colors, cyan `#54B3E9` glow, sparse deep blue `#114BC3`. Clean urban/editorial composition, soft underwater shimmer, watery gradients, glass reflections, refracted light, subtle blue rim light, pale gray sketch/ink details, one flowing blue ribbon or liquid trail guiding the eye. Elegant, crisp, expressive, minimal but not sterile. [TYPOGRAPHY INSTRUCTIONS IF NEEDED]. No magenta, no purple neon, no rainbow, no dark cyberpunk background, no clutter, no copied game logos, characters, or interface elements.

## Thumbnail recipe

For a YouTube-style thumbnail:

- 16:9
- white or pale gray field
- giant 1–4 word blue headline
- grayscale hero subject with blue edge light
- one bright azure paint/water stroke connecting foreground to subject
- slight perspective floor or horizon fade
- very sparse background detail
- high contrast at small size
- no more than 2 major visual clusters

## UI / poster recipe

For a more Persona-3-Reload-adjacent feel without copying it:

- treat water as a psychological / spatial metaphor
- use soft blue gradients and submerged depth
- add glass-like glints and reflection
- use clean architectural lines against flowing water forms
- let the subject appear suspended, drifting, or intersected by the interface
- combine precise geometry with one organic fluid gesture
- keep interaction labels readable and secondary to the composition

## Quality gate

Before finalizing, check all of these:

- Does it feel mostly white rather than mostly dark?
- Is the blue close to vivid clean azure, not purple or teal?
- Is there one clear focal point?
- Is the glow soft and aqueous rather than neon-sign-like?
- Is the composition spacious and editorial?
- Are gray/black details restrained?
- Is text readable at thumbnail scale?
- Does it avoid copying named characters, logos, or exact UI layouts from existing IP?

If any answer is no, revise before returning the image.

## Reference notes

For the reasoning behind the visual system, read `references/style-guide.md`.
