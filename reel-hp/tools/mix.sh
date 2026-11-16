#!/usr/bin/env bash
# Premixes the ad's audio: ElevenLabs music bed + ElevenLabs voiceover, music ducked under the voice.
# Usage: tools/mix.sh <bed: acoustic|soul|indie> <voice: chris|sarah> <out.m4a>
# Line placement (seconds) follows the edit: price on frame 0, city on the S2 cut, the six services
# across the punches, "home" over S10, the call to action after the logo lands.
set -euo pipefail
cd "$(dirname "$0")/.."
BED="assets/audio/music/bed_$1.mp3"; VO="assets/audio/vo/$2"; OUT="$3"
ffmpeg -hide_banner -loglevel error -y \
  -i "$BED" -i "${VO}_l1.mp3" -i "${VO}_l2.mp3" -i "${VO}_l3.mp3" -i "${VO}_l4.mp3" -i "${VO}_l5.mp3" \
  -filter_complex "
    [1]adelay=250|250[v1];[2]adelay=1850|1850[v2];[3]adelay=3750|3750[v3];[4]adelay=13400|13400[v4];[5]adelay=17350|17350[v5];
    [v1][v2][v3][v4][v5]amix=inputs=5:normalize=0,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=1.5,
      aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=19.8,atrim=0:19.8,asplit=2[vo][sc];
    [0]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:19.8,afade=t=in:d=0.03,afade=t=out:st=19.1:d=0.7,volume=0.55[mus];
    [mus][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=350:makeup=1[duck];
    [duck][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.85:level=false[out]" \
  -map "[out]" -c:a aac -b:a 192k "$OUT"
