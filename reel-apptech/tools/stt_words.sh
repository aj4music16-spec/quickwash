#!/usr/bin/env bash
# Word onsets for chosen VO takes via ElevenLabs Scribe (speech-to-text, word timestamps). eleven_v3's own
# with-timestamps alignment drifts by up to ~0.4 s on these takes, so the cue sheet uses Scribe's times.
# Usage: tools/stt_words.sh assets/audio/vo3/liam_b2_t2 [...]  -> <take>.words.json
set -uo pipefail
cd "$(dirname "$0")/.."
for t in "$@"; do
  [ -s "$t.words.json" ] && continue
  code=$(curl -sS -o "$t.words.json" -w '%{http_code}' -X POST https://api.elevenlabs.io/v1/speech-to-text \
    -F model_id=scribe_v1 -F timestamps_granularity=word -F "file=@$t.mp3")
  [ "$code" = 200 ] && echo "ok  $t" || { echo "ERR $code $t"; rm -f "$t.words.json"; }
done
