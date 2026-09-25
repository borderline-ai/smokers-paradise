/* =====================================================================
   THE APP DECIDES WHEN, GOHIGHLEVEL DECIDES WHAT IT LOOKS LIKE.

   Every message leaves through one webhook carrying a `type`, and a workflow
   on the other end branches on it. These tests are about the WHEN — the facts
   this service is the only thing that knows, because the visits live here.
   ===================================================================== */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import worker from '../src/index.js';
import { makeD1 } from './d1.mjs';
import { birthdaySweep, EVENTS } from '../src/notify.js';

const SCHEMA = join(dirname(fileURLToPath(import.meta.url)), '..', 'schema.sql');
const BASE = 'https://shop.example';
const HOOK = 'https://services.leadconnectorhq.com/hooks/abc123';

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
    headers.set('cf-connecting-ip', '203.0.113.20');
    const waits = [];
    const res = await worker.fetch(new Request(BASE + path, Object.assign({}, init, { headers })),
      env, { waitUntil: p => waits.push(p), passThroughOnException() {} });
    await Promise.all(waits.map(p => Promise.resolve(p).catch(() => {})));
    const sc = res.headers.get('set-cookie');
    if (sc) { const [pair] = sc.split(';'); const i = pair.indexOf('=');
              const v = pair.slice(i + 1).trim();
              if (v) jar.set(pair.slice(0, i).trim(), v); else jar.delete(pair.slice(0, i).trim()); }
    const ct = res.headers.get('content-type') || '';
    return { status: res.status, body: ct.includes('json') ? await res.json() : await res.text() };
  };
  return { env, call };
}

/* Stands in for GoHighLevel. Collects whatever the shop posts at it. */
function catchHook() {
  const got = [];
  const real = globalThis.fetch;
  globalThis.fetch = async (u, init) => {
    if (String(u).includes('leadconnectorhq')) {
      got.push(JSON.parse(init.body));
      return new Response('', { status: 200 });
    }
    return real(u, init);
  };
  return { got, stop: () => { globalThis.fetch = real; } };
}

const signIn = c => c('/api/staff/session', { method: 'POST', body: { pin: '7413' } });
const setHook = c => c('/api/staff/config', { method: 'POST', body: { rewards: { endpoint: HOOK } } });
const member = (c, first, phone, email) => c('/api/members', { method: 'POST',
  body: { first, phone, email, emailOk: true, birthday: '7-9', terms: 'Email me.' } });

test('nothing is sent anywhere until the shop pastes its webhook', async () => {
  /* The commonest state on day one, and it must not be an error. */
  const { call } = fresh();
  const h = catchHook();
  try { await member(call, 'Ana', '5205550134', 'ana@example.com'); }
  finally { h.stop(); }
  assert.equal(h.got.length, 0);
});

test('a reward becoming ready is its own event, raised once', async () => {
  /* The message worth sending. Raised on the visit that CROSSES the
     threshold — somebody sitting on a ready reward for three weeks should
     hear once, not after every subsequent visit. */
  const { call } = fresh();
  await signIn(call);
  await setHook(call);
  const m = await member(call, 'Ana', '5205550134', 'ana@example.com');
  const code = m.body.member.code;

  const h = catchHook();
  try {
    for (let i = 0; i < 12; i++) {
      await call('/api/staff/members/' + code + '/visit', { method: 'POST', body: { force: true } });
    }
  } finally { h.stop(); }

  const ready = h.got.filter(e => e.type === EVENTS.REWARD_READY);
  assert.equal(ready.length, 1, 'twelve visits, one reward, one message');
  assert.equal(ready[0].first, 'Ana');
  assert.equal(ready[0].email, 'ana@example.com');
  assert.equal(ready[0].reward, '$10 off');
  assert.equal(ready[0].code, code);
});

test('a member with no address raises nothing, rather than an empty message', async () => {
  const { call } = fresh();
  await signIn(call);
  await setHook(call);
  const m = await call('/api/members', { method: 'POST',
    body: { first: 'Beto', phone: '5205550199' } });
  const code = m.body.member.code;

  const h = catchHook();
  try {
    for (let i = 0; i < 10; i++) {
      await call('/api/staff/members/' + code + '/visit', { method: 'POST', body: { force: true } });
    }
  } finally { h.stop(); }
  assert.equal(h.got.filter(e => e.type === EVENTS.REWARD_READY).length, 0);
});

