# SPEC — "The $99 Tag" (QuickWash · High Point NC · new-market launch · paid social 9:16)

Picked from STORYLINES.md (A). Every line marked **[CLIENT TO CONFIRM]** depends on QuickWash
confirming it serves High Point (it is not on the public service-area list; see RESEARCH.md).

```text
GOAL:    A High Point driver scrolling with the sound off learns in 11 s that $99 buys six real
         jobs on their car in their own driveway, and taps through to book in the app.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, H.264 + AAC.
TIME:    19.8 s x 30 = 594 frames. 100 BPM = 18 frames per beat, 72 per bar; 33 beats.
         Every cut lands on a downbeat. Services start beat 6 (f108); payoff beat 18 (f324);
         end card beat 28 (f504), complete by f534, held 2.0 s to f594.
LOOK:    Medium = real iPhone daylight footage + one printed paper object (a showroom hang tag).
         Ground: the footage itself, full bleed 1080x1920, every shot. Grade: contrast +8,
           saturation +10, white balance matched shot to shot to within ±200 K, no vignette, 0% grain,
           no blur, no speed ramps. If a clip is landscape, recompose to 9:16 with the action in the
           centre-right column (x 420-1000), never letterboxed.
         Ink: white #FFFFFF type on navy #000099 slabs (slab = flat rectangle, 24 px padding,
           12 px darker #000470 thickness edge on the bottom). Navy #000099 print on the tag.
         Accent: orange #FF6600 ONLY on the tag's grommet ring, the rims of the punch holes,
           the words "ALL SIX" on the tag's back, and "$99" on the end card. Nowhere else.
         Display: League Gothic, caps, tracking 0, line-height 0.9. On-screen lines set left-aligned
           at x 72, in 1 or 2 rows justified to one width <= 780 px (right edge <= 852 px),
           font-size 150-190 px (never under 120 px). Body: Inter 700/800, never under 28 px.
         Tag price: "$99" League Gothic 300 px navy, tracking -1%: the largest, highest-contrast
           element in every frame it is in. Nothing else on screen exceeds 190 px type.
         Depth: one hard offset shadow on the tag only: 10 px x, 14 px y, 0 blur, rgba(0,0,4,0.30).
           Slabs get the 12 px thickness edge, no shadow.
         Safe area: all words inside y 168-1330 and x 72-860. Below 1330 only footage. Nothing but
           footage under the right action rail (x > 900).
OBJECTS: HANG TAG — white card stock #FFFFFF, 440 x 620 px, top corners clipped 56 px at 45°
           (classic furniture hang-tag silhouette), 2 px #D8DCE6 inner edge line 14 px inside the
           border; orange #FF6600 grommet ring 52 px outer / 20 px hole, centred 48 px below the top
           edge; cotton string 3 px #EFE9DC from the grommet straight up out of frame. Placed
           x 80-520, y 220-840; the string runs y 0-268 (above 168 it is decoration only).
           Front print: "$99" (300 px) at y 330-560; under it Inter 800 30 px navy, 2 rows:
           "STANDARD-SIZE" / "VEHICLE". Bottom edge: six punch positions, 30 px circles,
           56 px apart, centred, 70 px above the bottom edge; a punched hole shows the footage
           through it with a 3 px orange rim.
           Back print (shown from S9): "ALL SIX" League Gothic 120 px orange over "$99" 300 px navy;
           the six holes, all punched, mirrored.
         NAVY SLAB — the line carrier, flat #000099, width = text + 48 px.
         LOGO + APP-STORE BADGES — supplied by the build; badges at their official artwork,
           300 x 100 px each, untinted.
MOTION:  Cuts: hard, on the downbeat, no transitions between footage shots.
         Lines: each row arrives from 40 px below, opacity 0->1 in 1 frame (binary), position on
           power4.out over 5 frames; a second row starts 2 frames later and travels 26 px.
           Lines leave with the cut (hard), never fade. A landed line never moves.
         Punch (S3-S8, one per shot, on the shot's first frame): hole appears in 1 frame; the tag
           kicks 6 px down and returns over 4 frames, power2.out (causal — the punch hits it).
           The tag never sways, breathes or drifts at any other time.
         Flip (S9, f324-f336): tag rotates Y 0->180° over 12 frames, power3.inOut, scaling 1.00->1.20
           from the grommet (ends x 80-608, y 220-964); front swaps to back at 90°.
         Footage moves: whatever the camera did. One added move: S9 hero push, scale 1.00->1.05
           over 72 frames, power2.out.
         End card (f504): navy #000099 wipes up from the bottom edge to the top in 12 frames,
           power3.inOut; the tag is pulled up out of frame on its string in the same 12 frames,
           power4.in. Logo slams scale 1.5->1.0 in 5 frames power4.out at f516; line rows at f522;
           badges at f528 (both together); confirm line at f531. Complete f534. Hold still to f594.
SHOTS:   table below.
BANNED:  dark navy void with small floating things (the end card is full-frame navy with large
         elements, filled edge to edge) · glow, bloom, lens flare, particles, bubbles added in post ·
         purple/blue gradients, glass cards · pill chips, "01/02" numbered labels, mono caps labels ·
         everything centred (tag and lines sit left; action sits centre-right) · fade-and-slide-up
         entries · text moving while read · idle sway on the tag · logo docked in a corner ·
         three cards in a row / a bulleted service list · a title over a dimmed screenshot ·
         stock or generated imagery, actors · comparative price claims ("half the price of …") ·
         allergy or paint-damage claims · "Introducing", "effortless", "seamless", "unlock",
         "game-changer", "revolutionize", "in seconds" · any NJ/NY plate, street sign or
         storefront legible in a clip.
QA:      f0     thumbnail: foam on paint, tag reading $99, WASHED IN YOUR DRIVEWAY — readable at 360 px wide.
         f60    NOW IN HIGH POINT on a slab, van in frame, no NJ/NY plate legible.
         f110   first hole punched, FOAM + HAND WASH, hands with a mitt in foam.
         f146 / f182 / f218 / f254 / f290   holes 2-6 punched; each line matches its footage.
         f322   six holes punched; $99 still the largest element.
         f330   flip mid-turn (no text mirrored on screen).
         f340   tag back: ALL SIX (orange) over $99; hero car; no slab line.
         f400   NO NEED TO BE HOME; no customer in frame.
         f455   VETTED, TRAINED, INSURED over the detailer.
         f534   end card complete: logo, BOOK IN THE APP, both badges, confirm line, $99 in orange.
         every frame: no word outside y 168-1330 or right of x 860; nothing in the right rail.
         sound off: the words alone tell the pitch; the pictures alone tell it too.
```

