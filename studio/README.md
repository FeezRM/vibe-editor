# Vibe Studio

The video editor of [vibe-editor](../README.md): a Premiere-style non-linear editor in pure Rust where
you edit by hand what your agent cut, and ask the agent for the rest.

- **Opens a vibe-editor job as a real timeline.** Takes, camera framing and zoom punches as keyframes,
  captions in your look as editable text, graphics, b-roll, holds, SFX and music levels.
- **Your Claude Code, inside the editor.** The Assistant panel runs your own Claude Code session in the
  vibe-editor folder (skills, samples, `CLAUDE.md`, your login; no API key). Its permission prompts are
  buttons, and every change it makes to the timeline is an undo step listed in Activity. A Claude Code
  session started anywhere else in the folder (the Claude app, a terminal) reaches the open editor too.
- **Edits by hand survive the agent.** Magnetic timeline (captions, graphics and SFX follow a trimmed or
  deleted take), and `vibe.diffJob` hands your changes back to the pipeline before it re-runs a step.
- **Exports** 9:16 H.264 with captions burned in, or any of the formats below.

```sh
../lanes/vibe/setup.sh                       # build, and register the editor for Claude Code sessions
../lanes/vibe/open.sh ../projects/<job>      # open a job (hand edits live in <job>/vibe/<job>.vibeproj)
../lanes/vibe/export.sh ../projects/<job> out.mp4
```

What changes when, how the pipeline maps onto the timeline and how agents drive it:
[VIBE-STUDIO.md](VIBE-STUDIO.md). Engine reference (time base, commands, codecs, interchange,
control protocol): [`docs/`](docs/).

## Credits

Vibe Studio is built on **[FilmCraft](https://github.com/storytold/filmcraft)** by the ArtCraft team,
an open-source, clean-room, pure-Rust professional editor: its engine, codecs, renderer, timeline and
editing tools are FilmCraft's work, used under the MIT OR Apache-2.0 licence
([LICENSE-MIT](LICENSE-MIT), [LICENSE-APACHE](LICENSE-APACHE), [NOTICE](NOTICE)). Third-party assets
and code are listed in [ATTRIBUTION.md](ATTRIBUTION.md). Vibe Studio's changes are under the same
terms.
