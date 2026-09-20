#!/usr/bin/env python3
# Stage 42 — a studio sweep under the product, instead of hoping the gradient
# lands white in the right place.
#
# The field is a diagonal, so where it happens to be pure white depends on the
# panel's proportions. Get it slightly wrong and a packshot printed on white
# shows a hard vertical edge against the tint — which is exactly the "pasted
# on" look, arriving by a different route.
#
# So the product cell paints its own white, feathered out in the direction the
# product is cropped: up from the bottom when the product sits along the
# bottom, in from the right when it sits on the right. Linear only — a white
# radial behind a product is a halo, and this app does not have those.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CSS = """
/* ---- the studio sweep ----
   White where the product stands, feathered out toward the copy. A packshot
   printed on white now has the same white under it in every layout, which is
   why there is no plate and no edge. */
.camp-shot{position:relative;z-index:2;isolation:isolate}
.camp-shot::before{content:"";position:absolute;inset:0;z-index:0;
  pointer-events:none;
  background:linear-gradient(to top,
    #FFF 0%, #FFF 58%, rgba(255,255,255,.55) 82%, rgba(255,255,255,0) 100%)}
.camp .camp-ground{z-index:1}
.camp .camp-back{z-index:2}
.camp .camp-lead{z-index:3}
.camp.dark .camp-shot::before{display:none}

/* the product sits on the right in the horizontal .tall, so the sweep does */
.camp.tall .camp-shot::before{
  background:linear-gradient(to left,
    #FFF 0%, #FFF 62%, rgba(255,255,255,.55) 86%, rgba(255,255,255,0) 100%)}
@container (min-width:560px){
  /* stood up: product along the bottom again */
  .camp.tall .camp-shot::before{
    background:linear-gradient(to top,
      #FFF 0%, #FFF 58%, rgba(255,255,255,.55) 82%, rgba(255,255,255,0) 100%)}
}
"""
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
io.open(P, 'w', encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
