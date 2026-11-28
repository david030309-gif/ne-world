// Ne Globus live relay — a Cloudflare Worker (free plan).
// The app cannot read t.me pages directly (the browser blocks cross-site reads), so this worker fetches the
// PUBLIC preview page of our channels and hands it to the app with permission to read it.
// No tokens, no logins, nothing stored. Each channel is fetched from Telegram at most once every 20 seconds.
//
// Deployed automatically with the site by Cloudflare from this repository (wrangler.jsonc): https://ne-world.david030309.workers.dev/?c=golosswiss
// Manual alternative: Cloudflare dashboard → Workers & Pages → Create → Worker → name it "ne-live" → Deploy →
// Edit code → replace everything with this file → Deploy. Then send the worker address (…workers.dev) to Claude.

const CHANNELS = ['golosswiss', 'NeMyfair', 'ehochweiz'];   // only our channels, nothing else can be fetched
const FRESH_SECONDS = 20;

export default {
  async fetch(request, env, ctx) {
    const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, OPTIONS' };
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    const url = new URL(request.url);
    // Nice buses and trams, live positions (open data Lignes d'Azur, etalab-2.0). Fixed URL only, cached 15 s.
    if (url.searchParams.get('t') === 'nice') {
      const cache = caches.default, key = new Request('https://ne-live.cache/nice-vp');
      const hit = await cache.match(key);
      if (hit) return new Response(hit.body, { headers: { ...cors, 'content-type': 'application/octet-stream', 'x-ne-live': 'cache' } });
      const r = await fetch('https://www.data.gouv.fr/api/1/datasets/r/5f571595-aef1-480f-acde-b9315d9f5f3b', { redirect: 'follow', headers: { 'User-Agent': 'Ne Globus live relay' } });
      if (!r.ok) return new Response('feed ' + r.status, { status: 502, headers: cors });
      const buf = await r.arrayBuffer();
      ctx.waitUntil(cache.put(key, new Response(buf.slice(0), { headers: { 'content-type': 'application/octet-stream', 'Cache-Control': 'public, max-age=15' } })));
      return new Response(buf, { headers: { ...cors, 'content-type': 'application/octet-stream', 'x-ne-live': 'fresh' } });
    }
    const channel = url.searchParams.get('c') || '';
    if (!CHANNELS.includes(channel)) {
      // Deployed together with the site (wrangler.jsonc): everything that is not a relay request is the site itself.
      if (env && env.ASSETS) return env.ASSETS.fetch(request);
      return new Response(JSON.stringify({ ok: true, channels: CHANNELS }), { headers: { ...cors, 'content-type': 'application/json' } });
    }
    const cache = caches.default;
    const key = new Request(`https://ne-live.cache/${channel}`);
    let hit = await cache.match(key);
    if (hit) return new Response(hit.body, { headers: { ...cors, 'content-type': 'text/html; charset=utf-8', 'x-ne-live': 'cache' } });
    const res = await fetch(`https://t.me/s/${channel}`, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Ne Globus live relay)', 'Accept-Language': 'ru' },
    });
    if (!res.ok) return new Response(`telegram ${res.status}`, { status: 502, headers: cors });
    const html = await res.text();
    const out = new Response(html, { headers: { 'content-type': 'text/html; charset=utf-8', 'Cache-Control': `public, max-age=${FRESH_SECONDS}` } });
    ctx.waitUntil(cache.put(key, out.clone()));
    return new Response(html, { headers: { ...cors, 'content-type': 'text/html; charset=utf-8', 'x-ne-live': 'fresh' } });
  },
};
