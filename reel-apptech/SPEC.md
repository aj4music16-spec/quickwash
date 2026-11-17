# QuickWash app product film ("Your car wash is now an app") - v2

1080x1920, 30 fps, 24.5 s (735 frames). Main: `../dist/quickwash-app-product.mp4` (Liam). Alternate:
`../dist/quickwash-app-product-alt-jessica.mp4` (same picture; `index.html` audio swapped to `assets/audio/mix-jessica.m4a`
for that render). Render: `npx --yes hyperframes@0.9.27 render -o ../dist/<file>.mp4 --quality delivery --max-bitrate 12M`
(env `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1`).

v2: the voice is ElevenLabs eleven_v3 and the picture is retimed to the spoken words (tools/cues.json).

Look: product-keynote "tech". Light ground `#f4f6fb` with a 60 px navy grid at 5% and faint navy/orange glows; navy `#000099`
type, orange `#FF6600` accents; Poppins 600-700 for headlines/callouts, Inter for UI labels; thin navy leader lines with a
white halo; expo/back eases; soft ring tap ripples (no cursor). No CSS filters on footage.

## Script (eleven_v3, stability 0.5)

| beat | line (as sent) | main take (Liam TX3LPaxmHKxFdv7VOQHJ) | alt take (Jessica cgSgspJ2msm6clMCkdW9) |
|---|---|---|---|
| b1 hook | `[excited] Okay, your car wash? It's an app now.` | liam_b1_t2 | jessica_b1_t2 |
| b2 book | `Pick your car. Pick your wash. Pick a time. And... booked. About twenty seconds.` | liam_b2_t2 | jessica_b2_t1 |
| b3 garage | `Every car you own? Right here. Put 'em on repeat if you want.` | liam_b3_t1 | jessica_b3_t1 |
| b4 van | `Then we pull up to you.` | liam_b4_t3 | jessica_b4_t2 |
| b5 anywhere | `Home. The office. The gym. Even the golf course. Wherever you're parked.` | liam_b5_t2 | jessica_b5_t2 |
| b6 end | `[warmly] QuickWash. Go grab the app.` | liam_b6_t2 | jessica_b6_t2 |

Takes: 3 per beat for Liam and 2 for Jessica (`tools/gen-vo-v3.sh`). They were picked by F0 movement (`tools/vo_analyze.py`:
10-90% pitch spread in semitones, autocorrelation F0), then for natural pauses and length: b1 t2 17.2 st (the biggest swing,
a real pause before "It's an app now"); b2 t2 11.5 st, the tighter of the two lively takes (t3 is 8.6 s long); b3 t1 13.1 st
(t3 has more swing but says "Put them"); b4 t3 (sd 5.4 st, the least clipped); b5 t2 14.7 st; b6 t2 12.4 st. Nobody listened.
Word onsets come from ElevenLabs Scribe (`tools/stt_words.sh`), because eleven_v3's own with-timestamps alignment was up to
0.4 s off on these takes. `tools/vo_plan.py` places the takes: pauses longer than 0.35 s between phrases in b2 and 0.5 s in b5
are shortened in the silence, with no time-stretch. Jessica is split at her full stops and each phrase is placed on Liam's cue word.

## Cue sheet (main cut; film seconds / frames; "spoken" = Scribe on the rendered MP4)

| word | spoken | visual | event |
|---|---|---|---|
| It's | 1.92 f58 | 1.91 f57 | home screen wakes on the corner-pinned phone ("app" 2.17: underline) |
| Pick (1) | 3.14 f94 | 3.15 f94 | STEP 1 "Pick your car" callout + leader line |
| car | 3.52 f106 | 3.51 f105 | tap on Ringo's card (press frame) + card glow; tap sound |
| pick (2) | 4.20 f126 | 4.18 f125 | STEP 2 "Pick your wash" |
| wash | 4.56 f137 | 4.56 f137 | tap on the $99.00 QuickWash row + row highlight; sheet opens 4.86 |
| pick (3) | 5.28 f158 | 5.27 f158 | STEP 3 "Pick a time" |
| time | 5.56 f167 | 5.53 f166 | tap on 01:00 PM + orange ring |
| and | 6.26 f188 | 6.20 f186 | Book This Slot glows through the held "and..." |
| booked | 7.58 f227 | 7.58 f227 | tap on Book This Slot + "Booked ✓" chip; success sound |
| twenty | 8.60 f258 | 8.59 f258 | stopwatch reads 0:20 (counting since 3.15) + "Booked in 20 seconds." |
| (cut) | | 9.30 f279 | phone pushes in; My Garage is fully up at 9.80 |
| Every | 9.90 f297 | 9.90 f297 | "Every car. / One garage." |
| Right | 11.10 f333 | 11.10 f333 | Book Wash / History / Set Recurring chips (0.1 s stagger) |
| repeat | 12.40 f372 | 12.38 f371 | Set Recurring turns orange, ring on the button in the app |
| (cut) | | 13.40 f402 | c03 van (illustration push-in -> real van at 14.37) |
| Then | 13.66 f410 | 13.65 f410 | "Then we pull / up to you." (line 2 at 13.85) |
| (cut) | | 14.90 f447 | "We pull up at" + route rail |
| Home | 15.18 f455 | 15.15 f454 | Home card cuts in |
| office | 16.26 f488 | 16.23 f487 | Office card |
| gym | 17.42 f523 | 17.39 f522 | Gym card |
| golf | 18.64 f559 | 18.63 f559 | The club card |
| wherever | 19.84 f595 | 19.83 f595 | "Wherever / you're parked." (line 2 on "you're" 20.23) |
| (cut) | | 21.00 f630 | end card |
| Quick(Wash) | 21.32 f640 | 21.30 f639 | logo pops |
| Go | 22.26 f668 | 22.24 f667 | "DOWNLOAD QUICKWASH" (22.0) + store badges |

