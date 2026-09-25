/* =====================================================================
   MEMBERS, VISITS, REDEMPTIONS.

   The half of the product that did not exist. Before this file:

       customer joins on her phone    -> SP26699 written to HER localStorage
       staff type SP26699 on the iPad -> "No member with that code on this device."

   Four rules govern everything below, and they are the reason the code is
   shaped the way it is rather than the obvious way.

   1. ONLY THE COUNTER WRITES A VISIT. There is no path from a customer
      device into the visits table. `addVisit` and `redeem` live behind a
      staff session and the router will not route to them without one. A
      visit the customer's own device can create is a coupon anyone can print.

   2. A REDEMPTION IS PRICED WHEN IT HAPPENS. `cost` is written from the rule
      as it stands at that instant and never recomputed. Stage 167: changing
      10 to 6 re-priced history and invented four free visits.

   3. THE SHOP OWNS THE DATA. `exportCsv` dumps every member, every visit and
      every redemption, in full, on demand. That is a sales promise.

   4. OFFLINE DEGRADES. A join arrives here possibly minutes or days after it
      was made, carrying its own `joined` timestamp and its own idea of the
      member code. Both are honoured where they can be. Joining twice with the
      same number is not an error, it is the retry queue doing its job.
   ===================================================================== */

import { ok, fail, str, digits, email as cleanEmail, nowIso } from './http.js';
import { codeVariants, memberToken, codeFor } from './ids.js';

/* ---------------------------------------------------------------------
   PROGRESS. One function, used by the customer's card, by the counter and
   by the export, so the three can never disagree about how many visits
   somebody has. The card on the phone no longer computes this at all.
   --------------------------------------------------------------------- */
export async function progressFor(env, shop, memberId, rule) {
  const need = Math.max(1, rule.visitsFor | 0);
  const v = await env.DB
    .prepare('SELECT COUNT(*) AS n FROM visits WHERE member_id = ?1').bind(memberId).first();
  const r = await env.DB
    .prepare('SELECT COALESCE(SUM(cost), 0) AS spent, COUNT(*) AS n FROM redemptions WHERE member_id = ?1')
    .bind(memberId).first();

  const total = v ? v.n : 0;
  /* Spend what was actually spent, at the price it was spent at. Not
     `redemptions * today's rule` — that is the stage 167 bug. */
  const spent = r ? r.spent : 0;
  const net = Math.max(0, total - spent);
  return {
    visits: net % need,
    need,
    ready: Math.floor(net / need),
    total,
    redeemed: r ? r.n : 0
  };
}

/* What a customer's own phone is allowed to know about itself. Deliberately
   not the database row: no id, no token echoed back, no other member. */
const cardOf = m => ({
  first: m.first, phone: m.phone, email: m.email, code: m.code,
  birthday: m.birthday, sms: !!m.sms, emailOk: !!m.email_ok, joined: m.joined
});

/* What the counter is allowed to see. The phone number is here because the
   counter already has the customer standing in front of them and sometimes
   needs to check they typed the right code. */
const counterOf = m => ({
  first: m.first, code: m.code, phone: m.phone, email: m.email,
  birthday: m.birthday, sms: !!m.sms, emailOk: !!m.email_ok, joined: m.joined
});

/* ---------------------------------------------------------------------
   JOIN.  POST /api/members
   Body is the flat object the app already sends to SHOP_REWARDS.endpoint:
   {first, phone, birthday, sms, code, joined, shop}. That shape was chosen
   for a GoHighLevel inbound webhook and it is kept exactly, so the same
   queued item can be posted either here or straight at a CRM.
   --------------------------------------------------------------------- */
