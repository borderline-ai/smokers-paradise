/* =====================================================================
   SMOKERS PARADISE — THE SERVICE.

   One Worker. It serves the app and it answers the app, from the same
   origin, and that is not a convenience — it is forced.

   `call()` in app/index.html sends `credentials: 'same-origin'`, and the
   counter's proof that it is the counter is a cookie. A cookie on a
   same-origin request is sent; a cookie on a cross-origin one is not, unless
   it is SameSite=None, which is exactly the setting that would let a link in
   a text message make the counter's own browser add a visit. So the API is
   served beside the page or the register board does not work. That rules out
   hosting the app on GitHub Pages and the API somewhere else, and it is the
   reason this Worker serves a 12MB HTML file.

   Routes are matched exactly and in one place. Anything under /api that is
   not on this list is a JSON 404, never the app's HTML, because the client
   reads a non-JSON answer as "there is no shop here" and turns the whole
   ordering surface off.
   ===================================================================== */

import { ok, fail, notFound, readJson, str, nowIso } from './http.js';
import { requireSession, signIn, signOut } from './session.js';
import { readConfig, writeConfig, cleanRewards, DEFAULT_REWARDS, DEFAULT_PRICING } from './config.js';
import * as M from './members.js';
import * as O from './orders.js';
import * as C from './catalog.js';
import * as Sub from './subscribers.js';
import * as Media from './media.js';
import * as Points from './loyalty.js';
import { counterStaffId } from './loyalty.js';
import * as Out from './outbound.js';
import { notify, EVENTS, memberFields, birthdaySweep } from './notify.js';

const API = '/api';

/* The app is handed its API base and, on the counter address, the flag that
   makes it put the PIN pad up. Injected here rather than baked into the file
   so the same build runs from a disk with no server, which is tested. */
function injectBoot(response, staff) {
  /* <base> FIRST, before anything in the document can resolve a relative URL.

     Since stage 172 every photograph is referenced as `img/<hash>.webp` with
     no leading slash, so that the same file also works opened straight off a
     disk. Served, that relative path has to resolve against the root or the
     counter address would ask for /counter/img/... and get nothing. One tag
     fixes it for every URL in the document at once, which is why the paths
     are relative rather than root-relative in the first place. */
  const boot = '<base href="/">' +
    '<script>window.SP_API=' + JSON.stringify(API) +
    (staff ? ';window.SP_STAFF=1' : '') + ';</script>';

  const headers = new Headers(response.headers);
  /* The counter address must never be cached by anything in between: a cached
     copy carrying SP_STAFF served to a customer would put a PIN pad in front
     of a shopper. */
  headers.set('cache-control', staff ? 'no-store' : 'public, max-age=300, must-revalidate');
  if (staff) headers.set('x-robots-tag', 'noindex, nofollow');

  /* HTMLRewriter streams, which is the only sane way to put eleven megabytes
     through a Worker. It exists only in the Workers runtime, so the same
     handler running under plain Node — scripts/serve.mjs, and the browser test
     that drives it — takes the slow path instead. Same output, and the point
     of the fallback is that the thing under test is this file and not a second
     implementation of it. */
  if (typeof HTMLRewriter !== 'undefined') {
    return new HTMLRewriter()
      .on('head', { element(el) { el.prepend(boot, { html: true }); } })
      .transform(new Response(response.body, { status: response.status, headers }));
  }
  return response.text().then(html => {
    const i = html.search(/<head[^>]*>/i);
    const at = i < 0 ? 0 : i + html.slice(i).indexOf('>') + 1;
    return new Response(html.slice(0, at) + boot + html.slice(at),
      { status: response.status, headers });
  });
}

async function serveApp(request, env, staff) {
  const url = new URL(request.url);
  url.pathname = '/index.html';
  const res = await env.ASSETS.fetch(new Request(url.toString(), { method: 'GET' }));
  if (!res.ok) return res;
  return injectBoot(res, staff);
}

/* Reads the two pieces of config nearly every handler needs. One place, so a
   handler can never accidentally price a redemption against a stale rule. */
