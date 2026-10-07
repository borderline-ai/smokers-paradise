/* =====================================================================
   POINTS, AND THE ARITHMETIC THAT MUST LIVE IN EXACTLY ONE PLACE.

       discount = tier ? tier.discount_cents : 0
       tender   = subtotal_cents - discount
       points   = round(tender / 100 * points_per_dollar)
       balance -= tier ? tier.points_cost : 0

   Four lines, and every one of them is somewhere a bug would be expensive.

   MONEY IS INTEGERS. Cents in, cents out, points as whole numbers. No float
   ever touches a balance. The single rounding decision is here, in `earn`,
   and nowhere else.

   POINTS ACCRUE ON WHAT THE CUSTOMER ACTUALLY PAYS. `tender_cents`, never
   `subtotal_cents`. A $30 basket with $25 off earns 50 points, not 300 — the
   discounted portion earns nothing. The brief says "pre tax subtotal" in one
   place and `tender_cents` in another; tender is what its own worked example
   requires, and tender is what this does.

   BALANCE IS COMPUTED, NEVER STORED. Earned minus spent plus adjusted, over
   non-voided rows. A stored running total is exactly how a phone and an iPad
   end up disagreeing, and it is how a void becomes unfixable.
   ===================================================================== */

import { ok, fail, str, nowIso } from './http.js';

/* The one rounding decision. Nearest whole point, on the tender. */
export function earn(tenderCents, pointsPerDollar, multiplier = 1) {
  const raw = (tenderCents / 100) * pointsPerDollar * (multiplier || 1);
  return Math.round(raw);
}

/* Balance as one SQL expression, so it can be embedded in a guard and read
   in the same statement that writes. Parameterised on a single member id
   repeated three times. */
const BALANCE_SQL = `(
  COALESCE((SELECT SUM(points_earned) FROM transactions
             WHERE member_id = %ID% AND voided_at IS NULL), 0)
+ COALESCE((SELECT SUM(points_delta)  FROM adjustments
             WHERE member_id = %ID%), 0)
- COALESCE((SELECT SUM(points_cost)   FROM redemptions
             WHERE member_id = %ID% AND voided_at IS NULL), 0)
)`;

export const balanceExpr = id => BALANCE_SQL.replace(/%ID%/g, id);

export async function balanceOf(env, memberId) {
  const r = await env.DB.prepare('SELECT ' + balanceExpr('?1') + ' AS balance')
    .bind(memberId).first();
  return (r && r.balance) || 0;
}

/* What the customer's card shows: where they are, and what they could take
   right now. A tier they cannot afford still appears, with the reason — a
   greyed-out rung somebody is working toward is the whole point of a ladder. */
export async function standing(env, shop, memberId) {
  const balance = await balanceOf(env, memberId);
  const tiers = await env.DB.prepare(
    `SELECT id, name, description, points_cost, discount_cents, min_subtotal_cents
       FROM reward_tiers WHERE shop = ?1 AND active = 1 ORDER BY sort_order, points_cost`
  ).bind(shop).all();

  const list = (tiers.results || []).map(t => ({
    id: t.id,
    /* The dollar amount, never the internal name. `name` is the owner's
       label for her reports; no product name goes next to a reward on a
       customer's screen. */
    label: '$' + (t.discount_cents / 100).toFixed(2).replace(/\.00$/, '') + ' off',
    points: t.points_cost,
    discountCents: t.discount_cents,
    minSubtotalCents: t.min_subtotal_cents,
    affordable: balance >= t.points_cost,
    short: Math.max(0, t.points_cost - balance)
  }));

  const next = list.find(t => !t.affordable) || null;
  return { balance, tiers: list, next };
}

/* ---------------------------------------------------------------------
   THE ONE CALL THE COUNTER MAKES.

   Rings a sale, credits points on what is actually tendered, and optionally
   spends a tier against that same sale. One call, one idempotency key, one
   confirm at the till.

   There is deliberately no standalone redeem. `redemptions.transaction_id`
   is NOT NULL, a redemption requires a qualifying sale, and the cleanest way
   to make an invalid state unrepresentable is to refuse to expose an API
   that could create one.
   --------------------------------------------------------------------- */
