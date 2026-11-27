// Ne Mayfair Live updater (London & Britain).
// Runs on GitHub Actions every 10 minutes (.github/workflows/update-map.yml) and writes map/uk-live.json.
// Only open data that needs no registration:
//   TfL Unified API     - Underground, Elizabeth line, Overground, DLR status; London road disruptions
//   Environment Agency  - flood warnings (England)
//   Met Office          - national severe weather warnings (RSS)
// Motorways (National Highways) need a registered key and are not included yet.
// No AI: Russian labels come from fixed dictionaries below.
import { writeFile } from 'node:fs/promises';

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

// ---------- TfL lines ----------
const LINE = {
  bakerloo: ['Bakerloo', '#B36305', '#fff'], central: ['Central', '#E32017', '#fff'], circle: ['Circle', '#FFD300', '#111'],
  district: ['District', '#00782A', '#fff'], 'hammersmith-city': ['Hammersmith & City', '#F3A9BB', '#111'], jubilee: ['Jubilee', '#A0A5A9', '#111'],
  metropolitan: ['Metropolitan', '#9B0056', '#fff'], northern: ['Northern', '#000000', '#fff'], piccadilly: ['Piccadilly', '#003688', '#fff'],
  victoria: ['Victoria', '#0098D4', '#fff'], 'waterloo-city': ['Waterloo & City', '#95CDBA', '#111'], elizabeth: ['Elizabeth', '#6950A1', '#fff'],
  dlr: ['DLR', '#00A4A7', '#fff'], liberty: ['Liberty', '#5D6061', '#fff'], lioness: ['Lioness', '#FAA61A', '#111'], mildmay: ['Mildmay', '#006FE6', '#fff'],
  suffragette: ['Suffragette', '#18A95D', '#fff'], weaver: ['Weaver', '#9B0058', '#fff'], windrush: ['Windrush', '#DC241F', '#fff'],
};
const STATUS_RU = {
  'Minor Delays': 'Небольшие задержки', 'Severe Delays': 'Сильные задержки', 'Part Suspended': 'Не ходит на части линии', 'Suspended': 'Не ходит',
  'Part Closure': 'Частично закрыта', 'Planned Closure': 'Закрыта (плановые работы)', 'Reduced Service': 'Сокращённое движение', 'Special Service': 'Особый режим',
  'Bus Service': 'Вместо поездов автобусы', 'Change of frequency': 'Изменён интервал', 'Diverted': 'Изменён маршрут', 'Not Running': 'Не ходит',
  'Issues Reported': 'Есть сбои', 'No Issues': 'Без сбоев', 'Information': 'Информация', 'Closed': 'Закрыта', 'Part Closed': 'Частично закрыта',
};
const CAUSE_RU = [
  [/signal/i, 'сбой сигнализации'], [/train fault|faulty train|broken down train/i, 'неисправность поезда'],
  [/customer incident|person (taken )?ill|passenger|medical/i, 'происшествие с пассажиром'], [/staff|shortage of/i, 'нехватка персонала'],
  [/strike|industrial action/i, 'забастовка'], [/track|points|rail defect|broken rail/i, 'проблема с путями'], [/power/i, 'проблема с электропитанием'],
  [/planned|engineering|improvement works|works/i, 'плановые работы'], [/fire|smoke/i, 'пожарная тревога'], [/police|security/i, 'работа полиции'],
  [/flood|weather|heat|ice|snow|leaves/i, 'погода'], [/obstruction|object on the track|trespass/i, 'препятствие на путях'],
  [/earlier/i, 'последствия более раннего сбоя'],
];
const cause = t => (CAUSE_RU.find(([re]) => re.test(t || '')) || [, ''])[1];
async function lines() {
  const r = await get('https://api.tfl.gov.uk/Line/Mode/tube,elizabeth-line,overground,dlr/Status');
  const arr = await r.json(), out = [];
  for (const l of arr) {
    const st = (l.lineStatuses || []).filter(s => ![10, 18, 19, 20].includes(s.statusSeverity));   // 10 good, 18/19 no issues/info, 20 closed for the night
    if (!st.length) continue;
    const worst = st.sort((a, b) => a.statusSeverity - b.statusSeverity)[0];
    const [name, bg, fg] = LINE[l.id] || [l.name, '#555', '#fff'];
    const statusRu = STATUS_RU[worst.statusSeverityDescription] || worst.statusSeverityDescription;
    const c = cause(worst.reason);
    out.push({ id: l.id, name, bg, fg, mode: l.modeName, severity: worst.statusSeverity, status: statusRu, cause: c,
      text: c ? `${statusRu}, ${c}` : statusRu, reason: (worst.reason || '').replace(/\s+/g, ' ').trim() });
  }
  out.sort((a, b) => a.severity - b.severity);
  return { ok: true, total: out.length, items: out };
}

