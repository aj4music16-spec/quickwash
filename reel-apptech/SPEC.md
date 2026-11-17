# QuickWash app product film ("Your car wash is now an app")

1080x1920, 30 fps, 21.6 s (648 frames). Output: `../dist/quickwash-app-product.mp4`
(`npx --yes hyperframes@0.9.27 render -o ../dist/quickwash-app-product.mp4 --quality delivery --max-bitrate 12M`,
env `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1`).

Look: product-keynote "tech". Light ground `#f4f6fb` with a 60 px navy grid at 5% and faint navy/orange glows; navy `#000099`
type, orange `#FF6600` accents; Poppins 600-700 for headlines/callouts, Inter for UI labels; thin navy leader lines with a
white halo; expo/back eases; soft ring tap ripples (no cursor). No CSS filters on footage.

## Beats

| # | film s | composition | picture | on-screen text | VO (start) |
|---|---|---|---|---|---|
| 1 HOOK | 0.0-2.4 | `hook.html` | c14 0-2.4 (floating phone), shown at 88% from the bottom edge. From 0.9 s the clean home screen is corner-pinned on the phone screen (per-frame tracked, `tools/track_phone.py` -> `tools/pin_matrices.py`, matrix3d per frame), with a drawn Dynamic Island on top | "Your car wash / is now an app." (on frame 0; orange underline draws at 0.95) | l1 0.25 |
| 2 BOOK | 2.4-8.4 | `app.html` 0-6 | CSS phone (632x1336, real screenshots at 0.4545) arrives from the hook phone's place. Taps: Ringo card 3.25 (glow) -> QuickWash $99.00 row 4.2 (row highlight) -> Book an Appointment sheet 4.55 -> 01:00 PM 5.0 -> Book This Slot 5.65 -> "Booked ✓" chip 5.95 | stopwatch 0:00 -> 0:20 (3.0-5.95); STEP 1 "Pick your car", STEP 2 "Pick a service", STEP 3 "Pick a time" with leader lines to each tap; headline "Booked in / 20 seconds." 6.05 | l2 3.20 (car 3.20, service 4.17, time 4.89, "Booked in twenty seconds" 6.03) |
| 3 GARAGE | 8.4-10.4 | `app.html` 6-8 | phone pushes to 1.35x, centred; My Garage slides in | "Every car. / One garage."; chips "Book Wash", "History", "Set Recurring" on leader lines to Ringo's card buttons | l3 8.55 |
| 4 DISPATCH | 10.4-12.8 | `dispatch.html` | c03 0.4-1.6 (illustrated van, push in), then c03 3.6-4.8 (van on the road; cropped to the top-left 90% so the sparkle watermark is out; starts after the big phone-number pass) | card "Then we / come to you." | l4 10.60 |
| 5 ANYWHERE | 12.8-17.6 | `anywhere.html` | four whole 3:2 cards (960x640), 1.2 s each, push in from the right: c06 0.4- "Home", c09 1.6- "Office" (side-on, after the front-grille frames), c08 0.0- "Gym" (before the car foams white), c01 0.4- "The club"; route rail with four stops below | "Wherever / you park." + pin chips | l5a 13.00 "Home, the office, the gym." / l5b 15.40 "Wherever you park." |
| 6 END | 17.6-21.6 | `end.html` | white + grid; logo (with wordmark) pops in a ring | "The car wash that / comes to you.", "DOWNLOAD QUICKWASH", App Store + Google Play badges (badges y 980-1092) | l6 18.10 |

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

Client AI clips, 24 fps silent -> 30 fps H.264 yuv420p CRF 16, no audio: hook-phone (c14 0-2.4), van-illus (c03 0.4 +1.3),
van-road (c03 3.6 +1.3, crop 968x1721+54+77), place-home (c06 0.4 +1.6), place-office (c09 1.6 +1.6), place-gym
(c08 0.0 +1.6), place-club (c01 0.4 +1.6), dioramas at 1200x800.

## Audio (tools/gen-audio.sh, tools/mix.sh -> assets/audio/mix.m4a)

- ElevenLabs sound-generation, 22 s, prompt_influence 0.6: "Clean modern upbeat tech product commercial music bed, soft
  synth plucks, light electronic beat, 116 BPM, bright and optimistic, steady energy, polished keynote style, no vocals".
  Three candidates; short-term loudness 3-21 s: bed1 sd 7.3 LU (fades out from 17 s), bed2 sd 1.8, bed3 sd 1.9 -> bed2.
- VO: ElevenLabs TTS voice iP95p4xoKVk53GoZ742B, eleven_multilingual_v2, stability 0.4 / similarity 0.8 / style 0.4,
  lines l1-l6 as written; silence-trimmed (-45 dB), l5 split at its pause; no time-stretch.
- UI sounds (ElevenLabs sound-generation): tap (x4 on the taps), success (Booked), whoosh (cuts and card pushes).
- Chain: VO high-pass 80 Hz + compressor; music x0.5 side-chain ducked by the VO; loudnorm I=-14, TP=-2; limiter 0.75;
  AAC 192k. Measured on the render: -14.3 LUFS integrated, true peak -1.7 dBFS.
