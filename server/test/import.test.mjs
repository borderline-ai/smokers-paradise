/* =====================================================================
   THE OWNER'S SPREADSHEET.

   A shop's inventory does not arrive as clean JSON. It arrives as an export
   from whatever the till runs, with a header row somebody renamed, prices
   with dollar signs in them, a blank row where a person hit enter, and the
   same product twice because two people maintained the file.

   These tests are that file. The rule they enforce is rule 3 in CLAUDE.md:
   a number that is not verified does not ship. A row with no price is not
   a free product, it is a row that has to be reported back.
   ===================================================================== */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import worker from '../src/index.js';
import { makeD1 } from './d1.mjs';
import { parseCsv, readCatalogue } from '../src/importer.js';

const SCHEMA = join(dirname(fileURLToPath(import.meta.url)), '..', 'schema.sql');
const BASE = 'https://shop.example';

function fresh() {
  const env = { DB: makeD1(SCHEMA), SHOP: 'smokers-paradise', STAFF_PIN: '7413',
                ASSETS: { fetch: async () => new Response('', { status: 404 }) } };
  const jar = new Map();
  const call = async (path, init = {}) => {
    const headers = new Headers(init.headers || {});
    if (init.body !== undefined) {
      headers.set('content-type', 'application/json');
      init.body = JSON.stringify(init.body);
      headers.set('content-length', String(init.body.length));
    }
    if (jar.size) headers.set('cookie', [...jar].map(([k, v]) => k + '=' + v).join('; '));
    headers.set('cf-connecting-ip', '203.0.113.9');
    const res = await worker.fetch(new Request(BASE + path, Object.assign({}, init, { headers })),
      env, { waitUntil() {}, passThroughOnException() {} });
    const sc = res.headers.get('set-cookie');
    if (sc) { const [pair] = sc.split(';'); const i = pair.indexOf('=');
              const v = pair.slice(i + 1).trim();
              if (v) jar.set(pair.slice(0, i).trim(), v); else jar.delete(pair.slice(0, i).trim()); }
    const ct = res.headers.get('content-type') || '';
    return { status: res.status, body: ct.includes('json') ? await res.json() : await res.text() };
  };
  return { env, call };
}

const signIn = c => c('/api/staff/session', { method: 'POST', body: { pin: '7413' } });

/* ---- the parser, on the file as it actually turns up ---- */

test('a quoted field with a comma in it is one field', () => {
  const r = parseCsv('Item,Price\n"Geek Bar Pulse, Miami Mint",24.99\n');
  assert.deepEqual(r[1], ['Geek Bar Pulse, Miami Mint', '24.99']);
});

test('a doubled quote is one quote, and a newline inside quotes is not a row', () => {
  const r = parseCsv('a,b\n"say ""hi""","two\nlines"\n');
  assert.equal(r.length, 2);
  assert.deepEqual(r[1], ['say "hi"', 'two\nlines']);
});

test("Excel's byte order mark does not become part of the first header", () => {
  const r = readCatalogue('﻿Item,Price\nThing,5.00\n');
  assert.equal(r.error, '');
  assert.equal(r.items.length, 1);
});

test('the header can say Item or Product or Description', () => {
  for (const h of ['Item', 'Product Name', 'DESCRIPTION', 'title']) {
    const r = readCatalogue(h + ',Retail Price\nThing,5.00\n');
    assert.equal(r.error, '', h);
    assert.equal(r.items[0].name, 'Thing');
  }
});

test('prices arrive with dollar signs, commas and words on them', () => {
  const r = readCatalogue('Item,Price\nA,$24.99\nB,"1,299.00"\nC,12.50 ea\nD,"12,99"\n');
  assert.deepEqual(r.items.map(i => i.price), [24.99, 1299, 12.5, 12.99]);
});

test('a row with no price is refused, not priced at nothing', () => {
  /* The most important refusal in the file. The register is the final word,
     but the screen is what the customer read before they walked in. */
  const r = readCatalogue('Item,Price\nGood,5.00\nBad,\nAlsoBad,   \n');
  assert.equal(r.items.length, 1);
  assert.equal(r.skipped.length, 2);
  assert.match(r.skipped[0].why, /no price/);
  assert.equal(r.skipped[0].line, 3, 'and it says which line');
});

test('a blank row in the middle is not an error', () => {
  const r = readCatalogue('Item,Price\nA,1.00\n\n\nB,2.00\n');
  assert.equal(r.items.length, 2);
  assert.equal(r.skipped.length, 0);
});

test('the same product twice is reported, with the line it clashed with', () => {
  const r = readCatalogue('Item,Brand,Price\nPulse,Geek Bar,24.99\nPulse,Geek Bar,25.99\n');
  assert.equal(r.items.length, 1);
  assert.match(r.skipped[0].why, /same product as line 2/);
});

test('a missing name column is said plainly, not guessed at', () => {
  const r = readCatalogue('Thing,Cost\nA,1\n');
  assert.match(r.error, /product name column/);
  const p = readCatalogue('Item,Colour\nA,red\n');
  assert.match(p.error, /price column/);
});

