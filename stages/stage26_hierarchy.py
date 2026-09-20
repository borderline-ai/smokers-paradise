#!/usr/bin/env python3
# Stage 26 — retail hierarchy, and no claim the shop has not made.
#
# Mushroom Chocolate was sitting beside Water Pipes and Puffco as though a
# product type were a department. It is not. It goes inside Exotic Snacks,
# with Mushroom Chocolates as a filter within that shelf, next to the exotic
# candy, lollipops, gummies and novelty a border-town smoke shop actually
# groups it with.
#
# And every line that told a customer something was in stock has come out.
# We do not have this shop's inventory feed, so the app cannot say it does.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))

# ============================================================ 1. departments
rep("""  ["nic","Nicotine Pouches","Cans and rolls"],
  ["shroom","Mushroom Chocolate","Bars and edibles"],""",
    """  ["nic","Nicotine Pouches","Cans and rolls"],""")

rep("""  ["snack","Snacks & Drinks","Late-night shelf"],""",
    """  ["snack","Snacks, Drinks & Treats","Late-night shelf"],
  ["exotic","Exotic Snacks","Mushroom chocolate, candy, gummies"],""")

# the shelf key moves with the products
rep("""const RAW={
love:[""", """const RAW={
love:[""")
rep("""shroom:[""", """exotic:[""")

# ---- subcategories, for the shelves that need them --------------------------
rep("""const CATS=[""",
"""/* ---- subcategories ----
   A department can carry groups. Only two need them, and neither group is
   allowed to graduate to a department of its own: a product type sitting
   beside Water Pipes is the mistake this replaces. The chips filter the
   shelf; nothing else in the app has to know they exist. */
const SUBCATS = {
  exotic: [
    ['shroom', 'Mushroom Chocolates'],
    ['candy',  'Exotic Candy'],
    ['lolli',  'Lollipops'],
    ['gummy',  'Gummies'],
    ['novel',  'Novelty Treats']
  ],
  snack: [
    ['snacks', 'Snacks'],
    ['drinks', 'Drinks'],
    ['sweets', 'Sweets']
  ]
};
const subOf = p => (p && p.sub) || '';

const CATS=[""")

# tag the bars so the filter has something to match
for flav, sub in [('Peanut Butter','shroom'), ('Fruity Cereal','shroom'),
                  ('Chocolate Crunch','shroom'), ('Cookies & Cream','shroom'),
                  ('Chocolate Milk','shroom')]:
    a = '["Mushroom Chocolate, %s","TRE House",30,34.99,"bar",' % flav
    rep(a, a.replace('"bar",', '"bar|shroom",'))

# shape carries the sub after a pipe; split it where products are built
rep("""    PRODUCTS.push({id,cat,name:r[0],brand:r[1],price:r[2],was:r[3],shape:r[4],c1:r[5],c2:r[6],""",
"""    /* a shape may carry its subcategory after a pipe: "bar|shroom" */
    const sh=String(r[4]||'').split('|');
    PRODUCTS.push({id,cat,name:r[0],brand:r[1],price:r[2],was:r[3],shape:sh[0],sub:sh[1]||'',c1:r[5],c2:r[6],""")

# ---- the tile -------------------------------------------------------------
rep("""  {k:'shroom',n:'Mushroom Chocolate',       img:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter')||"https://trehouse.com/cdn/shop/files/trehouse-photo-render-product-mushroomchocolates-extrastrength-group-nov-11-2025.jpg?width=900"},""",
"""  {k:'exotic',n:'Exotic Snacks',           img:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter')||"https://trehouse.com/cdn/shop/files/trehouse-photo-render-product-mushroomchocolates-extrastrength-group-nov-11-2025.jpg?width=900"},""")

# ---- the shelf page gets a group filter -----------------------------------
rep("""  <div class="filterbar">
    ${brands.length>1?`""",
"""  ${(SUBCATS[cat[0]]||[]).length ? `<div class="filterbar subbar">
    <div class="fl-lab">In this shelf</div>
    <div class="chips" role="group" aria-label="Filter by group">
      <button class="chip ${CATSTATE.sub?'':'on'}" data-sub="all" aria-pressed="${!CATSTATE.sub}">All</button>
      ${SUBCATS[cat[0]].filter(g=>items.some(p=>subOf(p)===g[0]))
        .map(g=>`<button class="chip ${CATSTATE.sub===g[0]?'on':''}" data-sub="${g[0]}"
          aria-pressed="${CATSTATE.sub===g[0]}">${esc(g[1])}</button>`).join('')}
    </div></div>` : ''}
  <div class="filterbar">
    ${brands.length>1?`""")

rep("""  const items=PRODUCTS.filter(p=>p.cat===cat[0]);""",
"""  let items=PRODUCTS.filter(p=>p.cat===cat[0]);
  if(CATSTATE.sub && !items.some(p=>subOf(p)===CATSTATE.sub)) CATSTATE.sub='';
  if(CATSTATE.sub) items = items.filter(p=>subOf(p)===CATSTATE.sub);""")

rep("""    CATSTATE={c,b:keepB,sort:'featured'};""",
    """    CATSTATE={c,b:keepB,sort:'featured',sub:''};""")

