# Review — "Full Service" (2026-11-10)

## Creative calls
- **Angle:** New Jersey is the only state where you don't pump your own gas, so "full service" is
  already a point of local pride. QuickWash is that, for washing the car. End line: FULL SERVICE IS A JERSEY THING.
- **Form:** one drive past roadside signs, whip-pans left on the beat, one squeegee wipe from
  black-and-white to colour, one crane up into the end card.
- **No generated images.** The two photos are existing project shots, shown at their native 16:9 on
  a billboard so they stay sharp. Everything else is drawn in code; the app screens and logo are QuickWash's own.
- **Small jokes kept on purpose:** the yellow "IT EXISTS" tab on Central Jersey; the booking meter stops at :19 ("under 20").
- **Storylines not built:** "Salt Season" (winter, photographic) and "What Exit?" (coverage). See STORYLINES.md.

## Measured
- `hyperframes check`: 0 errors, 0 warnings (lint, layout, read-time, contrast, first frame).
- Render: 575 frames, 19.167 s, 1080×1920, H.264 + AAC, 4.6 MB.
- Sound: −14.1 LUFS integrated, true peak −1.3 dB, no clipping; first onsets at 0.02 s (bell),
  0.41 s and 0.83 s (the beat grid).

## Looked at
- 12 beat frames, the phone-width sheet, 10 cut strips (−0.2 s to +0.2 s around every seam),
  5 frames at full resolution, and 20 frames pulled from the rendered MP4.

## Not checked
- **The sound was measured, not heard.** It is synthesized in `tools/soundtrack.js`.
- Motion was judged from still frames, not watched at speed.

## Fixed during review
- New headline showed through below the squeegee blade → clipped to the clean side.
- Squeegee handle hung into frame before the wipe → handle now trails above the blade.
- "Film scratch" lines read as rendering glitches → removed.
- Elements hidden with a timeline `set` could flash on a scene's first frame → hidden in CSS instead.
- WashClub footer was on screen 1.1 s → now 1.7 s.

## Weakest shot, and what more time would buy
- The hook holds a still sign for about a second (only "GAS" gets painted). A photo or short clip
  of a real full-service attendant behind the sign would make the first frame warmer.
- The hills and road are deliberately plain; they sit under the platform's caption area.

## Known mismatches (from the source material)
- The app screenshots name the middle package "Mini Detail" and show Full Detail at $350 for
  members; the website says "Detail" and $349. The price sign follows the website.
- The app screenshots show the account name and street addresses that are on the public website.
- The phone's status bar (time, signal, battery) is redrawn so the three screens match.