export async function join(env, shop, body, rule) {
  const phone = digits(body.phone, 15);
  const first = str(body.first, 60);

  /* Ten digits, because the form says ten digits and the counter is going to
     read it back to somebody. A number that cannot be texted is not a
     membership, it is a row. */
  if (phone.length !== 10) {
    return fail(400, 'bad phone', 'That does not look like a 10 digit mobile number.');
  }
  if (!first) {
    return fail(400, 'no name', 'We need a first name for the counter.');
  }

  /* Month and day, never a year. The column must not learn to hold one, so
     anything that looks like a year is dropped rather than stored. */
  let birthday = str(body.birthday, 8);
  if (birthday && !/^(1[0-2]|[1-9])-(3[01]|[12]\d|[1-9])$/.test(birthday)) birthday = '';

  /* EMAIL IS VALIDATED BUT NOT REQUIRED, AND THE ASYMMETRY IS DELIBERATE.

     The join form requires one, because email is the only channel the shop
     has and a member without an address is a member nobody can ever reach.
     This endpoint does not, because it also receives joins that were queued
     on a phone BEFORE stage 174 existed — {first, phone, birthday, sms, …}
     with no email in it at all. Refusing those would strand them in that
     phone's retry queue forever, which is precisely the hole stage 170 was
     written to close.

     So a bad address is refused and an absent one is accepted. The export
     shows the blank so the counter can ask for it next time they come in. */
  const addr = cleanEmail(body.email);
  if (body.email && !addr) {
    return fail(400, 'bad email', 'That does not look like an email address.');
  }

  const sms = body.sms ? 1 : 0;
  /* Old queued joins carry `sms` as the consent flag and no `emailOk`. The
     sentence they ticked at the time said texting, so it is not read as
     permission to email — an absent emailOk means no. */
  const emailOk = body.emailOk ? 1 : 0;
  const terms = str(body.terms, 400);
  const joined = /^\d{4}-\d{2}-\d{2}T/.test(str(body.joined, 40))
    ? str(body.joined, 40) : nowIso();

  /* Already a member? One membership per phone number is what the terms say,
     so this is not an error and must not read like one. The retry queue on a
     phone posts the same join until something answers 2xx; answering 409
     would strand it there forever. */
  const existing = await env.DB
    .prepare('SELECT * FROM members WHERE shop = ?1 AND phone = ?2').bind(shop, phone).first();

  if (existing) {
    /* Somebody who left and came back gets their history, not a blank card.
       The visits they already paid for were never deleted. */
    if (existing.left_at) {
      await env.DB.prepare(
        'UPDATE members SET left_at = NULL, first = ?2, birthday = ?3, sms = ?4 WHERE id = ?1'
      ).bind(existing.id, first, birthday, sms).run();
      existing.left_at = null;
    } else if (first !== existing.first || sms !== existing.sms ||
               (addr && addr !== existing.email) || emailOk !== existing.email_ok ||
               (birthday && birthday !== existing.birthday)) {
      /* A second join from the same number is how somebody corrects a typo in
         their own name or their own address, so take the new one. An absent
         address does not wipe one the shop already has. */
      await env.DB.prepare(
        `UPDATE members SET first = ?2, birthday = ?3, sms = ?4, email = ?5,
                            email_ok = ?6, contact_terms = ?7 WHERE id = ?1`
      ).bind(existing.id, first, birthday || existing.birthday, sms,
             addr || existing.email, emailOk,
             terms || existing.contact_terms).run();
    }
    const fresh = await env.DB.prepare('SELECT * FROM members WHERE id = ?1')
      .bind(existing.id).first();
    return ok({
      member: cardOf(fresh),
      token: fresh.token,
      rejoined: true,
      progress: await progressFor(env, shop, fresh.id, rule)
    });
  }

  /* A free code. Usually the first candidate, which is the one the phone
     already computed and is already showing on a card. When two numbers
     collide the server walks forward and the phone is told what it actually
     got — see ids.js. */
  let code = '';
  for (const c of codeVariants(phone)) {
    const taken = await env.DB
      .prepare('SELECT 1 AS x FROM members WHERE shop = ?1 AND code = ?2').bind(shop, c).first();
    if (!taken) { code = c; break; }
  }
  if (!code) {
    return fail(503, 'no code',
      'Could not allocate a member code. The shop has run out of the short codes in that range.');
  }

  const token = memberToken();
  await env.DB.prepare(
    `INSERT INTO members (shop, code, phone, email, first, birthday, sms,
                          email_ok, contact_terms, token, joined)
     VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)`
  ).bind(shop, code, phone, addr, first, birthday, sms, emailOk, terms,
         token, joined).run();

  const row = await env.DB.prepare('SELECT * FROM members WHERE shop = ?1 AND phone = ?2')
    .bind(shop, phone).first();

  return ok({
    member: cardOf(row),
    token,
    /* True when the phone's own guess at the code collided with somebody
       else's. The client swaps the card over when it sees this. */
    recoded: code !== codeFor(phone),
    progress: await progressFor(env, shop, row.id, rule)
  });
}