## Shots

Footage categories (the editor's log): **FOAM** foam / hand wash · **VAC** vacuuming ·
**GLASS** glass · **TIRES** tires (and door jambs if logged there) · **WIPE** interior wipe-down ·
**WAX** spray wax · **HERO** finished car · **CREW** the detailer and the van.

| # | Frames | Time (s) | Footage (fallback) | Hero move | On-screen line (window) | Sound | Hand-off |
|---|---|---|---|---|---|---|---|
| S1 | 0–54 | 0.00–1.80 | FOAM: foam pre-soak sheeting down a dark door or hood, close (fb: FOAM rinse, or HERO wet paint) | Footage only; tag and line already on frame 0 | Tag: **$99** · Line: WASHED IN YOUR DRIVEWAY (f0–54) | Foam hiss from the clip; guitar riff from f0, kick enters f18 | Hard cut on beat 3 |
| S2 | 54–108 | 1.80–3.60 | CREW: van parked at a house, detailer stepping out or unloading (fb: CREW detailer carrying kit; then HERO) | Detailer walks toward camera | NOW IN HIGH POINT (f56–108) **[CLIENT TO CONFIRM]** | Van door slide from the clip, riff continues | Cut on beat 6 to the first punch |
| S3 | 108–144 | 3.60–4.80 | FOAM: wash mitt passes through foam, hands only (fb: another FOAM clip) | Punch 1 | FOAM + HAND WASH (f108–144) | Punch *chunk* on f108 | Cut, punch |
| S4 | 144–180 | 4.80–6.00 | VAC: nozzle across seat or trunk floor (fb: VAC any angle; if no trunk shot, line stays — trunk is in the package) | Punch 2 | VACUUM, TRUNK TOO (f144–180) | *Chunk*; vacuum whine from the clip, ducked −12 dB | Cut, punch |
| S5 | 180–216 | 6.00–7.20 | GLASS: towel wipe across a windshield, ideally shot from inside (fb: GLASS exterior) | Punch 3 | GLASS, BOTH SIDES (f180–216) | *Chunk*; towel squeak | Cut, punch |
| S6 | 216–252 | 7.20–8.40 | TIRES: tire-shine applicator round a sidewall, or a door-jamb wipe (fb: HERO tight on a shined tire) | Punch 4 | TIRE SHINE + JAMBS (f216–252) | *Chunk*; spray pump click | Cut, punch |
| S7 | 252–288 | 8.40–9.60 | WIPE: cloth along dashboard / console (fb: WIPE door panel) | Punch 5 | DASH WIPED DOWN (f252–288) | *Chunk* | Cut, punch |
| S8 | 288–324 | 9.60–10.80 | WAX: spray wax misting onto paint, towel buffing (fb: HERO paint reflection close) | Punch 6 — all six holes now open | CERAMIC-INFUSED WAX (f288–324) | *Chunk*; spray hiss; riff resolves on f323 | Cut on beat 18 to the payoff |
| S9 | 324–396 | 10.80–13.20 | HERO: the finished car, best reflection, wide enough to read as a whole car (fb: WAX last buff pull-back) | Tag flips (f324–336) and grows to 1.2×; footage push 1.00→1.05 | Tag back: **ALL SIX** / **$99** (f336–396) — no slab line | Full band: kick, bass, guitar; a single bell-like hit on f336 | Cut on beat 22 |
| S10 | 396–450 | 13.20–15.00 | CREW: detailer working alone at the car outside a house, no customer (fb: FOAM or TIRES wide with the house behind) | Detailer works; tag stays, back side out | NO NEED TO BE HOME (f398–450) | Band continues | Cut on beat 25 |
| S11 | 450–504 | 15.00–16.80 | CREW: detailer close, kit or van in background (fb: FOAM hands close) | Detailer turns to camera or lifts kit | VETTED, TRAINED, INSURED (f452–504) | Band; riff turnaround | Navy wipes up, tag pulled up and out |
| S12 | 504–594 | 16.80–19.80 | End card (no footage after f516) | Navy wipe up (f504–516); logo slams in (f516); built by f534; holds | Logo · BOOK IN THE APP · App Store + Google Play badges · "**$99** QuickWash · standard-size vehicle" · "Now booking High Point & the Triad" **[CLIENT TO CONFIRM]** | Punch *chunk* on the logo; held guitar chord; last kick f576; ring out to f594 | — |

### Why the rhythm works without a list
The six services are six full-frame shots, 1.2 s each, each with its own footage and its own
three-word line; the only thing that accumulates is the row of holes in the tag — a tally the eye
reads without words. Six punches in 7.2 s, then the tag turns over and the sum is printed on its
back: ALL SIX / $99. The lines hold 1.2 s, 0.2 s under story.md's 0.3 s/word guide for three words;
each is reinforced by the shot behind it. If a muted reading test fails, cut each line to two words
(FOAM WASH · VACUUM · BOTH-SIDE GLASS · TIRE SHINE · DASH WIPE · CERAMIC WAX) rather than slowing the cut.

### Layout per frame (y in px)
- 0–168: footage and the tag string only.
- 220–840 (S9 onward 220–964): the tag, x 80–520 (x 80–608 after the flip).
- 1000–1300: the line slab, x 72–852, 1 or 2 rows. In S9 the slab is absent.
- 1330–1920: footage only.

## Sound
100 BPM. Finger-picked Piedmont-blues-style acoustic guitar riff (a nod to the region; no named
artist, no claim) over a dry kick and upright bass from f18; the hole-punch *chunk* on f108, 144,
180, 216, 252, 288 and f516, mixed −3 dB under the kick; clip audio (foam, vacuum, spray) kept at
−12 dB under the bed. Free option: a library or generated instrumental cleared for paid social;
paid option: catalog music. Mastered to −14 LUFS integrated, true peak −1 dBTP.

## Optional voiceover (33 words, only if the client records one)
On-screen text works with sound off; the voice never repeats a screen line word for word.

| Window | VO |
|---|---|
| f0–54 (0.0–1.8 s) | "Ninety-nine dollars." |
| f54–108 (1.8–3.6 s) | "QuickWash is in High Point." **[CLIENT TO CONFIRM]** |
| f108–324 (3.6–10.8 s) | "Foam, hand wash, vacuum, glass, tires, dash, and a spray wax that lasts a month." |
| f396–504 (13.2–16.8 s) | "You don't have to be home." |
| f504–594 (16.8–19.8 s) | "Book it in the app." |

Words: 2 + 5 + 15 + 6 + 5 = 33. Silence under the S9 payoff lets the flip land.

## Sources for every claim

| On screen | Source |
|---|---|
| $99, standard-size vehicle | quickwashtech.com, QuickWash package (checked 2026-11-12) |
| Washed in your driveway | Site: mobile service; vans bring water and power |
| Foam + hand wash · vacuum, trunk too · glass, both sides · tire shine + jambs · dash wiped down · ceramic-infused wax | Site package list: Precision Hand Wash & Foam Pre-Soak; Light Interior Vacuum (Seats, Floors, Trunk); Window & Glass Cleaning (In & Out); Tire Shine & Door Jamb Detail; Interior Wipe-Down (Dashboard, Console, Doors); Ceramic-Infused Spray Wax (1-Month Protection) |
| No need to be home | Site: you don't need to be present as long as there's access to the car |
| Vetted, trained, insured | Site: detailers are "vetted, trained, and insured" |
| Book in the app | Site: booking and payment in the app |
| Now in High Point / Now booking High Point & the Triad | **Not on the site. Client must confirm** (RESEARCH.md flag) |
| The hang tag | Creative device drawn from High Point's furniture-market identity (RESEARCH.md); makes no claim |

## As built (2026-11-12)

Rendered to `/home/user/quickwash/dist/quickwash-highpoint-99.mp4`: 1080x1920, 30 fps, 594 frames, H.264 + AAC 48 kHz.
Every cut, punch, flip and end-card beat lands on the frame given above. Deviations:

- **Line type.** The SPEC's own numbers cannot all hold: at >=150 px no line fits one 732 px row (x 96-852 inside the
  slab padding), and two rows justified to one width would need row sizes outside 150-190 px or a slab taller than
  the 1000-1300 band. Built as: every slab line is two left-aligned rows of League Gothic 150 px (ragged right, not
  justified), one slab 24 px padding, y 1000-1318 + 12 px edge to 1330. Widest row: VETTED, TRAINED, (730 px, slab
  right edge 850). End card BOOK IN THE APP is one row at 168 px.
