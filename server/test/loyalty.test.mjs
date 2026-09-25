/* =====================================================================
   THE POINTS ENGINE, PROVED BEFORE ANY SCREEN TOUCHES IT.

   The brief's build order says: schema, the atomic bits, and tests for
   rules 1, 2 and 3 BEFORE any client code exists. This is that.

     1. only the counter may credit points
     2. a redemption is priced at the moment it happened
     3. money is integers

   Plus the compliance rules, which are not preferences: money must change
   hands on every redemption, a discount is never silently capped, and a
   member nobody age-verified cannot redeem.
   ===================================================================== */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { readFileSync } from 'node:fs';

import { makeD1 } from './d1.mjs';
import { checkout, balanceOf, standing, earn } from '../src/loyalty.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const SHOP = 'smokers-paradise';

const CFG = { points_per_dollar: 10, min_tender_cents: 1, max_txn_cents: 30000 };

function db() {
  const env = { DB: makeD1(join(HERE, '..', 'schema.sql')) };
  /* The real order: the live schema, then the migration that moves the
     visit-era tables aside, then the points schema. Testing any other order
     would be testing something the shop will never run. */
  env.DB._raw.exec(readFileSync(join(HERE, '..', 'migrations', '001_points.sql'), 'utf8'));
  env.DB._raw.exec(readFileSync(join(HERE, '..', 'schema.loyalty.sql'), 'utf8')
    .replace(/^-- ALTER TABLE/gm, 'ALTER TABLE'));
  env.DB._raw.exec(`INSERT INTO staff (shop,name,email,role,pin_hash,pin_salt,created_at)
    VALUES ('${SHOP}','Jose','','employee','x','y',datetime('now')),
           ('${SHOP}','Elizabeth','','owner','x','y',datetime('now'))`);
  return env;
}

async function enrol(env, first = 'Ana', code = 'SP00001', verified = true) {
  env.DB._raw.exec(`INSERT INTO members (shop,code,phone,email,first,token,joined${verified ? ',age_verified_at,age_verified_by' : ''})
    VALUES ('${SHOP}','${code}','520555${code.slice(-4)}','a@b.com','${first}','t-${code}',datetime('now')${verified ? ",datetime('now'),1" : ''})`);
  const m = await env.DB.prepare('SELECT * FROM members WHERE code = ?1').bind(code).first();
  return m;
}

const tierBy = async (env, points) =>
  env.DB.prepare('SELECT * FROM reward_tiers WHERE points_cost = ?1').bind(points).first();

const sale = (code, cents, extra = {}) => Object.assign(
  { code, subtotal_cents: cents, idempotency_key: 'k' + Math.random() }, extra);

/* ---- RULE 3: money is integers ---- */

test('rule 3: points are whole numbers off cents, rounded once', () => {
  assert.equal(earn(2499, 10), 250);   /* $24.99 -> 249.9 -> 250 */
  assert.equal(earn(1500, 10), 150);
  assert.equal(earn(1, 10), 0);        /* a cent earns nothing */
  assert.equal(earn(3333, 10), 333);
  assert.equal(Number.isInteger(earn(2499, 10)), true);
});

test('a $24.99 sale credits 250 points and the customer pays $24.99', async () => {
  /* Straight out of the definition of done. */
  const env = db();
  const m = await enrol(env);
  const r = await checkout(env, SHOP, 1, sale('SP00001', 2499), CFG);
  const b = r.status === 200 ? await r.json() : null;
  assert.equal(b.points_earned, 250);
  assert.equal(b.tender_cents, 2499);
  assert.equal(b.balance, 250);
});

/* ---- RULE 1: only the counter credits ---- */

test('rule 1: crediting requires a staff id, and the customer has none', async () => {
  /* The customer's device cannot reach this function — there is no route to
     it without a staff session. The database says so too: created_by is NOT
     NULL and references staff. */
  const env = db();
  await enrol(env);
  assert.throws(() => env.DB._raw.exec(
    `INSERT INTO transactions (shop,member_id,subtotal_cents,discount_cents,tender_cents,
       points_earned,created_at,created_by,idempotency_key)
     VALUES ('${SHOP}',1,1000,0,1000,100,datetime('now'),NULL,'x')`),
    /NOT NULL|constraint/i);
});

/* ---- the ladder, as the owner set it ---- */

