# QuickWash "The race": everything in a $99 QuickWash, faster than it takes to book it

Main cut (v4, Liam): 1080x1920, 30 fps, 27.567 s (827 frames), `../dist/quickwash-race.mp4`. The v3 close-up race is kept as
`../dist/quickwash-race-alt-closeups.mp4`.
Superseded renders: `../dist/quickwash-race-alt-laura.mp4` (v2, Laura, no b4 line) and `../dist/quickwash-race-alt-liam.mp4`
(v1, Liam, before the shot changes and the WashClub beat).
v3 pipeline: `tools/cues_v3.py` (Liam's placed VO from tools/cues-liam.json + the mid-line cuts + the WashClub insert)
-> `tools/apply_cues.py` -> `tools/mix.py` -> check -> render. `tools/verify_cues.py <mp4>` checks the result.

## v4 (client feedback): wider shots, fewer and longer, no zoom feel

The client asked for wide shots of the detailing even where they don't match the words, and no quick zoom cuts. The race is now
five wide or medium shots on a steady camera. Each cut lands on the first word of an item (verified in the MP4); there are no
mid-phrase splits. Nothing scales the footage: the payoff's 1.00->1.04 push on the hero car is removed. The remaining scale
tweens act on text only. The bottom scrim is stronger (0.5 at 45%, 0.62 at the bottom) for the brighter wide frames.

| items covered | frames | clip (source window) | on screen |
|---|---|---|---|
| Foam + hand wash | 143-202 (1.97 s) | r1w-foam-street: IMG_0012_1_14 4.5 s +2.1 | wide street: detailer in the QuickWash hoodie foam-cannons the SUV |
| Vacuum | 202-298 (3.20 s) | r2w-interior: IMG_6439 0.1 s +3.35 | driver door open, slow move over the clean interior |
| Glass | 298-359 (2.03 s) | r3w-durango-rinse: IMG_2046 0.8 s +2.25 (fixed blur on the static front plate) | wide rooftop: detailer (QuickWash hoodie) rinsing the windshield and roof |
| Tire shine + jambs, Interior | 359-480 (4.03 s) | r4w-wheel-scrub: IMG_6383 8.4 s +4.2 | medium: detailer crouched scrubbing the foamed wheel and tyre, face away |
| Ceramic spray wax | 480-533 (1.77 s) | s08-spray-hood (reel-hp, plate blurred) | detailer spraying wax on the hood |

Rejected:
- IMG_6397 / 6407 / 6408 / 6399 (wide Volvo wash): the 485 7752 plate is in frame on a moving camera and would need a new
  tracked blur. 6406 and 6399 also show faces.
- IMG_0012_1_13 / 1_12 (s02 / s10): the plate is tracked only for short windows. 1_15 (s11): a walking, handheld follow.
- 1_18: whip and lunge. 1_16: the subject is small with a walk-on.
- IMG_2041 and IMG_2040 POV: close and handheld.
- The v3 macro shots: the client asked for wide shots.
The wax shot stays 1.77 s: the only spray-wax footage (IMG_6393) is 2.27 s long.

## v3 (client feedback): every phrase over its own action, plus the WashClub beat (superseded race shots; WashClub kept)

| spoken (Liam) | frames | clip / source window | what is visible |
|---|---|---|---|
| "Foam ..." | 143-166 | r1-foam-cannon: IMG_0012_1_17 1.0 s +1.0 | a foam cannon blasting snow foam onto the dark SUV's side |
| "... and a hand wash" | 166-202 (cut on "hand") | s03-mitt-bumper (reel-hp) | the detailer mitt-washing the foamed rear bumper |
| "Vacuum: seats, floors, trunk" | 202-298 | s04-vacuum-long: IMG_2059 at 0.91x | fresh vacuum lines in the 2nd-row carpet (the only vacuum footage) |
| "Glass, inside and out" | 298-359 | r3-glass-mitt: IMG_2041 15.0 +2.25 | gloved hand and mitt washing the foamed windshield, close POV |
| "Tire shine ..." | 359-391 | r4-tire-spray: IMG_2040 4.6 +1.3 | spray bottle working the wheel and tyre |
| "... and door jambs" | 391-427 (cut on "door") | r4-door-jamb: IMG_2040 61.9 +1.4 | door open, gloved hand and wand rinsing the jamb and sill |
| "Interior wiped down" | 427-480 | r5-console-wipe: IMG_2034 35.5 +1.95 | gloved hand wiping the centre console by the shifter |
| "Ceramic spray wax" | 480-533 | s08-spray-hood (reel-hp, plate blurred) | spray wax misting onto the hood |

Re-cut windows use reel-hp's grade (eq contrast 1.05, saturation 1.08); there are no plates, faces or legible labels.
The tyre shot shows the wheel's centre-cap emblem. The checklist rows are unchanged; a row still lands on the first word of its item.

WashClub beat (`compositions/washclub.html`): frames 602-680 (2.6 s), light grid background, after the payoff.
- "$99" carries over from the payoff (same place and size), is struck (6 frames, 0.15 s in), then steps up, shrinks and dims.
- "$69" pops in with back.out at the "Sixty" cue (planned 0.75 s in), with "with WashClub" beside it.
- The client's WashClub badge (880 px wide) follows 4 frames later, then "WashClub membership $4.99/mo".
- Sources: quickwashtech.com/washclub: QuickWash $99, member $69, membership $4.99/mo. The client confirmed 5% Quickbucks back.
- Badge: `assets/app/washclub-badge-5.png` is the client's PNG (real alpha) with the two "8"s changed to "5" (`tools/fix_badge.py`,
  Poppins Bold, the closest weight, with the same thin navy edge; painted with the local navy, no visible patch). Only the
  corrected crop `assets/app/washclub-badge-5-crop.png` is used.
