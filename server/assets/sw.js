/* =====================================================================
   OFFLINE, REBUILT PROPERLY.

   Until stage 172 this app worked with the network off for exactly one
   reason: all 328 photographs were inside the document. That made the
   document 11.5 MB, re-downloaded whenever a price changed, and it was
   heading for the 25 MiB ceiling on a Workers static asset.

   The photographs are files now, so the offline property has to be built
   rather than inherited. This is that.

   WHAT IT BUYS: the shop keeps taking orders through an internet outage,
   which is the failure that actually happens. The iPad by the counter has
   the document and every photograph anyone has looked at.

   WHAT IT DOES NOT BUY: a cold first load with no signal ever. That was the
   emailed-around walkthrough, and opening app/index.html off a disk still
   does it — a file:// page needs no service worker and registers none.

   THREE RULES, AND THE REASONING IS THE WHOLE FILE.
   ===================================================================== */

const VERSION = '__VERSION__';
const SHELL = 'sp-shell-' + VERSION;

/* Photographs are named by the hash of their own bytes, so a name can never
   refer to different bytes later. That means this cache never needs a version
   and never needs invalidating: a replaced photograph arrives under a new
   name, and the old one is evicted below when nothing references it. */
const MEDIA = 'sp-media-v1';

self.addEventListener('install', event => {
  /* Just the document. Deliberately NOT the 309 photographs: a customer on
     cellular should not pay to download the whole shelf to look at one vape.
     The counter's iPad will hold the lot within a day of normal use, because
     of the runtime cache below. */
  event.waitUntil(
    caches.open(SHELL).then(c => c.add('/')).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keep = new Set([SHELL, MEDIA]);
    for (const k of await caches.keys()) if (!keep.has(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch { return; }
  if (url.origin !== self.location.origin) return;

  /* ---- 1. THE API IS NEVER CACHED, NOT EVEN A LITTLE ----
     A stale order board is worse than no order board: it shows a counter
     tickets that were collected ten minutes ago, and shows a customer a
     reward that has already been taken off. Everything under /api goes to
     the network or fails honestly, and the app already knows how to say
     "we could not reach the register". */
  if (url.pathname === '/api' || url.pathname.startsWith('/api/')) return;

  /* ---- 2. PHOTOGRAPHS: CACHE FIRST, FOREVER ----
     The name is a hash of the bytes, so a hit is always correct. */
  if (url.pathname.startsWith('/img/')) {
    event.respondWith((async () => {
      const cache = await caches.open(MEDIA);
      const hit = await cache.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res.ok) cache.put(req, res.clone());
        return res;
      } catch (e) {
        /* A picture that will not load is a gap, and a gap is what the app
           already draws for a product with no photograph. Rule 2 in
           CLAUDE.md: nothing is substituted, ever. */
        return new Response('', { status: 504, statusText: 'offline' });
      }
    })());
    return;
  }

  /* ---- 3. THE DOCUMENT: NETWORK FIRST, CACHE AS THE FLOOR ----
     Network first, because a price edited at the counter has to reach a
     customer's phone on its next open and a cached document would hold it
     back for a day. Cache as the floor, because a shop with no internet
     still has to open the app. */
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res.ok) {
          const cache = await caches.open(SHELL);
          cache.put('/', res.clone());
        }
        return res;
      } catch (e) {
        const hit = await caches.match('/', { cacheName: SHELL });
        if (hit) return hit;
        throw e;
      }
    })());
  }
});