test('a blank stock cell means nobody counted, not zero', () => {
  const r = readCatalogue('Item,Price,Qty\nA,1.00,\nB,2.00,7\n');
  assert.equal('stock' in r.items[0], false);
  assert.equal(r.items[1].stock, 7);
});

test('an id is derived from brand and name when the file has none', () => {
  const r = readCatalogue('Item,Brand,Price\nPulse 15K,Geek Bar,24.99\n');
  assert.equal(r.items[0].id, 'shop-geek-bar-pulse-15k');
});

/* ---- the endpoint ---- */

const CSV = [
  'SKU,Item,Brand,Retail Price,Category,Qty,Image',
  'A1,Pulse 15K,Geek Bar,$24.99,disp,12,ab12cd34ef567890.webp',
  'A2,"Peak Pro, Onyx",Puffco,"1,299.00",dab,2,',
  'A3,No Price Here,Nobody,,misc,1,',
  ''
].join('\n');

test('the whole spreadsheet becomes the shop, and the rejects come back', async () => {
  const { call } = fresh();
  await signIn(call);
  const r = await call('/api/staff/catalog/import', { method: 'POST', body: { csv: CSV } });
  assert.equal(r.status, 200);
  assert.equal(r.body.imported, 2);
  assert.equal(r.body.skippedCount, 1);
  assert.match(r.body.skipped[0].why, /no price/);

  const seen = await call('/api/catalog/overrides');
  const ids = seen.body.custom.map(c => c.id).sort();
  assert.deepEqual(ids, ['A1', 'A2']);
  const pulse = seen.body.custom.find(c => c.id === 'A1');
  assert.equal(pulse.price, 24.99);
  assert.equal(pulse.brand, 'Geek Bar');
  assert.equal(pulse.stock, 12);
});

test('a photo arrives as a path, and a picture is still refused', async () => {
  const { call } = fresh();
  await signIn(call);
  const r = await call('/api/staff/catalog/import', { method: 'POST', body: { csv: CSV } });
  const seen = await call('/api/catalog/overrides');
  assert.equal(seen.body.custom.find(c => c.id === 'A1').photo, 'img/ab12cd34ef567890.webp',
    'a bare filename is taken as living in img/');

  const withPicture = await call('/api/staff/catalog/overrides', { method: 'POST',
    body: { edits: { A1: { price: 1, photo: 'data:image/webp;base64,AAAA' } } } });
  assert.equal(withPicture.status, 413);
  assert.match(withPicture.body.detail, /path, not as the picture/);

  const climbing = await call('/api/staff/catalog/overrides', { method: 'POST',
    body: { edits: { A1: { photo: 'img/../../etc/passwd' } } } });
  assert.equal(climbing.status, 400);
});

test('the imported list is what a phone gets, prices and all', async () => {
  const { call } = fresh();
  await signIn(call);
  await call('/api/staff/catalog/import', { method: 'POST', body: { csv: CSV } });
  const placed = await call('/api/orders', { method: 'POST', body: {
    code: 'QQ-1111', who: 'Ana',
    items: [{ id: 'A1', n: 'Pulse 15K', q: 2, unit: 9.99 }],
    placedAt: Date.now() } });
  assert.equal(placed.body.subtotal, 49.98, 'the shop priced it, not the phone');
  assert.equal(placed.body.priced, 'shop');
});

test('retiring the starter catalogue hides it rather than deleting it', async () => {
  const { call } = fresh();
  await signIn(call);
  await call('/api/staff/catalog/seed', { method: 'POST', body: {
    items: [{ id: 'disp0', name: 'Starter Vape', price: 30 },
            { id: 'disp1', name: 'Another Starter', price: 20 }] } });

  const r = await call('/api/staff/catalog/import', {
    method: 'POST', body: { csv: CSV, retireStarter: true } });
  assert.equal(r.status, 200);
  assert.equal(r.body.retired, 2);

  const seen = await call('/api/catalog/overrides');
  assert.equal(seen.body.edits.disp0.hidden, true);
  /* Hidden, not gone: the owner who imported the wrong file at four in the
     afternoon gets their shelf back by importing the right one. */
  assert.equal(seen.body.edits.disp0.price, 30, 'the price it had is still there');
  assert.equal(seen.body.custom.length, 2, 'and the real list is live');
});

test('retiring before the shelf was ever seeded says so instead of reporting a clean sweep', async () => {
  const { call } = fresh();
  await signIn(call);
  const r = await call('/api/staff/catalog/import', {
    method: 'POST', body: { csv: CSV, retireStarter: true } });
  assert.equal(r.status, 409);
  assert.match(r.body.detail, /not been seeded/);
});

test('a file that is not a catalogue is refused with the reason', async () => {
  const { call } = fresh();
  await signIn(call);
  const r = await call('/api/staff/catalog/import', { method: 'POST', body: { csv: 'hello\nthere\n' } });
  assert.equal(r.status, 400);
  assert.match(r.body.detail, /product name column/);
});

test('nobody without a staff session can replace the shop catalogue', async () => {
  const { call } = fresh();
  const r = await call('/api/staff/catalog/import', { method: 'POST', body: { csv: CSV } });
  assert.equal(r.status, 401);
});
