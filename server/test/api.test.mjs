/* =====================================================================
   THE SERVICE, TESTED THE WAY THE APP IS TESTED.

   Not unit tests. Each one drives the real Worker through real HTTP requests
   and asserts on what a person at the counter or on a phone would actually
   get. Two "devices" here means two cookie jars, exactly as two browser
   contexts meant two devices in the bug this whole backend exists to fix:

       customer joins on her phone      -> code SP26699
       staff type SP26699 on the iPad   -> "No member with that code on this device."

   The first test below is that sentence, inverted.

   Run:  node --test server/test/
   ===================================================================== */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import worker from '../src/index.js';
import { makeD1 } from './d1.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const SCHEMA = join(HERE, '..', 'schema.sql');
const BASE = 'https://shop.example';

/* A device is a cookie jar and nothing else, which is the whole point: the
   counter and the customer differ only in what they can prove. */
class Device {
  constructor(env) { this.env = env; this.cookies = new Map(); }

  async call(path, init = {}) {
    const headers = new Headers(init.headers || {});
    if (init.body !== undefined) {
      headers.set('content-type', 'application/json');
      init.body = typeof init.body === 'string' ? init.body : JSON.stringify(init.body);
      headers.set('content-length', String(init.body.length));
    }
    if (this.cookies.size) {
      headers.set('cookie', [...this.cookies].map(([k, v]) => k + '=' + v).join('; '));
    }
    headers.set('cf-connecting-ip', this.ip || '203.0.113.7');

    const waits = [];
    const ctx = { waitUntil: p => waits.push(p), passThroughOnException() {} };
    const res = await worker.fetch(
      new Request(BASE + path, Object.assign({}, init, { headers })), this.env, ctx);
    await Promise.all(waits);

    const sc = res.headers.get('set-cookie');
    if (sc) {
      const [pair] = sc.split(';');
      const i = pair.indexOf('=');
      const k = pair.slice(0, i).trim(), v = pair.slice(i + 1).trim();
      if (v) this.cookies.set(k, v); else this.cookies.delete(k);
    }

    const ct = res.headers.get('content-type') || '';
    const body = ct.includes('json') ? await res.json() : await res.text();
    return { status: res.status, body, ct, headers: res.headers };
  }
}

function fresh() {
  const env = {
    DB: makeD1(SCHEMA),
    SHOP: 'smokers-paradise',
    STAFF_PIN: '7413',
    ASSETS: { fetch: async () => new Response('', { status: 404 }) }
  };
  return { env, phone: new Device(env), ipad: new Device(env) };
}

const TERMS = 'Email me when something I actually want lands, and on my birthday.';
const JOIN = { first: 'Ana', phone: '5205550134', email: 'ana@example.com',
               birthday: '3-14', emailOk: true, sms: false, terms: TERMS,
               code: 'SP00000', joined: '2026-09-10T17:02:00.000Z' };

async function counterIn(ipad) {
  const r = await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '7413' } });
  assert.equal(r.status, 200, 'counter signs in');
  return r;
}

/* =====================================================================
   THE BUG THIS EXISTS TO FIX
   ===================================================================== */

test('a member joined on a phone is found by the counter on another device', async () => {
  const { phone, ipad } = fresh();

  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  assert.equal(join.status, 200);
  const code = join.body.member.code;
  assert.match(code, /^SP\d{5}$/);

  await counterIn(ipad);
  const hit = await ipad.call('/api/staff/members?code=' + code);
  assert.equal(hit.status, 200, 'the counter finds her');
  assert.equal(hit.body.member.first, 'Ana');
  assert.equal(hit.body.progress.total, 0);
});

test('the member code the phone computed is the code it gets', async () => {
  /* codeFor() in the app and codeFor() in ids.js must agree, because a phone
     that joined with no signal is showing its own answer on a card right now. */
  const { phone } = fresh();
  const { codeFor } = await import('../src/ids.js');
  const r = await phone.call('/api/members', { method: 'POST', body: JOIN });
  assert.equal(r.body.member.code, codeFor(JOIN.phone));
  assert.equal(r.body.recoded, false);
});

/* =====================================================================
   RULE 1 — ONLY THE COUNTER MAY WRITE A VISIT
   ===================================================================== */

