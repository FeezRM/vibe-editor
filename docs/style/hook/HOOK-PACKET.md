# Hook Packet contract

`projects/<slug>/HOOK-PACKET.json` is the hard interface between creative reasoning,
HyperFrames rendering, and Premiere execution. Human prose may explain it, but only the
packet controls the build.

## Required top-level fields

| Field | Purpose |
|---|---|
| `version` | Contract version; currently `1` |
| `project` | Stable slug used in filenames and sequence names |
| `runMode` | `design`, `trial`, or `fast` |
| `goal` | `views`, `leads`, `sales`, or another explicit outcome |
| `audience` | The person the hook should qualify |
| `promise` | One sentence describing the unchanged idea behind all candidates |
| `durationSeconds` | Opening length; normally `8` |
| `evidence` | Provenance ledger for every asset and metric |
| `candidates` | Complete A/B/C opening sequences |
| `selectedCandidate` | Candidate promoted after the gate |
| `captionMuteWindows` | Windows where designed text replaces captions |
| `premiere` | Sandbox sequence and track instructions |
| `qa` | Snapshot times and pass/fail state |

## Evidence ledger

Every evidence item needs:

- stable `id`;
- `kind`: screenshot, clip, document, interface, prop, or source-footage;
- local `path` or precise source reference;
- the claim it supports;
- source/provenance;
- `verified: true` before it may appear in a selected candidate.

Generated imagery may depict a metaphor, environment, or prop. It may not manufacture a
metric, screenshot, DM, testimonial, or analytics result.

## Candidate shape

Each candidate needs:

- `id` and dominant `mode`;
- `frameZero.visual`, `frameZero.owner`, and `frameZero.evidenceIds`;
- at least three contiguous beats spanning the opening;
- exact `speech`, `visual`, `change`, and `owner` for each beat;
- a 0–2 score in all six dimensions;
- risks or missing dependencies;
- optional `comparison.samenessIsClaim` and provenance when verified sameness is the point.

Allowed owners: `premiere`, `hyperframes`, `both`.

## Score

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| `specificity` | topic label | specific claim | person/behavior/consequence |
| `proof` | none | related visual | literal verified receipt or demonstration |
| `tension` | none | generic curiosity | contradiction, objection, or risk |
| `secondBeat` | more explanation | cosmetic change | meaningful proof/mechanism advance by second five |
| `muteTest` | unintelligible | gist visible | claim and contradiction visible without audio |
| `feasibility` | missing/private dependency | one manageable dependency | buildable from verified local material |

Selected candidate threshold: **9/12**, with `proof`, `secondBeat`, and `muteTest` all at
least 1. The score is a gate, not a prediction of virality.

## Beat ownership

Use `premiere` for real footage operations, `hyperframes` for deterministic designed
objects, and `both` only when the proof truly combines them. The owner field prevents both
engines from recreating the same job and gives the agent a mechanical execution queue.

## Lifecycle

1. Write evidence and candidates.
2. Validate with `workflows/validate-hook-packet.py`.
3. Create candidate storyboard strips.
4. Select; set `selectedCandidate`.
5. Build in `HOOK-LAB__<slug>__<candidate>`.
6. Set `qa.status` to `pass` only after pixel review.
7. Promote the selected opening.
8. After publishing, append actual results to the project's result record; never rewrite
   the original score to make the prediction look accurate.

The tracked example at `templates/hook-packet.example.json` is valid input for the
validator and shows the complete structure.

