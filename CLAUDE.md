# Ne World — notes for Claude (and for people)

Ne World is a Russian-language news site for the AMG Telegram channels. You pick a country on a 3D globe and get that country's news feed.
Live site: https://david030309-gif.github.io/ne-world/ (GitHub Pages; it deploys automatically on every push to `main`, in about 1 minute).

Owner: David. Anyone else editing the site (for example David's brother) works through this repository.
The site is in Russian, and David writes in Russian and English.

## Channels
| Key | Channel | Telegram | Status |
|---|---|---|---|
| `ch` | Ne Alpy 🇨🇭 | t.me/golosswiss | live |
| `uk` | Ne Mayfair 🇬🇧 | t.me/NeMyfair | live |
| `eho` | ehoschweiz (youth CH, "Движ" tab) | t.me/ehochweiz | live |
| `de` | Ne Ordnung 🇩🇪 | — | coming soon |
| `fr` | Ne Provence 🇫🇷 | — | coming soon |
| `mc` | Ne Lazurka 🇲🇨 (Monaco + Nice) | — | coming soon |
| `il` | Ne Kosher 🇮🇱 | — | coming soon |
Planned later: Ne Zhabka 🇵🇱 (logo in `brand/`, not on the site yet). The old Ne Shalom idea was replaced by Ne Kosher.

## Files
- `index.html`: the whole app in one file (HTML + CSS + JS). Routing uses the hash: `#globe`, `#ch`, `#uk`, `#ch-dvizh`, `#ch-1107` (article), `#eho-NNN`, `#ch-map`, `#uk-map`.
  - The `R` / regions config holds the live channels. `NEXT` holds the coming-soon channels: their globe label, zoom level, and teaser text (`hook`, `desc`, `tags`) and logo.
  - The globe is a canvas built with d3 (`d3.min.js` and `topojson-client.min.js`, both bundled locally). It also uses `world-110m.json` (country names are in Russian, in `properties.ru`) and `world.json`.
- `posts.json`: news posts for `ch`, `uk` and `eho`. The bot updates it, so don't rewrite it by hand unless you have to.
- `hidden.json`: ids of posts that were removed for good (for example `["ch-1101"]`). The bot will never add them back. To remove a post from the site, add its id here and delete it from `posts.json`.
- `img/`: pictures saved by the bot. `eho/`: ehoschweiz media and the giveaway poster.
- `logo-*.png`: logos used on the site. They are white on a transparent background. `logo-de/fr/mc/il.png` share the same frame (877×755), so the teaser cards look identical.
- `map/`:
  - `ch-cantons.json`: Swiss map. **It stays static, with data from 08:10.** David asked for it not to auto-update.
  - `uk.json` and `thames.json`: England and London map.
  - `uk-live.json`: bot output for the UK map.
  - `uk-core.mjs`: shared TfL logic (Tube lines and London roads). The browser uses it directly, and so does the bot.
- `scripts/update-posts.mjs`: reads the public pages `t.me/s/<channel>` and adds new posts and photos. It uses no AI: titles come from the first line of the post, and categories come from fixed keyword rules (`CATS`). It skips ads and announcements.
- `scripts/update-uk.mjs`: fetches TfL, Environment Agency floods and Met Office warnings into `map/uk-live.json`, using fixed Russian wording.
- `.github/workflows/update-posts.yml` and `update-map.yml`: scheduled bots that commit as `ne-world-bot`. The GitHub schedule can be slow (roughly hourly at times). To run one by hand: `gh workflow run update-posts.yml`.
- `manifest.webmanifest`, `sw.js`, `icons/`: installable app (PWA). The service worker is network-first, so news is always fresh, and the cache is only an offline fallback. To change the app icon, replace the files in `icons/` (keep the names and sizes: 512, 192, 180 apple-touch, 32) and bump `CACHE` in `sw.js`.
- `docs/HISTORY.md`: project history, decisions and backlog (read it first).
- `brand/`: final SVG logos, plus `brand/src/` with the Python generators (fontTools + Montserrat 800, which is included). Example: `cd brand/src && python3 monaco.py`. Render PNGs from the SVGs with a headless browser.

## Rules when editing
1. **Run `git pull --rebase origin main` before every push.** The bots commit every few minutes, so pushing without pulling first gets rejected.
2. Test locally before pushing:
   - Run `python3 -m http.server` and open `http://localhost:8000/#globe`. Check both a desktop width and a phone width (390px).
   - The console should show no JS errors.
3. Keep the design calm and dark. The globe must stay smooth on phones: pinch-zoom uses native touch events, and double-tap resets the zoom.
4. The site has no backend and stores no secrets. Never put API keys or passwords in this repository or in chat. If a key is ever needed, it goes in GitHub → Settings → Secrets.
5. Write commit messages in plain English describing what changed.
