#!/usr/bin/env python3
"""Build PixelQuest.ttf — the pixel-arcade look's typeface — from the bitmap table in presets/graphics/_pixel.html.

One home for the letterforms: the canvas presets (pixel-quest, pixel-crowd) draw the same 5x7 glyphs, and this script
turns them into a real TrueType font so every other preset can wear them through the pixel-arcade skin. Each lit pixel
is a square; runs of pixels in a row merge into one rectangle. Lowercase maps to the capitals (an arcade font).

Needs fontTools (it lives in .venv-whisperx):
    .venv-whisperx/Scripts/python.exe scripts/pixel-font.py      →  presets/vertical/default/fonts/PixelQuest.ttf
"""
import json
import re
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "presets" / "graphics" / "_pixel.html"
OUT = REPO / "presets" / "vertical" / "default" / "fonts" / "PixelQuest.ttf"
UPM, P = 1000, 125            # one font pixel = 125 units → 7 rows = 875 (cap height)

text = SRC.read_text(encoding="utf-8")
block = text[text.index("PX.FONT = {"):text.index("};", text.index("PX.FONT = {"))]
glyphs = {}
for m in re.finditer(r'^\s*("(?:[^"\\]|\\.)+")\s*:\s*(\[[^\]]*\])', block, re.M):
    glyphs[json.loads(m.group(1))] = json.loads(m.group(2))
assert "A" in glyphs and "0" in glyphs, "could not parse PX.FONT"


def gname(ch: str) -> str:
    return "space" if ch == " " else f"uni{ord(ch):04X}"


fb = FontBuilder(UPM, isTTF=True)
order = [".notdef"] + [gname(c) for c in glyphs]
fb.setupGlyphOrder(order)
cmap = {ord(c): gname(c) for c in glyphs}
for c in glyphs:
    if c.isalpha() and c.isupper() and c.lower() != c:
        cmap[ord(c.lower())] = gname(c)
fb.setupCharacterMap(cmap)

pen_glyphs, metrics = {}, {}
nd = TTGlyphPen(None)
for (x0, y0, x1, y1) in [(P, 0, 5 * P, 7 * P)]:
    nd.moveTo((x0, y0)); nd.lineTo((x0, y1)); nd.lineTo((x1, y1)); nd.lineTo((x1, y0)); nd.closePath()
pen_glyphs[".notdef"] = nd.glyph()
metrics[".notdef"] = (6 * P, 0)
for ch, rows in glyphs.items():
    pen = TTGlyphPen(None)
    w = len(rows[0])
    for r, row in enumerate(rows):
        y0, y1 = (6 - r) * P, (7 - r) * P
        q = 0
        while q < w:
            if row[q] == "#":
                s = q
                while q < w and row[q] == "#":
                    q += 1
                x0, x1 = s * P, q * P
                pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0)); pen.closePath()
            else:
                q += 1
    pen_glyphs[gname(ch)] = pen.glyph()
    metrics[gname(ch)] = ((w + 1) * P, 0)
fb.setupGlyf(pen_glyphs)
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=1000, descent=-250)
fb.setupNameTable({"familyName": "PixelQuest", "styleName": "Regular", "uniqueFontIdentifier": "PixelQuest-Regular",
                   "fullName": "PixelQuest Regular", "psName": "PixelQuest-Regular", "version": "Version 1.0",
                   "licenseDescription": "Drawn for vibe-editor (presets/graphics/_pixel.html); same license as the repository."})
fb.setupOS2(sTypoAscender=1000, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=1000, usWinDescent=250,
            sCapHeight=7 * P, sxHeight=7 * P, achVendID="VIBE")
fb.setupPost()
OUT.parent.mkdir(parents=True, exist_ok=True)
fb.save(str(OUT))
print(f"pixel-font: {len(glyphs)} glyphs (+ lowercase -> caps) -> {OUT.relative_to(REPO)}")
