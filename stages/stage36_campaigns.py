#!/usr/bin/env python3
# Stage 36 — the campaign system. Art direction, not another card.
#
# WHAT WAS WRONG
# The banners were a card with a coloured rectangle behind it, a product
# floating in the middle of a white plate, and a headline beside it. Three
# banners, one layout, one purple, product pasted on. That is a template, not
# a campaign, and it is why the app read as generated rather than designed.
#
# WHAT A REAL RETAIL CAMPAIGN DOES
#   - the ground is built from the PRODUCT's packaging, not from one house
#     purple repeated forever
#   - the ground is LIGHT where the product stands, so a manufacturer packshot
#     printed on white has nothing to sit on: no plate, no edge, no halo. The
#     colour arrives away from the product, which is also how a photographer
#     lights a still life
#   - the product is BIG and CROPPED by the frame. Cropping is what says a
#     photograph continues past the edge; a product centred inside a box says
#     it was dropped in
#   - it stands on a contact shadow on the ground plane, not inside a glow
#   - a second product OVERLAPS it, smaller and set back, which is depth
#   - the offer has a hierarchy: kicker, headline, the number, one CTA
#   - the shop's own mark signs it
#
# DIFFERENT CONTENT, DIFFERENT LAYOUT
#   .camp.lead    a full-width product campaign
#   .camp.tall    the same language at half width, vertical
#   .camp.editor  no product at all: real photography, dark, editorial. Used
#                 for the award and for order-ahead, so the pair reads as two
#                 coordinated pieces rather than the same tile twice.
#
# COLOUR SOURCES (packaging, named, not invented)
#   Off-Stamp Crystal Cube   iced translucent blue      their 10 Jul flyer
#   Lost Mary NERA           soft coral / peach         their 16 Jul post
#   Geek Bar Pulse X 25K     violet  (catalogue c1 #7C4DFF)
#   TRE House                cream / gold / cacao (catalogue c1 #B4762E)
#
# Nothing here claims stock. Every offer keeps its sample/demo label.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ==========================================================================
# 1. THE CAMPAIGNS
# ==========================================================================
i = s.index('const GROUND =')
j = s.index("].filter(Boolean);", s.index('const PROMO_PAIR')) + len("].filter(Boolean);")

