#!/usr/bin/env bash
# Footage for reel-race. Most shots are reel-hp's finished clips (already trimmed, graded, plate-blurred), copied as-is.
# Three windows are re-cut longer from the same proxies with reel-hp's grade (tools/trim.py there: eq contrast 1.05,
# saturation 1.08), H.264 CRF 18 yuv420p 30 fps, AAC audio kept. None of these windows shows a plate.
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
cut s01-foam-long    "$PA/IMG_0012.mp4" 7.4 5.1               # hook: foam sheeting down the side (reel-hp s01 is 10.2-12.0 of this)
cut s06-wheel-long   "$PA/IMG_6386.mp4" 4.4 2.6 # tires: pressure rinse blasts foam off the wheel (reel-hp s06 is 4.8-6.0)
# vacuum: the only vacuum shot (fresh vacuum lines, IMG_2059, 3.0 s in all) is a little short of its line: played at 0.91x (3.3 s)
ffmpeg -hide_banner -loglevel error -y -i "$PB/IMG_2059.mp4" -an -vf "$G,setpts=PTS*1.1,fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 18 \
  -movflags +faststart "$OUT/s04-vacuum-long.mp4"; echo "s04-vacuum-long $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/s04-vacuum-long.mp4) s"
