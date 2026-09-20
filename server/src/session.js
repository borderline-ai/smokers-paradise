/* =====================================================================
   THE COUNTER PROVING IT IS THE COUNTER.

   Only the counter may add a visit, take a reward off, read the board, read a
   member by code, or change the rule. That sentence is the product. This file
   is the only thing enforcing it, so it is worth reading slowly.

   The PIN lives in a Worker secret, not in the database and not in the app.
   `wrangler secret put STAFF_PIN`. It is compared in constant time. Changing
   it is one command and takes effect on the next sign in; existing sessions
   are cut with `wrangler secret put` followed by nothing else, because a
   session is only valid while its row is in the table and the table can be
   emptied.

   The session cookie is HttpOnly so no script on the page can read it,
   Secure so it never crosses a plain connection, and SameSite=Strict so a
   link in a text message cannot make the counter's own browser add a visit.
   ===================================================================== */

import { fail, unauthorised, nowIso, callerIp } from './http.js';
import { sessionId, sameSecret } from './ids.js';

const COOKIE = 'sp_staff';
const SESSION_HOURS = 14;      /* one trading day, 8 AM to 9 PM, plus slack */
const MAX_FAILS = 8;           /* per address, per window                   */
const FAIL_WINDOW_MIN = 15;

function readCookie(request, name) {
  const raw = request.headers.get('cookie') || '';
  for (const part of raw.split(';')) {
    const i = part.indexOf('=');
    if (i < 0) continue;
    if (part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return '';
}

function setCookie(id, maxAge) {
  return [
    COOKIE + '=' + id,
    'Path=/',
    'HttpOnly',
    'Secure',
    'SameSite=Strict',
    'Max-Age=' + maxAge
  ].join('; ');
}

/* Resolves the staff session for this request, or null. Every /staff/ route
   calls this first and there is no way round it: the router refuses to
   dispatch a /staff/ path without one. */
export async function currentSession(request, env, shop) {
  const id = readCookie(request, COOKIE);
  if (!id) return null;
  const row = await env.DB
    .prepare('SELECT id, expires FROM staff_sessions WHERE id = ?1 AND shop = ?2')
    .bind(id, shop).first();
  if (!row) return null;
  if (row.expires <= nowIso()) {
    await env.DB.prepare('DELETE FROM staff_sessions WHERE id = ?1').bind(id).run();
    return null;
  }
  return row;
}

export async function requireSession(request, env, shop) {
  const s = await currentSession(request, env, shop);
  return s || unauthorised();
}

/* POST /api/staff/session  {pin} */
export async function signIn(request, env, shop, body) {
  const who = callerIp(request);
  const since = new Date(Date.now() - FAIL_WINDOW_MIN * 60000).toISOString();

  const recent = await env.DB
    .prepare('SELECT COUNT(*) AS n FROM pin_attempts WHERE shop = ?1 AND who = ?2 AND at > ?3')
    .bind(shop, who, since).first();
  if (recent && recent.n >= MAX_FAILS) {
    /* Deliberately not 401. 401 means "wrong PIN, try again" to the client and
       to the person holding the iPad; this is a different fact and it should
       read differently at the counter. */
    return fail(429, 'locked',
      'Too many wrong PINs from this connection. Wait a quarter of an hour.');
  }

  const expected = env.STAFF_PIN || '';
  if (!expected) {
    return fail(503, 'no pin set',
      'No staff PIN is configured on this service. Run: wrangler secret put STAFF_PIN');
  }

  if (!sameSecret(String(body.pin || ''), expected)) {
    await env.DB
      .prepare('INSERT INTO pin_attempts (shop, who, at) VALUES (?1, ?2, ?3)')
      .bind(shop, who, nowIso()).run();
    return fail(401, 'bad pin', 'That PIN is not right.');
  }

  const id = sessionId();
  const expires = new Date(Date.now() + SESSION_HOURS * 3600000).toISOString();
  await env.DB.prepare(
    'INSERT INTO staff_sessions (id, shop, created, expires, ua) VALUES (?1, ?2, ?3, ?4, ?5)'
  ).bind(id, shop, nowIso(), expires,
         String(request.headers.get('user-agent') || '').slice(0, 200)).run();

  /* Housekeeping on the way past, so expired rows and stale failures do not
     accumulate. There is no cron worth spending on this. */
  await env.DB.prepare('DELETE FROM staff_sessions WHERE expires < ?1').bind(nowIso()).run();
  await env.DB.prepare('DELETE FROM pin_attempts WHERE at < ?1').bind(since).run();

  return new Response(JSON.stringify({ ok: true, expires }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'set-cookie': setCookie(id, SESSION_HOURS * 3600)
    }
  });
}

/* DELETE /api/staff/session — signing out has to actually delete the row.
   Clearing the cookie alone leaves a live session id in the wild. */
export async function signOut(request, env, shop) {
  const id = readCookie(request, COOKIE);
  if (id) {
    await env.DB.prepare('DELETE FROM staff_sessions WHERE id = ?1 AND shop = ?2')
      .bind(id, shop).run();
  }
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'set-cookie': setCookie('', 0)
    }
  });
}
