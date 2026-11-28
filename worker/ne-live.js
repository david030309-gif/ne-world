// Ne Globus live relay — a Cloudflare Worker (free plan).
// The app cannot read t.me pages directly (the browser blocks cross-site reads), so this worker fetches the
// PUBLIC preview page of our channels and hands it to the app with permission to read it.
// No tokens, no logins, nothing stored. Each channel is fetched from Telegram at most once every 20 seconds.
//
// Deploy: Cloudflare dashboard → Workers & Pages → Create → Worker → name it "ne-live" → Deploy →
// Edit code → replace everything with this file → Deploy. Then send the worker address (…workers.dev) to Claude.

const CHANNELS = ['golosswiss', 'NeMyfair', 'ehochweiz'];   // only our channels, nothing else can be fetched
const FRESH_SECONDS = 20;

export default {
  async fetch(request, env, ctx) {
    const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, OPTIONS' };
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    const url = new URL(request.url);
    const channel = url.searchParams.get('c') || '';
    if (!CHANNELS.includes(channel)) {
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
