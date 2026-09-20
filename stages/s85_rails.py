#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 85 — the first rail on the home screen was lying about itself.
#
# THE HEADING SAID MUSHROOM CHOCOLATE AND THE RAIL HELD VAPES.
#
# The first product rail a customer meets, directly under the deals, is built
# from STORE_CONTENT.featuredBrands: the nine names the shop leads with. It was
# titled "Mushroom Chocolate", its eyebrow read "From our feed" — the same words
# as the section heading immediately below it — and its button went to Shop All.
# Only the first item in it, TRE House, is mushroom chocolate. The other eleven
# are disposables. Two sections further down there is a separate rail correctly
# titled Exotic Snacks holding the same five TRE House bars.
#
# So the rail was mislabelled, its eyebrow was duplicated, and it repeated a
# rail that comes later.
#
# AND IT ONLY EVER SHOWED FOUR OF THE NINE BRANDS. It took the first three
# products of each brand in list order and then cut the result at twelve:
# TRE House, Off-Stamp, Lost Mary and Geek Bar filled all twelve slots, so RAZ,
# RAW, GRAV, Puffco and Ooze — including the entire Puffco wall and twenty-six
# pieces of GRAV glass — never reached the rail the section exists to show.
# Round-robin instead: the best of each brand in turn, then round again. All
# nine appear.
#
# WHILE LOOKING AT IT: two rails below were ten cards of a single brand.
# "Water Pipes, Rigs & Hand Pipes" was ten Diamond Glass in a row and
# "Glass Parts & Accessories" was ten GRAV, because the ranking ends in
# localeCompare on the brand name and D and G sort early. Twelve brands of glass
# are on that shelf and a customer scrolling the rail saw one. The same spread
# now applies to every rail built by pickR, so a rail reads like the wall it is
# photographed from.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. one brand must not eat a whole rail --------------------------------
rep("""  const pickR=(f,n)=>PRODUCTS.filter(f).filter(shot).slice().sort(rank).slice(0,n);""",
"""  /* A window with ten of the same brand in it is a stock list, not a window.
     The ranking ends in localeCompare on the brand, so the glass rails opened
     with ten Diamond Glass and ten GRAV while ten other brands sat on the same
     shelf unseen. Take the best of each brand in turn, then go round again. */
  const spread=(list,n)=>{
    const by=new Map();
    list.forEach(p=>{ const k=p.brand||''; if(!by.has(k)) by.set(k,[]); by.get(k).push(p) });
    const cols=[...by.values()], out=[];
    for(let i=0; out.length<n; i++){
      let added=false;
      for(const c of cols){ if(c[i] && out.length<n){ out.push(c[i]); added=true } }
      if(!added) break;
    }
    return out;
  };
  const pickR=(f,n)=>spread(PRODUCTS.filter(f).filter(shot).slice().sort(rank), n);""")

# ---- 2. the featured-brand rail shows the brands it is named after ---------
rep("""  /* Popular in Nogales: the brands we lead with in store, in our own order. */
  const famous = (STORE_CONTENT.featuredBrands||[])
    .flatMap(b=>PRODUCTS.filter(p=>p.brand===b && p.published!==false).filter(shot).slice(0,3))
    .slice(0,12);""",
"""  /* The nine names the shop leads with, in the shop's own order. Three of each
     taken in list order meant the first four brands filled all twelve slots and
     the last five never appeared at all, Puffco and GRAV among them. One of
     each first, then round again, so every name on the list reaches the rail. */
  const famous = (()=>{
    const cols = (STORE_CONTENT.featuredBrands||[]).map(b =>
      PRODUCTS.filter(p=>p.brand===b && p.published!==false).filter(shot)
              .slice().sort(rank).slice(0,3));
    const out=[];
    for(let i=0;i<3;i++) cols.forEach(c=>{ if(c[i] && out.length<12) out.push(c[i]) });
    return out;
  })();""")

rep("""  ${famous.length?railSec('Mushroom Chocolate',
      '<button class="more" data-go="all">See the shelf</button>',
      famous.map(card).join(''),
      4,'From our feed'):''}""",
"""  ${famous.length?railSec('Shop Our Brands',
      '<button class="more" data-go="all">Shop All</button>',
      famous.map(card).join(''),
      4,'Across the shelf'):''}""")

# ---- 3. a section heading and its own eyebrow should not be the same words --
rep("""    ${secHead('From Our Feed','<button class="more" data-go="store">See the shop</button>','From our feed')}""",
    """    ${secHead('From Our Feed','<button class="more" data-go="store">See the shop</button>',STORE.instagramHandle)}""")

# ---- 4. Spanish for the two new strings ------------------------------------
rep(""""I tapped that by mistake":"Le piqué por error"};""",
    """"I tapped that by mistake":"Le piqué por error","Shop Our Brands":"Nuestras marcas","Across the shelf":"En todo el estante"};""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
