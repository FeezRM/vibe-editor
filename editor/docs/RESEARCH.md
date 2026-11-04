# Research: Premiere, Resolve, CapCut, and FilmCraft

> Written 2026-11-04 on branch `rust-editor`. This is the evidence behind `PLAN.md`.
> Sources are listed at the end. Vendor sites (helpx.adobe.com, capcut.com, blackmagicdesign.com) were
> unreachable from the research sandbox. Product facts below come from search-result summaries, the press, and
> working knowledge of the apps. Where a fact matters for the build, it is marked **verify** and is checked in
> the app before we copy it.

---

## 0. The question

The vibe pipeline already makes the editing *decisions*: takes, captions, graphics, zooms, sound. Today the
editable result exists only in Premiere, through a fragile CEP bridge. `lanes/premiere/lab-notes.md` and
`docs/lab-notes-archive.md` record the problems: `export_frame` lies, `encodeSequence` throws, the timeline eats
audio, and re-renders hit a file Premiere still has open. We want an editor that:

1. feels like the editors people already know, so the agent's skills and the user's habits carry over, and
2. opens anything the pipeline produced as a real, fully editable timeline: clips, keyframes, caption text,
   graphics layers and audio, all trimmable by hand,
3. is driven by the agent natively, with no bridge, no screenshots, and no success flags that lie.

To build it, we first need to know what the three reference apps share, where they differ, and what already exists
in open source that we can build on.

---

## 1. Adobe Premiere (desktop), v26.x

**State in 2026.** Version 26.0 (January 2026) renamed the product "Premiere" (desktop). Releases 26.2 (April)
and 26.3 (June) followed. Headline features: AI Object Mask, which left beta in 26.0; redesigned shape masks;
native Windows ARM64; about 90 GPU-accelerated effects and transitions; Firefly media sent straight into
Premiere; and Media Intelligence search for sound effects, alternate takes and censored words. Earlier
releases added Generative Extend (25.2, made with Firefly frames), text-based editing (2023), caption
translation, and a Properties panel.

**What carries over: the mental model every pro NLE copies.**

| Concept | Premiere's form |
|---|---|
| Project → bins → items | Project panel, bins, subclips |
| Source / Program monitors | Mark In/Out in Source; three-point edits into Program |
| Sequence | V1…Vn over A1…An, plus a caption track; patch and target buttons; sync lock; track lock |
| Tools | Selection `V`, Track Select `A`, Ripple `B`, Rolling `N`, Rate Stretch `R`, Razor `C`, Slip `Y`, Slide `U`, Pen `P`, Hand `H`, Zoom `Z`, Type `T` |
| Edit keys | `,` insert · `.` overwrite · `;` lift · `'` extract · `⌘K` add edit · `Q`/`W` ripple trim to playhead · `⇧⌫` ripple delete · `J K L` shuttle · `I O` marks · `M` marker · `S` snap |
| Clip properties | Effect Controls: intrinsic Motion (position, scale, rotation, anchor), Opacity (blend mode), Time Remapping, Volume, plus added effects. Each parameter has a stopwatch and keyframes with a value graph and a velocity graph |
| Properties panel | The newer context panel: shows whatever is selected (clip, text, shape, caption) with the common controls |
| Color | Lumetri: Basic, Creative, Curves, Color Wheels, HSL Secondary, Vignette; scopes |
| Audio | Essential Sound (Dialogue, Music, SFX, Ambience) with Enhance Speech, auto-ducking, loudness; Track Mixer and Clip Mixer |
| Text | Text panel: Transcript tab (text-based editing) and Captions tab; Essential Graphics / MOGRT templates |
| Export | Export mode with destinations; Media Encoder queue |

**Lessons for us.**
- These keys and panel names are the industry lingua franca. Resolve and FilmCraft both ship a "Premiere
  keyboard" preset. If our editor speaks Premiere, the user's hands already know it.
- The Properties panel is where Premiere is heading: one context panel instead of a dozen. CapCut's inspector
  already works this way, and it suits short-form work better than Effect Controls.
- Text-based editing (delete a word, the cut ripples) is what our pipeline already does in files
  (`review/takes.md`). Its natural home is a Transcript panel.

---

## 2. DaVinci Resolve 20 → 21.1

