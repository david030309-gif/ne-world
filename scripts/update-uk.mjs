// Ne Mayfair Live updater (London & Britain).
// Runs on GitHub Actions every 10 minutes (.github/workflows/update-map.yml) and writes map/uk-live.json.
// Only open data that needs no registration:
//   TfL Unified API     - Underground, Elizabeth line, Overground, DLR status; London road disruptions
//   Environment Agency  - flood warnings (England)
//   Met Office          - national severe weather warnings (RSS)
// Motorways (National Highways) need a registered key and are not included yet.
// No AI: Russian labels come from fixed dictionaries below.
import { writeFile } from 'node:fs/promises';
import { lines as tflLines, roads as tflRoads } from '../map/uk-core.mjs';

const now = new Date();
async function get(url, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(url, { headers: { 'User-Agent': 'NeMayfairLive/1.0 (+https://t.me/NeMyfair)' }, signal: AbortSignal.timeout(25000) });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r;
    } catch (e) { if (i === tries) throw e; await new Promise(res => setTimeout(res, 1500 * i)); }
  }
}

// ---------- Environment Agency floods ----------
const FLOOD_RU = { 1: 'Серьёзная угроза жизни', 2: 'Наводнение ожидается', 3: 'Может подняться вода' };
async function floods() {
  const r = await get('https://environment.data.gov.uk/flood-monitoring/id/floods');
  const j = await r.json();
  const its = (j.items || []).filter(f => f.severityLevel >= 1 && f.severityLevel <= 3).sort((a, b) => a.severityLevel - b.severityLevel);
  const out = [];
  for (const f of its.slice(0, 40)) {
    let ll = null;
    try { const a = await (await get(`https://environment.data.gov.uk/flood-monitoring/id/floodAreas/${f.floodAreaID}`, 1)).json(); const it = a.items || {}; if (it.lat) ll = [+it.long, +it.lat]; } catch {}
    out.push({ level: f.severityLevel, label: FLOOD_RU[f.severityLevel], area: f.description || f.eaAreaName || '', county: f.floodArea?.county || '', river: f.floodArea?.riverOrSea || '', ll });
  }
  const c = [1, 2, 3].map(l => its.filter(f => f.severityLevel === l).length);
  return { ok: true, total: its.length, severe: c[0], warnings: c[1], alerts: c[2], items: out };
}

// ---------- Met Office warnings ----------
const WX_RU = [[/rain/i, 'дождь'], [/wind/i, 'ветер'], [/snow/i, 'снег'], [/ice/i, 'гололёд'], [/fog/i, 'туман'], [/thunder/i, 'грозы'], [/heat/i, 'жара'], [/lightning/i, 'молнии']];
const COL_RU = { Yellow: 'Жёлтое', Amber: 'Оранжевое', Red: 'Красное' };
async function weather() {
  const r = await get('https://www.metoffice.gov.uk/public/data/PWSCache/WarningsRSS/Region/UK');
  const xml = await r.text();
  const items = [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].map(m => {
    const t = ((m[1].match(/<title>([\s\S]*?)<\/title>/) || [])[1] || '').replace(/<!\[CDATA\[|\]\]>/g, '').trim();
    const col = (t.match(/\b(Yellow|Amber|Red)\b/) || [])[1] || '';
    const kinds = WX_RU.filter(([re]) => re.test(t)).map(([, v]) => v);
    return { color: col, text: `${COL_RU[col] || ''} предупреждение${kinds.length ? ': ' + kinds.join(', ') : ''}`.trim(), title: t };
  }).filter(x => x.title);
  return { ok: true, total: items.length, items };
}

const live = { updated: now.toISOString(), sources: {} };
for (const [k, fn] of [['lines', () => tflLines(get)], ['roads', () => tflRoads(get, now)], ['floods', floods], ['weather', weather]]) {
  try { live[k] = await fn(); live.sources[k] = 'ok'; }
  catch (e) { live[k] = { ok: false }; live.sources[k] = 'error: ' + e.message; console.error(k, 'failed:', e.message); }
}
live.motorways = { ok: false, reason: 'needs_registration' };
await writeFile('map/uk-live.json', JSON.stringify(live, null, 1));
console.log(JSON.stringify({ lines: live.lines.total, roads: live.roads.total, floods: live.floods.total, weather: live.weather.total, sources: live.sources }));
