/* =====================================================================
   THE OWNER'S SPREADSHEET AND THE OWNER'S PHOTOGRAPHS, IN ONE GO.

       node scripts/import-catalogue.mjs inventory.csv \
            --photos ~/Desktop/product-photos \
            --url http://127.0.0.1:8787 --pin 7413 --retire

   What it does, in order, and the order is the point:

     1. reads the spreadsheet and says what it made of it BEFORE anything
        else, because a shop should see the twenty rejected rows while it
        can still fix the file rather than after its shelf has changed;
     2. signs in and checks the shop will actually accept this import;
     3. asks;
     4. only then copies each named photograph into app/img, renamed to the
        hash of its own bytes — the same scheme stage 172 used, so a picture
        is cacheable forever and a replacement can never be mistaken for the
        thing it replaced — and rewrites the image column to those names;
     5. posts the lot.

   Steps 2 and 3 come before step 4 because the first version of this script
   had them the other way round: it copied the photographs, then the shop
   refused the import, and two files were left in app/img belonging to a
   catalogue that had never arrived. Nothing touches the repository until
   the send is known to be possible and somebody has said yes.

   --retire hides every starter product the spreadsheet did not mention.
   Hides, not deletes. Nothing here removes anything.

   IT ASKS BEFORE IT WRITES. Replacing a shop's catalogue is not a thing to
   do on a typo, so with a terminal attached it prints the summary and waits
   for a yes. --yes skips that, for a script.
   ===================================================================== */

