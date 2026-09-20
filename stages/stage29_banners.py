#!/usr/bin/env python3
# Stage 29 — one banner system.
#
# Structure, not colour experiments. A featured banner, and directly under it
# a coordinated pair. Every banner in the system shares one radius, one border,
# one inset, one eyebrow, one headline scale, one CTA and one image stage, and
# the pair stacks on a narrow screen rather than squeezing the copy.
#
# The palette is fixed: plum ground, magenta accent. Slides carry a photograph
# or a product line-up, never a different colour idea.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))

# ---------------------------------------------------------------- content
# One palette. The only thing that changes between banners is what is on them.
GROUND = 'linear-gradient(118deg,#1B0A26 0%,#330F33 52%,#4A1038 100%)'

NEW_PROMOS = '''/* ---- the featured banner ----
   One at a time, in the carousel. Same ground, same inset, same type scale as
   the pair beneath it, so the three read as one campaign rather than three
   experiments. */
const PROMOS = [
  { id:'p-new', eyebrow:'Demo selection', headline:'See what\\u2019s new',
    sub:'New-generation disposables from Geek Bar, Lost Mary, RAZ and Off-Stamp.',
    cta:'Browse new vapes', target:{view:'cat', arg:'disp'},
    disclaimer:'Demo selection. Selection and pricing are confirmed with the store.',
    theme:{bg:GROUND, ink:'#FFFFFF', accent:'#FF2FA8'},
    mark:true,
    media:{kind:'product', items:[
      {src:()=>heroShot('Geek Bar','Pulse X 25K'),  alt:'Geek Bar Pulse X 25K',  tilt:-4, z:3, scale:1},
      {src:()=>heroShot('Lost Mary','MT35000 Turbo'),alt:'Lost Mary MT35000 Turbo',tilt:3,  z:2, scale:.96},
      {src:()=>heroShot('RAZ','DC25000'),           alt:'RAZ DC25000',           tilt:-1, z:1, scale:.92}
    ]},
    startDate:null, endDate:null, active:true },

  { id:'p-award', eyebrow:'Santa Cruz County', headline:'Best Smoke Shop 2026',
    sub:'Thank you, Nogales.',
    cta:'Our store', target:{view:'store'},
    disclaimer:'',
    theme:{bg:GROUND, ink:'#FFFFFF', accent:'#FF2FA8'},
    media:{kind:'photo', src:()=>CERT_PHOTO, alt:'Best of Santa Cruz County 2026, Winner, Best Smoke Shop'},
    startDate:null, endDate:null, active:true },

  { id:'p-offstamp', eyebrow:'Sample offer',
    headline:'Off-Stamp pods, 2 for $10',
    sub:'Or 3 for $12. Seen in Smokers Paradise content.',
    cta:'Browse pods', target:{view:'cat', arg:'disp'},
    disclaimer:'Sample offer. Pending store confirmation. 21+ only.',
    theme:{bg:GROUND, ink:'#FFFFFF', accent:'#FF2FA8'},
    media:{kind:'product', items:[
      {src:()=>heroShot('Off-Stamp','X Cube 25K'), alt:'Off-Stamp X Cube 25K', tilt:-4, z:2, scale:1},
      {src:()=>heroShot('Off-Stamp','SW9000'),     alt:'Off-Stamp SW9000',     tilt:3,  z:1, scale:.94}
    ]},
    startDate:null, endDate:null, active:true }
].filter(live);

/* ---- the pair ----
   Directly under the featured banner, two smaller banners built from the same
   parts. They are not a second design; they are the same banner at half width.
   Below 430px they stack, because two columns of this copy is unreadable. */
const PROMO_PAIR = [
  { id:'pp-flavor', eyebrow:'Demo selection', headline:'Find your next flavor',
    sub:'Three questions, and the shelf narrows to what suits you.',
    cta:'Find Your Fit', act:'ff',
    media:{kind:'product', items:[
      {src:()=>heroShot('Geek Bar','Pulse 15K'),   alt:'Geek Bar Pulse 15K',  tilt:-5, z:2, scale:1},
      {src:()=>heroShot('Lost Mary','MO20000 Pro'),alt:'Lost Mary MO20000 Pro',tilt:4, z:1, scale:.92}
    ]}},
  { id:'pp-order', eyebrow:'Pickup', headline:'Order ahead.\\nPick up in store.',
    sub:'Save what you want and collect it at the counter on North Grand.',
    cta:'Start an order', act:'all',
    media:{kind:'mark'}}
].filter(Boolean);
'''

i = s.index('const PROMOS = [')
j = s.index("].filter(live);", i) + len("].filter(live);")
s = s[:i] + "const GROUND = '%s';\n\n" % GROUND + NEW_PROMOS + s[j:]
print('  PROMOS + PROMO_PAIR written')

