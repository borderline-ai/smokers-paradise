/* =====================================================================
   THE OWNER EDITS HER OWN LADDER.

   Every number in this programme is the shop's. The six rungs it ships with
   were chosen with Marco, not chosen by the code, and the moment the owner
   wants $20 off instead of $25 she should be able to do it from the counter
   rather than asking somebody to run a database command.

   WHAT IS SHOWN WHILE SHE EDITS. The percentage back. A tier is points in and
   dollars out, and the only number that says whether it is a good idea is
   what it gives away: at ten points per dollar, 5,000 points for $25 off is
   5% of the spend that earned it. Without that on screen an owner sets 2,000
   points for $25 off and finds out at the end of the month.

   WHAT IS REFUSED. Nothing that would make a rung impossible to use or
   ruinous to honour, and the refusals say which:

     points at or below zero
     a discount at or below zero
     a minimum basket smaller than the discount, which could never be redeemed
       because the sale must exceed the discount
     more than 2% back, which is not a rule but a warning she has to confirm

   A DEACTIVATED TIER IS NOT DELETED. Somebody redeemed it last week and that
   row names it. Deactivating takes it off the ladder and leaves the history
   readable, the same reason redemptions stamp their own price.
   ===================================================================== */

import { ok, fail, str, nowIso } from './http.js';

const MAX_TIERS = 12;

export async function list(env, shop) {
  const rows = await env.DB.prepare(
    `SELECT id, name, description, points_cost, discount_cents, min_subtotal_cents,
            active, sort_order
       FROM reward_tiers WHERE shop = ?1 ORDER BY sort_order, points_cost`
  ).bind(shop).all();
  return ok({ tiers: rows.results || [] });
}

function clean(body, perDollar) {
  const points = parseInt(body.points_cost, 10);
  const discount = Math.round(Number(body.discount_cents));

  if (!(points > 0)) {
    return { error: 'Points has to be a whole number above zero.' };
  }
  if (!(discount > 0)) {
    return { error: 'The amount off has to be above zero.' };
  }

  let minSub = body.min_subtotal_cents === '' || body.min_subtotal_cents == null
    ? null : Math.round(Number(body.min_subtotal_cents));
  if (minSub !== null && !(minSub >= 0)) minSub = null;

  /* A minimum basket below the discount can never be redeemed: the sale has to
     be strictly greater than the discount anyway, so the lower number is a
     promise the till would always refuse. */
  if (minSub !== null && minSub <= discount) {
    return { error: 'The minimum basket has to be more than the amount off, or the reward could never be used.' };
  }

  /* What it gives away. spend = points / perDollar * 100 cents. */
  const spendCents = (points / (perDollar || 10)) * 100;
  const back = spendCents > 0 ? (discount / spendCents) : 1;
  if (back > 0.2 && !body.confirmed) {
    return {
      error: 'That is ' + (back * 100).toFixed(0) + '% back. Send it again with confirm if you mean it.',
      back
    };
  }

  return {
    value: {
      name: str(body.name, 60) || ('$' + (discount / 100).toFixed(2).replace(/\.00$/, '') + ' off'),
      description: str(body.description, 160),
      points_cost: points,
      discount_cents: discount,
      min_subtotal_cents: minSub,
      sort_order: parseInt(body.sort_order, 10) || points
    },
    back
  };
}

/* POST /api/staff/tiers  — create or update one rung */
export async function save(env, shop, body, staffId, perDollar) {
  const c = clean(body, perDollar);
  if (c.error) return fail(400, 'bad tier', c.error);
  const v = c.value;
  const now = nowIso();

  if (body.id) {
    const found = await env.DB
      .prepare('SELECT id FROM reward_tiers WHERE id = ?1 AND shop = ?2')
      .bind(body.id, shop).first();
    if (!found) return fail(404, 'no tier', 'That reward is not on this shop.');
    await env.DB.prepare(
      `UPDATE reward_tiers SET name = ?3, description = ?4, points_cost = ?5,
             discount_cents = ?6, min_subtotal_cents = ?7, sort_order = ?8,
             updated_at = ?9, updated_by = ?10
        WHERE id = ?1 AND shop = ?2`
    ).bind(body.id, shop, v.name, v.description, v.points_cost, v.discount_cents,
           v.min_subtotal_cents, v.sort_order, now, staffId).run();
    return ok({ id: body.id, back: c.back });
  }

  const n = await env.DB
    .prepare('SELECT COUNT(*) AS n FROM reward_tiers WHERE shop = ?1 AND active = 1')
    .bind(shop).first();
  if (n && n.n >= MAX_TIERS) {
    return fail(409, 'too many',
      'Twelve rewards is already more than a customer will read. Retire one first.');
  }

  const made = await env.DB.prepare(
    `INSERT INTO reward_tiers
       (shop, name, description, points_cost, discount_cents, min_subtotal_cents,
        active, sort_order, created_at, updated_at, updated_by)
     VALUES (?1,?2,?3,?4,?5,?6,1,?7,?8,?8,?9) RETURNING id`
  ).bind(shop, v.name, v.description, v.points_cost, v.discount_cents,
         v.min_subtotal_cents, v.sort_order, now, staffId).first();
  return ok({ id: made.id, back: c.back });
}

/* POST /api/staff/tiers/:id/active  {active}
   Off the ladder, not out of the history. A redemption last week names this
   tier and that row has to stay readable. */
export async function setActive(env, shop, id, active, staffId) {
  const found = await env.DB
    .prepare('SELECT id, active FROM reward_tiers WHERE id = ?1 AND shop = ?2')
    .bind(id, shop).first();
  if (!found) return fail(404, 'no tier', 'That reward is not on this shop.');

  if (!active) {
    const left = await env.DB
      .prepare('SELECT COUNT(*) AS n FROM reward_tiers WHERE shop = ?1 AND active = 1 AND id != ?2')
      .bind(shop, id).first();
    if (!left || left.n === 0) {
      return fail(409, 'last one',
        'That is the only reward left. A programme with nothing to earn is worse than no programme.');
    }
  }

  await env.DB.prepare(
    'UPDATE reward_tiers SET active = ?3, updated_at = ?4, updated_by = ?5 WHERE id = ?1 AND shop = ?2'
  ).bind(id, shop, active ? 1 : 0, nowIso(), staffId).run();
  return ok({ id, active: !!active });
}
