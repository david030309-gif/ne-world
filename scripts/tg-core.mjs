// Shared Telegram-post rules for Ne Globus. Used by BOTH the GitHub bot (scripts/update-posts.mjs, with cheerio)
// and the browser (live/tg-live.mjs, with DOMParser), so a post looks the same whichever way it arrives.
// No AI: titles come from the first line of the post, categories from fixed keyword rules.

export const CHANNELS = [
  { key: 'ch', channel: 'golosswiss', keep: 40 },
  { key: 'uk', channel: 'NeMyfair', keep: 40 },
  { key: 'eho', channel: 'ehochweiz', keep: 30 },
];

const EMOJI = /[\p{Extended_Pictographic}\p{Regional_Indicator}\u{FE0F}\u{200D}\u{20E3}]/gu;
export const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export const clean = s => s.replace(EMOJI, '').replace(/[ \t ]+/g, ' ').replace(/^[\s|•·\-–—:]+|[\s|•·\-–—]+$/g, '').trim();
export const sentences = t => t.replace(/<br>/g, ' ').match(/[^.!?…]+[.!?…]*/g)?.map(s => s.trim()).filter(Boolean) || [];
export function cut(s, n = 78) {
  s = s.replace(/[.\s]+$/, '');
  if (s.length <= n) return s;
  const c = s.slice(0, n); return c.slice(0, Math.max(c.lastIndexOf(' '), n - 12)).replace(/[,;:\s]+$/, '') + '…';
}

// categories (fixed keyword rules, checked in order)
export const CATS = [
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
export const catOf = t => (CATS.find(([, re]) => re.test(t)) || ['Общество'])[0];
export const bgUrl = st => ((st || '').match(/background-image:\s*url\(['"]?([^'")]+)/) || [])[1] || null;
const views = v => { v = (v || '').trim().replace(',', '.'); const n = parseFloat(v) || 0; return Math.round(/k/i.test(v) ? n * 1000 : /m/i.test(v) ? n * 1e6 : n); };

/**
 * One message, already pulled out of the t.me/s page by an adapter:
 * { num, service, lines[], hasMedia, photoStyle, thumbStyle, padStyle, video, datetime, viewsText, dur }
 * Returns the parsed post, or null when it is not news (ads, announcements, signature-only, no text).
 */
export function fromMessage(m, channel) {
  if (!m.num || m.service) return null;
  const raw = m.lines;
  const blocks = []; let cur = [];
  for (const l of raw) { if (!l.trim()) { if (cur.length) blocks.push(cur); cur = []; } else cur.push(l); }
  if (cur.length) blocks.push(cur);
  const sig = new RegExp(`t\\.me/${channel}|подпис(аться|ывайтесь)|прислать новость|^\\s*(ne alpy|ne mayfair|nemyfair|ehoschweiz|ehochweiz|eho|ехо|эхо)\\b`, 'i');
  const kept = blocks.filter(b => !(b.length <= 2 && b.every(l => sig.test(l) || !clean(l))));
  if (!kept.length && !m.hasMedia) return null;
  const first = kept.length ? kept[0] : [];
  let title = clean(first[0] || '');
  const restFirst = first.slice(1).map(clean).filter(Boolean);
  if (title.length > 120) { const s = sentences(title); if (s.length > 1 && s[0].length >= 20 && s[0].length <= 140) { title = s[0]; restFirst.unshift(s.slice(1).join(' ')); } }
  const paras = [...(restFirst.length ? [restFirst.map(esc).join('<br>')] : []),
    ...kept.slice(1).map(b => b.map(clean).filter(Boolean).map(esc).join('<br>')).filter(Boolean)];
  if (!title && paras.length) title = cut(paras.shift().replace(/<br>/g, ' '), 90);
  if (!title) return null;   // picture without any text: nothing to show as news
  const all = [title, ...paras].join(' ');
  if (/#?реклама|erid|партн[её]рск(ий|ая) материал|промокод|вход за репост|резервация стол|розыгрыш|^друзья[,!]|небольшой анонс/i.test(all)) return null;
  const pad = parseFloat((m.padStyle || '').match(/padding-top:\s*([\d.]+)%/)?.[1] || 0);
  return {
    num: m.num, date: m.datetime || new Date().toISOString(), views: views(m.viewsText),
    title, paras, img: bgUrl(m.photoStyle) || bgUrl(m.thumbStyle), ar: pad ? +(100 / pad).toFixed(3) : null,
    video: !!m.video, dur: (m.dur || '').trim(),
    urgent: /‼|❗|⚡|🚨|срочно/i.test(raw.slice(0, 2).join(' ')),
    sub: /^от подписчик/i.test(title), whole: raw.join(' '),
  };
}

/** Turn a parsed post into the shape stored in posts.json. `img` = saved path (bot) or the Telegram CDN url (browser). */
export function toPost(p, key, channel, img) {
  const id = `${key}-${p.num}`, text = `${p.title} ${p.whole}`;
  const post = { id, tg: `https://t.me/${channel}/${p.num}`, date: p.date, views: p.views, title: p.title, paras: p.paras };
  if (key === 'eho') return Object.assign(post, { video: p.video, dur: p.dur, urgent: p.urgent, sub: p.sub, ...(img ? { img, ar: p.ar || 1.25 } : {}) });
  const cat = catOf(text);
  return Object.assign(post, { bullets: sentences(p.paras.join(' ')).slice(0, 3).map(s => cut(s)), cat, img, video: p.video,
    digest: cat === 'Главное за ночь', london: key === 'uk' && /лондон|london|tfl|метро|темз|хитроу|heathrow/i.test(text), urgent: p.urgent });
}
