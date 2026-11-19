#!/usr/bin/env bash
# Footage for reel-race. Most shots are reel-hp's finished clips (already trimmed, graded, plate-blurred), copied as-is.
# Three windows are re-cut longer from the same proxies with reel-hp's grade (tools/trim.py there: eq contrast 1.05,
# saturation 1.08), H.264 CRF 18 yuv420p 30 fps, AAC audio kept. None of these windows shows a plate.
# v3 (shot = word): the race shows exactly what each phrase says; new windows below the reel-hp copies.
# Usage: tools/trim.sh <reel-hp footage dir> <hp proxy dir> <dirty-shoot proxy dir>
set -euo pipefail
HP=$1; PA=$2; PB=$3; cd "$(dirname "$0")/.."; OUT=assets/footage; mkdir -p "$OUT"
for f in s03-mitt-bumper s05-windshield-rinse s07-door-wipe s08-spray-hood s09-hero-side; do cp "$HP/$f.mp4" "$OUT/"; done
G="eq=contrast=1.05:saturation=1.08"
cut() { # name src in dur extra-vf
  ffmpeg -hide_banner -loglevel error -y -ss "$3" -t "$4" -i "$2" -vf "$G${5:+,$5},fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 18 \
    -c:a aac -b:a 128k -movflags +faststart "$OUT/$1.mp4"
  echo "$1 $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$1.mp4") s"
}
cut s01-foam-long    "$PA/IMG_0012.mp4" 6.8 5.7               # hook: foam sheeting down the side (reel-hp s01 is 10.2-12.0 of this)
cut s06-wheel-long   "$PA/IMG_6386.mp4" 4.4 2.6 # tires: pressure rinse blasts foam off the wheel (reel-hp s06 is 4.8-6.0)
# vacuum: the only vacuum shot (fresh vacuum lines, IMG_2059, 3.0 s in all) is a little short of its line: played at 0.91x (3.3 s)
ffmpeg -hide_banner -loglevel error -y -i "$PB/IMG_2059.mp4" -an -vf "$G,setpts=PTS*1.1,fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 18 \
  -movflags +faststart "$OUT/s04-vacuum-long.mp4"; echo "s04-vacuum-long $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/s04-vacuum-long.mp4) s"
# v3 race windows (graded the same; no plate, face or legible label in any of them; audio unused)
cut r1-foam-cannon   "$PA/IMG_0012_1_17.mp4" 1.0 1.0             # "Foam ..." foam cannon blasting snow foam onto the SUV
cut r3-glass-mitt    "$PB/IMG_2041.mp4"      15.0 2.25           # "Glass, inside and out": mitt washing the windshield (POV close-up)
cut r4-tire-spray    "$PB/IMG_2040.mp4"      4.6 1.3             # "Tire shine": spray bottle working the wheel and tire
cut r4-door-jamb     "$PB/IMG_2040.mp4"      61.9 1.4            # "... and door jambs": wand rinsing the open door's jamb and sill
cut r5-console-wipe  "$PB/IMG_2034.mp4"      35.5 1.95           # "Interior wiped down": gloved hand wiping the centre console
# v4 race (client: wider shots, fewer and longer, no zoom feel): wide/medium windows, steady camera, same grade
cut r1w-foam-street  "$PA/IMG_0012_1_14.mp4" 4.5 2.1             # wide street: detailer foam-cannons the SUV white (no plate in view)
cut r2w-interior     "$PA/IMG_6439.mp4"      0.1 3.35            # driver door open, slow arc over the clean interior (door edge enters after 3.4 s)
cut r4w-wheel-scrub  "$PA/IMG_6383.mp4"      8.4 4.2             # medium: detailer crouched, scrubbing the foamed wheel and tyre (face away)
# wide rooftop: detailer rinsing the Durango's windshield and roof; the front plate is static in this window -> fixed blur box
ffmpeg -hide_banner -loglevel error -y -ss 0.8 -t 2.25 -i "$PB/IMG_2046.mp4" -an -filter_complex \
  "[0]$G,split[a][b];[b]crop=80:120:5:1220,boxblur=18:4[bl];[a][bl]overlay=5:1220,fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 18 -movflags +faststart "$OUT/r3w-durango-rinse.mp4"; echo "r3w-durango-rinse $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/r3w-durango-rinse.mp4) s"
