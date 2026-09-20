#!/usr/bin/env python3
# Stage 25 — no more white squares, no circle behind the mark, and a real wheel.
#
# Three things, all the same root problem: a shape was standing in for design.
#
#  1. Manufacturer packshots ship on white. Dropped onto a dark app inside a
#     box, every one of them reads as a white square with a product in it.
#     Fixed by lighting them instead of framing them: a radial pool that is
#     bright where the product sits and fully transparent by its edge, so
#     there is no edge. The packshot's own white ground melts into the pool.
#  2. The mark had a lamp behind it drawn as a disc, which put the logo back
#     in the circle it was cut out of. The bloom now follows the logo's own
#     silhouette.
#  3. The Spin-N-Win card had the characters "$15+" where a wheel belongs.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))

# ================================================================ 1. the mark
rep(""".hcm-glow{position:absolute;left:50%;top:44%;width:112%;height:112%;transform:translate(-50%,-50%);
  border-radius:50%;pointer-events:none;z-index:0;
  background:radial-gradient(circle,rgba(255,47,168,.22) 0%,rgba(255,47,168,.07) 44%,transparent 66%);
  animation:markLamp 7s ease-in-out infinite}""",
""".hcm-glow{display:none}""")

rep(""".hcm-glow{box-shadow:0 0 44px 10px rgba(255,47,168,.26)}""",
"""/* The light comes off the letters, not out of a disc behind them. A box or a
   circle drawn behind a cut-out logo puts the logo straight back into the
   shape it was cut out of. */
.hcm-img{filter:drop-shadow(0 0 14px rgba(255,47,168,.42)) drop-shadow(0 0 34px rgba(255,47,168,.20))}
@keyframes markBloom{0%,100%{opacity:.86}50%{opacity:1}}
.hcm .hcm-img{animation:markBloom 7s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){.hcm .hcm-img{animation:none}}""")

# ================================================================ 2. the pools
# One rule, used everywhere a packshot lands.
rep(""".slide .stage .pz.flat{background:#FFF;border-radius:13px;padding:9px;width:88%;height:70%;""",
"""/* ---- the light pool ----
   Not a card. A pool of light that is bright under the product and gone by
   the time it reaches anything else, so a packshot on a white ground has
   nothing to have a corner against. */
.pool{background:radial-gradient(58% 56% at 50% 47%,
    rgba(255,255,255,.97) 0%, rgba(255,255,255,.93) 30%,
    rgba(255,255,255,.62) 55%, rgba(255,255,255,.18) 72%,
    rgba(255,255,255,0) 84%)}
.slide .stage .pz.flat{border-radius:13px;padding:9px;width:88%;height:70%;""")

rep("""  box-shadow:0 18px 34px rgba(0,0,0,.44)}
.slide .stage .pz.flat img{filter:none;border-radius:7px}""",
"""  background:radial-gradient(56% 54% at 50% 47%,
    rgba(255,255,255,.97) 0%, rgba(255,255,255,.92) 30%,
    rgba(255,255,255,.58) 54%, rgba(255,255,255,.16) 71%,
    rgba(255,255,255,0) 84%)}
.slide .stage .pz.flat img{filter:none}""")

rep("""/* Fanned plates overlap, so each needs an edge of its own or three white
   cards read as one white shape. */
.slide .stage .pz.flat{outline:1px solid rgba(0,0,0,.10);outline-offset:-1px}""",
"""/* Pools overlap softly, so nothing needs an edge to separate it. */""")

# product cards: the panel was a white block with a rule under it
rep(""".card .thumb{aspect-ratio:1/1;height:auto;position:relative;padding:0;
  background:var(--stage);border-bottom:1px solid var(--hair2);overflow:hidden}""",
""".card .thumb{aspect-ratio:1/1;height:auto;position:relative;padding:0;overflow:visible}""")

rep(""".card .thumb{background:
  radial-gradient(78% 62% at 50% 32%,#FFFFFF 0%,var(--stage) 58%,#E2DBF4 100%)}""",
""".card .thumb{background:radial-gradient(54% 52% at 50% 46%,
  rgba(255,255,255,.97) 0%, rgba(255,255,255,.92) 28%,
  rgba(255,255,255,.56) 52%, rgba(255,255,255,.14) 70%,
  rgba(255,255,255,0) 83%)}""")