- Sound: soft whooshes on the cut and the strike, the success chime on "$69"; the music runs through.

Timing: the timer still runs from "Go" f126 to "Done" f561 (14.5 s, reads 0:14). The WashClub beat shifts the booking beat
(f680), the end card (f737; 3.0 s) and Liam's b4/b5 lines by 2.6 s.
Measured: all 13 hard cuts in the MP4 fall on their cue frames. Voice onsets on a VO stem rebuilt as the mix places it are 0-1
frames from their cues. Two exceptions:
- "Ninety-nine" cuts 4 frames after the acoustic onset of the "N", 1 frame before Scribe's word start.
- "hand" has no pause before it, so it is cut on Scribe's word start.
Scribe on Liam's v1 render put every cue word 0-2 frames after its visual; the placement is unchanged, and b4/b5 are shifted
whole. Mix: -13.8 LUFS, true peak -1.6 dBFS (limiter now 4x oversampled).

### Pickup lines (ElevenLabs credits were 0)
Reserved: b3b "And if you join WashClub? Sixty-nine." (Liam), first word 0.2 s into the WashClub beat; its "Sixty" becomes
the $69 cue. When credits return:

    cd reel-race
    VOICE=liam tools/gen-audio.sh pickup 3            # assets/audio/vo/b3b_t1..3
    tools/stt_words.sh assets/audio/vo/b3b_t1 assets/audio/vo/b3b_t2 assets/audio/vo/b3b_t3
    python3 -I tools/vo_analyze.py assets/audio/vo/b3b_t1 assets/audio/vo/b3b_t2 assets/audio/vo/b3b_t3   # pick the liveliest
    B3B=b3b_t2 python3 -I tools/cues_v3.py             # places the line, sets "Sixty" from its word onset
    python3 -I tools/apply_cues.py && python3 -I tools/mix.py
    npx --yes hyperframes@0.9.27 check && npx --yes hyperframes@0.9.27 render -o ../dist/quickwash-race.mp4 --quality delivery --max-bitrate 12M

`cues_v3.py` refuses a line that runs past the booking cut. For Laura's missing b4, run `VOICE=laura tools/gen-audio.sh pickup 3`
(it also generates her b3b).

## v2: Laura (main cut)

Voice: Laura FGY2WhTYpPnrIDTdsKH5, eleven_v3, stability 0.5 (`VOICE=laura tools/gen-audio.sh vo 4`, `assets/audio/vo-laura`).
The lines are the same as Liam's, with speed-run tags and "!":
- b1 `[excited] ... book one! Ready? Go!`
- b2 `[speaking fast] Foam and a hand wash! ... Ceramic spray wax!`
- b3 `[excited] Ninety-nine bucks. Done, with time to spare!`
- b5 `[playful] QuickWash. Grab the app!`

Takes, picked by pitch spread and pace:
- b1_t2: 11.3 st, the tightest "Ready? Go!"
- b2_t3: 15.1 st, the liveliest of four; she reads the list in 10.0 s, Liam took 12.9 s.
- b3_t1: the only b3 take.
- b5_t4: the only b5 take.

The ElevenLabs credit quota ran out partway through the batch. Only b1 t1-t4, b2 t1-t4, b3_t1 and b5_t4 were generated, and
**b4 ("Booking it? Twenty seconds.") could not be generated, so the booking beat has no voice in this cut.** Its picture keeps
the Liam rhythm: the tap 0.3 s in, "Booked ✓" + "20 seconds." 1.07 s in, a 1.9 s beat. Scribe was blocked by the same quota.
Phrase onsets therefore come from the audio (`tools/vo_plan_laura.py`): a speech segment is where the 10 ms envelope is above
-38 dB, and eleven_v3's alignment picks the segment each phrase starts in. Every cue word starts a phrase.

Pauses:
- b2: gaps between items are evened to at least 0.35 s, because she ran two items together at 0.15 s. This adds silence only.
- Hook: gaps are capped at 0.3 s.
- "Go" -> "Foam" and "wax" -> "Ninety-nine": 0.55 s.
- No time-stretch.

The timer stops at 13.20 s and reads 0:13. The hook foam is re-cut longer (IMG_0012 6.8 s +5.7 s) for the 5.6 s hook.
"With time to spare." is now white Poppins 700 64 px with the soft shadow, on a slightly stronger top scrim.

| cue | voice onset / visual (frames) | event |
|---|---|---|
| Go | 142 / 142 | timer starts |
| Foam / Vacuum / Glass / Tire / Interior / Ceramic | 168, 212, 290, 341, 401, 448 / same | race cuts + rows |
| Ninety-nine | 500 / 500 | payoff cut + $99 |
| Done | 538 / 538 | timer stops at 0:13, ding |
| (Booking) | no VO / 596 | tap on Book This Slot |
| (Twenty) | no VO / 619 | Booked ✓ + "20 seconds." |
| QuickWash | 653 / 653 | logo |
| Grab | 679 / 679 | badges |

Beat cuts: race f168, payoff f500, book f587, end f644, end f735 (end card 3.03 s).
Voice onsets are measured on a VO stem rebuilt exactly as the mix places it (`tools/verify_cues.py`). The cut frames were
detected in the rendered MP4 itself. Every cue is 0 frames off by this acoustic measure. With Liam, Scribe's word starts ran
0-2 frames later than the acoustic onset, and Scribe could not be run on this render.
Mix: -14.1 LUFS, true peak -2.1 dBFS. There are 13 ticks, one per timer second.

## v1: Liam (alternate cut). The sections below describe it.

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
