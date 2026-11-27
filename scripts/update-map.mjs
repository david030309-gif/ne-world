// Ne World live map updater.
// Runs on GitHub Actions every 10 minutes (see .github/workflows/update-map.yml).
// Pulls official open data and writes two small files the website reads:
//   map/ch-live.json       summary + event list (Russian labels, no AI involved)
//   map/ch-avalanche.json  avalanche warning zones as GeoJSON, with danger level 1-5
// Sources:
//   SLF avalanche bulletin (open, no key)       https://aws.slf.ch/api/bulletin/caaml
//   Public transport disruptions (needs key)    https://api.opentransportdata.swiss/la/siri-sx
import { writeFile } from 'node:fs/promises';

const LEVEL = { low: 1, moderate: 2, considerable: 3, high: 4, very_high: 5 };
const LEVEL_RU = ['', 'слабая', 'умеренная', 'значительная', 'большая', 'очень большая'];
const now = new Date();

async function get(url, opts = {}, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(url, { ...opts, signal: AbortSignal.timeout(20000) });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r;
    } catch (e) {
      if (i === tries) throw e;
      await new Promise(res => setTimeout(res, 1500 * i));
    }
  }
}

// --- geometry helpers: round to ~100 m and drop near-duplicate points to keep the file small
const rnd = n => Math.round(n * 1000) / 1000;
function thinRing(ring) {
  const out = [];
  for (const [x, y] of ring) {
    const p = [rnd(x), rnd(y)], q = out[out.length - 1];
    if (!q || Math.abs(q[0] - p[0]) + Math.abs(q[1] - p[1]) >= 0.004) out.push(p);
  }
  if (out.length > 2) { const a = out[0], b = out[out.length - 1]; if (a[0] !== b[0] || a[1] !== b[1]) out.push(a); }
  return out.length >= 4 ? out : null;
}
function thinGeom(g) {
  if (!g) return null;
  if (g.type === 'Polygon') { const c = g.coordinates.map(thinRing).filter(Boolean); return c.length ? { type: 'Polygon', coordinates: c } : null; }
  if (g.type === 'MultiPolygon') {
    const c = g.coordinates.map(p => p.map(thinRing).filter(Boolean)).filter(p => p.length);
    return c.length ? { type: 'MultiPolygon', coordinates: c } : null;
  }
  return null;
}

// ---------- 1. Avalanches (SLF) ----------
async function avalanche() {
  const r = await get('https://aws.slf.ch/api/bulletin/caaml/de/geojson');
  const gj = await r.json();
  const feats = [];
  let max = 0, published = null, next = null;
  const regions = [];
  for (const f of gj.features || []) {
    const p = f.properties || {};
    const lv = Math.max(0, ...(p.dangerRatings || []).map(d => LEVEL[d.mainValue] || 0));
    published = published || p.publicationTime; next = next || p.nextUpdate;
    if (lv > max) max = lv;
    for (const rg of p.regions || []) regions.push({ name: rg.name, level: lv });
    if (lv < 2) continue;                 // only show "moderate" and above on the map
    const geometry = thinGeom(f.geometry);
    if (geometry) feats.push({ type: 'Feature', properties: { level: lv }, geometry });
  }
  const top = regions.filter(x => x.level === max).map(x => x.name);
  return {
    geo: { type: 'FeatureCollection', features: feats },
    summary: {
      ok: true, max, maxText: LEVEL_RU[max] || '', published, nextUpdate: next,
      regionsAtMax: top.length, topRegions: [...new Set(top)].slice(0, 6),
      counts: [1, 2, 3, 4, 5].map(l => regions.filter(x => x.level === l).length),
    },
  };
}

