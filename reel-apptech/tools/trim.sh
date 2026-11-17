#!/usr/bin/env bash
# Footage for reel-apptech: cut each window from the client's raw AI clips (24 fps, silent) and transcode it to
# 30 fps H.264 yuv420p (CRF 16, no audio, faststart, keyframe every 15 frames so seeks are cheap).
# Usage: tools/trim.sh /path/to/raw   (holds c01.mp4 ... c14.mp4)
set -euo pipefail
RAW="${1:?raw clip dir}"; cd "$(dirname "$0")/.."; OUT=assets/footage; mkdir -p "$OUT"
enc() { # name src start dur vf
  ffmpeg -hide_banner -loglevel error -y -ss "$3" -i "$RAW/$2.mp4" -t "$4" -an \
    -vf "$5,fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 16 -g 15 -movflags +faststart "$OUT/$1.mp4"
  printf '%-14s %s %5ss +%ss  %s frames\n' "$1" "$2" "$3" "$4" "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$OUT/$1.mp4")"
}
# 1 HOOK: floating phone, steady window 0-2.4 s (cover 1080x1920: 1076x1924 -> 1080x1931, crop 5 px top / 6 px bottom)
enc hook-phone   c14 0   2.4 "scale=1080:1931:flags=lanczos,crop=1080:1920:0:5"
# 4 DISPATCH: illustrated van (before the push), then the photoreal van on the road. The road window starts at 3.6 s,
#   after the big phone-number pass; it is cropped to the top-left 90% so the sparkle watermark (bottom-right from 2.6 s) is out.
enc van-illus    c03 0.4 1.3 "scale=1080:1931:flags=lanczos,crop=1080:1920:0:5"
enc van-road     c03 3.6 1.3 "crop=968:1721:54:77,scale=1080:1920:flags=lanczos"
# 5 ANYWHERE: 3:2 dioramas kept whole (1200x800), 1.6 s each (1.2 s on screen + slide overlap)
enc place-home   c06 0.4 1.6 "scale=1200:800:flags=lanczos"
enc place-office c09 1.6 1.6 "scale=1200:800:flags=lanczos"
enc place-gym    c08 0.0 1.6 "scale=1200:800:flags=lanczos"
enc place-club   c01 0.4 1.6 "scale=1200:800:flags=lanczos"
