# QuickWash "The $99 QuickWash, Orlando" (Meta lead-form ad)

Output: `../dist/quickwash-orlando-99.mp4`, 1080x1920, 30 fps, 30.30 s (909 frames), H.264 + AAC, -14.3 LUFS integrated,
true peak -1.9 dBTP. A showcase of QuickWash detailers doing the $99 QuickWash, in service order, with the package as a
checklist, the price, an Orlando call to action and the Orlando lead-form end card.

Pipeline: `tools/trim.py` (footage) -> `tools/gen-audio.sh` (ElevenLabs VO, music, Scribe) -> `tools/extend_bed.py` ->
`tools/vo_plan.py` (beat grid + VO placement -> `tools/cues.json`) -> `tools/build.py` (writes index.html + compositions) ->
`tools/mix.py` -> `npx --yes hyperframes@0.9.27 check` -> render (`--quality delivery --max-bitrate 12M`) ->
`tools/verify_cues.py <mp4> <render.words.json>`. Edit copy/layout in `tools/build.py`, not in the generated HTML.

## For the client to confirm

- **That QuickWash is booking in Orlando, FL.** Orlando is not checked against a published service-area list; the chip,
  the VO ("Orlando, this is ...", "Orlando spots ...") and the end card all say Orlando.
- **That "Orlando spots are filling up this week" is true** whenever the ad runs (on screen and in the VO).
- **The footage was shot in New Jersey / New York**, not Orlando (May suburban driveway, July city parking lot, a Jersey City
  rooftop). High-rises show in the upper part of several July-lot shots (s01, s03, s04, s07) and a Jersey City block behind
  s06; nothing pretends to be Orlando (no added palms or landmarks).
- **The end card is the client's Davenport card with only the pill repainted** ("DAVENPORT, FLORIDA" -> "ORLANDO, FLORIDA").
- Detailers' faces are visible in profile in several shots (s01, s04, s05, s09, s11): releases as for the earlier ads.

## Structure (cuts on the bed's 110 BPM beat grid; every section's line starts on its first cut)

| # | section | frames | time (s) | on screen |
|---|---|---|---|---|
| 1 | OPEN | 0-135 | 0.00-4.50 | orange pin chip "Orlando, FL" + "The $99 / QuickWash." from frame 0; "We come to you." on the van cut (f86) |
| 2 | THE SERVICE | 135-626 | 4.50-20.87 | nine shots; checklist rows land on each line's first word, previous row dims to 0.78 |
| 3 | RESULT + PRICE | 626-724 | 20.87-24.13 | all six rows back to full on "All"; "$99" (orange, 250 px) on "Ninety-nine" + "Standard-size vehicle" |
| 4 | ORLANDO CTA | 724-789 | 24.13-26.30 | "Orlando spots are / filling up this week." |
| 5 | END CARD | 789-909 | 26.30-30.30 | Orlando lead-form card wipes up on "Drop" (12 f, power3.inOut), then holds 3.6 s |

Text stays inside y 168-1330 and x <= 930 (checklist block y 890-1300, widest row "Vacuum: seats, floors, trunk" ends x ~ 830).
White Poppins with soft shadow over gentle gradient scrims (top scrim on open/price/CTA, bottom scrim on service/price); no
slabs. No scale or push on any footage; the only scale tweens act on the "$99" and the check badges.

## Script (Liam TX3LPaxmHKxFdv7VOQHJ, eleven_v3, stability 0.5)

| line | as sent | take | why |
|---|---|---|---|
| b1 open | `[cheerful] Orlando, this is the ninety-nine dollar QuickWash. And yeah, we come to you.` | open_t2 | 11.9 st pitch spread; 0.64 s shorter than t1 (13.4 st), which kept the film near 30 s |
| b2-b7 list (one take) | `Foam and a full hand wash. Vacuum: seats, floors, trunk. Glass, inside and out. Tire shine and door jambs. Interior wiped down. And a ceramic spray wax to finish.` | list_t2 | 9.5 st vs 8.0 st |
| b8 price | `[excited] All of it, in your driveway. Ninety-nine bucks.` | price_t1 | 13.7 st, quicker into "Ninety-nine" |
| b9 CTA | `Orlando spots are filling up this week. Drop your info below and grab yours.` | cta_t1 | 12.5 st vs 8.6 st, tighter |

Two takes per line (8 TTS requests). The list was one continuous take; each line is placed on its section's first cut and the
silence between lines is lengthened (the b-roll plays there). Pauses shortened inside silence: "Vacuum:" -> "seats" to 0.30 s,
"Glass," -> "inside" to 0.12 s. Nothing is time-stretched. Scribe hears "Interior wipe down" (the script says "wiped").

