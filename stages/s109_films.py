#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 109 — the films, and the honest count.
#
# Marco: "We need way more videos. We need 10x more product videos inside their
# display. When I scroll down I want to see the video of the product. Most of
# the brands have them for their products."
#
# I went and looked, properly, at every place a film could come from, and the
# answer is not the one either of us wanted. Written down here because the next
# person to pick this up should not spend the night finding it again.
#
# WHAT WAS SEARCHED. Thirteen manufacturer stores that answer cross-origin, and
# six of the large online head shops, by reading each store's own product feed
# and then each product's own media list — which is where a Shopify store keeps
# its video files, and it is exact: no scraping, no guessing.
#
#     GRAV                278 products      0 videos
#     Session Goods       147 products      0 videos
#     Smokebuddy           74 products      0 videos
#     Santa Cruz Shredder 119 products      0 videos
#     Kaloud              110 products      0 videos
#     King Palm           331 products      0 videos
#     Zippo             1,232 products      0 videos
#     Smoke Cartel      1,250 products      0 videos
#     Juice Head           60 products      0 videos
#     Eyce                 48 products      1 video   (a banger bundle we do not carry)
#     MJ Arsenal          292 products     11 videos  (none of our four models)
#     Ooze                470 products     26 videos  (none of our two)
#     Stundenglass        176 products     20 videos  (the Gravity Infuser: ours)
#     Puffco              164 products     29 videos  (four of ours)
#     DankGeek, BadAssGlass, Headshop.com, Grasscity, Daily High Club,
#     The Dabbing Specialists: 1,589 listings carrying our brands, 11 videos,
#     of which one was for a product we stock.
#
# So: GRAV, the biggest name on this shelf at thirty products, publishes no
# product video at all. Neither does Session Goods. The film is a Puffco and
# Stundenglass habit, not an industry one, and the six retailers who resell
# everybody have almost none either.
#
# WHAT IS BLOCKED, AND HOW MARCO UNBLOCKS IT. Every other brand — Pulsar,
# Lookah, Diamond Glass, Higher Standards, Marley Natural, and the whole
# disposable wall: Geek Bar, RAZ, Lost Mary, Elf Bar, Flum, Off-Stamp, Air Bar,
# Fume, Tyson, Fifty Bar and the rest — refuses a cross-origin read, so their
# feeds can only be read by opening their site in the browser, and the browser
# asks Marco to approve each site before it will load it. He was asleep. That
# is the entire blocker: it is one approval list, not a research problem, and
# the scanner is written and proven. Ask him for it and the disposable wall
# gets scanned in about twenty minutes.
#
# WHAT SHIPPED TONIGHT: seven films, embedded.
#
# They were five, and all five were REMOTE URLs on puffco.com. In a shop in
# Nogales with no wifi, which is the room this app has to work in, every one of
# those was a black rectangle, and so were the two films on the home screen.
# The five are now eight products' worth of film carried IN the file, along
# with the two home screen bands, cut to their product shots, re-encoded at
# 480px baseline H.264, six seconds at most: 860 KB for all seven, posters
# included. The demo no longer needs a network to play a video.
#
# The Pivot film is a twenty four second lifestyle ad — a party, a beach, a DJ
# — with the product on screen for about three of them. Those three are the
# clip. A product page shows the product.
#
# AND THE PRESENTATION, which is the part of his note that was actually about
# the app rather than about supply: "when I scroll down I want to see the video
# of the product". It was a black frame with a play button on it, preload off,
# waiting to be pressed. It now starts itself when it reaches the screen,
# silently, looping, and stops when it leaves — and it carries a poster frame,
# so it is a picture of the product before it is anything else, never a black
# hole in the middle of the page.
import io
import json
import base64
import os

P = '/root/work/smokers-paradise-demo/build/index.html'
VID = '/tmp/spnight/vid'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


def datauri(path, mime):
    with open(path, 'rb') as fh:
        return 'data:%s;base64,%s' % (mime, base64.b64encode(fh.read()).decode())


# film file -> the source page it came off, for the credit line
FILMS = {
    'spv1_peakpro':  'https://www.puffco.com/products/the-peak-pro',
    'spv2_proxypipe':'https://www.puffco.com/products/proxy-kit',
    'spv3_proxycore':'https://www.puffco.com/products/proxy-core-kit',
    'spv4_pivot':    'https://www.puffco.com/products/pivot',
    'spv5_hotknife': 'https://www.puffco.com/products/the-puffco-hot-knife',
    'spv6_peak3d':   'https://www.puffco.com/products/new-peak-3d-chambers',
    'spv7_stunden':  'https://stundenglass.com/products/stundenglass-gravity-infuser',
}