test('nothing a customer device can call adds a visit', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const code = join.body.member.code;
  const token = join.body.token;

  /* Every shape a customer's device could plausibly reach for. */
  const tries = [
    ['/api/members/me/visit', { method: 'POST', body: { token } }],
    ['/api/members/' + code + '/visit', { method: 'POST', body: {} }],
    ['/api/staff/members/' + code + '/visit', { method: 'POST', body: {} }],
    ['/api/visits', { method: 'POST', body: { code } }]
  ];
  for (const [p, init] of tries) {
    const r = await phone.call(p, init);
    assert.ok(r.status === 404 || r.status === 401,
      p + ' answered ' + r.status + ', which is not a refusal');
    assert.ok(r.ct.includes('json'), p + ' answered something that is not JSON');
  }

  await counterIn(ipad);
  const after = await ipad.call('/api/staff/members?code=' + code);
  assert.equal(after.body.progress.total, 0, 'still no visits');
});

test('the counter adds a visit and the customer card moves with it', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const { token, member } = join.body;

  await counterIn(ipad);
  const add = await ipad.call('/api/staff/members/' + member.code + '/visit', { method: 'POST', body: {} });
  assert.equal(add.status, 200);
  assert.equal(add.body.progress.visits, 1);

  const card = await phone.call('/api/members/me?token=' + token);
  assert.equal(card.body.progress.visits, 1, 'her own phone sees it');
  assert.equal(card.body.visits.length, 1);
});

test('a double tap at the counter does not hand out a free visit', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const code = join.body.member.code;
  await counterIn(ipad);

  await ipad.call('/api/staff/members/' + code + '/visit', { method: 'POST', body: {} });
  const twice = await ipad.call('/api/staff/members/' + code + '/visit', { method: 'POST', body: {} });
  assert.equal(twice.status, 409);
  assert.equal(twice.body.reason, 'too soon');
  assert.match(twice.body.detail, /Ana/, 'the refusal names her, so the counter can read it out');

  /* Two real sales in the same minute is rare and possible, so there is a way
     through it that a person has to choose. */
  const forced = await ipad.call('/api/staff/members/' + code + '/visit',
    { method: 'POST', body: { force: true } });
  assert.equal(forced.status, 200);
  assert.equal(forced.body.progress.visits, 2);
});

/* =====================================================================
   RULE 2 — A REDEMPTION IS PRICED WHEN IT HAPPENED  (stage 167)
   ===================================================================== */

test('changing the rule from 10 to 6 does not invent four free visits', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const code = join.body.member.code;
  const token = join.body.token;
  await counterIn(ipad);

  for (let i = 0; i < 10; i++) {
    const r = await ipad.call('/api/staff/members/' + code + '/visit',
      { method: 'POST', body: { force: true } });
    assert.equal(r.status, 200, 'visit ' + (i + 1));
  }
  let card = await phone.call('/api/members/me?token=' + token);
  assert.equal(card.body.progress.ready, 1, 'a reward is ready at ten');

  const used = await ipad.call('/api/staff/members/' + code + '/redeem', { method: 'POST', body: {} });
  assert.equal(used.status, 200);
  assert.equal(used.body.took.cost, 10, 'the redemption is stamped at ten');
  assert.equal(used.body.progress.visits, 0);
  assert.equal(used.body.progress.ready, 0);

  /* The owner changes their mind. The past does not change with it. */
  const ruled = await ipad.call('/api/staff/config',
    { method: 'POST', body: { rewards: { visitsFor: 6 } } });
  assert.equal(ruled.status, 200);
  assert.equal(ruled.body.rewards.visitsFor, 6);

  card = await phone.call('/api/members/me?token=' + token);
  assert.equal(card.body.progress.total, 10);
  assert.equal(card.body.progress.need, 6);
  assert.equal(card.body.progress.visits, 0,
    'ten visits, one redemption priced at ten, nothing left over');
  assert.equal(card.body.progress.ready, 0, 'and no reward invented out of nothing');
});

test('a reward cannot be taken off before it is earned', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const code = join.body.member.code;
  await counterIn(ipad);
  await ipad.call('/api/staff/members/' + code + '/visit', { method: 'POST', body: {} });

  const r = await ipad.call('/api/staff/members/' + code + '/redeem', { method: 'POST', body: {} });
  assert.equal(r.status, 409);
  assert.equal(r.body.reason, 'not ready');
  assert.match(r.body.detail, /9 visits short/);
});

/* =====================================================================
   RULE 3 — THE SHOP OWNS THE DATA
   ===================================================================== */