- **Stand-in footage** (the log has no vacuum, wipe-down, glass-cleaning or tire-dressing action, and no labelled
  wax): S4 VACUUM = slow push over the clean footwell (IMG_6436); S5 GLASS = windshield pressure-rinse, wiper raised
  (IMG_6397); S6 TIRES = foam blasted off the wheel (IMG_6386); S7 DASH = door opens on the clean dash (IMG_6439);
  S8 WAX = unlabelled yellow-bottle mist over the hood (IMG_6393). Lines are unchanged; no text claims a shot shows
  more than it does.
- **S1** uses IMG_0012 (foam sheeting off black paint, plate-free), not the log's hook pick IMG_6398, which carries a
  readable plate and is a rinse rather than the "foam sheeting down" the SPEC asks for.
- **S2** has no van arrival in the footage: the detailer at a black SUV in a house driveway (IMG_0012_1_13); the
  open van is at the far left, mostly under the tag.
- **S3** IMG_0012_1_21 (green mitt in foam on the rear bumper) instead of 1_22, whose mitt sat behind the slab.
- **S9** IMG_6432 (dry, finished front three-quarter, best gloss) reads as the front of the car, not the whole car;
  IMG_6409 shows the whole car but still with suds on the paint.
- **Plates**: tracked box blur (ffmpeg crop+boxblur+overlay, centre interpolated from keyframes read every 0.3-0.4 s,
  box 30-60% larger than the plate) on S2 (X39-RVK, IMG_0012_1_13), S5 (485 7752, IMG_6397), S8 (485 7752, IMG_6393),
  S10 (X39-RVK, IMG_0012_1_12). Checked on 3 frames each: unreadable. S3's file holds a partial "39" plate fragment
  in its trailing 0.5 s handle only (source 2.8-3.0 s), never on screen.
