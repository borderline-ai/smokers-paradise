/* =====================================================================
   WHAT THE COUNTER APP NEEDS THAT THE CUSTOMER APP NEVER DID.

   The register moved out of the customer app into its own 36 KB page, and
   three things it used to get from the document now have to come from the
   service: the shelf as an editor sees it, the member list, and somewhere
   to put a photograph.
   ===================================================================== */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import worker from '../src/index.js';
import { makeD1 } from './d1.mjs';

const SCHEMA = join(dirname(fileURLToPath(import.meta.url)), '..', 'schema.sql');
const BASE = 'https://shop.example';

/* R2, as a Map. The Worker uses head/put/get and nothing else. */
function bucket() {
  const m = new Map();
  return {
    _m: m,
    async head(k) { return m.has(k) ? { size: m.get(k).bytes.byteLength } : null; },
    async put(k, bytes, opts) {
      m.set(k, { bytes, type: (opts && opts.httpMetadata && opts.httpMetadata.contentType) || '' });
    },
    async get(k) {
      if (!m.has(k)) return null;
      const o = m.get(k);
      return { body: o.bytes, httpEtag: '"x"', writeHttpMetadata(h) { h.set('content-type', o.type) } };
    }
  };
}

function fresh() {
  const MEDIA = bucket();
  const env = { DB: makeD1(SCHEMA), SHOP: 'smokers-paradise', STAFF_PIN: '7413', MEDIA,
                ASSETS: { fetch: async () => new Response('', { status: 404 }) } };
  const jar = new Map();
  const call = async (path, init = {}) => {
    const headers = new Headers(init.headers || {});
    if (init.body !== undefined && typeof init.body !== 'string' && !(init.body instanceof Uint8Array)) {
      headers.set('content-type', 'application/json');
      init.body = JSON.stringify(init.body);
    }
    if (init.body !== undefined) headers.set('content-length', String(init.body.length || init.body.byteLength || 0));
    if (jar.size) headers.set('cookie', [...jar].map(([k, v]) => k + '=' + v).join('; '));
    headers.set('cf-connecting-ip', '203.0.113.11');
    const res = await worker.fetch(new Request(BASE + path, Object.assign({}, init, { headers })),
      env, { waitUntil() {}, passThroughOnException() {} });
    const sc = res.headers.get('set-cookie');
    if (sc) { const [pair] = sc.split(';'); const i = pair.indexOf('=');
              const v = pair.slice(i + 1).trim();
              if (v) jar.set(pair.slice(0, i).trim(), v); else jar.delete(pair.slice(0, i).trim()); }
    const ct = res.headers.get('content-type') || '';
    return { status: res.status, headers: res.headers,
             body: ct.includes('json') ? await res.json() : await res.text() };
  };
  return { env, call, MEDIA };
}

const signIn = c => c('/api/staff/session', { method: 'POST', body: { pin: '7413' } });

/* Real magic numbers, because the uploader reads the bytes rather than
   trusting what the browser called them. */
const PNG  = new Uint8Array([0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0,0,0,13,1,2,3,4]);
const JPEG = new Uint8Array([0xFF,0xD8,0xFF,0xE0,0,16,0x4A,0x46,0x49,0x46,0,1,1,0,0,1]);
const WEBP = new Uint8Array([0x52,0x49,0x46,0x46,40,0,0,0,0x57,0x45,0x42,0x50,0x56,0x50,0x38,0x20]);
const put = (call, bytes, type) => call('/api/staff/media',
  { method: 'POST', body: bytes, headers: { 'content-type': type } });

/* ---- the photo store ---- */

test('a photograph uploads and comes back as a path, not bytes', async () => {
  const { call } = fresh();
  await signIn(call);
  const r = await put(call, PNG, 'image/png');
  assert.equal(r.status, 200);
  assert.match(r.body.path, /^img\/[0-9a-f]{16}\.png$/);
});

test('the same photograph twice is one object', async () => {
  /* The name is the hash of the bytes, so re-uploading is not a conflict
     and not a second object. */
  const { call, MEDIA } = fresh();
  await signIn(call);
  const a = await put(call, JPEG, 'image/jpeg');
  const b = await put(call, JPEG, 'image/jpeg');
  assert.equal(a.body.path, b.body.path);
  assert.equal(b.body.reused, true);
  assert.equal(MEDIA._m.size, 1);
});

test('what the browser calls the file is not evidence', async () => {
  /* A content-type header is a claim by whoever is uploading. A shop's
     product page is not where you find out it was wrong. */
  const { call } = fresh();
  await signIn(call);
  const r = await put(call, new Uint8Array([1,2,3,4,5,6,7,8,9,10,11,12,13]), 'image/webp');
  assert.equal(r.status, 415);
  assert.match(r.body.detail, /not a JPEG/);
});

test('the extension follows the bytes, not the header', async () => {
  const { call } = fresh();
  await signIn(call);
  const r = await put(call, WEBP, 'image/png');
  assert.match(r.body.path, /\.webp$/);
});