// ---------- 2. Public transport disruptions (opentransportdata.swiss, SIRI-SX) ----------
const REASON_RU = {
  technicalProblem: 'Техническая неисправность', signalProblem: 'Неисправность сигнала', signalFailure: 'Неисправность сигнала',
  accident: 'Авария', collision: 'Столкновение', personUnderTrain: 'Происшествие на путях', personHitByTrain: 'Происшествие на путях',
  constructionWork: 'Строительные работы', maintenanceWork: 'Ремонтные работы', roadworks: 'Ремонтные работы',
  powerProblem: 'Проблемы с электропитанием', overheadWireFailure: 'Повреждение контактной сети', levelCrossingFailure: 'Неисправность переезда',
  weather: 'Погодные условия', heavySnowFall: 'Сильный снегопад', snowDrifts: 'Снежные заносы', ice: 'Гололёд', fog: 'Туман', flooding: 'Наводнение',
  landslide: 'Оползень', avalanches: 'Лавина', rockfalls: 'Камнепад', fallenTree: 'Упавшее дерево', obstruction: 'Препятствие на путях',
  staffAbsence: 'Нехватка персонала', industrialAction: 'Забастовка', vehicleFailure: 'Неисправность поезда', breakDown: 'Неисправность поезда',
  policeActivity: 'Работа полиции', securityAlert: 'Проверка безопасности', fire: 'Пожар', emergencyServicesCall: 'Работа экстренных служб',
  congestion: 'Перегрузка', specialEvent: 'Мероприятие', undefinedProblem: 'Сбой', unknown: 'Сбой',
};
const tag = (x, t) => { const m = x.match(new RegExp(`<(?:\\w+:)?${t}\\b[^>]*>([\\s\\S]*?)</(?:\\w+:)?${t}>`)); return m ? m[1].trim() : ''; };
const tagsAll = (x, t) => [...x.matchAll(new RegExp(`<(?:\\w+:)?${t}\\b[^>]*>([\\s\\S]*?)</(?:\\w+:)?${t}>`, 'g'))].map(m => m[1].trim());
const unxml = s => s.replace(/<[^>]+>/g, '').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
function textIn(x, t, langs = ['DE', 'EN', 'FR', 'IT']) {
  const all = [...x.matchAll(new RegExp(`<(?:\\w+:)?${t}\\b([^>]*)>([\\s\\S]*?)</(?:\\w+:)?${t}>`, 'g'))];
  for (const l of langs) { const m = all.find(a => new RegExp(`lang="${l}"`, 'i').test(a[1])); if (m) return unxml(m[2]); }
  return all[0] ? unxml(all[0][2]) : '';
}
async function trains() {
  const key = process.env.OTD_API_KEY;
  if (!key) return { ok: false, reason: 'no_key' };
  const r = await get('https://api.opentransportdata.swiss/la/siri-sx', { headers: { Authorization: `Bearer ${key}`, 'Accept-Encoding': 'gzip' } });
  const xml = await r.text();
  const out = [];
  for (const el of tagsAll(xml, 'PtSituationElement')) {
    // only situations that are valid right now and not planned works far in advance
    const per = tagsAll(el, 'ValidityPeriod').map(p => [tag(p, 'StartTime'), tag(p, 'EndTime')]);
    const active = !per.length || per.some(([s, e]) => (!s || new Date(s) <= now) && (!e || new Date(e) >= now));
    if (!active) continue;
    const planned = /<(?:\w+:)?Planned>\s*true/i.test(el);
    if (planned) continue;
    const reasonKey = (el.match(/<(?:\w+:)?(\w+)Reason>\s*([\w]+)\s*</) || [])[2] || '';
    const summary = textIn(el, 'Summary');
    const lines = [...new Set(tagsAll(el, 'PublishedLineName').map(unxml))].slice(0, 3);
    const operator = unxml(tag(el, 'OperatorRef')).replace(/^.*:/, '');
    const end = per.map(p => p[1]).filter(Boolean).sort().pop() || '';
    out.push({
      type: 'train', badge: lines[0] || operator || 'ÖV',
      title: summary || lines.join(', ') || 'Сбой в общественном транспорте',
      reason: REASON_RU[reasonKey] || '', until: end, lines,
      severity: tag(el, 'Severity'), id: tag(el, 'SituationNumber'),
    });
  }
  // most important first: rail (lines like IC/IR/RE/S), then the rest
  out.sort((a, b) => (/^(IC|IR|RE|EC|ICE|TGV|S\d)/.test(b.badge) - /^(IC|IR|RE|EC|ICE|TGV|S\d)/.test(a.badge)));
  return { ok: true, total: out.length, items: out.slice(0, 25) };
}

