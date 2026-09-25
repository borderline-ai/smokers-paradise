/* =====================================================================
   THE SHOP'S RULE, IN ONE PLACE EVERY DEVICE CAN READ.

   The counter screen has always been able to change the rewards rule. Until
   now that change reached exactly one device: the one it was typed on. The
   owner could set "6 visits" on the iPad and every customer's phone would go
   on saying 10 forever. Same for a price edit. That is the bug class this
   file closes.

   `rev` goes up on every write. A client that already has rev 4 and asks
   again gets told 4 and changes nothing.
   ===================================================================== */

import { str, nowIso } from './http.js';

/* The defaults are the ones in app/index.html, and they are here only so a
   brand new database answers something sensible on its very first request.
   The moment the owner saves the rule at the counter, these stop mattering. */
export const DEFAULT_REWARDS = {
  on: true,
  name: 'Paradise Rewards',
  visitsFor: 10,
  reward: '$10 off',
  /* EMAIL, NOT A TEXT. This is the value the app's card actually prints:
     Shop.pullConfig() copies `perk` over whatever the document shipped with,
     so the server's default wins. Stage 174 changed the wording in the app and
     missed it here, and the false "birthday text" claim came straight back on
     the hosted shop while the offline file read correctly. Found by opening
     it, not by a test — there is one now. */
  perk: 'A birthday email with something on us, every year.',
  endpoint: '',
  /* 'webhook' posts at `endpoint`, which GHL bills per execution. 'ghl' goes
     through the Contacts API and adds a tag, which is a standard trigger and
     costs nothing. Both are kept so a shop can switch back without a deploy. */
  transport: 'webhook',
  ghlLocationId: '',
  terms: 'One membership per phone number. Visits are added at the counter when you pay. 21+ only. The register is the final word on any discount.'
};

/* Nogales AZ: 5.6 state + 1.0 county + 2.0 city. Marked verified in STORE and
   it stays verified here. */
export const DEFAULT_PRICING = { taxRate: 0.086, fee: 0 };

export async function readConfig(env, shop, key, fallback) {
  const row = await env.DB
    .prepare('SELECT value, rev FROM config WHERE shop = ?1 AND key = ?2')
    .bind(shop, key).first();
  if (!row) return { value: fallback, rev: 0 };
  try {
    return { value: Object.assign({}, fallback, JSON.parse(row.value)), rev: row.rev };
  } catch {
    return { value: fallback, rev: row.rev };
  }
}

export async function writeConfig(env, shop, key, value) {
  const next = await env.DB.prepare(
    `INSERT INTO config (shop, key, value, rev, updated) VALUES (?1, ?2, ?3, 1, ?4)
       ON CONFLICT (shop, key) DO UPDATE SET value = ?3, rev = config.rev + 1, updated = ?4
     RETURNING rev`
  ).bind(shop, key, JSON.stringify(value), nowIso()).first();
  return next ? next.rev : 1;
}

export const rewardsRule = env_shop => env_shop;   /* see readConfig callers */

/* Everything a counter can type into the rule screen, clamped to what the
   screen itself allows. `visitsFor` outside 1..100 is refused rather than
   clamped: silently saving 100 when somebody typed 1000 is a lie the owner
   would not find until a customer complained. */
export function cleanRewards(body, current) {
  const out = Object.assign({}, current);
  if ('on' in body) out.on = !!body.on;
  if ('name' in body) out.name = str(body.name, 60) || current.name;
  if ('reward' in body) out.reward = str(body.reward, 80) || current.reward;
  if ('perk' in body) out.perk = str(body.perk, 200);
  if ('ghlLocationId' in body) out.ghlLocationId = str(body.ghlLocationId, 60);
  if ('transport' in body) {
    const t = str(body.transport, 20);
    if (t !== 'webhook' && t !== 'ghl') {
      return { error: 'The transport has to be webhook or ghl.' };
    }
    /* Switching to the API path without a location id would silently send
       nothing, which is the failure mode this whole codebase keeps refusing. */
    if (t === 'ghl' && !(out.ghlLocationId || current.ghlLocationId)) {
      return { error: 'Set the GoHighLevel location id before switching to the API.' };
    }
    out.transport = t;
  }
  if ('terms' in body) out.terms = str(body.terms, 600) || current.terms;
  if ('endpoint' in body) {
    const e = str(body.endpoint, 400);
    /* An endpoint the server will POST a customer's name and number to is
       worth one check. Anything that is not an https URL is refused. */
    if (!e) out.endpoint = '';
    else {
      let u = null;
      try { u = new URL(e); } catch { u = null; }
      if (!u || u.protocol !== 'https:') {
        return { error: 'The webhook has to be an https address.' };
      }
      out.endpoint = u.toString();
    }
  }
  if ('visitsFor' in body) {
    const n = parseInt(body.visitsFor, 10);
    if (!(n >= 1 && n <= 100)) {
      return { error: 'Visits to earn a reward has to be a whole number from 1 to 100.' };
    }
    out.visitsFor = n;
  }
  return { value: out };
}
