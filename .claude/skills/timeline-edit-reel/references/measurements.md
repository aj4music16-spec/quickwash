# Reference measurements

Source: a client-supplied 10.84 s phone screen recording (1320x2868, 120 fps, AAC stereo) of a third-party
interior-renovation reel made in an editing app ("Edits"-style). Measured 2026-11-19 with ffmpeg + numpy
(`scripts/beats.py` for audio; frame luminance / correlation scripts for video). Numbers only — no frames of the
third-party footage are kept in this repo. The viewer's own UI (status bar, back arrow, like/comment/share rail,
"Made with Edits" pill, username, caption, buttons, progress bar) was ignored.

## Frame mapping

The reel fills the phone screen's full width (1320 px) and runs from the top edge to the comment bar (~2690 px),
so the platform crops the sides of a 9:16 source a little. Proportions below are given as fractions of the
**visible width W = 1320** and then converted to a 1080-wide frame (x 0.818). Vertical positions are given in the
same width units; this is the safest mapping because the exact side crop is unknown (±7%).

| Element | Reference (px @1320) | Fraction of W | 1080x1920 (used in the overlay) |
|---|---|---|---|
| Duration label, cap/digit height | 385–450 (65 incl. comma) | 0.049 | font 64 px Inter 700, top 208 |
| Label centre x | 659 | 0.50 (frame centre) | 540 |
| Label bottom -> strip top | 136 | 0.103 | ~100 |
| Strip panel x | 155–1226 (1071 wide) | 0.117–0.929 (0.811) | 102–978 (876), centred |
| Strip panel y | 586–774 (188 tall) | top at 0.204 of screen height | 372–526 (154 tall) |
| Thumbnail rows inside panel | 598–758 (160 tall), ~12 px inset | 0.121 | 134 tall, 10 px inset |
| Thumbnail cell | ~88 x 160 (portrait, ≈9:16) | | 75 x 134 |
| Tile gap / corner radius | ~6 px / ~12 px | | 6 px / 10 px |
| Panel colour | #0f0f0f | | #111113 |
| Black ("gap") tile colour | #0b0009 – #060005 (near-black, faint purple) | | #0d0b12 |
| Playhead | 10 px wide (x 687–696), y 587–765, white, fixed | 0.0076 | 8 px, panel height + 2x5 px |
| Playhead x | 692 = centre of the strip (strip is offset 32 px right of frame centre) | | 540 (strip centred instead) |
| Trim handle | 53 x 54 white rounded rect (r≈14), 6 px black vertical bar | 0.040 | 43 x 44, r 12, 5x20 bar |
| "+" tile | 87 x 87 white (r≈18), black plus, fixed at the strip's right end, over the tiles | 0.066 | 71 x 71, r 16 |

Handles sit on the outer edges of footage tiles (straddling the edge, mostly inside the tile); the "+" does not
scroll. Left of the timeline start the panel is empty (the app shows a small mute icon there; not copied).

## Motion

- Strip scroll: constant 455 px/s (±10, 12-frame correlation steps of 45–46 px from 1.5 s to 10.5 s), i.e.
  **0.345 W per second of timeline** -> 372 px/s at 1080. Linear, no easing. One second of timeline = 0.42 of the
  strip's width; the strip shows ≈2.35 s, ≈1.2 s ahead of the playhead.
- The tile under the playhead is always the segment on screen: tiles are laid out in real time at that px/s.
- Cuts: every transition is a hard cut (luminance jumps in one source frame; 0 intermediate frames at 120 fps).
  Source cadence ≈30 fps (every value held 4 recorded frames). No fades, no zooms on footage, no speed ramps.
- Label: static per segment (not a counter), switches at the segment boundary (within ~1–3 frames), shows one
  decimal with a comma ("1,2s"); gaps get a duration label too.

## Schedule (recording time; playback starts ~0.75 s after a paused first frame)

| Seg | Time (s) | Length (s) | Label |
|---|---|---|---|
| clip (ceiling) | 0.75–2.07 | 1.32 | 1,0s |
| black | 2.07–2.95 | 0.88 | 0,8s |
| clip (window wall) | 2.95–4.22 | 1.27 | 1,2s |
| black | 4.22–4.78 | 0.57 | 0,5s |
| clip (cabinet) | 4.78–5.38 | 0.60 | 0,4s |
| clip (plaster, no gap) | 5.38–6.25 | 0.87 | 0,8s |
| black | 6.25–7.25 | 1.00 | 1,0s |
| clip (worker, plank) | 7.25–8.62 | 1.37 | 1,3s |
| black | 8.62–9.39 | 0.78 | 0,7s |
| clip (worker, sander) | 9.39–10.49 | 1.10 | 1,1s |
| black | 10.49–(10.84+) | ≥0.35 | 1,0s |

- Clips 0.6–1.4 s (median ≈1.2), gaps 0.57–1.0 s (median ≈0.8, not constant); gap ≈ 0.65 x clip.
  Clip+gap pairs: 2.15, 2.03, 2.37, 1.87 s (≈ one bar).
- Labels read 0–0.3 s short of the measured lengths (truncated, and the app's own rounding); treat them as
  approximate, not frame-exact.
- One clip-to-clip cut without a gap (cabinet -> plaster): the pattern is mostly but not strictly alternating.

## Audio

- Integrated -9.3 LUFS (loud, platform-normalised music). Silent until 1.14 s (paused start).
- Tempo ≈107 BPM (beat 0.56 s). Strongest onsets every ~1.09 s (2 beats): 1.97, 3.06, 4.15, 6.33, 7.42, 8.51,
  9.60, 10.70 s.
- Cuts vs that 2-beat grid: black-in cuts at 2.07 / 4.22 / 6.25 / 8.62 sit +0.10 / +0.07 / −0.08 / +0.11 s off;
  clip-in cuts 2.95 / 4.78 / 7.25 / 9.39 sit −0.11 / +0.03 / −0.17 / −0.21 s off. So the edit is on the music
  loosely (±0.2 s, one bar per clip+gap) rather than frame-locked; part of the offset may be screen-recording A/V
  skew. Our builder locks every boundary to the beat grid instead (tighter, reads as deliberate).

## Footage character

Locked-off or slow handheld, wide/medium interiors and one-action close-ups (a man sawing a plank, a sander);
muted warm-brown grade, low saturation, soft window light; no text, no captions, no speed effects.