Beat cuts: 0 / 2.8 / 9.3 / 13.4 / 14.9 / 21.0 / end 24.5 (end card 3.5 s). Each VO line ends at least 0.1 s before its
beat's cut, and every line starts at least 0.25 s after the previous one ends.

## Beats (picture)

| # | film s | composition | picture |
|---|---|---|---|
| 1 HOOK | 0.0-2.8 | `hook.html` | c14 0-2.4 at 6/7 speed, at 88% from the bottom edge; clean home screen corner-pinned per frame (`tools/track_phone.py` -> `tools/pin_matrices.py`) from "It's" |
| 2 BOOK | 2.8-9.3 | `app.html` 0-6.5 | CSS phone (real screenshots at 0.4545) lands from the hook phone; the taps/callouts above |
| 3 GARAGE | 9.3-13.4 | `app.html` 6.5-10.6 | phone pushes to 1.35x, My Garage slides in; chips on leader lines under Ringo's buttons |
| 4 DISPATCH | 13.4-14.9 | `dispatch.html` | c03 1.0-2.55 at 1.6x (push-in, start of the morph), cut to c03 3.8-4.33 (real van, wide). The big phone-number pass (2.6-3.4) is skipped. Both are cropped to the top-left 90%, so the sparkle watermark is out of frame |
| 5 ANYWHERE | 14.9-21.0 | `anywhere.html` | four whole 3:2 cards (c06 Home, c09 Office, c08 Gym, c01 "The club"), hard cut on each word + route rail |
| 6 END | 21.0-24.5 | `end.html` | logo, "The car wash that / comes to you.", "DOWNLOAD QUICKWASH", App Store + Google Play badges |

Text over full-frame footage stays in y 168-1330, x <= 930. All end-card content is above y 1100.

## Claims and sources

- "Booked in 20 seconds" / the 0:00 -> 0:20 stopwatch: client site quickwashtech.com ("under 20 seconds").
- App flow, prices ($99.00 QuickWash, $249.00 Detail, $399.00 Full Detail), garage actions, time slots: the client's own app
  screenshots (unchanged except the privacy patch below).
- App Store / Google Play availability: the client's store badges (from reel-app).
- "The car wash that comes to you" / "we come to you": the client's mobile service model (site).

## Privacy

`assets/app/screen-home.png` (client original, git-ignored) shows a real name and street address. `tools/clean_home.py`
writes `assets/app/screen-home-clean.png`: each line's ink box is painted with the exact flat background (#FF6600 /
#FFFFFF), and the replacement is set in Inter fitted to the original line (greeting: Inter Regular 42.6 px white
"Hi Alex!"; address: Inter SemiBold 41 px #12181B "123 Main St, Your City") at the same left edge and top. Verified: the
painted tails are exact background (max channel deviation 0). Only the clean file is referenced.

## Footage (tools/trim.sh)

Client AI clips, 24 fps silent -> 30 fps H.264 yuv420p CRF 16, no audio: hook-phone (c14 0-2.4 at 6/7 speed), van-morph
(c03 1.0-2.55 at 1.6x), van-road (c03 3.8 +0.8), both cropped 968x1721+54+77; place-home (c06 0.4 +1.6), place-office
(c09 1.6 +1.6), place-gym (c08 0.0 +1.6), place-club (c01 0.4 +2.5), dioramas at 1200x800.

## Audio (tools/gen-vo-v3.sh, tools/stt_words.sh, tools/vo_plan.py, tools/extend_bed.py, tools/mix.py)

- Music: the same ElevenLabs bed2 (v1's choice: the steadiest of three 22 s candidates). It is lengthened with
  `tools/extend_bed.py`: two bars (4.14 s at 116 BPM) of its steady middle are repeated, cut 13.99 s -> 9.85 s at the best
  envelope match, with a 40 ms equal-power crossfade, then trimmed to 24.5 s with a 0.9 s fade.
- VO: eleven_v3, voice_settings stability 0.5 (v3's "natural"), with-timestamps endpoint, mp3_44100_128; inline tags only
  [excited] (b1) and [warmly] (b6). Placement from tools/cues.json; 15 ms / 30 ms fades on each phrase cut.
- UI sounds (ElevenLabs sound-generation): a tap on each press frame (car, wash, time, booked), success on "booked", whooshes
  50 ms before each cut and softer ones on the card cuts.
- Chain (tools/mix.py): VO high-pass 80 Hz + compressor; music x0.5 side-chain ducked by the VO; loudnorm I=-14, TP=-2;
  limiter 0.75; AAC 192k. Measured on the renders: Liam -14.4 LUFS / -1.9 dBTP; Jessica -14.2 LUFS / -2.2 dBTP.
- Alt (Jessica) offsets from the picture cues, measured on its render: within ±1 frame except "It's" -2, "Then" +4, "and" -6
  and "Go" -7 (her b4 line is longer, so the beat was pulled 0.13 s earlier; b6 is anchored on "QuickWash" only).
