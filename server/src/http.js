/* =====================================================================
   EVERY ANSWER IS JSON, INCLUDING THE REFUSALS.

   This is not a style preference, it is forced by the client. `call()` in
   app/index.html reads the content-type before it reads the body:

       if(ct.indexOf('json') < 0){ reachable = false; return null }

   and the comment above it says why — a static host answers an unknown path
   with its own HTML and a 200, and treating that as a stored order would tell
   a customer the counter has a ticket that does not exist.

   So a 404 that renders an HTML error page does not read as "no such order"
   to this app. It reads as "there is no shop here at all", and the whole
   ordering surface quietly turns itself off. Every path out of this Worker
   goes through one of these.
   ===================================================================== */

const CORE = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store',
  /* The API is same-origin with the app by construction, so no request to it
     is ever a cross-origin one. Saying so explicitly means a stray
     Access-Control-Allow-Origin can never be added by accident later. */
  'vary': 'Cookie',
  'x-content-type-options': 'nosniff'
};

export function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: Object.assign({}, CORE, headers)
  });
}

/* ok:true is what the client tests. Everything else in the object is the
   payload for that particular call. */
export const ok = (body = {}, headers = {}) =>
  json(Object.assign({ ok: true }, body), 200, headers);

/* `reason` is machine-readable and stable. `detail` is the sentence a person
   reads. The client prints detail where it has somewhere to print it, and
   falls back to its own copy where it does not. */
export const fail = (status, reason, detail = '') =>
  json({ ok: false, reason, detail }, status);

export const notFound = (what = 'that') =>
  fail(404, 'not found', 'There is no ' + what + ' here.');

/* 401 is special to the client: OrderStore treats it as "the staff session
   expired", drops the board and stops polling rather than deciding the
   service is gone. So an unauthenticated staff call must be 401 and must not
   be 403. */
export const unauthorised = () =>
  fail(401, 'no session', 'The counter is not signed in on this device.');

/* ---- reading a request without trusting it ---- */

/* A body that is not JSON, or is enormous, or is an array where an object was
   expected, is a bad request and not a 500. Nothing downstream should ever
   have to ask whether `body` is an object. */
export async function readJson(request, limit = 256 * 1024) {
  const len = Number(request.headers.get('content-length') || 0);
  if (len > limit) return null;
  let text;
  try { text = await request.text(); } catch { return null; }
  if (text.length > limit) return null;
  if (!text) return {};
  try {
    const v = JSON.parse(text);
    return (v && typeof v === 'object' && !Array.isArray(v)) ? v : null;
  } catch { return null; }
}

export const str = (v, max = 200) =>
  (typeof v === 'string' ? v : v == null ? '' : String(v)).trim().slice(0, max);

export const digits = (v, max = 20) =>
  String(v == null ? '' : v).replace(/\D/g, '').slice(0, max);

/* Money the shop will actually charge, rounded the way a till rounds. Comes
   back as a number, never a string, because the client does arithmetic on it. */
export const money = v => {
  const n = Number(v);
  return Number.isFinite(n) ? Math.round(n * 100) / 100 : 0;
};

export const nowIso = () => new Date().toISOString();

/* The caller's address as the edge reports it. Used only for rate limiting a
   four digit PIN; it is never stored against a member or an order. */
export const callerIp = request =>
  request.headers.get('cf-connecting-ip') ||
  request.headers.get('x-forwarded-for') ||
  'unknown';
