# vertical/broll-story

The **B-roll Story** edit: a talking head carried by the creator's own b-roll, cut on the nouns, with game-world
graphics only where the face is on screen. Measured from the 9030 reel ("Is it possible to get to 10K a month while
working a job and in uni?", 2026-10-24), the creator's own Premiere cut.

- `numbers.json` extends `vertical/pixel-arcade` (graphics style) → `vertical/default`, and adds a `broll_story`
  block: shot lengths, the hook-montage cadence, how much of the reel stays on the face, the frame-snap rule, the 4K
  phone-clip scale, clip reuse and the music clip gain. Skills and plans cite these numbers; none are hard-coded elsewhere.
- **The playbook is `docs/style/BROLL-STORY.md`**: the beat grammar, how to pick b-roll, where graphics may go,
  the Premiere mechanics, and the creator's rejections. Read it before planning.
- Pick it at intake: `workflows/new-job.py <src> --slug <job> --preset vertical/broll-story`.