# ---------------------------------------------------------------- markup
rep("""function heroHTML(){
  if(!PROMOS.length) return '';
  return `<div class="promoc" id="hero">""",
"""/* The pair, built from the featured banner's own parts. */
function pairHTML(){
  if(!PROMO_PAIR.length) return '';
  return `<div class="bpair">${PROMO_PAIR.map(p=>`
    <button class="bnr sm" data-pair="${p.id}" aria-label="${esc(p.headline.replace(/\\n/g,' '))}">
      <div class="bgl" style="background:${GROUND}"></div>
      ${p.media.kind==='mark'
        ? `<div class="stage markstage">${markImg('bnrmark')}</div>`
        : slideMedia(p)}
      <div class="txt">
        <span class="eye">${esc(p.eyebrow)}</span>
        <h2>${esc(p.headline).replace(/\\n/g,'<br>')}</h2>
        <p>${esc(p.sub)}</p>
        <span class="cta">${esc(p.cta)} ${ARROW}</span>
      </div>
    </button>`).join('')}</div>`;
}

function heroHTML(){
  if(!PROMOS.length) return '';
  return `<div class="promoc" id="hero">""")

rep("""        ${slideMedia(p)}
        <div class="txt" style="color:${p.theme.ink}">""",
"""        ${p.mark?`<span class="bnr-mark">${markImg('bnrmark')}</span>`:''}
        ${slideMedia(p)}
        <div class="txt" style="color:${p.theme.ink}">""")

rep("""  ${heroHTML()}
""", """  ${heroHTML()}
  ${pairHTML()}
""")

# the pair's buttons go where the featured banner's do
rep("""document.addEventListener('click', e=>{
  const g = e.target.closest('[data-sub]');""",
"""document.addEventListener('click', e=>{
  const bp = e.target.closest('[data-pair]');
  if(bp){
    const p = PROMO_PAIR.find(x=>x.id===bp.dataset.pair);
    if(p){ p.act==='ff' ? (typeof openFF==='function'?openFF():go('all')) : go(p.act) }
    return;
  }
}, true);

document.addEventListener('click', e=>{
  const g = e.target.closest('[data-sub]');""")

# ---------------------------------------------------------------- style
BANNER_CSS = """
/* ==========================================================================
   THE BANNER SYSTEM
   One radius, one border, one inset, one eyebrow, one headline scale, one
   CTA, one image stage. The featured banner and the pair beneath it are the
   same object at two widths.
   ========================================================================== */
.promoc,.bnr{border-radius:var(--r-card);overflow:hidden;
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,123,200,.20)}
.promoc{margin:0 var(--sp-edge)}
.bpair{display:grid;grid-template-columns:1fr 1fr;gap:11px;
  margin:11px var(--sp-edge) 0}
@media (max-width:430px){.bpair{grid-template-columns:1fr}}

.bnr{position:relative;display:block;text-align:left;min-height:186px;
  padding:15px 15px 14px;isolation:isolate}
.bnr .bgl{position:absolute;inset:0;z-index:0}
.bnr .txt{position:relative;z-index:3;display:flex;flex-direction:column;
  align-items:flex-start;max-width:66%}
.bnr .stage{position:absolute;right:0;top:0;bottom:0;width:46%;z-index:2}
.bnr .eye{font-family:var(--mono);font-size:9px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--go-ink);opacity:1;line-height:1}
.bnr h2{font-family:var(--disp);font-weight:800;font-size:20px;line-height:1.03;
  letter-spacing:-.04em;margin:8px 0 0;color:#FFF;text-wrap:balance}
.bnr p{font-size:11.5px;line-height:1.38;margin:6px 0 0;color:var(--ink2);
  max-width:20ch;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden}
.bnr .cta{margin-top:auto;padding-top:12px;display:inline-flex;align-items:center;
  gap:6px;font-family:var(--block);text-transform:uppercase;letter-spacing:.045em;
  font-size:11px;color:var(--go-ink)}
.bnr .cta svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.bnr:active{transform:scale(.99)}
.bnr .markstage{display:grid;place-items:center;width:44%;padding:14px}
.bnr .markstage .hcm{width:100%}

/* the shop's own mark on the featured banner, small and in one corner */
.slide .bnr-mark{position:absolute;left:20px;top:16px;width:52px;z-index:4;
  opacity:.96;pointer-events:none}
.slide .bnr-mark .hcm{width:100%}
.slide .txt{padding-top:58px}
@media (max-width:360px){.slide .bnr-mark{width:44px}.slide .txt{padding-top:50px}}
"""
i = s.rindex('</style>')
s = s[:i] + BANNER_CSS + s[i:]
print('  banner css appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
