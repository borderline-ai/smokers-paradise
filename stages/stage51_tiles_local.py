#!/usr/bin/env python3
# Stage 51 — the category tiles use the embedded photographs.
#
# The last remote images in the app. Every tile on "Shop by category" pointed
# at somebody else's CDN, so with the network blocked the whole department grid
# went to empty frames while every product card underneath it was fine.
#
# Both of the functions that feed those tiles now look in this file first.
# After this, nothing a customer can see depends on a network request.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


rep("""const img = (brand, model, flavor) => {
  const r = (typeof REMOTE!=='undefined') && REMOTE[brand+'|'+model+'|'+(flavor||'*')];""",
"""const img = (brand, model, flavor) => {
  /* the embedded photograph of this exact model, if this build has one */
  if(typeof LOCAL_PHOTOS !== 'undefined'){
    const list = (typeof ALL_PRODUCTS!=='undefined' && ALL_PRODUCTS.length) ? ALL_PRODUCTS
               : (typeof PRODUCTS!=='undefined' ? PRODUCTS : []);
    const norm = x => String(x||'').toLowerCase().replace(/[^a-z0-9]/g,'');
    const want = norm(model);
    /* exact model first, then a loose match, because the catalogue spells some
       models with a registered mark or a size the tile does not repeat */
    const hit = list.find(p => p.brand===brand && p.name===model && LOCAL_PHOTOS[p.id])
             || list.find(p => p.brand===brand && LOCAL_PHOTOS[p.id] &&
                  (norm(p.name).indexOf(want)>=0 || want.indexOf(norm(p.name))>=0))
             || list.find(p => p.brand===brand && LOCAL_PHOTOS[p.id]);
    if(hit) return LOCAL_PHOTOS[hit.id];
  }
  const r = (typeof REMOTE!=='undefined') && REMOTE[brand+'|'+model+'|'+(flavor||'*')];""")

rep("""  const p=PRODUCTS.find(x=>x.cat===cat && x.featured) || PRODUCTS.find(x=>x.cat===cat);
  if(!p) return '';""",
"""  const p=PRODUCTS.find(x=>x.cat===cat && x.featured && LOCAL_PHOTOS[x.id])
        || PRODUCTS.find(x=>x.cat===cat && LOCAL_PHOTOS[x.id])
        || PRODUCTS.find(x=>x.cat===cat && x.featured)
        || PRODUCTS.find(x=>x.cat===cat);
  if(!p) return '';
  if(typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[p.id]) return LOCAL_PHOTOS[p.id];""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