test('the whole member list exports as CSV, with what each reward cost', async () => {
  const { phone, ipad } = fresh();
  const a = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const other = new Device(phone.env);
  await other.call('/api/members', { method: 'POST',
    body: { first: 'Beto', phone: '5205550199', email: 'beto@example.com',
            birthday: '11-2', emailOk: false, terms: TERMS } });

  await counterIn(ipad);
  for (let i = 0; i < 10; i++) {
    await ipad.call('/api/staff/members/' + a.body.member.code + '/visit',
      { method: 'POST', body: { force: true } });
  }
  await ipad.call('/api/staff/members/' + a.body.member.code + '/redeem', { method: 'POST', body: {} });

  const csv = await ipad.call('/api/staff/members/export.csv');
  assert.equal(csv.status, 200);
  assert.match(csv.headers.get('content-type'), /text\/csv/);
  assert.match(csv.headers.get('content-disposition'), /attachment; filename=/);

  const lines = csv.body.trim().split('\n');
  assert.equal(lines.length, 3, 'a header and both members');
  assert.match(lines[0], /visits_spent_on_rewards/);
  assert.match(lines[0], /email_consent,sms_consent,consented_to/);
  assert.match(csv.body, /Ana,5205550134,ana@example\.com,3-14,yes,no,/);
  assert.match(csv.body, /Beto,5205550199,beto@example\.com,11-2,no,no,/);
  /* The sentence they ticked travels with the yes. A list that says "yes"
     without saying yes to WHAT is a list the shop cannot defend. */
  assert.match(csv.body, /Email me when something I actually want lands/);
  const ana = lines.find(l => l.includes('Ana'));
  assert.match(ana, /,10,/, 'ten visits all time');
});

test('the export is not readable without a staff session', async () => {
  const { phone } = fresh();
  const r = await phone.call('/api/staff/members/export.csv');
  assert.equal(r.status, 401);
  assert.ok(r.ct.includes('json'), 'even the refusal is JSON');
});

/* =====================================================================
   RULE 4 — OFFLINE DEGRADES, IT DOES NOT BREAK
   ===================================================================== */

test('the same queued join posted twice is one member, not an error', async () => {
  /* This is Member.flush() doing its job: it retries until something answers
     2xx. Answering 409 would strand the join on that phone forever. */
  const { phone } = fresh();
  const one = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const two = await phone.call('/api/members', { method: 'POST', body: JOIN });
  assert.equal(two.status, 200);
  assert.equal(two.body.rejoined, true);
  assert.equal(two.body.member.code, one.body.member.code);
  assert.equal(two.body.token, one.body.token, 'and the same phone keeps its key');
});

test('a join carries its own timestamp, from whenever the signal was out', async () => {
  const { phone } = fresh();
  const r = await phone.call('/api/members', { method: 'POST', body: JOIN });
  assert.equal(r.body.member.joined, '2026-09-10T17:02:00.000Z');
});

test('a second join from the same number corrects the name', async () => {
  const { phone } = fresh();
  await phone.call('/api/members', { method: 'POST', body: JOIN });
  const fix = await phone.call('/api/members', { method: 'POST',
    body: Object.assign({}, JOIN, { first: 'Ana Maria' }) });
  assert.equal(fix.body.member.first, 'Ana Maria');
});

/* =====================================================================
   WHAT THE JOIN FORM WILL AND WILL NOT ACCEPT
   ===================================================================== */

test('the join refuses what it cannot use', async () => {
  const { phone } = fresh();
  const short = await phone.call('/api/members', { method: 'POST',
    body: Object.assign({}, JOIN, { phone: '52055501' }) });
  assert.equal(short.status, 400);
  assert.equal(short.body.reason, 'bad phone');

  const nameless = await phone.call('/api/members', { method: 'POST',
    body: Object.assign({}, JOIN, { first: '   ' }) });
  assert.equal(nameless.status, 400);
  assert.equal(nameless.body.reason, 'no name');
});

test('a birthday with a year in it is not stored', async () => {
  const { phone } = fresh();
  const r = await phone.call('/api/members', { method: 'POST',
    body: Object.assign({}, JOIN, { birthday: '1991-03-14' }) });
  assert.equal(r.body.member.birthday, '', 'dropped rather than kept');
});

/* =====================================================================
   THE MEMBER CODE IS A NAME, THE TOKEN IS A KEY
   ===================================================================== */

test('knowing a member code reveals nothing without a staff session', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const stranger = new Device(phone.env);

  const byCode = await stranger.call('/api/staff/members?code=' + join.body.member.code);
  assert.equal(byCode.status, 401);

  const byGuess = await stranger.call('/api/members/me?token=' + join.body.member.code);
  assert.equal(byGuess.status, 404, 'the code is not a token');
});

