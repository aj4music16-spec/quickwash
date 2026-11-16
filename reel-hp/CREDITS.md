# Credits: footage used in "The $99 Tag"

All footage: QuickWash B-roll (May driveway shoot and July city-lot shoot), from the 1080x1920 proxies.
Each file in assets/footage/ is the shot window plus 0.5 s handles (clamped at the clip start), re-encoded by
tools/trim.py. "In-out" is the source time on screen.

| Part / shot | Time (s) | File | Source | In-out (s) | Notes |
|---|---|---|---|---|---|
| A hook still 1 | 0.0-0.8 | assets/stills/04b_cups.jpg | client-supplied AI-generated image | — | not QuickWash footage |
| A hook still 2 | 0.8-1.6 | assets/stills/01b_crumbs.jpg | client-supplied AI-generated image | — | not QuickWash footage |
| A hook still 3 | 1.6-2.4 | assets/stills/04c_clutter.jpg | client-supplied AI-generated image | — | not QuickWash footage |
| B we come to you | 2.4-3.6 | s02-detailer-driveway.mp4 | IMG_0012_1_13.mp4 | 1.5-2.7 | NJ plate blurred; detailer from behind |
| B now in High Point | 3.6-4.8 | s01-foam-sheet.mp4 | IMG_0012.mp4 | 10.2-11.4 | clip sound at 0.12 |
| C foam + hand wash | 4.8-6.0 | s03-mitt-bumper.mp4 | IMG_0012_1_21.mp4 | 1.3-2.5 | face in profile |
| C vacuum (stand-in) | 6.0-7.2 | s04-clean-footwell.mp4 | IMG_6436.MOV | 1.4-2.6 | |
| C glass (stand-in) | 7.2-8.4 | s05-windshield-rinse.mp4 | IMG_6397.MOV | 4.4-5.6 | plate blurred; QuickWash van at left |
| C tires (stand-in) | 8.4-9.6 | s06-wheel-rinse.mp4 | IMG_6386.MOV | 4.8-6.0 | clip sound at 0.12 |
| C dash (stand-in) | 9.6-10.8 | s07-clean-dash.mp4 | IMG_6439.MOV | 1.8-3.0 | Volvo wheel badge |
| C wax (stand-in) | 10.8-12.0 | s08-spray-hood.mp4 | IMG_6393.MOV | 0.3-1.5 | plate blurred; unlabelled bottle |
| D payoff hero | 12.0-15.6 | s09-hero-side.mp4 | IMG_6438.MOV | 0.1-3.7 | v5 re-trim (handles clamped at both clip ends); 1.00-1.05 push in HTML |
| E urgency | 15.6-18.4 | s11-detailer-logo.mp4 | IMG_0012_1_15.mp4 | 0.3-3.1 | v5 re-trim; under the end-card wipe 18.0-18.4; clip sound at 0.12 |

Not used in v5: s10-detailer-house.mp4 (IMG_0012_1_12, plate blurred) stays in assets/footage for a later cut.

People on camera: the May detailer (s02, s03, s11) and the July detailer (s05 small, s06 hand, s08 partial face).
Get signed releases before the ad runs. Third-party marks visible: Nissan, Volvo badges.

v1 music (no longer used): synthesized by tools/soundtrack.js.
Logo (store badges no longer on the v5 end card): assets/app (QuickWash; official Apple and Google badge artwork, untinted).
Fonts: Poppins, Inter, League Gothic (tag print) — all SIL OFL.

## Audio (v4)

- Music: ElevenLabs sound generation, three 20 s instrumental beds in `assets/audio/music/` (acoustic pop, southern soul, indie pop), generated on the client's ElevenLabs account.
- Voiceover: ElevenLabs text-to-speech, `eleven_multilingual_v2`, voices Chris and Sarah, 5 lines (`assets/audio/vo/script.json`).
- Mix: `tools/mix.sh <bed> <voice> <out.m4a>` places the lines at 0.25 / 1.85 / 3.75 / 13.4 / 17.35 s, ducks the music under the voice, and normalizes to about -14 LUFS.
  Main cut: acoustic + Chris (`dist/quickwash-highpoint-99.mp4`). Alternate: soul + Sarah (`dist/quickwash-highpoint-99-alt-soul-sarah.mp4`).
- Clip natural sound lowered from 0.25 to 0.12 so it sits under the voice.
- Check ElevenLabs' commercial-use terms for your plan before running paid media.

## Audio (v5)

- Music: `assets/audio/music/bed_acoustic22.mp3`, a 22 s ElevenLabs instrumental (acoustic).
- Voiceover: ElevenLabs, voice Chris, 5 new lines in `assets/audio/vo2/` (`script.json`).
- Mix: `tools/mix.sh [out.m4a]` trims each line's silence, places them at 0.15 / 2.50 / 8.30 / 12.85 / 16.10 s, ducks the
  music and normalizes to about -14 LUFS → `assets/audio/mix-v5.m4a`. The v4 alternates (soul + Sarah) were made with the
  previous mix.sh (it took `<bed> <voice> <out>`); that form is replaced by this one.
