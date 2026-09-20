#!/usr/bin/env python3
# Stage 46 — strict mode accepts the embedded photograph.
#
# `art(p, vkey, strict)` refuses a model-level picture when the shopper has
# chosen a specific flavour, which is right: a Blue Razz card should not show
# the Watermelon file. But it was also refusing the EMBEDDED model photograph,
# so fifteen disposables whose sources publish one photo per model rather than
# one per flavour fell through to "Photo coming soon".
#
# The rule now: try the exact variant first, local then remote — and only if
# neither exists, use the manufacturer's photograph of that exact model. That
# is still the right brand and the right model, which is what a shelf card is
# for. It is never a different product, and never a stand-in from another line.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

OLD = """  /* 4. unavailable state. Unbranded house stock gets the shop's plate; a
     branded product gets an honest empty frame, never a drawing of itself. */
  if(HOUSE_BRANDS.indexOf(p.brand)>=0) return comingSoon(p);"""
NEW = """  /* 3b. the embedded photograph of this exact model.
     Reached only after the exact variant has been looked for and not found.
     Many manufacturers publish one photograph per model rather than one per
     flavour, so this IS that product's official picture — right brand, right
     model — and it is in this file, so it cannot fail to load. A card with a
     real photograph of the right model beats a card with no photograph. */
  if(PHOTOS[p.id]) return `<img src="${PHOTOS[p.id]}" alt="${esc(alt)}">`;

  /* 4. unavailable state. Unbranded house stock gets the shop's plate; a
     branded product gets an honest empty frame, never a drawing of itself. */
  if(HOUSE_BRANDS.indexOf(p.brand)>=0) return comingSoon(p);"""
assert s.count(OLD)==1
s=s.replace(OLD,NEW)
io.open(P,'w',encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
