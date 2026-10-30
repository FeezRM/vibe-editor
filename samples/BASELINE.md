# BASELINE: the approved edit every new edit has to match

**9278 "Instagram just dropped Muse", v5 (2026-10-28).** The creator approved it: "this should be the baseline for
all edits going forward." `samples/STYLE.md` describes the reference reels. This file describes the one edit made by
this pipeline that reached their level. Before handing over any edit, put its frames next to this one. If it has less
going on, or looks cheaper, it is not done yet.

Local copies (gitignored), in `samples/baseline/`:
- `9278-muse-v5.mp4` is the final.
- `graphics-plan.json`, `cuts.overrides.json`, `captions.overrides.json` and `compositions/*.html` are the decisions
  and the code that produced it.

Open a composition before writing a new one of the same kind. Reuse its structure and spacing, but write the content
fresh for the new video.

## The reel, beat by beat (18.8 s)

| t (s) | Said | On screen | Device |
|---|---|---|---|
| 0.0 | "Okay, Instagram" | caption `OKAY INSTAGRAM` (Tactic italic caps) + Instagram logo under it, from frame 0; camera zooms out from 1.35× | logo under the word |
| 0.8 | "just dropped the greatest" | a card under the caption plays Meta's own launch reel: "Introducing **Muse**" | real clip of the thing that dropped |
| 1.8 | "AI assistant" | same card: "Muse 😊 is your personal AI agent"; caption cyan | (continues) |
| 3.0 | "that makes viral videos" | the creator's three top reels **playing**, each tile with its real play count (▷ 973K / 26.2K / 19.2K); caption green | proof, in motion |
| 4.1–5.5 | "I'm not even joking, you've probably heard of it" | face only | breather |
| 5.5 | "It's called Muse" | Muse's real app icon under the caption; caption cyan | logo under the word |
| 6.4 | "And since it has access to Instagram" | Instagram's own Muse screen: the chat with "Connect my Instagram, Facebook, DMs…" | real UI card |
| 8.1–13.6 | "tell it to find viral content … for your account. It'll analyze your account and research some perfect content" | **a Muse chat acting out the line**: the message is sent → "is working…" with typing dots → a bubble with the creator's avatar and @<handle> reading "Analyzing your account…" as a bar fills → the chat scrolls and Muse answers with three ideas, popping in one by one | acted-out UI, timed to the words |
| 13.6–14.9 | "And you can even tell it to look through" | face only | breather |
| 14.9 | "your followers for potential outreach" | the creator's real followers row; a cyan ring draws itself round 1,551 | real UI + one pointed move |
| 16.7–17.6 | "It's actually INSANE" | face; `INSANE` in green caps | the caption carries it |
| 17.6 | "You gotta use it ASAP" | split screen: Muse's own "Your Muse gets it ✓ done" with confetti, to the last word; `ASAP` in red | payoff from the product itself |

Ten visual moments in 18.8 s, five different devices, and something on screen through the whole hook. The
face-only stretches are short (≤ 1.4 s) and come right after a dense beat.

## What made it work, from the creator's notes on v1–v4

- **The hook needs a visual on every line, not just the first word.** v4 had a logo at 0 s and then nothing until
  3 s: "the hook is not hooking." In v5 a logo, then the launch clip, then the reels playing run from 0 to 4 s.
- **Act out the claim; don't stand in for it.** For "tell it to find viral content", a zoomed-in stock clip of someone
  typing a different request read as "weird". What landed was the claim itself: a chat where you message the AI and
  watch it do the thing, with each step on the word that says it. When a line describes a workflow, show that
  workflow happening.
- **Use several devices, not one card type repeated.** v3 had seven still cards under the caption and got "we should
  improve on the visuals". v5 mixes logos, a playing clip, playing reels, a real UI card, an acted-out chat, a ring
  that draws, and a split screen.
- **Motion where it means something.** Reels play, the chat sends, types, loads and scrolls, the ring draws. Cards
  still come in fast: a 0.18–0.2 s slide-up, or a hard cut.
- **No decorative flourishes.** The light-leak glow on "insane" was "tacky", so it is gone, along with its whoosh.
  An emphasis word gets a keyword caption, not an effect.
- **Real material first:**
  - the creator's own reels with real play counts;
  - the product's own launch reel (@muse);
  - Instagram's own @creators screens;
  - the creator's own profile.
  The only made-up visual is the acted-out chat. It carries no numbers, uses the real icon, avatar and handle, and
  its `provenance` says it is an illustration.
- **Measured look:**
  - captions are Europa Grotesk SH Bold ~84 px at frame centre, with keywords in Tactic Sans Ultra Italic caps
    (`presets/vertical/samples`);
  - the camera is locked, with the face ~0.25 of the frame wide at 0.33 of the height;
  - one opening zoom-out;
  - zero pauses.

## Where material came from (so the next edit knows where to look)

- Product footage: the product's own Instagram reels. `yt-dlp` downloaded `instagram.com/<acct>/reel/<id>` logged
  out, even though IG profiles and reels tabs are login-walled.
- Platform screens: Instagram's @creators carousel on Threads (`threads.com/@creators/post/<id>/media`). The page's
  `<img>`/`<video>` tags hold the 1080 px originals.
- The creator's profile and followers: `instagram.com/<handle>`, captured in the browser pane at 430 px wide with the
  login modal hidden.
- The creator's own reels: `samples/` (posted exports), with plays from `samples/INDEX.md`.
