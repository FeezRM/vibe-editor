# Style Guide — Azure Void

## Why this visual language works

The target look combines two references:

1. The supplied thumbnail: a bright white field, enormous saturated blue display type, a mostly grayscale central figure, and a glowing blue painted/water trail.
2. Persona 3 Reload's documented UI direction: water, blue, shimmer, gradation, glass-like reflection, and a clean urban sensibility.

The goal is **not to reproduce Persona 3 Reload**. It is to turn those broad art-direction principles into a reusable, original design system.

## Research summary

Persona 3 Reload art director Tomohiro Kumagai described the UI as building on the original game's beautiful blue and movement reminiscent of water and bubbles. For Reload, the team expanded this into underwater shimmer, gradation, sparkle, reflection, and glass-like qualities. He also described the menu as evoking the protagonist sinking into an internal "sea" or psychological space.

In a later art-direction interview, Kumagai said the team combined a "blue that evokes death" and "seaside blue" with a sophisticated urban representation, mixing **clean urban lines** with the **soft expression of water**.

Those ideas translate well into a general visual system:

- precise geometry + organic fluid motion
- clean white space + vivid blue
- emotional depth without dark visual heaviness
- movement through ribbons, ripples, gradients, reflection, and suspension

## Palette derivation

The attached thumbnail was sampled for pixels in the saturated-blue range. The median qualifying blue was approximately RGB `(31, 132, 237)`, or `#1F84ED`.

Useful companion tones:

| Role | Hex | Purpose |
|---|---|---|
| Primary Azure | `#1F84ED` | Main blue typography and forms |
| Hot Azure | `#1371EB` | Strong accents and saturated edges |
| Glow Cyan | `#54B3E9` | Bloom and refracted highlights |
| Deep Blue | `#114BC3` | Depth, sparingly |
| Ice White | `#F7FAFF` | Main high-key field |
| Paper White | `#FFFFFF` | Peak highlights |
| Mist Gray | `#DCE3E8` | Background texture |
| Graphite | `#303740` | Linework and muted subject detail |

## Prompt vocabulary

Good words:

- luminous azure
- high-key
- submerged
- aqueous
- refracted
- shimmering
- glass-like
- sea-of-light
- clean urban lines
- pale negative space
- ink contour
- soft bloom
- fluid ribbon
- reflected blue light
- editorial
- suspended
- drifting

Words to avoid unless specifically requested:

- cyberpunk
- vaporwave
- synthwave
- purple neon
- holographic rainbow
- dark sci-fi
- maximalist

## Research sources

- Persona Central, "Persona 3 Reload Developer Interview on UI Development, Concept Screenshots" — summary of Famitsu interview with art director Tomohiro Kumagai, director Takuya Yamaguchi, and producer Ryota Niitsuma.
- Persona Central, "Persona 3 Reload Art Design and Direction Interview" — summary of Persona Magazine interview discussing "blue that evokes death," seaside blue, clean urban lines, and water.
- Official Persona 3 Reload website — describes the remake's signature stylish UI.
- OpenAI documentation — Codex can explicitly invoke the `$imagegen` skill for image generation; Codex skills use a `SKILL.md` file with YAML `name` and `description` metadata.