# category tiles
rep(""".ctile .ph{width:104px;height:104px;border-radius:16px;background:var(--card2);border:1px solid var(--hair);
  display:grid;place-items:center;overflow:hidden;position:relative;transition:border-color .18s,box-shadow .18s}
.ctile:hover .ph{border-color:var(--hairD);box-shadow:0 8px 18px rgba(0,0,0,.09)}""",
""".ctile .ph{width:104px;height:104px;border-radius:16px;
  background:radial-gradient(56% 54% at 50% 47%,
    rgba(255,255,255,.97) 0%, rgba(255,255,255,.92) 30%,
    rgba(255,255,255,.58) 54%, rgba(255,255,255,.16) 71%,
    rgba(255,255,255,0) 84%);
  display:grid;place-items:center;overflow:visible;position:relative;transition:transform .18s}
.ctile:hover .ph{transform:translateY(-2px)}""")

# brand tiles
rep(""".btile .bp{height:56px;display:grid;place-items:center;width:100%;background:var(--card2);border-radius:8px}""",
""".btile .bp{height:56px;display:grid;place-items:center;width:100%;border-radius:8px;
  background:radial-gradient(58% 56% at 50% 48%,
    rgba(255,255,255,.96) 0%, rgba(255,255,255,.88) 32%,
    rgba(255,255,255,.48) 58%, rgba(255,255,255,0) 82%)}""")

# deal card plates
rep(""".dcard .dart .dplate{position:absolute;inset:0;background:#FFF;border-radius:12px;""",
""".dcard .dart .dplate{position:absolute;inset:0;border-radius:12px;
  background:radial-gradient(56% 54% at 50% 47%,
    rgba(255,255,255,.97) 0%, rgba(255,255,255,.92) 30%,
    rgba(255,255,255,.56) 54%, rgba(255,255,255,.14) 72%,
    rgba(255,255,255,0) 85%);""")
rep(""".dealrow .drart .dplate{position:absolute;inset:0;background:#FFF;border-radius:13px;""",
""".dealrow .drart .dplate{position:absolute;inset:0;border-radius:13px;
  background:radial-gradient(56% 54% at 50% 47%,
    rgba(255,255,255,.97) 0%, rgba(255,255,255,.92) 30%,
    rgba(255,255,255,.56) 54%, rgba(255,255,255,.14) 72%,
    rgba(255,255,255,0) 85%);""")

# the Puffco row
rep(""".spotitem .sp{height:104px;border-radius:13px;background:rgba(255,255,255,.045);""",
""".spotitem .sp{height:104px;border-radius:13px;
  background:radial-gradient(56% 54% at 50% 47%,
    rgba(255,255,255,.95) 0%, rgba(255,255,255,.88) 30%,
    rgba(255,255,255,.52) 55%, rgba(255,255,255,0) 82%);""")
rep(""".spotitem:hover .sp{transform:translateY(-3px);background:rgba(255,255,255,.08)}""",
""".spotitem:hover .sp{transform:translateY(-3px)}""")

