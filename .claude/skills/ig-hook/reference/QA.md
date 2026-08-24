# Visual-hook QA

Run this gate on the selected 0–8 second opening before it reaches the main Premiere
sequence. Trial mode runs it independently on A, B, and C.

## 1. Storyboard gate

Composite the designed layer over actual A-roll at:

`0.15s · 1.25s · 3.25s · 5.25s · 7.25s`

Pass only when:

- frame zero contains the claimed object, consequence, or receipt;
- the frame is understandable on mute;
- the evidence is literal and verified, not a typographic substitute;
- the 3.25s frame advances the argument rather than repeating the headline;
- the 5.25s or 7.25s frame reveals a mechanism or next step;
- the subject, hands, proof, and text do not collide;
- each text-bearing object has a caption mute window;
- the five stills read as one causal sequence, not five unrelated cards.

## 2. Pixel gate

- Render at the live sequence frame rate and 1080×1920.
- Check top, bottom, and side safe zones from `brand.json`.
- Compare the overlay against the real A-roll frame, not transparency.
- Verify text and proof at phone-viewing size.
- Check surfaces are opaque where `ig-show` requires them.
- Check the designed layer does not unintentionally darken or recolor the face.
- Reject duplicated evidence unless `samenessIsClaim` is true and provenance is explicit.
- Reject any number that cannot be traced to the evidence ledger.

`hyperframes lint` and `check` prove validity, not quality. Read the five pixels.

## 3. Motion gate

- Every state is seek-safe and deterministic.
- Motion changes the argument: reveal, compare, annotate, correct, or reframe.
- No ambient drift or loop is accepted as the second beat.
- A Lockup candidate may hold still for readability under `VISUAL-HOOK.md`; other modes
  should produce a meaningful state change by second five.
- One mover at a time unless simultaneous contrast is the point.
- No exit animation; the cut is the exit.

## 4. Premiere gate

1. `verify_premiere_connection` and read the current server instructions.
2. Confirm sequence fps, dimensions, and tracks.
3. Work in `HOOK-LAB__<slug>__<candidate>`, never the main sequence.
4. Import rendered assets and place them at Hook Packet cues.
5. Read clip positions back from Premiere; do not infer frames from source time.
6. Export or composite frames at all five QA times.
7. Assert each expected file exists. `export_frame` may lie on this machine.
8. Render a short preview and watch it once muted, once with sound, once at 1× on a phone-
   sized window.

If the same MCP call fails twice, run the CEP panel diagnostics and stop retrying.

## 5. Promotion gate

The selected candidate may enter the main sequence only if:

- validator passes;
- storyboard and pixel gates pass;
- all evidence is verified;
- `qa.status` is `pass`;
- the user approved it, or Fast mode was explicitly requested.

## 6. Learning after publication

Record candidate ID, mode, exact 0–8 speech, frame-zero object, duration, Trial/feed status,
reach, views, average watch time, saves, shares, and buyer actions when available.

Do not call a hook good or bad from a single low-reach upload. Distribution is noisy; Feez's
own byte-identical Reel pairs produced roughly 4–5× different view counts. Below about 300
reached accounts, mark the result `insufficient-signal` rather than rewriting the system.

Prefer sibling-variant comparisons:

1. average watch time and watch-time/duration;
2. shares and saves per reached account;
3. reach/views;
4. qualified profile actions, DMs, and calls for buyer-specific content.

