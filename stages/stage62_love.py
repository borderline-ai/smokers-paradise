#!/usr/bin/env python3
# Stage 62 — the Love shelf. Two rules were colliding and both were losing.
#
# WHAT WAS THERE
#   Ten products under a brand called "Paradise" — a brand that does not exist —
#   at prices nobody ever quoted: Rechargeable Personal Massager $39.99, Couples
#   Ring $14.99, Lace Lingerie Set $34.99, and so on. None of them had a
#   photograph, so each rendered as a coloured plate with a heart and one word.
#
# WHY THAT IS TWO FAULTS, NOT ONE
#   1. "Every product card must display a real photograph. There cannot be one
#      blank product card anywhere." Ten blank cards.
#   2. "Never invent products, prices or inventory." Ten invented SKUs, an
#      invented house brand and ten invented prices — the worst of the two, and
#      the one nobody had caught because the audit swept for invented CLAIMS
#      and never for invented PRODUCTS.
#
#   The plates were a deliberate privacy design and the reasoning still holds:
#   somebody buying from this shelf is buying it here so they do not have to
#   stand in front of it. But privacy is not a licence to invent a catalogue.
#
# THE FIX
#   The invented SKUs are deleted. The department stays — it is the shop's
#   strongest differentiator — and becomes what it honestly is right now: an
#   in-store shelf, designed properly, with no product grid to be blank. It goes
#   back to being orderable the moment the shop sends real product names and
#   real photographs, exactly like the other 266 products got theirs.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))


# ---------------------------------------------------------- 1. the invented SKUs
i = s.index('const RAW={\nlove:[\n')
j = s.index('\n],\nexotic:[', i)
removed = s[i:j].count('\n["')
s = s[:i] + 'const RAW={\n/* The Love shelf carries no catalogue.\n' \
            '   It used to carry ten products under a house brand called\n' \
            '   "Paradise" at invented prices, none of which had a photograph.\n' \
            '   Invented merchandise is worse than an empty shelf, so the shelf\n' \
            '   is empty and the department page says plainly that this one is\n' \
            '   bought in store. Real names and real photographs from the shop\n' \
            '   turn it back into a shelf like any other. */\nlove:[' + s[j:]
print('  removed %d invented Love SKUs' % removed)

# ------------------------------------------------- 2. the department page itself
rep("""function renderCat(c){
  if(c){""",
"""function renderCat(c){
  if(c){""")

rep("""  const cat=CATS.find(x=>x[0]===CATSTATE.c)||CATS[0];
  CATSTATE.c=cat[0];
  let items=PRODUCTS.filter(p=>p.cat===cat[0]);""",
"""  const cat=CATS.find(x=>x[0]===CATSTATE.c)||CATS[0];
  CATSTATE.c=cat[0];
  /* The discreet shelf has no catalogue to render, so it does not get the
     grid, the filter bar or the sort — it gets its own page. */
  if(cat[0]===DISCREET_CAT) return renderLove(cat);
  let items=PRODUCTS.filter(p=>p.cat===cat[0]);""")

LOVE_FN = r'''
/* ---- the discreet shelf ----
   Designed, not padded. There is no product grid here because there are no
   real products to put in one, and a grid of invented merchandise is a worse
   answer than an honest page. Everything on it is either the app's own
   behaviour or a fact already verified about the store. */
function renderLove(cat){
  $('#v-cat').innerHTML = `
  <div class="shelfhead cat-love" data-cat="love">
    <span class="sh-sky" aria-hidden="true"><span class="sh-stars"></span></span>
    <div class="sh-row">
      <button class="bk" data-back="1" aria-label="Back">
        <svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></button>
      <span class="sh-kick">Shelf</span>
    </div>
    <h2>${cat[1]}</h2>
    <div class="sh-meta">In store &middot; 21+</div>
    <span class="hcrule"></span>
  </div>

  <div class="lovepage">
    <div class="lv-panel">
      <span class="lv-glow" aria-hidden="true"></span>
      <span class="lv-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24"><path d="M12 20.5s-7.4-4.8-7.4-9.9A4.4 4.4 0 0112 7.6a4.4 4.4 0 017.4 3C19.4 15.7 12 20.5 12 20.5z"/></svg>
      </span>
      <span class="lv-kick">Discreet &middot; 21+</span>
      <h3>This shelf stays in store</h3>
      <p>Lingerie, toys, couples and the care that goes with them. We don&rsquo;t
         put this one in the app &mdash; come in and ask at the counter.</p>
      <p class="es">Lencer&iacute;a, juguetes, parejas y el cuidado que va con eso.
         Esta secci&oacute;n no va en la app. Pasa y pregunta en el mostrador.</p>
      <div class="lv-groups">
        <span>Lingerie</span><span>Toys</span><span>Couples</span><span>Care</span>
      </div>
      <div class="lv-acts">
        <a class="pri" href="${STORE.phoneHref}">Call the shop</a>
        <a class="sec2" href="${STORE.mapHref}" target="_blank" rel="noopener">Directions</a>
      </div>
      <span class="lv-fine">21+ only. Valid ID at the counter.</span>
    </div>
    <button class="lv-back" data-go="all">Back to the shelf</button>
  </div>
  <div style="height:26px"></div>`;
  if(typeof wireReveal === 'function') wireReveal('#v-cat');
}

'''
k = s.index('function renderCat(c){')
s = s[:k] + LOVE_FN + s[k:]
print('  renderLove added')

