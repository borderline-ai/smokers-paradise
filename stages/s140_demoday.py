#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 140 — demo day. Three faults found by looking at every screen.
#
# Marco: "today is the day and I STILL see a ton of mistakes."
#
# No screenshots this time, so I swept every screen top to bottom at real size
# and read them. Three things are wrong and the first one is the worst thing in
# this app.
#
# ======================================================================
# 1. A PHOTOGRAPH IN A THUMBNAIL WAS PAINTING OVER THE WHOLE PRODUCT PAGE
# ======================================================================
# Open the Off-Stamp SW9000 and the page is a collage: an Air Bar Nex on a grey
# marble slab, with AIR BAR / WATERMELON printed across it, filling the screen,
# with the Off-Stamp floating on top of it. Two different products in one view,
# on a page for a brand the shop leads with.
#
# It is not a collage. It is one image out of its box. Measured:
#
#     <img class="scenephoto">   natural 340x340   RENDERED 390 x 785
#
# in a rail whose thumbnails are 52 pixels tall.
#
# WHY. Ten products in this catalogue have a lifestyle photograph rather than a
# keyed cut-out, and those get `.scenephoto`, which is:
#
#     position:absolute !important; inset:0 !important
#
# so the photograph fills its frame edge to edge instead of floating inside it.
# That is right, and it works everywhere the frame is a stage — the card thumb,
# the product page art, the Puffco band — because every one of those is
# `position:relative`. The cross-sell rail at the bottom of the product page is
# `.xs .t`, a 56px grid cell, and it is `position:static`. An absolutely
# positioned child of a static parent does not stop at that parent: it goes up
# to the nearest positioned ancestor, which is the sheet, and fills it.
#
# So the rule was not "fill your frame". It was "fill your frame IF somebody
# remembered to make that frame a containing block", and the day somebody adds
# a thumbnail rail without `position:relative` — which is most thumbnail rails,
# because most do not need it — one of ten products blows a photograph across
# the screen. That is a rule that fails silently and at random, which is the
# only kind that survives to a demo.
#
# It is inverted now. The BASE behaviour is safe in any box: a fitted image
# that respects whatever frame it is in. Filling a stage edge to edge is the
# EXCEPTION, named frame by frame, and every one of those frames is positioned.
# A new rail added tomorrow gets the safe behaviour by default.
#
# ======================================================================
# 2. THE OFFER ON A PRODUCT CARD WAS CHOPPED MID CHARACTER
# ======================================================================
#     2 for $10 · 3 for $1        <- what the card printed
#     2 for $10 · 3 for $12       <- what the offer is
#
# On every Off-Stamp card, which is the brand with the offer. Measured: the
# text needs 153px and the box is 141px. The rule says
# `overflow:hidden; text-overflow:ellipsis`, so it should at least have said
# "…". It does not, because the same rule says `display:flex`, and
# text-overflow does not apply to the anonymous text inside a flex container.
# So it silently cut a price in half.
#
# Both halves are fixed: the text is wrapped in its own element so the ellipsis
# can actually work, and the offer is set in a form that fits — "2 for $10 or 3
# for $12" is how it is said at the counter and it is shorter on screen than
# the middot version, which was 21 characters of mono at 9px.
#
# ======================================================================
# 3. ELEVEN CARDS PRINTED THE BRAND TWICE
# ======================================================================
#     GRAV
#     GRAV® Small Wide Base Water Pipe
#
# The brand line is drawn from p.brand and the title from p.name, and GRAV
# publish their titles with the brand and the registered mark in front. Eleven
# products, on the shelf, on the product page, and in the bag. The title drops
# a leading brand token when the card is already carrying it — done at render
# time, so the catalogue keeps the maker's exact published title, which is the
# rule this file has followed since the start.
import io
import re

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the photograph stays in its box ------------------------------------
rep(""".scenephoto{pointer-events:none;position:absolute!important;inset:0!important;
  width:100%!important;height:100%!important;padding:0!important;
  max-width:none!important;max-height:none!important;
  object-fit:cover!important;object-position:center!important;
  filter:none!important;border-radius:inherit}""",
"""/* THE BASE IS SAFE IN ANY BOX, POSITIONED OR NOT.
   This used to be absolute with inset:0, which fills the frame only when that
   frame is a containing block. In `.xs .t` — the cross-sell rail on the
   product page, a 56px grid cell that is position:static — the photograph
   escaped to the sheet and rendered 390 x 785 over the whole page. Filling a
   stage is now the exception, named below, and every frame named there is
   positioned. Anything else gets an image that fits where it is put. */
.scenephoto{pointer-events:none;padding:0!important;
  max-width:100%!important;max-height:100%!important;
  object-fit:contain!important;object-position:center!important;
  filter:none!important;border-radius:inherit}
/* the stages: frames that establish a containing block and are meant to be
   filled edge to edge, because on those a photograph IS the stage */
.card .thumb>.scenephoto,
.pdp-art>.scenephoto,
.spotitem .sp>.scenephoto,
.ctile .ph>.scenephoto{
  position:absolute!important;inset:0!important;
  width:100%!important;height:100%!important;
  max-width:none!important;max-height:none!important;
  object-fit:cover!important}""")