test('two numbers that hash to the same code get different codes', async () => {
  const { phone } = fresh();
  const { codeFor } = await import('../src/ids.js');

  /* Find a real collision rather than asserting one exists. Ten digit numbers
     hash into a hundred thousand codes; they are not hard to find. */
  const target = codeFor('5205550134');
  let twin = '';
  for (let i = 0; i < 400000 && !twin; i++) {
    const n = '520' + String(1000000 + i).padStart(7, '0');
    if (n !== '5205550134' && codeFor(n) === target) twin = n;
  }
  assert.ok(twin, 'found a colliding number');

  const a = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const b = await phone.call('/api/members', { method: 'POST',
    body: { first: 'Carlos', phone: twin, sms: true } });

  assert.equal(a.body.member.code, target);
  assert.notEqual(b.body.member.code, a.body.member.code, 'the second one is moved along');
  assert.equal(b.body.recoded, true, 'and told that it was');
});

test('leaving the programme keeps the visits the shop already took money for', async () => {
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  const { token, member } = join.body;
  await counterIn(ipad);
  await ipad.call('/api/staff/members/' + member.code + '/visit', { method: 'POST', body: {} });

  const gone = await phone.call('/api/members/me/leave', { method: 'POST', body: { token } });
  assert.equal(gone.status, 200);
  assert.equal((await phone.call('/api/members/me?token=' + token)).status, 404);
  assert.equal((await ipad.call('/api/staff/members?code=' + member.code)).status, 404);

  const back = await phone.call('/api/members', { method: 'POST', body: JOIN });
  assert.equal(back.status, 200);
  assert.equal(back.body.progress.total, 1, 'her visit is still hers');
});

/* =====================================================================
   ORDERS
   ===================================================================== */

const ORDER = {
  code: 'AB-1234', who: 'Ana', phone: '5205550134',
  items: [{ id: 'geekbar-pulse', n: 'Geek Bar Pulse', brand: 'Geek Bar', v: 'Miami Mint', q: 2, unit: 25 }],
  subtotal: 50, fee: 0, tax: 4.3, total: 54.3,
  source: 'smokersparadise-mobile', pickup: 'ASAP, ', placedAt: Date.now(), status: 'placed'
};

test('an order placed on a phone appears on the counter board on another device', async () => {
  const { phone, ipad } = fresh();
  const placed = await phone.call('/api/orders', { method: 'POST', body: ORDER });
  assert.equal(placed.status, 200);
  assert.equal(placed.body.code, 'AB-1234');

  await counterIn(ipad);
  const board = await ipad.call('/api/staff/orders');
  assert.equal(board.status, 200);
  assert.equal(board.body.orders.length, 1);
  const t = board.body.orders[0];
  assert.equal(t.who, 'Ana');
  assert.equal(t.items[0].n, 'Geek Bar Pulse');
  assert.equal(typeof t.placedAt, 'number', 'placedAt is ms, because agoText() subtracts it');
});

test('the shop prices the order, not the phone', async () => {
  const { phone, ipad } = fresh();
  await counterIn(ipad);
  const seeded = await ipad.call('/api/staff/catalog/seed', { method: 'POST',
    body: { items: [{ id: 'geekbar-pulse', name: 'Geek Bar Pulse', brand: 'Geek Bar', price: 30 }] } });
  assert.equal(seeded.body.seeded, 1);

  /* The phone says $25. The shelf says $30. The shop wins and says so. */
  const placed = await phone.call('/api/orders', { method: 'POST', body: ORDER });
  assert.equal(placed.body.subtotal, 60);
  assert.equal(placed.body.tax, 5.16);
  assert.equal(placed.body.total, 65.16);
  assert.equal(placed.body.priced, 'shop');
});

test('a price edited at the counter reaches a customer phone', async () => {
  /* Verified broken before this backend: edited 30 -> 999.99 on the shop
     device, the customer device still showed 30. */
  const { phone, ipad } = fresh();
  await counterIn(ipad);
  await ipad.call('/api/staff/catalog/seed', { method: 'POST',
    body: { items: [{ id: 'geekbar-pulse', name: 'Geek Bar Pulse', price: 30 }] } });

  const before = await phone.call('/api/catalog/overrides');
  assert.deepEqual(before.body.edits, {}, 'the baseline is not an override');

  await ipad.call('/api/staff/catalog/overrides', { method: 'POST',
    body: { edits: { 'geekbar-pulse': { price: 22.5 } } } });

  const after = await phone.call('/api/catalog/overrides');
  assert.equal(after.body.edits['geekbar-pulse'].price, 22.5);

  const placed = await phone.call('/api/orders', { method: 'POST', body: ORDER });
  assert.equal(placed.body.subtotal, 45, 'and the till agrees with the screen');
});

