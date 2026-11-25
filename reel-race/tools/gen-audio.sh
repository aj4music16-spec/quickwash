#!/usr/bin/env bash
# ElevenLabs audio for reel-race (the proxy injects the API key; no auth header; one request at a time; mp3_44100_128).
# Usage: tools/gen-audio.sh vo|items|music|sfx|pickup [takes]
#   VOICE=laura tools/gen-audio.sh vo 4  -> Laura FGY2WhTYpPnrIDTdsKH5 into assets/audio/vo-laura (speed-run tags);
#   default VOICE=liam (TX3LPaxmHKxFdv7VOQHJ, assets/audio/vo, the alt cut)
#   vo    : eleven_v3 voice Liam, beats b1-b5, with-timestamps (alignment JSON kept; cues use Scribe, tools/stt_words.sh)
#   items : the six b2 list items as separate short takes (i1-i6), for butting together if one b2 take paces badly
set -uo pipefail
cd "$(dirname "$0")/.."
A=assets/audio; API=https://api.elevenlabs.io/v1; T=${2:-3}; VOICE=${VOICE:-liam}
if [ "$VOICE" = laura ]; then VID=FGY2WhTYpPnrIDTdsKH5; VD=$A/vo-laura; else VID=TX3LPaxmHKxFdv7VOQHJ; VD=$A/vo; fi; mkdir -p "$VD"
tts() { # text out
  local f=$2; [ -s "$f.mp3" ] && return 0
  local body; body=$(python3 -I -c 'import json,sys; print(json.dumps({"text": sys.argv[1], "model_id": "eleven_v3", "voice_settings": {"stability": 0.5}}))' "$1")
  local code n=0
  while :; do   # the account is shared: on HTTP 429 wait 20 s and retry (up to 6 times)
    code=$(curl -sS -o "$f.resp" -w '%{http_code}' -X POST "$API/text-to-speech/$VID/with-timestamps?output_format=mp3_44100_128" -H 'Content-Type: application/json' --data "$body")
    [ "$code" = 429 ] && [ $n -lt 6 ] && { n=$((n+1)); echo "429, waiting 20 s"; sleep 20; continue; }; break
  done
  if [ "$code" != 200 ]; then echo "ERR $code $f: $(head -c 300 "$f.resp")"; rm -f "$f.resp"; return 1; fi
  python3 -I -c 'import json,base64,sys; d=json.load(open(sys.argv[1])); open(sys.argv[2]+".mp3","wb").write(base64.b64decode(d["audio_base64"])); json.dump(d["alignment"], open(sys.argv[2]+".json","w"))' "$f.resp" "$f" && rm -f "$f.resp"; echo "ok  $f.mp3"
}
sfx() { # text dur influence out
  [ -s "$4" ] && return 0
  local code; code=$(curl -sS -o "$4.tmp" -w '%{http_code}' -X POST "$API/sound-generation?output_format=mp3_44100_128" -H 'Content-Type: application/json' \
    --data "$(python3 -I -c 'import json,sys; print(json.dumps({"text": sys.argv[1], "duration_seconds": float(sys.argv[2]), "prompt_influence": float(sys.argv[3])}))' "$1" "$2" "$3")")
  if [ "$code" = 200 ]; then mv "$4.tmp" "$4"; echo "ok  $4"; else echo "ERR $code $4: $(head -c 300 "$4.tmp")"; rm -f "$4.tmp"; fi
}
LINES=(
  "[playful] Everything you get in a QuickWash, faster than it takes to book one. Ready? [excited] Go."
  "Foam and a hand wash. Vacuum: seats, floors, trunk. Glass, inside and out. Tire shine and door jambs. Interior wiped down. Ceramic spray wax."
  "[excited] Ninety-nine bucks. Done, with time to spare."
  "Booking it? Twenty seconds."
  "[warmly] QuickWash. Grab the app."
)
if [ "$VOICE" = laura ]; then LINES=(
  "[excited] Everything you get in a QuickWash, faster than it takes to book one! Ready? Go!"
  "[speaking fast] Foam and a hand wash! Vacuum: seats, floors, trunk! Glass, inside and out! Tire shine and door jambs! Interior wiped down! Ceramic spray wax!"
  "[excited] Ninety-nine bucks. Done, with time to spare!"
  "Booking it? Twenty seconds."
  "[playful] QuickWash. Grab the app!"
); fi
# pickup lines for the reserved slots (credits were exhausted): b3b for both voices, b4 for Laura
PICKUP_B3B="And if you join WashClub? Sixty-nine."
ITEMS=("Foam and a hand wash." "Vacuum: seats, floors, trunk." "Glass, inside and out." "Tire shine and door jambs." "Interior wiped down." "Ceramic spray wax.")
case "$1" in
  vo) for b in 1 2 3 4 5; do for k in $(seq 1 "$T"); do tts "${LINES[$((b-1))]}" "$VD/b${b}_t$k"; done; done ;;
  pickup) for k in $(seq 1 "$T"); do tts "$PICKUP_B3B" "$VD/b3b_t$k"; done
          if [ "$VOICE" = laura ]; then for k in $(seq 1 "$T"); do tts "${LINES[3]}" "$VD/b4_t$k"; done; fi ;;
  items) for i in 1 2 3 4 5 6; do for k in $(seq 1 "$T"); do tts "${ITEMS[$((i-1))]}" "$VD/i${i}_t$k"; done; done ;;
  music) for n in 1 2 3; do sfx "Driving playful upbeat electronic pop instrumental, 128 BPM, punchy kick and claps, bright synth stabs, fast energetic speed-run feel, clean modern commercial music, steady energy throughout, no vocals" 26 0.6 "$A/music/bed$n.mp3"; done ;;
  sfx) sfx "single soft clock tick, short clean mechanical click, dry, no reverb" 0.5 0.8 "$A/sfx/tick.mp3"
       sfx "bright clean bell ding, single short pleasant chime, game show correct answer" 1.2 0.8 "$A/sfx/ding.mp3" ;;
esac