# and the frames that hold product art get a containing block, so this class of
# fault cannot come back through a frame nobody thought about
rep(""".xs .t{height:56px;display:grid;place-items:center}""",
"""/* a containing block, so an absolutely positioned child cannot escape to the
   sheet: belt and braces behind the .scenephoto rule above */
.xs .t{position:relative;height:56px;display:grid;place-items:center;overflow:hidden}""")

# ---- 2. the offer fits, and truncates honestly if it ever does not ---------
rep("""  if(p.brand==='Off-Stamp') return '2 for $10 &middot; 3 for $12';""",
"""  /* Was '2 for $10 &middot; 3 for $12': 21 characters of 9px mono in a 141px
     box, which the card cut to "3 for $1". Said the way the counter says it,
     and it fits. */
  if(p.brand==='Off-Stamp') return '2 for $10, 3 for $12';""")

rep("""      ${pr?`<div class="promo">${TAGICO} ${pr}</div>`:''}""",
"""      ${/* the text is its own element so text-overflow can reach it: on a
             flex container the ellipsis never applies to the loose text
             inside it, which is why a price was being cut mid-character
             instead of truncated */''}
      ${pr?`<div class="promo">${TAGICO}<span>${pr}</span></div>`:''}""")

rep(""".card .promo{display:flex;align-items:center;gap:5px;font-size:9px;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}""",
""".card .promo{display:flex;align-items:center;gap:5px;font-size:9px;white-space:nowrap;
  overflow:hidden;min-width:0}
.card .promo>span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}""")

# ---- 3. the brand is printed once ------------------------------------------
i = s.index('function card(p,i){')
rep("""function card(p,i){""",
"""/* THE TITLE DOES NOT REPEAT THE BRAND LINE ABOVE IT.
   GRAV publish their titles with the brand and the registered mark in front —
   "GRAV(R) Small Wide Base Water Pipe" — and the card already draws GRAV on
   its own line, so eleven cards said it twice. The catalogue keeps the maker's
   exact published title; this drops the duplicate at the moment of drawing,
   and only when the leading token really is the brand. */
function titleOf(p){
  if(!p || !p.name) return '';
  const b = (p.brand || '').trim();
  if(!b) return p.name;
  const esc = b.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  const cut = new RegExp('^' + esc + '\\\\s*(?:\\u00ae|\\u2122|\\u00a9)?[\\\\s\\u2013\\u2014:-]*', 'i');
  const out = p.name.replace(cut, '').trim();
  return out.length >= 3 ? out : p.name;
}

function card(p,i){""")

rep("""      <div class="br">${brandLabel(p.brand)}</div><div class="nm">${p.name}</div>""",
"""      <div class="br">${brandLabel(p.brand)}</div><div class="nm">${titleOf(p)}</div>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