/* ---------------------------------------------------------------------
   THE CUSTOMER READING THEIR OWN CARD.  GET /api/members/me?token=
   Read only, by construction: there is no write anywhere in this function.
   --------------------------------------------------------------------- */
export async function readMe(env, shop, token, rule) {
  const t = str(token, 60);
  if (!t) return fail(400, 'no token', 'No membership on this device.');
  const m = await env.DB
    .prepare('SELECT * FROM members WHERE shop = ?1 AND token = ?2').bind(shop, t).first();
  /* A token the server has never seen, or one belonging to somebody who left,
     is the same answer: this device is not holding a membership. The client
     clears its local copy on this, which is what stops a forgotten card
     hanging around on a phone forever. */
  if (!m || m.left_at) return fail(404, 'no member', 'This device is not holding a membership.');

  const visits = await env.DB
    .prepare('SELECT at FROM visits WHERE member_id = ?1 ORDER BY at DESC LIMIT 60')
    .bind(m.id).all();
  const reds = await env.DB
    .prepare('SELECT at, reward, cost FROM redemptions WHERE member_id = ?1 ORDER BY at DESC LIMIT 60')
    .bind(m.id).all();

  return ok({
    member: cardOf(m),
    progress: await progressFor(env, shop, m.id, rule),
    visits: (visits.results || []),
    redemptions: (reds.results || [])
  });
}

/* Leaving the programme. The row stays, flagged, so the shop's own history is
   not rewritten and so a rejoin is a rejoin rather than a new person. */
export async function leave(env, shop, token) {
  const t = str(token, 60);
  if (!t) return fail(400, 'no token', 'No membership on this device.');
  const m = await env.DB
    .prepare('SELECT id FROM members WHERE shop = ?1 AND token = ?2').bind(shop, t).first();
  if (!m) return ok({ left: true });          /* already gone; not an error   */
  await env.DB.prepare('UPDATE members SET left_at = ?2, sms = 0 WHERE id = ?1')
    .bind(m.id, nowIso()).run();
  return ok({ left: true });
}

/* ---------------------------------------------------------------------
   THE COUNTER.  Everything below here is behind a staff session.
   --------------------------------------------------------------------- */

/* GET /api/staff/members?code=SP26699   (or ?phone=5205550134)
   This is the call that did not exist, and its absence is what made the whole
   rewards programme a demo: the counter could never find a real customer. */
export async function lookup(env, shop, params, rule) {
  const code = str(params.get('code') || '', 12).toUpperCase().replace(/[^A-Z0-9]/g, '');
  const phone = digits(params.get('phone') || '', 15);

  let m = null;
  if (code) {
    m = await env.DB.prepare('SELECT * FROM members WHERE shop = ?1 AND code = ?2')
      .bind(shop, code).first();
  } else if (phone.length === 10) {
    m = await env.DB.prepare('SELECT * FROM members WHERE shop = ?1 AND phone = ?2')
      .bind(shop, phone).first();
  } else {
    return fail(400, 'nothing to look up', 'Type the code from the customer\'s card.');
  }

  if (!m || m.left_at) {
    /* The wording matters at a counter with a queue behind it. "Not on this
       device" was the old message and it was true and useless. */
    return fail(404, 'no member', 'No member with that code. Check the code on their screen.');
  }
  return ok({
    member: counterOf(m),
    progress: await progressFor(env, shop, m.id, rule)
  });
}

const DOUBLE_TAP_MS = 30000;

/* POST /api/staff/members/:code/visit
   The fifty-times-a-day action. Two guards on it:
   - a staff session, because only the counter may write a visit;
   - a thirty second window, because a thumb on a busy iPad hits a button
     twice and a customer should not get a free visit out of that. `force`
     gets through deliberately, for the rare case of two real sales. */
