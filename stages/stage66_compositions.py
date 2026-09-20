#!/usr/bin/env python3
# Stage 66 — the four weak compositions, rebuilt.
#
# 1. THE AWARD SLIDE
#    Their photograph of the plaque is 676x404. It was being stretched across a
#    716x880 slide — a 2.2x upscale — so the seal was mush and the headline sat
#    on top of the word WINNER. The award is real (Nogales International, Best
#    of Santa Cruz County 2026) so it stays; what changes is that the picture
#    is no longer asked to do a job it does not have the pixels for.
#
#    The seal is cut from their photograph at native resolution, masked to its
#    own circle, and shown at 108px — under 1:1 on a 2x screen, so it is sharp.
#    The message is set in type on a designed ground taken from the plaque's
#    own navy and gold. Nothing is enlarged and nothing is invented.
#
# 2. THE RAFFLE
#    It laid seven product photographs across the top and then said underneath
#    that they were "examples ... not a promised prize". Showing merchandise as
#    a prize and disclaiming it in the fine print is the worst of both. Nobody
#    has confirmed what goes on the table, so the card is text-led: what it
#    costs to enter, what you get, where it happens. No photographs, no hedge.
#
# 3. TRE HOUSE
#    The bar was pinned to the bottom edge of the card and cropped by it — the
#    peanut butter ran off the right, the packaging off the bottom. It becomes
#    the ground of the card, which is what a lifestyle photograph is for, with
#    the copy on a scrim above it.
#
# 4. GLASS
#    Two tall bongs and a headline occupying the same space; "Beakers, rigs and
#    spoons" was reading through a beaker. The art keeps the top right, the
#    copy keeps the bottom left, and they no longer meet.
import io
import os

P = '/root/work/smokers-paradise-demo/build/index.html'
SEAL = '/root/work/assets/seal_b64.txt'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))


# ============================================================== 1. the seal
seal = io.open(SEAL, encoding='utf-8').read().strip()
print('  seal %.0f KB' % (len(seal) / 1024))

rep("""const CERT_PHOTO = ""","""/* The seal, cut from their own photograph of the plaque at native resolution
   and masked to its circle. Shown at 108px, which is under 1:1 on a 2x screen,
   so it stays sharp — unlike the full plaque, which was being stretched 2.2x
   across the slide. Nothing about the award itself is altered. */
const AWARD_SEAL = "%s";
const CERT_PHOTO = """ % seal)

rep("""  { id:'p-award', kind:'editor',
    kicker:'Santa Cruz County',
    headline:'Best Smoke\\nShop 2026.',
    sub:'Thank you, Nogales.',
    offer:'', offer2:'',
    cta:'Our store', target:{view:'store'},
    disclaimer:'',
    mark:false,
    photo:()=>CERT_PHOTO, photoAlt:'Best of Santa Cruz County 2026, Winner, Best Smoke Shop',
    active:true, startDate:null, endDate:null }""",
"""  { id:'p-award', kind:'award',
    kicker:'Nogales International',
    headline:'Best Smoke Shop 2026',
    sub:'Voted Best of Santa Cruz County.',
    offer:'', offer2:'',
    cta:'Our store', target:{view:'store'},
    disclaimer:'',
    mark:false,
    seal:()=>AWARD_SEAL, sealAlt:'Best of Santa Cruz County 2026 seal, Nogales International',
    active:true, startDate:null, endDate:null }""")

