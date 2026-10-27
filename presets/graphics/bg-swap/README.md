# bg-swap

"Your background is kind of mid… not anymore" — the room behind the speaker is replaced, on the words. The speaker
stays the real footage; a hole-cut plate covers only the room. Make the plate first:

```bash
npx hyperframes remove-background projects/<job>/preview/spine.mp4 -o projects/<job>/assets/subject.webm
# schedule in assets/bg-plan.json: {"segments": [{"at": 0.0, "bg": "space"}, {"at": 1.45, "bg": "none"}, {"at": 2.77, "bg": "mid"}, …]}
python workflows/bg-plate.py projects/<job>          # --textures-only writes review/bg-*.png to look first
```

`bg`: a generated texture (azure · sunset · neon · space · chroma), `mid` (the real room drained of colour), `none`
(the real room) or an image path. The preset plays the plate full-frame and sweeps a light leak across each switch
(`reveal_at` = segment times − cue). It is a background, not content: `x-no-content` keeps the caption-band and face
checks off it. The plate is in spine time, so no zoom punch inside its window. Placement: `wash` (a full-frame layer under the others; it may overlap them, like `wash`).