test('the tiers are the six the owner set, cheapest first', async () => {
  const env = db();
  const m = await enrol(env);
  const s = await standing(env, SHOP, m.id);
  assert.deepEqual(s.tiers.map(t => t.points), [400, 750, 2500, 3000, 5000, 15000]);
  assert.deepEqual(s.tiers.map(t => t.label),
    ['$1 off', '$3 off', '$10 off', '$12 off', '$25 off', '$75 off']);
  /* No product name next to a reward, anywhere a customer can see. */
  for (const t of s.tiers) assert.match(t.label, /^\$\d+(\.\d\d)? off$/);
});

test('an unaffordable tier still shows, with how far away it is', async () => {
  const env = db();
  const m = await enrol(env);
  await checkout(env, SHOP, 1, sale('SP00001', 4000), CFG);   /* 400 points */
  const s = await standing(env, SHOP, m.id);
  assert.equal(s.balance, 400);
  assert.equal(s.tiers[0].affordable, true);
  assert.equal(s.tiers[1].affordable, false);
  assert.equal(s.tiers[1].short, 350);
});

/* ---- the worked examples from the definition of done ---- */

test('$25 off a $40 sale: the customer pays $15 and earns 150, not 400', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 5000);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 4000, { redeem_tier_id: t.id, id_checked: true }), CFG);
  const b = await r.json();
  assert.equal(b.tender_cents, 1500);
  /* THE DISCOUNTED PORTION EARNS NOTHING. */
  assert.equal(b.points_earned, 150);
  assert.equal(b.balance, 5000 - 5000 + 150);
});

test('the balance drops by exactly the tier cost, not to zero', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},15000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 750);
  await checkout(env, SHOP, 1, sale('SP00001', 1200, { redeem_tier_id: t.id, id_checked: true }), CFG);
  /* 15000 - 750, plus 90 earned on the $9 tendered */
  assert.equal(await balanceOf(env, m.id), 15000 - 750 + 90);
});

/* ---- COMPLIANCE: money must change hands ---- */

test('$25 off a $25.00 sale is REFUSED, because the customer would pay nothing', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 5000);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 2500, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(r.status, 409);
  const b = await r.json();
  assert.equal(b.reason, 'must pay');
  /* and the points are NOT spent */
  assert.equal(await balanceOf(env, m.id), 5000);
});

test('at $25.01 it goes through and the customer pays a cent', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 5000);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 2501, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(r.status, 200);
  const b = await r.json();
  assert.equal(b.tender_cents, 1);
  assert.equal(b.points_earned, 0);
});

test('the discount is never silently capped', async () => {
  /* 5,000 points on a $19.99 basket is refused, not applied as $19.99 off.
     Capping would rob the customer of $5 and they would notice. */
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 5000);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 1999, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(r.status, 409);
  assert.match((await r.json()).detail, /has to pay|over \$25/);
});

test('the $1 tier is refused under its own $15 floor', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},400,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 400);
  const small = await checkout(env, SHOP, 1,
    sale('SP00001', 1200, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(small.status, 409);
  assert.equal((await small.json()).reason, 'basket too small');

  const fine = await checkout(env, SHOP, 1,
    sale('SP00001', 1500, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(fine.status, 200);
});

/* ---- COMPLIANCE: age verification and ID ---- */

test('a member nobody verified cannot redeem, however many points they hold', async () => {
  const env = db();
  const m = await enrol(env, 'Beto', 'SP00002', false);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},99999,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 750);
  const r = await checkout(env, SHOP, 1,
    sale('SP00002', 5000, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(r.status, 403);
  assert.equal((await r.json()).reason, 'not verified');
});

test('a redemption cannot be written without answering id_checked', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 750);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 5000, { redeem_tier_id: t.id }), CFG);
  assert.equal(r.status, 400);
  assert.equal((await r.json()).reason, 'no id answer');
});

test('answering no to ID refuses the reward', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 750);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 5000, { redeem_tier_id: t.id, id_checked: false }), CFG);
  assert.equal(r.status, 403);
});

/* ---- RULE 2: priced at the moment it happened ---- */

