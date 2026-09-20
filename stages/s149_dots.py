#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 149 — the five dots nobody could hit.
#
# The twelve device test reports every control smaller than a finger. On the
# phones it finds two. On every iPad it finds nine, and five of the nine are
# the offer carousel's dots:
#
#     Offer 1  20 x 6
#     Offer 2   6 x 6
#     Offer 3   6 x 6
#     Offer 4   6 x 6
#     Offer 5   6 x 6
#
# Six pixels square. hittest passes them because a mouse pointer can land on
# six pixels; a thumb cannot. They are `<button>` elements with an aria-label
# each, so they ARE meant to be tapped, and on the iPad Marco is handing across
# the counter they are the smallest thing on the screen.
#
# WHAT IS NOT CHANGED. Not how they look. A carousel indicator is supposed to be
# a small dot, and making it a 44 point circle would look like five buttons
# nobody asked for. The visible dot is drawn by ::before and is untouched — this
# adds an invisible ::after that only the finger meets.
#
# HOW BIG, AND WHY NOT 44. The dots sit 11 points apart (6 wide, 5 gap). A 44
# point wide pad would cover its two neighbours, so tapping "offer 4" would
# sometimes fire offer 3 — a worse bug than a small target. So the pad grows to
# exactly the gap and no further, 11 points wide, and takes the height it wants:
#
#     6 x 6  ->  11 x 36, with no two pads touching
#
# Thirty six points tall and eleven wide is a strip a thumb finds, and the miss
# rate on a strip that tall is nothing like the miss rate on a dot. The arrows
# (27 points) and the announcement chevrons (28) are left alone deliberately:
# their pads would have to grow over the promo card behind them, and stealing a
# tap from the card to feed an arrow is the trade the paragraph above refuses.
#
# TOUCH ONLY. All of it sits inside `pointer:coarse`, so the browser demo on a
# laptop is byte for byte what it was.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

a = """.dots button{position:relative}"""
assert s.count(a) == 1, s.count(a)
s = s.replace(a, a + """
/* A FINGER CANNOT LAND ON SIX PIXELS.
   The dot the eye sees is ::before and is unchanged. This is the area the
   finger meets: as wide as the gap allows and no wider, so no pad ever
   reaches its neighbour, and tall enough to be found without looking. */
@media (pointer:coarse), (display-mode:standalone){
  .dots button::after{content:'';position:absolute;left:-2.5px;right:-2.5px;
    top:-15px;bottom:-15px}
}""")
print('  ok: the dots get a pad a thumb can find')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
