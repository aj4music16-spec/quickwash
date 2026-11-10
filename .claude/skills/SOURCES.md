# Installed skills — sources

Copied from these repositories (skill folders only; demos, tests and node_modules excluded).
Each was scanned for risky patterns before install. Notes are listed beside each source.

| Skills | Source | License |
|---|---|---|
| hyperframes, hyperframes-cli, hyperframes-registry, media-use, figma, remotion-to-hyperframes, reverse-any-video, slideshow, style-sampling, motion-doctrine, cut-the-curve, seam-craft, captions-overlay, changelog-video, oversized-cursor | github.com/heygen-com/hyperframes | Apache-2.0 |
| remotion-* (13) | github.com/remotion-dev/skills | none in repo |
| cartoon-3d-short | github.com/mromidev/claude-animated-shorts | MIT |
| cinematic-director | github.com/wuwangzhang1216/DirectorSKILL | MIT |
| shader-art-coding | github.com/gokayfem/shader-skills | MIT |
| webgpu-threejs-tsl | github.com/dgreenheck/webgpu-claude-skill | none in repo |
| pixelfx | github.com/patch-gg/pixelfx | MIT |
| text-to-speech, sound-effects, music, speech-to-text, dubbing, voice-changer, voice-isolator, agents, realtime, speech-engine, onboarding, setup-api-key | github.com/elevenlabs/skills | MIT |
| seedance-storyboard-generator | github.com/liangdabiao/Seedance2-Storyboard-Generator | none in repo |
| short-drama, short-drama-* (12) | github.com/zenstory-ai/drama-skills | MIT |

Not installed: github.com/bitwize-music-studio/claude-ai-music-skills (53 skills, CC0). It is a
full Suno album workflow whose generic names (help, setup, test, resume, rename, configure)
would trigger on unrelated requests.

Notes:
- ElevenLabs skills need an ElevenLabs API key; their CLI installs via a vendor `curl | sh`
  script — ask before running it.
- pixelfx may suggest installing the patch.gg CLI — ask before running it.
- HyperFrames `media-use` scripts send coarse usage telemetry to PostHog; set `DO_NOT_TRACK=1`
  (or `HYPERFRAMES_NO_TELEMETRY=1`) to opt out.