- **Grade**: one uniform mild ffmpeg eq (contrast 1.05, saturation 1.08) in the trim step; no per-shot white-balance
  matching (May suburban and July city footage differ in colour; not corrected).
- **Flip**: rotateY about the grommet axis and scale about the grommet, plus a +44/+9.6 px shift in the same 12
  frames so the tag lands exactly on x 80-608, y 220-964. At f330 the tag is edge-on (invisible), so no mirrored text.
- **End card**: logo shown in a 600 px white rounded tile (the supplied PNG has a white ground); the Google Play
  badge is fitted inside its 300x100 box (its artwork is 3.375:1, so it renders 300x89).
- **Sound**: synthesized (tools/soundtrack.js). Natural clip sound kept on S1, S6 and S11 at data-volume 0.25 (-12 dB).
  No VO.
- **Check warnings kept**: nested_media_start_basis_ambiguous (the media starts are composition-local on purpose),
  timeline_track_too_dense (six line clips in the services scene is the SPEC's shot group), contrast_aa_failure on
  ALL SIX (#FF6600 on white is 2.94:1; the SPEC fixes the brand orange; 120 px display type).

## Overlay v2 (client feedback, 2026-11-12) — supersedes LOOK's Ink, Display, Depth and the slab/tag numbers above

Story, timing, cuts, footage, sound and end-card content are unchanged.
- **Lines**: no slabs. White Poppins 700, mixed case, 84 px, letter-spacing -0.01em, line-height 1.1, left x 72,
  max width 800 px (wraps to two lines only past 800: "Washed in your driveway", "Ceramic-infused wax",
  "No need to be home", "Vetted, trained, insured"). Text box bottom at y 1300 (baseline ~1283), so wrapped lines
  grow upward. Legibility: text-shadow 0 3px 18px rgba(0,0,10,.55), 0 1px 2px rgba(0,0,10,.5), plus a full-width
  scrim div (y 980-1920, linear-gradient 0 / .42 at 60% / .55) on every footage shot, S9 included. Arrival: binary
  opacity (the clip window), 5-frame power4.out from 24 px below; leaves with the cut.
  Exception: "Foam + hand wash" (S3) sits 100 px higher (text box bottom y 1200) because at y 1300 it covered the mitt.
- **Tag**: whole tag at 0.62 (card ~273 x 384), pinned top-left x 72, y 200; $99 ~186 px; STANDARD-SIZE / VEHICLE at
  46 card px = 28.5 px on screen; six holes, punch kick 6 px on screen. Shadow 6 x 8 px, rgba(0,0,4,.22). S9 flip
  (f324-336): back face grows 0.62 -> 1.0 (440 x 620 at x 72, y 200) anchored top-left; shrinks back to 0.62 over 8
  frames from the S10 cut (f396).
- **End card**: "Book in the app" Poppins 700 96 px mixed case; logo, badges and fine print unchanged (moved up to
  close the gap).