rep("""document.addEventListener('click', e=>{
  const r = e.target.closest('.ck-row.priv[data-reveal]');""",
"""document.addEventListener('click', e=>{
  const g = e.target.closest('[data-sub]');
  if(g && typeof CATSTATE==='object'){
    CATSTATE.sub = g.dataset.sub === 'all' ? '' : g.dataset.sub;
    renderCat(); return;
  }
}, true);

document.addEventListener('click', e=>{
  const r = e.target.closest('.ck-row.priv[data-reveal]');""")

# the home rail follows the shelf
rep("""  const shrooms= pickR(p=>p.cat==='shroom',10);""",
    """  const shrooms= pickR(p=>p.cat==='exotic',10);""")
rep("""  ${shrooms.length?railSec('Mushroom Chocolate','<button class="more" data-go="cat-shroom">View All</button>',
      shrooms.map(card).join(''),1.8,'$30 a bar','deal'):''}""",
    """  ${shrooms.length?railSec('Exotic Snacks','<button class="more" data-go="cat-exotic">View All</button>',
      shrooms.map(card).join(''),1.8,'Featured in the demo'):''}""")

# ============================================================ 2. the claims
CLAIMS = [
  ("eyebrow:'On the shelf now',", "eyebrow:'Sample offer',"),
  ("eyebrow:'New on the counter',", "eyebrow:'Demo selection',"),
  ("eyebrow:'Just landed',", "eyebrow:'Demo selection',"),
  ("badge:'In store now', disclaimer:'21+ only. Valid ID at pickup. While stock lasts.',",
   "badge:'Sample offer', disclaimer:'Sample offer taken from Smokers Paradise content. Pending store confirmation. 21+ only.',"),
  ("badge:'New', disclaimer:'21+ only. Valid ID at pickup.',",
   "badge:'Demo promotion', disclaimer:'Demo promotion. Pending store confirmation. 21+ only.',"),
  ("badge:'Every visit', disclaimer:'In store only. One spin per visit.',",
   "badge:'Sample offer', disclaimer:'Seen in Smokers Paradise content. Pending store confirmation.',"),
  ("badge:'Ongoing', disclaimer:'In store only. Ask at the counter for the current prize.',",
   "badge:'Sample offer', disclaimer:'Seen in Smokers Paradise content. Pending store confirmation.',"),
  ("subtitle:'Five flavors of extra-strength mushroom chocolate, in stock.',",
   "subtitle:'Five flavors of extra-strength mushroom chocolate.',"),
  ("sub:'Five flavors, $30 a bar.',", "sub:'Five flavors, $30 a bar.',"),
  ("""    <div class="sec-lead">Current in-store promotions. Save one and show the screen at the register.</div>""",
   """    <div class="sec-lead">Sample offers, pending confirmation with the store. Save one and show the screen at the register.</div>"""),
  ("""    What we are running in store right now.
    Save the ones you want and show this screen at the register.""",
   """    Sample offers and demo promotions, pending confirmation with the store.
    Save the ones you want and show this screen at the register."""),
  ("""  ${famous.length?railSec('Popular in Nogales',
      '<button class="more" data-go="all">Shop All</button>',
      famous.map(card).join(''),
      4,'Moves fastest','deal'):''}""",
   """  ${famous.length?railSec('New-Generation Favorites',
      '<button class="more" data-go="all">Explore the collection</button>',
      famous.map(card).join(''),
      4,'Seen in Smokers Paradise content'):''}"""),
  ("railSec('Disposable Vapes','<button class=\"more\" data-go=\"cat-disp\">View All</button>',\n      disp.map(card).join(''),2,'On the shelf')",
   "railSec('Disposable Vapes','<button class=\"more\" data-go=\"cat-disp\">View All</button>',\n      disp.map(card).join(''),2,'Demo selection')"),
  ("railSec('Paradise Picks','<button class=\"more\" data-go=\"all\">Shop All</button>',\n      picks.map(card).join(''),1.5,'Chosen at the counter')",
   "railSec('Paradise Picks','<button class=\"more\" data-go=\"all\">Shop All</button>',\n      picks.map(card).join(''),1.5,'Featured in the demo')"),
  ("<div class=\"eye\">Puffco at Smokers Paradise</div>", "<div class=\"eye\">Featured in the demo</div>"),
  ("<h3>Peak, Proxy, Pivot.<br>On the shelf in Nogales.</h3>", "<h3>Peak, Proxy, Pivot.<br>Explore the collection.</h3>"),
  ("<p>The current Puffco line and the chambers and glass that go with it, without waiting on a shipment.</p>",
   "<p>The current Puffco line and the chambers and glass that go with it.</p>"),
  ("{t:'TRE House mushroom chocolate now in, $30 a bar', k:'new'},", "{t:'TRE House mushroom chocolate, $30 a bar', k:'new'},"),
  ("{t:'Off-Stamp pods 2 for $10, 3 for $12', k:''},", "{t:'Sample offer: Off-Stamp pods 2 for $10, 3 for $12', k:''},"),
  ("{t:'Spend $15, spin the wheel at the counter', k:''},", "{t:'Sample offer: spend $15, spin the wheel', k:''},"),
  ("{t:'New disposable flavors just added to the menu', k:'new'},", "{t:'Demo selection. Confirmed with the store at onboarding', k:''},"),
  ("shop stocked", "demo selection"),
  ("'Moves fastest'", "'Seen in Smokers Paradise content'"),
]
for a, b in CLAIMS:
    rep(a, b, count=s.count(a) if s.count(a) > 1 else 1, must=False)

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
