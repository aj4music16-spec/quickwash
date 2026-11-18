# QuickWash "The race": everything in a $99 QuickWash, faster than it takes to book it

1080x1920, 30 fps, 24.967 s (749 frames). Output `../dist/quickwash-race.mp4`.
Render: `npx --yes hyperframes@0.9.27 render -o ../dist/quickwash-race.mp4 --quality delivery --max-bitrate 12M`
(env `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1`).
Pipeline: `tools/gen-audio.sh` (takes, bed, sfx) -> `tools/stt_words.sh` (Scribe word onsets) -> `tools/vo_plan.py`
(places the VO, writes `tools/cues.json`) -> `tools/apply_cues.py` (writes the frame-snapped cue times into index.html and
compositions) -> `tools/mix.py` -> check -> render. Footage: `tools/trim.sh`.

## Concept
A race against the booking timer. Booking in the app takes 20 seconds, so a timer pill runs in real time from the word
"Go" while a quick, playful VO lists the six things in a $99 QuickWash over real shots. Each item is checked off, and the
clock stops on "Done" at 0:14, under the 0:20 mark.

## Beats (film seconds / frames)

| beat | time | picture | on screen |
|---|---|---|---|
| 1 HOOK | 0-4.767 (f0-143) | foam sheeting down the side (IMG_0012 7.4-12.5, reel-hp grade) | timer pill 0:00 / 0:20; "Everything in / a QuickWash." + "[Faster] than it takes / to book it." on frame 0; pill and line kick on "Go" |
| 2 RACE | 4.767-17.767 (f143-533) | s03 mitt + foam · s04 vacuum lines (0.91x) · s05 windshield · s06 wheel rinse (longer cut, own sound at 0.12) · s07 door-panel wipe · s08 spray wax; each cut on its item's first word | checklist rows (reel-hp v9 style: 48 px orange check + white Poppins 600 50 px, older rows 0.78, fixed rows y 890-1300 on a bottom scrim); timer running |
| 3 PAYOFF | 17.767-20.067 (f533-602) | s09 finished car, push 1.00->1.04 | "$99" (orange, 230 px) on "Ninety-nine"; timer stops on "Done" at 0:14, turns orange and pulses; "Done. / With time to spare."; all six rows at full opacity |
| 4 BOOK | 20.067-21.967 (f602-659) | light tech grid, the reel-apptech CSS phone with screen-booktime | "Booking it?"; tap ripple on Book This Slot on "Booking"; "Booked ✓" + "20 seconds." on "Twenty" |
| 5 END | 21.967-24.967 (f659-749, 3.0 s) | reel-apptech end card | logo on "QuickWash"; "The car wash that comes to you."; DOWNLOAD QUICKWASH; App Store + Google Play badges on "Grab" |

Text on footage stays in y 168-1330 and x <= 930. The longest checklist row, "Vacuum: seats, floors, trunk", ends at x ≈ 920.

## Script (eleven_v3, Liam TX3LPaxmHKxFdv7VOQHJ, stability 0.5)

| beat | line as sent | take | why |
|---|---|---|---|
| b1 | `[playful] Everything you get in a QuickWash, faster than it takes to book one. Ready? [excited] Go.` | b1_t1 | 17.5 st pitch spread, quickest "Go" (t3 swings more, 21.5 st, but runs 0.2 s longer) |
| b2 | `Foam and a hand wash. Vacuum: seats, floors, trunk. Glass, inside and out. Tire shine and door jambs. Interior wiped down. Ceramic spray wax.` | b2_t1 | 10.5 st, the liveliest whole take; one continuous performance paced better than the separately generated items (i1-i6; the glass items were flat, 3-4 st) |
| b3 | `[excited] Ninety-nine bucks. Done, with time to spare.` | b3_t1 | 14.2 st, shortest to "Done" |
| b4 | `Booking it? Twenty seconds.` | b4_t1 | 15.2 st; says "Booking" (t2 says "Bookin'") |
| b5 | `[warmly] QuickWash. Grab the app.` | b5_t2 | 21.4 st |

