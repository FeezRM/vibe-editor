# TEXTURE — why it looks hand-made instead of generated

The single question this file answers: **why does one motion graphic read as premium
and another — same layout, same palette — read as AI slop?**

The answer is not taste. It is that premium work contains *deliberate, controlled
imperfection*, and generated work is maximally smooth, crisp, and flat by default.
Every technique below is a small, named, intentional un-clean-up step.

> **The rule: stack four or five restrained imperfections. Never one loud effect.**

A single heavy grain pass reads as an Instagram filter. Grain at 12% + a felt-not-seen
vignette + feathered mask edges + a contour ground + a 15fps stutter reads as a thing a
person made. None of the five is visible on its own. That is the point.

---

## 0. The tells — read this before building anything

Every row is a real failure mode. The left column is what generated work does by default.

| | Generated / cheap | Premium counter-move |
|---|---|---|
| Background | Purple→blue gradient blob, glassmorphism blur | Flat warm near-black, or a 5–8% radial lift. **Never a hue gradient as the ground.** |
| Glow | Everything glows, 20–40px blur, screen blend | One hero glow at most. 2–6px radius, 10–20% opacity, warm not blue-white |
| Type | Centred Montserrat/Poppins/Inter Bold, default tracking | Display face with deliberate optical tracking; engraved caps for micro-labels |
| Easing | `elastic`, `back`, overshoot on everything | `power3.out` in, `power1.inOut` between, `steps()` for mechanical counts |
| Simultaneity | Everything animates at once, same duration, same frame | 1–2 movers at a time, 60–120ms stagger, 300–800ms holds |
| Colour | 3+ saturated hues, neon | Near-black + bone + **exactly one** metallic accent |
| Depth | Fake-3D bevel, `box-shadow`, frosted glass | Flat 2D. Depth comes from line-weight hierarchy and print registration offset |
| Icons | Emoji, rounded-square icon packs, 3D renders | Single-weight linework matching the engraving weight of everything else |
| Motion physics | Weightless snap and teleport | Needle overshoot-then-settle, dial rotation with implied mass |
| Texture | Perfectly flat vector, zero grain, banding gradients | Grain, paper tooth, halftone in the darkest 20% |
| Layout | Centred everything, generic card-with-shadow | Off-centre or radial; hairline rules; tick-mark scale language |
| Borders | Thick rounded boxes with heavy shadow | 1px rules and ticks. Cartographic instrument language |

**If a graphic has a purple-blue gradient, a glow on every element, and bounce easing, it
does not need adjusting. It needs deleting.**

---

## 1. Grain

The base layer. Present on every composition in the analog skin.

| Parameter | Value |
|---|---|
| Opacity | `0.08–0.15` (token: `--grain-opacity`). Above ~0.35 it reads as a filter |
| Blend | `overlay` or `soft-light` — both preserve midtone contrast; `normal` muddies |
| Cell size | 3–5px for the analog register. 1–2px for digital/broadcast |
| Animation | **Static.** One fixed noise field for the whole comp |

That last row is the one people get wrong. Grain that re-randomises every frame reads as
video noise — cheap, busy, and it wrecks H.264 compression. A single fixed field reads as
*material*, like the image is printed on something.

```html
<svg width="0" height="0" aria-hidden="true">
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.65"
                  numOctaves="3" seed="7" stitchTiles="stitch" result="noise"/>
    <feColorMatrix in="noise" type="matrix"
      values="0 0 0 0 0
              0 0 0 0 0
              0 0 0 0 0
              0 0 0 0.12 0"/>
  </filter>
</svg>
```

```css
.grain {
  position: absolute; inset: 0;
  filter: url(#grain);
  mix-blend-mode: overlay;
  opacity: var(--grain-opacity);
  pointer-events: none;
}
```

**`seed` must be a fixed integer.** `feTurbulence` is algorithmic, not random, so a fixed
seed is deterministic *within* a Chrome version — but rasterisation can shift across
Chrome versions and GPUs. If a project must be bit-identical across machines, bake the
grain to a PNG once and reference it as a static asset instead.

---

## 2. Vignette

```css
.card-ground {
  background: radial-gradient(ellipse at 50% 42%,
              var(--ground-lift) 0%,
              var(--ground) 62%,
              #070806 100%);
}
```

5–12% luminance drop at the corners, feather covering >70% of the frame. Its job is to
pull the eye to centre. **A vignette should be felt, not seen** — if you can point at
where it starts, it is too strong.

Note the centre is at 42% height, not 50%. An optically-centred lift sits slightly high;
a mathematically centred one reads as sagging.

---

## 3. Feathered edges — the luxury tell

Hard vector edges are the fastest way to look like a template. Every glow, every reveal,
every masked shape gets a soft edge instead of a clean opacity cut.

```css
.feather   { mask-image: radial-gradient(ellipse at center, #000 55%, transparent 100%); }
.feather-b { mask-image: linear-gradient(to bottom, #000 60%, transparent 100%); }
```

Applies to: scrims, glows, the outer limit of a contour field, the edges of a background
grid, the bottom of a tall plate. It does **not** apply to type, rules, ticks, or
engraved linework — those stay crisp. Soft grounds, sharp instruments.

---

## 4. Contour ground (analog skin)

The topographic field behind the compass reference. This is what makes the black read as
terrain rather than as an empty div.

| Parameter | Value |
|---|---|
| Stroke | 0.5–1px |
| Colour | A few % lighter than the ground — `#1A1C18` on `#0B0C0A` |
| Opacity | 40–60% (token: `--contour-opacity`) |
| Spacing | Irregular/organic, but **fixed** |

