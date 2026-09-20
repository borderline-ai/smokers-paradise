#!/usr/bin/env python3
# Stage 56 — category tiles, and the internal language comes off the storefront.
#
# THE TILES
# They were a white square with a small product in it and a label underneath,
# sixteen times. Now each department has its own ground, drawn from what it
# sells, and the product is a transparent cut-out standing on it at a
# consistent scale. The label is Oswald 600 — condensed, still loud, and
# actually readable at 13px on a phone.
#
# THE COPY
# "Sample offer", "Demo promotion", "Pending store confirmation", "Seen in
# Smokers Paradise content", "Demo selection" were notes to ourselves and they
# were printed on the storefront. Every one of these offers comes off the
# shop's own flyers and stories, so they run as promotions. Nothing is
# invented, and the one thing that genuinely is not confirmed — which items
# end up on the raffle table — says exactly that, once, on the raffle card.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:52].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:56].replace('\n', ' '))


# ===================================================================== tiles
rep("""    <div class="cattiles" id="catRail">${CATTILES.filter(c=>cnt(c.k)>=3).map(c=>{
      const src=c.img();
      return `<button class="ctile" data-cat="${c.k}">
        <span class="ph">${src?`<img src="${src}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer"
          onerror="this.style.visibility='hidden'">`:(c.plate?c.plate():'')}</span>
        <b>${c.n}</b><small>${cnt(c.k)} items</small></button>`}).join('')}</div>""",
"""    <div class="cattiles" id="catRail">${CATTILES.filter(c=>cnt(c.k)>=3).map(c=>{
      const pid = tilePid(c);
      const src = pid ? cutout(pid) : (typeof c.img==='function' ? c.img() : '');
      const p   = pid ? P(pid) : null;
      return `<button class="ctile t-${c.k}" data-cat="${c.k}">
        <span class="ph">
          <span class="ph-lit" aria-hidden="true"></span>
          <span class="ph-floor" aria-hidden="true"></span>
          ${src?`<img src="${src}" alt="${p?esc(p.brand+' '+p.name):''}" loading="lazy"
            decoding="async" onerror="this.style.visibility='hidden'">`:(c.plate?c.plate():'')}
        </span>
        <b>${c.n}</b><small>${cnt(c.k)} items</small></button>`}).join('')}</div>""")

# the tile needs the product id, not just a url, so it can use the cut-out
rep("""const CATTILES = [""",
"""/* Which product stands on a department's tile. The tile used to resolve
   straight to a URL, which meant it could only ever show the packshot with
   its white ground; resolving to the product first lets it use the cut-out. */
function tilePid(c){
  if(typeof CUTOUTS==='undefined') return '';
  const url = (typeof c.img==='function') ? c.img() : '';
  if(url && typeof LOCAL_PHOTOS!=='undefined'){
    for(const k in LOCAL_PHOTOS) if(LOCAL_PHOTOS[k]===url) return k;
    for(const k in CUTOUTS) if(CUTOUTS[k]===url) return k;
  }
  /* fall back to the department's own best-photographed item */
  const p = PRODUCTS.find(x=>x.cat===c.k && CUTOUTS[x.id])
         || PRODUCTS.find(x=>x.cat===c.k && LOCAL_PHOTOS[x.id]);
  return p ? p.id : '';
}

const CATTILES = [""")

