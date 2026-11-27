// Ne World posts updater.
// Runs on GitHub Actions (.github/workflows/update-posts.yml): reads the public web preview of each
// Telegram channel (t.me/s/<channel>), adds new posts to posts.json and saves their pictures to img/.
// No AI and no Telegram login: titles, text, categories and flags come from the post itself and fixed rules.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import * as cheerio from 'cheerio';

const CHANNELS = [
  { key: 'ch', channel: 'golosswiss', keep: 40 },
  { key: 'uk', channel: 'NeMyfair', keep: 40 },
  { key: 'eho', channel: 'ehochweiz', keep: 30 },
];
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

// ---------- text helpers ----------
const EMOJI = /[\p{Extended_Pictographic}\p{Regional_Indicator}\u{FE0F}\u{200D}\u{20E3}]/gu;
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const clean = s => s.replace(EMOJI, '').replace(/[ \t ]+/g, ' ').replace(/^[\s|•·\-–—:]+|[\s|•·\-–—]+$/g, '').trim();

/** Turn the message HTML into plain lines (emoji images become their characters, <br> becomes a line break). */
function linesOf($, el) {
  const m = $(el).clone();
  m.find('i.emoji').each((_, e) => { $(e).replaceWith($(e).text()); });
  m.find('br').replaceWith('\n');
  m.find('tg-spoiler').each((_, e) => { $(e).replaceWith($(e).text()); });
  return m.text().split('\n');
}

const sentences = t => t.replace(/<br>/g, ' ').match(/[^.!?…]+[.!?…]*/g)?.map(s => s.trim()).filter(Boolean) || [];
function cut(s, n = 78) {
  s = s.replace(/[.\s]+$/, '');
  if (s.length <= n) return s;
  const c = s.slice(0, n); return c.slice(0, Math.max(c.lastIndexOf(' '), n - 12)).replace(/[,;:\s]+$/, '') + '…';
}

// ---------- categories (fixed keyword rules, checked in order) ----------
const CATS = [
  ['Главное за ночь', /за ночь/i],
  ['Транспорт', /поезд|sbb|сбб|метро|tfl|автобус|трамва|аэропорт|рейс|авиа|eurostar|дорог|трасс|пробк|туннел|вокзал|забастовк.*(транспорт|машинист)|swiss\b|easyjet|heathrow|хитроу/i],
  ['Происшествия', /полици|арест|задержа|погиб|пострада|пожар|авари|убий|нападени|ограблен|кокаин|наркотик|суд\b|осуждён|приговор|взрыв|эвакуац|подозрительн/i],
  ['Здоровье', /врач|больниц|nhs|здоровь|вакцин|лекарств|болезн|вирус|грипп|медицин|пациент|аптек/i],
  ['Экономика', /франк|фунт|банк|цен[аыу]|инфляц|налог|зарплат|аренд|ипотек|бюджет|компани|рынок|акци|млрд|млн|экономик|магазин|coop|migros|tesco|работ[уа] |вакансии|пенси/i],
  ['Политика', /правительств|парламент|министр|выбор|референдум|голосован|совет|партия|премьер|санкци|закон/i],
  ['Спорт', /футбол|хоккей|теннис|матч|чемпионат|олимпи|лыж|гонк|спорт|премьер-лиг/i],
  ['Афиша', /концерт|фестиваль|выставк|музе|кино|фильм|сериал|театр|ярмарк|рождественск|шоу\b|top gear/i],
  ['Мир', /росси|украин|сша|трамп|европ|ес\b|китай|израил|германи|франци/i],
];
const catOf = t => (CATS.find(([, re]) => re.test(t)) || ['Общество'])[0];

