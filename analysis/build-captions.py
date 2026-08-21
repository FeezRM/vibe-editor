"""Build a HyperFrames caption composition from word-level timestamps.

House caption spec (single-line variant):
  body font-size  88px   -> cap ~59px   (references measure 58-65px)
  hook font-size 140px   -> cap ~100px  (the opening block only)
  ONE LINE ALWAYS         -- never wraps to a second line
  2-4 words per caption
  max line width  842px = 78% of frame

Note on the width ceiling: the reference reels use TWO-line blocks capped at
62% of frame width. This project uses single-line captions, and 4 words cannot
fit inside 62% at 88px. Rather than shrink the type below the reference cap
height, the ceiling is raised to 78% -- which is what the references' own
single-line captions ("BUT INSTEAD") actually measure at. It is the width cap,
not the word count, that keeps a caption off the frame edges: a 4-word group of
long words measures 100% and must break into two captions.

Usage:
  python analysis/build-captions.py <words.json> <out.html> [--duration S]
"""
import json, sys, html, os

BODY_SIZE, HOOK_SIZE = 88, 140
# CAPTION MUTE WINDOWS -- handed over by ig-show in the MOTION PLAN.
#
# Only ONE text layer at a time. Where a graphic carries its own words, the
# caption track goes silent for that window; it does not shrink and it does not
# move. Measured across the reference reels: whenever a content card with its
# own baked-in text is on screen there is no burnt-in caption, and S1 -- which
# is one continuous rebuilt Instagram profile -- has no burnt-in captions at all.
#
# Blocks whose MIDPOINT falls inside a window are DROPPED, not hidden: a hidden
# block still renders its glow, which is visible over a dark graphic.
#
# Not a mute window: app UI whose text is chrome (tab bar, stat row, nav). The
# distinction is content vs chrome, not graphic vs no-graphic.
MUTE = [
    (0.00,  4.50),   # 07-hook    the lockup IS the caption for these seconds
    (14.10, 16.70),  # 06-comment the sheet carries its own comment + typed word
    (22.90, 30.17),  # 03-trials  three cover labels + three view counts
]

MAX_W = 842                      # px = 78% of frame. Hard ceiling, one line.
BODY_CPX = 842 / 16.4            # ~16 chars/line at 88px.
                                 # 17.5 under-estimated wide-glyph strings:
                                 # 'write a good hook' rendered at 80% of frame
                                 # against a predicted 76%. Measured worst case is
                                 # ~51px/char, so the budget is set from that.
HOOK_CPX = 842 / 11.0            # ~11 chars on one line at 140px
MAX_WORDS = 4                    # per caption -- and there is only one line
MIN_WORDS_HOOK = 2

# Function words that must not END a caption -- they belong with what follows,
# and a caption ending on one reads as a sentence chopped mid-phrase.
# Deliberately narrow: over-broad glue (adding "you", "just", "each") starves the
# grouper and pushes captions down to one or two words each.
GLUE = {
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "and", "or", "but",
    "so", "if", "with", "as", "than", "then", "that", "my", "your", "is", "are",
    "was", "were", "be", "into", "from", "about",
}

ACCENT = {
    "good": {"good", "best", "works", "viral", "3"},
    "bad":  {"sucked", "waste", "rest", "2", "eliminate"},
    "hot":  {"5", "hook", "trial", "farming"},
}


def accent_of(word):
    w = word.lower().strip(".,!?'’")
    for cls, terms in ACCENT.items():
        if w in terms:
            return cls
    return None


def width_of(words, cpx):
    return (sum(len(w) for w in words) + max(0, len(words) - 1)) * cpx


def fits(words, cpx):
    """One line only. A caption fits if it is inside both budgets."""
    return len(words) <= MAX_WORDS and width_of(words, cpx) <= MAX_W


def repair(words):
    """Fix word-level transcription artefacts before grouping.

    Whisper splits some words across tokens ('c' + 'uz'). A one-or-two letter
    fragment that is not a real word gets merged into its neighbour, otherwise
    it surfaces as a caption line reading 'even watch c'.
    """
    REAL = {"a", "i", "o", "ok", "so", "to", "do", "no", "go", "up", "us", "it",
            "is", "at", "in", "on", "of", "or", "my", "me", "we", "he", "by",
            "am", "an", "as", "be", "if", "hi"}
    out, i = [], 0
    while i < len(words):
        w = dict(words[i])
        tok = w["w"]
        # merge FORWARD: 'c' + 'uz' -> 'cuz'. Merging backward would produce
        # 'watchc' + 'uz' -> 'watchcuz', which is how this went wrong first time.
        while (i + 1 < len(words) and len(w["w"]) <= 2
               and w["w"].lower() not in REAL and not w["w"].isdigit()):
            nxt = words[i + 1]
            w = {**w, "w": w["w"] + nxt["w"], "e": nxt["e"],
                 "end_punct": nxt.get("end_punct", "")}
            i += 1
        out.append(w)
        i += 1
    return out