CAMPAIGNS = r'''/* ==========================================================================
   CAMPAIGNS
   A campaign is a composition, not a card. Each one carries its own field,
   built from the packaging of the product it features, and its own crop.
   ========================================================================== */

/* A field is three stops and an accent. White where the product stands, so a
   packshot printed on white has no edge; the colour arrives at the far corner.
   `block` is the soft colour shape the product overlaps, which is what gives
   the composition depth without a decorative doodad. */
const CAMP_FIELDS = {  /* FIELDS is taken further down the file */
  /* Off-Stamp Crystal Cube: iced translucent blue, off their July flyer */
  ice:   {f0:'#FFFFFF', f1:'#E9F3FA', f2:'#C4DCEE', acc:'#1C6FA8', ink:'#0E2434', block:'#7FB6DA'},
  /* Lost Mary NERA: soft coral and peach, off their July post */
  coral: {f0:'#FFFFFF', f1:'#FFF1E9', f2:'#F7D3BE', acc:'#C9502A', ink:'#361409', block:'#F0A382'},
  /* Geek Bar Pulse X 25K: violet, the catalogue's own c1 */
  violet:{f0:'#FFFFFF', f1:'#F2EDFF', f2:'#D9CDFA', acc:'#5B2FD0', ink:'#190A33', block:'#A88BF2'},
  /* TRE House: cream, gold and cacao, the catalogue's own c1/c2 */
  cacao: {f0:'#FFFFFF', f1:'#FFF7E9', f2:'#F0D9AC', acc:'#8A5418', ink:'#2B1A06', block:'#D9A75B'}
};
const fieldCSS = k => {
  const f = CAMP_FIELDS[k] || CAMP_FIELDS.violet;
  return `--f0:${f.f0};--f1:${f.f1};--f2:${f.f2};--acc:${f.acc};--cink:${f.ink};--blk:${f.block}`;
};

/* ---- the featured campaigns, one at a time in the carousel ---- */
const PROMOS = [
  { id:'p-offstamp', kind:'lead', field:'ice',
    kicker:'Sample offer',
    headline:'Crystal Cube,\nstacked.',
    sub:'Twenty-five thousand puffs a pod, and the flavours mix however you like.',
    offer:'2 for $10',
    offer2:'or 3 for $12',
    cta:'Browse pods', target:{view:'cat', arg:'disp'},
    disclaimer:'Sample offer taken from Smokers Paradise content. Pending store confirmation. 21+ only.',
    mark:true,
    shot:{ hero:()=>heroShot('Off-Stamp','X Cube 25K'),  heroAlt:'Off-Stamp X Cube 25K',
           back:()=>heroShot('Off-Stamp','SW9000'),      backAlt:'Off-Stamp SW9000' },
    active:true, startDate:null, endDate:null },

  { id:'p-lostmary', kind:'lead', field:'coral',
    kicker:'Demo selection',
    headline:'Lost Mary,\nnew flavours.',
    sub:'Pineapple Coconut, Polar Mint, Strawberry Watermelon and the rest of the NERA run.',
    offer:'', offer2:'',
    cta:'See the flavours', target:{view:'cat', arg:'disp'},
    disclaimer:'Demo selection. Flavours and pricing are confirmed with the store.',
    mark:false,
    shot:{ hero:()=>heroShot('Lost Mary','MT35000 Turbo'), heroAlt:'Lost Mary MT35000 Turbo',
           back:()=>heroShot('Lost Mary','MO20000 Pro'),   backAlt:'Lost Mary MO20000 Pro' },
    active:true, startDate:null, endDate:null },

  { id:'p-geek', kind:'lead', field:'violet',
    kicker:'Demo selection',
    headline:'Pulse X.\nTwenty-five thousand.',
    sub:'Dual mesh, a screen, and a charge that outlasts the weekend.',
    offer:'', offer2:'',
    cta:'Browse new vapes', target:{view:'cat', arg:'disp'},
    disclaimer:'Demo selection. Selection and pricing are confirmed with the store.',
    mark:false,
    shot:{ hero:()=>heroShot('Geek Bar','Pulse X 25K'), heroAlt:'Geek Bar Pulse X 25K',
           back:()=>heroShot('Geek Bar','Pulse X2 50K'), backAlt:'Geek Bar Pulse X2 50K' },
    active:true, startDate:null, endDate:null },

  /* Not a product campaign, and it should not look like one. Their own
     photograph of their own plaque, treated as editorial. */
  { id:'p-award', kind:'editor',
    kicker:'Santa Cruz County',
    headline:'Best Smoke\nShop 2026.',
    sub:'Thank you, Nogales.',
    offer:'', offer2:'',
    cta:'Our store', target:{view:'store'},
    disclaimer:'',
    mark:false,
    photo:()=>CERT_PHOTO, photoAlt:'Best of Santa Cruz County 2026, Winner, Best Smoke Shop',
    active:true, startDate:null, endDate:null }
].filter(live);

/* ---- the pair, directly beneath ----
   Two coordinated pieces, deliberately NOT the same object twice: one is a
   product campaign at half width, the other is the shop itself, photographed.
   Below 480px they stack, because two columns of this copy is unreadable. */
const PROMO_PAIR = [
  { id:'pp-tre', kind:'tall', field:'cacao',
    kicker:'Exotic Snacks',
    headline:'Five flavours\nof chocolate.',
    sub:'TRĒ House bars, in the Exotic Snacks shelf.',
    offer:'$30', offer2:'a bar',
    cta:'Browse the shelf', act:{view:'cat', arg:'exotic', sub:'shroom'},
    shot:{ hero:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter'),
           heroAlt:'TRĒ House mushroom chocolate bar, peanut butter',
           back:()=>heroShot('TRE House','Mushroom Chocolate, Fruity Cereal'),
           backAlt:'TRĒ House mushroom chocolate bar, fruity cereal' },
    disclaimer:'21+ only.' },

  { id:'pp-order', kind:'editor',
    kicker:'Pickup on North Grand',
    headline:'Order ahead.',
    sub:'Build the bag here, collect it at the counter.',
    offer:'', offer2:'',
    cta:'Start an order', act:{view:'all'},
    photo:()=>FRONT_PHOTO, photoAlt:'Smokers Paradise on North Grand Avenue',
    mark:true,
    disclaimer:'' }
].filter(Boolean);
'''
s = s[:i] + CAMPAIGNS + s[j:]
print('  campaigns written')

# ==========================================================================
# 2. THE RENDERER
# ==========================================================================
i = s.index('/* The pair, built from')
j = s.index('function heroTo(i){')