// ---------- one channel ----------
async function readChannel(channel) {
  if (SOURCE) return readFile(`${SOURCE}/${channel}.html`, 'utf8');
  return (await get(`https://t.me/s/${channel}`)).text();
}
const bgUrl = st => ((st || '').match(/background-image:\s*url\(['"]?([^'")]+)/) || [])[1] || null;
const views = v => { v = (v || '').trim().replace(',', '.'); const n = parseFloat(v) || 0; return Math.round(/k/i.test(v) ? n * 1000 : /m/i.test(v) ? n * 1e6 : n); };

function parse(html, channel) {
  const $ = cheerio.load(html), out = [];
  $('.tgme_widget_message[data-post]').each((_, msg) => {
    const m = $(msg), num = +m.attr('data-post').split('/')[1];
    if (!num || m.hasClass('service_message')) return;
    const textEl = m.find('.tgme_widget_message_text').first();
    const raw = textEl.length ? linesOf($, textEl) : [];
    // paragraphs = blocks separated by empty lines; drop the channel signature and subscribe links
    const blocks = []; let cur = [];
    for (const l of raw) { if (!l.trim()) { if (cur.length) blocks.push(cur); cur = []; } else cur.push(l); }
    if (cur.length) blocks.push(cur);
    const sig = new RegExp(`t\\.me/${channel}|подпис(аться|ывайтесь)|прислать новость|^\\s*(ne alpy|ne mayfair|nemyfair|ehoschweiz|ehochweiz|eho|ехо|эхо)\\b`, 'i');
    const kept = blocks.filter(b => !(b.length <= 2 && b.every(l => sig.test(l) || !clean(l))));
    if (!kept.length && !m.find('.tgme_widget_message_photo_wrap, .tgme_widget_message_video_thumb').length) return;
    const first = kept.length ? kept[0] : [];
    let title = clean(first[0] || '');
    const restFirst = first.slice(1).map(clean).filter(Boolean);
    const paras = [...(restFirst.length ? [restFirst.map(esc).join('<br>')] : []),
      ...kept.slice(1).map(b => b.map(clean).filter(Boolean).map(esc).join('<br>')).filter(Boolean)];
    if (!title && paras.length) { title = cut(paras.shift().replace(/<br>/g, ' '), 90); }
    if (!title) return;   // picture without any text: nothing to show as news
    const all = [title, ...paras].join(' ');
    // not news: ads and channel announcements
    if (/#?реклама|erid|партн[её]рск(ий|ая) материал|промокод|вход за репост|резервация стол|розыгрыш|^друзья[,!]|небольшой анонс/i.test(all)) return;
    const wholeRaw = raw.join(' ');
    const photo = m.find('.tgme_widget_message_photo_wrap').first();
    const vthumb = m.find('.tgme_widget_message_video_thumb').first();
    const img = bgUrl(photo.attr('style')) || bgUrl(vthumb.attr('style'));
    const pad = parseFloat((photo.find('div[style*="padding-top"]').attr('style') || m.find('.tgme_widget_message_video_wrap').attr('style') || '').match(/padding-top:\s*([\d.]+)%/)?.[1] || 0);
    const video = m.find('.tgme_widget_message_video_player, .tgme_widget_message_video').length > 0;
    out.push({
      num, date: m.find('time[datetime]').last().attr('datetime') || new Date().toISOString(),
      views: views(m.find('.tgme_widget_message_views').first().text()),
      title: title.replace(/^(срочно|важно)\s*[:!.]\s*/i, s => s), paras, img, ar: pad ? +(100 / pad).toFixed(3) : null,
      video, dur: m.find('.message_video_duration').first().text().trim(),
      urgent: /‼|❗|⚡|🚨|срочно/i.test(raw.slice(0, 2).join(' ')),
      sub: /^от подписчик/i.test(title), whole: wholeRaw,
    });
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
    if (old) { if (p.views > (old.views || 0)) old.views = p.views; continue; }   // known post: only refresh the view count
    let img = null;
    if (p.img) { const path = `img/${id}.jpg`; if (await saveImage(p.img, path)) img = path; }
    const text = `${p.title} ${p.whole}`;
    const post = { id, tg: `https://t.me/${channel}/${p.num}`, date: p.date, views: p.views, title: p.title, paras: p.paras };
    if (key === 'eho') Object.assign(post, { video: p.video, dur: p.dur, urgent: p.urgent, sub: p.sub, ...(img ? { img, ar: p.ar || 1.25 } : {}) });
    else {
      const cat = catOf(text);
      Object.assign(post, { bullets: sentences(p.paras.join(' ')).slice(0, 3).map(s => cut(s)), cat, img, video: p.video,
        digest: cat === 'Главное за ночь', london: key === 'uk' && /лондон|london|tfl|метро|темз|хитроу|heathrow/i.test(text), urgent: p.urgent });
    }
    list.push(post); byId.set(id, post); added++;
  }
  list.sort((a, b) => new Date(b.date) - new Date(a.date));
  data[key] = list.filter(p => !HIDDEN.has(p.id)).slice(0, keep);
  report[key] = `${posts.length} read, ${added} new`;
}
await writeFile(FILE, JSON.stringify(data));
console.log(JSON.stringify(report));