## Cue table (Scribe word start on the rendered MP4's audio vs the picture event; hard cuts detected in the MP4)

| word | spoken (Scribe on render) | picture | event | diff (f) |
|---|---|---|---|---|
| Orlando | f4.8 | f0 | chip + "The $99 QuickWash." already on frame 0 (thumbnail) | by design |
| And (yeah, we come to you) | f87.0 | f86 | cut s02 (van) + "We come to you." | -1.0 |
| Foam | f135.6 | f135 | cut s03 + row 1 "Foam + hand wash" | -0.6 |
| Vacuum | f283.2 | f282 | cut s06 + row 2 "Vacuum: seats, floors, trunk" | -1.2 |
| Glass | f365.4 | f364 | cut s07 + row 3 "Glass, in + out" | -1.4 |
| Tire | f414.6 | f413 | cut s08 + row 4 "Tire shine + door jambs" | -1.6 |
| Interior | f511.8 | f511 | cut s10 + row 5 "Interior wiped down" | -0.8 |
| And (a ceramic spray wax) | f561.0 | f560 | cut s11 + row 6 "Ceramic spray wax" | -1.0 |
| All | f627.0 | f626 | cut s12, rows to full opacity | -1.0 |
| Ninety-nine | f676.8 | f675 | cut s13 + "$99" | -1.8 |
| Orlando (spots) | f725.4 | f724 | cut s14 + CTA line | -1.4 |
| Drop | f789.0 | f789 | end-card wipe starts | 0.0 |

All 13 hard cuts (f86 ... f724) were found in the MP4 on their planned frames (0 f off); the wipe registers at f795-796.

## Shots (selects used in the cut)

Proxies: scratchpad `hp/proxy` (May = suburban driveway, black Nissan, navy QuickWash hoodie; July = city lot, black Volvo,
navy polo, QuickWash van) and `dirty/proxy` (Jersey City rooftop, grey Durango, purple QuickWash hoodie). All HLG HDR
originals were already tone-mapped to SDR in the proxies (zscale + hable, as reel-hp); one grade for all (eq contrast 1.05,
saturation 1.08). Window = seconds in the proxy file.

