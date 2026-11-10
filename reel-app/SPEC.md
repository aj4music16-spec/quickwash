# QuickWash — app awareness reel

1080×1920, 30 fps, 18.0 s, 120 BPM (cuts on the beat). Built with HyperFrames.
Every claim and price is taken from quickwashtech.com (read 2026-11-10).

| t (s) | Scene | On screen | Source |
|---|---|---|---|
| 0–2 | Hook | Still driving to the car wash? → Make it come to **you.** | — |
| 2–7.5 | App | Book a wash in **20 seconds.** Real app screens: pick your wash → pick a time → track your detailer; clock runs 0:00→0:20, "Booked ✓" | Homepage ("under 20 seconds"), FAQ (real-time tracking), site app screenshots |
| 7.5–10.5 | Service | We come to **you.** Vetted · Trained · Insured → We bring the water & power. | FAQ 9, 13 |
| 10.5–13 | Packages | Flat pricing. No surprises. QuickWash $99 · Detail $249 · Full Detail $399 | /pricing |
| 13–15 | Proof | 10,000+ washes & details completed · 200+ five-star Google reviews · NJ · NY · FL | /testimonials |
| 15–18 | End card | Logo · The car wash that comes to you. · App Store + Google Play badges | Site assets |

Sound: `tools/soundtrack.js` synthesizes the bed and effects (`node tools/soundtrack.js out.wav`).
Render: `npm run render`. Edit copy in `compositions/*.html`; brand colours are variables in `index.html`.