async function shopState(env, shop) {
  const [rw, pr] = await Promise.all([
    readConfig(env, shop, 'rewards', DEFAULT_REWARDS),
    readConfig(env, shop, 'pricing', DEFAULT_PRICING)
  ]);
  return { rule: rw.value, ruleRev: rw.rev, pricing: pr.value };
}

async function handleApi(request, env, ctx, url, shop) {
  const path = url.pathname.slice(API.length) || '/';
  const method = request.method.toUpperCase();
  const seg = path.split('/').filter(Boolean);

  /* Every write reads its body once, here, so no handler has to think about
     a request that is not JSON or is a hundred megabytes. */
  let body = {};
  if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
    /* A whole shop's inventory is a bigger thing than a join, and it arrives
       as one POST. Everything else stays on the small limit, because a 2 MB
       ceiling on /orders would only ever be used by somebody abusing it. */
    /* A photograph is not JSON. Its route reads the body itself. */
    if (path === '/staff/media') {
      const guard = await requireSession(request, env, shop);
      if (guard instanceof Response) return guard;
      return Media.upload(request, env);
    }
    const big = path.startsWith('/staff/catalog/');
    body = await readJson(request, big ? 4 * 1024 * 1024 : 256 * 1024);
    if (body === null) {
      return fail(400, 'bad body', big
        ? 'That file was not readable, or it is bigger than 4 MB.'
        : 'That request was not readable JSON.');
    }
  }

  /* ---- staff first, because the guard has to come before the routing ----
     A /staff/ path cannot reach a handler without a live session. Putting the
     check here rather than in each handler means a route added later is
     protected by default instead of by remembering. */
  if (seg[0] === 'staff') {
    if (seg[1] === 'session') {
      if (method === 'POST') return signIn(request, env, shop, body);
      if (method === 'DELETE') return signOut(request, env, shop);
      return fail(405, 'bad method', 'That is not how you sign in.');
    }

    const guard = await requireSession(request, env, shop);
    if (guard instanceof Response) return guard;
    const sid = guard.id;
    const { rule, pricing } = await shopState(env, shop);

    /* the register board */
    if (seg[1] === 'orders' && seg.length === 2 && method === 'GET') return O.board(env, shop);
    if (seg[1] === 'orders' && seg[3] === 'status' && method === 'POST') {
      const res = await O.setStatus(env, shop, seg[2], body.status);
      if (res.status === 200 && str(body.status, 20) === 'ready') {
        const who = await O.readForNotify(env, shop, seg[2]);
        /* Only when there is somewhere to send it. An order placed without an
           address is collected the way it always was: the customer's own
           screen follows the counter. */
        if (who && who.email) {
          notify(env, ctx, shop, rule, EVENTS.ORDER_READY, who);
        }
      }
      return res;
    }

    /* the rewards counter */
    if (seg[1] === 'members' && seg.length === 2 && method === 'GET') {
      const res = await M.lookup(env, shop, url.searchParams, rule);
      if (res.status !== 200) return res;
      const body = await res.json();
      try {
        const m = await env.DB
          .prepare('SELECT id, age_verified_at FROM members WHERE shop = ?1 AND code = ?2')
          .bind(shop, str(body.member.code, 12)).first();
        if (m) {
          body.points = await Points.standing(env, shop, m.id);
          /* The counter has to know before it offers a reward, not after. */
          body.member.ageVerified = !!m.age_verified_at;
        }
      } catch (e) { /* no points programme here yet */ }
      return ok(body);
    }

    /* THE ONE CALL THE COUNTER MAKES. Rings the sale, credits points on what
       is actually tendered, and optionally spends a tier against that same
       sale. One call, one idempotency key, one confirm at the till. */
    if (seg[1] === 'checkout' && method === 'POST') {
      const staffId = await counterStaffId(env, shop);
      const pricing2 = await readConfig(env, shop, 'points', {
        points_per_dollar: 10, min_tender_cents: 1, max_txn_cents: 30000
      });
      return Points.checkout(env, shop, staffId, body, pricing2.value);
    }

    /* Somebody looked at an ID across the counter. Recorded once, and it is
       what unlocks redeeming — joining on a phone verifies nobody. */
    if (seg[1] === 'members' && seg[3] === 'verify' && method === 'POST') {
      const staffId = await counterStaffId(env, shop);
      const r = await env.DB.prepare(
        `UPDATE members SET age_verified_at = ?3, age_verified_by = ?4,
                            age_verify_method = 'id_checked'
          WHERE shop = ?1 AND code = ?2 AND left_at IS NULL`
      ).bind(shop, str(seg[2], 12).toUpperCase(), nowIso(), staffId).run();
      return ok({ verified: true });
    }
    if (seg[1] === 'members' && seg[2] === 'list' && method === 'GET') {
      return M.list(env, shop, url.searchParams, rule);
    }
    if (seg[1] === 'members' && seg[2] === 'export.csv' && method === 'GET') {
      return M.exportCsv(env, shop, rule);
    }
    if (seg[1] === 'subscribers' && seg[2] === 'export.csv' && method === 'GET') {
      return Sub.exportCsv(env, shop);
    }
    if (seg[1] === 'members' && seg[3] === 'visit' && method === 'POST') {
      const before = await M.readForNotify(env, shop, seg[2], rule);
      const res = await M.addVisit(env, shop, seg[2], sid, rule, { force: !!body.force });
      /* The message worth sending. Raised only on the visit that CROSSES the
         threshold, not on every visit after it — somebody sitting on a ready
         reward for three weeks should hear about it once, not weekly. */
      if (res.status === 200) {
        const after = await M.readForNotify(env, shop, seg[2], rule);
        if (after && before && after.progress.ready > before.progress.ready && after.member.email) {
          notify(env, ctx, shop, rule, EVENTS.REWARD_READY,
            Object.assign(memberFields(after.member), {
              reward: str(rule.reward, 80),
              ready: after.progress.ready,
              visits: after.progress.total
            }));
        }
      }
      return res;
    }
    if (seg[1] === 'members' && seg[3] === 'redeem' && method === 'POST') {
      return M.redeem(env, shop, seg[2], sid, rule);
    }

    /* the rule, and where new members are sent */
    if (seg[1] === 'config' && method === 'GET') {
      return ok({ rewards: rule, pricing, crm: await Out.status(env, shop) });
    }
    if (seg[1] === 'config' && method === 'POST') {
      const next = cleanRewards(body.rewards || body, rule);
      if (next.error) return fail(400, 'bad rule', next.error);
      const rev = await writeConfig(env, shop, 'rewards', next.value);
      return ok({ rewards: next.value, rev });
    }

    /* the shelf */
    if (seg[1] === 'catalog' && seg.length === 2 && method === 'GET') {
      return Media.editorCatalog(env, shop, url.searchParams);
    }
    if (seg[1] === 'catalog' && seg[2] === 'seed' && method === 'POST') {
      return C.seed(env, shop, body);
    }
    if (seg[1] === 'catalog' && seg[2] === 'overrides' && method === 'POST') {
      return C.saveOverrides(env, shop, body);
    }
    if (seg[1] === 'catalog' && seg[2] === 'import' && method === 'POST') {
      return C.importCatalogue(env, shop, body);
    }

    return notFound('counter route');
  }

  /* ---- everything a customer's phone may call ---- */

  if (path === '/health' && method === 'GET') {
    return ok({ shop, at: nowIso() });
  }

  if (path === '/config' && method === 'GET') {
    const { rule, ruleRev, pricing } = await shopState(env, shop);
    /* `endpoint` is the shop's own CRM webhook. It is not a customer's
       business and a public config that leaks it is a public config that
       lets anybody post fake members into the shop's list. */
    const { endpoint, ...publicRule } = rule;
    /* The ladder travels with the rule, because a card that cannot name the
       next rung cannot show somebody what they are working toward. Labels are
       dollar amounts; the tier's internal name is the owner's, for her
       reports, and never reaches a customer's screen. */
    let tiers = { results: [] };
    try {
      tiers = await env.DB.prepare(
        `SELECT id, points_cost, discount_cents, min_subtotal_cents
           FROM reward_tiers WHERE shop = ?1 AND active = 1
          ORDER BY sort_order, points_cost`
      ).bind(shop).all();
    } catch (e) { /* no ladder on this shop yet */ }
    return ok({
      rewards: publicRule, pricing, rev: ruleRev,
      points: { perDollar: (pricing && pricing.pointsPerDollar) || 10 },
      tiers: (tiers.results || []).map(t => ({
        id: t.id, points: t.points_cost,
        label: '$' + (t.discount_cents / 100).toFixed(2).replace(/\.00$/, '') + ' off',
        discountCents: t.discount_cents, minSubtotalCents: t.min_subtotal_cents
      }))
    });
  }

  /* The external loyalty provider, answered honestly. `Loyalty` in the app is
     a client for a provider this shop does not have, and saying provider:none
     is what makes the app fall through to the shop's own programme instead of
     showing a broken points screen. */
  if (path === '/loyalty/status' && method === 'GET') {
    return ok({
      provider: 'none',
      capabilities: { live: false, demo: false, lookup: false, balance: false,
                      rewards: false, redeem: false, earn: false, reverse: false,
                      history: false },
      note: 'Smokers Paradise runs its own rewards programme. There is no external provider.'
    });
  }
  if (seg[0] === 'loyalty') {
    return fail(404, 'no provider', 'This shop has no external loyalty provider.');
  }

  /* members */
  if (path === '/members' && method === 'POST') {
    const { rule } = await shopState(env, shop);
    const res = await M.join(env, shop, body, rule);
    /* Forward the join to the shop's CRM if they have one, without making the
       customer wait for somebody else's webhook to answer. */
    if (res.status === 200) {
      /* The flat shape a GoHighLevel inbound webhook was set up for, plus the
         address and what was consented to. `sms` is kept and kept false-able:
         the shop is not doing SMS, and a CRM that receives sms:true will
         eventually act on it.

         `type` is an added key, never a replacement — an automation somebody
         already built against the original shape keeps working. */
      notify(env, ctx, shop, rule, EVENTS.MEMBER_JOINED, {
        first: str(body.first, 60), phone: str(body.phone, 20).replace(/\D/g, ''),
        email: str(body.email, 160).toLowerCase(),
        birthday: str(body.birthday, 8),
        sms: !!body.sms, emailOk: !!body.emailOk, terms: str(body.terms, 400),
        code: str(body.code, 12), joined: str(body.joined, 40) || nowIso()
      });
    }
    return res;
  }
  if (path === '/members/me' && method === 'GET') {
    const { rule } = await shopState(env, shop);
    const res = await M.readMe(env, shop, url.searchParams.get('token'), rule);
    if (res.status !== 200) return res;
    /* The points standing rides alongside the visit progress rather than
       replacing it, so a build of the app that predates the ladder keeps
       working while one that knows about points reads the balance. */
    const body = await res.json();
    /* THE WHOLE ENRICHMENT IS OPTIONAL. A database that has not had the
       points migration run on it has no reward_tiers and no age_verified_at,
       and this endpoint still has a job to do. Additive means additive: it
       must never be able to break the answer it is decorating. */
    try {
      const m = await env.DB
        .prepare('SELECT id FROM members WHERE shop = ?1 AND token = ?2')
        .bind(shop, str(url.searchParams.get('token'), 60)).first();
      if (m) body.points = await Points.standing(env, shop, m.id);
    } catch (e) { /* no points programme here yet */ }
    return ok(body);
  }
  if (path === '/members/me/leave' && method === 'POST') {
    return M.leave(env, shop, body.token);
  }

  /* the deal-alerts list, which is not a membership */
  if (path === '/subscribers' && method === 'POST') {
    const res = await Sub.subscribe(env, shop, body);
    if (res.status === 200) {
      const { rule } = await shopState(env, shop);
      notify(env, ctx, shop, rule, EVENTS.SUBSCRIBED, {
        email: str(body.email, 160).toLowerCase(),
        source: str(body.source, 40) || 'deal-alerts',
        terms: str(body.terms, 400),
        joined: nowIso()
      });
    }
    return res;
  }
  if (path === '/subscribers/leave' && method === 'POST') {
    return Sub.unsubscribe(env, shop, body);
  }

  /* orders */
  if (path === '/orders' && method === 'POST') {
    const { pricing } = await shopState(env, shop);
    return O.place(env, shop, body, pricing);
  }
  if (path === '/orders/status' && method === 'GET') {
    return O.statuses(env, shop, url.searchParams);
  }
  if (seg[0] === 'orders' && seg[2] === 'arriving' && method === 'POST') {
    return O.arriving(env, shop, seg[1], body.state);
  }

  /* the shelf, as a phone reads it */
  if (path === '/catalog' && method === 'GET') return C.catalog(env, shop);
  if (path === '/catalog/overrides' && method === 'GET') return C.overrides(env, shop);
  if (path === '/availability' && method === 'GET') {
    return C.availability(env, shop, url.searchParams);
  }

  return notFound('route');
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const shop = env.SHOP || 'smokers-paradise';

    if (url.pathname === API || url.pathname.startsWith(API + '/')) {
      try {
        return await handleApi(request, env, ctx, url, shop);
      } catch (err) {
        /* A 500 that renders HTML would read to the client as "there is no
           shop here", which is a worse lie than "something broke". */
        console.error('api', url.pathname, err && err.stack || err);
        return fail(500, 'server', 'Something went wrong at the shop\'s end.');
      }
    }

    /* THE COUNTER IS A DIFFERENT APP.

       It used to be the customer app with a flag injected, which meant the
       register screen downloaded 1.9 MB of document and 309 photographs to
       show a lookup box and a ticket list. It is 36 KB now and it ships none
       of the customer-facing code — so what a customer can fetch no longer
       includes the menu editor, the member list screen or the till.

       The URL still reveals nothing on its own: the PIN pad stands in front
       of it and the PIN is checked here, not in the browser. */
    if (url.pathname === '/counter' || url.pathname === '/counter/') {
      const u = new URL(request.url);
      u.pathname = '/counter.html';
      const res = await env.ASSETS.fetch(new Request(u.toString(), { method: 'GET' }));
      if (!res.ok) return res;
      const h = new Headers(res.headers);
      h.set('cache-control', 'no-store');
      h.set('x-robots-tag', 'noindex, nofollow');
      return new Response(res.body, { status: res.status, headers: h });
    }

    if (url.pathname === '/' || url.pathname === '/index.html') {
      return serveApp(request, env, false);
    }

    /* Manifest, icons, service worker, anything else that ships beside the
       app. An unknown path falls back to the app itself, because this is a
       single-page app and a deep link is not a missing file. */
    const asset = await env.ASSETS.fetch(request);
    if (asset.status === 404 && url.pathname.startsWith('/img/')) {
      /* Shipped pictures win; an uploaded one is looked for only when stages/
         did not ship that name. Which cannot collide anyway — the name is the
         hash of the bytes. */
      const up = await Media.serve(env, url.pathname);
      if (up) return up;
      return fail(404, 'no image', 'There is no picture at that name.');
    }
    if (asset.status === 404) return serveApp(request, env, false);

    /* Photographs are named by the hash of their own bytes, so a given name
       can never refer to different bytes later. That is what makes a year of
       immutable caching safe rather than reckless: replacing a photograph
       produces a new name, so nobody is ever left holding a stale one. */
    if (url.pathname.startsWith('/img/')) {
      const h = new Headers(asset.headers);
      h.set('cache-control', 'public, max-age=31536000, immutable');
      return new Response(asset.body, { status: asset.status, headers: h });
    }
    /* The worker script itself must not be cached by the browser, or a deploy
       could not replace it and the shop would keep serving last week's app out
       of a cache it cannot reach. */
    if (url.pathname === '/sw.js') {
      const h = new Headers(asset.headers);
      h.set('cache-control', 'no-cache');
      return new Response(asset.body, { status: asset.status, headers: h });
    }
    return asset;
  },

  /* The CRM queue, drained on a timer as well as opportunistically, so a
     webhook that was down when somebody joined still gets them. */
  async scheduled(event, env, ctx) {
    const shop = env.SHOP || 'smokers-paradise';
    ctx.waitUntil((async () => {
      await Out.drain(env, 50);
      try {
        const { rule } = await shopState(env, shop);
        await birthdaySweep(env, shop, rule);
      } catch (e) {
        console.error('birthday sweep', e && e.stack || e);
      }
    })());
  }
};
