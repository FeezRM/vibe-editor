"""Motion-density gate - measure whether a composition is actually animated.

`hyperframes check` verifies a composition is CORRECT. Nothing verified it was
ALIVE. Three finished videos shipped with 58% of every animated property being
`opacity`, zero rotation, zero depth, zero masks, and a median of 9 tweens per
composition. Four of twenty-four compositions were, literally, a card that fades
in. Every one of them passed `lint` and `check`.

This is the counter that would have caught that. Same doctrine as the rest of the
repo: a verification step that cannot fail is not a verification step - applied,
for the first time here, to craft rather than correctness.

    python analysis/motion-density.py projects/<slug>/compositions/07-scene.html
    python analysis/motion-density.py projects/<slug>/compositions/*.html
    python analysis/motion-density.py --baseline projects/*/compositions/*.html

Exit 0 = clears the floor. Exit 1 = one or more HARD metrics failed.
`--baseline` reports without enforcing, for auditing existing work.

WHAT IT CANNOT SEE. It reads the source, not the pixels. It cannot tell you the
motion is *good* - only that it exists. A composition can clear every threshold
here and still be ugly, mistimed, or off-style. It is a floor, not a ceiling, and
it does not replace compositing the render over a real A-roll frame and looking
at it.
"""
import re
import sys
import os

# ---------------------------------------------------------------- thresholds
# Calibrated against the built corpus (projects/*/compositions/*.html). See
# .claude/skills/ig-show/reference/SAMPLES.md for what the target tier does.
HARD = {
    "tweens":     (25,   "ge", "tween count"),
    "states":     (5,    "ge", "distinct timeline cues"),
    "properties": (6,    "ge", "distinct animated properties"),
    "fade_share": (0.50, "le", "fade share of animated properties"),
    "depth":      (1,    "ge", "elements with depth"),
}

# Properties that are a fade and nothing else.
FADE_PROPS = {"opacity", "autoAlpha"}

# Anything here means the composition has left the flat axis-aligned plane.
DEPTH_MARKERS = [
    r"box-shadow\s*:", r"text-shadow\s*:", r"drop-shadow\(", r"blur\(",
    r"backdrop-filter\s*:", r"perspective", r"rotateX", r"rotateY", r"rotateZ",
    r"translateZ", r"matrix3d", r"\bskew", r"\brotate\b", r"transform-style",
    r"mask-image\s*:", r"-webkit-mask", r"clip-path\s*:", r"mix-blend-mode\s*:",
]

# GSAP shorthands that are not animated properties.
NOT_A_PROPERTY = {
    "duration", "ease", "delay", "stagger", "repeat", "yoyo", "onComplete",
    "onUpdate", "onStart", "immediateRender", "overwrite", "paused", "id",
    "repeatDelay", "yoyoEase", "callbackScope", "onRepeat", "onReverseComplete",
    "transformOrigin", "svgOrigin", "force3D", "lazy", "data", "keyframes",
    "startAt", "runBackwards", "inherit", "smoothOrigin",
}

TWEEN_CALL = re.compile(r"\btl\s*\.\s*(to|from|fromTo)\s*\(")
SET_CALL = re.compile(r"\btl\s*\.\s*set\s*\(")
CALL_CALL = re.compile(r"\btl\s*\.\s*(call|add)\s*\(")
LABEL_CALL = re.compile(r"\btl\s*\.\s*addLabel\s*\(")


def strip_comments(js):
    """Remove block and line comments. Parts of the corpus are more than half
    comments by line, and those comments are full of the words we grep for."""
    js = re.sub(r"/\*.*?\*/", " ", js, flags=re.S)
    js = re.sub(r"(^|[^:])//[^\n]*", r"\1", js)
    return js


def scripts_of(html):
    return "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S))