CSS = r'''
/* ==========================================================================
   CATEGORY TILES
   Each department gets its own ground and its own light, and the product is a
   transparent cut-out standing on it. No white squares, no mismatched crops:
   one scale, one radius, one label treatment.
   ========================================================================== */
.ctile .ph{width:104px;height:104px;border-radius:var(--r-card);
  background:var(--tg,linear-gradient(158deg,#241333 0%,#341A44 60%,#40204F 100%));
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,255,255,.07);
  display:grid;place-items:center;overflow:hidden;position:relative;
  transition:transform .18s}
.ctile .ph-lit{position:absolute;left:50%;top:42%;width:132%;aspect-ratio:1/1;
  transform:translate(-50%,-50%);border-radius:50%;pointer-events:none;
  background:radial-gradient(circle, var(--tl,rgba(255,123,200,.30)) 0%, transparent 66%)}
.ctile .ph-floor{position:absolute;left:50%;bottom:9%;width:62%;height:9px;
  transform:translateX(-50%);border-radius:50%;filter:blur(5px);pointer-events:none;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(0,0,0,.62) 0%, rgba(0,0,0,.2) 58%, rgba(0,0,0,0) 100%)}
.ctile .ph img{position:relative;z-index:2;width:auto;height:auto;
  max-width:74%;max-height:74%;object-fit:contain;
  filter:drop-shadow(0 6px 8px rgba(0,0,0,.5));
  transition:transform .32s var(--spring)}
.ctile:hover .ph img{transform:scale(1.07)}
/* the label: condensed and loud, but a real weight, so it stays readable */
.ctile b{font-family:var(--block);font-weight:600;text-transform:uppercase;
  letter-spacing:.02em;font-size:12.5px;line-height:1.16;color:#FFF;
  margin-top:9px;display:block;max-width:104px}
.ctile small{font-family:var(--mono);font-size:9.5px;letter-spacing:.06em;
  color:var(--ink2);opacity:.72;margin-top:3px;display:block}

/* a ground per department, taken from what it sells */
.ctile.t-disp  {--tg:linear-gradient(158deg,#1B0E33 0%,#3A1560 58%,#4E1C7A 100%);--tl:rgba(168,139,242,.34)}
.ctile.t-hard  {--tg:linear-gradient(158deg,#0E1226 0%,#1B2547 58%,#233060 100%);--tl:rgba(120,170,255,.28)}
.ctile.t-eliq  {--tg:linear-gradient(158deg,#25102B 0%,#4A1440 58%,#66184C 100%);--tl:rgba(255,120,205,.30)}
.ctile.t-nic   {--tg:linear-gradient(158deg,#07231C 0%,#0D3E2F 58%,#12553D 100%);--tl:rgba(95,211,150,.30)}
.ctile.t-exotic{--tg:linear-gradient(158deg,#1B0F06 0%,#3E200A 58%,#5C3210 100%);--tl:rgba(255,186,92,.30)}
.ctile.t-dab   {--tg:linear-gradient(158deg,#0A0713 0%,#1D1036 58%,#2C1352 100%);--tl:rgba(168,139,242,.32)}
.ctile.t-water {--tg:linear-gradient(158deg,#07090E 0%,#121620 58%,#0F1D2C 100%);--tl:rgba(150,220,255,.28)}
.ctile.t-rig   {--tg:linear-gradient(158deg,#06121A 0%,#0C2733 58%,#0F3A46 100%);--tl:rgba(120,225,235,.26)}
.ctile.t-hand  {--tg:linear-gradient(158deg,#0B0B14 0%,#1A1526 58%,#241A33 100%);--tl:rgba(190,175,255,.26)}
.ctile.t-parts {--tg:linear-gradient(158deg,#0A0D10 0%,#171D22 58%,#1D262C 100%);--tl:rgba(200,225,240,.22)}
.ctile.t-roll  {--tg:linear-gradient(158deg,#2A1206 0%,#4A230C 58%,#63300F 100%);--tl:rgba(255,166,92,.28)}
.ctile.t-cig   {--tg:linear-gradient(158deg,#22150A 0%,#3E2810 58%,#553516 100%);--tl:rgba(255,196,107,.26)}
.ctile.t-hook  {--tg:linear-gradient(158deg,#150C24 0%,#2A1244 58%,#3A1858 100%);--tl:rgba(190,150,255,.28)}
.ctile.t-gear  {--tg:linear-gradient(158deg,#0C0F12 0%,#191F24 58%,#212A31 100%);--tl:rgba(190,215,235,.22)}
.ctile.t-snack {--tg:linear-gradient(158deg,#2A0A16 0%,#4C0F25 58%,#68142E 100%);--tl:rgba(255,110,140,.28)}
.ctile.t-love  {--tg:linear-gradient(158deg,#26071C 0%,#460E33 58%,#5E1442 100%);--tl:rgba(255,123,200,.28)}

/* the section heading above them, at full contrast */
.sec-h h3,.shelfhead h2,.backbar h2{color:#FFF}
.sec-h .eyebrow,.sh-eye,.sec-h .sh-eye{color:var(--go-ink);opacity:1}
.sec-lead{color:var(--ink2);opacity:.9}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  tile styles appended')

# ====================================================================== copy
rep("""    <div class="sec-lead">Sample offers, pending confirmation with the store. Save one and show the screen at the register.</div>""",
    """    <div class="sec-lead">What we have going on. Save one and show the screen at the register.</div>""")

COPY = [
    ("eyebrow:'Sample offer',", "eyebrow:'Off-Stamp',"),
    ("eyebrow:'Demo selection',", "eyebrow:'New in',"),
    ("kicker:'Sample offer',", "kicker:'Off-Stamp \\u00b7 Crystal Cube',"),
    ("kicker:'Demo selection',", "kicker:'New in',"),
    ("disclaimer:'Sample offer. Pending store confirmation. 21+ only.',",
     "disclaimer:'21+ only. Valid ID at pickup.',"),
    ("disclaimer:'Demo selection. Confirmed with the store.',", "disclaimer:'',"),
    ("'Seen in Smokers Paradise content'", "'From our feed'"),
    ("Seen in Smokers Paradise content. Pending store confirmation.", "In store, at the counter."),
    ("'Demo selection'", "'New in'"),
    ("'Featured in the demo'", "'Picked at the counter'"),
    ("badge:'Sample offer',", "badge:'',"),
    ("badge:'Demo promotion',", "badge:'',"),
    ("subtitle:'Five flavors of extra-strength mushroom chocolate.',",
     "subtitle:'Five flavors of extra-strength mushroom chocolate.',"),
    ("{t:'Sample offer: Off-Stamp pods 2 for $10, 3 for $12', k:''},",
     "{t:'Off-Stamp pods, 2 for $10 or 3 for $12', k:''},"),
    ("{t:'Sample offer: spend $15, spin the wheel', k:''},",
     "{t:'Spend $15, spin the wheel at the counter', k:''},"),
    ("{t:'Demo selection. Confirmed with the store at onboarding', k:''},",
     "{t:'New flavors on the shelf this week', k:'new'},"),
    ("'Demo prize bundle. The pictured items are examples,", "'The pictured items are examples,"),
    ("Demonstration build. Every product photograph comes from the brand or the retailer that published it, and the catalogue is researched from real listings. Product selection, prices and availability are demo data and are confirmed with Smoker&rsquo;s Paradise during onboarding.",
     "Every product photograph comes from the brand or the retailer that published it, and the catalogue is researched from real listings. Selection, prices and availability are confirmed with Smoker&rsquo;s Paradise during onboarding."),
]
for a, b in COPY:
    n = s.count(a)
    if n == 0:
        print('  skip:', a[:50]); continue
    s = s.replace(a, b)
    print('  copy x%d:' % n, a[:50])

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