def unorphan(blocks):
    """Remove single-word captions left over when a group overflows.

    A greedy fill can strand the tail of a sentence as one word ("strat",
    "views", "this") on screen for ~0.35s, which reads as a stutter rather than
    a caption. Fix in order of preference:
      1. merge the orphan into the NEXT caption, if the result still fits
      2. merge it into the PREVIOUS caption, if that fits
      3. pull the last word of the previous caption forward, so the orphan has
         two words and the previous still has at least two
    A one-word caption that is genuinely sentence-final and held (>=0.7s) is
    left alone -- "SUCKED." on its own is the point, not an accident.
    """
    HELD = 0.7
    i = 0
    while i < len(blocks):
        b = blocks[i]
        words = b["lines"][0]
        if len(words) > 1 or (b["e"] - b["s"]) >= HELD:
            i += 1; continue

        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        prv = blocks[i - 1] if i > 0 else None

        if nxt and fits(words + nxt["lines"][0], BODY_CPX):
            nxt["lines"][0] = words + nxt["lines"][0]
            nxt["s"] = b["s"]
            blocks.pop(i); i = max(i - 1, 0); continue

        if prv and fits(prv["lines"][0] + words, BODY_CPX):
            prv["lines"][0] = prv["lines"][0] + words
            prv["e"] = b["e"]
            blocks.pop(i); i = max(i - 1, 0); continue

        if prv and len(prv["lines"][0]) >= 3:
            moved = prv["lines"][0][-1]
            if fits([moved] + words, BODY_CPX):
                prv["lines"][0] = prv["lines"][0][:-1]
                b["lines"][0] = [moved] + words
                i += 1; continue
        i += 1
    return blocks


def group(words):
    """Greedy single-line grouping.

    Extends a caption while it still fits on ONE line inside the width ceiling,
    then breaks. A group never crosses a sentence boundary, and a caption is
    never left ending on a glue word when the next word could join it.
    """
    blocks, cur = [], []

    def emit():
        if cur:
            blocks.append({"s": cur[0]["s"], "e": cur[-1]["e"],
                           "lines": [[w["w"] for w in cur]], "hook": False})

    for wd in words:
        trial = cur + [wd]
        if cur and not fits([w["w"] for w in trial], BODY_CPX):
            # Never end a caption on a function word. Pop them onto the front of
            # the next caption -- repeatedly, since a group can end on a run of
            # them ("tell you to", "just write a"). Always leave >=2 words behind.
            held = []
            while len(cur) > 2 and cur[-1]["w"].lower().strip(".,!?’") in GLUE:
                held.insert(0, cur.pop())
            emit(); cur = held + [wd]
        else:
            cur = trial
        if wd.get("end_punct"):
            emit(); cur = []
    emit()

    blocks = unorphan(blocks)

    # the opening caption is the hook, if it still fits on one line when bigger
    if blocks:
        flat = blocks[0]["lines"][0]
        if len(flat) >= MIN_WORDS_HOOK and fits(flat, HOOK_CPX):
            blocks[0]["hook"] = True

    # hold each caption until the next begins so they never flicker off
    for i, b in enumerate(blocks[:-1]):
        b["e"] = max(b["e"], min(blocks[i + 1]["s"], b["e"] + 0.35))
    return blocks


TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="stylesheet" href="tokens.css" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{
        font-family: 'EuropaLocal';
        src: url('assets/europa-grotesk-sh-bold.otf') format('opentype');
        font-weight: normal; font-style: normal; font-display: block;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: transparent; }}

      .band {{
        position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      }}
      .cap {{
        position: absolute; left: 50%; top: 50%;
        transform: translate(-50%, -50%);
        width: {maxw}px;                     /* hard ceiling: 62% of frame */
        text-align: center;
        font-family: 'EuropaLocal', sans-serif;
        font-size: {body}px; line-height: 0.98;
        letter-spacing: var(--track-caption);
        word-spacing: 0.14em;   /* the caption face + negative tracking runs words together */
        text-transform: uppercase;
        color: var(--ink);
        text-shadow: 0 0 18px rgba(0,0,0,0.88), 0 6px 26px rgba(0,0,0,0.7),
                     0 0 44px rgba(255,255,255,0.20);
        opacity: 0; will-change: opacity;
      }}
      .cap.hook {{ font-size: {hook}px; line-height: 0.94; }}
      .cap b {{ font-weight: inherit; display: block; white-space: nowrap; }}
      .cap em {{ font-style: normal; }}
      .bad  {{ color: var(--sig-down);
               text-shadow: 0 0 18px rgba(0,0,0,.88), 0 0 34px rgba(235,4,8,.75); }}
      .good {{ color: var(--sig-up);
               text-shadow: 0 0 18px rgba(0,0,0,.88), 0 0 34px rgba(0,232,0,.70); }}
      .hot  {{ color: var(--accent);
               text-shadow: 0 0 18px rgba(0,0,0,.88), 0 0 34px rgba(255,197,49,.70); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="captions" data-start="0"
         data-duration="{dur:.3f}" data-width="1080" data-height="1920"
         data-fps="30" data-track-index="0">
      <div class="band">
{caps}
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const ROWS = {rows};
      const tl = gsap.timeline({{ paused: true }});
      ROWS.forEach(function (r) {{
        const el = document.getElementById('c' + r.i);
        // HARD CUT on and off. No slide, no fade, no movement of any kind.
        // Zero-duration sets, so it is seek-safe and frame-exact: the caption
        // is either fully on or fully off, never mid-transition.
        tl.set(el, {{ opacity: 1 }}, r.s);
        tl.set(el, {{ opacity: 0 }}, r.e);
      }});
      window.__timelines['captions'] = tl;
    </script>
  </body>
</html>
"""


def render_block(i, b):
    """Render one caption block.

    Accent is applied per WORD, inline. Accenting the whole line produces
    nonsense like a red 'TO WASTE SO' -- the references colour the payload
    word itself (MELT, SECRETS, 5) or a complete noun phrase, never an
    arbitrary slice of a sentence.
    """
    cls = "cap hook" if b["hook"] else "cap"
    rows = []
    # AT MOST ONE accented word per caption. Two colours in a four-word caption
    # ("WRITE A GOOD HOOK" with GOOD green and HOOK gold) reads as decoration
    # and destroys the signal -- the eye cannot tell which word is the point.
    used = False
    for ln in b["lines"]:
        parts = []
        for w in ln:
            a = None if used else accent_of(w)
            if a:
                used = True
            esc = html.escape(w)
            parts.append(f'<em class="{a}">{esc}</em>' if a else esc)
        rows.append("<b>" + " ".join(parts) + "</b>")
    return f'        <div class="{cls}" id="c{i}">' + "".join(rows) + "</div>"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__.strip())
    src = sys.argv[1]
    out = sys.argv[2]
    words = repair(json.load(open(src)))
    blocks = group(words)
    # duration spans the whole reel and must be measured BEFORE muting, or
    # dropping a trailing block would shorten the composition
    dur = max(b["e"] for b in blocks) + 0.2

    def in_mute(b):
        mid = (b["s"] + b["e"]) / 2
        return any(a <= mid < z for a, z in MUTE)

    kept, dropped = [], []
    for b in blocks:
        (dropped if in_mute(b) else kept).append(b)
    blocks = kept
    print(f"mute windows: {len(MUTE)} -> dropped {len(dropped)} caption blocks")
    for b in dropped:
        print(f"   muted {b['s']:6.2f}-{b['e']:6.2f}  " + " ".join(b["lines"][0]))

    over = [ln for b in blocks for ln in b["lines"]
            if width_of(ln, HOOK_CPX if b["hook"] else BODY_CPX) > MAX_W]
    multi = [b for b in blocks if len(b["lines"]) != 1]
    longw = [ln for b in blocks for ln in b["lines"] if len(ln) > MAX_WORDS]
    words_per = sum(len(b["lines"][0]) for b in blocks) / len(blocks)
    print(f"{len(blocks)} captions / {dur:.2f}s | {words_per:.1f} words avg | "
          f"{len(over)} over-width | {len(multi)} multi-line | {len(longw)} over {MAX_WORDS} words")
    assert not over and not multi and not longw, "spec violation in generated captions"
    for b in blocks[:12]:
        print(f"   {b['s']:6.2f}-{b['e']:6.2f}  " + " ".join(b["lines"][0]))

    caps = "\n".join(render_block(i, b) for i, b in enumerate(blocks))
    rows = json.dumps([{"i": i, "s": round(b["s"], 3), "e": round(b["e"], 3)}
                       for i, b in enumerate(blocks)])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(TEMPLATE.format(
        maxw=MAX_W, body=BODY_SIZE, hook=HOOK_SIZE,
        dur=dur, caps=caps, rows=rows))
    print("wrote", out)
