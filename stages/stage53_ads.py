#!/usr/bin/env python3
# Stage 53 — every promotion becomes its own advertisement.
#
# What was there: one rectangle, one plum ground, one layout, a packshot in a
# white box on the right and the copy on the left, six times over. That is a
# template with the words swapped, and it is why the page read as populated
# rather than designed.
#
# What replaces it: six concepts, four layouts, each ground built from the
# product it is selling, each product a transparent cut-out lit from behind and
# standing on its own shadow, and each one with its own idea of what the offer
# is. Nothing shares a composition with anything else.
#
#   OFF-STAMP   two real flavours angled into each other, iced cyan, the price
#               the largest thing on the card
#   TRE HOUSE   cacao and gold, the bar large and low, warm rim light
#   SPIN-N-WIN  carnival: gold rays, the wheel whole and never cropped
#   RAFFLE      the prize table, on a dark stage now the products are cut out
#   GLASS       near-black, one beaker lit like a still life
#   PUFFCO      graphite and violet, the device photographed as technology
#
# Nothing is invented: every price and mechanic here comes from the shop's own
# flyers and stories, and the internal "sample / demo / pending confirmation"
# labels are gone from the storefront entirely.
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


# ======================================================================= data
i = s.index('const DEAL_GROUND =')
j = s.index('].filter(live);', s.index('const DEALCARDS = [')) + len('].filter(live);')

DATA = r'''/* ==========================================================================
   THE ADVERTISEMENTS

   Six promotions, six concepts. Each one names the products it is selling by
   brand and model, and the renderer pulls their transparent cut-outs, so the
   artwork is always the actual thing on offer.

   Every price and mechanic below is the shop's own, off their own flyers and
   stories. Nothing is invented and nothing is hedged.
   ========================================================================== */
const DEALCARDS = [
  { id:'d-offstamp', concept:'offstamp', layout:'split',
    kicker:'Off-Stamp · Crystal Cube',
    title:'Mix and match',
    offer:'2 for $10', offerSub:'or 3 for $12',
    subtitle:'Twenty-five thousand puffs a pod. Take any two flavours.',
    dealType:'bundle', discountAmount:'2 for $10', qualifyingCategory:'disp',
    qualifyingBrandIds:[], ctaLabel:'Shop Off-Stamp', ctaTarget:{view:'cat',arg:'disp'},
    badge:'', disclaimer:'21+ only. Valid ID at pickup.',
    art:[ {b:'Off-Stamp', m:'X Cube 25K', role:'lead'},
          {b:'Off-Stamp', m:'SW9000',     role:'back'} ],
    featured:true, active:true, endDate:null },

  { id:'d-tre', concept:'tre', layout:'stack',
    kicker:'TRĒ House · Exotic Snacks',
    title:'Five flavours,\nextra strength',
    offer:'$30', offerSub:'a bar',
    subtitle:'Peanut Butter, Fruity Cereal, Chocolate Crunch, Cookies & Cream, Chocolate Milk.',
    dealType:'price', discountAmount:'$30', qualifyingCategory:'exotic',
    qualifyingBrandIds:[], ctaLabel:'Shop the bars',
    ctaTarget:{view:'cat', arg:'exotic', sub:'shroom'},
    badge:'', disclaimer:'21+ only.',
    art:[ {b:'TRE House', m:'Mushroom Chocolate, Peanut Butter', role:'lead'},
          {b:'TRE House', m:'Mushroom Chocolate, Fruity Cereal', role:'back'} ],
    featured:false, active:true, endDate:null },

  { id:'d-spin', concept:'spin', layout:'split',
    kicker:'At the counter',
    title:'Spin the wheel',
    offer:'$15', offerSub:'and up',
    subtitle:'Spend fifteen or more and take a spin before you go.',
    dealType:'note', discountAmount:'$15+', art_kind:'wheel', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'', disclaimer:'In store only. One spin per visit.',
    art:[],
    featured:false, active:true, endDate:null },

  { id:'d-raffle', concept:'raffle', layout:'center',
    kicker:'Raffle',
    title:'Spend $10,\nyou are in the drawing',
    offer:'$10', offerSub:'to enter',
    subtitle:'Glass, disposables and torches come off our own shelf.',
    dealType:'note', discountAmount:'$10+', art_kind:'prize', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'', disclaimer:'Pictured items are examples of what goes on the raffle table, not a promised prize. 21+ only.',
    art:[],
    featured:false, active:true, endDate:null },

  { id:'d-glass', concept:'glass', layout:'hero',
    kicker:'Glass',
    title:'Beakers, rigs\nand spoons',
    offer:'', offerSub:'',
    subtitle:'Pulsar, GRAV, Diamond Glass and Session, on the wall behind the counter.',
    dealType:'note', discountAmount:'', qualifyingCategory:'water',
    qualifyingBrandIds:[], ctaLabel:'Shop glass', ctaTarget:{view:'cat',arg:'water'},
    badge:'', disclaimer:'',
    art:[ {b:'Pulsar', m:'Snatched Beaker Bong', role:'lead'},
          {b:'GRAV',   m:'Medium Deco Beaker',   role:'back'} ],
    featured:false, active:true, endDate:null },

  { id:'d-puffco', concept:'puffco', layout:'reverse',
    kicker:'Puffco',
    title:'Peak Pro.\nProxy. Pivot.',
    offer:'', offerSub:'',
    subtitle:'The current line, and the chambers and glass that go with it.',
    dealType:'note', discountAmount:'', qualifyingCategory:'dab',
    qualifyingBrandIds:[], ctaLabel:'Shop Puffco', ctaTarget:{view:'cat',arg:'dab'},
    badge:'', disclaimer:'',
    art:[ {b:'Puffco', m:'Peak Pro 3DXL', role:'lead'},
          {b:'Puffco', m:'Proxy',         role:'back'} ],
    featured:false, active:true, endDate:null }
].filter(live);
'''
s = s[:i] + DATA + s[j:]
print('  six advertisements written')