export async function addVisit(env, shop, code, sessionId, rule, opts = {}) {
  const m = await env.DB.prepare('SELECT * FROM members WHERE shop = ?1 AND code = ?2')
    .bind(shop, str(code, 12).toUpperCase()).first();
  if (!m || m.left_at) return fail(404, 'no member', 'No member with that code.');

  if (!opts.force) {
    const last = await env.DB
      .prepare('SELECT at FROM visits WHERE member_id = ?1 ORDER BY at DESC LIMIT 1')
      .bind(m.id).first();
    if (last && (Date.now() - Date.parse(last.at)) < DOUBLE_TAP_MS) {
      return fail(409, 'too soon',
        'A visit was already added for ' + m.first + ' a moment ago.');
    }
  }

  await env.DB.prepare('INSERT INTO visits (shop, member_id, at, by) VALUES (?1, ?2, ?3, ?4)')
    .bind(shop, m.id, nowIso(), sessionId || 'counter').run();

  return ok({
    member: counterOf(m),
    progress: await progressFor(env, shop, m.id, rule)
  });
}

/* POST /api/staff/members/:code/redeem
   Refused when nothing is ready. The old client only hid the button, which is
   not the same thing: a hidden button is a suggestion and this is a rule. */
export async function redeem(env, shop, code, sessionId, rule) {
  const m = await env.DB.prepare('SELECT * FROM members WHERE shop = ?1 AND code = ?2')
    .bind(shop, str(code, 12).toUpperCase()).first();
  if (!m || m.left_at) return fail(404, 'no member', 'No member with that code.');

  const before = await progressFor(env, shop, m.id, rule);
  if (before.ready < 1) {
    return fail(409, 'not ready',
      m.first + ' is ' + (before.need - before.visits) + ' visits short of a reward.');
  }

  /* The price, stamped. This row will still read true after the owner changes
     the rule, which is the entire reason the column exists. */
  await env.DB.prepare(
    'INSERT INTO redemptions (shop, member_id, at, reward, cost, by) VALUES (?1, ?2, ?3, ?4, ?5, ?6)'
  ).bind(shop, m.id, nowIso(), rule.reward, Math.max(1, rule.visitsFor | 0),
         sessionId || 'counter').run();

  return ok({
    member: counterOf(m),
    progress: await progressFor(env, shop, m.id, rule),
    /* Echoed back so the counter can say what it took off, in the words that
       were true at the moment it took it off. */
    took: { reward: rule.reward, cost: Math.max(1, rule.visitsFor | 0) }
  });
}

/* ---------------------------------------------------------------------
   THE EXPORT.  GET /api/staff/members/export.csv

   "The shop owns the member data. It must be exportable in full, on demand.
   That is a sales promise, keep it true." — CLAUDE.md

   In full means in full: every member, their whole visit count, their whole
   redemption history and what each redemption cost. Not a summary.
   --------------------------------------------------------------------- */
