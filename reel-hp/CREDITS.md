# Credits: footage used in "The $99 Tag"

All footage: QuickWash B-roll (May driveway shoot and July city-lot shoot), from the 1080x1920 proxies.
Each file in assets/footage/ is the shot window plus 0.5 s handles (clamped at the clip start), re-encoded by
tools/trim.py. "In-out" is the source time on screen.

| Part / shot | Time (s) | File | Source | In-out (s) | Notes |
|---|---|---|---|---|---|
| A hook: salt-crusted floor | 0.0-0.9 | h1-salt-floor.mp4 | IMG_2020 (dirty-car shoot) | 0.0-0.9 | filmer's shoe at frame edge; no face |
| A hook: rear carpet | 0.9-1.8 | h2-rear-carpet.mp4 | IMG_2022 (dirty-car shoot) | 2.3-3.2 | |
| A hook: bottle + headphones | 1.8-2.7 | h3-bottle-headphones.mp4 | IMG_2022 (dirty-car shoot) | 8.3-9.2 | headphone brand not legible |
| A hook: "Dirty" on the door | 2.7-3.6 | h4-dirty-door.mp4 | IMG_2028 (dirty-car shoot) | 0.0-0.9 | tiny distant reflection in the mirror only |
| B we come to you | 3.6-4.8 | o1-van-logo.mp4 | IMG_3730 (dirty-car shoot) | 0.0-1.2 | QuickWash van logo; plate appears only after 2.6 s (not in the file) |
| B your driveway. $99. | 4.8-6.0 | s01-foam-sheet.mp4 | IMG_0012.mp4 | 10.2-11.4 | clip sound at 0.12 |
| C foam + hand wash | 6.0-7.1 | s03-mitt-bumper.mp4 | IMG_0012_1_21.mp4 | 1.3-2.4 | face in profile |
| C vacuum (result) | 7.1-8.2 | s04-vacuum-lines.mp4 | IMG_2059 (dirty-car shoot) | 0.2-1.3 | clean mat with fresh vacuum lines |
| C glass (stand-in) | 8.2-9.3 | s05-windshield-rinse.mp4 | IMG_6397.MOV | 4.4-5.5 | plate blurred; QuickWash van at left |
| C tires (stand-in) | 9.3-10.4 | s06-wheel-rinse.mp4 | IMG_6386.MOV | 4.8-5.9 | clip sound at 0.12 |
| C dash (stand-in) | 10.4-11.5 | s07-clean-dash.mp4 | IMG_6439.MOV | 1.8-2.9 | Volvo wheel badge |
| C wax (stand-in) | 11.5-12.6 | s08-spray-hood.mp4 | IMG_6393.MOV | 0.3-1.4 | plate blurred; unlabelled bottle |
| D payoff hero | 12.6-15.6 | s09-hero-side.mp4 | IMG_6438.MOV | 0.1-3.1 | 1.00-1.05 push in HTML |
| E urgency | 15.6-18.4 | s11-detailer-logo.mp4 | IMG_0012_1_15.mp4 | 0.3-3.1 | under the end-card wipe 18.0-18.4; clip sound at 0.12 |

"Dirty-car shoot" = the client's Drive folder "dirty car": one job on a grey Dodge Durango (rooftop deck), proxies
already tone-mapped SDR. The customer plate H45-VLA and the van plate P81-RZT appear in other clips of that shoot;
neither is in any window used here. The other clips come from the May and July B-roll shoots.

Not used in v6: s02-detailer-driveway.mp4, s04-clean-footwell.mp4, s10-detailer-house.mp4 (kept in assets/footage), and the
v5 AI-generated stills in assets/stills (no longer referenced).

People on camera: the May detailer (s03, s11) and the July detailer (s05 small, s06 hand, s08 partial face). No people in the dirty-car windows.
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

## Audio (v6)

- Voiceover: `assets/audio/vo3/` (Chris), new l1 and l4; music `bed_acoustic22.mp3` as v5.
- Mix: `tools/mix.sh [out.m4a]` → `assets/audio/mix-v6.m4a`; lines at 0.10 / 3.70 / 8.80 / 12.75 / 16.10 s after silence trim.
