#!/usr/bin/env bash
# usage: tools/mix.sh <frames_dir> <out.mp4>   (run from reel-detaileros/)
# Layers: music bed (ducks under effects and voice) + sound effects + voiceover (ElevenLabs "Chris", first-person detailer story).
set -euo pipefail
FR=$1; OUT=$2; A=assets/audio; DUR=20.5
# sound effects: name  time(s)  gain
CUES="buzz 0.30 1.0
whoosh 2.50 0.7
pop 3.05 0.35
pop 3.42 0.4
whoosh 3.45 0.35
tap 5.35 1.6
whoosh 6.00 0.75
pop 6.38 0.45
tick 10.47 0.6
kaching 10.85 0.6
whoosh 11.90 0.75
pop 12.32 0.35
pop 12.67 0.4
whoosh 12.80 0.35
tick 13.45 0.55
tick 13.85 0.55
tick 14.25 0.55
pop 14.92 0.45
tap 15.60 1.6
impact 16.62 0.9
pop 17.97 0.45"
# voiceover lines: file  time(s)
VO="v1 1.25
v2 3.50
v3 6.40
v4 9.75
v5 12.55
v6 17.15"

args=(-i "$A/music22.mp3")
FADE=$(awk "BEGIN{print $DUR-0.9}")
fc="[1:a]atrim=0:$DUR,asetpts=PTS-STARTPTS,volume=0.7,afade=t=in:d=0.15,afade=t=out:st=$FADE:d=0.9[bed];"
i=2; n=0; labels=""
while read -r name t g; do
  args+=(-i "$A/$name.wav"); ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  fc+="[$i:a]aformat=channel_layouts=stereo,volume=$g,adelay=$ms|$ms[s$i];"; labels+="[s$i]"; i=$((i+1)); n=$((n+1))
done <<< "$CUES"
fc+="${labels}amix=inputs=$n:normalize=0:duration=longest,apad=whole_dur=$DUR,volume=1.3,asplit[sfx][sc];"
v=0; vlabels=""
while read -r name t; do
  args+=(-i "$A/vo_story/$name.wav"); ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  fc+="[$i:a]aformat=channel_layouts=stereo,adelay=$ms|$ms[v$i];"; vlabels+="[v$i]"; i=$((i+1)); v=$((v+1))
done <<< "$VO"
fc+="${vlabels}amix=inputs=$v:normalize=0:duration=longest,apad=whole_dur=$DUR,highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=5:release=120,volume=2.2,asplit[vo][vsc];"
# music ducks under effects, then under voice (harder), and the effects sit a little lower under voice
fc+="[bed][sc]sidechaincompress=threshold=0.03:ratio=5:attack=4:release=220[bd1];"
fc+="[bd1][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=10:release=300[bd2];"
fc+="[bd2][sfx][vo]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.7,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]"
ffmpeg -v error -y -framerate 30 -i "$FR/f%05d.jpg" "${args[@]}" -filter_complex "$fc" -map 0:v -map "[a]" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 192k -t $DUR -movflags +faststart "$OUT"
