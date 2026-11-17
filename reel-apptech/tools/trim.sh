#!/usr/bin/env bash
# Footage for reel-apptech: cut each window from the client's raw AI clips (24 fps, silent) and transcode it to
# 30 fps H.264 yuv420p (CRF 16, no audio, faststart, keyframe every 15 frames so seeks are cheap).
# Usage: tools/trim.sh /path/to/raw   (holds c01.mp4 ... c14.mp4)
set -euo pipefail
RAW="${1:?raw clip dir}"; cd "$(dirname "$0")/.."; OUT=assets/footage; mkdir -p "$OUT"
enc() { # name src start source-dur vf   (a setpts in vf changes speed; the source window is what -t reads)
  ffmpeg -hide_banner -loglevel error -y -ss "$3" -t "$4" -i "$RAW/$2.mp4" -an \
    -vf "$5,fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 16 -g 15 -movflags +faststart "$OUT/$1.mp4"
  printf '%-14s %s %5ss +%ss  %s frames\n' "$1" "$2" "$3" "$4" "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$OUT/$1.mp4")"
}
# 1 HOOK: floating phone, steady window 0-2.4 s played at 6/7 speed to fill the 2.8 s hook (v2 VO line is longer)
#   (cover 1080x1920: 1076x1924 -> 1080x1931, crop 5 px top / 6 px bottom)
enc hook-phone   c14 0   2.4 "setpts=PTS*2.8/2.4,scale=1080:1931:flags=lanczos,crop=1080:1920:0:5"
# 4 DISPATCH (v2), under "Then we pull up to you": c03 1.0-2.55 at 1.6x (0.97 s: the illustrated van pushes in and starts
#   to morph on "pull up"), then cut to c03 3.8-4.6 (the real van on the road, wide; the phone number is small again). The
#   big phone-number pass (2.6-3.4) is skipped. Both are cropped to the top-left 90% so the sparkle watermark is out.
enc van-morph    c03 1.0 1.55 "setpts=(PTS-STARTPTS)/1.6,crop=968:1721:54:77,scale=1080:1920:flags=lanczos"
enc van-road     c03 3.8 0.8  "crop=968:1721:54:77,scale=1080:1920:flags=lanczos"
# 5 ANYWHERE: 3:2 dioramas kept whole (1200x800); each cut lands on its spoken word
enc place-home   c06 0.4 1.6 "scale=1200:800:flags=lanczos"
enc place-office c09 1.6 1.6 "scale=1200:800:flags=lanczos"
enc place-gym    c08 0.0 1.6 "scale=1200:800:flags=lanczos"
enc place-club   c01 0.4 2.5 "scale=1200:800:flags=lanczos"   # held 2.4 s (golf course -> end of the beat)