export async function checkout(env, shop, staffId, body, cfg) {
  const subtotal = Math.round(Number(body.subtotal_cents));
  if (!Number.isFinite(subtotal) || subtotal <= 0) {
    return fail(400, 'bad subtotal', 'Enter the sale total.');
  }
  const key = str(body.idempotency_key, 80);
  if (!key) return fail(400, 'no key', 'That request carried no idempotency key.');

  /* Sent twice is what a till on a bad connection does. The second one must
     return the first one's answer, not a second sale. */
  const already = await env.DB
    .prepare('SELECT id FROM transactions WHERE shop = ?1 AND idempotency_key = ?2')
    .bind(shop, key).first();
  if (already) {
    return ok(Object.assign({ duplicate: true }, await receipt(env, already.id)));
  }

  const member = await env.DB
    .prepare('SELECT * FROM members WHERE shop = ?1 AND code = ?2')
    .bind(shop, str(body.code, 12).toUpperCase()).first();
  if (!member || member.left_at) {
    return fail(404, 'no member', 'No member with that code.');
  }

  if (subtotal > (cfg.max_txn_cents || 30000) && !body.approved_by) {
    return fail(409, 'needs approval',
      'A sale over $' + ((cfg.max_txn_cents || 30000) / 100).toFixed(0) +
      ' needs a manager to approve it.');
  }

  /* ---- the tier, if one was asked for ---- */
  let tier = null, discount = 0;
  if (body.redeem_tier_id) {
    tier = await env.DB.prepare(
      'SELECT * FROM reward_tiers WHERE id = ?1 AND shop = ?2 AND active = 1'
    ).bind(body.redeem_tier_id, shop).first();
    if (!tier) return fail(404, 'no tier', 'That reward is not available.');

    /* AGE VERIFICATION GATES REDEMPTION. Joining on a phone verifies nobody —
       the 21+ gate in the app is a checkbox. Somebody has to have looked at
       an ID across a counter. */
    if (!member.age_verified_at) {
      return fail(403, 'not verified',
        'Check their ID and verify them once before they can use a reward.');
    }
    if (body.id_checked !== true && body.id_checked !== false) {
      return fail(400, 'no id answer',
        'Answer whether you checked their ID. It is recorded on the redemption.');
    }
    if (body.id_checked !== true) {
      return fail(403, 'id not checked', 'A reward cannot come off without checking ID.');
    }

    discount = tier.discount_cents;

    /* THE LEGAL ONE. The sale must be strictly greater than the discount, so
       the customer tenders something above zero. That is what makes this a
       discount inside a sale rather than a free distribution, which is the
       thing the FDA guidance prohibits for tobacco products.

       IT IS NOT A BUSINESS RULE. It must not be made optional, configurable
       to zero, or bypassable by a manager. */
    const minTender = Math.max(1, cfg.min_tender_cents || 1);
    if (subtotal - discount < minTender) {
      return fail(409, 'must pay',
        'The customer has to pay something. This basket needs to be over $' +
        ((discount + minTender) / 100).toFixed(2) + '. Add an item.');
    }

    /* Never silently capped. Burning 5,000 points for $19.99 of value on a
       $19.99 basket robs the customer of $5 and they will notice. */
    if (tier.min_subtotal_cents && subtotal < tier.min_subtotal_cents) {
      return fail(409, 'basket too small',
        'That reward needs a basket over $' +
        (tier.min_subtotal_cents / 100).toFixed(2) + '.');
    }
  }

  const tender = subtotal - discount;
  const points = earn(tender, cfg.points_per_dollar || 10, body.multiplier);
  const now = nowIso();

  /* ---- the sale ---- */
  const txn = await env.DB.prepare(
    `INSERT INTO transactions
       (shop, member_id, subtotal_cents, discount_cents, tender_cents, points_earned,
        multiplier, created_at, created_by, source, approved_by, idempotency_key)
     VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12) RETURNING id`
  ).bind(shop, member.id, subtotal, discount, tender, points,
         Number(body.multiplier) || 1.0, now, staffId,
         str(body.source, 20) || 'counter', body.approved_by || null, key).first();

  if (!tier) return ok(await receipt(env, txn.id));

  /* ---- the redemption, guarded ----

     One statement, so the balance cannot move underneath it. The guard
     subtracts the points this very sale just earned: a customer cannot spend
     points they are earning in the same transaction. If the guard fails,
     nothing is inserted and the balance was short. */
  const red = await env.DB.prepare(
    `INSERT INTO redemptions
       (shop, member_id, transaction_id, tier_id, tier_name, points_cost,
        discount_cents, subtotal_cents, tender_cents, id_checked, id_checked_by,
        applied_to, created_at, created_by, idempotency_key)
     SELECT ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, 1, ?10, ?11, ?12, ?10, ?13
      WHERE ` + balanceExpr('?2') + ` - ?14 >= ?6
     RETURNING id`
  ).bind(shop, member.id, txn.id, tier.id, tier.name, tier.points_cost,
         discount, subtotal, tender, staffId, str(body.applied_to, 120),
         now, key + ':r', points).first();

  if (!red) {
    /* Short. Undo the sale rather than leaving a transaction whose discount
       was never paid for — the customer has not been charged yet, so the
       honest thing is to refuse the whole call. */
    await env.DB.prepare('DELETE FROM transactions WHERE id = ?1').bind(txn.id).run();
    const have = await balanceOf(env, member.id);
    return fail(409, 'not enough points',
      member.first + ' has ' + have + ' points and that reward costs ' +
      tier.points_cost + '.');
  }

  return ok(await receipt(env, txn.id));
}

