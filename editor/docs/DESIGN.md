# Design: simple, clean, dark

> The look of Vibe Studio. `vibe-theme` turns these tokens into egui `Visuals`. No colour, radius or size is
> written anywhere else. The mockup is `editor/design/mockup.html` (screenshot: `editor/design/mockup.png`).

## 1. Principles

1. **The footage is the brightest thing on screen.** Chrome is near-black and neutral, so colour judgements
   happen in the monitor, not against a tinted UI.
2. **Flat.** No gradients, glows, glass, blur, neon, inner shadows or decorative shapes. Depth comes from
   three greys and a 1 px line. The only shadow is under floating menus and dialogs, where it separates
   layers.
3. **One accent.** One colour means "selected / active / now": the selection outline, the playhead, focus,
   the primary button. Everything else is grey. Status colours (red, amber, green) appear only in meters and
   messages.
4. **Quiet until touched.** Controls show their value, not their chrome. Borders and fills appear on hover and
   focus. Panels have no titles when their tab already says what they are.
5. **Familiar placement.** Monitors at the top, timeline at the bottom, assets on the left, inspector on the
   right: where Premiere, Resolve and CapCut all put them. Familiarity is part of being simple.
6. **Dense, but with air.** A 4 px grid, 28 px rows, 12–13 px type. Everything a reel edit needs fits on a
   1440×900 laptop without scrolling the inspector.

## 2. Tokens

| Token | Value | Use |
|---|---|---|
| `bg.app` | `#0B0B0C` | behind panels; gutters between panels (2 px) |
| `bg.panel` | `#131315` | panel bodies |
| `bg.raised` | `#18181B` | top bar, panel tab strips, timeline track headers, inspector section headers |
| `bg.field` | `#1D1D21` | inputs, sliders, dropdowns |
| `bg.hover` | `#232328` | hover on rows and buttons |
| `bg.active` | `#2A2A30` | pressed; selected rows (non-accent) |
| `line` | `#26262B` | separators, panel borders, ruler ticks |
| `line.strong` | `#34343A` | field borders on focus-less hover, clip borders |
| `text` | `#E7E7EA` | primary text, values |
| `text.dim` | `#A1A1A8` | labels |
| `text.faint` | `#6B6B73` | hints, disabled, ruler numbers |
| `accent` | the brand colour, `brand/brand.json` `palette.accent` (default `#FFC531`) | selection outline, playhead, focus ring, primary button, keyframes set |
| `on.accent` | `#0B0B0C` on a light accent, `#FFFFFF` on a dark one | text and icons on an accent fill |
| `accent.dim` | accent at 20 % | selected range on the ruler, In/Out shading |
| `danger` / `warn` / `ok` | `#E5484D` / `#E2A336` / `#3FB97A` | meters, errors, render bar only |

**Clip colours.** Muted and flat, each with a 1 px border 8 % darker. Hue tells you the kind of clip;
nothing shouts.

| Kind | Fill | Notes |
|---|---|---|
| Video (A-roll) | `#2F4A63` | thumbnails at head/tail when space allows |
| B-roll / media overlay | `#2D5357` | |
| Graphic (render or graphic clip) | `#4A4466` | label = plan id + what it is ("g3 · followers ring") |
| Caption | `#5C5233` | caption text drawn in the clip; accent words in `text` weight 600 |
| Audio voice | `#2E4F40` | waveform in `#7FB79A` at 60 % |
| Audio SFX / music | `#3B4A35` / `#34424F` | |
| Selected (any) | the clip's own fill + 1.5 px `accent` outline | never a different fill |
| Disabled / muted | 40 % opacity | |

The accent is the creator's brand colour (decided 2026-11-04). Only `accent` changes with the brand; the rest of
the palette never does. The mockup was drawn with a blue placeholder before that decision.

## 3. Structure: pages, not workspaces

One row of page tabs, centred in the 40 px top bar: **Edit · Captions · Color · Audio · Export.** This is
Resolve's idea with fewer pages. Each page is a fixed, considered layout; panels can be resized but not
scattered. Docking stays available under *Window ▸ Custom layout* for power users, but it isn't the default.