test('re-seeding does not undo what the counter changed', async () => {
  const { phone, ipad } = fresh();
  await counterIn(ipad);
  await ipad.call('/api/staff/catalog/seed', { method: 'POST',
    body: { items: [{ id: 'x1', name: 'Thing', price: 10 }] } });
  await ipad.call('/api/staff/catalog/overrides', { method: 'POST',
    body: { edits: { x1: { price: 12 } } } });
  await ipad.call('/api/staff/catalog/seed', { method: 'POST',
    body: { items: [{ id: 'x1', name: 'Thing', price: 10 }] } });

  const after = await phone.call('/api/catalog/overrides');
  assert.equal(after.body.edits.x1.price, 12);
});

test('a photo is refused rather than truncated into a broken image', async () => {
  const { ipad } = fresh();
  await counterIn(ipad);
  const r = await ipad.call('/api/staff/catalog/overrides', { method: 'POST',
    body: { edits: { x1: { price: 5, photo: 'data:image/webp;base64,AAAA' } } } });
  assert.equal(r.status, 413);
  assert.equal(r.body.reason, 'photo');
});

test('placing the same order twice is one ticket', async () => {
  const { phone, ipad } = fresh();
  await phone.call('/api/orders', { method: 'POST', body: ORDER });
  const again = await phone.call('/api/orders', { method: 'POST', body: ORDER });
  assert.equal(again.status, 200, 'not an error: the customer pressed it twice on a bad signal');
  assert.equal(again.body.duplicate, true);

  await counterIn(ipad);
  assert.equal((await ipad.call('/api/staff/orders')).body.orders.length, 1);
});

test('a pickup code reveals a status and nothing else', async () => {
  const { phone } = fresh();
  await phone.call('/api/orders', { method: 'POST', body: ORDER });
  const r = await phone.call('/api/orders/status?codes=AB-1234');
  assert.deepEqual(r.body.statuses, { 'AB-1234': 'placed' });
  assert.equal(JSON.stringify(r.body).includes('Ana'), false, 'no name');
  assert.equal(JSON.stringify(r.body).includes('5205550134'), false, 'no number');
  assert.equal(JSON.stringify(r.body).includes('Geek Bar'), false, 'no basket');
});

test('the arrival signal only moves forward', async () => {
  const { phone } = fresh();
  await phone.call('/api/orders', { method: 'POST', body: ORDER });
  assert.equal((await phone.call('/api/orders/AB-1234/arriving',
    { method: 'POST', body: { state: 'otw' } })).body.arriving, 'otw');
  assert.equal((await phone.call('/api/orders/AB-1234/arriving',
    { method: 'POST', body: { state: 'here' } })).body.arriving, 'here');
  assert.equal((await phone.call('/api/orders/AB-1234/arriving',
    { method: 'POST', body: { state: 'otw' } })).body.arriving, 'here', 'cannot walk back');
});

test('the counter marks a ticket ready and the customer phone sees it', async () => {
  const { phone, ipad } = fresh();
  await phone.call('/api/orders', { method: 'POST', body: ORDER });
  await counterIn(ipad);
  const r = await ipad.call('/api/staff/orders/AB-1234/status', { method: 'POST', body: { status: 'ready' } });
  assert.equal(r.status, 200);
  assert.deepEqual((await phone.call('/api/orders/status?codes=AB-1234')).body.statuses,
    { 'AB-1234': 'ready' });

  await ipad.call('/api/staff/orders/AB-1234/status', { method: 'POST', body: { status: 'collected' } });
  assert.equal((await ipad.call('/api/staff/orders')).body.orders.length, 0, 'cleared off the board');
});

test('ordering ahead does not add a visit', async () => {
  /* The rewards screen tells the customer this in as many words. The database
     must not quietly disagree with it. */
  const { phone, ipad } = fresh();
  const join = await phone.call('/api/members', { method: 'POST', body: JOIN });
  await phone.call('/api/orders', { method: 'POST', body: ORDER });
  await counterIn(ipad);
  const hit = await ipad.call('/api/staff/members?code=' + join.body.member.code);
  assert.equal(hit.body.progress.total, 0);
});