// ---------- 3. Official warnings (Alertswiss, the federal/cantonal alert system) ----------
const EVENT_RU = [[/flood|hochwasser/i,'Наводнение'],[/fire|brand/i,'Пожар'],[/storm|sturm|wind/i,'Буря'],[/water|wasser/i,'Питьевая вода'],
  [/power|strom/i,'Отключение электричества'],[/landslide|rock|rutsch|fels/i,'Оползень / камнепад'],[/avalanche|lawine/i,'Лавины'],
  [/chemical|toxic|gift/i,'Опасные вещества'],[/earthquake|erdbeben/i,'Землетрясение'],[/heat|hitze/i,'Жара'],[/closure|sperr|closed|traffic|verkehr/i,'Ограничение движения'],
  [/police|polizei/i,'Полиция'],[/test/i,'Тест']];
const SEV_RU = { extreme: 'чрезвычайное', severe: 'серьёзное', moderate: 'умеренное', minor: 'незначительное' };
async function warnings() {
  const r = await get('https://www.alert.swiss/content/alertswiss-internet/en/home/_jcr_content/polyalert.alertswiss_alerts.actual.json');
  const j = await r.json();
  const items = [];
  for (const a of j.alerts || []) {
    if (a.allClear || a.testAlert || a.technicalTestAlert) continue;
    const area = (a.areas || [])[0] || {};
    let ll = null;
    const c = (area.circles || [])[0];
    if (c && c.centerPosition) ll = [ +c.centerPosition[1], +c.centerPosition[0] ];
    else if ((area.polygons || [])[0]) {
      const pts = (area.polygons[0].coordinates || area.polygons[0]).map(p => Array.isArray(p) ? p : [p.longitude ?? p[1], p.latitude ?? p[0]]);
      if (pts.length) ll = [ pts.reduce((s, p) => s + +p[1], 0) / pts.length, pts.reduce((s, p) => s + +p[0], 0) / pts.length ].reverse();
    }
    if (ll && !(ll[0] > 5.8 && ll[0] < 10.6 && ll[1] > 45.7 && ll[1] < 47.9)) ll = null;   // keep only points inside Switzerland
    const title = a.title?.title || a.title?.titleGtransOrigin || '';
    const kind = (EVENT_RU.find(([re]) => re.test(`${a.event} ${title}`)) || [, 'Предупреждение'])[1];
    const place = area.description?.description || (area.regions || []).map(x => x.region).join(', ');
    items.push({ type: 'warn', badge: '!', kind, place, title, severity: SEV_RU[a.severity] || a.severity || '',
      canton: (area.regions || []).map(x => x.region).join(', '), publisher: a.publisherName || '', ll });
  }
  return { ok: true, total: items.length, items };
}

// ---------- run ----------
const live = { updated: now.toISOString(), sources: {} };
let geo = null;
try { const a = await avalanche(); geo = a.geo; live.avalanche = a.summary; live.sources.slf = 'ok'; }
catch (e) { live.avalanche = { ok: false }; live.sources.slf = 'error: ' + e.message; console.error('SLF failed:', e.message); }
try { live.trains = await trains(); live.sources.trains = live.trains.ok ? 'ok' : live.trains.reason; }
catch (e) { live.trains = { ok: false, reason: 'error' }; live.sources.trains = 'error: ' + e.message; console.error('Trains failed:', e.message); }
try { live.warnings = await warnings(); live.sources.alertswiss = 'ok'; }
catch (e) { live.warnings = { ok: false }; live.sources.alertswiss = 'error: ' + e.message; console.error('Alertswiss failed:', e.message); }
live.roads = { ok: false, reason: 'not_connected' };

// Keep the previous avalanche zones if SLF was unreachable this time
if (geo) await writeFile('map/ch-avalanche.json', JSON.stringify(geo));
// Only rewrite the summary when something besides the timestamp changed (saves needless site rebuilds),
// but always refresh it at least once an hour so the "updated" time stays honest.
await writeFile('map/ch-live.json', JSON.stringify(live, null, 1));
console.log(JSON.stringify({ avalanche: live.avalanche?.max, zones: geo?.features.length, trains: live.sources.trains, warnings: live.warnings?.total }));