# ------------------------------------------------------- 3. the department tile
rep("""    <div class="cattiles" id="catRail">${CATTILES.filter(c=>cnt(c.k)>=3).map(c=>{""",
    """    <div class="cattiles" id="catRail">${CATTILES.filter(c=>c.k==='love'||cnt(c.k)>=3).map(c=>{""")

rep("""        <b>${c.n}</b><small>${cnt(c.k)} items</small></button>`}).join('')}</div>""",
    """        <b>${c.n}</b><small>${c.k==='love'?'In store':cnt(c.k)+' items'}</small></button>`}).join('')}</div>""")

rep("""  {k:'love',  n:'Love',                     img:()=>'', plate:()=>discreetPlate({shape:'couples'""",
    """  {k:'love',  n:'Love',                     img:()=>'', plate:()=>loveMark({shape:'couples'""")

rep("""function discreetPlate(p){""",
"""/* The department's own emblem. A tile is not a product card, so it is allowed
   to carry a designed mark rather than a photograph — what it may not do is
   look like a product card with the picture missing. */
function loveMark(){
  return `<span class="lvmark" role="img" aria-label="Love, in store">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.4-4.8-7.4-9.9A4.4 4.4 0 0112 7.6a4.4 4.4 0 017.4 3C19.4 15.7 12 20.5 12 20.5z"/></svg>
    <b>21+</b></span>`;
}
function discreetPlate(p){""")

# --------------------------------------------------------------- 4. the styles
CSS = r'''
/* ==========================================================================
   THE DISCREET SHELF
   One designed page instead of a grid of merchandise nobody has photographed.
   ========================================================================== */
.lovepage{padding:16px 16px 8px}
.lv-panel{position:relative;overflow:hidden;border-radius:var(--r-card);
  padding:30px 20px 22px;text-align:center;
  background:linear-gradient(158deg,#26071C 0%,#460E33 54%,#2A0A22 100%);
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,123,200,.20)}
.lv-glow{position:absolute;left:50%;top:-12%;width:150%;aspect-ratio:1/1;
  transform:translateX(-50%);pointer-events:none;border-radius:50%;
  background:radial-gradient(circle, rgba(255,47,168,.26) 0%, transparent 62%)}
.lv-mark{position:relative;display:grid;place-items:center;width:64px;height:64px;
  margin:0 auto 14px;border-radius:50%;
  background:radial-gradient(circle at 50% 38%, rgba(255,123,200,.26), rgba(255,47,168,.06));
  box-shadow:inset 0 0 0 1px rgba(255,123,200,.34)}
.lv-mark svg{width:28px;height:28px;fill:none;stroke:#FF7BC8;stroke-width:1.6;
  stroke-linecap:round;stroke-linejoin:round}
.lv-panel .lv-kick{position:relative;display:block;font-family:var(--mono);
  font-size:9.5px;letter-spacing:.26em;text-transform:uppercase;color:#FF9BD4}
.lv-panel h3{position:relative;font-family:var(--disp);font-weight:800;
  font-size:26px;line-height:1.1;letter-spacing:-.03em;color:#FFF;margin:8px 0 10px}
.lv-panel p{position:relative;font-size:13px;line-height:1.55;color:var(--body);
  margin:0 auto 8px;max-width:30em}
.lv-panel p.es{color:var(--muted);font-size:12px}
.lv-groups{position:relative;display:flex;flex-wrap:wrap;gap:7px;
  justify-content:center;margin:15px 0 4px}
.lv-groups span{font-family:var(--block);font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;font-size:11px;color:#FFD3EC;padding:7px 13px;border-radius:99px;
  background:rgba(255,123,200,.10);box-shadow:inset 0 0 0 1px rgba(255,123,200,.26)}
.lv-acts{position:relative;display:flex;gap:9px;justify-content:center;
  flex-wrap:wrap;margin-top:17px}
.lv-acts a{display:inline-flex;align-items:center;justify-content:center;
  min-height:44px;padding:0 20px;border-radius:99px;font-size:13.5px;font-weight:700;
  font-family:var(--body-f);text-decoration:none}
.lv-acts .pri{background:var(--go);color:var(--go-on)}
.lv-acts .sec2{color:#FFD3EC;box-shadow:inset 0 0 0 1px rgba(255,123,200,.34)}
.lv-panel .lv-fine{position:relative;display:block;margin-top:14px;
  font-size:10.5px;letter-spacing:.02em;color:var(--faint)}
.lv-back{display:block;width:100%;margin:14px 0 0;padding:13px;background:transparent;
  border:0;color:var(--ink2);font-size:12.5px;font-family:var(--body-f);cursor:pointer}

/* the department tile's emblem */
.lvmark{display:grid;place-items:center;gap:3px;position:relative;z-index:2}
.lvmark svg{width:26px;height:26px;fill:none;stroke:#FF7BC8;stroke-width:1.6;
  stroke-linecap:round;stroke-linejoin:round}
.lvmark b{font-family:var(--mono);font-size:9px;letter-spacing:.16em;color:#FF9BD4}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  love styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