# Which products each film is a film OF. A film is only attached to the product
# it actually shows: the Peak Pro film is not a film of the Peak, and the 3D
# chamber film is not a film of the 3DXL chamber, so neither is borrowed.
ATTACH = [
    ('Puffco|Peak Pro 3DXL',  'spv1_peakpro'),
    ('Puffco|Proxy Pipe Kit', 'spv2_proxypipe'),
    ('Puffco|Proxy Pipe',     'spv2_proxypipe'),
    ('Puffco|Proxy Core Kit', 'spv3_proxycore'),
    ('Puffco|Proxy Core',     'spv3_proxycore'),
    ('Puffco|Pivot',          'spv4_pivot'),
    ('Puffco|Hot Knife',      'spv5_hotknife'),
    ('Puffco|Peak 3D Chamber','spv6_peak3d'),
    ('Stundenglass|Gravity Infuser (Classic)', 'spv7_stunden'),
]

media = {}
for k, src in FILMS.items():
    mp4 = os.path.join(VID, k + '.mp4')
    wbm = os.path.join(VID, k + '.webm')
    pw = os.path.join(VID, k + '.webp')
    media[k] = {'u': datauri(mp4, 'video/mp4'),
                'w': datauri(wbm, 'video/webm'),
                'p': datauri(pw, 'image/webp'),
                's': src,
                'kb': (os.path.getsize(mp4) + os.path.getsize(wbm)) // 1024}

table = {}
for key, film in ATTACH:
    m = media[film]
    table[key] = {'url': m['u'], 'webm': m['w'], 'poster': m['p'], 'source': m['s']}

print('  ok: %d films, %d KB of video, attached to %d products'
      % (len(media), sum(m['kb'] for m in media.values()), len(table)))

# ---- 1. the table, now carried in the file ---------------------------------
k = 'const PRODUCT_VIDEO='
i = s.index(k)
j = s.index('};\n', i) + 1
s = (s[:i]
     + '/* THE FILMS ARE IN THIS FILE.\n'
       '   These were five remote URLs on puffco.com. In a shop in Nogales with no\n'
       '   wifi, which is the room this app has to work in, every one of them was a\n'
       '   black rectangle. They are carried here now: 480px baseline H.264, six\n'
       '   seconds at most, cut to the part of the film that shows the product,\n'
       '   with a poster frame so the page never shows black. 860 KB for all seven.\n'
       '   A film is attached only to the product it is actually a film of. */\n'
     + k + json.dumps(table, separators=(',', ':')) + s[j:])

# ---- 2. the home bands play their own copies -------------------------------
rep("""  if(!v || !/^https?:\\/\\//.test(v.url) || /youtube|youtu\\.be|vimeo/.test(v.url)) return '';""",
"""  /* A data URI is the file itself, which is the whole point of embedding it;
     the guard is against a hosted PLAYER, not against a local file. */
  if(!v || !/^(https?:|data:video)/.test(v.url) || /youtube|youtu\\.be|vimeo/.test(v.url)) return '';""")

rep("""      <video id="spotVid" src="${v.url}" muted loop playsinline preload="none"
        aria-label="${esc(p.brand + ' ' + p.name)}, manufacturer footage"
        onerror="const s=this.closest('.sec'); if(s) s.remove()"></video>""",
"""      <video id="spotVid" src="${v.url}" poster="${v.poster||''}" ${v.webm?`data-webm="${v.webm}"`:''}
        muted loop playsinline preload="metadata"
        aria-label="${esc(p.brand + ' ' + p.name)}, manufacturer footage"
        onerror="if(!filmFail(this)){const s=this.closest('.sec'); if(s) s.remove()}"></video>""")

# the glass band, same file, same fallback
rep("""        ? `<video id="glassVid" src="${film.url}" muted loop playsinline preload="none"
             ${film.poster?`poster="${film.poster}"`:''}
             aria-label="${esc((film.brand||'Smokers Paradise') + ' gravity film')}"
             onerror="const b=this.closest('.glassband'); if(b){this.remove(); b.classList.add('nophoto')}"></video>`""",
"""        ? `<video id="glassVid" src="${film.url}" muted loop playsinline preload="metadata"
             ${film.poster?`poster="${film.poster}"`:''} ${film.webm?`data-webm="${film.webm}"`:''}
             aria-label="${esc((film.brand||'Smokers Paradise') + ' gravity film')}"
             onerror="if(!filmFail(this)){const b=this.closest('.glassband'); if(b){this.remove(); b.classList.add('nophoto')}}"></video>`""")

# the glass band's film, off the same local copy
rep("""const GLASS_FILM = {
  url:    'https://stundenglass.com/cdn/shop/videos/c/vp/12d6eddcc8cc486da1609097ff3b3df7/12d6eddcc8cc486da1609097ff3b3df7.HD-720p-3.0Mbps-85174064.mp4?v=0',
  poster: 'https://stundenglass.com/cdn/shop/files/preview_images/12d6eddcc8cc486da1609097ff3b3df7.thumbnail.0000000000_500x.jpg?v=1779987757',""",
"""/* Was a 720p file on stundenglass.com, which is a black band in a shop with no
   wifi. Same film, carried in this file. */
const GLASS_FILM = {
  url:    (typeof PRODUCT_VIDEO!=='undefined'
           && PRODUCT_VIDEO['Stundenglass|Gravity Infuser (Classic)'])
          ? PRODUCT_VIDEO['Stundenglass|Gravity Infuser (Classic)'].url : '',
  poster: (typeof PRODUCT_VIDEO!=='undefined'
           && PRODUCT_VIDEO['Stundenglass|Gravity Infuser (Classic)'])
          ? PRODUCT_VIDEO['Stundenglass|Gravity Infuser (Classic)'].poster : '',
  webm:   (typeof PRODUCT_VIDEO!=='undefined'
           && PRODUCT_VIDEO['Stundenglass|Gravity Infuser (Classic)'])
          ? PRODUCT_VIDEO['Stundenglass|Gravity Infuser (Classic)'].webm : '',""")

# the glass band's own guard was https-only too
rep("""  const film = GLASS_FILM && GLASS_FILM.url && /^https?:\\/\\//.test(GLASS_FILM.url)""",
"""  const film = GLASS_FILM && GLASS_FILM.url && /^(https?:|data:video)/.test(GLASS_FILM.url)""")

# ---- 3. the product page film: it plays when you reach it ------------------
rep("""        : `<div class="pvid"><video src="${vid.url}" ${vid.poster?`poster="${vid.poster}"`:''}
             muted playsinline preload="none" controls
             onerror="this.closest('.pvid').remove()"></video>
             <div class="vcap">Official ${p.brand} footage</div></div>`}`:''}""",
"""        : `<div class="pvid"><video class="autofilm" src="${vid.url}" ${vid.poster?`poster="${vid.poster}"`:''}
             ${vid.webm?`data-webm="${vid.webm}"`:''}
             muted loop playsinline preload="metadata" controls
             aria-label="${esc(p.brand+' '+p.name)}, manufacturer footage"
             onerror="if(!filmFail(this)) this.closest('.pvid').remove()"></video>
             <div class="vcap"><span>Film by ${esc(p.brand)}. No sound.</span>${
               vid.source?`<a href="${vid.source}" target="_blank" rel="noopener noreferrer">Source</a>`:''}
             </div></div>`}`:''}""")

rep("""function specTable(p){""",
"""/* ---- one file, two containers ----
   Every film here is carried twice: H.264 in an mp4, which is the only thing
   an iPad will play, and VP9 in a webm, which is the only thing a browser
   built without the licensed decoder will play. That second case is not
   theoretical — it is the browser this app's own test suite runs in, which is
   why five remote films sat in this app for weeks with every test passing and
   not one of them ever played in a test.

   The mp4 is what loads. If the decoder refuses it, this swaps the webm in
   once and tries again; if that fails too the caller removes the frame, which
   is what it did before. */
function filmFail(el){
  const w = el.getAttribute('data-webm');
  if(!w || el.getAttribute('data-alt') === '1') return false;
  el.setAttribute('data-alt','1');
  el.src = w;
  try{ el.load() }catch(e){}
  const pr = el.play(); if(pr && pr.catch) pr.catch(()=>{});
  return true;
}

/* ---- a film starts when you reach it ----
   Marco: "when I scroll down I want to see the video of the product". It was a
   black frame with a play button, preload off, waiting to be pressed. A film on
   a product page is a photograph that moves; nobody presses play on a
   photograph. It runs silently while it is on the screen and stops the moment
   it is not, which is also the only version of this that does not decode video
   for a page nobody is looking at.

   Controls stay on, so anyone who wants to stop it, scrub it or take it full
   screen still can. Under reduced motion it never starts itself. */
function wireFilms(scope){
  const vs = (scope||document).querySelectorAll('video.autofilm:not([data-wired])');
  if(!vs.length) return;
  const reduced = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const main = document.getElementById('main');
  vs.forEach(v => {
    v.setAttribute('data-wired','1');
    if(reduced) return;
    const root = (main && main.contains(v)) ? main : null;
    const io = new IntersectionObserver(es => es.forEach(e => {
      if(e.isIntersecting){ const pr = v.play(); if(pr && pr.catch) pr.catch(()=>{}) }
      else if(!v.paused) v.pause();
    }), {root:root, rootMargin:'0px', threshold:0.35});
    io.observe(v);
  });
}
/* Every screen that can paint one, without thirty call sites. */
(function filmWatch(){
  if(typeof MutationObserver === 'undefined') return;
  let q = false;
  const sweep = () => { q = false; try{ wireFilms() }catch(e){} };
  const mo = new MutationObserver(() => { if(q) return; q = true; requestAnimationFrame(sweep) });
  /* The product sheet is NOT inside #main, so watching #main alone meant the
     one screen that actually carries a film never got wired. */
  const begin = () => { mo.observe(document.body, {childList:true, subtree:true}); sweep() };
  if(document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', begin, {once:true});
  else begin();
})();

function specTable(p){""")

rep(""".pvid .vcap{display:flex;align-items:center;gap:6px;padding:7px 10px;background:var(--card2);""",
""".pvid .vcap a{margin-left:auto;color:var(--go-ink);font-weight:700;text-decoration:underline}
.pvid .vcap span{min-width:0}
.pvid .vcap{display:flex;align-items:center;gap:6px;padding:7px 10px;background:var(--card2);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
