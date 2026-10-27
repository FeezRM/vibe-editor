"""Run the WhisperX CLI unchanged, except that every segment's digits are spelled out right before alignment.

wav2vec2 has no characters for "30%" or "$5", so the aligner gives a numeral a ~0.1 s span and pushes every
later word in the sentence early (9078: "thirty percent" said over 0.45 s, the closing "value" placed 0.67 s
before it was spoken — the cut chopped it). --suppress_numerals is not the fix: the model then drops the number
entirely ("depend on the idea"). Spelling out after recognition keeps the words and makes them alignable.

Runs inside .venv-whisperx:  python workflows/_wx_spell.py <whisperx CLI args…>
"""
import re
import sys

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
       "seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def say(n: int) -> str:
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else "-" + ONES[n % 10])
    for size, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= size:
            rest = n % size
            return say(n // size) + " " + name + ("" if rest == 0 else " " + say(rest))
    return str(n)


NUM = re.compile(r"(\$)?(\d[\d,]*)(\.\d+)?(?:\s?(%|[kK]\b|[mM]\b|[xX]\b))?")


def spell(text: str) -> str:
    def one(m):
        cur, whole, frac, suf = m.groups()
        n = int(whole.replace(",", ""))
        s = say(n)
        if frac:
            s += " point " + " ".join(ONES[int(d)] for d in frac[1:])
        s += {"%": " percent", "k": " thousand", "K": " thousand", "m": " million", "M": " million",
              "x": " times", "X": " times"}.get(suf or "", "")
        if cur:
            s += " dollars"
        return s
    return NUM.sub(one, text)


if __name__ == "__main__":
    import whisperx.transcribe as wt
    from whisperx.__main__ import cli

    _align = wt.align

    def align(segments, *a, **kw):
        for s in segments:
            s["text"] = spell(s["text"])
        return _align(segments, *a, **kw)

    wt.align = align
    sys.argv = ["whisperx"] + sys.argv[1:]
    cli()
