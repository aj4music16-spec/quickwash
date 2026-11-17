#!/usr/bin/env bash
# Premix for reel-apptech: ElevenLabs bed (bed2, the steadiest of three) + ElevenLabs VO (voice iP95p4xoKVk53GoZ742B)
# + three ElevenLabs UI sounds, music side-chain ducked under the voice, loudnorm -14 LUFS / -1 dBTP.
# Usage: tools/mix.sh [out.m4a]   (default assets/audio/mix.m4a)
# 1. Each VO line has leading/trailing silence trimmed (silenceremove -45 dB, 40 ms kept at each end); l5 is split at its
#    internal pause (1.15 s) so "Wherever you park." lands on its own. Durations are printed; a line that would overlap the
#    next or cross its beat end fails the script (regenerate the take; never time-stretch).
# 2. Lines and UI sounds are placed at the starts below (film seconds).
set -euo pipefail
cd "$(dirname "$0")/.."
FILM=21.6
BED=assets/audio/music/bed2.mp3; VO=assets/audio/vo; SFX=assets/audio/sfx; OUT="${1:-assets/audio/mix.m4a}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
TRIM="silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse"
for i in 1 2 3 4 5 6; do ffmpeg -hide_banner -loglevel error -y -i "$VO/l$i.mp3" -af "$TRIM" -ar 48000 -ac 2 "$TMP/l$i.wav"; done
ffmpeg -hide_banner -loglevel error -y -i "$TMP/l5.wav" -af "atrim=0:1.15,afade=t=out:st=1.10:d=0.05" "$TMP/l5a.wav"
ffmpeg -hide_banner -loglevel error -y -i "$TMP/l5.wav" -af "atrim=start=1.17,asetpts=PTS-STARTPTS,$TRIM" "$TMP/l5b.wav"

#        file     start  latest-end   (beat)
LINES=("l1  0.25  2.35"    # HOOK "Your car wash is now an app."
       "l2  3.20  8.30"    # BOOK "Pick your car (3.20), pick a service (4.17), pick a time (4.89). Booked in twenty seconds (6.03)."
       "l3  8.55 10.35"    # GARAGE
       "l4 10.60 12.75"    # DISPATCH
       "l5a 13.00 14.60"   # ANYWHERE "Home, the office, the gym."
       "l5b 15.40 17.55"   # ANYWHERE "Wherever you park."
       "l6 18.10 21.00")   # END "QuickWash. Download the app."
#      file     start  gain(dB)
SFXS=("whoosh  2.30 -16" "tap  3.25 -4" "tap  4.20 -4" "tap  5.00 -4" "tap  5.65 -4" "success 5.95 -14"
      "whoosh  8.32 -18" "whoosh 10.32 -16" "whoosh 12.72 -16" "whoosh 13.92 -22" "whoosh 15.12 -22" "whoosh 16.32 -22"
      "whoosh 17.52 -16")

IN=(-i "$BED"); FC=""; VL=""; n=1; prev_end=0
for row in "${LINES[@]}"; do
  read -r f s lim <<<"$row"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/$f.wav")
  e=$(awk -v s="$s" -v d="$d" 'BEGIN{printf "%.2f", s + d}')
  printf '%-4s %.2f s  start %5s  end %5s\n' "$f" "$d" "$s" "$e"
  awk -v s="$s" -v pe="$prev_end" -v e="$e" -v lim="$lim" 'BEGIN{exit !(s >= pe + 0.1 && e <= lim)}' || { echo "  $f overlaps or overruns (limit $lim)"; exit 1; }
  prev_end=$e; ms=$(awk -v s="$s" 'BEGIN{printf "%d", s*1000+0.5}')
  IN+=(-i "$TMP/$f.wav"); FC+="[$n]adelay=$ms|$ms[v$n];"; VL+="[v$n]"; n=$((n+1))
done
NV=$((n-1)); SL=""; k=0
for row in "${SFXS[@]}"; do
  read -r f s g <<<"$row"; ms=$(awk -v s="$s" 'BEGIN{printf "%d", s*1000+0.5}')
  IN+=(-i "$SFX/$f.mp3"); FC+="[$n]aformat=sample_rates=48000:channel_layouts=stereo,volume=${g}dB,adelay=$ms|$ms[s$k];"; SL+="[s$k]"; n=$((n+1)); k=$((k+1))
done
FADE_ST=$(awk -v f="$FILM" 'BEGIN{print f - 0.8}')
ffmpeg -hide_banner -loglevel error -y "${IN[@]}" -filter_complex "$FC
  ${VL}amix=inputs=$NV:normalize=0,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=1.5,
    aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=$FILM,atrim=0:$FILM,asplit=2[vo][sc];
  ${SL}amix=inputs=$k:normalize=0,apad=whole_dur=$FILM,atrim=0:$FILM[fx];
  [0]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=$FILM,atrim=0:$FILM,afade=t=out:st=$FADE_ST:d=0.8,volume=0.5[mus];
  [mus][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=350:makeup=1[duck];
  [duck][fx][vo]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.75:level=false,atrim=0:$FILM[out]" \
  -map "[out]" -c:a aac -b:a 192k "$OUT"
echo "wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT") s)"
ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak:"
