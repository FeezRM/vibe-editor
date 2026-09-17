# captions — the look (numbers in `numbers.json` → `captions`)

The video is watched on mute; the captions are the video. One line, 2–5 words, lowercase Inter 800 (tight
tracking) at `size_px`, centred in the band `band_top`–`band_bottom` (under the chin, never the bottom third),
≤ `max_width_frac` of the frame, white with a dark halo (`glow`) and no stroke or box.

Hard cut on the frame the first word is spoken, hard cut off when the next group starts. No slide,
fade or scale — ever (rejected twice by the owner; `docs/lab-notes-archive.md#caption-motion`).

Emphasis: at most `accent_share_max` of groups carry one accented word, set in the italic serif
(Playfair Display Italic) — white `em` for the payload word of a phrase, green `good` / gold `hot` for a
number, red `bad` for the wrong/old thing. This is the reference look (Jason's “edited by *Claude*”, Faiz's
green script “$10k”). Never two colours in a
line, never three accented groups in a row. The first group may render at `hook_size_px` when it is
2–3 words.

Mute windows: where a graphic carries its own words (`phrase`), the caption is dropped for that
window — not shrunk, not moved.

Case is `lower` to match Faiz's hand-edited reels; `"none"` keeps the transcript's case, `"upper"` is
the old Anton look and was rejected on sight (archive#caption-font).
