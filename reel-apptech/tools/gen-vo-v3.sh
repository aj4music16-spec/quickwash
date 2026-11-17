#!/usr/bin/env bash
# v2 voiceover: ElevenLabs eleven_v3 with character timestamps (proxy injects the key; no auth header; one request at a time).
# Usage: tools/gen-vo-v3.sh <voice-name> <voice-id> <takes>    e.g. tools/gen-vo-v3.sh liam TX3LPaxmHKxFdv7VOQHJ 3
# Writes assets/audio/vo3/<voice>_b<N>_t<K>.mp3 and .json (alignment). Existing takes are skipped.
set -uo pipefail
cd "$(dirname "$0")/.."
NAME=$1; VID=$2; TAKES=${3:-3}; OUT=assets/audio/vo3; mkdir -p "$OUT"
LINES=(
  "[excited] Okay, your car wash? It's an app now."
  "Pick your car. Pick your wash. Pick a time. And... booked. About twenty seconds."
  "Every car you own? Right here. Put 'em on repeat if you want."
  "Then we pull up to you."
  "Home. The office. The gym. Even the golf course. Wherever you're parked."
  "[warmly] QuickWash. Go grab the app."
)
for b in 1 2 3 4 5 6; do
  for k in $(seq 1 "$TAKES"); do
    f="$OUT/${NAME}_b${b}_t${k}"; [ -s "$f.mp3" ] && continue
    body=$(python3 -I -c 'import json,sys; print(json.dumps({"text": sys.argv[1], "model_id": "eleven_v3", "voice_settings": {"stability": 0.5}}))' "${LINES[$((b-1))]}")
    code=$(curl -sS -o "$f.resp" -w '%{http_code}' -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VID/with-timestamps?output_format=mp3_44100_128" -H 'Content-Type: application/json' --data "$body")
    if [ "$code" != 200 ]; then echo "ERR $code $f: $(head -c 300 "$f.resp")"; rm -f "$f.resp"; continue; fi
    python3 -I -c 'import json,base64,sys; d=json.load(open(sys.argv[1])); open(sys.argv[2]+".mp3","wb").write(base64.b64decode(d["audio_base64"])); json.dump(d["alignment"], open(sys.argv[2]+".json","w"))' "$f.resp" "$f" && rm -f "$f.resp"
    echo "ok  $f.mp3"
  done
done
