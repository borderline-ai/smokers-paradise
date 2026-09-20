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
import * as Out from './outbound.js';

const API = '/api';

/* The app is handed its API base and, on the counter address, the flag that
   makes it put the PIN pad up. Injected here rather than baked into the file
   so the same build runs from a disk with no server, which is tested. */
function injectBoot(response, staff) {
  const boot = '<script>window.SP_API=' + JSON.stringify(API) +
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
    body = await readJson(request);
    if (body === null) return fail(400, 'bad body', 'That request was not readable JSON.');
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
      return O.setStatus(env, shop, seg[2], body.status);
    }

    /* the rewards counter */
    if (seg[1] === 'members' && seg.length === 2 && method === 'GET') {
      return M.lookup(env, shop, url.searchParams, rule);
    }
    if (seg[1] === 'members' && seg[2] === 'export.csv' && method === 'GET') {
      return M.exportCsv(env, shop, rule);
    }
    if (seg[1] === 'members' && seg[3] === 'visit' && method === 'POST') {
      return M.addVisit(env, shop, seg[2], sid, rule, { force: !!body.force });
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
    if (seg[1] === 'catalog' && seg[2] === 'seed' && method === 'POST') {
      return C.seed(env, shop, body);
    }
    if (seg[1] === 'catalog' && seg[2] === 'overrides' && method === 'POST') {
      return C.saveOverrides(env, shop, body);
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
    return ok({ rewards: publicRule, pricing, rev: ruleRev });
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
    if (res.status === 200 && rule.endpoint) {
      const payload = {
        first: str(body.first, 60), phone: str(body.phone, 20).replace(/\D/g, ''),
        birthday: str(body.birthday, 8), sms: !!body.sms,
        code: str(body.code, 12), joined: str(body.joined, 40) || nowIso(), shop
      };
      ctx.waitUntil(
        Out.enqueue(env, shop, rule.endpoint, payload).then(() => Out.drain(env, 5))
      );
    }
    return res;
  }
  if (path === '/members/me' && method === 'GET') {
    const { rule } = await shopState(env, shop);
    return M.readMe(env, shop, url.searchParams.get('token'), rule);
  }
  if (path === '/members/me/leave' && method === 'POST') {
    return M.leave(env, shop, body.token);
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

    /* The counter has its own address. The URL reveals nothing on its own:
       the PIN pad still stands in front of it and the PIN is checked here. */
    if (url.pathname === '/counter' || url.pathname === '/counter/') {
      return serveApp(request, env, true);
    }

    if (url.pathname === '/' || url.pathname === '/index.html') {
      return serveApp(request, env, false);
    }

    /* Manifest, icons, service worker, anything else that ships beside the
       app. An unknown path falls back to the app itself, because this is a
       single-page app and a deep link is not a missing file. */
    const asset = await env.ASSETS.fetch(request);
    if (asset.status === 404) return serveApp(request, env, false);
    return asset;
  },

  /* The CRM queue, drained on a timer as well as opportunistically, so a
     webhook that was down when somebody joined still gets them. */
  async scheduled(event, env, ctx) {
    ctx.waitUntil(Out.drain(env, 50));
  }
};
