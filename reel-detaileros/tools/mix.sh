#!/usr/bin/env bash
# usage: tools/mix.sh <frames_dir> <out.mp4>   (run from reel-detaileros/)
set -euo pipefail
FR=$1; OUT=$2; A=assets/audio; DUR=18
# cue list: sound  time(s)  gain
CUES="ding 0.42 0.9
whoosh 2.50 0.7
pop 3.05 0.35
pop 3.42 0.4
whoosh 3.45 0.35
tap 5.35 0.8
whoosh 6.00 0.75
pop 6.38 0.45
tick 7.27 0.6
kaching 7.70 0.6
whoosh 9.50 0.75
pop 9.92 0.35
pop 10.27 0.4
whoosh 10.40 0.35
tick 11.45 0.55
tick 11.75 0.55
tick 12.05 0.55
pop 12.38 0.45
tap 12.95 0.8
impact 13.42 0.9
pop 15.18 0.45"
args=(-i "$A/bed.mp3"); fc="[0:a]atrim=0:$DUR,asetpts=PTS-STARTPTS,volume=0.55,afade=t=in:d=0.15,afade=t=out:st=$((DUR-1)).2:d=0.8[bed];"
i=1; labels="[bed]"
while read -r name t g; do
  args+=(-i "$A/$name.wav"); ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  fc+="[$i:a]aformat=channel_layouts=stereo,volume=$g,adelay=$ms|$ms[s$i];"; labels+="[s$i]"; i=$((i+1))
done <<< "$CUES"
fc+="${labels}amix=inputs=$i:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]"
ffmpeg -v error -y -framerate 30 -i "$FR/f%05d.jpg" "${args[@]}" -filter_complex "$fc" -map 0:v -map "[a]" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 192k -t $DUR -movflags +faststart "$OUT"
