"""The speech envelope: where the voice actually starts and stops, measured on the audio, not inferred from
word timestamps (WhisperX word edges drift 50–150 ms, which clips onsets and leaves dead air at the tails).

One 10 ms frame = one dB value. "Loud" is relative to this recording's own speech level (the 95th percentile
of frames inside transcribed words) minus cut.edge_rel_db, so a quiet lav and a hot one cut the same way.
"""
import wave
from pathlib import Path

import numpy as np

HOP = 0.01


class Envelope:
    def __init__(self, wav: Path, words: list, rel_db: float):
        with wave.open(str(wav), "rb") as f:
            sr, n, ch, sw = f.getframerate(), f.getnframes(), f.getnchannels(), f.getsampwidth()
            raw = f.readframes(n)
        x = np.frombuffer(raw, {2: np.int16, 4: np.int32}[sw]).astype(np.float64)
        if ch > 1:
            x = x.reshape(-1, ch).mean(axis=1)
        x /= float(2 ** (8 * sw - 1))
        hop = int(sr * HOP)
        m = len(x) // hop
        rms = np.sqrt(np.mean(x[: m * hop].reshape(m, hop) ** 2, axis=1))
        self.db = 20 * np.log10(rms + 1e-9)
        inside = np.concatenate([self.db[int(w["s"] / HOP): max(int(w["s"] / HOP) + 1, int(w["e"] / HOP))] for w in words]) \
            if words else self.db
        self.speech_db = float(np.percentile(inside, 95))
        self.thr = self.speech_db - rel_db
        self.loud = self.db >= self.thr
        self.n = len(self.db)

    def i(self, t: float) -> int:
        return min(max(int(round(t / HOP)), 0), self.n - 1)

    def t(self, i: int) -> float:
        return i * HOP

    def level(self, t0: float, t1: float) -> float:
        a, b = self.i(t0), max(self.i(t1), self.i(t0) + 1)
        return float(self.db[a:b].max())

    def onset(self, lo: float, hi: float, hold: int = 3):
        """First frame in [lo, hi] that starts `hold` loud frames. None when the window is already loud at `lo`
        (continuous speech — no clean onset) or never gets loud."""
        a, b = self.i(lo), self.i(hi)
        if self.loud[a]:
            return None
        for k in range(a, b - hold + 1):
            if self.loud[k: k + hold].all():
                return self.t(k)
        return None

    def offset(self, lo: float, hi: float, hold: int = 8):
        """Start of the first run of `hold` quiet frames in [lo, hi] — where the voice stops. A dip the voice comes
        back from within `resume` frames is the closure inside a word ("wa-s"), not its end: keep scanning."""
        a, b = self.i(lo), self.i(hi)
        resume = 15
        k = a
        while k <= b - hold:
            if not self.loud[k: k + hold].any():
                back = np.flatnonzero(self.loud[k + hold: min(k + hold + resume, b)])
                if not len(back):
                    return self.t(k)
                k = k + hold + int(back[0])
                continue
            k += 1
        return None

    def quietest(self, lo: float, hi: float) -> float:
        a, b = self.i(lo), max(self.i(hi), self.i(lo) + 1)
        return self.t(a + int(np.argmin(self.db[a:b])))

    def quiet_runs(self, lo: float, hi: float, min_s: float):
        """Silences of at least min_s inside [lo, hi], as (start, end)."""
        a, b = self.i(lo), self.i(hi)
        runs, k = [], a
        while k < b:
            if not self.loud[k]:
                j = k
                while j < b and not self.loud[j]:
                    j += 1
                if (j - k) * HOP >= min_s:
                    runs.append((self.t(k), self.t(j)))
                k = j
            else:
                k += 1
        return runs

    def hot(self, t: float, w: float = 0.03) -> bool:
        """A cut at t is inside speech when both sides of it are loud."""
        return self.level(t - w, t) >= self.thr and self.level(t, t + w) >= self.thr
