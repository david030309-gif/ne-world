// Ne Globus: brand-new Telegram posts straight into the open app, without waiting for the GitHub bot.
// Reads our channels' public pages through the Cloudflare relay (worker/ne-live.js) and applies the SAME
// rules as the bot (scripts/tg-core.mjs). Pictures load straight from Telegram until the bot archives them.
import { CHANNELS, fromMessage, toPost } from '../scripts/tg-core.mjs';

function parse(html, channel) {
  const doc = new DOMParser().parseFromString(html, 'text/html'), out = [];
  for (const m of doc.querySelectorAll('.tgme_widget_message[data-post]')) {
    const textEl = m.querySelector('.tgme_widget_message_text');
    let lines = [];
    if (textEl) {
      const c = textEl.cloneNode(true);
      c.querySelectorAll('i.emoji, tg-spoiler').forEach(e => e.replaceWith(doc.createTextNode(e.textContent)));
      c.querySelectorAll('br').forEach(e => e.replaceWith(doc.createTextNode('\n')));
      lines = c.textContent.split('\n');
    }
    const photo = m.querySelector('.tgme_widget_message_photo_wrap');
    const thumb = m.querySelector('.tgme_widget_message_video_thumb');
    const times = m.querySelectorAll('time[datetime]');
    const p = fromMessage({
      num: +m.getAttribute('data-post').split('/')[1], service: m.classList.contains('service_message'), lines,
      hasMedia: !!(photo || thumb), photoStyle: photo?.getAttribute('style'), thumbStyle: thumb?.getAttribute('style'),
      padStyle: photo?.querySelector('div[style*="padding-top"]')?.getAttribute('style') || m.querySelector('.tgme_widget_message_video_wrap')?.getAttribute('style'),
      video: !!m.querySelector('.tgme_widget_message_video_player, .tgme_widget_message_video'),
      datetime: times.length ? times[times.length - 1].getAttribute('datetime') : null,
      viewsText: m.querySelector('.tgme_widget_message_views')?.textContent, dur: m.querySelector('.message_video_duration')?.textContent,
    }, channel);
    if (p) out.push(p);
  }
  return out;
}

/** Returns { key: [posts…] } with only the posts the app does not have yet (and that are not hidden). */
export async function freshPosts(relay, data, hidden) {
  const res = {};
  await Promise.all(CHANNELS.map(async ({ key, channel }) => {
    try {
      const r = await fetch(`${relay}?c=${channel}`, { cache: 'no-store' });
      if (!r.ok) return;
      const have = new Set((data[key] || []).map(p => p.id));
      const posts = parse(await r.text(), channel)
        .map(p => toPost(p, key, channel, p.img))
        .filter(p => !have.has(p.id) && !hidden.has(p.id));
      if (posts.length) res[key] = posts;
    } catch (e) { /* relay offline: the bot's posts.json still works */ }
  }));
  return res;
}
