#!/usr/bin/env python3
# Stage 48 — the giveaway becomes a real prize bundle.
#
# The raffle card was text on a plum rectangle since the drawn ticket came out,
# which is honest but reads as unfinished. A raffle is the one thing in a smoke
# shop that IS a picture: a table of prizes.
#
# So it is built the way a retail giveaway is shot: a beaker standing at the
# back, a second piece of glass beside it, four disposables fanned across the
# front at descending scale so they overlap and read as depth, a torch at the
# edge, every one of them standing on its own contact shadow. Every item is a
# real manufacturer photograph, already embedded in this file — the same
# photographs those products carry on their own shelves.
#
# Nothing is drawn, generated or invented. And because the shop has not
# confirmed what the next raffle actually gives away, the bundle says so: it is
# labelled a demo prize bundle, and the items are described as the kind of
# thing the shop raffles, not as prizes anyone is promised.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ---------------------------------------------------------------- component
COMP = r'''
/* ==========================================================================
   THE PRIZE BUNDLE
   A raffle is a table of prizes, so it is photographed like one: the glass at
   the back, the disposables fanned across the front at descending scale, and
   every piece standing on its own contact shadow. Each item is the real
   manufacturer photograph already embedded in this file.

   The shop has not confirmed what the next raffle gives away, so nothing here
   is presented as a promised prize. It is a demo bundle of the kind of thing
   they raffle, and it says so.
   ========================================================================== */
const PRIZE_ITEMS = [
  /* id, what it is, where it sits, how big, how far back */
  {id:'rx119', label:'Pulsar Snatched Beaker Bong',   x:'50%', y:'2%',  h:'92%', z:2, s:1.00},
  {id:'rx097', label:'GRAV Medium Beaker Base',       x:'14%', y:'16%', h:'70%', z:1, s:1.00},
  {id:'r039',  label:'Blazer Big Shot torch',         x:'88%', y:'30%', h:'52%', z:1, s:1.00},
  {id:'disp2', label:'Geek Bar Pulse X 25K',          x:'22%', y:'54%', h:'44%', z:4, s:1.00},
  {id:'rx089', label:'Lost Mary MT35000 Turbo',       x:'42%', y:'58%', h:'42%', z:5, s:1.00},
  {id:'rx065', label:'Off-Stamp X Cube 25K',          x:'61%', y:'56%', h:'40%', z:4, s:1.00},
  {id:'rx092', label:'RAZ DC25000',                   x:'79%', y:'59%', h:'38%', z:3, s:1.00}
];

function prizeItem(it){
  const src = (typeof LOCAL_PHOTOS!=='undefined') && LOCAL_PHOTOS[it.id];
  if(!src) return '';
  return `<span class="pz-i" style="left:${it.x};top:${it.y};height:${it.h};z-index:${it.z}">
    <span class="pz-sh" aria-hidden="true"></span>
    <img src="${src}" alt="${esc(it.label)}">
  </span>`;
}

/* The bundle. `compact` is the version that sits inside a deal card. */
function prizeBundle(compact){
  const shot = PRIZE_ITEMS.map(prizeItem).join('');
  if(!shot) return '';
  return `<div class="prize${compact?' sm':''}">
    <div class="pz-stage">${shot}</div>
    ${compact?'':`<span class="pz-mark">${markImg('pzmark')}</span>`}
  </div>`;
}

function prizeSection(){
  if(!PRIZE_ITEMS.some(i=>(typeof LOCAL_PHOTOS!=='undefined')&&LOCAL_PHOTOS[i.id])) return '';
  return `<div class="sec loose reveal" style="--i:12">
    ${secHead('Raffles','<button class="more" data-go="deals">See the deals</button>','Demo prize bundle')}
    <div class="pad">
      <div class="prizecard">
        ${prizeBundle(false)}
        <div class="pz-copy">
          <span class="pz-eye">Demo raffle</span>
          <h3>Spend $10, and you are in the drawing.</h3>
          <p>Pictured is a sample prize bundle: glass, disposables and a torch,
             the kind of thing that goes on the raffle table. Real product
             photography from each brand.</p>
          <div class="pz-list">${PRIZE_ITEMS.map(i=>
            `<span>${esc(i.label)}</span>`).join('')}</div>
          <button class="btn neon" data-go="deals"><span>See the deals</span></button>
          <span class="pz-fine">Demo prize bundle. The pictured items are examples, not
            confirmed prizes, and the raffle is pending store confirmation. 21+ only.</span>
        </div>
      </div>
    </div>
  </div>`;
}
'''
i = s.index('function heroHTML(){')
s = s[:i] + COMP + '\n' + s[i:]
print('  prize bundle component written')

