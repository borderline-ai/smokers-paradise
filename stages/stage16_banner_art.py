#!/usr/bin/env python3
# Stage 16 — every banner and every deal card resolves to a real photograph.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for %s' % (s.count(a), a[:90])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))

# ---------------------------------------------------------------- 1
# A lookup that cannot come back empty: brand + a loose model match, then the
# first variant that actually has a photograph. img() only matched exact
# catalogue titles, so "Off-Stamp SW9000" found nothing and the slide ran with
# no picture at all.
rep("""const img = (brand, model, flavor) => {""",
"""/* Hero and deal-card artwork. Looks the product up the way a person would —
   brand plus roughly the model — and then takes the first variant that has a
   photograph, so a banner can never render empty because a catalogue title
   gained or lost a word. */
const heroShot = (brand, modelLike, flavor) => {
  const list = (typeof ALL_PRODUCTS!=='undefined' && ALL_PRODUCTS.length) ? ALL_PRODUCTS
             : (typeof PRODUCTS!=='undefined' ? PRODUCTS : []);
  const norm = x => String(x||'').toLowerCase().replace(/[^a-z0-9]/g,'');
  const want = norm(modelLike);
  const cands = list.filter(p => p.brand === brand)
    .filter(p => !want || norm(p.name).indexOf(want) >= 0 || want.indexOf(norm(p.name)) >= 0);
  const pool = cands.length ? cands : list.filter(p => p.brand === brand);
  for(const p of pool){
    if(flavor){
      const r = (typeof remoteFor==='function') && remoteFor(p, flavor);
      if(r && r.remoteImageUrl) return r.remoteImageUrl;
    }
    const g = (p.opts||[]).find(o=>o.k==='v');
    const names = g ? g.vals.map(v=>v.n) : [];
    for(const nm of names.concat([null])){
      const r = (typeof remoteFor==='function') && remoteFor(p, nm);
      if(r && r.remoteImageUrl) return r.remoteImageUrl;
    }
  }
  return '';
};

const img = (brand, model, flavor) => {""")

# ---------------------------------------------------------------- 2
# Point the banners and cards at it.
swaps = [
 ("{src:()=>img('Off-Stamp','Off-Stamp SW9000','Blue Razz Ice'), alt:'Off-Stamp SW9000, Blue Razz Ice', tilt:-4, z:2, scale:1}",
  "{src:()=>heroShot('Off-Stamp','X Cube 25K'), alt:'Off-Stamp X Cube 25K', tilt:-5, z:2, scale:1},\n"
  "      {src:()=>heroShot('Off-Stamp','SW9000'),    alt:'Off-Stamp SW9000',     tilt:4,  z:1, scale:.9}"),

 ("{src:()=>img('Lost Mary','MT15000 Turbo','Grape Jelly'), alt:'Lost Mary MT15000 Turbo, Grape Jelly', tilt:-4, z:2, scale:1}",
  "{src:()=>heroShot('Lost Mary','MT35000 Turbo'), alt:'Lost Mary MT35000 Turbo', tilt:-5, z:2, scale:1},\n"
  "      {src:()=>heroShot('Lost Mary','MO20000 Pro'),  alt:'Lost Mary MO20000 Pro',  tilt:4,  z:1, scale:.9}"),

 ("image:()=>img('Off-Stamp','Off-Stamp SW9000','Blue Razz Ice'),",
  "image:()=>heroShot('Off-Stamp','X Cube 25K'),"),

 ("image:()=>img('TRE House','Mushroom Chocolate, Peanut Butter'),",
  "image:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter'),"),
]
for a, b in swaps:
    rep(a, b)

for flav in ['Peanut Butter', 'Fruity Cereal', 'Chocolate Crunch']:
    rep("img('TRE House','Mushroom Chocolate, %s')" % flav,
        "heroShot('TRE House','Mushroom Chocolate, %s')" % flav)

# category tile: same resolver, so the shelf tile follows the catalogue
rep("""  {k:'shroom',n:'Mushroom Chocolate',       img:()=>\"""",
    """  {k:'shroom',n:'Mushroom Chocolate',       img:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter')||\"""")

# ---------------------------------------------------------------- 3
# "2 for $10" was being reduced to "2$10" by the numeric fallback. A card with
# no photograph now shows the offer as written, in the offer's own type.
rep("""  const pct=!im ? (d.discountAmount||'').replace(/[^0-9%$.]/g,'') : '';""",
    """  /* The old fallback stripped the words out of "2 for $10" and printed
     "2$10". An offer that is not a percentage is set as words instead. */
  const raw = (d.discountAmount||'').trim();
  const isPct = /^\\s*\\d+\\s*%\\s*$/.test(raw);
  const pct = !im ? (isPct ? raw.replace(/[^0-9%]/g,'') : '') : '';
  const words = !im && !isPct ? raw : '';""")

rep("""       :`<div class="dpct" style="color:${d.theme.accent}">${pct||'%'}<small>OFF</small></div>`}""",
    """       : words ? `<div class="dword" style="color:${d.theme.accent}">${esc(words)}</div>`
       : `<div class="dpct" style="color:${d.theme.accent}">${pct||'%'}<small>OFF</small></div>`}""")

rep("""            :`<div style="font-family:var(--block);font-size:60px;color:${d.theme.accent};position:relative">${(d.discountAmount||'').replace(/[^0-9%$.]/g,'')||'%'}</div>`}""",
    """            :`<div style="font-family:var(--block);font-size:${(d.discountAmount||'').length>6?'34px':'60px'};line-height:1;
                 letter-spacing:.5px;text-align:center;padding:0 18px;color:${d.theme.accent};position:relative">${esc(d.discountAmount||'')}</div>`}""")

# style for the word plate
rep(""".card .pr.ask b{""",
    """.dword{font-family:var(--block);font-size:26px;line-height:1.02;letter-spacing:.4px;
  text-align:center;padding:0 14px;position:relative;text-transform:uppercase}
.dcard.big .dword{font-size:34px}
.card .pr.ask b{""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
