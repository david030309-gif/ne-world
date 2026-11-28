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
  - `ch-cantons.json`: Swiss map shapes (cantons, lakes). **The Swiss map is live since 28.11.2026:** the AMG server (DigitalOcean, `nealpy-livemap.timer`, the same job that edits t.me/golosswiss/1094 every 5 min) publishes its `live.json` to a secret gist of `rezniklev341-create` (`CHLIVE` in `index.html`). The browser loads it at start and at :01, :06, :11… (`loadCH` → `chFromLive`), draws `items` as markers and `areas` as SLF avalanche polygons. If the gist fails, the old hard-coded 08:10 data in `MAPS.ch` stays as a fallback. No keys ever go in the site.
  - `uk.json` and `thames.json`: England and London map.
  - `uk-live.json`: bot output for the UK map. Since 28.11.2026 the UK map also reads the AMG server's `live-uk.json` from the same gist (`UKS_URL`, `mergeUKS`): motorways (National Highways, new «Трассы» section + diamond markers) and floods come from there, so they match the Ne Mayfair channel. Tube lines and London roads still come live from TfL in the browser. National Rail is not in the file yet (waiting for Rail Data Marketplace access).
  - `uk-core.mjs`: shared TfL logic (Tube lines and London roads). The browser uses it directly, and so does the bot.
- `scripts/update-posts.mjs`: reads the public pages `t.me/s/<channel>` and adds new posts and photos. It uses no AI: titles come from the first line of the post, and categories come from fixed keyword rules (`CATS`). It skips ads and announcements.
- `scripts/update-uk.mjs`: fetches TfL, Environment Agency floods and Met Office warnings into `map/uk-live.json`, using fixed Russian wording.
- `.github/workflows/update-posts.yml` and `update-map.yml`: scheduled bots that commit as `ne-world-bot`. The GitHub schedule can be slow (roughly hourly at times). To run one by hand: `gh workflow run update-posts.yml`.
- `manifest.webmanifest`, `sw.js`, `icons/`: installable app (PWA). The service worker is network-first, so news is always fresh, and the cache is only an offline fallback. To change the app icon, replace the files in `icons/` (keep the names and sizes: 512, 192, 180 apple-touch, 32) and bump `CACHE` in `sw.js`.
- Opening animation: the `#intro` block plus a small script at the end of `index.html`. It plays once per session (~3.4 s, the same length every time so the text can be read), only on `#globe` or an empty hash, and again when the user comes back to the app after 10+ minutes away (a small script reloads the page fresh on `visibilitychange`), then calls `window.nwGlobe.settle(true)`, which spins the real globe into place. Use `window.nwGlobe`, not `globe`: in the global scope `globe` is the `#globe` canvas element.
- `video/`: coming-soon card clips. `video/sources.json` lists Mixkit clip ids per country; pushing a change there runs `.github/workflows/build-videos.yml` (via `scripts/build-videos.sh`), which downloads, cuts and commits `video/<key>.mp4` and `.jpg`. The card shows the logo first, then flies into it and plays the clip; if the clip is missing, the logo stays.
- `docs/HISTORY.md`: project history, every decision David made, logo style rules and the backlog. **Read it first.** When something new is decided, write it there in the same commit.
- `brand/`: final SVG logos, plus `brand/src/` with the Python generators (fontTools + Montserrat 800, which is included). Example: `cd brand/src && python3 monaco.py`. Render PNGs from the SVGs with a headless browser.

## Rules when editing
1. **Run `git pull --rebase origin main` before every push.** The bots commit every few minutes, so pushing without pulling first gets rejected.
2. Test locally before pushing:
   - Run `python3 -m http.server` and open `http://localhost:8000/#globe`. Check both a desktop width and a phone width (390px).
   - The console should show no JS errors.
3. Keep the design calm and dark. The globe must stay smooth on phones: pinch-zoom uses native touch events, and double-tap resets the zoom.
4. The site has no backend and stores no secrets. Never put API keys or passwords in this repository or in chat. If a key is ever needed, it goes in GitHub → Settings → Secrets.
5. Write commit messages in plain English describing what changed.
