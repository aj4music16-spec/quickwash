#!/usr/bin/env bash
# v6 premix for the Meta lead-form cut: ElevenLabs acoustic bed + ElevenLabs voiceover (Chris), music ducked under the voice.
# Usage: tools/mix.sh [out.m4a]   (default assets/audio/mix-v6.m4a)
# 1. Each VO line has its leading/trailing silence trimmed (silenceremove, -45 dB, 40 ms kept at each end); the trimmed
#    durations are printed.
# 2. Lines are placed at their requested starts, then nudged so no two overlap (>= 0.1 s gap), l1 ends by 3.5 s, l4 ends by 15.7 s
#    (before the urgency cut) and l5 ends by 21.8 s.
# 3. Same chain as before: VO high-pass + compressor, sidechain duck of the music, loudnorm -14 LUFS, limiter.
set -euo pipefail
cd "$(dirname "$0")/.."
FILM=22.0
BED="assets/audio/music/bed_acoustic22.mp3"; VO="assets/audio/vo3/chris"; OUT="${1:-assets/audio/mix-v6.m4a}"
REQ=(0.10 3.7 8.8 12.85 16.1)         # requested starts for l1..l5 (s); l3 asked at 8.9, moved to 8.8 so l4 can end by 15.7
LIMIT=(3.5 0 0 15.7 21.8)               # latest allowed end per line (0 = none)
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

DUR=()
for i in 1 2 3 4 5; do
  ffmpeg -hide_banner -loglevel error -y -i "${VO}_l$i.mp3" -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse" -ar 48000 -ac 2 "$TMP/l$i.wav"
  DUR+=("$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/l$i.wav")")
done

START=()
prev_end=0
for k in 0 1 2 3 4; do
  read -r s e < <(awk -v r="${REQ[$k]}" -v d="${DUR[$k]}" -v pe="$prev_end" -v lim="${LIMIT[$k]}" 'BEGIN{
    s=r; if (s < pe + 0.1 && pe > 0) s = pe + 0.1;
    if (lim > 0 && s + d > lim) { s = lim - d; if (s < pe + 0.1) s = pe + 0.1 }
    printf "%.2f %.3f\n", s, s + d }')
  START+=("$s"); prev_end="$e"
  printf 'l%d  trimmed %.2f s  start %s  end %.2f\n' $((k + 1)) "${DUR[$k]}" "$s" "$e"
done

D=(); for s in "${START[@]}"; do D+=("$(awk -v s="$s" 'BEGIN{printf "%d", s*1000 + 0.5}')"); done
FADE_ST=$(awk -v f="$FILM" 'BEGIN{print f - 0.7}')
ffmpeg -hide_banner -loglevel error -y \
  -i "$BED" -i "$TMP/l1.wav" -i "$TMP/l2.wav" -i "$TMP/l3.wav" -i "$TMP/l4.wav" -i "$TMP/l5.wav" \
  -filter_complex "
    [1]adelay=${D[0]}|${D[0]}[v1];[2]adelay=${D[1]}|${D[1]}[v2];[3]adelay=${D[2]}|${D[2]}[v3];[4]adelay=${D[3]}|${D[3]}[v4];[5]adelay=${D[4]}|${D[4]}[v5];
    [v1][v2][v3][v4][v5]amix=inputs=5:normalize=0,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=1.5,
      aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=$FILM,atrim=0:$FILM,asplit=2[vo][sc];
    [0]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=$FILM,atrim=0:$FILM,afade=t=in:d=0.03,afade=t=out:st=$FADE_ST:d=0.7,volume=0.55[mus];
    [mus][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=350:makeup=1[duck];
    [duck][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.85:level=false,atrim=0:$FILM[out]" \
  -map "[out]" -c:a aac -b:a 192k "$OUT"
echo "wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT") s)"