# ==================================================================== render
RENDER = r'''
/* ---- one advertisement ----------------------------------------------------
   The concept picks the ground and the lighting; the layout picks where the
   copy and the artwork sit. Products arrive as transparent cut-outs, so they
   stand ON the design with their own shadow instead of inside a white box. */
function adArt(d){
  if(d.art_kind === 'wheel')
    return `<div class="ad-art wheelart">
      <span class="ad-glow" aria-hidden="true"></span>
      <span class="ad-rays" aria-hidden="true"></span>
      <div class="ad-wheel">${wheelSVG()}</div></div>`;
  if(d.art_kind === 'prize')
    return `<div class="ad-art prizeart">
      <span class="ad-glow" aria-hidden="true"></span>${prizeShot()}</div>`;

  const shots = (d.art||[]).map(a=>{
    const pid = pidFor(a.b, a.m); if(!pid) return '';
    const src = cutout(pid); if(!src) return '';
    const p = P(pid);
    const alt = p ? (p.brand+' '+p.name) : (a.b+' '+a.m);
    return `<img class="ad-p ${a.role}" src="${src}" alt="${esc(alt)}"
      loading="lazy" decoding="async">`;
  }).filter(Boolean).join('');
  if(!shots) return '';
  return `<div class="ad-art">
    <span class="ad-glow" aria-hidden="true"></span>
    <span class="ad-floor" aria-hidden="true"></span>
    ${shots}</div>`;
}

function adHTML(d, i){
  const got = S.claimed.includes(d.id);
  return `<article class="ad c-${d.concept} l-${d.layout}" style="--i:${i||0}">
    <span class="ad-bg" aria-hidden="true"></span>
    ${adArt(d)}
    <div class="ad-copy">
      ${d.kicker?`<span class="ad-kick">${esc(d.kicker)}</span>`:''}
      <h3 class="ad-title">${esc(d.title).replace(/\n/g,'<br>')}</h3>
      ${d.offer?`<div class="ad-offer"><b>${esc(d.offer)}</b>${
        d.offerSub?`<i>${esc(d.offerSub)}</i>`:''}</div>`:''}
      <p class="ad-sub">${esc(d.subtitle)}</p>
      <div class="ad-acts">
        <button class="ad-cta" data-dealgo="${d.id}">${esc(d.ctaLabel)} ${ARROW}</button>
        ${d.dealType==='note'?'':`<button class="ad-save ${got?'got':''}" data-deal="${d.id}"
          aria-label="Save this offer">${got?'&#10003; Saved':'Save'}</button>`}
      </div>
      ${d.disclaimer?`<span class="ad-fine">${esc(d.disclaimer)}</span>`:''}
    </div>
  </article>`;
}
'''
i = s.index('function heroHTML(){')
s = s[:i] + RENDER + '\n' + s[i:]
print('  renderer written')

# the deals page renders advertisements
rep("""  <div class="pad" style="color:var(--muted);font-size:13px;margin:6px 0 15px;line-height:1.55">
    Sample offers and demo promotions, pending confirmation with the store.
    Save the ones you want and show this screen at the register.</div>
  <div class="pad dealstack">
    ${DEALCARDS.map((d,i)=>{""",
"""  <div class="pad sec-lead" style="margin:4px 0 16px">
    What we have going on. Save one and show this screen at the register.</div>
  <div class="pad adstack">
    ${DEALCARDS.map((d,i)=>adHTML(d,i)).join('')}
  </div>
  <div class="pad" hidden>
    ${[].map((d,i)=>{""")

# the old markup block is now dead; close it cleanly
rep("""          ${d.disclaimer?`<span class="dfine">${d.disclaimer}${d.endDate?` &middot; ends ${d.endDate}`:''}</span>`:''}
        </div></article>`}).join('')}
  </div>""",
"""          ${d.disclaimer?`<span class="dfine">${d.disclaimer}</span>`:''}
        </div></article>`}).join('')}
  </div>""")

# ---- the prize table, now that the products are cut out -------------------
rep("""function prizeItem(it){
  const src = (typeof LOCAL_PHOTOS!=='undefined') && LOCAL_PHOTOS[it.id];
  if(!src) return '';
  return `<span class="pz-i" style="left:${it.x};top:${it.y};height:${it.h};z-index:${it.z}">
    <span class="pz-sh" aria-hidden="true"></span>
    <img src="${src}" alt="${esc(it.label)}">
  </span>`;
}""",
"""function prizeItem(it){
  const src = cutout(it.id);
  if(!src) return '';
  return `<span class="pz-i" style="left:${it.x};top:${it.y};height:${it.h};z-index:${it.z}">
    <span class="pz-sh" aria-hidden="true"></span>
    <img src="${src}" alt="${esc(it.label)}">
  </span>`;
}

/* the table on its own, for an advertisement that supplies its own copy */
function prizeShot(){
  const shot = PRIZE_ITEMS.map(prizeItem).join('');
  return shot ? `<div class="pz-stage lit">${shot}</div>` : '';
}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
