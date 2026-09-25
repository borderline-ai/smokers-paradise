/* =====================================================================
   ORDERS.

   `OrderStore` in app/index.html was written against this API years before
   this API existed. Nothing here is invented: every field name, every status
   string and every response shape below was read off that client. If a name
   looks odd, it is because the client already uses it.

   The one rule that governs the whole file is in the client's own comment on
   `place`:

       "The shop priced it and the shop reserved the stock, not the phone. If
        the two disagree the shop wins and the customer is told."

   So the totals a phone sends are read as a proposal, never as a fact. What
   comes back is what the ticket says and what the register will collect.
   ===================================================================== */

import { ok, fail, str, digits, money, nowIso } from './http.js';

/* The statuses the client can produce or display, and nothing else. A status
   this list does not contain would draw a ticket the counter cannot clear. */
const STATUSES = ['placed', 'making', 'ready', 'collected', 'cancelled'];
/* Forward only. The customer's arrival signal needs no session — whoever holds
   the pickup code is the person walking through the door — which is exactly
   why it must not be able to walk backwards or be replayed to any effect. */
const ARRIVING = { none: 0, otw: 1, here: 2 };

/* ---------------------------------------------------------------------
   PRICING.

   The server can only be an authority on a price it actually holds. It holds
   two kinds:

     - a price the counter set, in the catalog table. That one wins, always.
     - the seeded baseline from the app's own product list.

   For an id it has never seen — a product added to the app but never seeded —
   it has nothing to be authoritative with, so it takes the phone's number and
   says so in the response. That is the honest answer and it is visible in
   `priced`: 'shop' when every line came from the shop's own prices, 'partial'
   when some line did not. A shop reading its own tickets can tell.
   --------------------------------------------------------------------- */
async function priceOrder(env, shop, items, pricing) {
  const ids = [...new Set(items.map(i => i.id).filter(Boolean))].slice(0, 120);
  const known = new Map();
  if (ids.length) {
    const q = ids.map((_, i) => '?' + (i + 2)).join(',');
    const rows = await env.DB
      .prepare('SELECT id, patch FROM catalog WHERE shop = ?1 AND id IN (' + q + ')')
      .bind(shop, ...ids).all();
    for (const r of (rows.results || [])) {
      try {
        const p = JSON.parse(r.patch);
        if (typeof p.price === 'number' && p.price >= 0) known.set(r.id, p);
      } catch { /* a patch that will not parse is not a price */ }
    }
  }

  let allKnown = true;
  const priced = items.map(i => {
    const shelf = known.get(i.id);
    if (!shelf) allKnown = false;
    const unit = shelf ? money(shelf.price) : money(i.unit);
    return {
      id: i.id, d: i.d ? 1 : 0,
      n: shelf && shelf.name ? str(shelf.name, 120) : i.n,
      brand: shelf && shelf.brand ? str(shelf.brand, 60) : i.brand,
      v: i.v, q: i.q, unit,
      /* true when this line's price came from the shop rather than the phone */
      shop: !!shelf
    };
  });

  const subtotal = money(priced.reduce((a, l) => a + l.unit * l.q, 0));
  const fee = money(pricing.fee || 0);
  const tax = money(subtotal * (pricing.taxRate || 0));
  return {
    items: priced,
    subtotal, fee, tax,
    total: money(subtotal + fee + tax),
    priced: allKnown ? 'shop' : (known.size ? 'partial' : 'phone')
  };
}

/* A ticket as the register board reads it. The field names are OrderStore's,
   not mine — `custState`, `rewardLabel`, `paymentState` and the rest are what
   `ticketList()` destructures. */
function boardRow(row) {
  let body = {};
  try { body = JSON.parse(row.body); } catch { body = {}; }
  return {
    code: row.code,
    n: row.n,
    who: row.who,
    phone: row.phone,
    items: body.items || [],
    subtotal: row.subtotal,
    fee: row.fee,
    tax: row.tax,
    total: row.total,
    pickup: row.pickup,
    status: row.status,
    custState: row.arriving === 'none' ? '' : row.arriving,
    /* Milliseconds, because the client hands this straight to agoText(). */
    placedAt: Date.parse(row.placed_at) || 0,
    rewardLabel: body.rewardLabel || '',
    rewardStatus: body.rewardStatus || '',
    paymentState: body.paymentState || 'unconfirmed',
    paymentRef: body.paymentRef || '',
    cloverOrderId: body.cloverOrderId || ''
  };
}

