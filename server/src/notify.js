/* =====================================================================
   THE APP DECIDES WHEN. GOHIGHLEVEL DECIDES WHAT IT LOOKS LIKE.

   Every outbound message goes the same way: this service POSTs a small flat
   JSON object to the shop's inbound webhook, and a workflow on the other end
   branches on `type` and sends whatever the owner designed.

   That split is the whole point. The shop owns the wording, the templates and
   the sending reputation, and can change a subject line at four in the
   afternoon without anybody touching this code. This service owns the facts —
   who, when, and what happened — which is the part a marketing tool cannot
   know because the visits live here.

   WHY NOT SEND EMAIL DIRECTLY. Three reasons, in order of how much they cost:
   deliverability is a full-time job and a shop's domain reputation is easy to
   ruin and slow to repair; several mainstream ESPs refuse vape retail outright
   and close accounts with the list inside them; and the owner already pays for
   GoHighLevel. A sender here would be a fourth thing to maintain for no gain.

   ONE URL, MANY EVENTS. Every payload carries `type`. GHL filters on it. The
   alternative — a webhook per event — means the owner pasting five URLs and
   getting one of them wrong, and it makes adding an event a config change
   instead of a line of code.

   THE JOIN SHAPE IS UNCHANGED. It was chosen for a GoHighLevel inbound
   webhook before any of this existed, and a shop that already built an
   automation against it keeps working: `type` is an added key, not a
   replacement.
   ===================================================================== */

import { str, nowIso } from './http.js';
import { enqueue, drain } from './outbound.js';

/* The events this service can raise. Listed rather than free-form so that a
   typo cannot silently create an event no workflow is listening for — the
   owner builds one branch per entry here and that is the whole contract. */
export const EVENTS = {
  /* somebody joined the programme, from their own phone or at the counter */
  MEMBER_JOINED: 'member.joined',
  /* they just crossed the threshold — this is the one that brings them back */
  REWARD_READY: 'member.reward_ready',
  /* their birthday is today. Raised once, by the daily sweep. */
  BIRTHDAY: 'member.birthday',
  /* the counter marked their bag ready */
  ORDER_READY: 'order.ready',
  /* the front-page box, which is not a membership */
  SUBSCRIBED: 'list.subscribed'
};

/* Queued, never awaited by whoever raised it. A customer pressing Join should
   not wait on somebody else's webhook, and the counter marking a bag ready
   should not either. outbound.js does the retries with backoff. */
export function notify(env, ctx, shop, rule, type, payload) {
  if (!rule) return false;
  const viaApi = rule.transport === 'ghl';
  /* Either a webhook URL to post at, or a location id to upsert into. With
     neither there is nowhere to send and nothing is queued — a shop that has
     not connected anything yet is the commonest state on day one and must not
     be an error. */
  const target = viaApi ? rule.ghlLocationId : rule.endpoint;
  if (!target) return false;

  const body = Object.assign({ type, shop, at: nowIso() }, payload);
  const work = enqueue(env, shop, target, body, viaApi ? 'ghl' : 'webhook')
    .then(() => drain(env, 5));
  if (ctx && ctx.waitUntil) ctx.waitUntil(work.catch(() => {}));
  else work.catch(() => {});
  return true;
}

/* What every member event carries. Kept identical across types so the owner
   maps the fields once in GHL and every branch reads the same names. */
export const memberFields = m => ({
  first: str(m.first, 60),
  phone: str(m.phone, 20),
  email: str(m.email, 160).toLowerCase(),
  birthday: str(m.birthday, 8),
  code: str(m.code, 12),
  emailOk: !!(m.email_ok !== undefined ? m.email_ok : m.emailOk)
});

/* ---------------------------------------------------------------------
   THE DAILY BIRTHDAY SWEEP.

   Runs from the scheduled handler. Two guards, and both matter:

   - It only raises for members who agreed to be emailed and have an address.
     A birthday message to somebody who ticked nothing is the kind of thing
     that gets a sending domain blocked, and it is also just rude.

   - It records the year it last fired for each member, so a cron that runs
     every ten minutes does not send somebody one hundred and forty four
     birthday emails. That is the entire reason `birthday_sent` exists.
   --------------------------------------------------------------------- */
export async function birthdaySweep(env, shop, rule) {
  const target = rule && (rule.transport === 'ghl' ? rule.ghlLocationId : rule.endpoint);
  if (!target) return { raised: 0, reason: 'nowhere to send' };

  /* The shop's own clock, not UTC. A birthday that fires at 5pm the day
     before is worse than one that does not fire at all. */
  const now = new Date();
  const local = new Date(now.toLocaleString('en-US', { timeZone: rule.timezone || 'America/Phoenix' }));
  const key = (local.getMonth() + 1) + '-' + local.getDate();
  const year = local.getFullYear();

  const rows = await env.DB.prepare(
    `SELECT * FROM members
      WHERE shop = ?1 AND left_at IS NULL AND email_ok = 1 AND email != ''
        AND birthday = ?2 AND (birthday_sent IS NULL OR birthday_sent != ?3)`
  ).bind(shop, key, String(year)).all();

  let raised = 0;
  for (const m of (rows.results || [])) {
    notify(env, null, shop, rule, EVENTS.BIRTHDAY,
      Object.assign(memberFields(m), { perk: str(rule.perk, 200) }));
    await env.DB.prepare('UPDATE members SET birthday_sent = ?2 WHERE id = ?1')
      .bind(m.id, String(year)).run();
    raised++;
  }
  return { raised, on: key };
}