**State in 2026.** Resolve 20 (April/May 2025) added more than 100 features. They include a keyframe editor with
a curve view and timeline drawer on the Cut and Edit pages (no trip to Fusion), Source Tape on the Edit page,
live overwrite with edit keys and the search dial, safe trimming, vertical-timeline editing on the Cut page, AI
Animated Subtitles (words animate as they're spoken), subtitle presets dragged onto the subtitle track header,
and AI IntelliScript (builds a timeline from a script). Resolve 21 (June 2026) adds a Photo page, RAW stills
(CR3, RW2, RAF, ProRAW), AI CineFocus, AI Blemish Removal, AI Slate ID, Lottie animations and OGraf HTML
graphics. **Resolve 21.1 (September 2026) ships a native MCP server**, reportedly 88 tools covering timeline,
media pool, colour, Fairlight and render. It is **Studio only** ($295), as is the external Python scripting API.

**What Resolve adds to the shared model.**

| Concept | Resolve's form |
|---|---|
| Pages | Media · Cut · Edit · Fusion · Color · Fairlight · Deliver: one task per page, chosen by tabs along the bottom |
| Edit page | Same model as Premiere. Different keys: `A` select, `B` blade, `T` trim, `W` dynamic trim, `F9` insert, `F10` overwrite, `F11` replace, `F12` place on top, `⌘B` razor at playhead |
| Cut page | A fast lane for short-form work: Source Tape (the whole bin as one scrollable tape), dual timeline (the whole edit above, a zoomed view below), smart insert, a vertical-timeline mode |
| Color | Node graph (serial, parallel, layer nodes), primaries wheels, curves, qualifiers, Power Windows with tracking, Magic Mask |
| Subtitles | A subtitle track with presets per track; animated word-by-word subtitles |
| Deliver | Render queue with presets (YouTube, TikTok, …) |

**Lessons for us.**
- **Pages beat workspaces for clarity.** One row of tabs (Edit, Captions, Color, Audio, Export) is the
  simplest way to keep a pro feature set from cluttering the screen. This is how the editor stays "simple and
  clean."
- **The Cut page's dual timeline fits 15–60 s reels:** the whole reel always visible, plus a zoomed working
  strip.
- **Subtitle presets that apply to the whole track** are exactly what our caption looks are
  (`presets/vertical/<look>`).
- **Resolve 21.1's MCP server is real competition.** If Studio is affordable, it could become a lane
  alongside ours. It does not replace our editor: it's closed, Studio-only, and the agent drives a black
  box.

---

## 3. CapCut desktop (2026)

**State in 2026.** CapCut is the default editor for short-form creators. Desktop features we found: auto
captions styled on the timeline; a keyframe graph editor with ease curves; speed curves (presets plus custom);
AI Auto Reframe that follows the subject into 9:16 or 1:1; text templates and animations; effects, filters,
stickers; filler-word removal; voice enhancement and noise reduction; beat detection. The timeline controls are
**Main track magnet**, **Auto snapping**, **Linkage**, and **Preview axis**. Several AI features moved behind
Pro in 2025–26, and reported pricing is inconsistent ($7.99 vs $19.99 a month; **verify**).

**What CapCut does differently from Premiere and Resolve, and why creators love it.**

| Concept | CapCut's form |
|---|---|
| Main track | One magnetic main track for A-roll; deleting a clip closes the gap (an FCP-style spine). Everything else hangs above it as overlays that stay attached to the main-track clip under them (Linkage) |
| Inspector | One panel on the right with tabs per selection: Video (Basic / Remove BG / Mask / Retouch), Audio, Speed, Animation (In / Out / Combo), Adjust. No separate Effect Controls, Lumetri or Essential Graphics |
| Keyframes | A ◇ next to every property in the inspector. Click it at the playhead and a keyframe is set. A graph button per segment opens ease presets |
| Captions | Auto captions become a text track. The style applies to all captions at once. Templates animate word by word with keyword highlight |
| Text | Text presets, effects (stroke, glow, shadow) and animations (In / Out / Loop), applied per clip |
| Speed | Normal (a number) or Curve (named presets: Montage, Hero, Bullet, Jump Cut, Flash In/Out, plus Custom) |
| Asset browsers | Top-left tabs: Media, Audio, Text, Stickers, Effects, Transitions, Captions, Filters, Adjustment, Templates |
| Keys | `⌘B` split, `Q` / `W` delete left / right of the playhead (like Premiere's ripple trims), `Space`, `J K L` (**verify** the full map) |

**Lessons for us.**
- **The vibe pipeline's output is a CapCut-shaped edit.** One A-roll spine, word-timed captions with accent
  words, overlays pinned to beats, zoom punches, SFX on hits. CapCut's model (main track, linkage, one
  inspector, styled caption track) is the most natural way to *edit that output by hand*.
- **Premiere's model is the most natural way to do precise trim work** and is what the existing skills
  speak. **The editor should be a Premiere-grade engine with a CapCut-simple surface:** the same timeline,
  keys and commands, a CapCut-style inspector and asset browser, and Resolve-style pages.

---

## 4. Concepts all three share (the editor's vocabulary)

These are the nouns and verbs the editor must have so that skills and habits carry over from any of the three
apps:

- **Project → bins → media items**, with proxies and relink.
- **Sequence/timeline** with video tracks above audio tracks, a caption/subtitle track, markers, In/Out,
  snapping, linked A/V, track lock, mute, solo and visibility.
- **Edit operations:** insert, overwrite, replace, lift, extract, razor/split, ripple delete, close gap,
  ripple trim, roll, slip, slide, rate stretch, add edit, nest/compound.
- **Clip properties:** transform (position, scale, rotation, anchor, crop), opacity and blend, speed
  (constant, ramp, reverse, freeze), volume and pan, plus effect stacks. **Every property can be keyframed**,
  with ease/Bezier interpolation and a graph.
- **Text and captions:** styled text layers, word-timed caption tracks, templates, import/export of SRT and VTT.
- **Colour:** primaries, curves, wheels, HSL qualifier, LUTs, scopes.
- **Audio:** clip gain, track mixer, EQ, compressor, limiter, de-noise, loudness meter (LUFS), ducking.
- **Export:** presets by platform; H.264/HEVC/ProRes; loudness targets.
- **Interchange:** FCP7 XML, FCPXML, OTIO, EDL, AAF. This is how a timeline moves between editors.

---

## 5. Open-source landscape

### 5.1 FilmCraft (storytold/filmcraft): the base we evaluated in depth

Cloned at `c9be142` (2026-11-03). **MIT or Apache-2.0.** Pure Rust, edition 2024, MSRV 1.95.

| Fact | Detail |
|---|---|
| Size | 45 crates plus 3 apps; about 457 k lines of `.rs` (343 k by their count, excluding tests); 2,520 tests; 69 authors |
| Self-assessment | Feature breadth about 86 % of Premiere (menus 92 %, effects 100 %); **ready for real work about 56 %**; alpha. Their own estimate of the remaining work: **1,550–2,750 agent-hours** to full parity |
| Time base | `Tick(i64)` at 254,016,000,000 per second, which divides exactly into every frame rate and sample rate; rational `FrameRate`; no `f64` seconds in edit math |
| Model | `Arc<Project>` with copy-on-write snapshots. Undo is a stack of snapshots. Effects are data (`effect_defs()` generates the UI and the agent docs) |
| Commands | More than 650 engine commands (`Session::execute(id, params)`), each with an id, a label, a menu path, a shortcut, parameter docs and an `enabled()` check that returns a reason. UI, CLI, JSON control channel and **MCP** all dispatch the same commands |
| Editing | Three-point editing, every trim (ripple, roll, slip, slide, rate stretch, razor, trim mode, dynamic JKL trim, trim monitor), multicam, nesting, markers, sync locks, linked selection |
| Keyframes | Linear, Bezier, auto, continuous, hold, ease in and out; value and velocity graphs |
| Colour | Lumetri-equivalent panel with scopes, graded in linear light at 32-bit float |
| Effects | 90+ video effects, about 30 transitions, 26 blend modes, masks with tracking-ready Bezier paths |
| Audio | BS.1770/R128 meters (match ffmpeg `ebur128` to 0.1 LU), EQ, dynamics, limiter, de-noise, track/clip mixers, automation modes, audio clock as master |
| Text | Its own OpenType engine (harfrust shaping, bidi), graphic clips with text and shape layers, graphic templates |
| Captions | Caption tracks (Subtitle / 608 / 708 / Teletext); SRT, VTT and SCC in and out |
| Transcripts | `transcript.*` commands: text-based editing, filler and pause removal, captions from the transcript. Whisper runs on candle behind a feature flag |
| Codecs | Its own H.264 (decode and encode), HEVC, VP8/9, AV1, ProRes (decode and encode), DNx, AAC, Opus; MP4/MOV/MKV/MXF/TS. **No FFmpeg inside.** Hardware decode through VideoToolbox, MF and VA-API; hardware HEVC encode only |
| Export | Background jobs. Includes vertical 1080×1920 TikTok/Reels/Shorts presets normalised to −14 LUFS |
| Interchange | FCP7 XML, FCPXML 1.9–1.11, OTIO, CMX3600, AAF, OMF |
| UI | egui + wgpu, dockable panels, Premiere-measured dark tokens with a purple brand accent; about 100 k lines in `ui-egui`. **Not pluggable:** panels and theme are compiled in |
| Layering | `cargo xtask layers` enforces L0 codecs → L4 engine → L5 UI → L6 apps. Everything up to the engine is headless and builds for wasm |
| Rules | No `unwrap`/`panic` outside tests; no `unsafe` outside `platform`; **no Adobe assets of any kind** |
| Gaps (theirs) | Speed on big footage (grading and export are on the CPU); no `.prproj`; no plugins (VST/OFX); delivery codecs (software H.264 only); little real-world camera/phone media testing; few AI features |

**Verdict.** FilmCraft has already done the 80 % of an NLE that is hardest and least specific to us: codecs,
exact time, edit algebra, render, keyframes, mixing and interchange. The engine is headless and already
agent-first. What it lacks is exactly what we have: a short-form editing brain, a creator's look, and a
pipeline. It also has a busy UI with a purple brand that we must reskin. **Recommendation: build on its engine;
own the surface and the short-form layer (see `PLAN.md` §2).**

### 5.2 Others considered

| Project | Stack | Why not the base |
|---|---|---|
| Gausian native editor | Rust, egui + wgpu | Evidence that egui can host an NLE timeline; much smaller scope than FilmCraft |
| OpenCut | TypeScript/web | CapCut-like and web-first; not Rust; shallow engine |
| Kdenlive / Shotcut (MLT) | C++ / Qt | Mature, but not Rust, GPL, and their models don't match the agent-command design |
| Olive | C++ / Qt | Stalled |
| GStreamer Editing Services | C | Viable engine through `gstreamer-rs`, but timing isn't exact-integer and the edit algebra is thin |
| ffmpeg (`ffmpeg-next`) | C via FFI | Ideal for decode and encode breadth, and our pipeline already depends on it. Kept as a fallback import/export path (§6), not as the engine |

---

## 6. Rust tech stack findings

| Area | Finding | Choice |
|---|---|---|
| UI toolkit | egui (immediate mode) has a working NLE precedent: FilmCraft and Gausian. iced and Slint are retained mode and lighter on CPU, but have no NLE precedent. GPUI has no timeline evidence | **egui + wgpu**, inherited with FilmCraft's UI. Redraw only on change; watch CPU (risk R4) |
| GPU | wgpu (Metal/Vulkan/DX12/WebGPU); FilmCraft's compositor blends in linear light and is tested against the CPU path | inherit |
| Decode/encode | FilmCraft's own codecs plus hardware paths. Phone HEVC 10-bit needs hardware (their gap G3). The ffmpeg CLI is already a pipeline dependency | inherit; ffmpeg CLI as the transcode fallback at import (`proxy` / `optimized media`) |
| Audio out | cpal; the audio clock is master | inherit |
| Time | integer ticks (exact) vs our pipeline's float seconds | convert **once** at the bridge, snapping to frames (archive#frame-drift) |
| Agent | MCP over stdio (rmcp) and JSON lines over TCP; same command registry | inherit, plus `vibe.*` macro commands |
| Interchange | OTIO / FCPXML / FCP7 XML / AAF | inherit: the escape hatch to Premiere and Resolve |

---

## 7. What this means for vibe-editor

1. **A new Premiere clone is not needed: one exists.** The value we add is the bridge from *agent decisions*
   to an *editable timeline*, the *short-form surface*, and the *look*.
2. **Every pipeline artefact has a native home** in FilmCraft's model (see the mapping in `PLAN.md` §4):
   keeps become V1/A1 clips, framing becomes Motion, zoom punches become Scale and Position keyframes,
   captions become text clips on a caption track with accent styling, graphics renders become V3/V4 alpha
   clips, SFX go on A3, and voice gain becomes clip volume.
3. **The agent stops guessing.** No CEP bridge, no `PrintWindow`, no `export_frame` that lies. Every edit is
   a command with a typed result, every frame can be rendered headless, and the read-back is the project
   file itself.
4. **The user can take over at any point,** and the edit can go back to the agent (round trip: timeline →
   `cuts.json` / `captions.json`), or out to Premiere or Resolve via XML/OTIO.

---

## Sources

- FilmCraft repository, wiki and docs: [github.com/storytold/filmcraft](https://github.com/storytold/filmcraft/wiki) (read locally: `README.md`, `docs/architecture.md`, `docs/control-protocol.md`, `docs/gaps.md`, `docs/target-app-parity.md`, `docs/transcripts.md`, `docs/keyboard.md`, `AGENTS.md`)
- [FilmCraft guide: free Premiere Pro alternative in Rust (pasqualepillitteri.it)](https://pasqualepillitteri.it/en/news/22531/filmcraft-free-premiere-pro-alternative-guide-rust) · [selfhostedworld](https://selfhostedworld.com/software/filmcraft) · [alternativeto](https://alternativeto.net/software/filmcraft/)
- [What's new in Adobe Premiere 26.0, Newsshooter](https://www.newsshooter.com/2026/01/20/whats-new-in-adobe-premiere-pro-26-0/) · [Fstoppers: Premiere 26.0 drops "Pro"](https://fstoppers.com/post-production/premiere-260-drops-pro-and-adds-powerful-ai-masking-900238) · [Larry Jordan: Premiere 26.0](https://larryjordan.com/?p=171186) · [TV Technology](https://www.tvtechnology.com/production/postproduction/latest-adobe-premiere-release-taps-ai-to-enhance-masking-features) · [Adobe release notes](https://helpx.adobe.com/premiere-pro/kb/fixed-issues.html) · [Adobe: text-based editing](https://helpx.adobe.com/premiere-pro/using/text-based-editing.html) · [Adobe blog, NAB 2023](https://blog.adobe.com/en/publish/2023/04/13/nab-2023-introducing-text-based-editing-premiere-pro-properties-panel-after-effects-more) · [AI in Premiere Pro, Sept 2025](https://aiandadobe.myportfolio.com/ai-in-premiere-pro)
- [PetaPixel: Resolve 21 released](https://petapixel.com/2026/06/03/davinci-resolve-21-officially-released-with-new-photo-editing-ai-tools-and-much-more/) · [No Film School: Resolve 21](https://nofilmschool.com/davinci-resolve-21) · [Videomaker: Resolve 21](https://www.videomaker.com/news/davinci-resolve-21-adds-photos-page-ai-focus-tools-and-free-upgrades/) · [RedShark: Resolve 21.1](https://www.redsharknews.com/davinci-resolve-21.1-new-features-release) · [MotionMedia: Resolve 21.1 MCP](https://www.motionmedia.com/mm-blog/davinci-resolve-21-1-update-new-features) · [byteiota: Resolve MCP](https://byteiota.com/?p=22448) · [resolve-mcp (third party)](https://github.com/DigitalWorkflowCompany/resolve-mcp) · [ProVideo Coalition: Resolve 20](https://www.provideocoalition.com/davinci-resolve-20-released/) · [Newsshooter: Resolve 20 beta 2](https://www.newsshooter.com/2025/04/22/blackmagic-design-davinci-resolve-20-beta-2-released/) · [Engadget: IntelliScript](https://www.engadget.com/apps/davinci-resolve-20s-latest-ai-feature-can-create-an-entire-timeline-based-on-a-script-120009351.html) · [Blackmagic: Resolve](https://www.blackmagicdesign.com/products/davinciresolve)
- [CapCut PC (official)](https://www.capcut.com/resource/pc-professional-video-editor) · [CapCut tool cheat sheet (PDF)](https://litcommerce.com/wp-content/uploads/2026/03/CapCut-ToolCheat-Sheet.pdf) · [CapCut PC timeline tutorial](https://recapio.com/digest/capcut-pc-tutorial-how-to-use-timeline-by-filip-delac) · [Filmora: CapCut for PC](https://filmora.wondershare.com/video-editor-review/capcut-for-pc.html) · [VideoProc: CapCut graphs](https://www.videoproc.com/video-editor/how-to-use-graphs-on-capcut.htm) · [freeacademy: CapCut AI features 2026](https://freeacademy.ai/blog/capcut-ai-features-complete-guide-review-2026) · [marcandrews: CapCut AI review 2026](https://marcandrews.com/?p=3178)
- [Gausian native editor (egui + wgpu)](https://gh.hhj520.top/gausian-AI/Gausian_native_editor) · [Tritium: Rust GUI observations](https://tritium.legal/blog/desktop) · [Tauri / iced / egui performance comparison](https://lukaskalbertodt.github.io/2023/02/03/tauri-iced-egui-performance-comparison.html)