const csvCell = v => {
  const s = v == null ? '' : String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

export async function exportCsv(env, shop, rule) {
  const rows = await env.DB.prepare(
    `SELECT m.code, m.first, m.phone, m.email, m.birthday, m.sms, m.email_ok,
            m.contact_terms, m.joined, m.left_at,
            (SELECT COUNT(*) FROM visits v WHERE v.member_id = m.id)            AS visits,
            (SELECT MAX(at)   FROM visits v WHERE v.member_id = m.id)           AS last_visit,
            (SELECT COUNT(*)  FROM redemptions r WHERE r.member_id = m.id)      AS redemptions,
            (SELECT COALESCE(SUM(cost),0) FROM redemptions r WHERE r.member_id = m.id) AS visits_spent
       FROM members m WHERE m.shop = ?1 ORDER BY m.joined`
  ).bind(shop).all();

  const need = Math.max(1, rule.visitsFor | 0);
  /* `consented_to` carries the exact sentence they ticked. A list that says
     "yes" without saying yes to what is a list the shop cannot defend. */
  const head = ['code', 'first_name', 'phone', 'email', 'birthday_month_day',
    'email_consent', 'sms_consent', 'consented_to',
    'joined', 'left', 'visits_all_time', 'last_visit', 'rewards_redeemed',
    'visits_spent_on_rewards', 'visits_towards_next', 'rewards_ready'];

  const lines = [head.join(',')];
  for (const r of (rows.results || [])) {
    const net = Math.max(0, (r.visits || 0) - (r.visits_spent || 0));
    lines.push([
      r.code, r.first, r.phone, r.email, r.birthday,
      r.email_ok ? 'yes' : 'no', r.sms ? 'yes' : 'no', r.contact_terms || '',
      r.joined, r.left_at || '', r.visits || 0, r.last_visit || '',
      r.redemptions || 0, r.visits_spent || 0, net % need, Math.floor(net / need)
    ].map(csvCell).join(','));
  }

  const stamp = nowIso().slice(0, 10);
  return new Response(lines.join('\n') + '\n', {
    status: 200,
    headers: {
      'content-type': 'text/csv; charset=utf-8',
      'cache-control': 'no-store',
      'content-disposition': 'attachment; filename="' + shop + '-members-' + stamp + '.csv"'
    }
  });
}


/* ---------------------------------------------------------------------
   GET /api/staff/members/list?q=&limit=

   The Customers screen. Until the counter app there wasn't one — the Staff
   view's Customers tab was six hardcoded sample people, which was honest
   enough when there was no member list and is a lie now that there is.

   Ordered by who was in most recently, because that is the question somebody
   at a counter actually has.

   The `m.id DESC` tiebreak is not decoration. Timestamps here are ISO strings
   to the millisecond, and a shop that takes two payments in the same
   millisecond — or a member who joins in the same millisecond another gets a
   visit — produces a tie. Without a second key SQLite is free to return them
   in either order, so the list would reshuffle between three-second polls
   while nothing had changed. Newest member first is the tiebreak; what
   matters is that it is always the same one.
   --------------------------------------------------------------------- */
export async function list(env, shop, params, rule) {
  const q = str(params.get('q') || '', 60).toLowerCase();
  const limit = Math.max(1, Math.min(200, parseInt(params.get('limit'), 10) || 60));
  const need = Math.max(1, rule.visitsFor | 0);

  const rows = await env.DB.prepare(
    `SELECT m.id, m.code, m.first, m.phone, m.email, m.birthday, m.email_ok,
            m.joined, m.left_at,
            (SELECT COUNT(*) FROM visits v WHERE v.member_id = m.id)  AS visits,
            (SELECT MAX(at)  FROM visits v WHERE v.member_id = m.id)  AS last_visit,
            (SELECT COALESCE(SUM(cost),0) FROM redemptions r WHERE r.member_id = m.id) AS spent
       FROM members m WHERE m.shop = ?1 AND m.left_at IS NULL
       ORDER BY COALESCE((SELECT MAX(at) FROM visits v WHERE v.member_id = m.id), m.joined) DESC,
                m.id DESC
       LIMIT ?2`
  ).bind(shop, limit).all();

  const members = [];
  for (const r of (rows.results || [])) {
    const hay = (r.first + ' ' + r.code + ' ' + r.phone + ' ' + r.email).toLowerCase();
    if (q && hay.indexOf(q) < 0) continue;
    const net = Math.max(0, (r.visits || 0) - (r.spent || 0));
    members.push({
      code: r.code, first: r.first, phone: r.phone, email: r.email,
      birthday: r.birthday, emailOk: !!r.email_ok, joined: r.joined,
      total: r.visits || 0, lastVisit: r.last_visit || '',
      visits: net % need, need, ready: Math.floor(net / need)
    });
  }

  const all = await env.DB
    .prepare('SELECT COUNT(*) AS n FROM members WHERE shop = ?1 AND left_at IS NULL')
    .bind(shop).first();
  return ok({ members, total: all ? all.n : members.length });
}


/* Read a member and their progress without any of the answer-shaping the
   endpoints do. Used either side of a visit so the router can tell whether
   THAT visit is the one that crossed the threshold — a reward going from
   0 ready to 1 ready is the message worth sending, and a member sitting on a
   ready reward for three weeks should hear about it once rather than after
   every subsequent visit. */
export async function readForNotify(env, shop, code, rule) {
  const m = await env.DB.prepare('SELECT * FROM members WHERE shop = ?1 AND code = ?2')
    .bind(shop, str(code, 12).toUpperCase()).first();
  if (!m || m.left_at) return null;
  return { member: m, progress: await progressFor(env, shop, m.id, rule) };
}
