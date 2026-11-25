#!/usr/bin/env bash
# ElevenLabs audio for reel-orlando (the proxy injects the API key: no auth header; one request at a time; mp3_44100_128;
# on HTTP 429 wait 20 s and retry). Credit budget: <= 2 takes per line (3 for the list), one music generation (+1 retry).
# Usage: tools/gen-audio.sh vo <line 1-4> <take>   -> assets/audio/vo/<open|list|price|cta>_t<take>.mp3
#   line 1 = b1 open, 2 = b2-b7 the service list as one take, 3 = b8 price, 4 = b9 CTA (+ .json alignment, .cost)
#        tools/gen-audio.sh music <n>               -> assets/audio/music/bed<n>.mp3
#        tools/gen-audio.sh stt <path-without-ext>  -> <path>.words.json (Scribe word timings)
set -uo pipefail
cd "$(dirname "$0")/.."
A=assets/audio; API=https://api.elevenlabs.io/v1; VID=TX3LPaxmHKxFdv7VOQHJ   # Liam
LINES=(
  "[cheerful] Orlando, this is the ninety-nine dollar QuickWash. And yeah, we come to you."
  "Foam and a full hand wash. Vacuum: seats, floors, trunk. Glass, inside and out. Tire shine and door jambs. Interior wiped down. And a ceramic spray wax to finish."
  "[excited] All of it, in your driveway. Ninety-nine bucks."
  "Orlando spots are filling up this week. Drop your info below and grab yours."
)
post() { # out-file url body [content-type]  -> echoes the HTTP code; retries on 429
  local code
  for try in 1 2 3 4 5; do
    code=$(curl -sS -D "$1.hdr" -o "$1" -w '%{http_code}' -X POST "$2" -H 'Content-Type: application/json' --data "$3")
    [ "$code" = 429 ] && { echo "429, waiting 20 s" >&2; sleep 20; continue; }
    break
  done
  echo "$code"
}
case "$1" in
  vo)
    N=(x open list price cta); f=$A/vo/${N[$2]}_t$3; [ -s "$f.mp3" ] && { echo "exists $f"; exit 0; }
    body=$(python3 -I -c 'import json,sys; print(json.dumps({"text": sys.argv[1], "model_id": "eleven_v3", "voice_settings": {"stability": 0.5}}))' "${LINES[$(($2-1))]}")
    code=$(post "$f.resp" "$API/text-to-speech/$VID/with-timestamps?output_format=mp3_44100_128" "$body")
    if [ "$code" != 200 ]; then echo "ERR $code $f: $(head -c 300 "$f.resp")"; rm -f "$f.resp"; exit 1; fi
    python3 -I -c 'import json,base64,sys; d=json.load(open(sys.argv[1])); open(sys.argv[2]+".mp3","wb").write(base64.b64decode(d["audio_base64"])); json.dump(d["alignment"], open(sys.argv[2]+".json","w"))' "$f.resp" "$f"
    grep -i -E '^(character-cost|x-character-count|request-id)' "$f.resp.hdr" | tr -d '\r' > "$f.cost"; rm -f "$f.resp" "$f.resp.hdr"; echo "ok $f.mp3 $(cat "$f.cost" | tr '\n' ' ')" ;;
  music)
    f=$A/music/bed$2.mp3; [ -s "$f" ] && { echo "exists $f"; exit 0; }
    body=$(python3 -I -c 'import json; print(json.dumps({"text": "Warm sunny upbeat acoustic pop instrumental, 110 BPM, strummed acoustic guitar, light hand claps, bright ukulele and soft shaker, feel-good Saturday morning in the sun, steady groove throughout, clean modern commercial bed, no vocals", "duration_seconds": 22, "prompt_influence": 0.6}))')
    code=$(post "$f.tmp" "$API/sound-generation?output_format=mp3_44100_128" "$body")
    if [ "$code" = 200 ]; then mv "$f.tmp" "$f"; grep -i -E '^(character-cost|x-character-count)' "$f.tmp.hdr" | tr -d '\r' > "$f.cost"; echo "ok $f $(cat "$f.cost")"; else echo "ERR $code: $(head -c 300 "$f.tmp")"; rm -f "$f.tmp"; fi; rm -f "$f.tmp.hdr" ;;
  stt)
    t=$2; [ -s "$t.words.json" ] && { echo "exists $t"; exit 0; }
    for try in 1 2 3 4 5; do
      code=$(curl -sS -o "$t.words.json" -w '%{http_code}' -X POST $API/speech-to-text -F model_id=scribe_v1 -F timestamps_granularity=word -F "file=@$t.${3:-mp3}")
      [ "$code" = 429 ] && { sleep 20; continue; }; break
    done
    [ "$code" = 200 ] && echo "ok $t" || { echo "ERR $code $t: $(head -c 200 "$t.words.json")"; rm -f "$t.words.json"; } ;;
esac
