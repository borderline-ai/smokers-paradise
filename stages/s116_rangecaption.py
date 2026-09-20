#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 116 — six photographs show the whole rack, and cannot be split.
#
# Stage 115 split five range shots by finding the gaps between the units. These
# six have no gaps: Diamond Glass and Lookah photograph their assorted pieces
# OVERLAPPING, each one standing partly in front of the next. Measured three
# ways and all three fail:
#
#   band splitting   one band, at every gap width from 3% to 13%
#   period finding   autocorrelation of the column ink profile peaks at 0.13
#                    to 0.29, where a real repeat is above 0.6, and the one
#                    that did pass returned a 57px sliver of a 328px picture
#   a fixed crop     cuts the neighbours in
#
# So they are not cropped. A bad crop is the thing Marco is complaining about,
# and inventing one to hide a photograph I cannot split would be exactly that.
#
# What is true about them is the interesting part: every one of these products
# is filed in this catalogue as **"Clear with color accents"**. The rack IS the
# product — the same pipe, in the accent colours the shop receives it in. The
# picture was never wrong, it was unexplained, and an unexplained picture of
# five bongs above one price and one Add to bag reads as a bug.
#
# So it says what it is, in the shop's own voice, on the product page under the
# picture: the colours are what the piece comes in, and you take one. The line
# is generated from the product's own variant record rather than typed, so it
# cannot drift from what the catalogue says, and a product that stops being
# assorted stops carrying the line.
#
# The better answer is a single-unit photograph, and those live on
# diamond-glass.com and lookah.com, which the browser will not open until Marco
# approves them.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""    ${(function(){
       const g=(p.opts||[]).find(o=>o.k==='v'); if(!g) return '';
       const v=g.vals[(PICK.sel||{}).v||0]; if(!v) return '';
       const own = typeof PHOTOS!=='undefined' && PHOTOS[p.id+'::'+vslug(v.n)];
       return own ? '' : `<div class="artnote">Pictured: this model. Packaging differs by flavor.</div>`;
     })()}""",
"""    ${(function(){
       /* THE RACK IS THE PRODUCT. Six pieces in this catalogue are filed as
          "Clear with color accents", and their makers photograph the accent
          colours together, overlapping, which cannot be split without cutting
          the neighbours in. Five bongs over one price and one Add to bag reads
          as a bug until somebody says what it is. Read off the product's own
          variant record, so it cannot drift from the catalogue. */
       const vs = p.vars || [];
       if(vs.length === 1 && /colou?r accents|colou?rs vary|assorted/i.test(vs[0]))
         return `<div class="artnote">Pictured: the accent colours this piece comes
           in. One piece per order, and the counter will show you what is in today.</div>`;
       const g=(p.opts||[]).find(o=>o.k==='v'); if(!g) return '';
       const v=g.vals[(PICK.sel||{}).v||0]; if(!v) return '';
       const own = typeof PHOTOS!=='undefined' && PHOTOS[p.id+'::'+vslug(v.n)];
       return own ? '' : `<div class="artnote">Pictured: this model. Packaging differs by flavor.</div>`;
     })()}""")

# ---- and one record corrected against its own source ----------------------
# rx172 is filed with one variant, "Clear", and its photograph shows five
# pieces in five accent colours. One of those is wrong. The retailer this
# product was researched from titles it "Diamond Glass Clear Mansion Water
# Pipe - 11"/14mmF/Colors Vary", so it is the record that is wrong, not the
# picture. Corrected to what the source says, which also lets the line above
# explain the photograph.
import json
k = 'const RX_PRODUCTS='
i = s.index(k)
j = s.index('\n', i)
arr = json.loads(s[i + len(k):j].rstrip(';'))
n = 0
for prod in arr:
    if prod['id'] == 'rx172' and prod.get('vars') == ['Clear']:
        prod['vars'] = ['Clear with color accents']
        n += 1
if n:
    s = s[:i] + k + json.dumps(arr, separators=(',', ':')) + ';' + s[j:]
print('  ok: rx172 filed as assorted, matching the listing it was researched from'
      if n else '  ok: rx172 already corrected')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