| shot | frames | source | window | shoot | detailer doing | in an earlier ad? |
|---|---|---|---|---|---|---|
| s01 | 0-86 | IMG_6406 | 7.90-10.77 | July lot | mitt-washing the foamed grille, QuickWash van behind (plate 485 7752 tracked + blurred) | no |
| s02 | 86-135 | IMG_0012_1_18 | 2.90-4.53 | May driveway | walks to the open van and reaches into the kit, hoodie logo, house + picket fence | no |
| s03 | 135-184 | IMG_6394 | 0.60-2.23 | July lot | foam/spray on the hood and windshield | no |
| s04 | 184-233 | IMG_6405 | 2.00-3.63 | July lot | mitt along the foamed door and roof, wide | no |
| s05 | 233-282 | IMG_0012_1_22 | 1.50-3.13 | May driveway | green mitt on the lower door, wash buckets, open van behind | no |
| s06 | 282-364 | IMG_2032 | 0.00-2.73 | rooftop | in the open driver door working the interior (hoodie logo) - the vacuum section's stand-in | no |
| s07 | 364-413 | IMG_6408 | 4.30-5.93 | July lot | mitt on the door and side window (static blur over a bucket's partial print) | no |
| s08 | 413-462 | IMG_6382 | 1.50-3.13 | July lot | brush scrubbing the foamed wheel and tyre | no |
| s09 | 462-511 | IMG_6402 | 10.60-12.23 | July lot | rinses the rear, opens the rear door and works the jamb | no |
| s10 | 511-560 | IMG_2034 | 35.50-37.13 | rooftop | gloved hand wiping the centre console (close POV) | yes (reel-race r5, same window) |
| s11 | 560-626 | IMG_6392 | 0.00-2.20 | July lot | yellow spray bottle misted along the side (spray wax) | no |
| s12 | 626-675 | IMG_6438 | 1.60-3.23 | July lot | result: tracking along the clean, dry side; van behind | yes (reel-hp/glendale s09) |
| s13 | 675-724 | IMG_6432 | 2.00-3.63 | July lot | result: slow arc on the clean front | yes (reel-hp v1) |
| s14 | 724-801 | IMG_6400 | 2.00-4.57 | July lot | rinsing the roof, wide, steady; runs 0.4 s under the wipe | no |

14 different source clips; 10 never used in an earlier ad. No plate readable: 485 7752 (s01) is covered by a tracked box blur
(`tools/trim.py`, SSD template tracker from an anchor box, checked at 0.1/1.5/2.85 s); H45-VLA and P81-RZT are not in any chosen
window; s03 shows at most a two-digit fragment at the frame edge. No legible third-party brand except the car badges (Volvo, "S60").

Coverage gaps (as the shot logs say): there is no vacuum-in-action and no glass-cleaner/towel footage in the library. Vacuum is
shown by the detailer working inside the open door (s06); glass by the mitt on the side window (s07).

### Good shots left out
- IMG_0012_1_17 foam-cannon POV (strongest foam shot, but used twice before); IMG_0012_1_14 wide street foam (used in reel-race).
- IMG_6397 / IMG_6399 detailer rinsing with the van behind (plate 485 7752 readable, used before).
- IMG_6410 trunk hand wash (plate readable throughout); IMG_0012_1_19/1_20 hatch hand wash with hoodie logo (X39-RVK readable).
- IMG_6381 wheel and door rinse, IMG_6384/6385 crouched wheel scrub (faces frontal), IMG_0012_1_10 wheel brush (face, Nissan cap).
- IMG_6391 spray wax at the front (plate partly visible), IMG_2045 / IMG_2043 / IMG_3725 / IMG_3731 rooftop wides (NYC skyline).
- IMG_2033 hoodie-logo door shot (too close to s06), IMG_2048 clean wet side (Manhattan skyline across the top), IMG_6409 side + van (high-rises).
- IMG_0012_1_16 detailer foaming by the house (camera whips 2.4-3.0 s; plate X39-RVK readable when the car is in frame).
- IMG_2035 POV interior brush/air (too shaky), IMG_2034 seat wipe (water-bottle label legible).

## Audio (`tools/mix.py`)
- Bed: ElevenLabs sound-generation, one generation (no retry), 22 s, prompt_influence 0.6: "Warm sunny upbeat acoustic pop
  instrumental, 110 BPM, strummed acoustic guitar, light hand claps, bright ukulele and soft shaker, feel-good Saturday morning
  in the sun, steady groove throughout, clean modern commercial bed, no vocals". Measured 110.0 BPM, beat 0 at 0.130 s.
  Extended to 30.68 s by repeating 16 beats (8.72 s) at a matched point (`tools/extend_bed.py`, envelope r 0.91).
  (Generated for the superseded "Saturday" concept and kept, as the brief allowed.)
- VO high-pass + compressor; bed x0.5 side-chain ducked by the VO; loudnorm -14 / TP -2; 4x oversampled limiter.
  Clip sound kept low on s03 (0.12), s09 (0.10), s14 (0.12). Render: -14.3 LUFS, true peak -1.9 dBTP.

## End card
`assets/app/endcard-orlando.jpg` = `../reel-davenport/assets/app/endcard-davenport.jpg` with only the pill repainted
(`tools/endcard_pill.py tools/fonts/Montserrat-ExtraBold.ttf "ORLANDO, FLORIDA" <in> <out>`): old pill erased by per-column
interpolation of the surrounding blue, new pill 7 px cyan outline (#02E6FD, sampled from the Davenport card), 80 px tall,
65 px text padding as on the original, white Montserrat ExtraBold caps at the original cap height, centred on x 540.
Checked at full size: no patch edge.

## Claims and sources
| claim | source |
|---|---|
| $99, standard-size vehicle | quickwashtech.com/pricing, QuickWash package (as listed in reel-hp/SPEC.md) |
| Foam + hand wash · Vacuum: seats, floors, trunk · Glass, in + out · Tire shine + door jambs · Interior wiped down · Ceramic spray wax | quickwashtech.com/pricing package list: Precision Hand Wash & Foam Pre-Soak; Light Interior Vacuum (Seats, Floors, Trunk); Window & Glass Cleaning (In & Out); Tire Shine & Door Jamb Detail; Interior Wipe-Down (Dashboard, Console, Doors); Ceramic-Infused Spray Wax (on screen "Ceramic spray wax") |
| We come to you / in your driveway | site: mobile service |
| Orlando, FL / ORLANDO, FLORIDA | **client to confirm** |
| Orlando spots are filling up this week | **client's urgency claim; must be true when the ad runs** |

## Check
`npx hyperframes check`: 0 errors. Warnings kept: nested_media_start_basis_ambiguous x10 (video starts are composition-local
on purpose); a contrast flag on "We come to you." at 1.68 s, when that line is still at opacity 0 (it appears at 2.87 s over
the scrim).