/* ---------------------------------------------------------------------
   POST /api/orders
   --------------------------------------------------------------------- */
export async function place(env, shop, body, pricing) {
  const code = str(body.code, 12).toUpperCase();
  /* The code is generated on the phone and reserved by the payment step, so
     the server does not mint it. It does insist on the shape, because it is
     the primary key and it gets read out loud. */
  if (!/^[A-Z]{2}-\d{4}$/.test(code)) {
    return fail(400, 'bad code', 'That pickup code is not in the right shape.');
  }

  const raw = Array.isArray(body.items) ? body.items.slice(0, 60) : [];
  if (!raw.length) return fail(400, 'empty', 'There is nothing in that order.');

  const items = raw.map(i => ({
    id: str(i && i.id, 60),
    d: i && i.d ? 1 : 0,
    n: str(i && i.n, 120) || 'Item',
    brand: str(i && i.brand, 60),
    v: str(i && i.v, 80),
    q: Math.max(1, Math.min(99, parseInt(i && i.q, 10) || 1)),
    unit: money(i && i.unit)
  }));

  /* Placing the same order twice is what a phone with a flaky signal does:
     the request went out, the answer did not come back, the customer pressed
     it again. The second one must not become a second ticket, and it must not
     read as an error either — the client would tell the customer nothing was
     sent when in fact it was. */
  const already = await env.DB
    .prepare('SELECT * FROM orders WHERE shop = ?1 AND code = ?2').bind(shop, code).first();
  if (already) {
    const r = boardRow(already);
    return ok({ code, duplicate: true, items: r.items, subtotal: r.subtotal,
                fee: r.fee, tax: r.tax, total: r.total, status: r.status });
  }

  const p = await priceOrder(env, shop, items, pricing);
  const phone = digits(body.phone, 15);

  /* Linking an order to a member is worth doing for the shop's own reporting.
     It does NOT add a visit. A visit is a fact about the till and ordering
     ahead is not paying — the app already says so on the rewards screen and
     the database must not quietly disagree with it. */
  let memberId = null;
  if (phone.length === 10) {
    const m = await env.DB
      .prepare('SELECT id FROM members WHERE shop = ?1 AND phone = ?2').bind(shop, phone).first();
    if (m) memberId = m.id;
  }

  const placedAt = Number.isFinite(body.placedAt) ? new Date(body.placedAt).toISOString() : nowIso();
  const ticket = Object.assign({}, body, {
    items: p.items, subtotal: p.subtotal, fee: p.fee, tax: p.tax, total: p.total,
    priced: p.priced,
    /* A requested reward travels as a label and a status and nothing else. It
       cannot carry a value so it cannot move a total, and the register is the
       final word on any discount. */
    rewardStatus: body.rewardId || body.rewardLabel ? 'requested' : ''
  });

  const n = parseInt(code.split('-')[1], 10) || 0;
  await env.DB.prepare(
    `INSERT INTO orders (shop, code, n, who, phone, subtotal, fee, tax, total,
                         pickup, source, status, status_at, arriving, member_id,
                         placed_at, body)
     VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,'placed',?12,'none',?13,?14,?15)`
  ).bind(shop, code, n, str(body.who, 80) || 'Online customer', phone,
         p.subtotal, p.fee, p.tax, p.total, str(body.pickup, 60),
         str(body.source, 60), nowIso(), memberId, placedAt,
         JSON.stringify(ticket)).run();

  /* Line rows, so the shop can answer "what actually sells" without reading
     every ticket by hand. Batched: D1 charges per round trip. */
  if (p.items.length) {
    await env.DB.batch(p.items.map(l => env.DB.prepare(
      `INSERT INTO order_items (shop, code, product_id, name, brand, variant, qty, unit)
       VALUES (?1,?2,?3,?4,?5,?6,?7,?8)`
    ).bind(shop, code, l.id, l.n, l.brand, l.v, l.q, l.unit)));
  }

  return ok({
    code,
    items: p.items, subtotal: p.subtotal, fee: p.fee, tax: p.tax, total: p.total,
    priced: p.priced,
    status: 'placed',
    reward: ticket.rewardStatus
      ? { status: 'requested',
          note: 'The counter checks it against the shop\'s rewards and applies it at the register.' }
      : null
  });
}