import { readFileSync, writeFileSync, existsSync, statSync, readdirSync,
         mkdirSync, copyFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join, extname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';

import { readCatalogue, parseCsv } from '../src/importer.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_IMG = join(HERE, '..', '..', 'app', 'img');

/* ---- arguments ---- */
const argv = process.argv.slice(2);
const flag = (name, def = null) => {
  const i = argv.indexOf('--' + name);
  return i < 0 ? def : (argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : true);
};
const csvPath = argv.find(a => !a.startsWith('--') &&
  argv[argv.indexOf(a) - 1] !== '--photos' &&
  argv[argv.indexOf(a) - 1] !== '--url' &&
  argv[argv.indexOf(a) - 1] !== '--pin');

if (!csvPath || !existsSync(csvPath)) {
  console.error('Usage: node scripts/import-catalogue.mjs <inventory.csv> [options]');
  console.error('  --photos <dir>   a folder of product photographs');
  console.error('  --url <base>     the shop  (default http://127.0.0.1:8787)');
  console.error('  --pin <pin>      the staff PIN  (default 7413)');
  console.error('  --retire         hide the starter products this file does not mention');
  console.error('  --yes            do not ask');
  process.exit(1);
}

const BASE = String(flag('url', 'http://127.0.0.1:8787')).replace(/\/$/, '');
const PIN = String(flag('pin', '7413'));
const PHOTOS = flag('photos', null);
const RETIRE = !!flag('retire', false);
const YES = !!flag('yes', false);

/* ---- 1. read it, and say what you made of it ---- */
let csv = readFileSync(csvPath, 'utf8');
const read = readCatalogue(csv);

if (read.error) {
  console.error('That file cannot be read as a catalogue.\n  ' + read.error);
  process.exit(1);
}

console.log('%s\n  %d products\n  %d rows skipped',
  basename(csvPath), read.items.length, read.skipped.length);
for (const s of read.skipped.slice(0, 25)) {
  console.log('    line %d  %s  — %s', s.line, s.name || '(no name)', s.why);
}
if (read.skipped.length > 25) console.log('    … and %d more', read.skipped.length - 25);

/* ---- 2. the door, before anything is written anywhere ---- */
let cookie = '';
async function api(path, init = {}) {
  const headers = Object.assign({ 'content-type': 'application/json' }, init.headers || {});
  if (cookie) headers.cookie = cookie;
  const res = await fetch(BASE + path, Object.assign({}, init, { headers }));
  const sc = res.headers.get('set-cookie');
  if (sc) cookie = sc.split(';')[0];
  const ct = res.headers.get('content-type') || '';
  return { status: res.status, body: ct.includes('json') ? await res.json() : await res.text() };
}

const inDoor = await api('/api/staff/session', { method: 'POST', body: JSON.stringify({ pin: PIN }) })
  .catch(e => ({ status: 0, body: { detail: String(e.message || e) } }));
if (inDoor.status !== 200) {
  console.error('\nCould not sign in at ' + BASE + ': ' +
    ((inDoor.body && inDoor.body.detail) || inDoor.status));
  console.error('Is the shop running, and is --pin right?');
  process.exit(1);
}

/* --retire only means anything once the starter shelf is in the database.
   Asked here rather than discovered after the photographs have been copied. */
if (RETIRE) {
  const shelf = await api('/api/catalog');
  if (shelf.status === 404) {
    console.error('\n--retire has nothing to retire: the starter catalogue has never been');
    console.error('seeded into this shop. Open Staff then Menu once on ' + BASE + ',');
    console.error('then run this again. Nothing has been changed.');
    process.exit(1);
  }
}

/* ---- 3. ask ---- */
if (!YES && process.stdin.isTTY) {
  const what = RETIRE
    ? 'Replace the catalogue at ' + BASE + ' with these ' + read.items.length +
      ' products, and hide every starter product not in the file?'
    : 'Add or update these ' + read.items.length + ' products at ' + BASE + '?';
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const answer = await new Promise(r => rl.question('\n' + what + '  [y/N] ', r));
  rl.close();
  if (!/^y(es)?$/i.test(answer.trim())) {
    console.log('Nothing sent, and nothing written.');
    process.exit(0);
  }
}

/* ---- 4. the photographs, once the send is known to be possible ---- */
function placePhotographs() {
  if (!(PHOTOS && typeof PHOTOS === 'string')) return;
  if (!existsSync(PHOTOS)) {
    console.error('\nNo such photo folder: ' + PHOTOS);
    process.exit(1);
  }
  mkdirSync(APP_IMG, { recursive: true });

  /* Matched on the filename with its extension ignored, because a
     spreadsheet says "pulse15k" and the folder holds "pulse15k.JPG". */
  const onDisk = new Map();
  for (const f of readdirSync(PHOTOS)) {
    if (!statSync(join(PHOTOS, f)).isFile()) continue;
    onDisk.set(basename(f, extname(f)).toLowerCase(), f);
  }

  const rows = parseCsv(csv);
  const header = rows[0].map(h => h.toLowerCase().replace(/[^a-z0-9]/g, ''));
  const col = header.findIndex(h => ['photo', 'image', 'picture', 'img', 'imagefile', 'photofile'].includes(h));

  if (col < 0) {
    console.log('\nNo image column in the spreadsheet, so --photos has nothing to match on.');
  } else {
    let copied = 0, missing = [];
    for (let i = 1; i < rows.length; i++) {
      const cell = (rows[i][col] || '').trim();
      if (!cell) continue;
      const key = basename(cell, extname(cell)).toLowerCase();
      const file = onDisk.get(key);
      if (!file) {
        /* BLANKED, not passed through. The first version of this left the
           original name in the cell, so the product went live pointing at
           img/nosuchfile and drew a broken picture on a customer's phone.
           Rule 2 in CLAUDE.md: a gap is left as a gap. A product with no
           photograph has a shape the app already knows how to draw; a
           product with a photograph that 404s does not. */
        missing.push(cell);
        rows[i][col] = '';
        continue;
      }

      const bytes = readFileSync(join(PHOTOS, file));
      const name = createHash('sha256').update(bytes).digest('hex').slice(0, 16) +
        (extname(file).toLowerCase() || '.jpg');
      if (!existsSync(join(APP_IMG, name))) {
        copyFileSync(join(PHOTOS, file), join(APP_IMG, name));
        copied++;
      }
      rows[i][col] = 'img/' + name;
    }
    /* Written back out so what is posted is what was checked. */
    csv = rows.map(r => r.map(c =>
      /[",\n]/.test(c) ? '"' + String(c).replace(/"/g, '""') + '"' : c).join(',')).join('\n');

    console.log('\n  %d photographs copied into app/img', copied);
    if (missing.length) {
      console.log('  %d named in the file and not in the folder:', missing.length);
      for (const m of missing.slice(0, 10)) console.log('    ' + m);
      if (missing.length > 10) console.log('    … and %d more', missing.length - 10);
      console.log('  Those products go live with no photograph, which is the gap the');
      console.log('  app already draws. Nothing is substituted and nothing points at a');
      console.log('  picture that is not there — that is rule 2 in CLAUDE.md.');
    }
    if (copied) {
      console.log('  Run `npm run build` (or redeploy) so the shop serves them.');
    }
  }
}



placePhotographs();

/* Whatever the image column says by now — copied in above, or typed into the
   spreadsheet by hand — it has to name a file that actually exists, or the
   product is better off with no photograph at all. Same reason as above, and
   it runs even without --photos because a hand-typed name is the likeliest
   one to be wrong. */
function dropPhotographsThatAreNotThere() {
  const rows = parseCsv(csv);
  const header = rows[0].map(h => h.toLowerCase().replace(/[^a-z0-9]/g, ''));
  const col = header.findIndex(h =>
    ['photo', 'image', 'picture', 'img', 'imagefile', 'photofile'].includes(h));
  if (col < 0) return;

  const gone = [];
  for (let i = 1; i < rows.length; i++) {
    const cell = (rows[i][col] || '').trim();
    if (!cell || /^https:/.test(cell)) continue;
    const name = cell.replace(/^img\//, '');
    if (!existsSync(join(APP_IMG, name))) { gone.push(cell); rows[i][col] = ''; }
  }
  if (!gone.length) return;

  csv = rows.map(r => r.map(c =>
    /[",\n]/.test(c) ? '"' + String(c).replace(/"/g, '""') + '"' : c).join(',')).join('\n');
  console.log('\n  %d photograph(s) named in the file are not in app/img, so those', gone.length);
  console.log('  products go live without one rather than with a broken picture:');
  for (const g of gone.slice(0, 10)) console.log('    ' + g);
  if (gone.length > 10) console.log('    … and %d more', gone.length - 10);
}
dropPhotographsThatAreNotThere();

/* ---- 5. send it ---- */
const out = await api('/api/staff/catalog/import', {
  method: 'POST',
  body: JSON.stringify({ csv, retireStarter: RETIRE })
});

if (out.status !== 200) {
  console.error('\nThe shop refused it: ' + ((out.body && out.body.detail) || out.status));
  process.exit(1);
}

console.log('\n%d products are live.', out.body.imported);
if (out.body.retired) console.log('%d starter products hidden.', out.body.retired);
if (out.body.skippedCount) console.log('%d rows were not imported, listed above.', out.body.skippedCount);
console.log('Every phone picks this up on its next open.');
