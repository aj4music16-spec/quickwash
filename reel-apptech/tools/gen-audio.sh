#!/usr/bin/env bash
# ElevenLabs audio for reel-apptech (proxy injects the API key; no auth header here). Free plan: mp3_44100_128, one request at a time.
# Usage: tools/gen-audio.sh [music|vo|sfx|all]
set -uo pipefail
cd "$(dirname "$0")/.."
A=assets/audio; API=https://api.elevenlabs.io/v1
post() { # url json out
  local code; code=$(curl -sS -o "$3.tmp" -w '%{http_code}' -X POST "$1" -H 'Content-Type: application/json' --data "$2")
  if [ "$code" = 200 ]; then mv "$3.tmp" "$3"; echo "ok  $3"; else echo "ERR $code $3: $(head -c 300 "$3.tmp")"; rm -f "$3.tmp"; return 1; fi
}
music() {
  local P="Clean modern upbeat tech product commercial music bed, soft synth plucks, light electronic beat, 116 BPM, bright and optimistic, steady energy, polished keynote style, no vocals"
  for n in 1 2 3; do post "$API/sound-generation?output_format=mp3_44100_128" "{\"text\": \"$P\", \"duration_seconds\": 22, \"prompt_influence\": 0.6}" "$A/music/bed$n.mp3"; done
}
vo() {
  local V=iP95p4xoKVk53GoZ742B
  local L=("Your car wash is now an app." "Pick your car, pick a service, pick a time. Booked in twenty seconds." "Every car in one garage." "Then we come to you." "Home, the office, the gym. Wherever you park." "QuickWash. Download the app.")
  for i in 1 2 3 4 5 6; do
    [ -s "$A/vo/l$i.mp3" ] && continue
    post "$API/text-to-speech/$V?output_format=mp3_44100_128" "{\"text\": \"${L[$((i-1))]}\", \"model_id\": \"eleven_multilingual_v2\", \"voice_settings\": {\"stability\": 0.4, \"similarity_boost\": 0.8, \"style\": 0.4}}" "$A/vo/l$i.mp3"
  done
}
sfx() {
  post "$API/sound-generation?output_format=mp3_44100_128" '{"text": "soft clean UI tap click, single short digital touch sound, minimal, no reverb", "duration_seconds": 0.5, "prompt_influence": 0.8}' "$A/sfx/tap.mp3"
  post "$API/sound-generation?output_format=mp3_44100_128" '{"text": "soft airy whoosh transition, short, smooth, clean modern UI swoosh", "duration_seconds": 0.8, "prompt_influence": 0.8}' "$A/sfx/whoosh.mp3"
  post "$API/sound-generation?output_format=mp3_44100_128" '{"text": "bright pleasant success chime, two soft notes, modern app confirmation sound", "duration_seconds": 1.0, "prompt_influence": 0.8}' "$A/sfx/success.mp3"
}
case "${1:-all}" in music) music;; vo) vo;; sfx) sfx;; all) vo; music; sfx;; esac