/* =====================================================================
   THE COUNTER'S DOOR
   ===================================================================== */

test('the board is not readable without a session', async () => {
  const { phone } = fresh();
  const r = await phone.call('/api/staff/orders');
  assert.equal(r.status, 401, 'OrderStore drops the board on 401 rather than giving up on the shop');
  assert.ok(r.ct.includes('json'));
});

test('the wrong PIN is refused and the right one is not', async () => {
  const { ipad } = fresh();
  assert.equal((await ipad.call('/api/staff/session',
    { method: 'POST', body: { pin: '0000' } })).status, 401);
  assert.equal((await ipad.call('/api/staff/session',
    { method: 'POST', body: { pin: '7413' } })).status, 200);
});

test('a four digit PIN on a public address cannot be walked through', async () => {
  const { ipad } = fresh();
  for (let i = 0; i < 9; i++) {
    await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '000' + i } });
  }
  const locked = await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '7413' } });
  assert.equal(locked.status, 429, 'even the right PIN waits');
  assert.equal(locked.body.reason, 'locked');
  /* The wait is stated. "Try again later" is a dead end; "try again in 45
     seconds" is something somebody at a counter can make a decision about. */
  assert.match(locked.body.detail, /Try again in \d+ seconds|Try again in a minute|Try again in \d+ minutes/);
});

test('the first few fumbles cost nothing at all', async () => {
  /* The person who actually trips a PIN guard is a staff member with cold
     hands during a rush, not an attacker. Four slips are free; a flat lockout
     on the eighth punished the wrong person. */
  const { ipad } = fresh();
  for (let i = 0; i < 3; i++) {
    const r = await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '000' + i } });
    assert.equal(r.status, 401, 'fumble ' + (i + 1) + ' should be a plain refusal');
    assert.equal(r.body.reason, 'bad pin');
  }
  const good = await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '7413' } });
  assert.equal(good.status, 200, 'and the right PIN still works straight after');
});

test('it warns before the waiting starts', async () => {
  const { ipad } = fresh();
  let warned = false;
  for (let i = 0; i < 4; i++) {
    const r = await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '000' + i } });
    if (/means waiting/.test(r.body.detail || '')) warned = true;
  }
  assert.ok(warned, 'the last free fumble should say the next one costs time');
});

test('knowing the PIN clears the record of fumbling', async () => {
  /* Whoever got in knew the PIN, so the run of wrong ones was fumbling rather
     than an attack. The next mistake starts from zero. */
  const { ipad } = fresh();
  for (let i = 0; i < 3; i++) {
    await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '000' + i } });
  }
  assert.equal((await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '7413' } })).status, 200);

  const after = await ipad.env.DB
    .prepare('SELECT COUNT(*) AS n FROM pin_attempts').first();
  assert.equal(after.n, 0, 'the failures are gone');
});

test('the session cookie cannot be read by a script or sent from another site', async () => {
  const { ipad } = fresh();
  const r = await ipad.call('/api/staff/session', { method: 'POST', body: { pin: '7413' } });
  const c = r.headers.get('set-cookie');
  assert.match(c, /HttpOnly/);
  assert.match(c, /Secure/);
  assert.match(c, /SameSite=Strict/);
});

test('signing out actually ends the session', async () => {
  const { ipad } = fresh();
  await counterIn(ipad);
  assert.equal((await ipad.call('/api/staff/orders')).status, 200);
  await ipad.call('/api/staff/session', { method: 'DELETE' });
  assert.equal((await ipad.call('/api/staff/orders')).status, 401);
});

/* =====================================================================
   CONFIG
   ===================================================================== */

test('the rule set at the counter is the rule the phone reads', async () => {
  const { phone, ipad } = fresh();
  assert.equal((await phone.call('/api/config')).body.rewards.visitsFor, 10);

  await counterIn(ipad);
  await ipad.call('/api/staff/config', { method: 'POST',
    body: { rewards: { visitsFor: 6, reward: 'A free lighter' } } });

  const seen = await phone.call('/api/config');
  assert.equal(seen.body.rewards.visitsFor, 6);
  assert.equal(seen.body.rewards.reward, 'A free lighter');
});