test('the counter marking a bag ready reaches the customer', async () => {
  const { call } = fresh();
  await signIn(call);
  await setHook(call);
  await member(call, 'Ana', '5205550134', 'ana@example.com');
  await call('/api/orders', { method: 'POST', body: {
    code: 'AB-1234', who: 'Ana', phone: '5205550134',
    items: [{ id: 'x', n: 'Thing', q: 1, unit: 10 }], placedAt: Date.now() } });

  const h = catchHook();
  try {
    await call('/api/staff/orders/AB-1234/status', { method: 'POST', body: { status: 'ready' } });
    await call('/api/staff/orders/AB-1234/status', { method: 'POST', body: { status: 'collected' } });
  } finally { h.stop(); }

  const ready = h.got.filter(e => e.type === EVENTS.ORDER_READY);
  assert.equal(ready.length, 1, 'ready sends; collected does not');
  assert.equal(ready[0].email, 'ana@example.com');
  assert.equal(ready[0].code, 'AB-1234');
});

test('an order from somebody not in the programme has nowhere to send, and says so', async () => {
  const { call } = fresh();
  await signIn(call);
  await setHook(call);
  await call('/api/orders', { method: 'POST', body: {
    code: 'ZZ-9999', who: 'Walk-in', items: [{ id: 'x', n: 'Thing', q: 1, unit: 5 }],
    placedAt: Date.now() } });

  const h = catchHook();
  try { await call('/api/staff/orders/ZZ-9999/status', { method: 'POST', body: { status: 'ready' } }); }
  finally { h.stop(); }
  assert.equal(h.got.length, 0);
});

test('the birthday sweep fires once a year, not once every ten minutes', async () => {
  /* The cron runs every ten minutes. Without the guard a member would get one
     hundred and forty four birthday emails on the day and never open one
     again. */
  const { call, env } = fresh();
  await signIn(call);
  await setHook(call);

  const today = new Date();
  const local = new Date(today.toLocaleString('en-US', { timeZone: 'America/Phoenix' }));
  const key = (local.getMonth() + 1) + '-' + local.getDate();
  await call('/api/members', { method: 'POST', body: {
    first: 'Ana', phone: '5205550134', email: 'ana@example.com',
    emailOk: true, birthday: key } });

  const rule = { endpoint: HOOK, perk: 'Something on us.', timezone: 'America/Phoenix' };
  const h = catchHook();
  let first, again;
  try {
    first = await birthdaySweep(env, 'smokers-paradise', rule);
    for (let i = 0; i < 5; i++) again = await birthdaySweep(env, 'smokers-paradise', rule);
  } finally { h.stop(); }

  assert.equal(first.raised, 1);
  assert.equal(again.raised, 0, 'every later run that day raises nothing');
  assert.equal(h.got.length, 1);
  assert.equal(h.got[0].type, EVENTS.BIRTHDAY);
  assert.equal(h.got[0].perk, 'Something on us.');
});

test('a birthday is not sent to somebody who never agreed to be emailed', async () => {
  const { call, env } = fresh();
  await signIn(call);
  await setHook(call);
  const local = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Phoenix' }));
  const key = (local.getMonth() + 1) + '-' + local.getDate();
  await call('/api/members', { method: 'POST', body: {
    first: 'Beto', phone: '5205550199', email: 'beto@example.com',
    emailOk: false, birthday: key } });

  const h = catchHook();
  let r;
  try { r = await birthdaySweep(env, 'smokers-paradise', { endpoint: HOOK, timezone: 'America/Phoenix' }); }
  finally { h.stop(); }
  assert.equal(r.raised, 0);
  assert.equal(h.got.length, 0);
});

test('a webhook that is down leaves the message queued, not dropped', async () => {
  /* A CRM being down is a Tuesday, not an emergency. The join still succeeded;
     the message waits and outbound.js retries it with backoff. Losing it would
     mean a member the shop never hears about, which is the hole stage 170 was
     written to close. */
  const { call, env } = fresh();
  await signIn(call);
  await setHook(call);

  const real = globalThis.fetch;
  let tries = 0;
  globalThis.fetch = async (u, init) => {
    if (String(u).includes('leadconnectorhq')) { tries++; return new Response('', { status: 500 }); }
    return real(u, init);
  };
  let joined;
  try { joined = await member(call, 'Ana', '5205550134', 'ana@example.com'); }
  finally { globalThis.fetch = real; }

  assert.equal(joined.status, 200, 'the customer is a member regardless');
  assert.ok(tries > 0, 'it was attempted');

  const row = await env.DB
    .prepare('SELECT COUNT(*) AS n, MAX(tries) AS tries, MAX(last_err) AS err FROM outbound WHERE sent_at IS NULL')
    .first();
  assert.equal(row.n, 1, 'still queued');
  assert.equal(row.tries, 1, 'one failed attempt on record');
  assert.match(row.err, /500/, 'and why it failed');
});