Tightening: pauses between items are capped at 0.55 s (0.5 s after "Vacuum:"), "one." -> "Ready?" at 0.15 s, "Ready?" -> "Go"
at 0.3 s and "bucks." -> "Done" at 0.45 s. The cuts fall in the silences, with 15/30 ms fades. Nothing is time-stretched.
Word onsets come from ElevenLabs Scribe. Each phrase-first word is refined to the acoustic onset (where the 10 ms envelope
crosses -40 dB), because Scribe puts some onsets late: the nasal "N" of "Ninety-nine" starts 0.17 s before Scribe's estimate.
Cue frames are no earlier than 1 frame before Scribe's estimate.

## Cue table (word onset measured by Scribe on the rendered MP4 -> visual event frame)

| word | spoken | visual | event |
|---|---|---|---|
| Go | f128 (4.26) | f126 | timer starts (real time from here) + pill kick |
| Foam | f144 | f143 | cut to shot 1 + row 1 |
| Vacuum | f203 | f202 | shot 2 + row 2 |
| Glass | f299 | f298 | shot 3 + row 3 |
| Tire | f361 | f359 | shot 4 + row 4 |
| Interior | f428 | f427 | shot 5 + row 5 |
| Ceramic | f481 | f480 | shot 6 + row 6 |
| Ninety-nine | f534 | f533 | payoff cut + "$99" |
| Done | f562 | f561 | timer stops (f561 - f126 = 435 frames = 14.50 s -> reads 0:14), ding, "Done." |
| Booking | f611 | f611 | tap on Book This Slot |
| Twenty | f636 | f634 | "Booked ✓" + "20 seconds." |
| QuickWash | f670 | f668 | logo |
| Grab | f698 | f697 | store badges |

All visual events are 0 to 2 frames ahead of Scribe's word start, and 0 to 1 frame from the acoustic onset.

## Timer
`compositions/timer.html`: the value is film time minus the "Go" frame, floored to whole seconds, shown as m:ss. The bar
scaleX is value / 20. It freezes at "Done" (14.50 s, shown as 0:14). A soft tick sounds on every whole second (14 ticks),
then a ding on "Done".

## Claims and sources
- The six inclusions and $99: quickwashtech.com/pricing, QuickWash package, as listed in reel-hp/SPEC.md: Precision Hand Wash
  & Foam Pre-Soak; Light Interior Vacuum (Seats, Floors, Trunk); Window & Glass Cleaning (In & Out); Tire Shine & Door
  Jamb Detail; Interior Wipe-Down (Dashboard, Console, Doors); Ceramic-Infused Spray Wax. On screen and in the VO this is
  "Ceramic spray wax" (the site says "ceramic-infused").
- "Booking it? 20 seconds." / the 0:20 mark: homepage, "under 20 seconds".
- The 0:14 on the timer is the length of this VO list, not a claim about service time; the VO frames it as a race against booking.

## Footage (tools/trim.sh)
reel-hp clips copied as-is (trimmed, graded, plates blurred): s03-mitt-bumper, s05-windshield-rinse (tracked plate blur),
s07-door-wipe, s08-spray-hood (tracked plate blur), s09-hero-side. Re-cut longer from the same proxies with reel-hp's grade:
s01-foam-long (IMG_0012 7.4-12.5), s06-wheel-long (IMG_6386 4.4-7.0), s04-vacuum-long (IMG_2059 whole clip at 0.91x, 3.3 s,
the only vacuum shot). These windows show no plate; H45-VLA and P81-RZT are not readable anywhere.

## Audio (tools/mix.py)
- Bed: ElevenLabs sound-generation, 26 s, prompt_influence 0.6, "Driving playful upbeat electronic pop instrumental, 128 BPM,
  punchy kick and claps, bright synth stabs, fast energetic speed-run feel, clean modern commercial music, steady energy
  throughout, no vocals". Three candidates; bed2 is the steadiest (short-term sd 1.7 LU), ~128 BPM. It is lengthened by two
  repeated bars (tools/extend_bed.py) so its own fade-out falls after the film.
- SFX (sound-generation): tick (x14, every second of the race), ding (Done), tap (Booking), success (Twenty), whooshes into
  payoff, book and end.
- Footage sound: the hook foam and the wheel rinse at 0.12, as in reel-hp.
- Chain: VO high-pass + compressor, music x0.45 side-chain ducked by the VO, loudnorm -14 LUFS / TP -2, limiter 0.7, AAC 192k.
  Measured on the render: -14.0 LUFS integrated, true peak -1.3 dBFS.
