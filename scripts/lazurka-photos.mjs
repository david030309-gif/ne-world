// Finds a free-licensed photo on Wikimedia Commons for every Ne Lazurka post
// that has a `pic` (a search phrase, or an exact "File:Name.jpg") and no `img` yet.
// Saves it as img/mc/<id>.jpg and writes the credit into the post.
// Runs in GitHub Actions (.github/workflows/lazurka-photos.yml). No keys needed.
import fs from 'node:fs';

const FILE = 'lazurka.json';
const API = 'https://commons.wikimedia.org/w/api.php';
const UA = 'NeGlobus/1.0 (https://david030309-gif.github.io/ne-world/; news site photos)';
const OK_LIC = /^(cc[ -]?by(-sa)?[ -]?\d|cc[ -]?by(-sa)?$|cc0|public domain|pd)/i;
const strip = s => String(s || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();

async function api(params) {
  const u = API + '?' + new URLSearchParams({ format: 'json', origin: '*', ...params });
  const r = await fetch(u, { headers: { 'User-Agent': UA } });
  if (!r.ok) throw new Error('Commons ' + r.status);
  return r.json();
}

const II = { prop: 'imageinfo', iiprop: 'url|size|mime|extmetadata', iiurlwidth: '1280' };

async function candidates(pic) {
  if (/^File:/i.test(pic)) {
    const j = await api({ action: 'query', titles: pic, ...II });
    return Object.values(j.query?.pages || {});
  }
  const j = await api({ action: 'query', generator: 'search', gsrsearch: pic + ' filetype:bitmap', gsrnamespace: '6', gsrlimit: '25', ...II });
  return Object.values(j.query?.pages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
}

const norm = s => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
function pick(pages, used, exact, q = '') {
  const words = norm(q).split(/[^a-z0-9]+/).filter(w => w.length >= 5);
  for (const p of pages) {
    // the file name must mention at least one real word of the search (stops random matches)
    if (!exact && words.length && !words.some(w => norm(p.title).includes(w))) continue;
    const ii = p.imageinfo?.[0]; if (!ii) continue;
    const m = ii.extmetadata || {};
    const lic = strip(m.LicenseShortName?.value);
    if (!OK_LIC.test(lic) || /nonfree|fair use/i.test(m.NonFree?.value || '')) continue;
    if (!exact) {
      if (ii.mime !== 'image/jpeg' || ii.width < 1200) continue;
      const r = ii.width / ii.height; if (r < 1.25 || r > 2.4) continue;
      if (used.has(p.title)) continue;
    }
    const by = strip(m.Artist?.value) || 'Wikimedia Commons';
    return { title: p.title, thumb: ii.thumburl || ii.url, by: by.slice(0, 60), lic, url: ii.descriptionurl };
  }
  return null;
}

const data = JSON.parse(fs.readFileSync(FILE, 'utf8'));
const posts = data.mc || [];
const used = new Set(posts.map(p => p.credit?.file).filter(Boolean));
fs.mkdirSync('img/mc', { recursive: true });
let changed = 0;
for (const p of posts) {
  if (!p.pic || p.img) continue;
  try {
    const c = pick(await candidates(p.pic), used, /^File:/i.test(p.pic), p.pic);
    if (!c) { console.log('no photo for', p.id, p.pic); continue; }
    const r = await fetch(c.thumb, { headers: { 'User-Agent': UA } });
    if (!r.ok) { console.log('download failed', p.id, r.status); continue; }
    const path = `img/mc/${p.id}.jpg`;
    fs.writeFileSync(path, Buffer.from(await r.arrayBuffer()));
    p.img = path;
    p.credit = { by: c.by, lic: c.lic, url: c.url, file: c.title };
    used.add(c.title); changed++;
    console.log('ok', p.id, c.title, c.lic);
    await new Promise(r => setTimeout(r, 400));
  } catch (e) { console.log('error', p.id, e.message); }
}
if (changed) fs.writeFileSync(FILE, JSON.stringify(data, null, 1) + '\n');
console.log('photos added:', changed);