Generate the paths **offline** and paste them in as static `<path>` data. Do not run a
noise function at render time — even a seeded one is a liability, and there is no reason
to pay for it every frame. Feather the field's outer edge (§3) so it fades before the
frame boundary rather than being cropped by it.

Guilloche bands — layered parametric sine/epicycloid curves — are the same idea in a
tighter register, good at 15–25% opacity as a border band on a plate. They are pure
deterministic maths, so they can be computed in the composition safely.

---

## 5. The stutter — the highest-value technique in this file

The most reliable "a human made this" signal found in the entire research pass.

Animate everything smoothly with proper easing. Then **step the whole timeline down to
~15fps** so it stutters slightly against a 30fps render. Motion that is too smooth is
the single loudest generated-content tell, because nothing physical moves that cleanly.

```js
// Quantise a paused timeline to --stutter-fps. Deterministic and seek-safe.
function stutter(tl, fps) {
  if (!fps) return tl;                 // 0 disables (digital skin default)
  const step = 1 / fps;
  return { get time() { return Math.floor(tl.time() / step) * step; } };
}
```

In practice, apply it per-tween with a stepped ease rather than to the master timeline —
it composes better and stays seek-safe:

```js
// 15fps stutter across a 0.6s tween = 9 discrete steps
tl.to(needle, { rotation: 47, duration: 0.6, ease: "steps(9)" }, 0.2);
```

**Where to use it:** needle sweeps, dial rotations, counter rolls, ring spins — anything
mechanical. **Where not to:** grain, vignette, feathered drift, and type entrances, which
should stay smooth. Stuttering everything reads as a dropped-frame bug, not as craft.

Set `--stutter-fps: 0` to disable it globally; the digital skin ships with it off.

---

## 6. Making gold read as metal

The `#1` fake-3D tell is a flat gold hue with a bevel or drop shadow. Real metal is a
*directional reflection*, which means a gradient ramp with an off-centre specular.

```css
.gold {
  background: linear-gradient(115deg,
    #8A6A2A 0%, #C9A24B 25%, #F0D98C 45%, #C9A24B 65%, #8A6A2A 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
```

Five stops, not two. Specular at 45%, not 50% — symmetry reads as plastic. Add a 1px
darker edge stroke (`--accent-lo`) to imply ambient occlusion instead of a shadow. For
SVG linework use the identical stops in a `<linearGradient>` as `stroke`.

---

## 7. Print registration offset

Use this **instead of** a drop shadow, never as well as one.

```css
.misprint {
  position: absolute; inset: 0;
  transform: translate(1.5px, 1px);
  opacity: 0.15;
  color: var(--sig-down);       /* oxblood tint */
  pointer-events: none;
}
```

A duplicate of the linework, nudged 1–2px, tinted, at ~15%. It reads as mis-registered
print plates. Two elements maximum per composition — it is a seasoning, not a style.

---

## 8. Chromatic aberration

**Transition frames only. Never a persistent state.** 1–3px RGB offset, animated in and
out on a GSAP timeline, tied to fast motion. A static chromatic-aberration layer is a
2019 tell and reads as broken rather than expensive.

---

## 9. Halftone

Reserve for the shadow/fill areas of illustration linework — never on type. Dot 2–4px,
45°, only in the darkest ~20% of the tonal range.

---

## 10. Determinism — the hard constraints

HyperFrames renders by seeking a paused timeline. Anything that changes between two
renders of the same frame is a bug.

| Rule | Why |
|---|---|
| No `Math.random()` anywhere | Non-deterministic across renders. Use a seeded mulberry32 or bake the value |
| No `Date.now()` | Same |
| Fixed `seed` on every `feTurbulence` | Unseeded turbulence can shift across Chrome builds |
| No `repeat: -1` | Compute finite: `Math.ceil(duration / cycle) - 1` |
| Bake contour/guilloche paths offline | Cheaper per frame and immune to version drift |
| Avoid live `feDisplacementMap` for eroded type | GPU/driver-sensitive in headless. Pre-rasterise the distressed glyphs instead |
| Prefer few full-bleed texture layers | Many small independently-blended elements are expensive to rasterise at 1080×1920 |

---

## 11. The texture stack, in order

Bottom to top, for an analog full-frame card:

```
1. ground        radial lift        #15140F -> #0B0C0A -> #070806
2. contour       static SVG paths   --contour-opacity, feathered at the edges
3. guilloche     optional band      15-25%, plate borders only
4. CONTENT       instruments, type, linework  <- crisp, never feathered
5. misprint      optional           <=2 elements, 15%
6. grain         feTurbulence       --grain-opacity, overlay
7. vignette      radial             --vignette-drop
```

Overlays (alpha `.mov`) skip layers 1–3 — the footage underneath is the ground. They
carry grain only if the graphic has its own plate to carry it on; grain over transparency
produces a dirty alpha channel that fringes badly in Premiere.

---

## 12. Self-check

- [ ] Grain present, ≤15%, static, `overlay` blend
- [ ] Vignette felt, not visible
- [ ] Every glow/scrim/mask edge feathered; type and linework crisp
- [ ] Contour ground on full-frame analog cards, feathered at the edge
- [ ] Mechanical motion stepped to `--stutter-fps`; type and drift left smooth
- [ ] Gold is a 5-stop ramp with off-centre specular, never a flat hue + bevel
- [ ] No `box-shadow` anywhere. Depth = line weight + registration offset
- [ ] ≤2 misprint elements
- [ ] Chromatic aberration only on transition frames, if at all
- [ ] No `Math.random()`, no `Date.now()`, no `repeat: -1`, every `seed` fixed
- [ ] Exactly one accent colour, ≤2 accent elements in frame
