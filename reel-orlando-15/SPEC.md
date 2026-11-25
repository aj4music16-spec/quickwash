# QuickWash "The $99 QuickWash, Orlando" - 15 s cut (Meta lead form)

Output `../dist/quickwash-orlando-99-15s.mp4`: 1080x1920, 30 fps, 15.67 s (470 frames), -14.2 LUFS, true peak -2.0 dBTP.
Short-form cut of `../reel-orlando` (30 s, untouched). Same footage pipeline, bed, end card, look; see ../reel-orlando/SPEC.md for
the client flags (Orlando booking, "spots filling up", NJ/NY footage, repainted Davenport card), claims and sources.
Pipeline: tools/trim.py -> tools/gen-audio.sh (s1-s3) -> tools/shorten_bed.py -> tools/vo_plan.py -> tools/build.py -> tools/mix.py
-> check -> render -> tools/verify_cues.py <mp4> <render.words.json>.

| shot | frames | source (window) | on screen |
|---|---|---|---|
| s01 open | 0-110 (3.67 s) | IMG_6406 7.9-11.6 (plate tracked + blurred) | chip "Orlando, FL", "The $99 / QuickWash." from f0; "We come to you." on "We" (f82) |
| s02 hand wash | 110-151 (1.37) | IMG_0012_1_22 1.5-2.9 | row "Foam + hand wash" |
| s03 vacuum stand-in | 151-184 (1.10) | IMG_2032 0.0-1.1 | row "Vacuum: seats, floors, trunk" |
| s04 glass | 184-217 (1.10) | IMG_6408 4.3-5.4 | row "Glass, in + out" |
| s05 tires + jambs | 217-266 (1.63) | IMG_6402 10.9-12.5 | row "Tire shine + door jambs" |
| s06 interior | 266-299 (1.10) | IMG_6439 0.1-1.2 (steady wide; replaces the shaky console-wipe POV) | row "Interior wiped down" |
| s07 spray wax | 299-332 (1.10) | IMG_6392 0.0-1.1 | row "Ceramic spray wax" |
| s08 price | 332-380 (1.60) | IMG_6432 2.0-3.6 | "$99" + "Standard-size vehicle" on "Ninety-nine"; all rows full |
| end card | 380-470 (3.00) | endcard-orlando.jpg | wipes up on "Drop" (12 f) |

Cuts: s02 on the off-beat 6.5 (the open line needs 3.3 s plus a breath); s03-s08 and the wipe on beats of the 110 BPM grid,
each pushed to >= 33 frames (1.1 s) where the grid gives 32.7. Open is 3.67 s, not ~2.4 s: Liam's s1 line takes 3.3 s.

VO (Liam, eleven_v3): s1 `[upbeat] Orlando: the ninety-nine dollar QuickWash. We come to you.` (t1 of 2; t2 slower),
s2 `Hand wash. Vacuum. Glass. Tires and door jambs. Interior. Spray wax.` (t1, the full list; it spans 7.0 s placed),
s3 `[excited] Ninety-nine bucks. Drop your info below.` (t1). Pauses only shortened/lengthened in silence; no time-stretch.
Glass, Tires and Spray are placed 1 frame early (Scribe on the first render heard them 2.0-2.8 f late).

Cue check (Scribe on the render's audio; visual = cut frame): We -1.4, Hand -0.4, Vacuum -1.4, Glass -0.8, Tires -0.8,
Interior -1.6, Spray -0.4, Ninety-nine -1.6, Drop -0.4 frames. All 7 hard cuts found on their planned frames.

Bed: bed1 (reel-orlando) with 12 beats (6.55 s, three bars) skipped at 4.87 s (`tools/shorten_bed.py`), so the beat grid holds
and the bed ends on its own final hit at ~14.9 s; the end card holds 0.7 s in its ring-out.
Check: 0 errors; warnings: nested media starts (local on purpose), short "We come to you." (0.97 s), closing-line timing on "$99"
(the end card follows), a contrast flag on the hidden second line at 0.87 s.
