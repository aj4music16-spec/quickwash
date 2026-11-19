---
name: timeline-edit-reel
description: "Build a vertical reel in the 'edit shown while it plays' style: full-bleed footage with an editing-app timeline overlaid near the top (duration label, filmstrip scrolling under a fixed white playhead, trim handles, '+' tile), clips separated by black beats, hard cuts on the music's beats, then a brand end card. Use when asked for a reel 'like the timeline/Edits-style reference', 'with the editor timeline on screen', 'clips separated by black beats', or for a process / before-after montage (detailing, renovation, cleaning, build-ups) that should feel hand-edited. Ships a HyperFrames overlay sub-composition, a spec-driven project builder (trim, thumbnails, beat grid, loudness, index.html) and a beat detector. [timeline, filmstrip, playhead, edits, capcut, black-beat, montage, before-after, process, reel, vertical, beat-sync, hard-cut, quickwash]"
metadata:
  internal: true
---

# Timeline-edit reel

Authored in-house from a client-supplied reference reel (measurements in `references/measurements.md`).
Load `/hyperframes` first for the render contract; this skill is the style and the builder.

## What the style is, and why it works

The film shows its own edit. An editor timeline sits at the top of the frame: a duration label ("0.9s"), a
filmstrip of clip thumbnails scrolling right-to-left under a fixed white playhead, white trim grips on each
clip, a "+" at the end. Between clips the strip has **black tiles**; when the playhead crosses one the whole
picture is black, and the instant the next clip's edge reaches the playhead the footage hard-cuts in.

- **Anticipation.** The viewer sees the next clip coming in the strip before it plays: every cut is
  announced, and the black beat is a held breath, so each shot lands harder than in a plain montage.
- **Rhythm.** Clip / black / clip / black on the beat is a metronome the eye can read with the sound off.
- **Process honesty.** "Someone made this, shot by shot" suits before/after and work-in-progress content; the
  label is a small reading hook that changes every beat.
- **Calm footage, busy frame.** The UI supplies the motion; the shots can be still and simple.

## Anatomy (1080x1920; measured proportions, see references/measurements.md)

| Part | Spec |
|---|---|
| Label | white Inter 700, 64 px, centred, top 208 px; one decimal + "s" (`decimal` "." or ","); soft 10 px text-shadow |
| Strip panel | x 102–978 (0.81 W, centred on the playhead), y 372–526 (154 px), #111113, r 12 |
| Tiles | inset 10 px (134 px tall), 6 px apart, r 10; clip tiles = repeated 9:16 thumbnails (75x134); gap tiles #0d0b12 |
| Playhead | 8 px white bar at x 540, panel height + 5 px over each edge, slight shadow; never moves |
| Trim grips | 43x44 white, r 12, 5x20 black bar; on both outer edges of every footage tile |
| "+" tile | 71x71 white, r 16, fixed at the panel's right end, above the tiles |
| Scroll | linear, 372 px per second of timeline (0.345 W/s); the strip shows ≈2.35 s, 1.2 s ahead |
| Scrim | top 640 px gradient, black 34% -> 0, only over footage (legibility on bright skies/white cars) |

Everything sits between y 208 and 526: clear of the 168 px top bar of Reels/TikTok and far above the bottom
caption/handle zone (> 1330 px) and the right action rail, so the footage's subject keeps the middle of the frame.

## Timing rules

- **Hard cuts only.** No fades, zooms, speed ramps or transitions on footage. The scroll is linear.
- **Beat grid.** Every boundary sits on a beat of the bed (`scripts/beats.py` finds BPM + onsets; the builder
  starts the bed on a strong onset so beat k is at k x period, then snaps each boundary to a frame).
- **Lengths.** Reference: clips 0.6–1.4 s, gaps 0.6–1.0 s (gap ≈ 0.65 x clip), one clip+gap pair ≈ one bar.
  At 110–130 BPM: clip 2 beats (3 for the opener/hero), gap 1 beat; a 2-beat gap before the reveal is a
  good variation. Below ~90 BPM use clip 2 / gap 1 too, it just breathes more.
- **How many clips.** Clips ≈ (N − end card) / (clip + gap). 12–14 s at 128 BPM with a 2.8 s end card ≈ 8
  clips. Fewer than 6 and the rhythm never establishes; more than ~10 per 15 s and the black stops reading as a beat.
- **Frame 0 is footage, never black** (the thumbnail): start on a clip, not a gap.
- The label is static per segment and swaps exactly on the boundary; gaps get a duration label too.

## Footage

- Calm, locked-off or slow, wide or medium shots with **one readable action** (foam on, rinse, scrub, door
  opens). Each must read in under a second: no tight abstract close-ups, no shots whose payoff is late.
- Story order: before -> arrival -> process -> result. The strip itself previews it.
- Grade: muted and consistent across clips (the reference is warm and desaturated); grade at trim time with
  `npx hyperframes media-treatment` (`/media-use`), never with CSS filters. Already-graded footage stays as is.
- Plates, faces of the public, other brands' logos: blur before building (the QuickWash library already is).
- Only footage you own or are licensed to use. Never the reference creator's footage.

## Brand adaptation (QuickWash pattern)

- **Words in the label** at key moments instead of a duration: `"label": "before"` on the opener, `"after"`
  on the hero, the brand name on the end card. Keep it to one or two words, lower case for states.
- **End card after the last clip**, cut in on a beat. The strip keeps scrolling over it with an end tile (a
  white tile repeating the logo, like a thumbnail of the card), and the label turns brand navy on white.
  The card's own content lives below the strip (logo ~620–1040, headline ~1070, CTA ~1260).