# ================================================================ 3. the wheel
rep("""function dealCardBig(d,i){""",
"""/* The wheel they actually spin at the counter, drawn rather than photographed:
   ten wedges, a bulb rim, a pointer. It turns slowly, and stops turning for
   anyone who has asked the system for less motion. */
function wheelSVG(){
  const C=['#FF2FA8','#1B0F26','#FFA51F','#1B0F26','#B487FF','#1B0F26','#5FD36A','#1B0F26','#FF7BC8','#1B0F26'];
  const R=41, cx=50, cy=52, seg=36, wedge=[];
  for(let k=0;k<10;k++){
    const a0=(k*seg-90)*Math.PI/180, a1=((k+1)*seg-90)*Math.PI/180;
    wedge.push(`<path d="M${cx} ${cy} L${(cx+R*Math.cos(a0)).toFixed(2)} ${(cy+R*Math.sin(a0)).toFixed(2)} `
      + `A${R} ${R} 0 0 1 ${(cx+R*Math.cos(a1)).toFixed(2)} ${(cy+R*Math.sin(a1)).toFixed(2)} Z" fill="${C[k]}"/>`);
  }
  const bulbs=[];
  for(let k=0;k<16;k++){
    const a=(k*22.5-90)*Math.PI/180;
    bulbs.push(`<circle cx="${(cx+46*Math.cos(a)).toFixed(2)}" cy="${(cy+46*Math.sin(a)).toFixed(2)}" r="1.7" fill="#FFD98A"/>`);
  }
  return `<svg class="wheel" viewBox="0 0 100 100" aria-hidden="true">
    <g class="wsp" style="transform-origin:${cx}px ${cy}px">
      <circle cx="${cx}" cy="${cy}" r="46" fill="#3A2A08"/>
      <circle cx="${cx}" cy="${cy}" r="46" fill="none" stroke="#FFC46B" stroke-width="3"/>
      ${bulbs.join('')}
      ${wedge.join('')}
      <circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="rgba(0,0,0,.35)" stroke-width="1"/>
    </g>
    <circle cx="${cx}" cy="${cy}" r="7" fill="#FFC46B"/>
    <path d="M50 3 L57 16 L43 16 Z" fill="#FFD98A"/>
  </svg>`;
}
function ticketSVG(){
  return `<svg class="tkt" viewBox="0 0 100 100" aria-hidden="true">
    <path d="M14 32h72a6 6 0 016 6v8a7 7 0 000 14v8a6 6 0 01-6 6H14a6 6 0 01-6-6v-8a7 7 0 000-14v-8a6 6 0 016-6z"
      fill="none" stroke="#FF7BC8" stroke-width="3.4" stroke-linejoin="round"/>
    <path d="M50 34v6M50 47v6M50 60v6" stroke="#FF7BC8" stroke-width="3.4" stroke-linecap="round"/>
  </svg>`;
}

function dealCardBig(d,i){""")

rep("""  const raw = (d.discountAmount||'').trim();
  const isPct = /^\\s*\\d+\\s*%\\s*$/.test(raw);
  const pct = !im ? (isPct ? raw.replace(/[^0-9%]/g,'') : '') : '';
  const words = !im && !isPct ? raw : '';""",
"""  const raw = (d.discountAmount||'').trim();
  const isPct = /^\\s*\\d+\\s*%\\s*$/.test(raw);
  const pct = !im ? (isPct ? raw.replace(/[^0-9%]/g,'') : '') : '';
  const words = !im && !isPct && !d.art ? raw : '';
  const drawn = !im && d.art === 'wheel' ? wheelSVG() : (!im && d.art === 'ticket' ? ticketSVG() : '');""")

rep("""       : words ? `<div class="dword" style="color:${d.theme.accent}">${esc(words)}</div>`""",
"""       : drawn ? `<div class="ddraw">${drawn}</div>`
       : words ? `<div class="dword" style="color:${d.theme.accent}">${esc(words)}</div>`""")

rep("""    dealType:'note', discountAmount:'$15+', qualifyingCategory:'',""",
    """    dealType:'note', discountAmount:'$15+', art:'wheel', qualifyingCategory:'',""")
rep("""    dealType:'note', discountAmount:'$10+', qualifyingCategory:'',""",
    """    dealType:'note', discountAmount:'$10+', art:'ticket', qualifyingCategory:'',""")

rep(""".dword{font-family:var(--block);""",
""".ddraw{position:relative;display:grid;place-items:center;width:100%;height:100%;padding:6px}
.ddraw .wheel,.ddraw .tkt{width:100%;height:100%;max-width:120px;max-height:120px;
  filter:drop-shadow(0 8px 18px rgba(0,0,0,.45))}
.ddraw .wheel .wsp{animation:wheelTurn 22s linear infinite}
@keyframes wheelTurn{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.ddraw .wheel .wsp{animation:none}}
.dword{font-family:var(--block);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
