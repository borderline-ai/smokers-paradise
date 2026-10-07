#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 172 — the photographs come out of the HTML.
#
# 328 base64 blobs were inlined in app/index.html. Measured, they were 77% of
# the file: 5.98 MB of product cut-outs, 2.13 MB of product video, and the rest
# in scene shots and variant photos. The code around them is about 2.3 MB.
#
# Two things forced this.
#
# THE CEILING. A Cloudflare Workers static asset caps at 25 MiB. The file is
# 11.5 MiB and every photograph the owner adds moves it up. server/scripts/
# build.mjs already refuses rather than letting a deploy fail halfway, which
# turns a preference into a deadline.
#
# THE WASTE. Every one of those photographs is re-downloaded on every visit,
# because they are part of a document that changes whenever a price changes.
# A picture of a Geek Bar does not change when a price does.
#
# WHY THIS IS SMALL. Photographs already resolve through lookup maps keyed by
# product id, and the code that draws one does this:
#
#     if(PHOTOS[p.id]) return `<img src="${PHOTOS[p.id]}" alt="${esc(alt)}">`;
#
# The resolver does not care whether that string is a data URI or a path. So
# this stage changes values, not structure. Nothing that draws a card is
# touched.
#
# RELATIVE, NOT ROOT-RELATIVE, AND THAT IS THE WHOLE TRICK.
#
# The paths written here are `img/<hash>.webp`, with no leading slash. That one
# character is what lets the same file work in both worlds:
#
#   opened off a disk   file:///.../app/index.html  ->  file:///.../app/img/x.webp
#   served by the shop  <base href="/"> is injected ->  /img/x.webp
#
# A leading slash would break the first. An absolute URL would break both. The
# 65 Playwright suites drive the file:// case with every network request
# aborted, and they go on passing because a file:// image is not a network
# request.
#
# NAMED BY CONTENT. `<sha256[:16]>.webp`. Identical images collapse to one file
# for free, and the name changes only when the bytes change, which is what lets
# them be cached forever. A photograph that is replaced gets a new name rather
# than a stale copy on somebody's phone.
#
# SVG STAYS INLINE. The five remaining data URIs are icons of a few hundred
# bytes that are part of the layout. A request each to save nothing is a worse
# deal than the bytes.
#
# OFFLINE. Inlining everything was, until now, the only reason the app worked
# with the network off. That property is deliberate and tested, so it is not
# being dropped — it is being rebuilt properly, with a service worker. See the
# registration added at the end of this stage and server/assets/sw.js. The
# difference: the old way worked from a cold start with no signal ever; the new
# way needs one first load and then survives an outage, which is what a shop on
# Grand Ave actually needs.
import io, os, re, hashlib, base64, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'app', 'index.html')
IMG = os.path.join(ROOT, 'app', 'img')

s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---------------------------------------------------------------------------
# EXTRACT.
#
# Everything raster comes out. The manifest and the SVG icons stay, because
# they are structure rather than photography.
# ---------------------------------------------------------------------------
EXT = {'image/webp': '.webp', 'image/png': '.png', 'image/jpeg': '.jpg',
       'video/mp4': '.mp4', 'video/webm': '.webm'}

if os.path.isdir(IMG):
    shutil.rmtree(IMG)
os.makedirs(IMG)

blob = re.compile(r'data:([a-z]+/[a-z0-9+.-]+);base64,([A-Za-z0-9+/=]+)')

seen = {}
stats = {'files': 0, 'bytes': 0, 'dupes': 0, 'left': 0}


def swap(m):
    mime, b64 = m.group(1), m.group(2)
    ext = EXT.get(mime)
    if not ext:
        stats['left'] += 1
        return m.group(0)
    try:
        raw = base64.b64decode(b64, validate=False)
    except Exception:
        stats['left'] += 1
        return m.group(0)
    h = hashlib.sha256(raw).hexdigest()[:16]
    name = h + ext
    if name in seen:
        stats['dupes'] += 1
    else:
        with open(os.path.join(IMG, name), 'wb') as f:
            f.write(raw)
        seen[name] = len(raw)
        stats['files'] += 1
        stats['bytes'] += len(raw)
    return 'img/' + name


s, n = blob.subn(swap, s)
print('  %d data URIs rewritten, %d files written, %d duplicates collapsed, '
      '%d left inline' % (n, stats['files'], stats['dupes'], stats['left']))
print('  %.2f MB of media now on disk' % (stats['bytes'] / 1048576.0))
assert stats['files'] > 250, 'expected the whole catalogue, got %d' % stats['files']
assert stats['left'] == 6, 'expected 5 SVG icons and the manifest to stay, got %d' % stats['left']


# ---------------------------------------------------------------------------
# THE SERVICE WORKER.
#
# Registered only over http(s). On file:// there is no service worker and there
# does not need to be: nothing is being fetched over a network there anyway.
# Guarded so that a browser without one, or a refused registration, cannot stop
# the app from opening.
# ---------------------------------------------------------------------------
rep("""/* ================= boot ================= */""",
"""/* ================= offline =================
   Until stage 172 this app worked with the network off for one reason: every
   photograph was inside the document. That is no longer true, so the property
   is rebuilt rather than dropped.

   The worker caches the document and caches each photograph the first time it
   is actually shown. It does NOT pre-download all 300 of them: a customer on
   cellular should not pay for the whole shelf to look at one vape, and the
   iPad by the counter will have the lot within a day of normal use.

   What this buys: the shop keeps taking orders through an internet outage,
   which is the failure that actually happens on Grand Ave. What it does not
   buy: a cold first load with no signal. That was the emailed-around
   walkthrough file, and opening app/index.html off a disk still does it. */
(function(){
  if(typeof navigator === 'undefined' || !navigator.serviceWorker) return;
  if(!/^https?:$/.test(location.protocol)) return;   /* file:// needs none */
  window.addEventListener('load', function(){
    try{ navigator.serviceWorker.register('/sw.js', {scope: '/'}) }catch(e){}
  });
})();

/* ================= boot ================= */""")


io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars  (%.2f MB -> %.2f MB)'
      % (n0, len(s), n0 / 1048576.0, len(s) / 1048576.0))