// ---------- TfL roads ----------
const CAT_RU = { 'Works': 'Дорожные работы', 'Planned events': 'Мероприятие', 'Surface damage': 'Повреждение покрытия', 'Collisions': 'Авария', 'Hazard(s)': 'Опасность на дороге', 'Hazards': 'Опасность на дороге',
  'Traffic Incidents': 'Происшествие', 'Special and Planned Events': 'Мероприятие', 'Signal Failure': 'Не работают светофоры', 'Breakdowns': 'Сломанная машина',
  'Infrastructure Issue': 'Проблема с дорогой', 'Traffic Volume': 'Большой трафик', 'Network delays': 'Задержки', 'Burst water main': 'Прорыв водопровода' };
async function roads() {
  const r = await get('https://api.tfl.gov.uk/Road/all/Disruption?stripContent=true');
  const arr = await r.json();
  const SEV = { Severe: 3, Serious: 2, Moderate: 1 };
  const title = s => s.toLowerCase().replace(/\b([a-z])/g, c => c.toUpperCase()).replace(/\b(And|Of|The|At|To)\b/g, w => w.toLowerCase());
  const items = arr.filter(d => SEV[d.severity] && (!d.status || /active/i.test(d.status)) && (!d.startDateTime || new Date(d.startDateTime) <= now))
    .map(d => {
      const pt = (() => { try { const p = JSON.parse(d.point); return [+p[0], +p[1]]; } catch { return null; } })();
      const road = ((d.location || '').match(/\[([AM]\d{1,4}[A-Z]?)\]/) || [])[1] || (d.corridorIds || [])[0]?.toUpperCase() || '';
      const m = (d.location || '').replace(/^\s*\[[^\]]*\]\s*/, '').match(/^([^(]+)(?:\([^)]*\))?\s*(?:\(([^)]*)\))?/) || [];
      const place = [title((m[1] || '').trim()), m[2] ? `(${m[2]})` : ''].filter(Boolean).join(' ');
      const txt = `${d.comments || ''} ${d.currentUpdate || ''}`;
      const closed = d.hasClosures || /\b(is|are|currently) closed\b|closure|road closed|closed (northbound|southbound|eastbound|westbound)/i.test(txt);
      const lanes = /reduced to (one|two|three|a single) lane|lane restriction|lane closure/i.test(txt);
      const what = closed ? 'дорога частично перекрыта' : lanes ? 'сужение полос' : '';
      return { badge: road || '!', title: place, text: `${CAT_RU[d.category] || d.category || 'Сбой'}${what ? ', ' + what : ''}`,
        severity: d.severity, rank: SEV[d.severity] * 2 + (closed ? 1 : 0) + (d.levelOfInterest === 'High' ? 1 : 0), ll: pt };
    })
    .sort((a, b) => b.rank - a.rank);
  return { ok: true, total: items.length, items: items.slice(0, 6) };
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
for (const [k, fn] of [['lines', lines], ['roads', roads], ['floods', floods], ['weather', weather]]) {
  try { live[k] = await fn(); live.sources[k] = 'ok'; }
  catch (e) { live[k] = { ok: false }; live.sources[k] = 'error: ' + e.message; console.error(k, 'failed:', e.message); }
}
live.motorways = { ok: false, reason: 'needs_registration' };
await writeFile('map/uk-live.json', JSON.stringify(live, null, 1));
console.log(JSON.stringify({ lines: live.lines.total, roads: live.roads.total, floods: live.floods.total, weather: live.weather.total, sources: live.sources }));
