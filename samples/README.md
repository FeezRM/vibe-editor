# samples/ — what good editing looks like

Drop in reels whose editing you want the output to match: clean cuts, the captions, the graphics, the zooms, the
pacing. Yours, or ones you have a right to keep a local copy of. The videos are gitignored; only this README and
`STYLE.md` are tracked.

```
samples/
  01-<what-it-does-well>.mp4
  02-<what-it-does-well>.mp4
  STYLE.md          ← written by the agent (the ig-study skill), not by hand
```

Name each file for what it does well ("clean-jump-cuts", "screenshot-popups"), not for the account it came from.

## How they are used

After adding or removing samples, ask the agent to study them (`ig-study`). It watches each one frame by frame,
measures what it sees, and writes `STYLE.md`: the cut, the camera, the captions, the graphics, the sound, what makes
each reel engaging, and what none of them ever do. Every editing decision (`ig-reel`, `ig-cut`, `ig-show`,
`ig-pacing`) is made against that file, and every finished edit is compared frame by frame with the samples.

**Copy the craft, never the identity**: no handle, name or avatar from a sample ever appears in an edit.
