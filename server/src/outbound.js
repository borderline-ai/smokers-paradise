/* =====================================================================
   THE SHOP'S CRM, RETRIED BY THE SERVER.

   Stage 170 found that the join retry queue only drained when the app was
   reopened, so a join made by somebody who never opens the app again was a
   join the shop never heard about. Moving the queue here fixes the half of
   that problem the phone cannot fix: a server does not need the customer to
   come back.

   The payload is the same flat object SHOP_REWARDS.endpoint has always
   expected — {first, phone, birthday, sms, code, joined, shop} — because that
   shape was chosen for a GoHighLevel inbound webhook and there is no reason
   to make the shop rebuild their automation.

   Backoff is deliberate and slow. A webhook that is down is usually down for
   minutes or hours, and hammering somebody's CRM is how an integration gets
   turned off at the other end.
   ===================================================================== */

import { nowIso } from './http.js';

const BACKOFF_MIN = [0, 1, 5, 20, 60, 180, 360];   /* minutes, by try count */
const MAX_TRIES = BACKOFF_MIN.length;

export async function enqueue(env, shop, url, payload) {
  if (!url) return;
  await env.DB.prepare(
    'INSERT INTO outbound (shop, url, body, tries, next_try, created) VALUES (?1,?2,?3,0,?4,?4)'
  ).bind(shop, url, JSON.stringify(payload), nowIso()).run();
}

/* Drains what is due. Called after a join (so the common case is instant) and
   from the scheduled handler (so the uncommon case still happens). Bounded
   per run, because a Worker invocation has a wall clock and a queue that has
   been stuck for a week should not try to empty itself in one go. */
export async function drain(env, limit = 25) {
  const now = nowIso();
  const due = await env.DB.prepare(
    'SELECT * FROM outbound WHERE sent_at IS NULL AND next_try <= ?1 ORDER BY next_try LIMIT ?2'
  ).bind(now, limit).all();

  let sent = 0, failed = 0;
  for (const row of (due.results || [])) {
    let okish = false, err = '';
    try {
      const r = await fetch(row.url, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: row.body
      });
      okish = r.ok;
      if (!okish) err = 'HTTP ' + r.status;
    } catch (e) {
      err = String((e && e.message) || e).slice(0, 200);
    }

    if (okish) {
      await env.DB.prepare('UPDATE outbound SET sent_at = ?2, last_err = \'\' WHERE id = ?1')
        .bind(row.id, nowIso()).run();
      sent++;
    } else {
      const tries = row.tries + 1;
      /* Given up on, but not deleted. A row that was never delivered is a
         person who joined and never reached the shop's list, and the owner is
         entitled to find out about them. */
      const mins = BACKOFF_MIN[Math.min(tries, MAX_TRIES - 1)];
      const next = new Date(Date.now() + mins * 60000).toISOString();
      await env.DB.prepare(
        'UPDATE outbound SET tries = ?2, next_try = ?3, last_err = ?4 WHERE id = ?1'
      ).bind(row.id, tries, next, err).run();
      failed++;
    }
  }
  return { sent, failed };
}

/* What the counter sees when it asks whether anything is stuck. A shop that
   pasted a webhook URL with a typo in it should be able to find that out
   without reading a database. */
export async function status(env, shop) {
  const row = await env.DB.prepare(
    `SELECT COUNT(*) AS waiting,
            SUM(CASE WHEN tries >= ?2 THEN 1 ELSE 0 END) AS stuck,
            MAX(last_err) AS last_err
       FROM outbound WHERE shop = ?1 AND sent_at IS NULL`
  ).bind(shop, MAX_TRIES).first();
  return {
    waiting: (row && row.waiting) || 0,
    stuck: (row && row.stuck) || 0,
    lastError: (row && row.last_err) || ''
  };
}