rep("""function campHTML(c, attr){
  const light = c.kind !== 'editor';
  return `<button class="camp ${c.kind} ${light?'light':'dark'}" ${attr}
      style="${light?fieldCSS(c.field):''}" aria-label="${esc(c.headline.replace(/\\n/g,' '))}">
    ${light ? `<span class="camp-field" aria-hidden="true"></span>
               <span class="camp-block" aria-hidden="true"></span>` : campPhoto(c)}
    ${light ? campShot(c) : ''}
    ${campCopy(c)}
    ${c.mark && !light ? `<span class="camp-mark">${markImg('cmark'+c.id)}</span>` : ''}
    ${light ? `<span class="camp-sig" aria-hidden="true">Smokers Paradise</span>` : ''}
  </button>`;
}""",
"""/* A campaign whose subject is the award itself. Not a product composition and
   not a photograph stretched to fill: the seal at a size it is actually sharp
   at, and the claim set in type on a ground drawn from the plaque's own navy
   and gold. */
function awardHTML(c, attr){
  const src = typeof c.seal === 'function' ? c.seal() : c.seal;
  return `<button class="camp award" ${attr}
      aria-label="${esc(c.headline)} ${esc(c.sub||'')}">
    <span class="aw-bloom" aria-hidden="true"></span>
    <span class="aw-rule" aria-hidden="true"></span>
    ${src?`<img class="aw-seal" src="${src}" alt="${esc(c.sealAlt||'')}"
      decoding="async" onerror="this.style.display='none'">`:''}
    <span class="aw-kick">${esc(c.kicker)}</span>
    <h2 class="aw-head">${esc(c.headline)}</h2>
    ${c.sub?`<p class="aw-sub">${esc(c.sub)}</p>`:''}
    <span class="camp-cta">${esc(c.cta)} ${ARROW}</span>
  </button>`;
}

function campHTML(c, attr){
  if(c.kind === 'award') return awardHTML(c, attr);
  const light = c.kind !== 'editor';
  return `<button class="camp ${c.kind} ${light?'light':'dark'}" ${attr}
      style="${light?fieldCSS(c.field):''}" aria-label="${esc(c.headline.replace(/\\n/g,' '))}">
    ${light ? `<span class="camp-field" aria-hidden="true"></span>
               <span class="camp-block" aria-hidden="true"></span>` : campPhoto(c)}
    ${light ? campShot(c) : ''}
    ${campCopy(c)}
    ${c.mark && !light ? `<span class="camp-mark">${markImg('cmark'+c.id)}</span>` : ''}
    ${light ? `<span class="camp-sig" aria-hidden="true">Smokers Paradise</span>` : ''}
  </button>`;
}""")

# ============================================================= 2. the raffle
rep("""  { id:'d-raffle', concept:'raffle', layout:'center',
    kicker:'Raffle',
    title:'Spend $10+\\nfor a raffle entry',
    offer:'$10', offerSub:'to enter',
    subtitle:'Glass, disposables and torches come off our own shelf.',
    dealType:'note', discountAmount:'$10+', art_kind:'prize', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'', disclaimer:'Pictured items are examples of what goes on the raffle table, not a promised prize. 21+ only.',
    art:[],
    featured:false, active:true, endDate:null },""",
"""  /* Text-led on purpose. Nobody has confirmed which items go on the raffle
     table, and putting seven packshots on the card and calling them
     "examples" underneath shows a prize and takes it back in the same breath.
     The mechanic is the message. */
  { id:'d-raffle', concept:'raffle', layout:'ticket',
    kicker:'Raffle',
    title:'Spend $10+\\nfor a raffle entry',
    offer:'$10', offerSub:'to enter',
    subtitle:'One entry per visit. Ask at the counter and we\\u2019ll write your name on the ticket.',
    dealType:'note', discountAmount:'$10+', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'', disclaimer:'In store only. 21+ only.',
    art:[],
    featured:false, active:true, endDate:null },""")

# ============================================================ 3. TRE and glass
rep("""  { id:'d-tre', concept:'tre', layout:'stack',""",
    """  { id:'d-tre', concept:'tre', layout:'photo',""")

rep("""    subtitle:'Peanut Butter, Fruity Cereal, Chocolate Crunch, Cookies & Cream, Chocolate Milk.',""",
    """    subtitle:'Peanut Butter, Fruity Cereal, Chocolate Crunch, Cookies & Cream and Chocolate Milk.',""")
rep("""    offer:'$30', offerSub:'a bar',""", """    offer:'$30', offerSub:'each',""")
rep("""    offer:'$15', offerSub:'and up',""", """    offer:'$15', offerSub:'or more',""")
rep("""    subtitle:'Spend fifteen or more and take a spin before you go.',""",
    """    subtitle:'Spend $15 or more and spin the prize wheel at the counter.',""")