- A logo shot inside the montage (the branded van) brands the middle without a supered logo.
- Brand orange #FF6600 on white is 2.9:1, so text uses #E85D00 (`accent_text`); keep the true orange for the logo.
- Price / offer: as a label word on the hero ("$99") or a line on the end card, never a sticker over footage.

## Don'ts

- Don't copy the platform's chrome (status bar, like rail, "Made with ..." pill, username, progress bar) or
  any app's exact icons/branding; the overlay here is a generic editor timeline drawn from scratch.
- No third-party footage, music or fonts from the reference.
- Don't move the playhead, ease the scroll, animate the label, or add transitions; the restraint is the style.
- Don't put text in the gap frames besides the overlay (the black is the beat).
- Don't add captions/VO by default; if VO is needed, its captions go low (y 1150–1330), never near the strip.

## Files

- `assets/timeline-overlay.html` — HyperFrames sub-composition (`timeline`). Renders label, strip, tiles,
  grips, "+", playhead from `SPEC` (between `/*SPEC*/ ... /*ENDSPEC*/`); exposes it as `window.__timelineEdit`.
  Geometry in `G`. Deterministic: one linear tween + `tl.set` label swaps.
- `assets/gsap.min.js` — GSAP 3.15 (copied into each project's `assets/vendor/`).
- `scripts/build_timeline.py` — spec -> trimmed 30 fps clips, thumbnail strips (ffmpeg `tile`), bed trimmed to
  a beat and normalised (two-pass loudnorm, -14 LUFS / -1.5 dBTP), `index.html`, `compositions/timeline.html`,
  `compositions/end.html`, `package.json`, `hyperframes.json`, `timeline.json`. `--skip-media` rewrites HTML only.
- `scripts/beats.py` — tempo, beat phase and onsets of any audio/video (numpy only).
- `references/measurements.md` — the reference's numbers.

## Spec format (`timeline.spec.json`; paths relative to the spec)

```json
{
  "title": "QuickWash - timeline-edit demo",
  "fps": 30, "width": 1080, "height": 1920, "decimal": ".",
  "music": { "file": "../reel-race/assets/audio/music/bed2.mp3", "start": "auto", "min_start": 1.0,
             "lufs": -14, "true_peak": -1.5, "fade_out": 0.9 },
  "grid": { "clip_beats": 2, "gap_beats": 1 },
  "overlay": { "px_per_s": 372 },
  "clips": [
    { "id": "c1", "file": "../reel-hp/assets/footage/h4-dirty-door.mp4", "in": 0.0, "label": "before" },
    { "id": "c2", "file": "../reel-hp/assets/footage/o1-van-logo.mp4", "in": 0.3 },
    { "id": "c7", "file": "../reel-hp/assets/footage/s07-clean-dash.mp4", "in": 0.4, "gap_after_beats": 2 },
    { "id": "c8", "file": "../reel-hp/assets/footage/s09-hero-side.mp4", "in": 0.5, "beats": 3, "label": "after" }
  ],
  "end_card": { "beats": 6, "label": "QuickWash", "logo": "../reel-race/assets/app/logo.png", "brand": "QuickWash",
                "line": "The car wash that|comes to you.", "accent_word": "you.", "sub": "Book in the QuickWash app",
                "navy": "#000099", "accent": "#FF6600", "accent_text": "#E85D00", "sub_at": 0.16 }
}
```

- Per clip: `file`, `in` (s into the source), `beats` (default `grid.clip_beats`) or `dur` (s, with
  `"timing": "seconds"` or no music), `gap_after_beats` / `gap_after`, `label`, `gap_label`, `note` (HTML comment).
  The last clip has no gap unless you give one.
- `music.start`: `"auto"` = first onset of strength ≥ `min_strength` (0.6) after `min_start`; or a number
  (s into the file, put it on a beat). `bpm` overrides detection. No `music` -> seconds-based timing, silent film.
- `end_card`: `beats`/`dur`, `label`, `label_color`, `tile_color` (default white), `line` (`|` = line break),
  `accent_word`, `sub`, `sub_at`. Omit it for no end card.

## Workflow

1. Pick the bed; run `python3 -I .claude/skills/timeline-edit-reel/scripts/beats.py <bed>`: want a clear grid
   (strong onsets every 2 beats) and 110–130 BPM. Several beds? Prefer the one whose onsets are on-beat.
2. Contact-sheet the footage (`ffmpeg ... -vf scale=180:320,tile`), pick 6–9 calm shots in story order and
   note each one's in-point (the moment its action is clearest for ~1 s).
3. Write `<project>/timeline.spec.json`; run
   `python3 -I .claude/skills/timeline-edit-reel/scripts/build_timeline.py <project>/timeline.spec.json`.
   It prints the schedule; adjust beats/labels and re-run (`--skip-media` when only labels/overlay changed).
4. `cd <project>; HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 npx --yes hyperframes@0.9.27 check` -> 0 errors.
5. `npx --yes hyperframes@0.9.27 snapshot --at <clip>,<gap>,<label change>,<end>` and look: label legible on the
   brightest shot, frame 0 not black, plates unreadable, the end tile visible.
6. `npx --yes hyperframes@0.9.27 render --quality delivery --max-bitrate 12M -o ../dist/<name>.mp4`; verify
   frames, `ebur128` (≈ -14 LUFS, TP ≤ -1) and that black runs start/end on the scheduled frames.
7. Write `CREDITS.md` in the project (footage, music, logo, fonts).

Proven on `reel-timeline/` (QuickWash, 8 clips, 128 BPM, 14.03 s).
