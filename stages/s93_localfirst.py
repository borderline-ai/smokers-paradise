#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 93 — the shelf stops going to the internet for pictures it already has.
#
# HOW THIS WAS FOUND. The button walk reported seven thousand console errors on
# a run with the network switched off, while the image audit reported zero
# broken images. Both were right, and the gap between them is the bug: every
# one of those errors is a product photograph being fetched from somebody
# else's website, failing, and being quietly replaced by the copy already
# embedded in this file.
#
# Counted on a live page: 89 of the 259 cards on Shop All, and 34 of the 50 on
# the disposables shelf, take their picture from a remote host first.
#
# WHY. card() calls art(p, vk, false) where vk is simply the FIRST option in
# the product's list, and art() prefers a remote photograph of that flavour
# over the embedded photograph of the model. On a product page, where a
# customer has actually chosen Blue Razz, fetching the Blue Razz photograph is
# worth the wait. On a grid card nothing has been chosen: "the first flavour in
# the list" is not more accurate than the model shot, it is only more fragile.
#
# WHAT IT COST, beyond speed:
#
#   * Stage 92 recut three Tyson cards to take MIKETYSONOFFICIAL.COM off them.
#     Offline that worked. Online it did nothing at all, because the card was
#     still loading the original advertising slide from miketysonofficial.com.
#     Every picture audited on a contact sheet was the picture nobody with
#     signal was seeing.
#   * On one bar of signal in a shop on North Grand, a third of the shelf sits
#     empty until each request times out. That is the exact phone, in the exact
#     room, that this app has to work in on Saturday.
#
# THE RULE, now: an embedded photograph beats the network unless the customer
# has chosen the variant themselves. Strict mode, which is what the product
# page uses, is unchanged and still fetches the exact flavour. The Puffco panel
# on the home screen was asking strictly for the first variant of each item,
# which is the same mistake in a different place, and now does not.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""  /* 2. official remote URL for this exact variant */
  const vn = variantNameFor(p, vkey);
  if(vn){
    const rec = remoteFor(p, vn);
    if(rec && rec.level==='flavor') return remoteImg(p, rec, alt);
  }
  if(!vkey || !strict){
    if(PHOTOS[p.id]) return `<img src="${PHOTOS[p.id]}" alt="${esc(alt)}">`;
  }""",
"""  /* 2. THE EMBEDDED PHOTOGRAPH, unless the customer chose this variant.
     A card passes the first option in the product's list as `vkey`. Nobody
     picked it. So a remote photograph of that flavour is not more accurate
     than the embedded photograph of the model, it is only more fragile: on a
     weak connection the card is empty until the request gives up, and what
     finally appears is the embedded copy anyway. Strict means a customer
     really did choose this flavour on the product page, and only then is the
     wait worth it. */
  if(!strict && PHOTOS[p.id]) return `<img src="${PHOTOS[p.id]}" alt="${esc(alt)}">`;

  /* 3. official remote URL for this exact variant */
  const vn = variantNameFor(p, vkey);
  if(vn){
    const rec = remoteFor(p, vn);
    if(rec && rec.level==='flavor') return remoteImg(p, rec, alt);
  }
  if(!vkey || !strict){
    if(PHOTOS[p.id]) return `<img src="${PHOTOS[p.id]}" alt="${esc(alt)}">`;
  }""")

# the Puffco panel on the home screen: nothing is chosen there either
rep("""        const g=(p.opts||[]).find(o=>o.k==='v');
        const vk=g?vslug(g.vals[0].n):'';
        return `<button class="spotitem" data-p="${p.id}">
          <span class="sp">${art(p,vk,true)}</span>""",
"""        const g=(p.opts||[]).find(o=>o.k==='v');
        const vk=g?vslug(g.vals[0].n):'';
        return `<button class="spotitem" data-p="${p.id}">
          <span class="sp">${art(p,vk,false)}</span>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
