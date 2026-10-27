# vertical/azure-void

`vertical/default` with the **Azure Void** look (`azure-void-image-style/SKILL.md`): ice-white glass
cards with one cyan bloom, azure as the only signal colour, graphite detail, no red/green/gold.

- `numbers.json` carries `"extends": "vertical/default"` and only the keys that change: caption
  accent colours and `graphics.skin`. Everything else — cut, caption geometry, graphic geometry,
  audio, export, `fonts/`, `sfx/`, `transcript-corrections.json` — is inherited (`_lib.preset_file`).
- The graphics look is `presets/graphics/_skins/azure-void.css`, included by `_base.html` after the
  preset's own style block. Presets own the motion; the skin only recolours.
- Pick it at intake: `workflows/new-job.py <src> --slug <job> --preset vertical/azure-void`.
- Preview any preset in this skin: `python workflows/build-graphics.py --preset presets/graphics/list-card --vertical vertical/azure-void`.
