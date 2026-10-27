# B-ROLL STORY — the playbook

A talking-head reel told mostly in the creator's **own** b-roll, cut on the nouns, with **game-world graphics**
only where the face is on screen. Look: `presets/vertical/broll-story` (numbers in `broll_story`), graphics style
`presets/vertical/pixel-arcade`. Case study: the 9030 reel ("Is it possible to get to 10K a month while working a
job and in uni?"), 27 s, cut and captioned by the creator in Premiere, b-roll and graphics added on top, then
re-edited by the creator. Every rule below is either something that edit does or something the creator rejected.

## 1. The beat map: what the viewer sees, line by line

| Line type | Picture | 9030 |
|---|---|---|
| **The hook question** (frame zero) | the face, with a game scene performing the question's number | "Is it possible to get to 10K a month…": pixel stand-in punches a $ block, the counter rolls white → green to $10,000 |
| **A list of conditions** | a fast montage, one real shot per condition (`hook_montage_shots`, each `hook_montage_shot_s`) | "…while working a job and in uni?": 5 shots of 0.4–0.5 s: office, desk, campus library, a walk, campus hall |
| **The honest reaction** | the face, music out | "Yeah, I don't know, man. I'm trying to figure this out": the creator *removed* the b-roll here and the music drops |
| **Each concrete noun / place / activity** | the creator doing exactly that thing (`shot_s`) | co-op → his office desk · post content → his editor on screen · comp sci in uni → the campus hall · AI → a chat on his monitor |
| **A past claim** | the receipt from back then, in the footage | "when I was in high school": his old account's video grid with real view counts on a monitor |
| **The proof number** | the face, with the game world returning, changed | "150K followers": the same pixel stand-in, now with a crowd of pixel followers counting to the real 151.4K |
| **The identity pivot** | a short face beat, then the noun | "So I'm basically" (face, 0.6 s) → "the content AI expert" (his ChatGPT-prompts page) |
| **The CTA / journey** | the creator moving through the world | "if you want to see the journey, hit follow": a night walk |

Face share lands in `face_share` (9030: ~27 %). A face window shorter than `face_window_min_s` is a flash, not a
beat; cut to b-roll or hold the face longer.

## 2. Choosing b-roll

- **Own footage only, and it must be him doing the thing.** Screens showing *other* creators' grids or reels are
  never shown as his content. At most they illustrate "studying content", and even that got cut.
- **Proof beats illustration.** A monitor scrolling his real old posts with view counts is worth more than any
  graphic of a follower count.
- **Search the whole library, not just the newest folder.** The first pass used only the last week's clips and the
  creator called the picks "not good". The strong clips (old account grid, whiteboard strategy, 2024 editing, AI
  prompt pages) were a year older. Make a contact sheet of every clip before choosing.
- **Pick the frame range, not just the clip.** Skip ranges with a hand over the lens, a blurry swing or a selfie
  stare; land on the action (typing, pointing at the diagram, the counter visible).
- A clip appears at most `max_same_clip_uses` times, and never twice in a row from the same moment.
- Phone footage is 4K vertical: `phone_4k_scale_pct` (50) in a 1080×1920 sequence. Script-placed clips are not
  re-fitted by Premiere.

## 3. Cutting

- Cut on word onsets (from `transcript/spine-words.json`), never mid-word.
- **Snap every edit to the frame grid** (`frame_snap_frames`). 24 fps phone clips on a 30 fps timeline round
  their outs a frame short; extend the out or start the next shot one frame early. A single frame of face between
  two b-roll shots reads as a glitch.
- Montage shots go on their own track above the main b-roll so the creator can shuffle them; he will.

## 4. Graphics: only on the face, only as play

Graphics sit **only in face windows** (`graphic_windows: face`) and never over b-roll. When they do appear,
they **play**:

- **A game world with a stand-in of the creator.** `pixel-quest` (money: run, punch the $ block, coins → counter)
  and `pixel-crowd` (audience: followers pour in, count, hearts). Dress the hero with `look` sampled from the
  footage (hair, skin, glasses, beard, shirt and logo colour, pants, shoes), and use the **same look in every
  graphic** so it reads as one character returning.
- **The number is real and performed.** It counts on the spoken word and lands on the unit; the colour shift
  carries the meaning (white → green for money gained). Provenance goes in the plan.
- **Real proof inside the world.** His real avatar, pixelated to 16×16, in the follower HUD.
- **Callback, changed state:** the second graphic reuses the hero and ledge with something new (a crowd), not a
  second copy of the first.
- Placement follows **his framing, not the raw's**. His sequence punches in on V1 (head reaches y≈250 in the
  hook), so the `top` slot measured on the spine covered his hair; `inline` (below the captions) was clear.
  Check every graphic on the program monitor (PrintWindow) before calling it placed.

### Rejected by the creator, in his words

| What was shown | Verdict |
|---|---|
| A keyed green-screen cash explosion over his face | "tacky" |
| A hand-made profile card (PIL) placed over b-roll | "out of place" |
| The stock `metric` counter "$10k / month" | "lacks creativity in every single aspect" |
| A `receipt`: a real profile screenshot slowly zooming | "an image zooming in… there's nothing of substance" |
| A pixel-art game scene with a character that looks like him | asked for it, then asked to make it a style |

So: no stock overlays, no stills that only zoom, no generic counters or text cards. If a beat can't be played
as a scene, leave the face and the caption alone.

## 5. Sound

- Music bed at `music_clip_gain_db` (−15 dB clip gain), dropping out under the honest reaction beat.
- One hit (the creator's "Deep Hit") at frame zero; no extra SFX on b-roll cuts.
- B-roll is always silent: video only, its camera audio removed.

## 6. Captions

The creator's own: white, bold, lowercase, 2–4 words, centred at about y 960 on his punched-in frame. Don't add a
second caption layer on his sequence.

## 7. Premiere mechanics (his finished cut)

Tracks: V1 A-roll (punched in), V2 b-roll, V4–V6 montage / extra b-roll, V5 graphics; A1 voice, A2 music,
A3 hit. The pipeline adopts his cut (`ig-reel` → Premiere), builds and QAs the graphics, and the renders are
placed by hand.

- `add_to_timeline` with `linkAudio:false` still overwrites the A track with the **same index** before deleting
  its own audio: it wiped the music under every b-roll shot once. Place video on a V track whose A lane is
  empty, and diff the audio tracks after every placement.
- `place-layers.mjs` lifts V2–V4 and adds the pipeline's captions, so don't run it on his sequence.
- He edits between turns (nested the hook, rebuilt the montage, removed a shot). Re-list the tracks before every
  change and keep his edits.
- Leave saving to him (Ctrl+S); say so.

## 8. Checklist before handing over

- [ ] Every b-roll shot is his footage of the exact noun, a good range, scale correct
- [ ] No one-frame face flashes; every edit on a word onset
- [ ] Face windows = hook question, honest reaction, proof number, identity pivot; graphics only there
- [ ] Graphics play (a scene, a performed real number), the hero's look is consistent, provenance written
- [ ] Graphics checked on his framed program monitor, not only on the spine
- [ ] Voice, music and hit tracks read back unchanged; music gain intact