RENDER = r'''/* ---- one campaign, in whichever of the three shapes it asked for ---- */
function campShot(c){
  const sh = c.shot || {};
  const a = typeof sh.hero === 'function' ? sh.hero() : sh.hero;
  const b = typeof sh.back === 'function' ? sh.back() : sh.back;
  if(!a && !b) return '';
  return `<div class="camp-shot">
    <span class="camp-ground" aria-hidden="true"></span>
    ${b?`<img class="camp-back" src="${b}" alt="${esc(sh.backAlt||'')}" loading="lazy"
        decoding="async" referrerpolicy="no-referrer"
        onerror="this.style.display='none'">`:''}
    ${a?`<img class="camp-lead" src="${a}" alt="${esc(sh.heroAlt||'')}" loading="lazy"
        decoding="async" referrerpolicy="no-referrer"
        onerror="this.closest('.camp-shot').style.display='none'">`:''}
  </div>`;
}

function campPhoto(c){
  const src = typeof c.photo === 'function' ? c.photo() : c.photo;
  if(!src) return '';
  return `<div class="camp-photo"><img src="${src}" alt="${esc(c.photoAlt||'')}"
    loading="lazy" decoding="async" onerror="this.closest('.camp-photo').remove()"></div>`;
}

function campCopy(c){
  return `<div class="camp-copy">
    <span class="camp-kick">${esc(c.kicker)}</span>
    <h2 class="camp-head">${esc(c.headline).replace(/\n/g,'<br>')}</h2>
    ${c.offer?`<div class="camp-offer"><b>${esc(c.offer)}</b>${
      c.offer2?`<i>${esc(c.offer2)}</i>`:''}</div>`:''}
    ${c.sub?`<p class="camp-sub">${esc(c.sub)}</p>`:''}
    <span class="camp-cta">${esc(c.cta)} ${ARROW}</span>
  </div>`;
}

function campHTML(c, attr){
  const light = c.kind !== 'editor';
  return `<button class="camp ${c.kind} ${light?'light':'dark'}" ${attr}
      style="${light?fieldCSS(c.field):''}" aria-label="${esc(c.headline.replace(/\n/g,' '))}">
    ${light ? `<span class="camp-field" aria-hidden="true"></span>
               <span class="camp-block" aria-hidden="true"></span>` : campPhoto(c)}
    ${light ? campShot(c) : ''}
    ${campCopy(c)}
    ${c.mark?`<span class="camp-mark">${markImg('cmark'+c.id)}</span>`:''}
    ${c.disclaimer?`<span class="camp-fine">${esc(c.disclaimer)}</span>`:''}
  </button>`;
}

/* The pair. Same design language, deliberately different shapes. */
function pairHTML(){
  if(!PROMO_PAIR.length) return '';
  return `<div class="bpair">${PROMO_PAIR.map(c =>
    campHTML(c, `data-pair="${c.id}"`)).join('')}</div>`;
}

function heroHTML(){
  if(!PROMOS.length) return '';
  return `<div class="promoc" id="hero">
    <div class="vp" id="heroVp">${PROMOS.map(p =>
      `<div class="slide">${campHTML(p, `data-promo="${p.id}"`)}</div>`).join('')}</div>
    ${PROMOS.length>1?`
      <button class="arw l" data-hero="-1" aria-label="Previous offer">${CHEV_L}</button>
      <button class="arw r" data-hero="1" aria-label="Next offer">${CHEV_R}</button>
      <div class="dots" id="heroDots">${PROMOS.map((p,i)=>
        `<button class="${i?'':'on'}" data-herogo="${i}" aria-label="Offer ${i+1}: ${
          p.headline.replace(/\n/g,' ').replace(/"/g,'')}"></button>`).join('')}</div>`:''}
  </div>`;
}
'''
s = s[:i] + RENDER + s[j:]
print('  renderer written')

# the pair's click handler now carries a target object
rep("""    const p = PROMO_PAIR.find(x=>x.id===bp.dataset.pair);
    if(p){ p.act==='ff' ? (typeof openFF==='function'?openFF():go('all')) : go(p.act) }
    return;""",
"""    const p = PROMO_PAIR.find(x=>x.id===bp.dataset.pair);
    if(p) goTarget(p.act);
    return;""")