# ---------------------------------------------------------------- placement
rep("""  ${GIVEAWAYS.length?`<div class="sec loose reveal" style="--i:12">""",
    """  ${prizeSection()}

  ${GIVEAWAYS.length?`<div class="sec loose reveal" style="--i:12">""")

# the raffle deal card carries the bundle instead of nothing
rep("""  { id:'d-raffle', title:'Raffle entry at $10', subtitle:'Spend $10 or more and you are in the drawing. Prizes come off our own shelf.',""",
    """  { id:'d-raffle', title:'Raffle entry at $10', subtitle:'Spend $10 or more and you are in the drawing. Pictured: a demo prize bundle.',
    art:'prize',""")

rep("""            : d.art==='wheel' ? `<div class="ddraw" style="width:100%;height:100%">${wheelSVG()}</div>`""",
    """            : d.art==='prize' ? prizeBundle(true)
            : d.art==='wheel' ? `<div class="ddraw" style="width:100%;height:100%">${wheelSVG()}</div>`""")
rep("""  const drawn = !im && d.art === 'wheel' ? wheelSVG() : '';""",
    """  const drawn = !im && d.art === 'wheel' ? wheelSVG() : '';
  if(!im && d.art === 'prize'){ const pb = prizeBundle(true); if(pb) return pb }""")

# ---------------------------------------------------------------- style
CSS = r'''
/* ---- the prize bundle ---- */
.prizecard{position:relative;border-radius:var(--r-card);overflow:hidden;
  background:linear-gradient(168deg,#1B0A26 0%,#2E0E2E 54%,#43102F 100%);
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,123,200,.18)}
.prize{position:relative;width:100%;aspect-ratio:16/10}
.prize.sm{aspect-ratio:1/1}
/* the table the prizes stand on: one soft pool of light, no product halo */
.pz-stage{position:absolute;inset:0;
  background:
    linear-gradient(to top, rgba(255,47,168,.12) 0%, rgba(255,47,168,0) 46%),
    linear-gradient(to top, rgba(0,0,0,.34) 0%, rgba(0,0,0,0) 40%)}
.pz-i{position:absolute;transform:translateX(-50%);display:block}
.pz-i img{display:block;height:100%;width:auto;max-width:none;
  filter:drop-shadow(0 12px 16px rgba(0,0,0,.55))}
/* each piece stands on the table rather than floating over it */
.pz-sh{position:absolute;left:50%;bottom:-3%;transform:translateX(-50%);
  width:86%;height:9px;border-radius:50%;filter:blur(5px);
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(0,0,0,.62) 0%, rgba(0,0,0,.26) 56%, rgba(0,0,0,0) 100%)}
.pz-mark{position:absolute;right:14px;top:12px;width:58px;z-index:9;
  opacity:.95;pointer-events:none}
.pz-mark .hcm{width:100%}

.pz-copy{padding:16px var(--sp-edge) 18px;display:flex;flex-direction:column;
  align-items:flex-start;position:relative;z-index:2}
.pz-eye{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--go-ink)}
.prizecard h3{font-family:var(--disp);font-weight:800;font-size:24px;
  line-height:.98;letter-spacing:-.04em;margin:10px 0 0;color:#FFF;
  text-shadow:none}
.prizecard p{font-size:12.5px;line-height:1.42;margin:9px 0 0;color:var(--ink2);
  opacity:.88;max-width:38ch}
.pz-list{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 0}
.pz-list span{font-family:var(--mono);font-size:9px;letter-spacing:.06em;
  text-transform:uppercase;color:var(--ink2);opacity:.8;
  padding:5px 9px;border-radius:var(--r-chip);
  box-shadow:inset 0 0 0 1px rgba(255,123,200,.26)}
.prizecard .btn.neon{width:auto;margin:15px 0 0;padding:11px 20px}
.pz-fine{font-size:8.5px;line-height:1.4;margin:11px 0 0;color:var(--ink2);
  opacity:.55;max-width:44ch}

/* inside a deal card the bundle is the artwork, nothing else */
.dcard .prize.sm,.dealrow .prize.sm{aspect-ratio:1/1;height:100%}
.dcard .prize.sm .pz-stage,.dealrow .prize.sm .pz-stage{background:
  linear-gradient(to top, rgba(0,0,0,.30) 0%, rgba(0,0,0,0) 42%)}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  prize css appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
