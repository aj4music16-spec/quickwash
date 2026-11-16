#!/usr/bin/env bash
# usage: mix.sh <work_dir> <out.mp4>
# <work_dir> holds seg/ (from build.py) and audio/: vA..vE.mp3 (ElevenLabs VO, voice "Laura"),
# beat1.mp3 + beat2.mp3 (ElevenLabs generated beat, looped back to back).
set -euo pipefail
W=$1; OUT=$2
ls "$W"/seg/[0-9]*.mp4 | sed "s|^|file '|;s|$|'|" > "$W/seg/list.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$W/seg/list.txt" -c copy "$W/video_live.mp4"
ffmpeg -v error -y -i "$W/video_live.mp4" -i "$W/audio/vA.mp3" -i "$W/audio/vB.mp3" -i "$W/audio/vC.mp3" \
  -i "$W/audio/vD.mp3" -i "$W/audio/vE.mp3" -i "$W/audio/beat2.mp3" -i "$W/audio/beat1.mp3" -filter_complex "\
[0:a]volume=1.8,highpass=f=90[live];\
[1:a]adelay=150|150[a1];[2:a]adelay=2750|2750[a2];[3:a]adelay=7550|7550[a3];[4:a]adelay=18150|18150[a4];[5:a]adelay=22850|22850[a5];\
[a1][a2][a3][a4][a5]amix=inputs=5:normalize=0,aformat=channel_layouts=stereo,volume=1.6[vo];\
[vo][live]amix=inputs=2:normalize=0,apad=whole_dur=27.5,asplit[voice][sc];\
[6:a][7:a]concat=n=2:v=0:a=1,atrim=0:27.5,asetpts=PTS-STARTPTS,volume=0.45,afade=t=out:st=26.3:d=1.2[bed];\
[bed][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];\
[duck][voice]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 27.5 -movflags +faststart "$OUT"
