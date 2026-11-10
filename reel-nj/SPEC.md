# SPEC — "Full Service" (QuickWash · New Jersey · app downloads)

```text
GOAL:    A New Jersey driver smiles at the gas-pump line, sees QuickWash is full service for their
         car at their own driveway, and downloads the app.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, H.264 + AAC.
TIME:    19.167 s = 575 frames. 144 BPM, 12.5 frames per beat, 50 frames per bar.
         Stops change on beats 4, 14, 22, 30; the squeegee is beat 8; the end card is beat 38.
LOOK:    Medium = roadside signage in daylight.
         Ground: sky #5fbdf0 -> #b9e4fb (flat, no glow), white flat clouds kept in the top 170 px,
         two hill bands, grass #6cc257, asphalt #474c56 with 108 px lane dashes.
         Ink: navy #000099 on sky, white on navy. One accent, orange #f8630a, only as a painted
         slab behind one word per shot, the sign header, and lit counties.
         Display: League Gothic, caps, lines justified to one width (hook 386/326/265 px,
         headlines 183-268 px). Small text: Inter 700/900, never under 28 px.
         Depth: every object has a flat 12-14 px "thickness" edge in a darker tone; no blurs, no shadows.
         The old way: the same world in greys (#bdbdb6 sky) with a black-and-white photo.
OBJECTS: gas pylon (orange FULL SERVICE header with a white NJ silhouette, navy face, white frame,
         block base) · billboard (full-width 16:9 board, catwalk, lamps, monopole) · squeegee
         (black rubber blade, steel channel, orange joint and grip) · phone (real app screens,
         one shared status bar) · pump meter (black module, amber 7-segment digits) · sign plates
         for the three steps · NJ cut-out sign with the 21 real county shapes · map pin ·
         three green highway guide signs with a yellow tab · price pylon with LED modules ·
         cloud deck.
MOTION:  The current is LEFT: the camera drives one frame-width per stop, 16 frames, power3.inOut,
         with a horizontal-only blur peaking at 26 px mid-whip. Titles land and hold dead still.
         In-scene arrivals: words from below, binary opacity, power4.out, 4-6 frames, heavier
         words travel further (76 px vs 42 px). Slams (stamp, plate): scale 1.5-1.7 -> 1 in 5-6 frames.
         The one direction change is the last cut: a crane UP through cloud (land sinks 300 px, power4.in).
SHOTS:   see the table below.
BANNED:  dark navy void · glow, bloom, neon · floating particles · pill chips · three cards in a row ·
         a title over a dimmed screenshot · logo docked in a corner · everything fading and sliding up ·
         idle wobble on signs or titles · full-height "film scratch" lines (tried, read as glitches).
QA:      0.0 s thumbnail readable · 1.67 s whip blur · 3.5 s nothing of the new headline below the blade ·
         7.5 s tap ring on "Book This Slot" · 8.6 s meter reads 19 · 11.9 s 13 counties lit, 3 signs ·
         14.9 s prices 99/249/399 and 69/199/349 · 15.83 s cut hidden in white · 18.6 s end card complete.
```

## Shots

| Frames | Time (s) | Stop | Hero move | What the viewer reads | Sound | Hand-off |
|---|---|---|---|---|---|---|
| 0–50 | 0–1.67 | Gas pylon | Camera settles; "GAS" painted on beat 2 | FULL SERVICE · JERSEY DOESN'T PUMP GAS | Driveway bell (ding-ding), kick pattern | Whip left |
| 50–100 | 1.67–3.33 | Old billboard, black and white | Arrives with the whip, then holds | STILL WASHING YOUR OWN CAR? | Beat through a tinny radio, crackle | Squeegee |
| 100–175 | 3.33–5.83 | Same billboard, in colour | Squeegee wipes top to bottom; new line lands behind the blade; plate slapped on at beat 11 | FULL SERVICE IN YOUR DRIVEWAY · VETTED · TRAINED · INSURED | Rubber squeal, the drop | Whip left |
| 175–275 | 5.83–9.17 | The app | Two taps on real screens; meter runs 00 to 19; BOOKED stamp; a pin pops out | BOOK IT IN UNDER 20 SECONDS · 1 PICK YOUR WASH · 2 PICK A TIME · 3 TRACK IT LIVE | Taps, meter ticks, ding-ding | Pin flies, whip left |
| 275–375 | 9.17–12.5 | New Jersey | Pin lands in Passaic County; 13 counties light outward and are counted; three signs slot onto a post | 13 COUNTIES ONE APP · NORTH JERSEY · CENTRAL JERSEY (IT EXISTS) · THE SHORE | Thud, 13 rising notes, clanks | Whip left |
| 375–475 | 12.5–15.83 | Price pylon | Prices roll up; WashClub column switches on, then drops | FLAT PRICES · NO SURPRISES · 99/249/399 · 69/199/349 · WashClub $4.99/mo · cancel anytime | LED rattle | Crane up through cloud |
| 475–575 | 15.83–19.17 | End card | Logo, tagline, reviews, call to action drop in from above; hold 2.1 s | FULL SERVICE IS A JERSEY THING · 200+ FIVE-STAR GOOGLE REVIEWS · DOWNLOAD QUICKWASH | Held chord, half-time hits | — |

## Sources for every claim

| On screen | Source |
|---|---|
| Jersey doesn't pump gas | New Jersey has banned self-service fuel since 1949 and is the only state that still does (Oregon lifted its ban in 2023). Checked 2026-11-10; the state's "ban lifted" post of April 1, 2026 was an April Fools' joke. |
| Under 20 seconds | quickwashtech.com home and About: "Book … in under 20 seconds" |
| Vetted · Trained · Insured | FAQ: "Every QuickWash technician is fully vetted, trained, and insured" |
| Track it live | About: "Real-time detailer tracking" |
| 13 counties | /mobile-detailing-new-jersey lists Passaic, Bergen, Morris, Essex, Hudson, Union, Somerset, Middlesex, Monmouth, Mercer, Hunterdon, Warren, Sussex |
| Prices | /pricing ($99 / $249 / $399) and /washclub ($69 / $199 / $349, $4.99/mo, cancel anytime) |
| 200+ five-star Google reviews | /testimonials |
| County shapes | US Census geometry via the `us-atlas` package (tools/nj.json) |

## Editing

- Copy and timing live in `tools/src/*.html`; `python3 tools/gen.py` writes `index.html` and
  `compositions/*.html` (it fills in the county shapes, LED digits and the shared road).
  Edit `tools/src` and re-run, or edit `compositions/` directly and do not re-run.
- Sound: `node tools/soundtrack.js out.wav`, then encode to `assets/audio/bed.m4a`.
- Check: `npm run check`. Render: `npm run render`.