/* What the till prints and what the app shows. Read back rather than
   assembled from what went in, so it is the stored truth. */
async function receipt(env, txnId) {
  const t = await env.DB.prepare('SELECT * FROM transactions WHERE id = ?1').bind(txnId).first();
  const r = await env.DB.prepare('SELECT * FROM redemptions WHERE transaction_id = ?1 AND voided_at IS NULL')
    .bind(txnId).first();
  return {
    transaction_id: t.id,
    subtotal_cents: t.subtotal_cents,
    discount_cents: t.discount_cents,
    tender_cents: t.tender_cents,
    points_earned: t.points_earned,
    balance: await balanceOf(env, t.member_id),
    redemption: r ? {
      id: r.id, tier: r.tier_name, points_cost: r.points_cost,
      discount_cents: r.discount_cents, id_checked: !!r.id_checked
    } : null
  };
}

/* ---------------------------------------------------------------------
   WHO CREDITED IT.

   `transactions.created_by` is NOT NULL and references staff, because on a
   spend-based programme an employee types the dollar amount — which means an
   employee can type $500 instead of $50 and hand a friend a free vape. The
   audit trail is the control that makes the programme safe to run.

   Today there is one shared PIN, so every write is attributed to a single
   'Counter' row. That is honest about what the service actually knows: it
   knows a counter did this, not which person. Per-staff accounts turn the
   same column into a real name without a migration — the column is already
   there and already pointing at the right table.

   Do not ship the spend-based programme to a shop with more than one
   employee until that upgrade lands.
   --------------------------------------------------------------------- */
export async function counterStaffId(env, shop) {
  const found = await env.DB
    .prepare("SELECT id FROM staff WHERE shop = ?1 AND name = 'Counter'").bind(shop).first();
  if (found) return found.id;
  const made = await env.DB.prepare(
    `INSERT INTO staff (shop, name, email, role, pin_hash, pin_salt, active, created_at)
     VALUES (?1, 'Counter', '', 'employee', '', '', 1, ?2) RETURNING id`
  ).bind(shop, nowIso()).first();
  return made.id;
}