CSS = r'''
/* ==========================================================================
   THE AWARD
   Their plaque photograph is 676x404. It was being stretched across the whole
   slide, which is a 2.2x upscale, and the headline was landing on the word
   WINNER. The seal is cut from that same photograph at native size and shown
   at 108px — under 1:1 on a 2x screen — on a ground taken from the plaque's
   own navy and gold. Sharp, and nothing is invented.
   ========================================================================== */
.camp.award{
  position:relative;overflow:hidden;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:0;text-align:center;
  padding:34px 26px 30px;
  min-height:100%;
  border:0;
  background:
    radial-gradient(120% 80% at 50% 6%, #1E2A4E 0%, #141C34 42%, #0B0E1C 100%);
}
.camp.award .aw-bloom{
  position:absolute;left:50%;top:-6%;width:120%;aspect-ratio:1/1;
  transform:translateX(-50%);pointer-events:none;border-radius:50%;
  background:radial-gradient(circle, rgba(226,178,92,.20) 0%, transparent 62%);
}
.aw-seal{
  position:relative;z-index:2;
  width:108px;height:108px;
  filter:drop-shadow(0 10px 20px rgba(0,0,0,.55));
  margin-bottom:16px;
}
.camp.award .aw-kick{
  position:relative;z-index:2;
  font-family:var(--mono);font-size:9.5px;letter-spacing:.20em;
  text-transform:uppercase;color:#E2B25C;
}
.camp.award .aw-head{
  position:relative;z-index:2;
  font-family:var(--disp);font-weight:800;
  font-size:30px;line-height:1.08;letter-spacing:-.03em;
  color:#FFFFFF;margin:9px 0 0;text-transform:none;
}
.camp.award .aw-sub{
  position:relative;z-index:2;
  font-family:var(--body-f);font-size:14px;line-height:1.5;
  color:#D9CDBA;margin:9px 0 0;max-width:24ch;
}
.camp.award .aw-rule{
  position:relative;z-index:2;display:block;
  width:54px;height:2px;margin:18px 0 16px;border-radius:2px;
  background:linear-gradient(90deg,transparent,#E2B25C,transparent);
  order:9;
}
.camp.award .camp-cta{
  position:relative;z-index:2;order:10;margin:16px 0 0;
  background:#E2B25C;color:#20160A;box-shadow:none;
}

/* ==========================================================================
   THE RAFFLE, TEXT LED
   No product photograph on this card. The entry mechanic is the whole
   message, so it is set as one.
   ========================================================================== */
.ad.c-raffle,.ad.l-ticket{
  background:radial-gradient(120% 90% at 50% 0%, #3D0B33 0%, #260722 48%, #14040F 100%);
}
.ad.l-ticket{display:block;min-height:0;padding:0}
.ad.l-ticket .ad-art,.ad.c-raffle .ad-art,.ad.c-raffle .prizeart,
.ad.c-raffle .pz-stage{display:none}
.ad.l-ticket .ad-copy{
  position:relative;z-index:2;
  padding:32px 22px 28px;
  display:flex;flex-direction:column;align-items:flex-start;
}
.ad.l-ticket .ad-offer{margin:12px 0 0}
.ad.l-ticket .ad-offer b{font-size:52px;line-height:1}
/* a perforated edge, drawn — the card IS a ticket, so it may look like one */
.ad.l-ticket::before,.ad.l-ticket::after{
  content:"";position:absolute;left:0;right:0;height:12px;pointer-events:none;
  background-image:radial-gradient(circle at 8px 6px, rgba(0,0,0,.55) 5px, transparent 5.5px);
  background-size:20px 12px;
}
.ad.l-ticket::before{top:-6px}
.ad.l-ticket::after{bottom:-6px}

/* ==========================================================================
   TRE HOUSE
   The bar was anchored to the bottom edge and cropped by it. The photograph
   is the ground now, which is what a lifestyle shot is for, and the copy sits
   on a scrim over it.
   ========================================================================== */
.ad.c-tre.l-photo .ad-photo{object-position:center 58%}
.ad.c-tre.l-photo .ad-copy{
  background:linear-gradient(to top,
    rgba(24,12,4,.94) 0%, rgba(24,12,4,.88) 42%,
    rgba(24,12,4,.45) 72%, rgba(24,12,4,0) 100%);
  padding:96px 20px 22px;
}
.ad.c-tre .ad-sub{
  display:block;-webkit-line-clamp:none;overflow:visible;
  color:#F0E3D2;
}

/* ==========================================================================
   GLASS
   Two tall pieces and a headline were sharing the same space. The art keeps
   the top right, the copy keeps the bottom left.
   ========================================================================== */
.ad.c-glass.l-hero .ad-p.lead{left:70%;top:2%;max-height:56%;max-width:44%}
.ad.c-glass.l-hero .ad-p.back{left:34%;top:8%;max-height:44%;max-width:32%}
.ad.c-glass.l-hero .ad-copy{
  background:linear-gradient(to top,
    rgba(4,10,14,.95) 0%, rgba(4,10,14,.9) 46%,
    rgba(4,10,14,.42) 74%, rgba(4,10,14,0) 100%);
  padding:110px 20px 22px;
}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  composition styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
