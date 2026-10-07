/* =====================================================================
   THE ONE-FIELD BOX ON THE FRONT PAGE.

   It used to say this, and every word of it was false:

       "You are on the list. One text when a real deal lands."

   What actually happened was `S.phone = v; save()` — the number went into
   that browser's localStorage, nothing was sent anywhere, and nobody was
   ever told. There was no list. A form that does nothing is worse than no
   form at all, because the customer believes they have done something and
   stops looking for the real way in.

   This is the list. It is not a membership: no code, no visits, no card,
   nothing to carry. Somebody who wants to hear when a deal lands, and who
   can be un-subscribed the moment they ask.
   ===================================================================== */

import { ok, fail, str, email as cleanEmail, nowIso } from './http.js';

/* POST /api/subscribers  {email, source, terms} */
export async function subscribe(env, shop, body) {
  const addr = cleanEmail(body.email);
  if (!addr) {
    return fail(400, 'bad email', 'That does not look like an email address.');
  }

  /* Subscribing twice is what a person does when they are not sure it worked
     the first time. It is not an error and must not read like one. */
  const existing = await env.DB
    .prepare('SELECT id, left_at FROM subscribers WHERE shop = ?1 AND email = ?2')
    .bind(shop, addr).first();

  if (existing) {
    if (existing.left_at) {
      await env.DB.prepare('UPDATE subscribers SET left_at = NULL, created = ?2 WHERE id = ?1')
        .bind(existing.id, nowIso()).run();
    }
    return ok({ email: addr, already: !existing.left_at });
  }

  await env.DB.prepare(
    'INSERT INTO subscribers (shop, email, source, terms, created) VALUES (?1,?2,?3,?4,?5)'
  ).bind(shop, addr, str(body.source, 40), str(body.terms, 400), nowIso()).run();

  return ok({ email: addr, already: false });
}

/* POST /api/subscribers/leave  {email}
   No token and no confirmation step. Unsubscribing has to be the easiest
   thing on the whole service — a list somebody cannot get off is a list that
   gets reported as spam, and one spam complaint costs more than every address
   a confirmation step would have saved. The worst a stranger can do with this
   is take somebody off a marketing list. */
export async function unsubscribe(env, shop, body) {
  const addr = cleanEmail(body.email);
  if (!addr) return fail(400, 'bad email', 'That does not look like an email address.');
  await env.DB.prepare(
    'UPDATE subscribers SET left_at = ?3 WHERE shop = ?1 AND email = ?2 AND left_at IS NULL'
  ).bind(shop, addr, nowIso()).run();
  /* Members are on the same address, and somebody unsubscribing means it,
     whichever list the shop happens to hold them on. */
  await env.DB.prepare(
    'UPDATE members SET email_ok = 0 WHERE shop = ?1 AND email = ?2'
  ).bind(shop, addr).run();
  return ok({ left: true });
}

/* GET /api/staff/subscribers/export.csv — the shop's list, in full, the same
   promise the member export keeps. */
const csvCell = v => {
  const s = v == null ? '' : String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

export async function exportCsv(env, shop) {
  const rows = await env.DB
    .prepare('SELECT email, source, terms, created, left_at FROM subscribers WHERE shop = ?1 ORDER BY created')
    .bind(shop).all();
  const lines = ['email,source,consented_to,joined,unsubscribed'];
  for (const r of (rows.results || [])) {
    lines.push([r.email, r.source, r.terms, r.created, r.left_at || ''].map(csvCell).join(','));
  }
  return new Response(lines.join('\n') + '\n', {
    status: 200,
    headers: {
      'content-type': 'text/csv; charset=utf-8',
      'cache-control': 'no-store',
      'content-disposition': 'attachment; filename="' + shop + '-subscribers-' +
        nowIso().slice(0, 10) + '.csv"'
    }
  });
}