def balanced(src, open_idx):
    """Return the substring from the bracket at open_idx to its match."""
    depth, i, n = 0, open_idx, len(src)
    while i < n:
        c = src[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return src[open_idx:i + 1]
        elif c == '"' or c == "'":
            q, i = c, i + 1
            while i < n and src[i] != q:
                i += 2 if src[i] == "\\" else 1
        i += 1
    return src[open_idx:]


def object_literals(arg_src):
    """Every top-level brace group inside a call's argument list.
    fromTo carries two of them."""
    out, i, n = [], 0, len(arg_src)
    while i < n:
        c = arg_src[i]
        if c == "{":
            body = balanced(arg_src, i)
            out.append(body)
            i += len(body)
        elif c == '"' or c == "'":
            q, i = c, i + 1
            while i < n and arg_src[i] != q:
                i += 2 if arg_src[i] == "\\" else 1
            i += 1
        else:
            i += 1
    return out


def props_in(obj_src):
    """Keys of an object literal, top nesting level only."""
    inner = obj_src[1:-1]
    keys, depth, i, n, buf = [], 0, 0, len(inner), ""
    while i < n:
        c = inner[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == '"' or c == "'":
            q, i = c, i + 1
            while i < n and inner[i] != q:
                i += 2 if inner[i] == "\\" else 1
        elif c == "," and depth == 0:
            buf = ""
            i += 1
            continue
        if depth == 0 and c == ":":
            k = buf.strip().strip('"').strip("'")
            if re.fullmatch(r"[A-Za-z_$][\w$]*", k or ""):
                keys.append(k)
            buf = ""
            i += 1
            continue
        buf += c
        i += 1
    return [k for k in keys if k not in NOT_A_PROPERTY]


def loop_multipliers(js):
    """Source spans that repeat, with their repetition count. The corpus leans on
    `REVEAL.forEach(...)` and `[1,4].forEach(...)`; counting those as one tween
    each understates real density fivefold."""
    consts = {}
    pat = r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(\[[^\]]*\])"
    for m in re.finditer(pat, js):
        items = [x for x in m.group(2)[1:-1].split(",") if x.strip()]
        consts[m.group(1)] = len(items)

    spans = []
    fe = r"(\[[^\]]*\]|\b[A-Za-z_$][\w$]*)\s*\.\s*forEach\s*\("
    for m in re.finditer(fe, js):
        tok = m.group(1)
        if tok.startswith("["):
            n = len([x for x in tok[1:-1].split(",") if x.strip()])
        else:
            n = consts.get(tok, 1)
        body = balanced(js, m.end() - 1)
        if n > 1:
            spans.append((m.end() - 1, m.end() - 1 + len(body), n))

    fl = r"\bfor\s*\([^;]*;\s*[A-Za-z_$][\w$]*\s*<\s*(\d+)\s*;"
    for m in re.finditer(fl, js):
        brace = js.find("{", m.end())
        if brace != -1:
            body = balanced(js, brace)
            n = int(m.group(1))
            if n > 1:
                spans.append((brace, brace + len(body), n))
    return spans


def multiplier_at(spans, idx):
    mult = 1
    for a, b, n in spans:
        if a <= idx < b:
            mult *= n
    return mult


def cue_times(arg):
    """The position parameter is whatever trails the final object literal."""
    tail = arg[arg.rfind("}") + 1:] if "}" in arg else arg
    return re.findall(r"-?\d+\.?\d*", tail)


def analyse(path):
    html = open(path, encoding="utf-8", errors="replace").read()
    js = strip_comments(scripts_of(html))
    spans = loop_multipliers(js)

    tweens = 0
    prop_hits = []          # one entry per (tween x property), loop-expanded
    cues = set()

    for m in TWEEN_CALL.finditer(js):
        idx = m.end() - 1
        mult = multiplier_at(spans, idx)
        arg = balanced(js, idx)
        tweens += mult

        objs = object_literals(arg)
        keys = props_in(objs[-1]) if objs else []
        if m.group(1) == "fromTo" and len(objs) >= 2:
            keys = sorted(set(props_in(objs[0])) | set(props_in(objs[1])))
        for k in keys:
            prop_hits.extend([k] * mult)

        for num in cue_times(arg):
            cues.add(num)

    for rx in (SET_CALL, CALL_CALL):
        for m in rx.finditer(js):
            for num in cue_times(balanced(js, m.end() - 1)):
                cues.add(num)

    labels = len(LABEL_CALL.findall(js))
    depth = sum(len(re.findall(rx, html)) for rx in DEPTH_MARKERS)

    total = len(prop_hits)
    fades = sum(1 for p in prop_hits if p in FADE_PROPS)
    distinct = sorted(set(prop_hits))

    return {
        "path": path,
        "tweens": tweens,
        "states": len(cues),
        "labels": labels,
        "properties": len(distinct),
        "prop_list": distinct,
        "fade_share": (fades / total) if total else 1.0,
        "depth": depth,
    }


def verdict(r):
    fails = []
    for key in HARD:
        limit, op, label = HARD[key]
        v = r[key]
        ok = (v >= limit) if op == "ge" else (v <= limit)
        if not ok:
            fails.append((label, v))
    return fails


def fmt(r, fails, baseline):
    bad = set(f[0] for f in fails)

    def mark(label):
        return "!" if label in bad else " "

    lines = [
        "",
        "  " + os.path.basename(r["path"]),
        "   %s tweens                %5d   (>= %d)"
        % (mark("tween count"), r["tweens"], HARD["tweens"][0]),
        "   %s distinct cues         %5d   (>= %d)"
        % (mark("distinct timeline cues"), r["states"], HARD["states"][0]),
        "   %s animated properties   %5d   (>= %d)"
        % (mark("distinct animated properties"), r["properties"],
           HARD["properties"][0]),
        "   %s fade share             %4.0f%%   (<= %.0f%%)"
        % (mark("fade share of animated properties"), r["fade_share"] * 100,
           HARD["fade_share"][0] * 100),
        "   %s depth markers         %5d   (>= %d)"
        % (mark("elements with depth"), r["depth"], HARD["depth"][0]),
        "     timeline labels       %5d   (advisory)" % r["labels"],
        "     vocabulary: " + (", ".join(r["prop_list"]) or "(none)"),
    ]
    if not baseline:
        if fails:
            detail = "; ".join("%s %s" % (l, v) for l, v in fails)
            lines.append("     FAIL - " + detail)
        else:
            lines.append("     PASS")
    return "\n".join(lines)


def main(argv):
    baseline = "--baseline" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2

    failed_any = False
    rows = []
    for p in paths:
        if not os.path.isfile(p):
            print("  %s: not found" % p, file=sys.stderr)
            failed_any = True
            continue
        r = analyse(p)
        f = verdict(r)
        rows.append((r, f))
        print(fmt(r, f, baseline))
        if f:
            failed_any = True

    if len(rows) > 1:
        clear = sum(1 for _, f in rows if not f)
        print("\n  %d/%d compositions clear the motion floor."
              % (clear, len(rows)))

    if baseline:
        return 0
    return 1 if failed_any else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
