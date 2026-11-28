// Ne World posts updater.
// Runs on GitHub Actions (.github/workflows/update-posts.yml): reads the public web preview of each
// Telegram channel (t.me/s/<channel>), adds new posts to posts.json and saves their pictures to img/.
// No AI and no Telegram login: titles, text, categories and flags come from the post itself and fixed rules.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import * as cheerio from 'cheerio';

import { CHANNELS, fromMessage, toPost } from './tg-core.mjs';

const FILE = process.argv[2] || 'posts.json';
const SOURCE = process.env.POSTS_HTML_DIR || '';   // for local tests: read <dir>/<channel>.html instead of the web

async function get(url, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0 (NeWorld site updater; +https://david030309-gif.github.io/ne-world/)', 'Accept-Language': 'ru' }, signal: AbortSignal.timeout(25000) });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r;
    } catch (e) { if (i === tries) throw e; await new Promise(res => setTimeout(res, 2000 * i)); }
  }
}

// ---------- one channel ----------
async function readChannel(channel) {
  if (SOURCE) return readFile(`${SOURCE}/${channel}.html`, 'utf8');
  return (await get(`https://t.me/s/${channel}`)).text();
}
/** cheerio adapter: pull each message out of the t.me/s page for the shared rules in tg-core.mjs */
function parse(html, channel) {
  const $ = cheerio.load(html), out = [];
  $('.tgme_widget_message[data-post]').each((_, msg) => {
    const m = $(msg), textEl = m.find('.tgme_widget_message_text').first();
    let lines = [];
    if (textEl.length) {
      const c = textEl.clone();
      c.find('i.emoji').each((_, e) => { $(e).replaceWith($(e).text()); });
      { const lead = c.contents().filter((_, n) => !(n.type === 'text' && !$(n).text().trim())).first();   // bold opening = the headline
        if (lead.length && /^(b|strong)$/i.test(lead[0].tagName || '') && lead.text().trim().length >= 8) lead.after('\n'); }
      c.find('br').replaceWith('\n');
      c.find('tg-spoiler').each((_, e) => { $(e).replaceWith($(e).text()); });
      lines = c.text().split('\n');
    }
    const photo = m.find('.tgme_widget_message_photo_wrap').first();
    const p = fromMessage({
      num: +m.attr('data-post').split('/')[1], service: m.hasClass('service_message'), lines,
      hasMedia: m.find('.tgme_widget_message_photo_wrap, .tgme_widget_message_video_thumb').length > 0,
      photoStyle: photo.attr('style'), thumbStyle: m.find('.tgme_widget_message_video_thumb').first().attr('style'),
      padStyle: photo.find('div[style*="padding-top"]').attr('style') || m.find('.tgme_widget_message_video_wrap').attr('style'),
      video: m.find('.tgme_widget_message_video_player, .tgme_widget_message_video').length > 0,
      datetime: m.find('time[datetime]').last().attr('datetime'), viewsText: m.find('.tgme_widget_message_views').first().text(),
      dur: m.find('.message_video_duration').first().text(),
    }, channel);
    if (p) out.push(p);
  });
  return out;
}

async function saveImage(url, path) {
  try { const r = await get(url, 2); await writeFile(path, Buffer.from(await r.arrayBuffer())); return true; }
  catch (e) { console.error('image failed', url, e.message); return false; }
}

// ---------- main ----------
const data = JSON.parse(await readFile(FILE, 'utf8'));
// posts removed by hand stay removed: list their ids in hidden.json, e.g. ["ch-1101"]
const HIDDEN = new Set(JSON.parse(await readFile('hidden.json', 'utf8').catch(() => '[]')));
await mkdir('img', { recursive: true });
const report = {};
for (const { key, channel, keep } of CHANNELS) {
  const list = data[key] || (data[key] = []);
  const byId = new Map(list.map(p => [p.id, p]));
  let html; try { html = await readChannel(channel); } catch (e) { report[key] = 'error: ' + e.message; continue; }
  const posts = parse(html, channel);
  let added = 0;
  for (const p of posts) {
    const id = `${key}-${p.num}`, old = byId.get(id);
    if (HIDDEN.has(id)) continue;
    if (old) {   // known post: refresh the view count and the text (edited in Telegram, or parsed better now)
      if (p.views > (old.views || 0)) old.views = p.views;
      if (p.title !== old.title || JSON.stringify(p.paras) !== JSON.stringify(old.paras)) { const f = toPost(p, key, channel, old.img); old.title = f.title; old.paras = f.paras; if (f.bullets) old.bullets = f.bullets; }
      continue; }
    let img = null;
    if (p.img) { const path = `img/${id}.jpg`; if (await saveImage(p.img, path)) img = path; }
    const post = toPost(p, key, channel, img);
    list.push(post); byId.set(id, post); added++;
  }
  list.sort((a, b) => new Date(b.date) - new Date(a.date));
  data[key] = list.filter(p => !HIDDEN.has(p.id)).slice(0, keep);
  report[key] = `${posts.length} read, ${added} new`;
}
await writeFile(FILE, JSON.stringify(data));
console.log(JSON.stringify(report));