test('the shop CRM webhook is not in the public config', async () => {
  const { phone, ipad } = fresh();
  await counterIn(ipad);
  await ipad.call('/api/staff/config', { method: 'POST',
    body: { rewards: { endpoint: 'https://services.example/hooks/abc123' } } });

  const pub = await phone.call('/api/config');
  assert.equal('endpoint' in pub.body.rewards, false);
  assert.equal(JSON.stringify(pub.body).includes('abc123'), false);

  const priv = await ipad.call('/api/staff/config');
  assert.match(priv.body.rewards.endpoint, /abc123/, 'the owner can still see it');
});

test('a rule the counter could not have meant is refused, not clamped', async () => {
  const { ipad } = fresh();
  await counterIn(ipad);
  const r = await ipad.call('/api/staff/config', { method: 'POST', body: { rewards: { visitsFor: 1000 } } });
  assert.equal(r.status, 400);
  assert.match(r.body.detail, /1 to 100/);
  const h = await ipad.call('/api/staff/config', { method: 'POST',
    body: { rewards: { endpoint: 'http://services.example/hook' } } });
  assert.equal(h.status, 400, 'a customer name and number does not go out over plain http');
});

test('a join reaches the shop CRM without the customer waiting for it', async () => {
  const { phone, ipad } = fresh();
  await counterIn(ipad);
  await ipad.call('/api/staff/config', { method: 'POST',
    body: { rewards: { endpoint: 'https://services.example/hooks/abc123' } } });

  const seen = [];
  const real = globalThis.fetch;
  globalThis.fetch = async (u, init) => { seen.push({ u: String(u), body: JSON.parse(init.body) }); return new Response('', { status: 200 }); };
  try {
    await phone.call('/api/members', { method: 'POST', body: JOIN });
  } finally { globalThis.fetch = real; }

  assert.equal(seen.length, 1);
  assert.match(seen[0].u, /abc123/);
  /* The flat shape a GoHighLevel inbound webhook was set up for. */
  assert.deepEqual(Object.keys(seen[0].body).sort(),
    ['birthday', 'code', 'email', 'emailOk', 'first', 'joined', 'phone',
     'shop', 'sms', 'terms']);
  assert.equal(seen[0].body.email, 'ana@example.com');
  assert.equal(seen[0].body.emailOk, true);
  /* The shop is not doing SMS. A CRM that receives sms:true will eventually
     act on it, and the person never agreed to that. */
  assert.equal(seen[0].body.sms, false);
});

/* =====================================================================
   THE THINGS THE CLIENT CANNOT SURVIVE
   ===================================================================== */

test('every answer is JSON, including the refusals', async () => {
  /* call() reads the content-type before the body, and anything that is not
     JSON means "there is no shop here" — the whole ordering surface goes off. */
  const { phone } = fresh();
  for (const p of ['/api/nope', '/api/orders/status', '/api/staff/orders', '/api/members/me']) {
    const r = await phone.call(p);
    assert.ok(r.ct.includes('json'), p + ' answered ' + r.ct);
  }
  const bad = await phone.call('/api/orders', { method: 'POST', body: 'not json at all' });
  assert.equal(bad.status, 400);
  assert.ok(bad.ct.includes('json'));
});

test('the external loyalty provider answers none, so the shop programme shows', async () => {
  const { phone } = fresh();
  const r = await phone.call('/api/loyalty/status');
  assert.equal(r.body.provider, 'none');
  assert.equal(r.body.capabilities.demo, false, 'and it is not pretending to be a demo');
});

test('an unseeded catalogue says so instead of answering an empty shelf', async () => {
  const { phone } = fresh();
  const r = await phone.call('/api/catalog');
  assert.equal(r.status, 404);
  assert.equal(r.body.reason, 'not seeded');
});

test('availability never invents a stock count', async () => {
  const { phone, ipad } = fresh();
  await counterIn(ipad);
  await ipad.call('/api/staff/catalog/seed', { method: 'POST',
    body: { items: [{ id: 'x1', name: 'Thing', price: 10 }] } });
  const r = await phone.call('/api/availability?ids=x1');
  assert.equal(r.body.availability.x1.tracked, false);
  assert.equal(r.body.availability.x1.onHand, null);
});

/* =====================================================================
   EMAIL, AND THE LIST THAT USED TO NOT EXIST
   ===================================================================== */

test('an address that could not be sent to is refused', async () => {
  const { phone } = fresh();
  for (const bad of ['nope', 'a@b', 'a b@c.com', 'a@@b.com', 'a@b..com']) {
    const r = await phone.call('/api/members', { method: 'POST',
      body: Object.assign({}, JOIN, { email: bad }) });
    assert.equal(r.status, 400, bad + ' was accepted');
    assert.equal(r.body.reason, 'bad email');
  }
});