# ==========================================================================
# 3. THE STYLE
# ==========================================================================
CSS = r'''
/* ==========================================================================
   THE CAMPAIGN SYSTEM

   Three shapes, one language.

     .camp.lead    full width, product cropped by the right edge
     .camp.tall    half width, product cropped by the bottom edge
     .camp.editor  no product: a real photograph, dark, editorial

   The light campaigns put white under the product and the packaging colour
   away from it, which is why there is no plate, no edge and no halo: a
   manufacturer packshot printed on white has nothing to sit on.
   ========================================================================== */

.camp{position:relative;display:block;width:100%;text-align:left;border:0;padding:0;
  border-radius:var(--r-card);overflow:hidden;isolation:isolate;
  box-shadow:var(--sh-1);cursor:pointer}
.camp:active{transform:scale(.995)}

/* ---- the ground ---- */
.camp.light{background:var(--f0)}
.camp-field{position:absolute;inset:0;z-index:0;
  background:linear-gradient(158deg,
    var(--f0) 0%, var(--f0) 34%, var(--f1) 68%, var(--f2) 100%)}
/* The one shape in the composition. The product overlaps it, which is what
   reads as depth; on its own it is just a colour field, not a decoration. */
.camp-block{position:absolute;z-index:1;pointer-events:none;
  background:var(--blk);opacity:.20;filter:blur(0.5px)}

/* ---- the product ---- */
.camp-shot{position:absolute;z-index:2;pointer-events:none}
.camp-shot img{position:absolute;display:block;object-fit:contain;
  width:auto;height:auto;max-width:100%;max-height:100%}
/* the contact shadow: on the ground under the product, never behind it */
.camp-ground{position:absolute;left:50%;transform:translateX(-50%);
  border-radius:50%;filter:blur(7px);
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(20,8,30,.34) 0%, rgba(20,8,30,.16) 52%, rgba(20,8,30,0) 100%)}
.camp-lead{filter:drop-shadow(0 14px 20px rgba(20,8,30,.20))}
.camp-back{filter:drop-shadow(0 10px 16px rgba(20,8,30,.16));opacity:.92}

/* ---- the copy ---- */
.camp-copy{position:relative;z-index:4;display:flex;flex-direction:column;
  align-items:flex-start}
.camp-kick{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;line-height:1;color:var(--acc)}
.camp-head{font-family:var(--disp);font-weight:800;letter-spacing:-.045em;
  line-height:.94;margin:11px 0 0;color:var(--cink);text-wrap:balance}
.camp-offer{display:flex;align-items:baseline;gap:7px;margin:12px 0 0}
.camp-offer b{font-family:var(--block);font-weight:400;letter-spacing:-.01em;
  color:var(--cink);line-height:1}
.camp-offer i{font-family:var(--mono);font-style:normal;font-size:10.5px;
  letter-spacing:.06em;text-transform:uppercase;color:var(--acc)}
.camp-sub{font-size:12.5px;line-height:1.4;margin:10px 0 0;color:var(--cink);
  opacity:.72;max-width:27ch}
.camp-cta{margin-top:16px;display:inline-flex;align-items:center;gap:7px;
  background:var(--go);color:#2A0016;border-radius:var(--r-chip);
  padding:10px 17px;box-shadow:var(--sh-2);
  font-family:var(--block);text-transform:uppercase;letter-spacing:.045em;
  font-size:11px;line-height:1}
.camp-cta svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.camp-fine{position:absolute;z-index:4;left:var(--cx);right:var(--cx);bottom:9px;
  font-size:8.5px;line-height:1.3;color:var(--cink);opacity:.5}
.camp-mark{position:absolute;z-index:5;pointer-events:none}
.camp-mark .hcm{width:100%}

/* ==================== .camp.lead — the full-width campaign ================ */
.camp.lead{--cx:20px;min-height:330px}
.camp.lead .camp-copy{padding:22px var(--cx) 0;max-width:62%}
.camp.lead .camp-head{font-size:clamp(27px,8.2vw,40px)}
.camp.lead .camp-offer b{font-size:34px}
.camp.lead .camp-block{width:96%;height:58%;right:-30%;bottom:-16%;
  border-radius:50% 46% 52% 48%/48% 52% 48% 52%}
.camp.lead .camp-shot{right:-6%;bottom:0;width:62%;height:74%}
/* the lead product is taller than its box, so the frame crops its base */
.camp.lead .camp-lead{right:2%;bottom:-7%;height:104%}
.camp.lead .camp-back{right:44%;bottom:2%;height:74%}
.camp.lead .camp-ground{bottom:2%;width:58%;height:16px}
.camp.lead .camp-mark{left:var(--cx);bottom:24px;width:60px}
.camp.lead .camp-fine{right:42%}

@media (min-width:620px){
  .camp.lead{--cx:34px;min-height:340px}
  .camp.lead .camp-copy{padding:34px var(--cx) 0;max-width:46%}
  .camp.lead .camp-head{font-size:42px}
  .camp.lead .camp-offer b{font-size:42px}
  .camp.lead .camp-shot{right:0;bottom:0;width:52%;height:88%}
  .camp.lead .camp-lead{right:4%;bottom:-5%;height:100%}
  .camp.lead .camp-back{right:46%;bottom:4%;height:70%}
  .camp.lead .camp-ground{bottom:4%;width:52%;height:20px}
  .camp.lead .camp-block{width:64%;height:120%;right:-14%;bottom:-30%}
  .camp.lead .camp-fine{right:auto;left:var(--cx);max-width:44%}
}

/* ==================== .camp.tall — the same at half width ================= */
.camp.tall{--cx:16px;min-height:300px}
.camp.tall .camp-copy{padding:18px var(--cx) 0;max-width:100%}
.camp.tall .camp-head{font-size:22px}
.camp.tall .camp-offer b{font-size:26px}
.camp.tall .camp-sub{font-size:11.5px;max-width:22ch}
.camp.tall .camp-block{width:150%;height:52%;left:-25%;bottom:-18%;
  border-radius:50%}
.camp.tall .camp-shot{left:0;right:0;bottom:0;height:44%}
.camp.tall .camp-lead{left:52%;bottom:-8%;height:112%;transform:translateX(-50%)}
.camp.tall .camp-back{left:16%;bottom:-2%;height:82%}
.camp.tall .camp-ground{bottom:3%;width:64%;height:14px}
.camp.tall .camp-fine{bottom:7px}

/* ==================== .camp.editor — photography, not product ============= */
.camp.dark{--cx:18px;background:#150A20;min-height:300px;
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,123,200,.16)}
.camp.dark .camp-photo{position:absolute;inset:0;z-index:0}
.camp.dark .camp-photo img{width:100%;height:100%;object-fit:cover;
  object-position:center 42%}
/* One gradient, weighted to the copy side, so the photograph stays a
   photograph instead of disappearing under a flat black scrim. */
.camp.dark .camp-photo::after{content:"";position:absolute;inset:0;
  background:linear-gradient(4deg,
    rgba(12,4,20,.94) 0%, rgba(12,4,20,.72) 38%,
    rgba(12,4,20,.30) 66%, rgba(12,4,20,.10) 100%)}
.camp.dark .camp-copy{position:absolute;left:0;right:0;bottom:0;
  padding:0 var(--cx) 18px}
.camp.dark .camp-kick{color:var(--go-ink)}
.camp.dark .camp-head{color:#FFF;font-size:26px}
.camp.dark .camp-sub{color:#F3E9F6;opacity:.86;font-size:11.5px;max-width:24ch}
.camp.dark .camp-mark{right:var(--cx);top:16px;width:56px}
.camp.dark .camp-fine{color:#F3E9F6}

/* the award, in the carousel, gets the full width and a taller crop */
.camp.editor.dark{min-height:330px}
#hero .camp.dark .camp-head{font-size:clamp(28px,8.6vw,40px)}
@media (min-width:620px){
  #hero .camp.dark{min-height:340px}
  #hero .camp.dark .camp-photo img{object-position:center 38%}
  #hero .camp.dark .camp-copy{max-width:58%}
  #hero .camp.dark .camp-head{font-size:42px}
}

/* ==================== the carousel shell ================================= */
/* The slide is now only a track cell; the campaign inside it owns everything
   visual, so the old slide chrome is gone. */
#hero .slide{flex:0 0 100%;min-width:100%;padding:0;background:none;border:0;
  box-shadow:none;border-radius:0;min-height:0;display:block}
.promoc{border-radius:var(--r-card);overflow:visible;box-shadow:none;
  margin:0 var(--sp-edge);position:relative}
.promoc .vp{border-radius:var(--r-card);overflow:hidden}
.bpair{display:grid;grid-template-columns:1fr 1fr;gap:11px;
  margin:11px var(--sp-edge) 0}
@media (max-width:480px){.bpair{grid-template-columns:1fr}}

/* arrows and dots sit over the composition, out of the copy's way */
#hero .arw{z-index:6}
#hero .dots{z-index:6}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  campaign css appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
