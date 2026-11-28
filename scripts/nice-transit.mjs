// Builds map/nice-transit.json from the open GTFS of Lignes d'Azur (Nice, licence etalab-2.0):
// route names/colours (to label live vehicles) and the tram lines' shapes (drawn on the Ne Lazurka map).
// Runs weekly in GitHub Actions (.github/workflows/nice-transit.yml). No keys.
import fs from 'node:fs';
import { execSync } from 'node:child_process';

const GTFS = 'https://www.data.gouv.fr/api/1/datasets/r/f5678ab2-c863-4b48-ba1f-9021c7d97634';
const VP = 'https://www.data.gouv.fr/api/1/datasets/r/5f571595-aef1-480f-acde-b9315d9f5f3b';

function csv(text) {
  const rows = []; let row = [], f = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++ } else q = false } else f += c; continue }
    if (c === '"') q = true; else if (c === ',') { row.push(f); f = '' }
    else if (c === '\n') { row.push(f.replace(/\r$/, '')); rows.push(row); row = []; f = '' } else f += c;
  }
  if (f || row.length) { row.push(f); rows.push(row) }
  const head = rows.shift().map(h => h.replace(/^﻿/, '').trim());
  return rows.filter(r => r.length > 1).map(r => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

const r = await fetch(GTFS, { redirect: 'follow' });
if (!r.ok) throw new Error('GTFS ' + r.status);
fs.writeFileSync('/tmp/gtfs.zip', Buffer.from(await r.arrayBuffer()));
execSync('rm -rf /tmp/gtfs && mkdir /tmp/gtfs && unzip -q -o /tmp/gtfs.zip -d /tmp/gtfs');
const read = n => fs.existsSync('/tmp/gtfs/' + n) ? csv(fs.readFileSync('/tmp/gtfs/' + n, 'utf8')) : [];

const routes = {};
for (const x of read('routes.txt')) routes[x.route_id] = { n: x.route_short_name || x.route_long_name, t: +x.route_type, c: x.route_color ? '#' + x.route_color : null, l: x.route_long_name };
console.log('routes', Object.keys(routes).length, 'trams', Object.values(routes).filter(x => x.t === 0).map(x => x.n));

// tram shapes: for every tram route take the longest shape of each direction
const trips = read('trips.txt');
const tramIds = new Set(Object.keys(routes).filter(k => routes[k].t === 0));
const want = {}; for (const t of trips) if (tramIds.has(t.route_id) && t.shape_id) (want[t.route_id] ||= new Set()).add(t.shape_id);
const pts = {};
const allShapes = new Set(Object.values(want).flatMap(s => [...s]));
if (allShapes.size) for (const s of read('shapes.txt')) if (allShapes.has(s.shape_id)) (pts[s.shape_id] ||= []).push([+s.shape_pt_sequence, +(+s.shape_pt_lat).toFixed(5), +(+s.shape_pt_lon).toFixed(5)]);
const trams = [];
for (const [rid, set] of Object.entries(want)) {
  const best = [...set].map(id => (pts[id] || []).sort((a, b) => a[0] - b[0])).sort((a, b) => b.length - a.length)[0];
  if (best && best.length > 1) trams.push({ n: routes[rid].n, c: routes[rid].c, p: best.filter((_, i) => i % 2 === 0 || i === best.length - 1).map(p => [p[1], p[2]]) });
}
console.log('tram shapes', trams.map(t => t.n + ':' + t.p.length));
fs.mkdirSync('map', { recursive: true });
fs.writeFileSync('map/nice-transit.json', JSON.stringify({ updated: new Date().toISOString(), routes, trams }));

// quick look at the live feed (for the logs only)
try {
  const { default: G } = await import('gtfs-realtime-bindings');
  const v = await fetch(VP, { redirect: 'follow' });
  console.log('VP status', v.status, v.url, v.headers.get('content-type'), v.headers.get('access-control-allow-origin'));
  const feed = G.transit_realtime.FeedMessage.decode(new Uint8Array(await v.arrayBuffer()));
  console.log('vehicles', feed.entity.length, JSON.stringify(feed.entity.slice(0, 2)));
} catch (e) { console.log('VP check failed', e.message) }