test('rule 2: moving a tier does not re-price a redemption that already happened', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},5000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 5000);
  await checkout(env, SHOP, 1, sale('SP00001', 4000, { redeem_tier_id: t.id, id_checked: true }), CFG);

  const before = await balanceOf(env, m.id);

  /* The owner changes her mind: 5,000 becomes 6,000 and $25 becomes $30. */
  env.DB._raw.exec(`UPDATE reward_tiers SET points_cost = 6000, discount_cents = 3000 WHERE id = ${t.id}`);

  const row = await env.DB.prepare('SELECT * FROM redemptions WHERE member_id = ?1').bind(m.id).first();
  assert.equal(row.points_cost, 5000, 'the old row still reads 5,000');
  assert.equal(row.discount_cents, 2500, 'and still reads $25');
  assert.equal(await balanceOf(env, m.id), before, 'and no points were invented or destroyed');
});

/* ---- the refusals that keep it honest ---- */

test('a balance that is short is refused, and the sale is not left behind', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},2000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 2500);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 5000, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(r.status, 409);
  assert.equal((await r.json()).reason, 'not enough points');
  /* The whole call is refused — no orphan transaction whose discount was
     never paid for. */
  const n = await env.DB.prepare('SELECT COUNT(*) AS n FROM transactions').first();
  assert.equal(n.n, 0);
  assert.equal(await balanceOf(env, m.id), 2000);
});

test('points earned in a sale cannot pay for that same sale', async () => {
  /* A $300 basket earns 3,000 points. Those must not fund the 3,000 tier
     being redeemed on the very same ticket. */
  const env = db();
  const m = await enrol(env);
  const t = await tierBy(env, 3000);
  const r = await checkout(env, SHOP, 1,
    sale('SP00001', 30000, { redeem_tier_id: t.id, id_checked: true }), CFG);
  assert.equal(r.status, 409);
  assert.equal((await r.json()).reason, 'not enough points');
});

test('two rewards on one sale is impossible, not merely refused', async () => {
  const env = db();
  const m = await enrol(env);
  env.DB._raw.exec(`INSERT INTO adjustments (shop,member_id,points_delta,reason,created_at,created_by)
    VALUES ('${SHOP}',${m.id},20000,'seed',datetime('now'),2)`);
  const t = await tierBy(env, 750);
  const r = await checkout(env, SHOP, 1, sale('SP00001', 5000, { redeem_tier_id: t.id, id_checked: true }), CFG);
  const txn = (await r.json()).transaction_id;
  assert.throws(() => env.DB._raw.exec(
    `INSERT INTO redemptions (shop,member_id,transaction_id,tier_id,tier_name,points_cost,
       discount_cents,subtotal_cents,tender_cents,id_checked,id_checked_by,created_at,created_by,idempotency_key)
     VALUES ('${SHOP}',${m.id},${txn},${t.id},'x',750,300,5000,4700,1,1,datetime('now'),1,'z')`),
    /UNIQUE|constraint/i);
});

test('the same sale sent twice is one sale', async () => {
  const env = db();
  const m = await enrol(env);
  const s = sale('SP00001', 2499);
  const a = await checkout(env, SHOP, 1, s, CFG);
  const b = await checkout(env, SHOP, 1, s, CFG);
  assert.equal(b.status, 200);
  assert.equal((await b.json()).duplicate, true);
  const n = await env.DB.prepare('SELECT COUNT(*) AS n FROM transactions').first();
  assert.equal(n.n, 1);
  assert.equal(await balanceOf(env, m.id), 250);
});

test('a sale over the ceiling needs a manager', async () => {
  const env = db();
  await enrol(env);
  const r = await checkout(env, SHOP, 1, sale('SP00001', 50000), CFG);
  assert.equal(r.status, 409);
  assert.equal((await r.json()).reason, 'needs approval');

  const ok2 = await checkout(env, SHOP, 1, sale('SP00001', 50000, { approved_by: 2 }), CFG);
  assert.equal(ok2.status, 200);
});

test('a voided sale takes its points back out of the balance', async () => {
  const env = db();
  const m = await enrol(env);
  const r = await checkout(env, SHOP, 1, sale('SP00001', 2499), CFG);
  const id = (await r.json()).transaction_id;
  assert.equal(await balanceOf(env, m.id), 250);
  env.DB._raw.exec(`UPDATE transactions SET voided_at = datetime('now'), voided_by = 2,
    void_reason = 'keyed wrong' WHERE id = ${id}`);
  assert.equal(await balanceOf(env, m.id), 0);
});