test('nobody without a staff session can put anything in the photo store', async () => {
  const { call } = fresh();
  assert.equal((await put(call, PNG, 'image/png')).status, 401);
});

test('an uploaded photograph is served back, cached forever', async () => {
  const { call } = fresh();
  await signIn(call);
  const up = await put(call, PNG, 'image/png');
  const got = await call('/' + up.body.path);
  assert.equal(got.status, 200);
  assert.match(got.headers.get('cache-control'), /immutable/);
});

test('a name nothing was ever stored under is an honest 404, in JSON', async () => {
  const { call } = fresh();
  const r = await call('/img/0000000000000000.webp');
  assert.equal(r.status, 404);
  assert.match(r.headers.get('content-type'), /json/);
});

test('a photo path saves against a product and comes back on the shelf', async () => {
  const { call } = fresh();
  await signIn(call);
  const up = await put(call, WEBP, 'image/webp');
  await call('/api/staff/catalog/overrides', { method: 'POST',
    body: { custom: [{ id: 'x1', name: 'Thing', price: 5, photo: up.body.path }] } });
  const shelf = await call('/api/staff/catalog');
  assert.equal(shelf.body.items[0].photo, up.body.path);
});

/* ---- the shelf, as the editor needs it ---- */

test('the editor sees hidden products; a customer does not', async () => {
  /* Hiding is the thing the owner came to this screen to undo, so the screen
     that undoes it has to be able to see what is hidden. */
  const { call } = fresh();
  await signIn(call);
  await call('/api/staff/catalog/seed', { method: 'POST',
    body: { items: [{ id: 'a', name: 'Visible', price: 5 }, { id: 'b', name: 'Gone', price: 6 }] } });
  await call('/api/staff/catalog/overrides', { method: 'POST',
    body: { edits: { b: { name: 'Gone', price: 6, hidden: true } } } });

  const editor = await call('/api/staff/catalog');
  assert.equal(editor.body.items.length, 2);
  assert.equal(editor.body.items.find(i => i.id === 'b').hidden, true);

  const shopper = await call('/api/catalog');
  assert.deepEqual(shopper.body.items.map(i => i.id), ['a']);
});

test('the editor shelf is not readable without a staff session', async () => {
  const { call } = fresh();
  assert.equal((await call('/api/staff/catalog')).status, 401);
});

/* ---- the member list ---- */

const member = (call, first, phone) => call('/api/members', { method: 'POST',
  body: { first, phone, email: first.toLowerCase() + '@example.com', emailOk: true } });

test('the customers screen reads the real list, most recently in first', async () => {
  /* It was six hardcoded sample people, which was honest enough when there
     was no member list and is a lie now that there is. */
  const { call } = fresh();
  const a = await member(call, 'Ana', '5205550134');
  const b = await member(call, 'Beto', '5205550199');
  await signIn(call);
  await call('/api/staff/members/' + b.body.member.code + '/visit', { method: 'POST', body: {} });

  const r = await call('/api/staff/members/list');
  assert.equal(r.status, 200);
  assert.equal(r.body.total, 2);
  assert.equal(r.body.members[0].first, 'Beto', 'whoever was in last is first');
  assert.equal(r.body.members[0].total, 1);
});

test('the order does not reshuffle when two events share a millisecond', async () => {
  /* This test was flaky before the tiebreak, which is how the bug was found:
     everything here happens inside one millisecond, so the timestamps tie and
     SQLite was free to answer either way. A counter list that reorders itself
     between three-second polls while nothing has changed is worse than a list
     in the wrong order. */
  const { call } = fresh();
  await member(call, 'Ana', '5205550134');
  await member(call, 'Beto', '5205550199');
  await member(call, 'Caro', '5205550111');
  await signIn(call);

  const first = (await call('/api/staff/members/list')).body.members.map(m => m.code);
  for (let i = 0; i < 6; i++) {
    const again = (await call('/api/staff/members/list')).body.members.map(m => m.code);
    assert.deepEqual(again, first, 'poll ' + i + ' came back in a different order');
  }
});

test('the list finds somebody by name, code, number or address', async () => {
  const { call } = fresh();
  await member(call, 'Ana', '5205550134');
  await member(call, 'Beto', '5205550199');
  await signIn(call);
  for (const q of ['ana', '5550134', 'ANA@example.com']) {
    const r = await call('/api/staff/members/list?q=' + encodeURIComponent(q));
    assert.equal(r.body.members.length, 1, q);
    assert.equal(r.body.members[0].first, 'Ana', q);
  }
});

test('somebody who left the programme is off the counter list', async () => {
  const { call } = fresh();
  const a = await member(call, 'Ana', '5205550134');
  await call('/api/members/me/leave', { method: 'POST', body: { token: a.body.token } });
  await signIn(call);
  const r = await call('/api/staff/members/list');
  assert.equal(r.body.members.length, 0);
  assert.equal(r.body.total, 0);
});

test('the member list is not readable without a staff session', async () => {
  const { call } = fresh();
  assert.equal((await call('/api/staff/members/list')).status, 401);
});
