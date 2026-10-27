# dead-space
"cut out the dead space", "removed the silence", "tightened it" — shown on the recording's own waveform.
`workflows/waveform.py <job>` measures the raw and the cut (RMS per bin) and reads the keeps from `cuts.json`.
The raw grows out of the axis; one scan turns everything outside the keeps red; the red bars split at the axis
and their halves fly off while the speech slides together and the readout counts raw → kept seconds; then the
cut's real waveform fills the width. Every bar and number is measured. Placement: `inline` (default) or `top`.
