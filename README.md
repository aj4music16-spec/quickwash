# QuickWash — "The Reset" (40s)

A fully code-driven motion piece built around *that first drive after a detail*.
Every frame is drawn in HTML/SVG, animated by a small deterministic timeline engine,
captured frame-by-frame with Playwright, and encoded with ffmpeg alongside a
synthesized soundtrack.

**Output:** `dist/quickwash-the-reset.mp4` — 1920×1080, 30 fps, H.264 + AAC, 40.0 s.

## Cue sheet

| Time | Scene | On-screen | VO (caption) |
|---|---|---|---|
| 0–4s | Fast cuts: coffee drip in cupholder → crumbs in seat seam (rack focus) → fingerprints on screen | YOU KNOW THAT FEELING? | You know that first drive after your car gets detailed? |
| 4–9s | Door swings open onto sunlit, spotless interior; light rays and dust motes | SAME CAR. NEW FEELING. | Same car. Same seat. Somehow, a completely different feeling. |
| 9–15s | Archival collage: sepia photos drop in, film flicker, newsprint texture | *The enduring appeal of* THE NEW-CAR FEELING | We've spent generations chasing that new-car feeling. |
| 15–21s | Three diagonal panels: gym bag, coffee cups piling up, receipts; MON→FRI ticker; dust settles | THEN LIFE HAPPENS. | Then life happens. And the place you spend part of every day starts collecting all of it. |
| 21–25s | Macro: foam sliding off paint, rinse sheet reveals gloss, light sweep | WASH AWAY THE WEEK. | Sometimes, a reset is clean seats. Clear windows. |
| 25–29s | Split screen: brush clearing a seam / microfiber wipe revealing a reflection | Every detail. A fresh start. | And a car that feels like yours again. |
| 29–35s | Detailer at work in the driveway; front door opens, customer steps out with coffee | MOBILE DETAILING, DELIVERED. | With QuickWash, that feeling comes to you. |
| 35–36.5s | Back inside — door shuts (thump), then a beat of quiet black | — | — |
| 36.5–40s | Glossy hero car with highlight sweep, logo card, CTA | YOUR CAR. RESET. · Book in the QuickWash app. | Book in the QuickWash app. Get back to that fresh-car feeling. |

## Files

- `video/index.html` — the composition. Open it in a browser to preview in real time
  (`?t=12.5` freezes on a frame). `window.seek(t)` renders any moment deterministically.
- `video/render.js` — Playwright steps `seek()` per frame and pipes JPEGs into ffmpeg.
- `video/audio.js` — synthesizes the score and sound design (pad progression, pulse,
  whooshes on cuts, door open/thump, bubble pops, rinse, brush strokes, logo chime).
- `video/stills.js` — grab review frames: `node video/stills.js out_dir 3.3 22 38.5`.

## Render

Requires Node, ffmpeg, and Playwright with Chromium.

```bash
node video/render.js                 # → dist/quickwash-the-reset.mp4
node video/render.js out.mp4 --fps 24
```

## Notes

- The voiceover is shown as timed captions. Drop a recorded VO onto the same timings
  (the `CAPS` array in `index.html` is the cue list); the score leaves room under it.
  To remove the captions, hide `#cap`.
- No third-party footage, podcast audio or music is used. Everything is original and generated in code.