| Page | Left | Centre | Right | Bottom |
|---|---|---|---|---|
| **Edit** | asset rail | Program (Source as a tab) | Inspector | timeline + overview strip |
| **Captions** | transcript (takes view) | Program with the caption band and safe zones | caption style (track look, accent style, animation) | timeline focused on caption + V1 |
| **Color** | clips strip | Program + scopes | colour panel (Basic, Curves, Wheels, HSL, Vignette) | mini timeline |
| **Audio** | SFX/music browser | track mixer | clip audio (gain, EQ, dynamics, ducking) | timeline with waveforms large |
| **Export** | presets (Reels, TikTok, Shorts, master) | preview | settings + loudness target | job queue |

## 4. Typography

- UI: **Inter** (OFL) at 12 px for labels and 13 px for values and tabs. Weights 400 and 500, and 600 only for
  the active page tab and accent words in caption clips. No all-caps labels.
- Numbers: **JetBrains Mono** (OFL) with tabular figures for timecode, ruler, and numeric fields.
- The timecode in the monitor is 15 px mono. It's the one large number on screen.

## 5. Components

- **Buttons:** ghost by default (text or icon, no fill), `bg.hover` on hover. The single primary button per
  page (Export) is solid `accent` with `on.accent` text. Radius 4 px. Height 28 px.
- **Fields:** `bg.field`, no border at rest, 1 px `line.strong` on hover, 1 px `accent` on focus. Values are
  scrubbable (drag left/right), as in every NLE.
- **Tabs:** text only, `text.dim` at rest, `text` and a 2 px `accent` underline when active.
- **Inspector rows:** label (`text.dim`, 12 px), value (`text`, mono when numeric), and a ◇ keyframe toggle at
  the right edge. The ◇ is hollow when the property is unanimated, filled `accent` on a keyframe, and half-filled
  between keyframes. ◀ ▶ step to the previous or next keyframe. This is CapCut's affordance with Premiere's
  power.
- **Timeline:** 28 px track rows (video rows resizable to 56), headers 160 px with name, lock, eye/mute, and
  target. The playhead is a 1 px `accent` line with a small flat flag on the ruler. In/Out is shaded with
  `accent.dim`. Snapping shows a 1 px `text` guide, not a glow. The render bar is a 2 px line under the ruler.
- **Overview strip:** a 20 px tall miniature of the whole reel above the tracks, as on Resolve's Cut page. A
  viewport rectangle shows what the main timeline shows.
- **Monitor:** the 9:16 canvas is centred on `bg.app`. The safe-zone overlay (IG / TikTok / Shorts chrome) is a
  1 px dashed `text.faint` outline that toggles with `'`. Transport sits beneath: ⏮ ◀ ▶ ▶▶ ⏭, timecode left,
  duration right, and a fit/zoom dropdown.
- **Icons:** [Lucide](https://lucide.dev) (ISC licence), 16 px, 1.5 px stroke, `text.dim` and `text` on
  hover. One icon set, no emoji, and no icon copied or traced from any vendor's app.
- **Menus and dialogs:** `bg.raised`, 1 px `line`, radius 6 px, shadow `0 8px 24px #00000066`. This is the
  only shadow in the app.

## 6. Motion

Panel transitions are instant. Hover and focus changes take 80 ms; menus fade in over 120 ms. No bounces,
springs or attention animations. Playback and scrubbing never wait on UI animation.

## 7. Density and sizes

4 px grid. Panel padding 12 px. Row height 28 px. Section gap 16 px. Gutter between panels 2 px of `bg.app`.
Minimum supported window: 1280×800.

## 8. Do not

- Gradients of any kind, including "subtle" ones on buttons, headers or the monitor background.
- Coloured panel backgrounds, tinted greys, and a second accent colour.
- Pills everywhere, oversized radius (> 6 px), or cards inside cards.
- Glow, neon, glass, blur, noise texture, or decorative illustration.
- Emoji or playful copy in the UI. Labels say what the thing is: "Scale", not "Make it bigger ✨".
- Brand-coloured selection. Selection is always `accent`.

## 9. Checklist for any screen

1. Is the footage the brightest thing on screen?
2. Is the accent used only for selected, active and now?
3. Count the greys: more than `bg.app`, `bg.panel`, `bg.raised`, `bg.field`, `bg.hover` and `bg.active`
   means a token is missing.
4. Any gradient, glow or shadow outside menus? Remove it.
5. Does every visible control belong to this page's task?
6. Does it fit 1440×900 without scrolling the inspector?