test('a join queued before there was an email field is still accepted', async () => {
  /* THE SUBTLE ONE. A phone that queued a join under stage 171 holds
     {first, phone, birthday, sms, code, joined, shop} and no address. If this
     endpoint required an email, that item would fail forever in that phone's
     retry queue — which is exactly the hole stage 170 was written to close.
     A bad address is refused; an absent one is not. */
  const { phone } = fresh();
  const old = { first: 'Ana', phone: '5205550134', birthday: '3-14', sms: true,
                code: 'SP00000', joined: '2026-09-10T17:02:00.000Z' };
  const r = await phone.call('/api/members', { method: 'POST', body: old });
  assert.equal(r.status, 200);
  assert.equal(r.body.member.email, '');
  /* And the sentence they actually ticked back then said texting, so it is
     not read as permission to email them. */
  assert.equal(r.body.member.emailOk, false);
});

test('an address added on a second join is kept, and an absent one does not wipe it', async () => {
  const { phone } = fresh();
  await phone.call('/api/members', { method: 'POST', body: JOIN });
  const blanked = await phone.call('/api/members', { method: 'POST',
    body: { first: 'Ana', phone: '5205550134' } });
  assert.equal(blanked.body.member.email, 'ana@example.com', 'still hers');

  const moved = await phone.call('/api/members', { method: 'POST',
    body: Object.assign({}, JOIN, { email: 'ANA@Example.COM ' }) });
  assert.equal(moved.body.member.email, 'ana@example.com', 'and normalised');
});

test('the deal alerts box reaches the shop instead of one browser', async () => {
  /* It used to write the number to localStorage and say "You are on the list.
     One text when a real deal lands." There was no list. */
  const { phone, ipad } = fresh();
  const r = await phone.call('/api/subscribers', { method: 'POST',
    body: { email: 'Deals@Example.com', source: 'home', terms: TERMS } });
  assert.equal(r.status, 200);
  assert.equal(r.body.email, 'deals@example.com');

  await counterIn(ipad);
  const csv = await ipad.call('/api/staff/subscribers/export.csv');
  assert.equal(csv.status, 200);
  assert.match(csv.body, /deals@example\.com,home,/);
  assert.match(csv.body, /Email me when something I actually want lands/);
});

test('subscribing twice is not an error', async () => {
  const { phone } = fresh();
  await phone.call('/api/subscribers', { method: 'POST', body: { email: 'a@b.com' } });
  const again = await phone.call('/api/subscribers', { method: 'POST', body: { email: 'a@b.com' } });
  assert.equal(again.status, 200);
  assert.equal(again.body.already, true);
});

test('getting off the list is the easiest thing on the service', async () => {
  /* No token, no confirmation step, no sign in. A list somebody cannot get
     off is a list that gets reported as spam, and one complaint costs more
     than every address a confirmation step would have saved. */
  const { phone } = fresh();
  await phone.call('/api/members', { method: 'POST', body: JOIN });
  await phone.call('/api/subscribers', { method: 'POST', body: { email: 'ana@example.com' } });

  const off = await phone.call('/api/subscribers/leave', { method: 'POST',
    body: { email: 'ana@example.com' } });
  assert.equal(off.status, 200);

  const { ipad } = fresh();
  const back = await phone.call('/api/subscribers', { method: 'POST',
    body: { email: 'ana@example.com' } });
  assert.equal(back.body.already, false, 'and they can come back');
});

test('unsubscribing takes them off the member list too, not just the newsletter', async () => {
  const { phone, ipad } = fresh();
  await phone.call('/api/members', { method: 'POST', body: JOIN });
  await phone.call('/api/subscribers/leave', { method: 'POST', body: { email: 'ana@example.com' } });

  await counterIn(ipad);
  const csv = await ipad.call('/api/staff/members/export.csv');
  const ana = csv.body.split('\n').find(l => l.includes('Ana'));
  assert.match(ana, /ana@example\.com,3-14,no,/, 'email consent is off');
  /* Still a member with her visits. She asked not to be emailed, not to be
     forgotten. */
  assert.match(ana, /^SP\d{5},Ana,/);
});

test('the subscriber list is not readable without a staff session', async () => {
  const { phone } = fresh();
  assert.equal((await phone.call('/api/staff/subscribers/export.csv')).status, 401);
});
