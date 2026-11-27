// Shared TfL logic for Ne Mayfair Live: used by the GitHub bot (scripts/update-uk.mjs)
// and directly by the website, so the London part of the map is live on every visit.
// No AI: Russian labels come from fixed dictionaries.
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
export async function lines(get) {
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
export async function roads(get, now = new Date()) {
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