/* ---------------------------------------------------------------------
   GET /api/orders/status?codes=AB-1234,CD-5678

   Deliberately a different endpoint from the board, and the client says why:
   it answers with a status and nothing else, so knowing a pickup code never
   reveals a name, a phone number or a basket. Keep it that way.
   --------------------------------------------------------------------- */
export async function statuses(env, shop, params) {
  const codes = str(params.get('codes') || '', 200)
    .split(',').map(c => c.trim().toUpperCase())
    .filter(c => /^[A-Z]{2}-\d{4}$/.test(c)).slice(0, 12);
  if (!codes.length) return ok({ statuses: {} });

  const q = codes.map((_, i) => '?' + (i + 2)).join(',');
  const rows = await env.DB
    .prepare('SELECT code, status FROM orders WHERE shop = ?1 AND code IN (' + q + ')')
    .bind(shop, ...codes).all();

  const out = {};
  for (const r of (rows.results || [])) out[r.code] = r.status;
  return ok({ statuses: out });
}

/* POST /api/orders/:code/arriving  {state} */
export async function arriving(env, shop, code, state) {
  const s = str(state, 10);
  if (!(s in ARRIVING)) return fail(400, 'bad state', 'Unknown arrival state.');

  const row = await env.DB
    .prepare('SELECT arriving, status FROM orders WHERE shop = ?1 AND code = ?2')
    .bind(shop, str(code, 12).toUpperCase()).first();
  if (!row) return fail(404, 'no order', 'No order with that code.');
  /* Forward only. Nothing is granted by holding a pickup code except the
     ability to say "I am outside", and saying it twice must be worth no more
     than saying it once. */
  if (ARRIVING[s] <= ARRIVING[row.arriving]) return ok({ arriving: row.arriving });

  await env.DB.prepare('UPDATE orders SET arriving = ?3 WHERE shop = ?1 AND code = ?2')
    .bind(shop, str(code, 12).toUpperCase(), s).run();
  return ok({ arriving: s });
}

/* ---------------------------------------------------------------------
   THE REGISTER BOARD. Staff session required.
   --------------------------------------------------------------------- */
export async function board(env, shop) {
  /* Collected tickets are filtered by the client too, but sending a day's
     cleared tickets to an iPad every two seconds is rude to a shop on a phone
     hotspot. The cut is here as well as there. */
  const rows = await env.DB.prepare(
    `SELECT * FROM orders WHERE shop = ?1 AND status != 'collected' AND status != 'cancelled'
       ORDER BY placed_at DESC LIMIT 60`
  ).bind(shop).all();
  return ok({ orders: (rows.results || []).map(boardRow) });
}

/* POST /api/staff/orders/:code/status  {status} */
export async function setStatus(env, shop, code, status) {
  const s = str(status, 20);
  if (STATUSES.indexOf(s) < 0) return fail(400, 'bad status', 'Unknown ticket status.');
  const c = str(code, 12).toUpperCase();
  const row = await env.DB
    .prepare('SELECT code FROM orders WHERE shop = ?1 AND code = ?2').bind(shop, c).first();
  if (!row) return fail(404, 'no order', 'No order with that code.');
  await env.DB
    .prepare('UPDATE orders SET status = ?3, status_at = ?4 WHERE shop = ?1 AND code = ?2')
    .bind(shop, c, s, nowIso()).run();
  return ok({ code: c, status: s });
}


/* What an order-ready message needs, and nothing more. The email comes from
   the member the order was linked to at checkout — an order placed by somebody
   who is not in the programme has nowhere to send to, and says so by answering
   an empty email rather than by inventing one. */
export async function readForNotify(env, shop, code) {
  const row = await env.DB.prepare(
    `SELECT o.code, o.n, o.who, o.total, o.pickup, m.email, m.first
       FROM orders o LEFT JOIN members m ON m.id = o.member_id
      WHERE o.shop = ?1 AND o.code = ?2`
  ).bind(shop, str(code, 12).toUpperCase()).first();
  if (!row) return null;
  return {
    code: row.code, n: row.n,
    who: row.first || row.who,
    email: (row.email || '').toLowerCase(),
    total: row.total, pickup: row.pickup
  };
}
